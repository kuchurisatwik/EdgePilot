"""Similar-trade scoring — deterministic and pure (NOT the LLM).

MVP reduced feature set: strategy + direction (hard gates) then a weighted
distance over reward:risk, risk %, and session. Market indicators are added to
the vector later, once a real feed is wired. The LLM only narrates this result.
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.models.ai_insight import Recommendation

_RR_SCALE = Decimal("3")
_RISK_SCALE = Decimal("2")
_W_RR = Decimal("0.5")
_W_RISK = Decimal("0.2")
_W_SESSION = Decimal("0.3")
_Q = Decimal("0.0001")


def _q(value: Decimal) -> Decimal:
    return value.quantize(_Q, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class SimTrade:
    trade_id: str
    strategy_id: str
    direction: str
    rr_ratio: Decimal | None
    risk_pct: Decimal
    session: str
    r_multiple: Decimal | None = None
    is_win: bool | None = None


@dataclass(frozen=True)
class Match:
    trade: SimTrade
    similarity: Decimal


@dataclass(frozen=True)
class CohortStats:
    count: int
    win_rate: Decimal | None
    avg_r: Decimal | None
    avg_similarity: Decimal | None


def _numeric_sim(a: Decimal, b: Decimal, scale: Decimal) -> Decimal:
    return max(Decimal(0), Decimal(1) - (abs(a - b) / scale))


def score(target: SimTrade, candidate: SimTrade) -> Decimal:
    rr_a = target.rr_ratio if target.rr_ratio is not None else Decimal(0)
    rr_b = candidate.rr_ratio if candidate.rr_ratio is not None else Decimal(0)
    rr_sim = _numeric_sim(rr_a, rr_b, _RR_SCALE)
    risk_sim = _numeric_sim(target.risk_pct, candidate.risk_pct, _RISK_SCALE)
    session_sim = Decimal(1) if target.session == candidate.session else Decimal(0)
    return _q(_W_RR * rr_sim + _W_RISK * risk_sim + _W_SESSION * session_sim)


def find_similar(
    target: SimTrade,
    candidates: list[SimTrade],
    *,
    min_similarity: Decimal,
    limit: int = 20,
) -> list[Match]:
    matches: list[Match] = []
    for candidate in candidates:
        if candidate.trade_id == target.trade_id:
            continue
        # Hard gates: same strategy AND same direction.
        if candidate.strategy_id != target.strategy_id:
            continue
        if candidate.direction != target.direction:
            continue
        similarity = score(target, candidate)
        if similarity >= min_similarity:
            matches.append(Match(trade=candidate, similarity=similarity))
    matches.sort(key=lambda m: m.similarity, reverse=True)
    return matches[:limit]


def cohort_stats(matches: list[Match]) -> CohortStats:
    n = len(matches)
    if n == 0:
        return CohortStats(0, None, None, None)
    wins = sum(1 for m in matches if m.trade.is_win)
    r_values = [m.trade.r_multiple for m in matches if m.trade.r_multiple is not None]
    avg_r = _q(sum(r_values, Decimal(0)) / Decimal(len(r_values))) if r_values else None
    avg_similarity = _q(sum((m.similarity for m in matches), Decimal(0)) / Decimal(n))
    return CohortStats(n, _q(Decimal(wins) / Decimal(n)), avg_r, avg_similarity)


def recommend(stats: CohortStats, *, min_matches: int) -> Recommendation:
    if stats.count < min_matches or stats.win_rate is None:
        return Recommendation.insufficient
    win_rate = stats.win_rate
    avg_r = stats.avg_r if stats.avg_r is not None else Decimal(0)
    if win_rate >= Decimal("0.6") and avg_r >= Decimal(1):
        return Recommendation.take
    if win_rate >= Decimal("0.5"):
        return Recommendation.reduce
    return Recommendation.avoid
