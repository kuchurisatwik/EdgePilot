"""Security primitives — password hashing, JWT, and refresh-token hashing."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from app.core.config import settings

ACCESS_TOKEN = "access"
REFRESH_TOKEN = "refresh"

# bcrypt hashes at most the first 72 bytes of the password.
_BCRYPT_MAX_BYTES = 72


def _password_bytes(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_password_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(_password_bytes(password), password_hash.encode("utf-8"))
    except ValueError:
        return False


def _create_token(subject: str, token_type: str, expires_delta: timedelta, **claims: Any) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        **claims,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str, **claims: Any) -> str:
    return _create_token(
        subject, ACCESS_TOKEN, timedelta(minutes=settings.access_token_expire_min), **claims
    )


def create_refresh_token(subject: str) -> tuple[str, str]:
    """Return (token, jti). The jti uniquely identifies the token server-side."""
    jti = secrets.token_urlsafe(32)
    token = _create_token(
        subject, REFRESH_TOKEN, timedelta(days=settings.refresh_token_expire_days), jti=jti
    )
    return token, jti


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def hash_refresh_token(token: str) -> str:
    """Store only a hash of the refresh token, never the token itself."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
