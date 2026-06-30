"""AI insight model — caches generated narratives (cost + audit)."""

import enum
import uuid

from sqlalchemy import JSON, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class AIInsightType(enum.StrEnum):
    trade_summary = "trade_summary"
    performance = "performance"
    similar_trade = "similar_trade"
    strategy_review = "strategy_review"
    coaching = "coaching"


class AIConfidence(enum.StrEnum):
    high = "high"
    medium = "medium"
    low = "low"
    insufficient = "insufficient"


class Recommendation(enum.StrEnum):
    take = "take"
    reduce = "reduce"
    avoid = "avoid"
    insufficient = "insufficient"


class AIInsight(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ai_insights"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    trade_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("trades.id", ondelete="CASCADE"), index=True, nullable=True
    )
    insight_type: Mapped[AIInsightType] = mapped_column(
        Enum(AIInsightType, native_enum=False, length=20), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[AIConfidence] = mapped_column(
        Enum(AIConfidence, native_enum=False, length=12), nullable=False
    )
    # The pre-computed analytics that fed the narrative (auditability).
    inputs_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    model: Mapped[str] = mapped_column(String(60), nullable=False)
