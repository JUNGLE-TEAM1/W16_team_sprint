from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.app.db.base import Base
from backend.app.db.session import engine
from backend.app.main import app


def setup_function() -> None:
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS refresh_tokens CASCADE"))
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
    session_cookie = login_response.cookies.get("session_id")
    assert session_cookie is not None
    assert session_cookie not in str(login_response.json())

    me_response = client.get("/api/v1/auth/session/me")
    assert me_response.status_code == 200
    assert me_response.json()["display_name"] == "Team One"

    logout_response = client.post("/api/v1/auth/session/logout")
    assert logout_response.status_code == 204

    after_logout_response = client.get("/api/v1/auth/session/me")
    assert after_logout_response.status_code == 401
