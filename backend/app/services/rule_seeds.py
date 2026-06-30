"""Default risk rules seeded per user (DRD Phase 5)."""

from decimal import Decimal

from app.models.rule import RuleSeverity, RuleType

DEFAULT_RULES: list[dict[str, object]] = [
    {
        "rule_type": RuleType.max_risk_per_trade,
        "threshold": Decimal("2.0"),  # percent
        "severity": RuleSeverity.block,
    },
    {
        "rule_type": RuleType.daily_loss_limit,
        "threshold": Decimal("5.0"),  # percent of account
        "severity": RuleSeverity.block,
    },
    {
        "rule_type": RuleType.weekly_loss_limit,
        "threshold": Decimal("10.0"),  # percent of account
        "severity": RuleSeverity.block,
    },
    {
        "rule_type": RuleType.consecutive_loss_limit,
        "threshold": Decimal("3"),  # count
        "severity": RuleSeverity.warning,
    },
]
