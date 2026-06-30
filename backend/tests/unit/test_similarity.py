from decimal import Decimal

from app.models.ai_insight import Recommendation
from app.services.ai.similarity import (
    CohortStats,
    Match,
    SimTrade,
    cohort_stats,
    find_similar,
    recommend,
    score,
)

D = Decimal


def _t(tid, strat="s1", direction="long", rr="2", risk="1", session="london", r=None, win=None):
    return SimTrade(
        trade_id=tid,
        strategy_id=strat,
        direction=direction,
        rr_ratio=D(rr) if rr is not None else None,
        risk_pct=D(risk),
        session=session,
        r_multiple=D(r) if r is not None else None,
        is_win=win,
    )


def test_score_identical_is_one():
    a = _t("a")
    b = _t("b")
    assert score(a, b) == D("1")


def test_score_drops_with_different_session():
    a = _t("a", session="london")
    b = _t("b", session="asia")
    # Loses the 0.3 session weight -> 0.7.
    assert score(a, b) == D("0.7")


def test_find_similar_gates_strategy_and_direction():
    target = _t("target", strat="s1", direction="long")
    candidates = [
        _t("same", strat="s1", direction="long"),
        _t("other_strategy", strat="s2", direction="long"),
        _t("other_direction", strat="s1", direction="short"),
    ]
    matches = find_similar(target, candidates, min_similarity=D("0.6"))
    assert [m.trade.trade_id for m in matches] == ["same"]


def test_min_similarity_filter():
    target = _t("target", rr="2", risk="1", session="london")
    far = _t("far", rr="2", risk="1", session="asia")  # 0.7 similarity
    assert find_similar(target, [far], min_similarity=D("0.8")) == []
    assert len(find_similar(target, [far], min_similarity=D("0.6"))) == 1


def test_cohort_stats():
    matches = [
        Match(trade=_t("a", r="2", win=True), similarity=D("1")),
        Match(trade=_t("b", r="-1", win=False), similarity=D("0.8")),
    ]
    stats = cohort_stats(matches)
    assert stats.count == 2
    assert stats.win_rate == D("0.5")
    assert stats.avg_r == D("0.5")  # (2 - 1) / 2
    assert stats.avg_similarity == D("0.9")


def test_recommend_thresholds():
    def rec(count, win_rate, avg_r):
        return recommend(CohortStats(count, D(win_rate), D(avg_r), D("1")), min_matches=5)

    assert rec(2, "1", "2") == Recommendation.insufficient
    assert rec(10, "0.7", "1.5") == Recommendation.take
    assert rec(10, "0.55", "0.2") == Recommendation.reduce
    assert rec(10, "0.3", "-0.5") == Recommendation.avoid
