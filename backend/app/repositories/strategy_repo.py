"""Data access for strategies. Every query is scoped by user_id."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.strategy import Strategy


def list_for_user(db: Session, user_id: uuid.UUID, active_only: bool = True) -> list[Strategy]:
    stmt = select(Strategy).where(Strategy.user_id == user_id)
    if active_only:
        stmt = stmt.where(Strategy.is_active.is_(True))
    stmt = stmt.order_by(Strategy.is_default.desc(), Strategy.name.asc())
    return list(db.scalars(stmt))


def get(db: Session, user_id: uuid.UUID, strategy_id: uuid.UUID) -> Strategy | None:
    return db.scalar(
        select(Strategy).where(Strategy.id == strategy_id, Strategy.user_id == user_id)
    )


def name_exists(
    db: Session,
    user_id: uuid.UUID,
    name: str,
    exclude_id: uuid.UUID | None = None,
) -> bool:
    stmt = select(Strategy.id).where(Strategy.user_id == user_id, Strategy.name == name)
    if exclude_id is not None:
        stmt = stmt.where(Strategy.id != exclude_id)
    return db.scalar(stmt) is not None


def has_any_default(db: Session, user_id: uuid.UUID) -> bool:
    return (
        db.scalar(
            select(Strategy.id).where(
                Strategy.user_id == user_id, Strategy.is_default.is_(True)
            )
        )
        is not None
    )


def add(db: Session, strategy: Strategy) -> Strategy:
    db.add(strategy)
    db.flush()
    return strategy
