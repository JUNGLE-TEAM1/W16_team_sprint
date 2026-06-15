from fastapi.testclient import TestClient

from backend.app.db.base import Base
from backend.app.db.seeds import seed_demo_users
from backend.app.db.session import engine
from backend.app.main import app

client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_demo_users(engine)


def login(email: str = "member@sprint.local", password: str = "password123") -> dict:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()


def test_login_and_call_protected_me_endpoint() -> None:
    tokens = login()

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "member@sprint.local"
    assert response.json()["role"] == "member"


def test_signup_creates_user_and_returns_login_tokens() -> None:
    signup_response = client.post(
        "/api/v1/auth/signup",
        json={"email": "new@sprint.local", "password": "password123"},
    )

    assert signup_response.status_code == 201
    tokens = signup_response.json()
    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "new@sprint.local"

    duplicate_response = client.post(
        "/api/v1/auth/signup",
        json={"email": "new@sprint.local", "password": "password123"},
    )
    assert duplicate_response.status_code == 409


def test_member_cannot_call_admin_endpoint() -> None:
    tokens = login()

    response = client.get(
        "/api/v1/auth/admin/report",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_admin_can_call_admin_endpoint() -> None:
    tokens = login(email="admin@sprint.local", password="admin123")

    response = client.get(
        "/api/v1/auth/admin/report",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json()["current_role"] == "admin"


def test_csrf_protected_session_action_requires_csrf_header() -> None:
    tokens = login()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    missing_csrf_response = client.post("/api/v1/auth/session-action", headers=headers)
    assert missing_csrf_response.status_code == 403
    assert missing_csrf_response.json()["error"]["code"] == "CSRF_TOKEN_INVALID"

    success_response = client.post(
        "/api/v1/auth/session-action",
        headers={**headers, "X-CSRF-Token": tokens["csrf_token"]},
    )
    assert success_response.status_code == 200


def test_refresh_rotates_refresh_token_and_logout_revokes_session() -> None:
    tokens = login()
    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    rotated_tokens = refresh_response.json()
    assert rotated_tokens["refresh_token"] != tokens["refresh_token"]

    reuse_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert reuse_response.status_code == 401

    logout_response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {rotated_tokens['access_token']}"},
    )
    assert logout_response.status_code == 200

    me_after_logout = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {rotated_tokens['access_token']}"},
    )
    assert me_after_logout.status_code == 401
