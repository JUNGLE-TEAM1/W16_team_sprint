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


def test_create_list_and_get_post() -> None:
    tokens = register_and_login("author@sprint.local")

    create_response = client.post(
        "/api/v1/posts",
        json={"title": "스프린트 1", "content": "API와 DB 흐름", "tags": ["FastAPI", "db", "fastapi", ""]},
        headers=auth_headers(tokens),
    )

    assert create_response.status_code == 201
    created_post = create_response.json()
    assert created_post["id"] == 1
    assert created_post["title"] == "스프린트 1"
    assert created_post["tags"] == ["fastapi", "db"]
    assert "author_name" not in created_post
    assert "user_id" not in created_post

    list_response = client.get("/api/v1/posts")
    assert list_response.status_code == 200
    list_body = list_response.json()
    assert list_body["items"][0]["id"] == 1
    assert list_body["items"][0]["tags"] == ["fastapi", "db"]
    assert list_body["total"] == 1
    assert list_body["page"] == 1
    assert list_body["size"] == 10
    assert list_body["pages"] == 1

    get_response = client.get("/api/v1/posts/1")
    assert get_response.status_code == 200
    assert get_response.json()["content"] == "API와 DB 흐름"
    assert get_response.json()["tags"] == ["fastapi", "db"]


def test_create_post_requires_login() -> None:
    response = client.post(
        "/api/v1/posts",
        json={"title": "스프린트 1", "content": "인증 필요"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"


def test_owner_can_update_and_delete_post() -> None:
    tokens = register_and_login("owner@sprint.local")
    create_response = client.post(
        "/api/v1/posts",
        json={"title": "Before", "content": "Before content"},
        headers=auth_headers(tokens),
    )
    post_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/v1/posts/{post_id}",
        json={"title": "After", "content": "After content", "tags": ["updated"]},
        headers=auth_headers(tokens),
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "After"
    assert update_response.json()["tags"] == ["updated"]

    delete_response = client.delete(
        f"/api/v1/posts/{post_id}",
        headers=auth_headers(tokens),
    )

    assert delete_response.status_code == 204
    assert client.get(f"/api/v1/posts/{post_id}").status_code == 404


def test_other_user_cannot_update_or_delete_post() -> None:
    owner_tokens = register_and_login("owner@sprint.local")
    other_tokens = register_and_login("other@sprint.local")
    create_response = client.post(
        "/api/v1/posts",
        json={"title": "Owner only", "content": "Protected"},
        headers=auth_headers(owner_tokens),
    )
    post_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/v1/posts/{post_id}",
        json={"title": "Nope", "content": "Denied", "tags": ["denied"]},
        headers=auth_headers(other_tokens),
    )

    assert update_response.status_code == 403
    assert update_response.json()["error"]["code"] == "POST_FORBIDDEN"

    delete_response = client.delete(
        f"/api/v1/posts/{post_id}",
        headers=auth_headers(other_tokens),
    )

    assert delete_response.status_code == 403
    assert delete_response.json()["error"]["code"] == "POST_FORBIDDEN"


def test_get_missing_post_returns_common_error_shape() -> None:
    response = client.get("/api/v1/posts/999")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "POST_NOT_FOUND",
            "message": "게시글을 찾을 수 없습니다.",
            "details": {"post_id": 999},
        }
    }


def test_list_posts_filters_by_tag_search_and_paginates() -> None:
    tokens = register_and_login("tag-search@sprint.local")
    posts = [
        {"title": "FastAPI 검색", "content": "태그와 검색을 함께 확인", "tags": ["fastapi", "search"]},
        {"title": "React 화면", "content": "검색 결과 없음 상태", "tags": ["react"]},
        {"title": "FastAPI 페이징", "content": "두 번째 fastapi 글", "tags": ["fastapi"]},
    ]
    for post in posts:
        response = client.post("/api/v1/posts", json=post, headers=auth_headers(tokens))
        assert response.status_code == 201

    tag_response = client.get("/api/v1/posts?tag=fastapi&page=1&size=1")
    assert tag_response.status_code == 200
    tag_body = tag_response.json()
    assert tag_body["total"] == 2
    assert tag_body["page"] == 1
    assert tag_body["size"] == 1
    assert tag_body["pages"] == 2
    assert len(tag_body["items"]) == 1
    assert "fastapi" in tag_body["items"][0]["tags"]

    second_page_response = client.get("/api/v1/posts?tag=fastapi&page=2&size=1")
    assert second_page_response.status_code == 200
    assert len(second_page_response.json()["items"]) == 1

    search_response = client.get("/api/v1/posts?q=화면")
    assert search_response.status_code == 200
    assert [post["title"] for post in search_response.json()["items"]] == ["React 화면"]

    empty_response = client.get("/api/v1/posts?tag=missing")
    assert empty_response.status_code == 200
    assert empty_response.json()["items"] == []
    assert empty_response.json()["total"] == 0
    assert empty_response.json()["pages"] == 0
