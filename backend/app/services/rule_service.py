"""Risk rule management (per-user, with default seeding)."""

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.rule import RiskRule, RuleType
from app.repositories import rule_repo
from app.schemas.rule import RuleUpdate
from app.services.rule_seeds import DEFAULT_RULES


def ensure_default_rules(db: Session, user_id: uuid.UUID) -> None:
    """Idempotently seed the four default rules for a user."""
    if rule_repo.has_any(db, user_id):
        return
    for seed in DEFAULT_RULES:
        rule_repo.add(
            db,
            RiskRule(
                user_id=user_id,
                rule_type=seed["rule_type"],
                threshold=seed["threshold"],
                severity=seed["severity"],
                is_enabled=True,
            ),
        )


def list_rules(db: Session, user_id: uuid.UUID) -> list[RiskRule]:
    ensure_default_rules(db, user_id)
    return rule_repo.list_for_user(db, user_id)


def update_rule(
    db: Session, user_id: uuid.UUID, rule_type: RuleType, payload: RuleUpdate
) -> RiskRule:
    rule = rule_repo.get_by_type(db, user_id, rule_type)
    if rule is None:
        raise NotFoundError("Rule not found.")
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(rule, field, value)
    db.flush()
    return rule
