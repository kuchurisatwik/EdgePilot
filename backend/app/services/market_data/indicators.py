"""Pure technical-indicator math over OHLCV candles.

Separated from any network I/O so it is fully unit-testable. Used by the
BinanceProvider to turn fetched klines into a market fingerprint.
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.models.market_context import MarketTrend, VolatilityRegime

_PRICE_Q = Decimal("0.00000001")
_RSI_Q = Decimal("0.0001")
_PCT_Q = Decimal("0.0001")


@dataclass(frozen=True)
class Candle:
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


@dataclass(frozen=True)
class IndicatorSet:
    atr: Decimal | None
    rsi: Decimal | None
    vwap: Decimal | None
    volume: Decimal | None
    trend: MarketTrend
    volatility_regime: VolatilityRegime


def _q(value: Decimal, quant: Decimal) -> Decimal:
    return value.quantize(quant, rounding=ROUND_HALF_UP)


def atr(candles: list[Candle], period: int = 14) -> Decimal | None:
    if len(candles) < period + 1:
        return None
    true_ranges: list[Decimal] = []
    for prev, cur in zip(candles[:-1], candles[1:], strict=False):
        true_ranges.append(
            max(cur.high - cur.low, abs(cur.high - prev.close), abs(cur.low - prev.close))
        )
    window = true_ranges[-period:]
    return _q(sum(window, Decimal(0)) / Decimal(period), _PRICE_Q)


def rsi(candles: list[Candle], period: int = 14) -> Decimal | None:
    if len(candles) < period + 1:
        return None
    gains = Decimal(0)
    losses = Decimal(0)
    for prev, cur in zip(candles[-(period + 1) : -1], candles[-period:], strict=False):
        change = cur.close - prev.close
        if change > 0:
            gains += change
        else:
            losses += -change
    if losses == 0:
        return _q(Decimal(100), _RSI_Q)
    rs = (gains / period) / (losses / period)
    return _q(Decimal(100) - (Decimal(100) / (Decimal(1) + rs)), _RSI_Q)


def vwap(candles: list[Candle]) -> Decimal | None:
    total_volume = sum((c.volume for c in candles), Decimal(0))
    if total_volume == 0:
        return None
    weighted = sum(
        (((c.high + c.low + c.close) / Decimal(3)) * c.volume for c in candles), Decimal(0)
    )
    return _q(weighted / total_volume, _PRICE_Q)


def classify_trend(candles: list[Candle], period: int = 20) -> MarketTrend:
    if len(candles) < period:
        return MarketTrend.unknown
    sma = sum((c.close for c in candles[-period:]), Decimal(0)) / Decimal(period)
    close = candles[-1].close
    if close > sma * Decimal("1.001"):
        return MarketTrend.uptrend
    if close < sma * Decimal("0.999"):
        return MarketTrend.downtrend
    return MarketTrend.sideways


def classify_volatility(close: Decimal, atr_value: Decimal | None) -> VolatilityRegime:
    if atr_value is None or close <= 0:
        return VolatilityRegime.unknown
    atr_pct = atr_value / close
    if atr_pct < Decimal("0.01"):
        return VolatilityRegime.low
    if atr_pct <= Decimal("0.03"):
        return VolatilityRegime.normal
    return VolatilityRegime.high


def compute_indicators(candles: list[Candle]) -> IndicatorSet:
    atr_value = atr(candles)
    return IndicatorSet(
        atr=atr_value,
        rsi=rsi(candles),
        vwap=vwap(candles),
        volume=_q(candles[-1].volume, _PRICE_Q) if candles else None,
        trend=classify_trend(candles),
        volatility_regime=classify_volatility(
            candles[-1].close if candles else Decimal(0), atr_value
        ),
    )
