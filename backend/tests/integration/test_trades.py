def _register(client, email="t@example.com"):
    token = client.post(
        "/api/auth/register",
        json={"email": email, "password": "supersecret", "name": "Trader"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _setup(client, email="t@example.com", account=10000, risk=1):
    headers = _register(client, email)
    client.put(
        "/api/settings", headers=headers, json={"account_size": account, "default_risk_pct": risk}
    )
    strategy_id = client.get("/api/strategies", headers=headers).json()[0]["id"]
    return headers, strategy_id


def _plan_body(strategy_id, **overrides):
    body = {
        "strategy_id": strategy_id,
        "symbol": "btc_usdt",
        "direction": "long",
        "order_type": "market",
        "entry_price": 100,
        "stop_loss": 95,
        "take_profit": 110,
    }
    body.update(overrides)
    return body


def test_risk_calculate(client):
    headers, _ = _setup(client)
    res = client.post(
        "/api/risk/calculate",
        headers=headers,
        json={"entry_price": 100, "stop_loss": 95, "take_profit": 110},
    )
    assert res.status_code == 200
    b = res.json()
    assert float(b["per_unit_risk"]) == 5.0
    assert float(b["risk_amount"]) == 100.0
    assert float(b["position_size"]) == 20.0
    assert float(b["max_loss"]) == 100.0
    assert float(b["capital_exposure"]) == 2000.0
    assert float(b["rr_ratio"]) == 2.0
    assert float(b["exposure_pct"]) == 20.0


def test_risk_calculate_zero_risk_rejected(client):
    headers, _ = _setup(client)
    res = client.post(
        "/api/risk/calculate", headers=headers, json={"entry_price": 100, "stop_loss": 100}
    )
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "zero_risk"


def test_risk_calculate_overrides_risk_pct(client):
    headers, _ = _setup(client)
    res = client.post(
        "/api/risk/calculate",
        headers=headers,
        json={"entry_price": 100, "stop_loss": 95, "risk_pct": 2},
    )
    assert float(res.json()["risk_amount"]) == 200.0
    assert res.json()["rr_ratio"] is None  # no target supplied


def test_plan_trade_creates_draft(client):
    headers, strategy_id = _setup(client)
    res = client.post("/api/trades/plan", headers=headers, json=_plan_body(strategy_id))
    assert res.status_code == 201
    t = res.json()
    assert t["status"] == "draft"
    assert t["symbol"] == "BTC_USDT"  # normalized
    assert float(t["risk"]["position_size"]) == 20.0
    assert float(t["risk"]["risk_amount"]) == 100.0
    assert float(t["risk"]["rr_ratio"]) == 2.0
    assert float(t["account_size_at_entry"]) == 10000.0


def test_plan_invalid_stop_side_rejected(client):
    headers, strategy_id = _setup(client)
    res = client.post(
        "/api/trades/plan",
        headers=headers,
        json=_plan_body(strategy_id, direction="long", stop_loss=105),
    )
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "invalid_stop"


def test_plan_invalid_target_side_rejected(client):
    headers, strategy_id = _setup(client)
    res = client.post(
        "/api/trades/plan",
        headers=headers,
        json=_plan_body(strategy_id, direction="long", take_profit=90),
    )
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "invalid_target"


def test_plan_requires_account_size(client):
    # Fresh user has account_size 0 until they set it.
    headers = _register(client, email="poor@example.com")
    strategy_id = client.get("/api/strategies", headers=headers).json()[0]["id"]
    res = client.post("/api/trades/plan", headers=headers, json=_plan_body(strategy_id))
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "no_account_size"


def test_plan_risk_pct_falls_back_to_settings(client):
    headers, strategy_id = _setup(client, account=10000, risk=1.5)
    res = client.post("/api/trades/plan", headers=headers, json=_plan_body(strategy_id))
    assert float(res.json()["risk"]["risk_amount"]) == 150.0
    assert float(res.json()["risk_pct"]) == 1.5


def test_plan_cross_user_strategy_404(client):
    _, a_strategy = _setup(client, email="a@example.com")
    b_headers, _ = _setup(client, email="b@example.com")
    res = client.post("/api/trades/plan", headers=b_headers, json=_plan_body(a_strategy))
    assert res.status_code == 404


def test_get_and_list_and_update_trade(client):
    headers, strategy_id = _setup(client)
    created = client.post("/api/trades/plan", headers=headers, json=_plan_body(strategy_id)).json()

    got = client.get(f"/api/trades/{created['id']}", headers=headers)
    assert got.status_code == 200
    assert got.json()["id"] == created["id"]

    listing = client.get("/api/trades", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1

    # Editing a draft recomputes the snapshot.
    updated = client.put(
        f"/api/trades/{created['id']}",
        headers=headers,
        json=_plan_body(strategy_id, stop_loss=90),
    )
    assert updated.status_code == 200
    assert float(updated.json()["risk"]["position_size"]) == 10.0  # 100 risk / 10 stop distance


def test_trade_isolation(client):
    headers, strategy_id = _setup(client, email="owner@example.com")
    created = client.post("/api/trades/plan", headers=headers, json=_plan_body(strategy_id)).json()
    other, _ = _setup(client, email="intruder@example.com")
    assert client.get(f"/api/trades/{created['id']}", headers=other).status_code == 404


def test_trades_require_auth(client):
    assert client.get("/api/trades").status_code == 401
    res = client.post("/api/risk/calculate", json={"entry_price": 1, "stop_loss": 2})
    assert res.status_code == 401
