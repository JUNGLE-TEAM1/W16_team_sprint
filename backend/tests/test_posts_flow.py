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


def test_create_list_and_get_post() -> None:
    create_response = client.post(
        "/api/v1/posts",
        headers=auth_headers(),
        json={
            "title": "스프린트 1",
            "content": "API와 DB 흐름",
            "tag_names": ["api", "db"],
        },
    )

    assert create_response.status_code == 201
    created_post = create_response.json()
    assert created_post["id"] == 1
    assert created_post["title"] == "스프린트 1"
    assert [tag["name"] for tag in created_post["tags"]] == ["api", "db"]

    list_response = client.get("/api/v1/posts")
    assert list_response.status_code == 200
    assert list_response.json()["items"][0]["id"] == 1

    get_response = client.get("/api/v1/posts/1")
    assert get_response.status_code == 200
    assert get_response.json()["content"] == "API와 DB 흐름"


def test_post_write_requires_login_and_owner_permission() -> None:
    unauthenticated_response = client.post(
        "/api/v1/posts",
        json={"title": "No auth", "content": "Should fail"},
    )
    assert unauthenticated_response.status_code == 401

    owner_headers = auth_headers()
    create_response = client.post(
        "/api/v1/posts",
        headers=owner_headers,
        json={"title": "Owner post", "content": "Only owner can change"},
    )
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]

    signup_response = client.post(
        "/api/v1/auth/signup",
        json={"email": "other@sprint.local", "password": "password123"},
    )
    assert signup_response.status_code == 201
    other_headers = {"Authorization": f"Bearer {signup_response.json()['access_token']}"}

    forbidden_response = client.patch(
        f"/api/v1/posts/{post_id}",
        headers=other_headers,
        json={"title": "Stolen"},
    )
    assert forbidden_response.status_code == 403

    update_response = client.patch(
        f"/api/v1/posts/{post_id}",
        headers=owner_headers,
        json={"title": "Updated", "tag_names": ["crud"]},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated"
    assert update_response.json()["tags"][0]["name"] == "crud"

    delete_response = client.delete(f"/api/v1/posts/{post_id}", headers=owner_headers)
    assert delete_response.status_code == 204


def test_list_posts_supports_paging_search_and_tag_filter() -> None:
    headers = auth_headers()
    for index in range(12):
        client.post(
            "/api/v1/posts",
            headers=headers,
            json={
                "title": f"RAG search note {index}",
                "content": "검색과 페이징은 데이터 탐색 구조입니다.",
                "tag_names": ["rag" if index % 2 == 0 else "api"],
            },
        )

    page_response = client.get("/api/v1/posts?page=2&size=5")
    assert page_response.status_code == 200
    page_body = page_response.json()
    assert page_body["page"] == 2
    assert page_body["size"] == 5
    assert page_body["total"] == 12
    assert len(page_body["items"]) == 5

    search_response = client.get("/api/v1/posts?q=RAG")
    assert search_response.status_code == 200
    assert search_response.json()["total"] == 12

    tag_response = client.get("/api/v1/posts?tag=rag")
    assert tag_response.status_code == 200
    assert tag_response.json()["total"] == 6


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
