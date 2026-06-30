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
        "symbol": "btc_usdt",
        "direction": "long",
        "entry_price": 100,
        "stop_loss": 95,
        "take_profit": 110,
    }
    body.update(over)
    return client.post("/api/trades/plan", headers=headers, json=body).json()


def _open(client, headers, trade_id, **body):
    return client.post(f"/api/trades/{trade_id}/open", headers=headers, json=body)


def _close(client, headers, trade_id, exit_price):
    return client.post(
        f"/api/trades/{trade_id}/close", headers=headers, json={"exit_price": exit_price}
    )


def test_full_lifecycle_long_win(client):
    headers, strategy_id = _setup(client)
    t = _plan(client, headers, strategy_id)
    assert t["status"] == "draft"

    opened = _open(client, headers, t["id"])
    assert opened.status_code == 200
    assert opened.json()["status"] == "open"
    assert opened.json()["opened_at"] is not None

    closed = _close(client, headers, t["id"], 110)
    assert closed.status_code == 200
    body = closed.json()
    assert body["status"] == "closed"
    assert float(body["pnl"]) == 200.0  # 20 units * (110 - 100)
    assert float(body["r_multiple"]) == 2.0
    assert body["result"] == "win"


def test_lifecycle_long_loss(client):
    headers, strategy_id = _setup(client)
    t = _plan(client, headers, strategy_id)
    _open(client, headers, t["id"])
    body = _close(client, headers, t["id"], 95).json()
    assert float(body["pnl"]) == -100.0
    assert float(body["r_multiple"]) == -1.0
    assert body["result"] == "loss"


def test_lifecycle_short_win(client):
    headers, strategy_id = _setup(client)
    t = _plan(client, headers, strategy_id, direction="short", stop_loss=105, take_profit=90)
    _open(client, headers, t["id"])
    body = _close(client, headers, t["id"], 90).json()
    assert float(body["pnl"]) == 200.0
    assert body["result"] == "win"


def test_illegal_transitions(client):
    headers, strategy_id = _setup(client)
    t = _plan(client, headers, strategy_id)

    # Cannot close a draft.
    assert _close(client, headers, t["id"], 110).status_code == 422

    _open(client, headers, t["id"])
    # Cannot re-open an open trade.
    assert _open(client, headers, t["id"]).status_code == 422
    # Cannot delete a non-draft.
    assert client.delete(f"/api/trades/{t['id']}", headers=headers).status_code == 422


def test_delete_draft(client):
    headers, strategy_id = _setup(client)
    t = _plan(client, headers, strategy_id)
    assert client.delete(f"/api/trades/{t['id']}", headers=headers).status_code == 204
    assert client.get(f"/api/trades/{t['id']}", headers=headers).status_code == 404


def test_journal_filters_and_pagination(client):
    headers, strategy_id = _setup(client)
    # One winner, one loser, one draft.
    win = _plan(client, headers, strategy_id)
    _open(client, headers, win["id"])
    _close(client, headers, win["id"], 110)
    loss = _plan(client, headers, strategy_id)
    _open(client, headers, loss["id"])
    _close(client, headers, loss["id"], 95)
    _plan(client, headers, strategy_id)  # stays draft

    all_trades = client.get("/api/journal", headers=headers).json()
    assert all_trades["total"] == 3

    wins = client.get("/api/journal?result=win", headers=headers).json()
    assert wins["total"] == 1
    assert wins["items"][0]["result"] == "win"

    closed = client.get("/api/journal?status=closed", headers=headers).json()
    assert closed["total"] == 2

    page1 = client.get("/api/journal?page=1&page_size=2", headers=headers).json()
    assert len(page1["items"]) == 2
    assert page1["total"] == 3
    page2 = client.get("/api/journal?page=2&page_size=2", headers=headers).json()
    assert len(page2["items"]) == 1


def test_journal_carries_strategy_name(client):
    headers, strategy_id = _setup(client)
    _plan(client, headers, strategy_id)
    item = client.get("/api/journal", headers=headers).json()["items"][0]
    assert item["strategy_name"]  # resolved from the relationship


def test_journal_detail_and_isolation(client):
    headers, strategy_id = _setup(client, email="owner@example.com")
    t = _plan(client, headers, strategy_id)
    assert client.get(f"/api/journal/{t['id']}", headers=headers).status_code == 200

    other, _ = _setup(client, email="intruder@example.com")
    assert client.get(f"/api/journal/{t['id']}", headers=other).status_code == 404


def test_open_blocked_then_override(client):
    headers, strategy_id = _setup(client)
    client.put("/api/rules/max_risk_per_trade", headers=headers, json={"threshold": 1.0})
    # Plan with override so the draft saves despite the BLOCK.
    t = _plan(client, headers, strategy_id, risk_pct=2, acknowledge_override=True)
    # Opening re-checks rules: blocked without ack, allowed with ack.
    assert _open(client, headers, t["id"]).status_code == 409
    assert _open(client, headers, t["id"], acknowledge_override=True).status_code == 200


def test_journal_requires_auth(client):
    assert client.get("/api/journal").status_code == 401
