"""Trade planning business logic.

All risk numbers come from the Risk Engine; this layer validates inputs, loads
per-user settings/strategy, persists the draft, and never recomputes risk itself.
"""

import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, RuleBlockError, ValidationError
from app.models.rule import RuleSeverity, RuleStatus
from app.models.trade import Trade, TradeDirection, TradeStatus
from app.repositories import trade_repo, user_repo
from app.schemas.rule import RuleEvaluationResult
from app.schemas.trade import RiskCalcRequest, TradePlanRequest
from app.services import rule_engine, strategy_service
from app.services.risk_engine import RiskBreakdown, ZeroRiskError, compute_breakdown


def _resolve_risk_pct(db: Session, user_id: uuid.UUID, requested: Decimal | None) -> Decimal:
    settings = user_repo.get_settings(db, user_id)
    if settings is None:
        raise NotFoundError("Settings not found.")
    return requested if requested is not None else settings.default_risk_pct


def _account_size(db: Session, user_id: uuid.UUID) -> Decimal:
    settings = user_repo.get_settings(db, user_id)
    if settings is None:
        raise NotFoundError("Settings not found.")
    return settings.account_size


def _validate_sides(
    direction: TradeDirection,
    entry: Decimal,
    stop: Decimal,
    target: Decimal | None,
) -> None:
    if entry == stop:
        raise ValidationError("Entry and stop loss must differ.", code="zero_risk")
    if direction == TradeDirection.long and stop >= entry:
        raise ValidationError("For a long, the stop loss must be below entry.", code="invalid_stop")
    if direction == TradeDirection.short and stop <= entry:
        raise ValidationError(
            "For a short, the stop loss must be above entry.", code="invalid_stop"
        )
    if target is not None:
        if direction == TradeDirection.long and target <= entry:
            raise ValidationError(
                "For a long, the target must be above entry.", code="invalid_target"
            )
        if direction == TradeDirection.short and target >= entry:
            raise ValidationError(
                "For a short, the target must be below entry.", code="invalid_target"
            )


def calculate_risk(
    db: Session, user_id: uuid.UUID, payload: RiskCalcRequest
) -> tuple[RiskBreakdown, RuleEvaluationResult]:
    """Stateless preview for the live Trade Planner panel: risk + rule verdict."""
    risk_pct = _resolve_risk_pct(db, user_id, payload.risk_pct)
    account_size = _account_size(db, user_id)
    try:
        breakdown = compute_breakdown(
            account_size=account_size,
            risk_pct=risk_pct,
            entry=payload.entry_price,
            stop=payload.stop_loss,
            target=payload.take_profit,
        )
    except ZeroRiskError as exc:
        raise ValidationError("Entry and stop loss must differ.", code="zero_risk") from exc

    rules = rule_engine.evaluate(
        db,
        user_id,
        risk_pct=risk_pct,
        max_loss=breakdown.max_loss,
        account_size=account_size,
    )
    return breakdown, rules


