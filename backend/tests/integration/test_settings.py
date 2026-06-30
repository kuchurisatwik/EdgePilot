def _auth(client, email="t@example.com"):
    token = client.post(
        "/api/auth/register",
        json={"email": email, "password": "supersecret", "name": "Trader"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_settings_defaults(client):
    headers = _auth(client)
    res = client.get("/api/settings", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert float(body["account_size"]) == 0.0
    assert float(body["default_risk_pct"]) == 1.0
    assert body["quote_currency"] == "USDT"
    assert body["timezone"] == "UTC"


def test_settings_update_persists(client):
    headers = _auth(client)
    upd = client.put(
        "/api/settings",
        headers=headers,
        json={"account_size": 50000, "default_risk_pct": 1.5},
    )
    assert upd.status_code == 200
    assert float(upd.json()["account_size"]) == 50000.0

    again = client.get("/api/settings", headers=headers)
    assert float(again.json()["account_size"]) == 50000.0
    assert float(again.json()["default_risk_pct"]) == 1.5


def test_settings_validation(client):
    headers = _auth(client)
    # risk pct must be > 0 and <= 100
    bad = client.put("/api/settings", headers=headers, json={"default_risk_pct": 0})
    assert bad.status_code == 422


def test_settings_require_auth(client):
    assert client.get("/api/settings").status_code == 401


def test_settings_are_isolated_per_user(client):
    a = _auth(client, email="a@example.com")
    b = _auth(client, email="b@example.com")

    client.put("/api/settings", headers=a, json={"account_size": 1000})
    client.put("/api/settings", headers=b, json={"account_size": 2000})

    assert float(client.get("/api/settings", headers=a).json()["account_size"]) == 1000.0
    assert float(client.get("/api/settings", headers=b).json()["account_size"]) == 2000.0


def test_profile_update(client):
    headers = _auth(client)
    res = client.put("/api/profile", headers=headers, json={"name": "New Name"})
    assert res.status_code == 200
    assert res.json()["name"] == "New Name"
    assert client.get("/api/auth/me", headers=headers).json()["name"] == "New Name"
