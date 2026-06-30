"""Data access for cached AI insights."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_insight import AIInsight, AIInsightType


def get_for_trade(
    db: Session, user_id: uuid.UUID, trade_id: uuid.UUID, insight_type: AIInsightType
) -> AIInsight | None:
    return db.scalar(
        select(AIInsight).where(
            AIInsight.user_id == user_id,
            AIInsight.trade_id == trade_id,
            AIInsight.insight_type == insight_type,
        )
    )


def add(db: Session, insight: AIInsight) -> AIInsight:
    db.add(insight)
    db.flush()
    return insight
