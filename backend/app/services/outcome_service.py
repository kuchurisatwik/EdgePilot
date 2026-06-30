"""Trade outcome computation (pure functions).

R-multiple is dollar-based: pnl / risk_amount (the per-trade snapshot). This is
authoritative because it handles partial/early exits, not just exit-at-target.
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.models.trade import TradeDirection, TradeResult

_MONEY_Q = Decimal("0.01")
_RATIO_Q = Decimal("0.0001")


@dataclass(frozen=True)
class TradeOutcome:
    pnl: Decimal
    r_multiple: Decimal | None
    result: TradeResult


def _q(value: Decimal, quant: Decimal) -> Decimal:
    return value.quantize(quant, rounding=ROUND_HALF_UP)


def compute_outcome(
    *,
    direction: TradeDirection,
    entry_price: Decimal,
    exit_price: Decimal,
    position_size: Decimal,
    risk_amount: Decimal,
) -> TradeOutcome:
    sign = Decimal(1) if direction == TradeDirection.long else Decimal(-1)
    pnl = (exit_price - entry_price) * position_size * sign

    r_multiple = pnl / risk_amount if risk_amount > 0 else None

    if pnl > 0:
        result = TradeResult.win
    elif pnl < 0:
        result = TradeResult.loss
    else:
        result = TradeResult.breakeven

    return TradeOutcome(
        pnl=_q(pnl, _MONEY_Q),
        r_multiple=_q(r_multiple, _RATIO_Q) if r_multiple is not None else None,
        result=result,
    )
