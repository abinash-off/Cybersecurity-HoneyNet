from fastapi.testclient import TestClient

from app.auth import hash_password
from app.config import get_settings
import app.api.auth as auth_mod

auth_mod._hashed = hash_password(get_settings().admin_password)

from app.main import app  # noqa: E402

client = TestClient(app)


def test_health_public():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in {"ONLINE", "WARNING", "OFFLINE"}
    assert "services" in body


def test_stats_requires_auth():
    resp = client.get("/api/stats")
    assert resp.status_code == 401


def test_login_and_stats():
    settings = get_settings()
    resp = client.post("/api/auth/login/json", json={"username": settings.admin_username, "password": settings.admin_password})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    stats = client.get("/api/stats", headers={"Authorization": f"Bearer {token}"})
    assert stats.status_code == 200
    assert "total_attacks" in stats.json()


def test_bad_login():
    resp = client.post("/api/auth/login/json", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401
