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


def test_comment_create_list_and_delete_requires_author() -> None:
    owner = TestClient(app)
    register_and_login(owner, username="owner", display_name="Owner")
    post_response = owner.post(
        "/api/v1/posts",
        json={"title": "댓글 테스트", "content": "댓글 API 확인"},
    )
    assert post_response.status_code == 201
    post_id = post_response.json()["id"]

    commenter = TestClient(app)
    register_and_login(commenter, username="commenter", display_name="Commenter")
    create_response = commenter.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "좋은 정리입니다."},
    )
    assert create_response.status_code == 201
    comment = create_response.json()
    assert comment["post_id"] == post_id
    assert comment["author_display_name"] == "Commenter"

    list_response = owner.get(f"/api/v1/posts/{post_id}/comments")
    assert list_response.status_code == 200
    assert list_response.json()[0]["content"] == "좋은 정리입니다."

    forbidden_delete = owner.delete(f"/api/v1/comments/{comment['id']}")
    assert forbidden_delete.status_code == 403
    assert forbidden_delete.json()["error"]["code"] == "COMMENT_FORBIDDEN"

    delete_response = commenter.delete(f"/api/v1/comments/{comment['id']}")
    assert delete_response.status_code == 204

    after_delete_response = owner.get(f"/api/v1/posts/{post_id}/comments")
    assert after_delete_response.status_code == 200
    assert after_delete_response.json() == []


def test_create_comment_requires_session() -> None:
    owner = TestClient(app)
    register_and_login(owner, username="owner", display_name="Owner")
    post_response = owner.post(
        "/api/v1/posts",
        json={"title": "댓글 테스트", "content": "댓글 API 확인"},
    )
    assert post_response.status_code == 201

    anonymous = TestClient(app)
    response = anonymous.post(
        f"/api/v1/posts/{post_response.json()['id']}/comments",
        json={"content": "비로그인 댓글"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "SESSION_REQUIRED"
