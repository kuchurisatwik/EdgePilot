import pytest

from app.core.config import settings


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


def _closed(client, headers, strategy_id, exit_price=110):
    t = client.post(
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
    client.post(f"/api/trades/{t['id']}/open", headers=headers, json={})
    client.post(f"/api/trades/{t['id']}/close", headers=headers, json={"exit_price": exit_price})
    return t


def _similar_body(strategy_id):
    return {
        "strategy_id": strategy_id,
        "direction": "long",
        "entry_price": 100,
        "stop_loss": 95,
        "take_profit": 110,
    }


@pytest.fixture
def sufficient(monkeypatch):
    # Any user counts as having enough history; lower the cohort floor for tests.
    monkeypatch.setattr(settings, "ai_sufficient_days", 0)
    monkeypatch.setattr(settings, "ai_min_matches", 2)


def test_ai_requires_auth(client):
    assert client.get("/api/ai/performance").status_code == 401


def test_insufficient_data_gate(client):
    # Default 7-day floor + fresh user with no closed trades -> insufficient.
    headers, strategy_id = _setup(client)
    perf = client.get("/api/ai/performance", headers=headers).json()
    assert perf["confidence"] == "insufficient"
    assert "Not enough historical data" in perf["content"]

    sim = client.post("/api/ai/similar", headers=headers, json=_similar_body(strategy_id)).json()
    assert sim["recommendation"] == "insufficient"
    assert "Not enough historical data" in sim["reasoning"]


def test_performance_with_data(client, sufficient):
    headers, strategy_id = _setup(client)
    _closed(client, headers, strategy_id, 110)
    _closed(client, headers, strategy_id, 95)
    perf = client.get("/api/ai/performance", headers=headers).json()
    assert perf["confidence"] != "insufficient"
    assert "win rate" in perf["content"].lower()


def test_trade_summary_caches(client, sufficient):
    headers, strategy_id = _setup(client)
    t = _closed(client, headers, strategy_id, 110)
    first = client.get(f"/api/ai/trades/{t['id']}/summary", headers=headers).json()
    assert first["confidence"] == "medium"
    assert "win" in first["content"].lower()
    second = client.get(f"/api/ai/trades/{t['id']}/summary", headers=headers).json()
    assert second["content"] == first["content"]  # cached


def test_similar_recommendation(client, sufficient):
    headers, strategy_id = _setup(client)
    _closed(client, headers, strategy_id, 110)
    _closed(client, headers, strategy_id, 110)
    sim = client.post("/api/ai/similar", headers=headers, json=_similar_body(strategy_id)).json()
    assert sim["match_count"] >= 2
    assert sim["recommendation"] == "take"  # 100% win, avg 2R
    assert sim["reasoning"]


def test_summary_isolation(client, sufficient):
    headers, strategy_id = _setup(client, email="owner@example.com")
    t = _closed(client, headers, strategy_id, 110)
    other, _ = _setup(client, email="intruder@example.com")
    assert client.get(f"/api/ai/trades/{t['id']}/summary", headers=other).status_code == 404


def test_llm_path_uses_mock(client, sufficient, monkeypatch):
    class FakeLLM:
        last_prompt: str | None = None

        def complete(self, *, system: str, prompt: str) -> str:
            FakeLLM.last_prompt = prompt
            return "MOCKED NARRATIVE"

    monkeypatch.setattr("app.services.ai.ai_service.get_llm_client", lambda: FakeLLM())
    headers, strategy_id = _setup(client)
    _closed(client, headers, strategy_id, 110)
    perf = client.get("/api/ai/performance", headers=headers).json()
    assert perf["content"] == "MOCKED NARRATIVE"
    # Prompt carries the pre-computed analytics (AI explains, never calculates).
    assert "trade_count" in (FakeLLM.last_prompt or "")
