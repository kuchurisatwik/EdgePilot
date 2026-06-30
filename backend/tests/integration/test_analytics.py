def _setup(client, email="t@example.com", account=10000, risk=1):
    token = client.post(
        "/api/auth/register",
        json={"email": email, "password": "supersecret", "name": "Trader"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.put(
        "/api/settings", headers=headers, json={"account_size": account, "default_risk_pct": risk}
    )
    strategy_id = client.get("/api/strategies", headers=headers).json()[0]["id"]
    return headers, strategy_id


def _plan(client, headers, strategy_id, **over):
    body = {
        "strategy_id": strategy_id,
        "symbol": "BTC_USDT",
        "direction": "long",
        "entry_price": 100,
        "stop_loss": 95,
        "take_profit": 110,
    }
    body.update(over)
    return client.post("/api/trades/plan", headers=headers, json=body).json()


def _open(client, headers, trade_id):
    client.post(f"/api/trades/{trade_id}/open", headers=headers, json={})


def _closed(client, headers, strategy_id, exit_price, **over):
    t = _plan(client, headers, strategy_id, **over)
    _open(client, headers, t["id"])
    return client.post(
        f"/api/trades/{t['id']}/close", headers=headers, json={"exit_price": exit_price}
    ).json()


def test_summary_metrics(client):
    headers, strategy_id = _setup(client)
    _closed(client, headers, strategy_id, 110)  # +200, win, R=2
    _closed(client, headers, strategy_id, 95)  # -100, loss, R=-1

    s = client.get("/api/analytics/summary", headers=headers).json()
    assert s["trade_count"] == 2
    assert float(s["win_rate"]) == 0.5
    assert float(s["profit_factor"]) == 2.0  # 200 / 100
    assert float(s["expectancy"]) == 50.0  # 100 / 2
    assert float(s["average_r"]) == 0.5  # (2 - 1) / 2
    assert float(s["net_pnl"]) == 100.0
    assert float(s["max_drawdown"]) >= 0.0


def test_summary_insufficient_data(client):
    headers, _ = _setup(client)
    s = client.get("/api/analytics/summary", headers=headers).json()
    assert s["trade_count"] == 0
    assert s["win_rate"] is None
    assert s["profit_factor"] is None
    assert float(s["net_pnl"]) == 0.0


def test_strategy_performance(client):
    headers, strategy_id = _setup(client)
    _closed(client, headers, strategy_id, 110)
    _closed(client, headers, strategy_id, 95)
    groups = client.get("/api/analytics/strategy", headers=headers).json()
    assert len(groups) == 1
    assert groups[0]["trade_count"] == 2
    assert groups[0]["label"]  # strategy name


def test_session_performance(client):
    headers, strategy_id = _setup(client)
    _closed(client, headers, strategy_id, 110)
    groups = client.get("/api/analytics/session", headers=headers).json()
    assert len(groups) >= 1
    assert sum(g["trade_count"] for g in groups) == 1


def test_equity_curve(client):
    headers, strategy_id = _setup(client)
    _closed(client, headers, strategy_id, 110)
    _closed(client, headers, strategy_id, 95)
    body = client.get("/api/analytics/equity-curve", headers=headers).json()
    assert float(body["starting_balance"]) == 10000.0
    assert len(body["points"]) == 2


def test_period_performance(client):
    headers, strategy_id = _setup(client)
    _closed(client, headers, strategy_id, 110)
    monthly = client.get("/api/analytics/period?period=monthly", headers=headers).json()
    assert len(monthly) == 1
    assert monthly[0]["trade_count"] == 1


def test_dashboard(client):
    headers, strategy_id = _setup(client)
    _closed(client, headers, strategy_id, 110)  # +200
    _closed(client, headers, strategy_id, 95)  # -100
    opened = _plan(client, headers, strategy_id)  # leave one open
    _open(client, headers, opened["id"])

    d = client.get("/api/analytics/dashboard", headers=headers).json()
    assert float(d["account_balance"]) == 10100.0
    assert float(d["realized_pnl"]) == 100.0
    assert float(d["today_pnl"]) == 100.0
    assert float(d["risk_exposure"]) == 100.0  # one open trade, 1% of 10,000
    assert d["closed_trades"] == 2
    assert d["open_trades"] == 1
    assert d["trade_score"] is not None
    assert 0 <= d["trade_score"] <= 100


def test_analytics_isolation(client):
    a_headers, a_strategy = _setup(client, email="a@example.com")
    _closed(client, a_headers, a_strategy, 110)
    b_headers, _ = _setup(client, email="b@example.com")
    assert client.get("/api/analytics/summary", headers=b_headers).json()["trade_count"] == 0


def test_analytics_requires_auth(client):
    assert client.get("/api/analytics/summary").status_code == 401
    assert client.get("/api/analytics/dashboard").status_code == 401
