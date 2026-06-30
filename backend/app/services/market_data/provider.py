"""Market data provider seam.

MVP ships a stub: the trading session is always computable from the timestamp,
but indicators (ATR/RSI/VWAP/volume) are 'unknown' until a real crypto feed
(e.g. Crypto.com / Binance public REST) is wired behind this same interface.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol

from app.models.market_context import (
    MarketDataSource,
    MarketSession,
    MarketTrend,
    VolatilityRegime,
)
from app.services import analytics_engine


@dataclass(frozen=True)
class MarketContextData:
    atr: Decimal | None
    rsi: Decimal | None
    vwap: Decimal | None
    volume: Decimal | None
    trend: MarketTrend
    session: MarketSession
    volatility_regime: VolatilityRegime
    timeframe: str
    higher_timeframe: str
    data_source: MarketDataSource
    raw: dict | None


class MarketDataProvider(Protocol):
    def get_context(
        self,
        symbol: str,
        at_time: datetime,
        timeframe: str = "5m",
        higher_timeframe: str = "1h",
    ) -> MarketContextData: ...


class StubMarketDataProvider:
    """Real session from time; indicators left unknown (never fabricated)."""

    def get_context(
        self,
        symbol: str,
        at_time: datetime,
        timeframe: str = "5m",
        higher_timeframe: str = "1h",
    ) -> MarketContextData:
        session = MarketSession(analytics_engine.derive_session(at_time))
        return MarketContextData(
            atr=None,
            rsi=None,
            vwap=None,
            volume=None,
            trend=MarketTrend.unknown,
            session=session,
            volatility_regime=VolatilityRegime.unknown,
            timeframe=timeframe,
            higher_timeframe=higher_timeframe,
            data_source=MarketDataSource.stub,
            raw=None,
        )


def get_market_data_provider() -> MarketDataProvider:
    """Factory selected by ``settings.market_data_provider`` (only 'stub' in MVP)."""
    # Future: if settings.market_data_provider == "binance": return BinanceProvider()
    return StubMarketDataProvider()
