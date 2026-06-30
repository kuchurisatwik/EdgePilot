"""Shared API dependencies: DB session + authenticated user."""

import uuid

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AuthError
from app.core.security import ACCESS_TOKEN, decode_token
from app.models.user import User
from app.repositories import user_repo

__all__ = ["get_db", "get_current_user"]

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AuthError("Not authenticated.", code="not_authenticated")
    try:
        payload = decode_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise AuthError("Invalid or expired token.", code="invalid_token") from exc
    if payload.get("type") != ACCESS_TOKEN:
        raise AuthError("Invalid token type.", code="invalid_token")

    try:
        user_id = uuid.UUID(str(payload.get("sub")))
    except (ValueError, TypeError) as exc:
        raise AuthError("Invalid token subject.", code="invalid_token") from exc

    user = user_repo.get_by_id(db, user_id)
    if user is None or not user.is_active:
        raise AuthError("User not found or inactive.", code="inactive")
    return user
