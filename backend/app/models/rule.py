"""Risk rule model (Rule Engine configuration)."""

import enum
import uuid
from decimal import Decimal

from sqlalchemy import Boolean, Enum, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class RuleType(enum.StrEnum):
    max_risk_per_trade = "max_risk_per_trade"  # threshold = percent
    daily_loss_limit = "daily_loss_limit"  # threshold = percent of account
    weekly_loss_limit = "weekly_loss_limit"  # threshold = percent of account
    consecutive_loss_limit = "consecutive_loss_limit"  # threshold = count


class RuleSeverity(enum.StrEnum):
    warning = "warning"
    block = "block"


class RuleStatus(enum.StrEnum):
    PASS = "PASS"
    WARNING = "WARNING"
    BLOCK = "BLOCK"


class RiskRule(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "risk_rules"
    __table_args__ = (UniqueConstraint("user_id", "rule_type", name="uq_rule_user_type"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    rule_type: Mapped[RuleType] = mapped_column(
        Enum(RuleType, native_enum=False, length=30), nullable=False
    )
    threshold: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    severity: Mapped[RuleSeverity] = mapped_column(
        Enum(RuleSeverity, native_enum=False, length=10), nullable=False
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
