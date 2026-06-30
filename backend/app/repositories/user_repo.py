"""Data access for users and settings. All lookups are id/email scoped."""

import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserSettings


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def create(db: Session, *, email: str, password_hash: str, name: str) -> User:
    user = User(email=email, password_hash=password_hash, name=name)
    db.add(user)
    db.flush()
    return user


def create_settings(
    db: Session,
    *,
    user_id: uuid.UUID,
    account_size: Decimal = Decimal("0"),
    default_risk_pct: Decimal = Decimal("1.0"),
) -> UserSettings:
    settings = UserSettings(
        user_id=user_id,
        account_size=account_size,
        default_risk_pct=default_risk_pct,
    )
    db.add(settings)
    db.flush()
    return settings


def get_settings(db: Session, user_id: uuid.UUID) -> UserSettings | None:
    return db.scalar(select(UserSettings).where(UserSettings.user_id == user_id))
