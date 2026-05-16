from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ping_returns_pong() -> None:
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.text == "pong"

def test_healthz_returns_ok() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status":"ok"}

def test_version_returns_defaults() -> None:
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {
        "version": "dev",
        "commit": "local"
    }