from fastapi.testclient import TestClient

from backend.app.db.base import Base
from backend.app.db.session import engine
from backend.app.main import app

client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_create_list_and_get_post() -> None:
    create_response = client.post(
        "/api/v1/posts",
        json={"title": "스프린트 1", "content": "API와 DB 흐름", "author_name": "team1"},
    )

    assert create_response.status_code == 201
    created_post = create_response.json()
    assert created_post["id"] == 1
    assert created_post["title"] == "스프린트 1"

    list_response = client.get("/api/v1/posts")
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == 1

    get_response = client.get("/api/v1/posts/1")
    assert get_response.status_code == 200
    assert get_response.json()["content"] == "API와 DB 흐름"


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
