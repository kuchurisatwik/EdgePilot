"""Market context response schema."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.market_context import (
    MarketDataSource,
    MarketSession,
    MarketTrend,
    VolatilityRegime,
)


class MarketContextResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trade_id: uuid.UUID
    atr: Decimal | None
    rsi: Decimal | None
    vwap: Decimal | None
    volume: Decimal | None
    trend: MarketTrend
    session: MarketSession
    volatility_regime: VolatilityRegime
    timeframe: str
    higher_timeframe: str
    captured_at: datetime
    data_source: MarketDataSource
