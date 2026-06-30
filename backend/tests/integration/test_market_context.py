def _setup(client, email="t@example.com"):
    token = client.post(
        "/api/auth/register",
        json={"email": email, "password": "supersecret", "name": "Trader"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.put(
        "/api/settings", headers=headers, json={"account_size": 10000, "default_risk_pct": 1}
    )
    strategy_id = client.get("/api/strategies", headers=headers).json()[0]["id"]
    return headers, strategy_id


def _plan(client, headers, strategy_id):
    return client.post(
        "/api/trades/plan",
        headers=headers,
        json={
            "strategy_id": strategy_id,
            "symbol": "BTC_USDT",
            "direction": "long",
            "entry_price": 100,
            "stop_loss": 95,
            "take_profit": 110,
        },
    ).json()


def _open(client, headers, trade_id):
    client.post(f"/api/trades/{trade_id}/open", headers=headers, json={})


def test_context_captured_on_open(client):
    headers, strategy_id = _setup(client)
    t = _plan(client, headers, strategy_id)
    _open(client, headers, t["id"])

    res = client.get(f"/api/market-context/{t['id']}", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["session"] in {"asia", "london", "newyork"}
    assert body["trend"] == "unknown"
    assert body["volatility_regime"] == "unknown"
    assert body["data_source"] == "stub"
    # Indicators are honestly unknown until a real feed is wired (never fabricated).
    assert body["atr"] is None
    assert body["rsi"] is None
    assert body["vwap"] is None
    assert body["volume"] is None


def test_no_context_for_draft(client):
    headers, strategy_id = _setup(client)
    t = _plan(client, headers, strategy_id)  # draft, never opened
    assert client.get(f"/api/market-context/{t['id']}", headers=headers).status_code == 404


def test_refresh_recaptures(client):
    headers, strategy_id = _setup(client)
    t = _plan(client, headers, strategy_id)
    _open(client, headers, t["id"])
    res = client.post(f"/api/market-context/{t['id']}/refresh", headers=headers)
    assert res.status_code == 200
    assert res.json()["session"] in {"asia", "london", "newyork"}


def test_context_isolated_per_user(client):
    headers, strategy_id = _setup(client, email="owner@example.com")
    t = _plan(client, headers, strategy_id)
    _open(client, headers, t["id"])
    other, _ = _setup(client, email="intruder@example.com")
    assert client.get(f"/api/market-context/{t['id']}", headers=other).status_code == 404


def test_requires_auth(client):
    res = client.get("/api/market-context/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 401
