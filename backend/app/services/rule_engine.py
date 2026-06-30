"""Rule Engine — validates a planned trade against the user's risk rules.

Outputs PASS / WARNING / BLOCK. The decision function is pure; the evaluation
reads recent closed trades (loss limits / streaks) but never mutates risk and
never overrides the Risk Engine.
"""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.orm import Session

from app.models.rule import RuleSeverity, RuleStatus, RuleType
from app.repositories import rule_repo, trade_repo
from app.schemas.rule import RuleEvaluationResult, RuleViolation

_HUNDRED = Decimal("100")


def decide(violations: list[RuleViolation]) -> RuleStatus:
    if any(v.severity == RuleSeverity.block for v in violations):
        return RuleStatus.BLOCK
    if any(v.severity == RuleSeverity.warning for v in violations):
        return RuleStatus.WARNING
    return RuleStatus.PASS


def _start_of_day(now: datetime) -> datetime:
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def _start_of_week(now: datetime) -> datetime:
    return _start_of_day(now) - timedelta(days=now.weekday())


def _loss_limit_violation(
    db: Session,
    user_id: uuid.UUID,
    *,
    rule_type: RuleType,
    severity: RuleSeverity,
    threshold: Decimal,
    since: datetime,
    max_loss: Decimal,
    account_size: Decimal,
    label: str,
) -> RuleViolation | None:
    net = trade_repo.realized_pnl_since(db, user_id, since)
    realized_loss = -net if net < 0 else Decimal("0")
    projected = realized_loss + max_loss
    limit_amount = account_size * threshold / _HUNDRED
    if projected <= limit_amount:
        return None
    projected_pct = (projected / account_size * _HUNDRED).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return RuleViolation(
        rule_type=rule_type,
        severity=severity,
        message=(
            f"This trade could push {label} loss to {projected_pct}% of account, "
            f"over your {threshold}% limit."
        ),
        observed=projected_pct,
        threshold=threshold,
    )


def evaluate(
    db: Session,
    user_id: uuid.UUID,
    *,
    risk_pct: Decimal,
    max_loss: Decimal,
    account_size: Decimal,
    now: datetime | None = None,
) -> RuleEvaluationResult:
    now = now or datetime.now(UTC)
    rules = {r.rule_type: r for r in rule_repo.list_for_user(db, user_id) if r.is_enabled}
    violations: list[RuleViolation] = []

    rule = rules.get(RuleType.max_risk_per_trade)
    if rule is not None and risk_pct > rule.threshold:
        violations.append(
            RuleViolation(
                rule_type=RuleType.max_risk_per_trade,
                severity=rule.severity,
                message=f"Risk {risk_pct}% exceeds your max of {rule.threshold}% per trade.",
                observed=risk_pct,
                threshold=rule.threshold,
            )
        )

    if account_size > 0:
        for rule_type, since, label in (
            (RuleType.daily_loss_limit, _start_of_day(now), "daily"),
            (RuleType.weekly_loss_limit, _start_of_week(now), "weekly"),
        ):
            rule = rules.get(rule_type)
            if rule is None:
                continue
            violation = _loss_limit_violation(
                db,
                user_id,
                rule_type=rule_type,
                severity=rule.severity,
                threshold=rule.threshold,
                since=since,
                max_loss=max_loss,
                account_size=account_size,
                label=label,
            )
            if violation is not None:
                violations.append(violation)

    rule = rules.get(RuleType.consecutive_loss_limit)
    if rule is not None:
        streak = trade_repo.consecutive_loss_count(db, user_id)
        if Decimal(streak) >= rule.threshold:
            violations.append(
                RuleViolation(
                    rule_type=RuleType.consecutive_loss_limit,
                    severity=rule.severity,
                    message=(
                        f"You have {streak} consecutive losses "
                        f"(limit {rule.threshold}). Consider a break."
                    ),
                    observed=Decimal(streak),
                    threshold=rule.threshold,
                )
            )

    return RuleEvaluationResult(status=decide(violations), violations=violations)
