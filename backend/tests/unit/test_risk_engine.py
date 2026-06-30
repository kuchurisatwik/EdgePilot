from decimal import Decimal

import pytest

from app.services.risk_engine import (
    ZeroRiskError,
    compute_breakdown,
    per_unit_risk,
    rr_ratio,
)

D = Decimal


def test_golden_long_trade():
    b = compute_breakdown(
        account_size=D("10000"), risk_pct=D("1"), entry=D("100"), stop=D("95"), target=D("110")
    )
    assert b.per_unit_risk == D("5")
    assert b.risk_amount == D("100")
    assert b.position_size == D("20")
    assert b.max_loss == D("100")
    assert b.capital_exposure == D("2000")
    assert b.rr_ratio == D("2")
    assert b.exposure_pct == D("20")


def test_short_trade_uses_absolute_distances():
    b = compute_breakdown(
        account_size=D("10000"), risk_pct=D("1"), entry=D("100"), stop=D("105"), target=D("90")
    )
    assert b.per_unit_risk == D("5")
    assert b.position_size == D("20")
    assert b.max_loss == D("100")
    assert b.rr_ratio == D("2")


def test_fractional_crypto_sizing():
    # BTC-like: 1% of 10,000 = 100 risk; 1,000 stop distance -> 0.1 BTC.
    b = compute_breakdown(
        account_size=D("10000"),
        risk_pct=D("1"),
        entry=D("60000"),
        stop=D("59000"),
        target=D("62000"),
    )
    assert b.per_unit_risk == D("1000")
    assert b.risk_amount == D("100")
    assert b.position_size == D("0.1")
    assert b.capital_exposure == D("6000")
    assert b.rr_ratio == D("2")


def test_entry_equals_stop_raises():
    with pytest.raises(ZeroRiskError):
        compute_breakdown(account_size=D("10000"), risk_pct=D("1"), entry=D("100"), stop=D("100"))
    with pytest.raises(ZeroRiskError):
        per_unit_risk(D("100"), D("100"))


def test_no_target_yields_no_rr():
    b = compute_breakdown(
        account_size=D("10000"), risk_pct=D("1"), entry=D("100"), stop=D("95"), target=None
    )
    assert b.rr_ratio is None
    assert b.position_size == D("20")


def test_zero_account_size_has_no_exposure_pct():
    b = compute_breakdown(account_size=D("0"), risk_pct=D("1"), entry=D("100"), stop=D("95"))
    assert b.risk_amount == D("0")
    assert b.position_size == D("0")
    assert b.exposure_pct is None


@pytest.mark.parametrize(
    ("account", "risk", "entry", "stop"),
    [
        (D("10000"), D("1"), D("100"), D("95")),
        (D("25000"), D("0.5"), D("3500"), D("3450")),
        (D("10000"), D("2"), D("0.5"), D("0.48")),
        (D("100000"), D("1.5"), D("60000"), D("58750")),
    ],
)
def test_max_loss_equals_risk_amount(account, risk, entry, stop):
    b = compute_breakdown(account_size=account, risk_pct=risk, entry=entry, stop=stop)
    assert b.max_loss == b.risk_amount


def test_rr_ratio_function():
    assert rr_ratio(D("100"), D("95"), D("115")) == D("3")
    assert rr_ratio(D("100"), D("90"), D("105")) == Decimal("0.5")


def test_half_risk_percent_scales_amount():
    b = compute_breakdown(account_size=D("10000"), risk_pct=D("0.5"), entry=D("100"), stop=D("95"))
    assert b.risk_amount == D("50")
    assert b.position_size == D("10")
