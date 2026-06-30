"""Trade planning endpoints (per-user scoped via get_current_user)."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.rule import RuleEvaluationResult
from app.schemas.trade import TradePlanRequest, TradeResponse
from app.services import trade_service

router = APIRouter()


@router.post("/plan", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
def plan_trade(
    payload: TradePlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TradeResponse:
    trade = trade_service.plan_trade(db, current_user.id, payload)
    return TradeResponse.from_trade(trade)


@router.get("", response_model=list[TradeResponse])
def list_trades(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[TradeResponse]:
    return [TradeResponse.from_trade(t) for t in trade_service.list_trades(db, current_user.id)]


@router.get("/{trade_id}", response_model=TradeResponse)
def get_trade(
    trade_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TradeResponse:
    trade = trade_service.get_trade(db, current_user.id, trade_id)
    return TradeResponse.from_trade(trade)


@router.put("/{trade_id}", response_model=TradeResponse)
def update_trade(
    trade_id: uuid.UUID,
    payload: TradePlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TradeResponse:
    trade = trade_service.update_trade(db, current_user.id, trade_id, payload)
    return TradeResponse.from_trade(trade)


@router.post("/{trade_id}/validate", response_model=RuleEvaluationResult)
def validate_trade(
    trade_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RuleEvaluationResult:
    return trade_service.validate_trade(db, current_user.id, trade_id)
