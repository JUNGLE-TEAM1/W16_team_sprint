from fastapi.testclient import TestClient

from backend.app.api.dependencies import get_embedding_provider, get_rag_summary_provider
from backend.app.db.session import engine
from backend.app.main import app
from backend.app.services.embedding_service import MockEmbeddingProvider
from backend.tests.db_reset import reset_app_data_only


class FailingEmbeddingProvider:
    def embed(self, text: str) -> list[float]:
        raise RuntimeError("query embedding failed")


class NoopSummaryProvider:
    def summarize(self, payload, related_posts):  # noqa: ANN001
        return {}


class MockSummaryProvider:
    def summarize(self, payload, related_posts):  # noqa: ANN001
        return {
            row.post_id: f"{row.title}와 작성 중인 글은 인증 흐름이라는 점에서 관련됩니다. 기존 글은 {row.content_preview} 내용을 다룹니다."
            for row in related_posts
        }


class FailingSummaryProvider:
    def summarize(self, payload, related_posts):  # noqa: ANN001
        raise RuntimeError("summary failed")


def setup_function() -> None:
    app.dependency_overrides.clear()
    reset_app_data_only(engine)


def use_mock_rag_dependencies(summary_provider=None) -> None:  # noqa: ANN001
    app.dependency_overrides[get_embedding_provider] = lambda: MockEmbeddingProvider()
    app.dependency_overrides[get_rag_summary_provider] = lambda: summary_provider or NoopSummaryProvider()


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
            "post_type": "policy",
        },
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def test_related_posts_requires_session() -> None:
    use_mock_rag_dependencies()
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
    use_mock_rag_dependencies()
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
    use_mock_rag_dependencies()
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
            "post_type": "policy",
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
            "post_type": "policy",
            "exclude_post_id": first_id,
        },
    )

    assert exclude_response.status_code == 200
    assert all(item["post_id"] != first_id for item in exclude_response.json()["items"])


def test_related_posts_rejects_too_short_query() -> None:
    use_mock_rag_dependencies()
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
    app.dependency_overrides[get_rag_summary_provider] = lambda: NoopSummaryProvider()
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
            "message": "관련 지원/시설 검색을 위한 embedding 생성에 실패했습니다.",
            "details": {},
        }
    }


def test_related_posts_returns_llm_summaries_when_summary_provider_succeeds() -> None:
    use_mock_rag_dependencies(MockSummaryProvider())
    client = TestClient(app)
    register_and_login(client)

    post_id = create_post(
        client,
        title="FastAPI 세션 인증 흐름",
        content="Session cookie를 통해 로그인 사용자를 확인하고 CSRF 위험을 줄이는 방법을 정리합니다.",
        tags=["fastapi", "auth"],
    )

    response = client.post(
        "/api/v1/ai/rag/related-posts",
        json={
            "title": "FastAPI 세션 인증 흐름",
            "content": "Session cookie를 통해 로그인 사용자를 확인하고 CSRF 위험을 줄이는 방법을 정리합니다.",
            "tags": ["fastapi", "auth"],
            "post_type": "policy",
        },
    )

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["post_id"] == post_id
    assert "인증 흐름" in item["summary"]


def test_related_posts_keeps_items_when_summary_provider_fails() -> None:
    use_mock_rag_dependencies(FailingSummaryProvider())
    client = TestClient(app)
    register_and_login(client)

    post_id = create_post(
        client,
        title="FastAPI 세션 인증 흐름",
        content="Session cookie를 통해 로그인 사용자를 확인하고 CSRF 위험을 줄이는 방법을 정리합니다.",
        tags=["fastapi", "auth"],
    )

    response = client.post(
        "/api/v1/ai/rag/related-posts",
        json={
            "title": "FastAPI 세션 인증 흐름",
            "content": "Session cookie를 통해 로그인 사용자를 확인하고 CSRF 위험을 줄이는 방법을 정리합니다.",
            "tags": ["fastapi", "auth"],
            "post_type": "policy",
        },
    )

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["post_id"] == post_id
    assert item["summary"] is None
