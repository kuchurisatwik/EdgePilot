"""Market context capture (auto-captured on open; refreshable)."""

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.market_context import MarketContext
from app.models.trade import Trade
from app.repositories import market_context_repo
from app.services.market_data.provider import MarketContextData, get_market_data_provider


def _apply(context: MarketContext, data: MarketContextData, captured_at: datetime) -> None:
    context.atr = data.atr
    context.rsi = data.rsi
    context.vwap = data.vwap
    context.volume = data.volume
    context.trend = data.trend
    context.session = data.session
    context.volatility_regime = data.volatility_regime
    context.timeframe = data.timeframe
    context.higher_timeframe = data.higher_timeframe
    context.data_source = data.data_source
    context.raw = data.raw
    context.captured_at = captured_at


def capture_for_trade(db: Session, trade: Trade) -> MarketContext:
    """Capture (or refresh) the market fingerprint for a trade. Idempotent."""
    captured_at = trade.opened_at or datetime.now(UTC)
    data = get_market_data_provider().get_context(trade.symbol, captured_at)

    context = market_context_repo.get_for_trade(db, trade.id)
    if context is None:
        context = MarketContext(trade_id=trade.id, user_id=trade.user_id, captured_at=captured_at)
        _apply(context, data, captured_at)
        return market_context_repo.add(db, context)

    _apply(context, data, captured_at)
    db.flush()
    return context


def get_for_trade(db: Session, trade_id: uuid.UUID) -> MarketContext | None:
    return market_context_repo.get_for_trade(db, trade_id)
