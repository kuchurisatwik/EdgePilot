"""Strategy CRUD endpoints (per-user scoped via get_current_user)."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.strategy import StrategyCreate, StrategyResponse, StrategyUpdate
from app.services import strategy_service

router = APIRouter()


@router.get("", response_model=list[StrategyResponse])
def list_strategies(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[StrategyResponse]:
    strategies = strategy_service.list_strategies(db, current_user.id)
    return [StrategyResponse.model_validate(s) for s in strategies]


@router.post("", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
def create_strategy(
    payload: StrategyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StrategyResponse:
    strategy = strategy_service.create_strategy(db, current_user.id, payload)
    return StrategyResponse.model_validate(strategy)


@router.get("/{strategy_id}", response_model=StrategyResponse)
def get_strategy(
    strategy_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StrategyResponse:
    strategy = strategy_service.get_strategy(db, current_user.id, strategy_id)
    return StrategyResponse.model_validate(strategy)


@router.put("/{strategy_id}", response_model=StrategyResponse)
def update_strategy(
    strategy_id: uuid.UUID,
    payload: StrategyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StrategyResponse:
    strategy = strategy_service.update_strategy(db, current_user.id, strategy_id, payload)
    return StrategyResponse.model_validate(strategy)


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_strategy(
    strategy_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    strategy_service.delete_strategy(db, current_user.id, strategy_id)
