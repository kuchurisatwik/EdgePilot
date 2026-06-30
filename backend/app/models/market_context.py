"""Market Context model — a market fingerprint captured per trade.

In the crypto MVP the indicators are typically unknown (the stub provider only
derives the session). The storage and provider seam are in place so a real
crypto feed can backfill ATR/RSI/VWAP/volume later without service changes.
"""

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin

_NUM = Numeric(28, 8)


class MarketTrend(enum.StrEnum):
    uptrend = "uptrend"
    downtrend = "downtrend"
    sideways = "sideways"
    unknown = "unknown"


class MarketSession(enum.StrEnum):
    asia = "asia"
    london = "london"
    newyork = "newyork"
    unknown = "unknown"


class VolatilityRegime(enum.StrEnum):
    low = "low"
    normal = "normal"
    high = "high"
    unknown = "unknown"


class MarketDataSource(enum.StrEnum):
    stub = "stub"
    provider = "provider"
    manual = "manual"


class MarketContext(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "market_contexts"

    trade_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trades.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    atr: Mapped[Decimal | None] = mapped_column(_NUM, nullable=True)
    rsi: Mapped[Decimal | None] = mapped_column(Numeric(7, 4), nullable=True)
    vwap: Mapped[Decimal | None] = mapped_column(_NUM, nullable=True)
    volume: Mapped[Decimal | None] = mapped_column(_NUM, nullable=True)

    trend: Mapped[MarketTrend] = mapped_column(
        Enum(MarketTrend, native_enum=False, length=12), default=MarketTrend.unknown, nullable=False
    )
    session: Mapped[MarketSession] = mapped_column(
        Enum(MarketSession, native_enum=False, length=12),
        default=MarketSession.unknown,
        nullable=False,
    )
    volatility_regime: Mapped[VolatilityRegime] = mapped_column(
        Enum(VolatilityRegime, native_enum=False, length=12),
        default=VolatilityRegime.unknown,
        nullable=False,
    )

    timeframe: Mapped[str] = mapped_column(String(10), default="5m", nullable=False)
    higher_timeframe: Mapped[str] = mapped_column(String(10), default="1h", nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data_source: Mapped[MarketDataSource] = mapped_column(
        Enum(MarketDataSource, native_enum=False, length=12),
        default=MarketDataSource.stub,
        nullable=False,
    )
    raw: Mapped[dict | None] = mapped_column(JSON, nullable=True)
