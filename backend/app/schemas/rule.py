"""Rule configuration + evaluation schemas."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.rule import RuleSeverity, RuleStatus, RuleType


class RuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_type: RuleType
    threshold: Decimal
    severity: RuleSeverity
    is_enabled: bool


class RuleUpdate(BaseModel):
    threshold: Decimal | None = Field(default=None, ge=0)
    severity: RuleSeverity | None = None
    is_enabled: bool | None = None


class RuleViolation(BaseModel):
    rule_type: RuleType
    severity: RuleSeverity
    message: str
    observed: Decimal
    threshold: Decimal


class RuleEvaluationResult(BaseModel):
    status: RuleStatus
    violations: list[RuleViolation]
