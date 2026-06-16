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


def register_and_login(client: TestClient, username: str, display_name: str) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": "password123",
            "display_name": display_name,
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/session/login",
        json={"username": username, "password": "password123"},
    )
    assert login_response.status_code == 200


def test_support_card_comments_are_disabled() -> None:
    owner = TestClient(app)
    register_and_login(owner, username="owner", display_name="Owner")
    post_response = owner.post(
        "/api/v1/posts",
        json={"title": "지원 카드", "content": "공공데이터 기반 지원 정보", "post_type": "policy"},
    )
    assert post_response.status_code == 201
    post_id = post_response.json()["id"]

    commenter = TestClient(app)
    register_and_login(commenter, username="commenter", display_name="Commenter")
    create_response = commenter.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "좋은 정리입니다."},
    )
    assert create_response.status_code == 403
    assert create_response.json()["error"]["code"] == "COMMENTS_DISABLED"

    list_response = owner.get(f"/api/v1/posts/{post_id}/comments")
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_create_comment_requires_session() -> None:
    owner = TestClient(app)
    register_and_login(owner, username="owner", display_name="Owner")
    post_response = owner.post(
        "/api/v1/posts",
        json={"title": "지원 카드", "content": "공공데이터 기반 지원 정보", "post_type": "policy"},
    )
    assert post_response.status_code == 201

    anonymous = TestClient(app)
    response = anonymous.post(
        f"/api/v1/posts/{post_response.json()['id']}/comments",
        json={"content": "비로그인 댓글"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "SESSION_REQUIRED"
