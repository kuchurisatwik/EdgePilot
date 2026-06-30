from decimal import Decimal

from app.models.market_context import MarketTrend, VolatilityRegime
from app.services.market_data.indicators import (
    Candle,
    atr,
    classify_trend,
    classify_volatility,
    compute_indicators,
    rsi,
    vwap,
)

D = Decimal


def _c(close, high=None, low=None, volume="1"):
    close = D(close)
    return Candle(
        open=close,
        high=D(high) if high is not None else close + 5,
        low=D(low) if low is not None else close - 5,
        close=close,
        volume=D(volume),
    )


def test_vwap():
    candles = [
        Candle(open=D("100"), high=D("110"), low=D("90"), close=D("100"), volume=D("10")),
        Candle(open=D("110"), high=D("120"), low=D("100"), close=D("110"), volume=D("20")),
    ]
    # (100*10 + 110*20) / 30 = 106.66666667
    assert vwap(candles) == D("106.66666667")


def test_atr_insufficient_data():
    assert atr([_c("100") for _ in range(5)], period=14) is None


def test_atr_constant_range():
    # Flat closes, high=close+5, low=close-5 -> every true range = 10 -> ATR = 10.
    candles = [_c("100", high="105", low="95") for _ in range(15)]
    assert atr(candles, period=14) == D("10")


def test_rsi_all_gains_is_100():
    candles = [_c(str(100 + i)) for i in range(15)]  # strictly increasing closes
    assert rsi(candles, period=14) == D("100")


def test_rsi_insufficient_data():
    assert rsi([_c("100") for _ in range(5)], period=14) is None


def test_classify_trend_uptrend():
    candles = [_c(str(100 + i)) for i in range(20)]  # ascending
    assert classify_trend(candles, period=20) == MarketTrend.uptrend


def test_classify_volatility():
    assert classify_volatility(D("100"), D("10")) == VolatilityRegime.high  # 10%
    assert classify_volatility(D("100"), D("2")) == VolatilityRegime.normal  # 2%
    assert classify_volatility(D("100"), D("0.5")) == VolatilityRegime.low  # 0.5%
    assert classify_volatility(D("100"), None) == VolatilityRegime.unknown


def test_compute_indicators():
    candles = [_c("100", high="105", low="95") for _ in range(20)]
    result = compute_indicators(candles)
    assert result.atr == D("10")
    assert result.vwap is not None
    assert result.volume == D("1")
    assert result.volatility_regime == VolatilityRegime.high
