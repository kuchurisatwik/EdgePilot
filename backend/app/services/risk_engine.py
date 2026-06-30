"""Risk Engine — the deterministic source of truth.

Pure functions over ``Decimal``. No I/O, no DB, no app imports. AI may read
these outputs but must never replace or override them. All money/size values are
computed at full precision and quantized to display precision once, at the end.
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

# Display/storage precision (crypto MVP: fractional sizes are normal).
_PRICE_Q = Decimal("0.00000001")  # 8 dp
_SIZE_Q = Decimal("0.00000001")  # 8 dp
_MONEY_Q = Decimal("0.01")  # 2 dp
_RATIO_Q = Decimal("0.0001")  # 4 dp
_PCT_Q = Decimal("0.01")  # 2 dp

_HUNDRED = Decimal("100")


class ZeroRiskError(ValueError):
    """Entry equals stop -> per-unit risk is zero (would divide by zero)."""


def _q(value: Decimal, quant: Decimal) -> Decimal:
    return value.quantize(quant, rounding=ROUND_HALF_UP)


def per_unit_risk(entry: Decimal, stop: Decimal) -> Decimal:
    risk = abs(entry - stop)
    if risk == 0:
        raise ZeroRiskError("Entry and stop loss must differ.")
    return risk


def risk_amount(account_size: Decimal, risk_pct: Decimal) -> Decimal:
    return account_size * (risk_pct / _HUNDRED)


def position_size(amount: Decimal, unit_risk: Decimal) -> Decimal:
    return amount / unit_risk


def rr_ratio(entry: Decimal, stop: Decimal, target: Decimal) -> Decimal:
    return abs(target - entry) / per_unit_risk(entry, stop)


def capital_exposure(size: Decimal, entry: Decimal) -> Decimal:
    return size * entry


@dataclass(frozen=True)
class RiskBreakdown:
    per_unit_risk: Decimal
    risk_amount: Decimal
    position_size: Decimal
    max_loss: Decimal
    capital_exposure: Decimal
    rr_ratio: Decimal | None
    exposure_pct: Decimal | None


def compute_breakdown(
    *,
    account_size: Decimal,
    risk_pct: Decimal,
    entry: Decimal,
    stop: Decimal,
    target: Decimal | None = None,
) -> RiskBreakdown:
    """Compute the full risk picture for a trade. Quantizes once at the end."""
    unit_risk = per_unit_risk(entry, stop)  # raises ZeroRiskError if entry == stop
    amount = risk_amount(account_size, risk_pct)
    size = position_size(amount, unit_risk)
    max_loss = size * unit_risk  # mathematically equals `amount`
    exposure = capital_exposure(size, entry)

    rr = abs(target - entry) / unit_risk if target is not None else None
    exposure_pct = (exposure / account_size * _HUNDRED) if account_size > 0 else None

    return RiskBreakdown(
        per_unit_risk=_q(unit_risk, _PRICE_Q),
        risk_amount=_q(amount, _MONEY_Q),
        position_size=_q(size, _SIZE_Q),
        max_loss=_q(max_loss, _MONEY_Q),
        capital_exposure=_q(exposure, _MONEY_Q),
        rr_ratio=_q(rr, _RATIO_Q) if rr is not None else None,
        exposure_pct=_q(exposure_pct, _PCT_Q) if exposure_pct is not None else None,
    )
