from fastapi.testclient import TestClient

from backend.app.core.rate_limit import login_rate_limit
from backend.app.db.base import Base
from backend.app.db.session import engine
from backend.app.main import app

client = TestClient(app)


def setup_function() -> None:
    client.cookies.clear()
    login_rate_limit.clear()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def register(email: str = "user@example.com", role: str = "user") -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "role": role},
    )
    assert response.status_code == 201


def login(email: str = "user@example.com") -> dict:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    assert response.status_code == 200
    return response.json()


def test_bearer_access_token_identifies_current_user() -> None:
    register()
    tokens = login()

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"


def test_missing_auth_returns_401_and_normal_user_admin_returns_403() -> None:
    register()

    missing = client.get("/api/v1/auth/me")
    assert missing.status_code == 401
    assert missing.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"

    tokens = login()
    forbidden = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "FORBIDDEN"


def test_admin_can_list_users() -> None:
    register(email="admin@example.com", role="admin")
    tokens = login(email="admin@example.com")

    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json()[0]["email"] == "admin@example.com"


def test_refresh_token_rotates_access_token() -> None:
    register()
    tokens = login()

    response = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.cookies.get("session_id")
    assert response.cookies.get("csrf_token")
    reused = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert reused.status_code == 401


def test_cookie_session_requires_csrf_for_mutating_protected_api() -> None:
    register()
    tokens = login()

    blocked = client.post(
        "/api/v1/posts/protected",
        json={"title": "csrf", "content": "missing token"},
    )
    assert blocked.status_code == 403
    assert blocked.json()["error"]["code"] == "CSRF_FAILED"

    allowed = client.post(
        "/api/v1/posts/protected",
        headers={"X-CSRF-Token": tokens["csrf_token"]},
        json={"title": "secure post", "content": "with csrf"},
    )
    assert allowed.status_code == 201
    assert allowed.json()["author_name"] == "user@example.com"


def test_ai_request_requires_authentication_and_records_user_id() -> None:
    unauthenticated = client.post("/api/v1/ai/requests", json={"prompt": "write sprint summary"})
    assert unauthenticated.status_code == 401

    register()
    tokens = login()
    created = client.post(
        "/api/v1/ai/requests",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={"prompt": "write sprint summary"},
    )

    assert created.status_code == 201
    assert created.json()["requester_id"] == 1
    assert "write sprint summary" in created.json()["result"]


def test_login_rate_limit_returns_429() -> None:
    register()

    for _ in range(5):
        response = client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "wrong"})
        assert response.status_code == 401

    limited = client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "wrong"})
    assert limited.status_code == 429
    assert limited.json()["error"]["code"] == "RATE_LIMITED"


def test_cors_preflight_allows_configured_frontend_origin() -> None:
    response = client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
