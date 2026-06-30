"""Trade domain model.

The full column set (including lifecycle/outcome fields used in M5/M6) is
defined now so later phases need no schema migrations. The computed risk values
are a snapshot captured at plan time from the Risk Engine.
"""

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.strategy import Strategy

_PRICE = Numeric(28, 8)
_SIZE = Numeric(28, 8)
_MONEY = Numeric(18, 2)
_RATIO = Numeric(12, 4)


class TradeDirection(enum.StrEnum):
    long = "long"
    short = "short"


class OrderType(enum.StrEnum):
    market = "market"
    limit = "limit"


class TradeStatus(enum.StrEnum):
    draft = "draft"
    open = "open"
    closed = "closed"


class TradeResult(enum.StrEnum):
    win = "win"
    loss = "loss"
    breakeven = "breakeven"


class Trade(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "trades"
    __table_args__ = (
        Index("ix_trades_user_status", "user_id", "status"),
        Index("ix_trades_user_strategy", "user_id", "strategy_id"),
        Index("ix_trades_user_created", "user_id", "created_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    strategy_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False
    )

    # User inputs
    symbol: Mapped[str] = mapped_column(String(40), nullable=False)
    direction: Mapped[TradeDirection] = mapped_column(
        Enum(TradeDirection, native_enum=False, length=10), nullable=False
    )
    order_type: Mapped[OrderType] = mapped_column(
        Enum(OrderType, native_enum=False, length=10),
        default=OrderType.market,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    thesis: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Price inputs
    entry_price: Mapped[Decimal] = mapped_column(_PRICE, nullable=False)
    stop_loss: Mapped[Decimal] = mapped_column(_PRICE, nullable=False)
    take_profit: Mapped[Decimal | None] = mapped_column(_PRICE, nullable=True)
    current_price: Mapped[Decimal | None] = mapped_column(_PRICE, nullable=True)

    # Risk inputs snapshot
    account_size_at_entry: Mapped[Decimal] = mapped_column(_MONEY, nullable=False)
    risk_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    # Computed risk snapshot (from the Risk Engine)
    per_unit_risk: Mapped[Decimal] = mapped_column(_PRICE, nullable=False)
    position_size: Mapped[Decimal] = mapped_column(_SIZE, nullable=False)
    risk_amount: Mapped[Decimal] = mapped_column(_MONEY, nullable=False)
    max_loss: Mapped[Decimal] = mapped_column(_MONEY, nullable=False)
    rr_ratio: Mapped[Decimal | None] = mapped_column(_RATIO, nullable=True)
    capital_exposure: Mapped[Decimal] = mapped_column(_MONEY, nullable=False)

    # Lifecycle
    status: Mapped[TradeStatus] = mapped_column(
        Enum(TradeStatus, native_enum=False, length=10),
        default=TradeStatus.draft,
        nullable=False,
    )
    rule_overridden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Outcome (filled at close in M5)
    exit_price: Mapped[Decimal | None] = mapped_column(_PRICE, nullable=True)
    pnl: Mapped[Decimal | None] = mapped_column(_MONEY, nullable=True)
    r_multiple: Mapped[Decimal | None] = mapped_column(_RATIO, nullable=True)
    result: Mapped[TradeResult | None] = mapped_column(
        Enum(TradeResult, native_enum=False, length=10), nullable=True
    )

    strategy: Mapped["Strategy"] = relationship(lazy="selectin")
