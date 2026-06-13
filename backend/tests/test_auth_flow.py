from fastapi.testclient import TestClient

from backend.app.db.base import Base
from backend.app.db.session import engine
from backend.app.main import app


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def register_user(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "team1",
            "password": "password123",
            "display_name": "Team One",
        },
    )
    assert response.status_code == 201


def test_session_login_me_and_logout() -> None:
    client = TestClient(app)
    register_user(client)

    login_response = client.post(
        "/api/v1/auth/session/login",
        json={"username": "team1", "password": "password123"},
    )

    assert login_response.status_code == 200
    assert login_response.json()["user"]["username"] == "team1"
    assert "session_id" in login_response.cookies

    me_response = client.get("/api/v1/auth/session/me")
    assert me_response.status_code == 200
    assert me_response.json()["display_name"] == "Team One"

    logout_response = client.post("/api/v1/auth/session/logout")
    assert logout_response.status_code == 204

    after_logout_response = client.get("/api/v1/auth/session/me")
    assert after_logout_response.status_code == 401


def test_jwt_access_token_login_and_me() -> None:
    client = TestClient(app)
    register_user(client)

    login_response = client.post(
        "/api/v1/auth/jwt/login",
        json={"username": "team1", "password": "password123"},
    )

    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    me_response = client.get(
        "/api/v1/auth/jwt/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "team1"


def test_access_token_refresh_token_flow_rotates_refresh_token() -> None:
    client = TestClient(app)
    register_user(client)

    login_response = client.post(
        "/api/v1/auth/token-pair/login",
        json={"username": "team1", "password": "password123"},
    )

    assert login_response.status_code == 200
    token_pair = login_response.json()

    me_response = client.get(
        "/api/v1/auth/token-pair/me",
        headers={"Authorization": f"Bearer {token_pair['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "team1"

    refresh_response = client.post(
        "/api/v1/auth/token-pair/refresh",
        json={"refresh_token": token_pair["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    rotated_pair = refresh_response.json()
    assert rotated_pair["refresh_token"] != token_pair["refresh_token"]

    reused_refresh_response = client.post(
        "/api/v1/auth/token-pair/refresh",
        json={"refresh_token": token_pair["refresh_token"]},
    )
    assert reused_refresh_response.status_code == 401
