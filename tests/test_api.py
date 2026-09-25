import os

from fastapi.testclient import TestClient

os.environ.setdefault("SUPABASE_URL", "https://kyrsdewrgqejoajhpfrn.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")

from main import app


def test_health_does_not_expose_database_url():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert "postgresql://" not in response.text


def test_protected_route_requires_bearer_token():
    client = TestClient(app)
    response = client.get("/auth/me")
    assert response.status_code == 401
