from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.db.base import Base
from backend.app.db.session import engine
from backend.app.main import app
from backend.app.models.comment import Comment
from backend.app.models.post import Post
from backend.app.models.post_like import PostLike


def setup_function() -> None:
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS refresh_tokens CASCADE"))
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def register_and_login(
    client: TestClient,
    username: str = "team1",
    display_name: str = "Team One",
) -> None:
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


def test_create_list_and_get_post() -> None:
    client = TestClient(app)
    register_and_login(client)

    create_response = client.post(
        "/api/v1/posts",
        json={
            "title": "스프린트 1",
            "content": "API와 DB 흐름",
            "tags": [" FastAPI ", "auth", "fastapi"],
        },
    )

    assert create_response.status_code == 201
    created_post = create_response.json()
    assert created_post["id"] == 1
    assert created_post["title"] == "스프린트 1"
    assert created_post["author_id"] == 1
    assert created_post["author_display_name"] == "Team One"
    assert created_post["comment_count"] == 0
    assert created_post["like_count"] == 0
    assert created_post["tags"] == ["auth", "fastapi"]
    assert "updated_at" in created_post

    list_response = client.get("/api/v1/posts")
    assert list_response.status_code == 200
    list_body = list_response.json()
    assert list_body["page"] == 1
    assert list_body["size"] == 9
    assert list_body["total"] == 1
    assert list_body["total_pages"] == 1
    assert list_body["items"][0]["id"] == 1
    assert list_body["items"][0]["author_display_name"] == "Team One"
    assert list_body["items"][0]["comment_count"] == 0
    assert list_body["items"][0]["like_count"] == 0
    assert list_body["items"][0]["tags"] == ["auth", "fastapi"]

    get_response = client.get("/api/v1/posts/1")
    assert get_response.status_code == 200
    assert get_response.json()["content"] == "API와 DB 흐름"
    assert get_response.json()["author_display_name"] == "Team One"
    assert get_response.json()["comment_count"] == 0
    assert get_response.json()["like_count"] == 0
    assert get_response.json()["tags"] == ["auth", "fastapi"]

    tags_response = client.get("/api/v1/tags")
    assert tags_response.status_code == 200
    assert [tag["name"] for tag in tags_response.json()] == ["auth", "fastapi"]


def test_create_post_requires_session() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/posts",
        json={"title": "스프린트 1", "content": "API와 DB 흐름"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "SESSION_REQUIRED"


def test_update_and_delete_post_requires_author() -> None:
    owner = TestClient(app)
    register_and_login(owner, username="owner", display_name="Owner")
    create_response = owner.post(
        "/api/v1/posts",
        json={"title": "원본 제목", "content": "원본 내용"},
    )
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]

    other = TestClient(app)
    register_and_login(other, username="other", display_name="Other")
    forbidden_update = other.patch(
        f"/api/v1/posts/{post_id}",
        json={"title": "다른 사용자의 수정"},
    )
    assert forbidden_update.status_code == 403
    assert forbidden_update.json()["error"]["code"] == "POST_FORBIDDEN"

    update_response = owner.patch(
        f"/api/v1/posts/{post_id}",
        json={"title": "수정된 제목", "tags": ["crud"]},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "수정된 제목"
    assert update_response.json()["content"] == "원본 내용"
    assert update_response.json()["tags"] == ["crud"]

    comment_response = other.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "삭제될 댓글"},
    )
    assert comment_response.status_code == 201
    like_response = owner.post(f"/api/v1/posts/{post_id}/like")
    assert like_response.status_code == 200

    forbidden_delete = other.delete(f"/api/v1/posts/{post_id}")
    assert forbidden_delete.status_code == 403
    assert forbidden_delete.json()["error"]["code"] == "POST_FORBIDDEN"

    delete_response = owner.delete(f"/api/v1/posts/{post_id}")
    assert delete_response.status_code == 204

    get_deleted_response = owner.get(f"/api/v1/posts/{post_id}")
    assert get_deleted_response.status_code == 404

    with Session(engine) as db:
        assert db.query(Comment).count() == 0
        assert db.query(PostLike).count() == 0


