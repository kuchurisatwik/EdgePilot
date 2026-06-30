"""Analytics Engine — pure statistical functions. No AI, no DB, no I/O.

Operates on a lightweight ``TradeStat`` view of closed trades so it is fully
unit-testable. These outputs are exactly what the AI layer (M9+) will later
explain — it never recomputes them.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

_WR_Q = Decimal("0.0001")
_MONEY_Q = Decimal("0.01")
_RATIO_Q = Decimal("0.0001")
_PF_Q = Decimal("0.01")


def _q(value: Decimal, quant: Decimal) -> Decimal:
    return value.quantize(quant, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class TradeStat:
    pnl: Decimal
    r_multiple: Decimal | None
    closed_at: datetime
    strategy_id: str
    strategy_name: str
    risk_amount: Decimal
    session: str


@dataclass(frozen=True)
class StatsSummary:
    trade_count: int
    win_rate: Decimal | None
    profit_factor: Decimal | None
    expectancy: Decimal | None
    average_r: Decimal | None
    net_pnl: Decimal
    gross_profit: Decimal
    gross_loss: Decimal


@dataclass(frozen=True)
class EquityPoint:
    date: datetime
    equity: Decimal
    drawdown: Decimal


def derive_session(dt: datetime) -> str:
    """UTC time-of-day bucket (crypto is 24/7). Shared with Market Context (M7)."""
    hour = dt.hour
    if hour < 8:
        return "asia"
    if hour < 16:
        return "london"
    return "newyork"


def summarize(stats: list[TradeStat]) -> StatsSummary:
    n = len(stats)
    gross_profit = sum((s.pnl for s in stats if s.pnl > 0), Decimal(0))
    gross_loss = -sum((s.pnl for s in stats if s.pnl < 0), Decimal(0))
    net_pnl = sum((s.pnl for s in stats), Decimal(0))

    if n == 0:
        return StatsSummary(0, None, None, None, None, Decimal(0), Decimal(0), Decimal(0))

    wins = sum(1 for s in stats if s.pnl > 0)
    win_rate = _q(Decimal(wins) / Decimal(n), _WR_Q)
    profit_factor = _q(gross_profit / gross_loss, _PF_Q) if gross_loss > 0 else None
    expectancy = _q(net_pnl / Decimal(n), _MONEY_Q)

    r_values = [s.r_multiple for s in stats if s.r_multiple is not None]
    if r_values:
        average_r = _q(sum(r_values, Decimal(0)) / Decimal(len(r_values)), _RATIO_Q)
    else:
        average_r = None

    return StatsSummary(
        trade_count=n,
        win_rate=win_rate,
        profit_factor=profit_factor,
        expectancy=expectancy,
        average_r=average_r,
        net_pnl=_q(net_pnl, _MONEY_Q),
        gross_profit=_q(gross_profit, _MONEY_Q),
        gross_loss=_q(gross_loss, _MONEY_Q),
    )


def equity_curve(stats: list[TradeStat], starting_balance: Decimal) -> list[EquityPoint]:
    ordered = sorted(stats, key=lambda s: s.closed_at)
    equity = starting_balance
    peak = starting_balance
    points: list[EquityPoint] = []
    for s in ordered:
        equity += s.pnl
        peak = max(peak, equity)
        points.append(
            EquityPoint(
                date=s.closed_at,
                equity=_q(equity, _MONEY_Q),
                drawdown=_q(peak - equity, _MONEY_Q),
            )
        )
    return points


def max_drawdown(points: list[EquityPoint]) -> Decimal:
    return max((p.drawdown for p in points), default=Decimal(0))


def current_drawdown(points: list[EquityPoint]) -> Decimal:
    return points[-1].drawdown if points else Decimal(0)


def group_performance(
    stats: list[TradeStat], key_fn
) -> list[tuple[str, StatsSummary]]:
    groups: dict[str, list[TradeStat]] = {}
    for s in stats:
        groups.setdefault(key_fn(s), []).append(s)
    return [(key, summarize(items)) for key, items in groups.items()]


def trade_score(
    *,
    rr_ratio: Decimal | None,
    risk_pct: Decimal,
    default_risk_pct: Decimal,
    rule_overridden: bool,
) -> int:
    """Deterministic 0-100 quality score for a planned trade (owned by Analytics)."""
    rr = rr_ratio if rr_ratio is not None else Decimal(0)
    rr_component = min(rr / Decimal(2), Decimal(1)) * Decimal(40)
    if default_risk_pct > 0 and risk_pct > default_risk_pct:
        risk_component = Decimal(30) * (default_risk_pct / risk_pct)
    else:
        risk_component = Decimal(30)
    discipline_component = Decimal(0) if rule_overridden else Decimal(30)
    total = rr_component + risk_component + discipline_component
    return int(total.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
