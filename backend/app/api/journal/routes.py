"""Journal endpoints: filtered/paginated history + trade detail."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.trade import TradeResult, TradeStatus
from app.models.user import User
from app.schemas.trade import TradeListResponse, TradeResponse
from app.services import trade_service

router = APIRouter()


@router.get("", response_model=TradeListResponse)
def list_journal(
    strategy_id: uuid.UUID | None = Query(default=None),
    symbol: str | None = Query(default=None),
    result: TradeResult | None = Query(default=None),
    status: TradeStatus | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TradeListResponse:
    items, total = trade_service.list_journal(
        db,
        current_user.id,
        strategy_id=strategy_id,
        symbol=symbol,
        result=result,
        status=status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    return TradeListResponse(
        items=[TradeResponse.from_trade(t) for t in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{trade_id}", response_model=TradeResponse)
def get_journal_trade(
    trade_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TradeResponse:
    trade = trade_service.get_trade(db, current_user.id, trade_id)
    return TradeResponse.from_trade(trade)
