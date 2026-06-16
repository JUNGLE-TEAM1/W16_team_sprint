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


def auth_headers(email: str = "member@sprint.local", password: str = "password123") -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_post(headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/posts",
        headers=headers,
        json={"title": "Comment sprint", "content": "Connect API and UI"},
    )
    assert response.status_code == 201
    return response.json()


def test_create_list_and_delete_comment() -> None:
    headers = auth_headers()
    post = create_post(headers)

    create_response = client.post(
        f"/api/v1/posts/{post['id']}/comments",
        headers=headers,
        json={"content": "API만 끝나면 미완료", "author_name": "frontend"},
    )

    assert create_response.status_code == 201
    created_comment = create_response.json()
    assert created_comment["post_id"] == post["id"]
    assert created_comment["content"] == "API만 끝나면 미완료"

    list_response = client.get(f"/api/v1/posts/{post['id']}/comments")
    assert list_response.status_code == 200
    assert [comment["id"] for comment in list_response.json()] == [created_comment["id"]]

    delete_response = client.delete(f"/api/v1/comments/{created_comment['id']}", headers=headers)
    assert delete_response.status_code == 204

    empty_list_response = client.get(f"/api/v1/posts/{post['id']}/comments")
    assert empty_list_response.status_code == 200
    assert empty_list_response.json() == []


def test_create_comment_for_missing_post_returns_common_error_shape() -> None:
    response = client.post(
        "/api/v1/posts/999/comments",
        headers=auth_headers(),
        json={"content": "Missing parent", "author_name": "frontend"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "POST_NOT_FOUND",
            "message": "지원 카드나 상담 케이스를 찾을 수 없습니다.",
            "details": {"post_id": 999},
        }
    }


def test_delete_missing_comment_returns_common_error_shape() -> None:
    response = client.delete("/api/v1/comments/999", headers=auth_headers())

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "COMMENT_NOT_FOUND",
            "message": "상담 메모를 찾을 수 없습니다.",
            "details": {"comment_id": 999},
        }
    }
