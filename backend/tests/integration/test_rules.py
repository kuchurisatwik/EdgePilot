import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.models.trade import OrderType, Trade, TradeDirection, TradeResult, TradeStatus


def _auth_and_ids(client, email="t@example.com", account=10000, risk=1):
    token = client.post(
        "/api/auth/register",
        json={"email": email, "password": "supersecret", "name": "Trader"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.put(
        "/api/settings", headers=headers, json={"account_size": account, "default_risk_pct": risk}
    )
    user_id = uuid.UUID(client.get("/api/auth/me", headers=headers).json()["id"])
    strategy_id = uuid.UUID(client.get("/api/strategies", headers=headers).json()[0]["id"])
    return headers, user_id, strategy_id


def _insert_loss(db, user_id, strategy_id, pnl="-100"):
    db.add(
        Trade(
            user_id=user_id,
            strategy_id=strategy_id,
            symbol="BTC_USDT",
            direction=TradeDirection.long,
            order_type=OrderType.market,
            entry_price=Decimal("100"),
            stop_loss=Decimal("95"),
            account_size_at_entry=Decimal("10000"),
            risk_pct=Decimal("1"),
            per_unit_risk=Decimal("5"),
            position_size=Decimal("20"),
            risk_amount=Decimal("100"),
            max_loss=Decimal("100"),
            capital_exposure=Decimal("2000"),
            status=TradeStatus.closed,
            closed_at=datetime.now(UTC),
            pnl=Decimal(pnl),
            r_multiple=Decimal("-1"),
            result=TradeResult.loss,
        )
    )
    db.flush()


def _calc(client, headers, **body):
    payload = {"entry_price": 100, "stop_loss": 95, "take_profit": 110}
    payload.update(body)
    return client.post("/api/risk/calculate", headers=headers, json=payload)


def test_default_rules_seeded(client):
    headers, _, _ = _auth_and_ids(client)
    rules = {r["rule_type"]: r for r in client.get("/api/rules", headers=headers).json()}
    assert set(rules) == {
        "max_risk_per_trade",
        "daily_loss_limit",
        "weekly_loss_limit",
        "consecutive_loss_limit",
    }
    assert float(rules["max_risk_per_trade"]["threshold"]) == 2.0
    assert rules["max_risk_per_trade"]["severity"] == "block"
    assert rules["consecutive_loss_limit"]["severity"] == "warning"


def test_update_rule(client):
    headers, _, _ = _auth_and_ids(client)
    res = client.put(
        "/api/rules/max_risk_per_trade", headers=headers, json={"threshold": 1.0}
    )
    assert res.status_code == 200
    assert float(res.json()["threshold"]) == 1.0


def test_calculate_returns_pass(client):
    headers, _, _ = _auth_and_ids(client, risk=1)
    res = _calc(client, headers)
    assert res.status_code == 200
    assert res.json()["rules"]["status"] == "PASS"
    assert float(res.json()["risk"]["risk_amount"]) == 100.0


def test_calculate_block_on_excess_risk(client):
    headers, _, _ = _auth_and_ids(client)
    client.put("/api/rules/max_risk_per_trade", headers=headers, json={"threshold": 1.0})
    res = _calc(client, headers, risk_pct=2)
    body = res.json()
    assert body["rules"]["status"] == "BLOCK"
    assert any(v["rule_type"] == "max_risk_per_trade" for v in body["rules"]["violations"])


def test_plan_blocked_without_override_then_succeeds_with_ack(client):
    headers, _, strategy_id = _auth_and_ids(client)
    client.put("/api/rules/max_risk_per_trade", headers=headers, json={"threshold": 1.0})
    base = {
        "strategy_id": str(strategy_id),
        "symbol": "BTC_USDT",
        "direction": "long",
        "entry_price": 100,
        "stop_loss": 95,
        "take_profit": 110,
        "risk_pct": 2,
    }

    blocked = client.post("/api/trades/plan", headers=headers, json=base)
    assert blocked.status_code == 409
    assert blocked.json()["error"]["code"] == "rule_block"

    ack = client.post(
        "/api/trades/plan", headers=headers, json={**base, "acknowledge_override": True}
    )
    assert ack.status_code == 201


def test_consecutive_losses_warn(client, db_session):
    headers, user_id, strategy_id = _auth_and_ids(client)
    for _ in range(3):
        _insert_loss(db_session, user_id, strategy_id)
    res = _calc(client, headers)
    body = res.json()
    assert body["rules"]["status"] == "WARNING"
    assert any(v["rule_type"] == "consecutive_loss_limit" for v in body["rules"]["violations"])


def test_daily_loss_limit_blocks(client, db_session):
    headers, user_id, strategy_id = _auth_and_ids(client)
    # Disable consecutive so we isolate the daily-loss block.
    client.put("/api/rules/consecutive_loss_limit", headers=headers, json={"is_enabled": False})
    # 5 x -100 = -500 realized today; + this trade's 100 max loss = 600 > 5% of 10,000 (500).
    for _ in range(5):
        _insert_loss(db_session, user_id, strategy_id)
    res = _calc(client, headers)
    body = res.json()
    assert body["rules"]["status"] == "BLOCK"
    assert any(v["rule_type"] == "daily_loss_limit" for v in body["rules"]["violations"])


def test_validate_endpoint(client):
    headers, _, strategy_id = _auth_and_ids(client)
    trade = client.post(
        "/api/trades/plan",
        headers=headers,
        json={
            "strategy_id": str(strategy_id),
            "symbol": "BTC_USDT",
            "direction": "long",
            "entry_price": 100,
            "stop_loss": 95,
            "take_profit": 110,
        },
    ).json()
    res = client.post(f"/api/trades/{trade['id']}/validate", headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "PASS"


def test_rules_require_auth(client):
    assert client.get("/api/rules").status_code == 401
