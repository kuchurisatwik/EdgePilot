"""Market context endpoints (per-user scoped via trade ownership)."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.exceptions import NotFoundError
from app.models.user import User
from app.schemas.market_context import MarketContextResponse
from app.services import market_context_service, trade_service

router = APIRouter()


@router.get("/{trade_id}", response_model=MarketContextResponse)
def get_context(
    trade_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketContextResponse:
    trade_service.get_trade(db, current_user.id, trade_id)  # 404 if not the user's trade
    context = market_context_service.get_for_trade(db, trade_id)
    if context is None:
        raise NotFoundError("Market context not captured for this trade.")
    return MarketContextResponse.model_validate(context)


@router.post("/{trade_id}/refresh", response_model=MarketContextResponse)
def refresh_context(
    trade_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketContextResponse:
    trade = trade_service.get_trade(db, current_user.id, trade_id)
    context = market_context_service.capture_for_trade(db, trade)
    return MarketContextResponse.model_validate(context)
