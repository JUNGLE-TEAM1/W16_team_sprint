from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.app.api.dependencies import get_embedding_provider
from backend.app.db.base import Base
from backend.app.db.session import engine
from backend.app.main import app
from backend.app.services.embedding_service import MockEmbeddingProvider


class FailingEmbeddingProvider:
    def embed(self, text: str) -> list[float]:
        raise RuntimeError("query embedding failed")


def setup_function() -> None:
    app.dependency_overrides.clear()
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS refresh_tokens CASCADE"))
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def register_and_login(client: TestClient) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "team1",
            "password": "password123",
            "display_name": "Team One",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/session/login",
        json={"username": "team1", "password": "password123"},
    )
    assert login_response.status_code == 200


def create_post(client: TestClient, title: str, content: str, tags: list[str] | None = None) -> int:
    response = client.post(
        "/api/v1/posts",
        json={
            "title": title,
            "content": content,
            "tags": tags or [],
        },
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def test_related_posts_requires_session() -> None:
    app.dependency_overrides[get_embedding_provider] = lambda: MockEmbeddingProvider()
    client = TestClient(app)

    response = client.post(
        "/api/v1/ai/rag/related-posts",
        json={
            "title": "FastAPI 인증 문제",
            "content": "Session 인증과 JWT 인증 차이를 정리합니다.",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "SESSION_REQUIRED"


def test_related_posts_returns_empty_items_when_no_embeddings_exist() -> None:
    app.dependency_overrides[get_embedding_provider] = lambda: MockEmbeddingProvider()
    client = TestClient(app)
    register_and_login(client)

    response = client.post(
        "/api/v1/ai/rag/related-posts",
        json={
            "title": "FastAPI 인증 문제",
            "content": "Session 인증과 JWT 인증 차이를 정리합니다.",
            "tags": ["fastapi", "auth"],
        },
    )

    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_related_posts_returns_top_matches_and_supports_exclude_post_id() -> None:
    app.dependency_overrides[get_embedding_provider] = lambda: MockEmbeddingProvider()
    client = TestClient(app)
    register_and_login(client)

    first_id = create_post(
        client,
        title="FastAPI 인증 문제",
        content="Session 인증과 JWT 인증 차이를 정리합니다.",
        tags=["fastapi", "auth"],
    )
    create_post(
        client,
        title="React 상태 관리",
        content="server state와 client state를 구분합니다.",
        tags=["react"],
    )

    response = client.post(
        "/api/v1/ai/rag/related-posts",
        json={
            "title": "FastAPI 인증 문제",
            "content": "Session 인증과 JWT 인증 차이를 정리합니다.",
            "tags": ["auth", "fastapi"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["post_id"] == first_id
    assert body["items"][0]["title"] == "FastAPI 인증 문제"
    assert body["items"][0]["tags"] == ["auth", "fastapi"]
    assert body["items"][0]["similarity"] >= 0.99
    assert body["items"][0]["summary"] is None

    exclude_response = client.post(
        "/api/v1/ai/rag/related-posts",
        json={
            "title": "FastAPI 인증 문제",
            "content": "Session 인증과 JWT 인증 차이를 정리합니다.",
            "tags": ["auth", "fastapi"],
            "exclude_post_id": first_id,
        },
    )

    assert exclude_response.status_code == 200
    assert all(item["post_id"] != first_id for item in exclude_response.json()["items"])


def test_related_posts_rejects_too_short_query() -> None:
    app.dependency_overrides[get_embedding_provider] = lambda: MockEmbeddingProvider()
    client = TestClient(app)
    register_and_login(client)

    response = client.post(
        "/api/v1/ai/rag/related-posts",
        json={
            "title": "짧음",
            "content": "부족",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_related_posts_returns_rag_embedding_failed_when_query_embedding_fails() -> None:
    app.dependency_overrides[get_embedding_provider] = lambda: FailingEmbeddingProvider()
    client = TestClient(app)
    register_and_login(client)

    response = client.post(
        "/api/v1/ai/rag/related-posts",
        json={
            "title": "FastAPI 인증 문제",
            "content": "Session 인증과 JWT 인증 차이를 정리합니다.",
            "tags": ["fastapi", "auth"],
        },
    )

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "RAG_EMBEDDING_FAILED",
            "message": "유사 게시글 검색을 위한 embedding 생성에 실패했습니다.",
            "details": {},
        }
    }
