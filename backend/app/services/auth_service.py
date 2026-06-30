"""Authentication business logic.

Issues a short-lived access token (returned in the response body, held in memory
by the client) and a long-lived refresh token (delivered as an httpOnly cookie
and tracked server-side so it can be rotated and revoked).
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthError, ValidationError
from app.core.security import (
    REFRESH_TOKEN,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.user import User
from app.repositories import refresh_token_repo, user_repo
from app.schemas.auth import LoginRequest, RegisterRequest


@dataclass
class AuthResult:
    user: User
    access_token: str
    refresh_token: str  # raw token — the route sets it as an httpOnly cookie


def _issue_tokens(db: Session, user: User) -> AuthResult:
    access = create_access_token(str(user.id))
    refresh, jti = create_refresh_token(str(user.id))
    expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    refresh_token_repo.store(
        db,
        user_id=user.id,
        token_hash=hash_refresh_token(refresh),
        jti=jti,
        expires_at=expires_at,
    )
    return AuthResult(user=user, access_token=access, refresh_token=refresh)


def register(db: Session, payload: RegisterRequest) -> AuthResult:
    email = payload.email.lower()
    if user_repo.get_by_email(db, email) is not None:
        raise ValidationError("An account with this email already exists.", code="email_taken")

    user = user_repo.create(
        db, email=email, password_hash=hash_password(payload.password), name=payload.name
    )
    # Default settings (account size set later in Settings). Strategy and rule
    # defaults are seeded in M2/M4 via their own ensure_* hooks called here.
    user_repo.create_settings(db, user_id=user.id)
    return _issue_tokens(db, user)


def login(db: Session, payload: LoginRequest) -> AuthResult:
    user = user_repo.get_by_email(db, payload.email.lower())
    if user is None or not verify_password(payload.password, user.password_hash):
        raise AuthError("Invalid email or password.", code="invalid_credentials")
    if not user.is_active:
        raise AuthError("Account is inactive.", code="inactive")
    return _issue_tokens(db, user)


def refresh(db: Session, raw_token: str | None) -> AuthResult:
    if not raw_token:
        raise AuthError("Missing refresh token.", code="no_refresh")
    try:
        payload = decode_token(raw_token)  # also enforces expiry via `exp`
    except jwt.PyJWTError as exc:
        raise AuthError("Invalid or expired refresh token.", code="invalid_refresh") from exc
    if payload.get("type") != REFRESH_TOKEN:
        raise AuthError("Invalid token type.", code="invalid_refresh")

    stored = refresh_token_repo.get_by_hash(db, hash_refresh_token(raw_token))
    if stored is None or stored.revoked:
        raise AuthError("Refresh token is no longer valid.", code="revoked_refresh")

    user = user_repo.get_by_id(db, stored.user_id)
    if user is None or not user.is_active:
        raise AuthError("Account not found or inactive.", code="inactive")

    # Rotate: invalidate the presented token, issue a fresh pair.
    refresh_token_repo.revoke(db, stored)
    return _issue_tokens(db, user)


def logout(db: Session, raw_token: str | None) -> None:
    if not raw_token:
        return
    stored = refresh_token_repo.get_by_hash(db, hash_refresh_token(raw_token))
    if stored is not None and not stored.revoked:
        refresh_token_repo.revoke(db, stored)
