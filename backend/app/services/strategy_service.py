"""Strategy business logic (per-user scoped, with default seeding)."""

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.strategy import RiskAppetite, Strategy
from app.repositories import strategy_repo
from app.schemas.strategy import StrategyCreate, StrategyUpdate
from app.services.strategy_seeds import DEFAULT_STRATEGIES


def ensure_defaults(db: Session, user_id: uuid.UUID) -> None:
    """Idempotently seed the six default strategies for a user."""
    if strategy_repo.has_any_default(db, user_id):
        return
    for seed in DEFAULT_STRATEGIES:
        strategy_repo.add(
            db,
            Strategy(
                user_id=user_id,
                name=str(seed["name"]),
                description=str(seed["description"]),
                risk_appetite=seed["risk_appetite"]
                if isinstance(seed["risk_appetite"], RiskAppetite)
                else RiskAppetite.moderate,
                is_default=True,
                is_active=True,
            ),
        )


def list_strategies(db: Session, user_id: uuid.UUID) -> list[Strategy]:
    ensure_defaults(db, user_id)
    return strategy_repo.list_for_user(db, user_id, active_only=True)


def get_strategy(db: Session, user_id: uuid.UUID, strategy_id: uuid.UUID) -> Strategy:
    strategy = strategy_repo.get(db, user_id, strategy_id)
    if strategy is None:
        raise NotFoundError("Strategy not found.")
    return strategy


def create_strategy(db: Session, user_id: uuid.UUID, payload: StrategyCreate) -> Strategy:
    if strategy_repo.name_exists(db, user_id, payload.name):
        raise ValidationError("A strategy with this name already exists.", code="name_taken")
    return strategy_repo.add(
        db,
        Strategy(
            user_id=user_id,
            name=payload.name,
            description=payload.description,
            risk_appetite=payload.risk_appetite,
            notes=payload.notes,
            is_default=False,
            is_active=True,
        ),
    )


def update_strategy(
    db: Session, user_id: uuid.UUID, strategy_id: uuid.UUID, payload: StrategyUpdate
) -> Strategy:
    strategy = get_strategy(db, user_id, strategy_id)
    data = payload.model_dump(exclude_unset=True)
    new_name = data.get("name")
    if new_name and strategy_repo.name_exists(db, user_id, new_name, exclude_id=strategy_id):
        raise ValidationError("A strategy with this name already exists.", code="name_taken")
    for field, value in data.items():
        setattr(strategy, field, value)
    db.flush()
    return strategy


def delete_strategy(db: Session, user_id: uuid.UUID, strategy_id: uuid.UUID) -> None:
    strategy = get_strategy(db, user_id, strategy_id)
    if strategy.is_default:
        raise ValidationError(
            "Default strategies cannot be deleted; you can deactivate custom ones.",
            code="default_protected",
        )
    # Soft-delete custom strategies so historical trades keep referencing them (M3+).
    strategy.is_active = False
    db.flush()
