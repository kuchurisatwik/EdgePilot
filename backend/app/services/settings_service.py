"""User settings + profile business logic (per-user scoped)."""

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.user import User, UserSettings
from app.repositories import user_repo
from app.schemas.user import ProfileUpdate, UserSettingsUpdate


def get_settings(db: Session, user_id: uuid.UUID) -> UserSettings:
    settings = user_repo.get_settings(db, user_id)
    if settings is None:
        raise NotFoundError("Settings not found.")
    return settings


def update_settings(db: Session, user_id: uuid.UUID, payload: UserSettingsUpdate) -> UserSettings:
    settings = get_settings(db, user_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(settings, field, value)
    db.flush()
    return settings


def update_profile(db: Session, user: User, payload: ProfileUpdate) -> User:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(user, field, value)
    db.flush()
    return user
