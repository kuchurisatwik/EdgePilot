from datetime import UTC, datetime
from decimal import Decimal

from app.services.analytics_engine import (
    TradeStat,
    derive_session,
    equity_curve,
    group_performance,
    max_drawdown,
    summarize,
    trade_score,
)

D = Decimal


def _stat(pnl, r=None, hour=10, strat="s1", name="Breakout", risk="100", session="london"):
    return TradeStat(
        pnl=D(pnl),
        r_multiple=D(r) if r is not None else None,
        closed_at=datetime(2026, 1, 1, hour, tzinfo=UTC),
        strategy_id=strat,
        strategy_name=name,
        risk_amount=D(risk),
        session=session,
    )


def test_summarize_basic():
    stats = [_stat("200", "2", hour=10), _stat("-100", "-1", hour=11), _stat("150", "1.5", hour=12)]
    s = summarize(stats)
    assert s.trade_count == 3
    assert s.win_rate == D("0.6667")
    assert s.profit_factor == D("3.5")  # 350 / 100
    assert s.net_pnl == D("250")
    assert s.expectancy == D("83.33")  # 250 / 3
    assert s.average_r == D("0.8333")  # (2 - 1 + 1.5) / 3
    assert s.gross_profit == D("350")
    assert s.gross_loss == D("100")


def test_profit_factor_none_without_losses():
    s = summarize([_stat("100", "1"), _stat("50", "0.5")])
    assert s.profit_factor is None
    assert s.win_rate == D("1")


def test_summarize_empty():
    s = summarize([])
    assert s.trade_count == 0
    assert s.win_rate is None
    assert s.profit_factor is None
    assert s.expectancy is None
    assert s.net_pnl == D("0")


def test_equity_curve_and_drawdown():
    stats = [_stat("200", hour=10), _stat("-100", hour=11), _stat("150", hour=12)]
    points = equity_curve(stats, D("10000"))
    assert [p.equity for p in points] == [D("10200"), D("10100"), D("10250")]
    assert [p.drawdown for p in points] == [D("0"), D("100"), D("0")]
    assert max_drawdown(points) == D("100")


def test_average_r_ignores_none():
    s = summarize([_stat("100", "2"), _stat("50", None)])
    assert s.average_r == D("2")


def test_group_performance_by_strategy():
    stats = [
        _stat("200", strat="a", name="A"),
        _stat("-50", strat="a", name="A"),
        _stat("100", strat="b", name="B"),
    ]
    groups = dict(group_performance(stats, key_fn=lambda s: s.strategy_id))
    assert groups["a"].trade_count == 2
    assert groups["a"].net_pnl == D("150")
    assert groups["b"].trade_count == 1


def test_derive_session():
    assert derive_session(datetime(2026, 1, 1, 3, tzinfo=UTC)) == "asia"
    assert derive_session(datetime(2026, 1, 1, 10, tzinfo=UTC)) == "london"
    assert derive_session(datetime(2026, 1, 1, 18, tzinfo=UTC)) == "newyork"


def test_trade_score():
    def score(rr, risk, default, overridden):
        return trade_score(
            rr_ratio=D(rr),
            risk_pct=D(risk),
            default_risk_pct=D(default),
            rule_overridden=overridden,
        )

    assert score("2", "1", "1", False) == 100
    assert score("1", "1", "1", False) == 80
    assert score("2", "1", "1", True) == 70
    # Over-risking halves the risk component (30 -> 15): 40 + 15 + 30 = 85.
    assert score("2", "2", "1", False) == 85
