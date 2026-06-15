from fastapi.testclient import TestClient

from backend.app.db.base import Base
from backend.app.db.session import engine
from backend.app.main import app

client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def register_and_login(email: str) -> dict:
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert login_response.status_code == 200
    return login_response.json()


def auth_headers(tokens: dict) -> dict:
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def create_post(tokens: dict) -> int:
    response = client.post(
        "/api/v1/posts",
        json={"title": "댓글 테스트", "content": "게시글 내용"},
        headers=auth_headers(tokens),
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def test_create_list_update_and_delete_comment() -> None:
    tokens = register_and_login("comment-owner@sprint.local")
    post_id = create_post(tokens)

    create_response = client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "첫 댓글"},
        headers=auth_headers(tokens),
    )

    assert create_response.status_code == 201
    created_comment = create_response.json()
    assert created_comment["id"] == 1
    assert created_comment["post_id"] == post_id
    assert created_comment["content"] == "첫 댓글"
    assert "user_id" not in created_comment
    assert "author_name" not in created_comment
    assert created_comment["created_at"]
    assert created_comment["updated_at"]

    list_response = client.get(f"/api/v1/posts/{post_id}/comments")
    assert list_response.status_code == 200
    assert [comment["id"] for comment in list_response.json()] == [1]

    update_response = client.put(
        f"/api/v1/posts/{post_id}/comments/1",
        json={"content": "수정된 댓글"},
        headers=auth_headers(tokens),
    )
    assert update_response.status_code == 200
    assert update_response.json()["content"] == "수정된 댓글"

    delete_response = client.delete(
        f"/api/v1/posts/{post_id}/comments/1",
        headers=auth_headers(tokens),
    )
    assert delete_response.status_code == 204
    assert client.get(f"/api/v1/posts/{post_id}/comments").json() == []


def test_create_comment_requires_login() -> None:
    tokens = register_and_login("post-author@sprint.local")
    post_id = create_post(tokens)

    response = client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "로그인 필요"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"


def test_missing_post_or_mismatched_comment_returns_404() -> None:
    tokens = register_and_login("missing-scope@sprint.local")
    post_id = create_post(tokens)
    other_post_id = client.post(
        "/api/v1/posts",
        json={"title": "다른 글", "content": "다른 내용"},
        headers=auth_headers(tokens),
    ).json()["id"]

    create_response = client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "스코프 확인"},
        headers=auth_headers(tokens),
    )
    comment_id = create_response.json()["id"]

    missing_post_response = client.post(
        "/api/v1/posts/999/comments",
        json={"content": "없는 글"},
        headers=auth_headers(tokens),
    )
    assert missing_post_response.status_code == 404
    assert missing_post_response.json()["error"]["code"] == "POST_NOT_FOUND"

    mismatch_response = client.put(
        f"/api/v1/posts/{other_post_id}/comments/{comment_id}",
        json={"content": "다른 게시글 경로"},
        headers=auth_headers(tokens),
    )
    assert mismatch_response.status_code == 404
    assert mismatch_response.json()["error"]["code"] == "COMMENT_NOT_FOUND"


def test_other_user_cannot_update_or_delete_comment() -> None:
    owner_tokens = register_and_login("comment-owner-403@sprint.local")
    other_tokens = register_and_login("comment-other-403@sprint.local")
    post_id = create_post(owner_tokens)
    create_response = client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "소유자 댓글"},
        headers=auth_headers(owner_tokens),
    )
    comment_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/v1/posts/{post_id}/comments/{comment_id}",
        json={"content": "타인 수정"},
        headers=auth_headers(other_tokens),
    )

    assert update_response.status_code == 403
    assert update_response.json()["error"]["code"] == "COMMENT_FORBIDDEN"

    delete_response = client.delete(
        f"/api/v1/posts/{post_id}/comments/{comment_id}",
        headers=auth_headers(other_tokens),
    )

    assert delete_response.status_code == 403
    assert delete_response.json()["error"]["code"] == "COMMENT_FORBIDDEN"
