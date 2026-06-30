"""Security primitives — password hashing and JWT.

M0 ships the helper surface; M1 wires them into the auth service and the
``get_current_user`` dependency.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN = "access"
REFRESH_TOKEN = "refresh"


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _pwd_context.verify(password, password_hash)


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
        subject,
        ACCESS_TOKEN,
        timedelta(minutes=settings.access_token_expire_min),
        **claims,
    )


def create_refresh_token(subject: str, **claims: Any) -> str:
    return _create_token(
        subject,
        REFRESH_TOKEN,
        timedelta(days=settings.refresh_token_expire_days),
        **claims,
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
