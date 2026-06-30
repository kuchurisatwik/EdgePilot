"""Data access for market context (1:1 with a trade)."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.market_context import MarketContext


def get_for_trade(db: Session, trade_id: uuid.UUID) -> MarketContext | None:
    return db.scalar(select(MarketContext).where(MarketContext.trade_id == trade_id))


def add(db: Session, context: MarketContext) -> MarketContext:
    db.add(context)
    db.flush()
    return context
