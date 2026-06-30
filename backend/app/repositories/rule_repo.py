"""Data access for risk rules. Scoped by user_id."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rule import RiskRule, RuleType


def list_for_user(db: Session, user_id: uuid.UUID) -> list[RiskRule]:
    return list(
        db.scalars(select(RiskRule).where(RiskRule.user_id == user_id).order_by(RiskRule.rule_type))
    )


def get_by_type(db: Session, user_id: uuid.UUID, rule_type: RuleType) -> RiskRule | None:
    return db.scalar(
        select(RiskRule).where(RiskRule.user_id == user_id, RiskRule.rule_type == rule_type)
    )


def has_any(db: Session, user_id: uuid.UUID) -> bool:
    return db.scalar(select(RiskRule.id).where(RiskRule.user_id == user_id)) is not None


def add(db: Session, rule: RiskRule) -> RiskRule:
    db.add(rule)
    db.flush()
    return rule