def test_list_posts_supports_search_tag_filter_and_pagination() -> None:
    client = TestClient(app)
    register_and_login(client, username="fastapi_user", display_name="FastAPI Author")
    posts = [
        {
            "title": "Session 인증 정리",
            "content": "쿠키와 서버 세션을 설명합니다.",
            "tags": ["auth", "session"],
        },
        {
            "title": "React 상태 관리",
            "content": "client state와 server state를 구분합니다.",
            "tags": ["react"],
        },
        {
            "title": "PostgreSQL ILIKE 검색",
            "content": "제목과 본문 검색을 구현합니다.",
            "tags": ["db", "search"],
        },
    ]
    for post in posts:
        response = client.post("/api/v1/posts", json=post)
        assert response.status_code == 201

    title_response = client.get("/api/v1/posts?q=Session&search_type=title")
    assert title_response.status_code == 200
    assert title_response.json()["total"] == 1
    assert title_response.json()["items"][0]["title"] == "Session 인증 정리"

    content_response = client.get("/api/v1/posts?q=server state&search_type=content")
    assert content_response.status_code == 200
    assert content_response.json()["total"] == 1
    assert content_response.json()["items"][0]["title"] == "React 상태 관리"

    title_content_response = client.get("/api/v1/posts?q=본문&search_type=title_content")
    assert title_content_response.status_code == 200
    assert title_content_response.json()["total"] == 1
    assert title_content_response.json()["items"][0]["title"] == "PostgreSQL ILIKE 검색"

    author_response = client.get("/api/v1/posts?q=FastAPI&search_type=author")
    assert author_response.status_code == 200
    assert author_response.json()["total"] == 3

    tag_response = client.get("/api/v1/posts?tag=auth")
    assert tag_response.status_code == 200
    assert tag_response.json()["total"] == 1
    assert tag_response.json()["items"][0]["tags"] == ["auth", "session"]

    page_response = client.get("/api/v1/posts?page=2&size=2")
    assert page_response.status_code == 200
    assert page_response.json()["page"] == 2
    assert page_response.json()["size"] == 2
    assert page_response.json()["total"] == 3
    assert page_response.json()["total_pages"] == 2
    assert len(page_response.json()["items"]) == 1


def test_get_missing_post_returns_common_error_shape() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/posts/999")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "POST_NOT_FOUND",
            "message": "게시글을 찾을 수 없습니다.",
            "details": {"post_id": 999},
        }
    }


def test_like_post_requires_session_and_ignores_duplicate_like() -> None:
    client = TestClient(app)
    register_and_login(client, username="owner", display_name="Owner")
    create_response = client.post(
        "/api/v1/posts",
        json={"title": "좋아요 테스트", "content": "좋아요 버튼 확인"},
    )
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]
    assert create_response.json()["like_count"] == 0

    anonymous = TestClient(app)
    anonymous_response = anonymous.post(f"/api/v1/posts/{post_id}/like")
    assert anonymous_response.status_code == 401
    assert anonymous_response.json()["error"]["code"] == "SESSION_REQUIRED"

    first_like_response = client.post(f"/api/v1/posts/{post_id}/like")
    assert first_like_response.status_code == 200
    assert first_like_response.json()["like_count"] == 1

    second_like_response = client.post(f"/api/v1/posts/{post_id}/like")
    assert second_like_response.status_code == 200
    assert second_like_response.json()["like_count"] == 1

    other = TestClient(app)
    register_and_login(other, username="other", display_name="Other")
    other_like_response = other.post(f"/api/v1/posts/{post_id}/like")
    assert other_like_response.status_code == 200
    assert other_like_response.json()["like_count"] == 2

    get_response = client.get(f"/api/v1/posts/{post_id}")
    assert get_response.status_code == 200
    assert get_response.json()["like_count"] == 2

    with Session(engine) as db:
        assert db.query(PostLike).count() == 2


def test_list_posts_supports_comment_and_like_sorting() -> None:
    client = TestClient(app)
    register_and_login(client, username="owner", display_name="Owner")

    first_response = client.post(
        "/api/v1/posts",
        json={"title": "댓글 적은 글", "content": "댓글 하나"},
    )
    second_response = client.post(
        "/api/v1/posts",
        json={"title": "댓글 많은 글", "content": "댓글 둘"},
    )
    third_response = client.post(
        "/api/v1/posts",
        json={"title": "좋아요 많은 글", "content": "좋아요 정렬"},
    )
    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert third_response.status_code == 201

    first_id = first_response.json()["id"]
    second_id = second_response.json()["id"]
    third_id = third_response.json()["id"]

    assert client.post(f"/api/v1/posts/{first_id}/comments", json={"content": "댓글 1"}).status_code == 201
    assert client.post(f"/api/v1/posts/{second_id}/comments", json={"content": "댓글 1"}).status_code == 201
    assert client.post(f"/api/v1/posts/{second_id}/comments", json={"content": "댓글 2"}).status_code == 201

    with Session(engine) as db:
        first_post = db.get(Post, first_id)
        second_post = db.get(Post, second_id)
        third_post = db.get(Post, third_id)
        assert first_post is not None
        assert second_post is not None
        assert third_post is not None
        first_post.like_count = 2
        second_post.like_count = 1
        third_post.like_count = 7
        db.commit()

    comment_sort_response = client.get("/api/v1/posts?sort=comment_count")
    assert comment_sort_response.status_code == 200
    comment_sorted_items = comment_sort_response.json()["items"]
    assert [item["id"] for item in comment_sorted_items[:3]] == [second_id, first_id, third_id]
    assert comment_sorted_items[0]["comment_count"] == 2

    like_sort_response = client.get("/api/v1/posts?sort=like_count")
    assert like_sort_response.status_code == 200
    like_sorted_items = like_sort_response.json()["items"]
    assert [item["id"] for item in like_sorted_items[:3]] == [third_id, first_id, second_id]
    assert like_sorted_items[0]["like_count"] == 7
