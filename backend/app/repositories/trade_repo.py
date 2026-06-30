"""Data access for trades. Every query is scoped by user_id."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.trade import Trade, TradeResult, TradeStatus


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


def realized_pnl_since(db: Session, user_id: uuid.UUID, since: datetime) -> Decimal:
    """Net realized PnL of closed trades since `since` (0 if none)."""
    total = db.scalar(
        select(func.coalesce(func.sum(Trade.pnl), 0)).where(
            Trade.user_id == user_id,
            Trade.status == TradeStatus.closed,
            Trade.closed_at >= since,
        )
    )
    return Decimal(str(total)) if total is not None else Decimal("0")


def consecutive_loss_count(db: Session, user_id: uuid.UUID) -> int:
    """Number of trailing consecutive losing closed trades (most recent first)."""
    results = db.scalars(
        select(Trade.result)
        .where(Trade.user_id == user_id, Trade.status == TradeStatus.closed)
        .order_by(Trade.closed_at.desc())
    )
    count = 0
    for result in results:
        if result == TradeResult.loss:
            count += 1
        else:
            break
    return count
