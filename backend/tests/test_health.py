from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] in {"ok", "unavailable"}


def test_chat_rejects_empty_messages():
    response = client.post("/api/chat", json={"messages": []})
    assert response.status_code == 422
