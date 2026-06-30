import pytest

from app.core.config import settings

PNG = b"\x89PNG\r\n\x1a\nfake-image-bytes"


@pytest.fixture(autouse=True)
def _storage_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "screenshot_dir", str(tmp_path))


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
    trade = client.post(
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
    return headers, trade["id"]


def _upload(
    client, headers, trade_id, slot="entry_trade_tf", content=PNG, content_type="image/png"
):
    return client.post(
        f"/api/trades/{trade_id}/screenshots",
        headers=headers,
        files={"file": ("chart.png", content, content_type)},
        data={"slot": slot},
    )


def test_upload_list_and_stream(client):
    headers, trade_id = _setup(client)
    res = _upload(client, headers, trade_id)
    assert res.status_code == 201
    body = res.json()
    assert body["slot"] == "entry_trade_tf"
    assert body["url"] == f"/api/screenshots/{body['id']}"

    listing = client.get(f"/api/trades/{trade_id}/screenshots", headers=headers)
    assert len(listing.json()) == 1

    stream = client.get(body["url"], headers=headers)
    assert stream.status_code == 200
    assert stream.headers["content-type"].startswith("image/png")
    assert stream.content == PNG


def test_replace_same_slot(client):
    headers, trade_id = _setup(client)
    _upload(client, headers, trade_id)
    _upload(client, headers, trade_id, content=b"\x89PNG\r\n\x1a\nsecond")
    listing = client.get(f"/api/trades/{trade_id}/screenshots", headers=headers)
    assert len(listing.json()) == 1  # same slot replaced, not duplicated


def test_reject_bad_type(client):
    headers, trade_id = _setup(client)
    res = _upload(client, headers, trade_id, content=b"hello", content_type="text/plain")
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "bad_image_type"


def test_reject_too_large(client, monkeypatch):
    monkeypatch.setattr("app.services.screenshot_service.MAX_SIZE_BYTES", 8)
    headers, trade_id = _setup(client)
    res = _upload(client, headers, trade_id, content=PNG)  # PNG is > 8 bytes
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "file_too_large"


def test_delete(client):
    headers, trade_id = _setup(client)
    sid = _upload(client, headers, trade_id).json()["id"]
    assert client.delete(f"/api/screenshots/{sid}", headers=headers).status_code == 204
    assert client.get(f"/api/screenshots/{sid}", headers=headers).status_code == 404
    assert client.get(f"/api/trades/{trade_id}/screenshots", headers=headers).json() == []


def test_isolation(client):
    headers, trade_id = _setup(client, email="owner@example.com")
    sid = _upload(client, headers, trade_id).json()["id"]
    other, _ = _setup(client, email="intruder@example.com")
    assert client.get(f"/api/screenshots/{sid}", headers=other).status_code == 404
    assert _upload(client, other, trade_id).status_code == 404  # not their trade


def test_requires_auth(client):
    res = client.get("/api/screenshots/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 401
