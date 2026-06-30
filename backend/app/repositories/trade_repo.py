"""Data access for trades. Every query is scoped by user_id."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.trade import Trade


def add(db: Session, trade: Trade) -> Trade:
    db.add(trade)
    db.flush()
    return trade


def get(db: Session, user_id: uuid.UUID, trade_id: uuid.UUID) -> Trade | None:
    return db.scalar(select(Trade).where(Trade.id == trade_id, Trade.user_id == user_id))


def list_for_user(db: Session, user_id: uuid.UUID) -> list[Trade]:
    return list(
        db.scalars(
            select(Trade).where(Trade.user_id == user_id).order_by(Trade.created_at.desc())
        )
    )
