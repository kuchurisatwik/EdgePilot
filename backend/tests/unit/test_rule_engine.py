from decimal import Decimal

from app.models.rule import RuleSeverity, RuleStatus, RuleType
from app.schemas.rule import RuleViolation
from app.services.rule_engine import decide


def _violation(severity: RuleSeverity) -> RuleViolation:
    return RuleViolation(
        rule_type=RuleType.max_risk_per_trade,
        severity=severity,
        message="x",
        observed=Decimal("1"),
        threshold=Decimal("1"),
    )


def test_decide_pass_when_empty():
    assert decide([]) == RuleStatus.PASS


def test_decide_warning():
    assert decide([_violation(RuleSeverity.warning)]) == RuleStatus.WARNING


def test_decide_block():
    assert decide([_violation(RuleSeverity.block)]) == RuleStatus.BLOCK


def test_decide_block_dominates_warning():
    assert (
        decide([_violation(RuleSeverity.warning), _violation(RuleSeverity.block)])
        == RuleStatus.BLOCK
    )
