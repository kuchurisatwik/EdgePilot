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


def list_with_filters(
    db: Session,
    user_id: uuid.UUID,
    *,
    strategy_id: uuid.UUID | None = None,
    symbol: str | None = None,
    result: TradeResult | None = None,
    status: TradeStatus | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Trade], int]:
    conditions = [Trade.user_id == user_id]
    if strategy_id is not None:
        conditions.append(Trade.strategy_id == strategy_id)
    if symbol:
        conditions.append(Trade.symbol == symbol.strip().upper())
    if result is not None:
        conditions.append(Trade.result == result)
    if status is not None:
        conditions.append(Trade.status == status)
    if date_from is not None:
        conditions.append(Trade.created_at >= date_from)
    if date_to is not None:
        conditions.append(Trade.created_at <= date_to)

    total = db.scalar(select(func.count()).select_from(Trade).where(*conditions)) or 0
    items = list(
        db.scalars(
            select(Trade)
            .where(*conditions)
            .order_by(Trade.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    )
    return items, total
