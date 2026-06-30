"""Trade + risk-calculation schemas."""

import uuid
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.trade import OrderType, Trade, TradeDirection, TradeStatus
from app.schemas.rule import RuleEvaluationResult
from app.services.risk_engine import RiskBreakdown


class TradeRiskBreakdown(BaseModel):
    per_unit_risk: Decimal
    risk_amount: Decimal
    position_size: Decimal
    max_loss: Decimal
    capital_exposure: Decimal
    rr_ratio: Decimal | None
    exposure_pct: Decimal | None

    @classmethod
    def from_breakdown(cls, b: RiskBreakdown) -> "TradeRiskBreakdown":
        return cls(
            per_unit_risk=b.per_unit_risk,
            risk_amount=b.risk_amount,
            position_size=b.position_size,
            max_loss=b.max_loss,
            capital_exposure=b.capital_exposure,
            rr_ratio=b.rr_ratio,
            exposure_pct=b.exposure_pct,
        )


class RiskCalcRequest(BaseModel):
    entry_price: Decimal = Field(gt=0)
    stop_loss: Decimal = Field(gt=0)
    take_profit: Decimal | None = Field(default=None, gt=0)
    risk_pct: Decimal | None = Field(default=None, gt=0, le=100)


class TradePlanRequest(BaseModel):
    strategy_id: uuid.UUID
    symbol: str = Field(min_length=1, max_length=40)
    direction: TradeDirection
    order_type: OrderType = OrderType.market
    entry_price: Decimal = Field(gt=0)
    stop_loss: Decimal = Field(gt=0)
    take_profit: Decimal | None = Field(default=None, gt=0)
    current_price: Decimal | None = Field(default=None, gt=0)
    risk_pct: Decimal | None = Field(default=None, gt=0, le=100)
    notes: str | None = Field(default=None, max_length=4000)
    thesis: str | None = Field(default=None, max_length=4000)
    # Set true to proceed past a BLOCK verdict (override-with-acknowledgment).
    acknowledge_override: bool = False


class RiskCalcResponse(BaseModel):
    """Live preview: the Risk Engine breakdown + the Rule Engine verdict."""

    risk: TradeRiskBreakdown
    rules: RuleEvaluationResult


class TradeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    strategy_id: uuid.UUID
    symbol: str
    direction: TradeDirection
    order_type: OrderType
    entry_price: Decimal
    stop_loss: Decimal
    take_profit: Decimal | None
    current_price: Decimal | None
    account_size_at_entry: Decimal
    risk_pct: Decimal
    status: TradeStatus
    notes: str | None
    thesis: str | None
    created_at: datetime
    risk: TradeRiskBreakdown

    @classmethod
    def from_trade(cls, t: Trade) -> "TradeResponse":
        exposure_pct: Decimal | None = None
        if t.account_size_at_entry > 0:
            exposure_pct = (t.capital_exposure / t.account_size_at_entry * Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        return cls(
            id=t.id,
            strategy_id=t.strategy_id,
            symbol=t.symbol,
            direction=t.direction,
            order_type=t.order_type,
            entry_price=t.entry_price,
            stop_loss=t.stop_loss,
            take_profit=t.take_profit,
            current_price=t.current_price,
            account_size_at_entry=t.account_size_at_entry,
            risk_pct=t.risk_pct,
            status=t.status,
            notes=t.notes,
            thesis=t.thesis,
            created_at=t.created_at,
            risk=TradeRiskBreakdown(
                per_unit_risk=t.per_unit_risk,
                risk_amount=t.risk_amount,
                position_size=t.position_size,
                max_loss=t.max_loss,
                capital_exposure=t.capital_exposure,
                rr_ratio=t.rr_ratio,
                exposure_pct=exposure_pct,
            ),
        )
