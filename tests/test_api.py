from fastapi.testclient import TestClient

from main import app


def test_health_route():
    response = TestClient(app).get('/health')
    assert response.status_code == 200
    assert response.json()['project'] == 'MACCY-CREATIONS'


def test_static_assets_are_mounted():
    response = TestClient(app).get('/static/styles.css')
    assert response.status_code == 200


def test_local_dashboard_and_skills_api():
    client = TestClient(app)
    dashboard = client.get('/api/local/dashboard')
    skills = client.get('/api/local/skills')
    assert dashboard.status_code == 200
    assert skills.status_code == 200
    assert len(skills.json()) >= 1


def test_auth_requires_token():
    response = TestClient(app).get('/api/auth/me')
    assert response.status_code == 401
