"""AI endpoints (M9). AI explains pre-computed analytics; it never calculates."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.ai import AIInsightResponse, AISimilarRequest, SimilarTradeAnalysis
from app.services.ai import ai_service

router = APIRouter()


@router.get("/performance", response_model=AIInsightResponse)
def performance(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> AIInsightResponse:
    return ai_service.get_performance(db, current_user.id)


@router.get("/trades/{trade_id}/summary", response_model=AIInsightResponse)
def trade_summary(
    trade_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AIInsightResponse:
    return ai_service.get_trade_summary(db, current_user.id, trade_id)


@router.post("/similar", response_model=SimilarTradeAnalysis)
def similar(
    payload: AISimilarRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SimilarTradeAnalysis:
    return ai_service.get_similar(db, current_user.id, payload)
