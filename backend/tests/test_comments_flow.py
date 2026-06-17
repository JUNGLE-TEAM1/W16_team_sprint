from fastapi.testclient import TestClient

from backend.app.db.session import engine
from backend.app.main import app
from backend.tests.db_reset import reset_app_data_only


def setup_function() -> None:
    reset_app_data_only(engine)


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


def test_public_consultation_question_comments_are_enabled() -> None:
    owner = TestClient(app)
    register_and_login(owner, username="owner", display_name="Owner")
    post_response = owner.post(
        "/api/v1/posts",
        json={"title": "강아지가 기침해요", "content": "기침이 반복되어 상담 질문을 올립니다."},
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
    assert create_response.json()["content"] == "좋은 정리입니다."

    list_response = owner.get(f"/api/v1/posts/{post_id}/comments")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["content"] == "좋은 정리입니다."


def test_create_comment_requires_session() -> None:
    owner = TestClient(app)
    register_and_login(owner, username="owner", display_name="Owner")
    post_response = owner.post(
        "/api/v1/posts",
        json={"title": "강아지가 구토해요", "content": "구토 관련 상담 질문입니다."},
    )
    assert post_response.status_code == 201

    anonymous = TestClient(app)
    response = anonymous.post(
        f"/api/v1/posts/{post_response.json()['id']}/comments",
        json={"content": "비로그인 댓글"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "SESSION_REQUIRED"
