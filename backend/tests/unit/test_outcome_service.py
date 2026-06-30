from decimal import Decimal

from app.models.trade import TradeDirection, TradeResult
from app.services.outcome_service import compute_outcome

D = Decimal


def test_long_win():
    # 20 units, entry 100, exit 110 -> +200 pnl; risk 100 -> R = 2.
    o = compute_outcome(
        direction=TradeDirection.long,
        entry_price=D("100"),
        exit_price=D("110"),
        position_size=D("20"),
        risk_amount=D("100"),
    )
    assert o.pnl == D("200")
    assert o.r_multiple == D("2")
    assert o.result == TradeResult.win


def test_long_loss():
    o = compute_outcome(
        direction=TradeDirection.long,
        entry_price=D("100"),
        exit_price=D("95"),
        position_size=D("20"),
        risk_amount=D("100"),
    )
    assert o.pnl == D("-100")
    assert o.r_multiple == D("-1")
    assert o.result == TradeResult.loss


def test_short_win():
    # short 20 units, entry 100, exit 90 -> +200 pnl.
    o = compute_outcome(
        direction=TradeDirection.short,
        entry_price=D("100"),
        exit_price=D("90"),
        position_size=D("20"),
        risk_amount=D("100"),
    )
    assert o.pnl == D("200")
    assert o.r_multiple == D("2")
    assert o.result == TradeResult.win


def test_short_loss():
    o = compute_outcome(
        direction=TradeDirection.short,
        entry_price=D("100"),
        exit_price=D("105"),
        position_size=D("20"),
        risk_amount=D("100"),
    )
    assert o.pnl == D("-100")
    assert o.r_multiple == D("-1")
    assert o.result == TradeResult.loss


def test_breakeven():
    o = compute_outcome(
        direction=TradeDirection.long,
        entry_price=D("100"),
        exit_price=D("100"),
        position_size=D("20"),
        risk_amount=D("100"),
    )
    assert o.pnl == D("0")
    assert o.result == TradeResult.breakeven


def test_fractional_crypto():
    # 0.1 BTC, entry 60000, exit 62000 -> +200 pnl; risk 100 -> R = 2.
    o = compute_outcome(
        direction=TradeDirection.long,
        entry_price=D("60000"),
        exit_price=D("62000"),
        position_size=D("0.1"),
        risk_amount=D("100"),
    )
    assert o.pnl == D("200")
    assert o.r_multiple == D("2")
