from fastapi.testclient import TestClient

from backend.app.api.dependencies import get_embedding_provider
from backend.app.db.base import Base
from backend.app.db.session import engine
from backend.app.db.session import SessionLocal
from backend.app.main import app
from backend.app.models.post_embedding import PostEmbedding
from backend.app.services.embedding_provider import HashEmbeddingProvider

client = TestClient(app)


class FailingEmbeddingProvider(HashEmbeddingProvider):
    model_name = "failing-embedding"

    def embed(self, text: str) -> list[float]:
        raise RuntimeError("embedding failed")


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


def test_similar_posts_preview_returns_score_level_and_summary() -> None:
    tokens = register_and_login("rag@sprint.local")
    for post in [
        {"title": "JWT 로그인 구현", "content": "JWT 토큰 발급과 current_user 검증 흐름", "tags": ["auth", "jwt"]},
        {"title": "React 검색 화면", "content": "검색어와 태그 필터를 입력하는 화면", "tags": ["react"]},
    ]:
        response = client.post("/api/v1/posts", json=post, headers=auth_headers(tokens))
        assert response.status_code == 201

    response = client.post(
        "/api/v1/ai/similar-posts",
        json={
            "title": "JWT 인증 정리",
            "content": "토큰 발급과 current_user 흐름을 정리한다",
            "tags": ["jwt", "auth"],
            "limit": 3,
        },
        headers=auth_headers(tokens),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == "테스트 요약입니다."
    assert body["message"] == "비슷한 게시글 2개를 찾았습니다."
    assert body["items"][0]["title"] == "JWT 로그인 구현"
    assert body["items"][0]["similarity"] > 0
    assert body["items"][0]["similarity_level"] in {"high", "medium", "low"}


def test_similar_posts_requires_login() -> None:
    response = client.post(
        "/api/v1/ai/similar-posts",
        json={"title": "JWT", "content": "인증", "tags": []},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"


def test_embedding_failure_does_not_rollback_post() -> None:
    app.dependency_overrides[get_embedding_provider] = lambda: FailingEmbeddingProvider()
    tokens = register_and_login("failed-rag@sprint.local")

    response = client.post(
        "/api/v1/posts",
        json={"title": "임베딩 실패", "content": "게시글은 저장되어야 한다", "tags": ["rag"]},
        headers=auth_headers(tokens),
    )

    assert response.status_code == 201
    assert client.get("/api/v1/posts/1").status_code == 200

    db = SessionLocal()
    try:
        record = db.query(PostEmbedding).filter(PostEmbedding.post_id == 1).one()
        assert record.status == "failed"
        assert "embedding failed" in (record.last_error or "")
    finally:
        db.close()