def plan_trade(db: Session, user_id: uuid.UUID, payload: TradePlanRequest) -> Trade:
    # Validate strategy ownership (404 if not the user's).
    strategy = strategy_service.get_strategy(db, user_id, payload.strategy_id)

    account_size = _account_size(db, user_id)
    if account_size <= 0:
        raise ValidationError(
            "Set your account size in Settings before planning a trade.",
            code="no_account_size",
        )

    _validate_sides(payload.direction, payload.entry_price, payload.stop_loss, payload.take_profit)
    risk_pct = _resolve_risk_pct(db, user_id, payload.risk_pct)

    breakdown = compute_breakdown(
        account_size=account_size,
        risk_pct=risk_pct,
        entry=payload.entry_price,
        stop=payload.stop_loss,
        target=payload.take_profit,
    )

    # Rule Engine: a BLOCK requires an explicit acknowledged override.
    rules = rule_engine.evaluate(
        db, user_id, risk_pct=risk_pct, max_loss=breakdown.max_loss, account_size=account_size
    )
    overridden = False
    if rules.status == RuleStatus.BLOCK:
        if not payload.acknowledge_override:
            blocking = "; ".join(
                v.message for v in rules.violations if v.severity == RuleSeverity.block
            )
            raise RuleBlockError(f"Trade blocked by your rules: {blocking}", code="rule_block")
        overridden = True

    trade = Trade(
        user_id=user_id,
        strategy_id=strategy.id,
        symbol=payload.symbol.strip().upper(),
        direction=payload.direction,
        order_type=payload.order_type,
        notes=payload.notes,
        thesis=payload.thesis,
        entry_price=payload.entry_price,
        stop_loss=payload.stop_loss,
        take_profit=payload.take_profit,
        current_price=payload.current_price,
        account_size_at_entry=account_size,
        risk_pct=risk_pct,
        per_unit_risk=breakdown.per_unit_risk,
        position_size=breakdown.position_size,
        risk_amount=breakdown.risk_amount,
        max_loss=breakdown.max_loss,
        rr_ratio=breakdown.rr_ratio,
        capital_exposure=breakdown.capital_exposure,
        status=TradeStatus.draft,
        rule_overridden=overridden,
    )
    return trade_repo.add(db, trade)


def get_trade(db: Session, user_id: uuid.UUID, trade_id: uuid.UUID) -> Trade:
    trade = trade_repo.get(db, user_id, trade_id)
    if trade is None:
        raise NotFoundError("Trade not found.")
    return trade


def update_trade(
    db: Session, user_id: uuid.UUID, trade_id: uuid.UUID, payload: TradePlanRequest
) -> Trade:
    trade = get_trade(db, user_id, trade_id)
    if trade.status != TradeStatus.draft:
        raise ValidationError("Only draft trades can be edited.", code="not_draft")

    strategy = strategy_service.get_strategy(db, user_id, payload.strategy_id)
    account_size = _account_size(db, user_id)
    if account_size <= 0:
        raise ValidationError(
            "Set your account size in Settings before planning a trade.",
            code="no_account_size",
        )
    _validate_sides(payload.direction, payload.entry_price, payload.stop_loss, payload.take_profit)
    risk_pct = _resolve_risk_pct(db, user_id, payload.risk_pct)

    breakdown = compute_breakdown(
        account_size=account_size,
        risk_pct=risk_pct,
        entry=payload.entry_price,
        stop=payload.stop_loss,
        target=payload.take_profit,
    )

    trade.strategy_id = strategy.id
    trade.symbol = payload.symbol.strip().upper()
    trade.direction = payload.direction
    trade.order_type = payload.order_type
    trade.notes = payload.notes
    trade.thesis = payload.thesis
    trade.entry_price = payload.entry_price
    trade.stop_loss = payload.stop_loss
    trade.take_profit = payload.take_profit
    trade.current_price = payload.current_price
    trade.account_size_at_entry = account_size
    trade.risk_pct = risk_pct
    trade.per_unit_risk = breakdown.per_unit_risk
    trade.position_size = breakdown.position_size
    trade.risk_amount = breakdown.risk_amount
    trade.max_loss = breakdown.max_loss
    trade.rr_ratio = breakdown.rr_ratio
    trade.capital_exposure = breakdown.capital_exposure
    db.flush()
    return trade


def list_trades(db: Session, user_id: uuid.UUID) -> list[Trade]:
    return trade_repo.list_for_user(db, user_id)


def validate_trade(
    db: Session, user_id: uuid.UUID, trade_id: uuid.UUID
) -> RuleEvaluationResult:
    trade = get_trade(db, user_id, trade_id)
    return rule_engine.evaluate(
        db,
        user_id,
        risk_pct=trade.risk_pct,
        max_loss=trade.max_loss,
        account_size=trade.account_size_at_entry,
    )
