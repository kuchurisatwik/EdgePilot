def _register(client, email="trader@example.com", password="supersecret", name="Trader"):
    return client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "name": name},
    )


def test_register_returns_token_and_user(client):
    res = _register(client)
    assert res.status_code == 201
    body = res.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == "trader@example.com"
    assert body["user"]["name"] == "Trader"
    # Refresh token delivered as an httpOnly cookie, never in the body.
    assert "tc_refresh" in res.cookies
    assert "refresh_token" not in body


def test_register_duplicate_email_rejected(client):
    _register(client)
    res = _register(client, name="Other")
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "email_taken"


def test_login_success_and_wrong_password(client):
    _register(client)
    ok = client.post(
        "/api/auth/login",
        json={"email": "trader@example.com", "password": "supersecret"},
    )
    assert ok.status_code == 200
    assert ok.json()["access_token"]

    bad = client.post(
        "/api/auth/login",
        json={"email": "trader@example.com", "password": "wrongpass"},
    )
    assert bad.status_code == 401
    assert bad.json()["error"]["code"] == "invalid_credentials"


def test_me_requires_auth(client):
    token = _register(client).json()["access_token"]
    ok = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert ok.status_code == 200
    assert ok.json()["email"] == "trader@example.com"

    anon = client.get("/api/auth/me")
    assert anon.status_code == 401


def test_refresh_rotates_and_logout_revokes(client):
    _register(client)

    refreshed = client.post("/api/auth/refresh")
    assert refreshed.status_code == 200
    new_access = refreshed.json()["access_token"]
    # The freshly issued access token authenticates.
    assert (
        client.get("/api/auth/me", headers={"Authorization": f"Bearer {new_access}"}).status_code
        == 200
    )

    # A second rotation still works (the cookie was rotated each time).
    assert client.post("/api/auth/refresh").status_code == 200

    # Capture the current (valid) refresh token, then log out to revoke it.
    revoked = client.cookies.get("tc_refresh")
    assert client.post("/api/auth/logout").status_code == 200

    # Replaying the revoked token is rejected server-side (not just cookie-cleared).
    client.cookies.set("tc_refresh", revoked, path="/api/auth")
    after_logout = client.post("/api/auth/refresh")
    assert after_logout.status_code == 401
    assert after_logout.json()["error"]["code"] == "revoked_refresh"


def test_refresh_without_cookie_rejected(client):
    res = client.post("/api/auth/refresh")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "no_refresh"
