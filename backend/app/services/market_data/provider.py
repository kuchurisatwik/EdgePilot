"""Market data provider seam.

- StubMarketDataProvider (default): session from time; indicators 'unknown'.
- BinanceProvider: fetches public klines (no API key) and computes real
  ATR/RSI/VWAP/volume + trend/volatility. A flaky feed never blocks a trade
  open — it falls back to session-only.

Selected by ``settings.market_data_provider`` ("stub" | "binance").
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol

import httpx

from app.core.config import settings
from app.models.market_context import (
    MarketDataSource,
    MarketSession,
    MarketTrend,
    VolatilityRegime,
)
from app.services import analytics_engine
from app.services.market_data.indicators import Candle, compute_indicators

_BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"


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
        return MarketContextData(
            atr=None,
            rsi=None,
            vwap=None,
            volume=None,
            trend=MarketTrend.unknown,
            session=MarketSession(analytics_engine.derive_session(at_time)),
            volatility_regime=VolatilityRegime.unknown,
            timeframe=timeframe,
            higher_timeframe=higher_timeframe,
            data_source=MarketDataSource.stub,
            raw=None,
        )


class BinanceProvider:
    """Public Binance klines (keyless). Computes a real market fingerprint."""

    def __init__(self, timeout: float = 5.0) -> None:
        self._timeout = timeout

    def _fetch(self, symbol: str, interval: str, limit: int = 100) -> list[Candle]:
        binance_symbol = symbol.replace("_", "").replace("-", "").upper()
        response = httpx.get(
            _BINANCE_KLINES_URL,
            params={"symbol": binance_symbol, "interval": interval, "limit": limit},
            timeout=self._timeout,
        )
        response.raise_for_status()
        return [
            Candle(
                open=Decimal(str(row[1])),
                high=Decimal(str(row[2])),
                low=Decimal(str(row[3])),
                close=Decimal(str(row[4])),
                volume=Decimal(str(row[5])),
            )
            for row in response.json()
        ]

    def get_context(
        self,
        symbol: str,
        at_time: datetime,
        timeframe: str = "5m",
        higher_timeframe: str = "1h",
    ) -> MarketContextData:
        session = MarketSession(analytics_engine.derive_session(at_time))
        try:
            candles = self._fetch(symbol, timeframe)
            indicators = compute_indicators(candles)
            return MarketContextData(
                atr=indicators.atr,
                rsi=indicators.rsi,
                vwap=indicators.vwap,
                volume=indicators.volume,
                trend=indicators.trend,
                session=session,
                volatility_regime=indicators.volatility_regime,
                timeframe=timeframe,
                higher_timeframe=higher_timeframe,
                data_source=MarketDataSource.provider,
                raw={"symbol": symbol, "interval": timeframe, "candles": len(candles)},
            )
        except (httpx.HTTPError, ValueError, KeyError, IndexError):
            # Never block a trade open on a flaky feed — fall back to session-only.
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
                raw={"error": "market_data_unavailable"},
            )


def get_market_data_provider() -> MarketDataProvider:
    if settings.market_data_provider.lower() == "binance":
        return BinanceProvider()
    return StubMarketDataProvider()
