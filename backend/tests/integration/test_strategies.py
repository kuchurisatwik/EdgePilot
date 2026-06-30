def _auth(client, email="t@example.com"):
    token = client.post(
        "/api/auth/register",
        json={"email": email, "password": "supersecret", "name": "Trader"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


DEFAULT_NAMES = {
    "Breakout",
    "Pullback",
    "Reversal",
    "Trend Following",
    "Scalping",
    "Range Trading",
}


def test_defaults_seeded_on_register(client):
    headers = _auth(client)
    res = client.get("/api/strategies", headers=headers)
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 6
    assert {s["name"] for s in items} == DEFAULT_NAMES
    assert all(s["is_default"] for s in items)


def test_defaults_seed_is_idempotent(client):
    headers = _auth(client)
    client.get("/api/strategies", headers=headers)
    second = client.get("/api/strategies", headers=headers)
    assert len(second.json()) == 6


def test_create_custom_strategy(client):
    headers = _auth(client)
    res = client.post(
        "/api/strategies",
        headers=headers,
        json={"name": "London Open", "risk_appetite": "aggressive", "notes": "0700 UTC"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["name"] == "London Open"
    assert body["risk_appetite"] == "aggressive"
    assert body["is_default"] is False
    assert len(client.get("/api/strategies", headers=headers).json()) == 7


def test_duplicate_name_rejected(client):
    headers = _auth(client)
    client.post("/api/strategies", headers=headers, json={"name": "Dup"})
    dup = client.post("/api/strategies", headers=headers, json={"name": "Dup"})
    assert dup.status_code == 422
    assert dup.json()["error"]["code"] == "name_taken"
    # Collides with a default name too.
    dup_default = client.post("/api/strategies", headers=headers, json={"name": "Breakout"})
    assert dup_default.status_code == 422


def test_update_strategy(client):
    headers = _auth(client)
    created = client.post("/api/strategies", headers=headers, json={"name": "Edit Me"}).json()
    res = client.put(
        f"/api/strategies/{created['id']}",
        headers=headers,
        json={"risk_appetite": "conservative", "notes": "updated"},
    )
    assert res.status_code == 200
    assert res.json()["risk_appetite"] == "conservative"
    assert res.json()["notes"] == "updated"


def test_default_cannot_be_deleted(client):
    headers = _auth(client)
    default_id = next(
        s["id"] for s in client.get("/api/strategies", headers=headers).json() if s["is_default"]
    )
    res = client.delete(f"/api/strategies/{default_id}", headers=headers)
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "default_protected"


def test_custom_delete_is_soft(client):
    headers = _auth(client)
    created = client.post("/api/strategies", headers=headers, json={"name": "Temp"}).json()
    res = client.delete(f"/api/strategies/{created['id']}", headers=headers)
    assert res.status_code == 204
    # No longer in the active list.
    names = {s["name"] for s in client.get("/api/strategies", headers=headers).json()}
    assert "Temp" not in names


def test_strategies_isolated_per_user(client):
    a = _auth(client, email="a@example.com")
    b = _auth(client, email="b@example.com")
    created = client.post("/api/strategies", headers=a, json={"name": "A-only"}).json()

    # B cannot see or fetch A's strategy.
    b_names = {s["name"] for s in client.get("/api/strategies", headers=b).json()}
    assert "A-only" not in b_names
    assert client.get(f"/api/strategies/{created['id']}", headers=b).status_code == 404


def test_strategies_require_auth(client):
    assert client.get("/api/strategies").status_code == 401
