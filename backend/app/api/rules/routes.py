"""Risk rule configuration endpoints (per-user scoped)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.rule import RuleType
from app.models.user import User
from app.schemas.rule import RuleResponse, RuleUpdate
from app.services import rule_service

router = APIRouter()


@router.get("", response_model=list[RuleResponse])
def list_rules(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[RuleResponse]:
    return [RuleResponse.model_validate(r) for r in rule_service.list_rules(db, current_user.id)]


@router.put("/{rule_type}", response_model=RuleResponse)
def update_rule(
    rule_type: RuleType,
    payload: RuleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RuleResponse:
    rule = rule_service.update_rule(db, current_user.id, rule_type, payload)
    return RuleResponse.model_validate(rule)
