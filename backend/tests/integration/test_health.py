def test_health_returns_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body == {"status": "ok", "db": "ok"}


def test_health_sets_request_id_header(client):
    response = client.get("/api/health")
    assert response.headers.get("x-request-id")
