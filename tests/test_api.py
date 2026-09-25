from fastapi.testclient import TestClient

from main import app


def test_health_route():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["project"] == "MACCY-CREATIONS"


def test_auth_requires_token():
    client = TestClient(app)
    response = client.get("/api/auth/me")
    assert response.status_code == 401
