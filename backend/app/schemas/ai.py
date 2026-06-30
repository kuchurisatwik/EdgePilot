"""AI insight + similar-trade schemas."""

import uuid
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.ai_insight import AIConfidence, AIInsightType, Recommendation
from app.models.trade import TradeDirection


class AIInsightResponse(BaseModel):
    insight_type: AIInsightType
    content: str
    confidence: AIConfidence


class AISimilarRequest(BaseModel):
    strategy_id: uuid.UUID
    direction: TradeDirection
    entry_price: Decimal = Field(gt=0)
    stop_loss: Decimal = Field(gt=0)
    take_profit: Decimal | None = Field(default=None, gt=0)
    risk_pct: Decimal | None = Field(default=None, gt=0, le=100)


class SimilarTradeAnalysis(BaseModel):
    match_count: int
    avg_similarity: Decimal | None
    historical_win_rate: Decimal | None
    historical_avg_r: Decimal | None
    recommendation: Recommendation
    reasoning: str
    confidence: AIConfidence
