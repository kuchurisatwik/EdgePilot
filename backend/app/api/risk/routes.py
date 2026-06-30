"""Risk calculation endpoint (stateless preview for the live Trade Planner)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.trade import RiskCalcRequest, RiskCalcResponse, TradeRiskBreakdown
from app.services import trade_service

router = APIRouter()


@router.post("/calculate", response_model=RiskCalcResponse)
def calculate_risk(
    payload: RiskCalcRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RiskCalcResponse:
    breakdown, rules = trade_service.calculate_risk(db, current_user.id, payload)
    return RiskCalcResponse(risk=TradeRiskBreakdown.from_breakdown(breakdown), rules=rules)
