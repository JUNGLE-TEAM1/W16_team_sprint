from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_embedding_provider
from backend.app.db.session import engine
from backend.app.main import app
from backend.app.models.post_embedding import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_STATUS_COMPLETED,
    EMBEDDING_STATUS_FAILED,
    PostEmbedding,
)
from backend.app.services.embedding_service import MockEmbeddingProvider
from backend.tests.db_reset import reset_app_data_only


class FailingEmbeddingProvider:
    def embed(self, text: str) -> list[float]:
        raise RuntimeError("embedding provider is down")


def setup_function() -> None:
    app.dependency_overrides.clear()
    reset_app_data_only(engine)


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


def get_post_embedding(post_id: int) -> PostEmbedding:
    with Session(engine) as db:
        row = db.query(PostEmbedding).filter(PostEmbedding.post_id == post_id).one()
        db.expunge(row)
        return row


def test_mock_embedding_is_saved_and_regenerated_only_when_post_text_changes() -> None:
    app.dependency_overrides[get_embedding_provider] = lambda: MockEmbeddingProvider()
    client = TestClient(app)
    register_and_login(client)

    create_response = client.post(
        "/api/v1/posts",
        json={
            "title": "FastAPI 인증 정리",
            "content": "Session 인증과 JWT 인증 차이를 정리합니다.",
            "tags": ["auth", "fastapi"],
            "post_type": "policy",
        },
    )

    assert create_response.status_code == 201
    post_id = create_response.json()["id"]
    created_embedding = get_post_embedding(post_id)
    assert created_embedding.status == EMBEDDING_STATUS_COMPLETED
    assert created_embedding.error_message is None
    assert created_embedding.attempt_count == 1
    assert created_embedding.embedding is not None
    assert len(created_embedding.embedding) == EMBEDDING_DIMENSIONS
    assert "title: FastAPI 인증 정리" in created_embedding.content_snapshot
    assert "tags: auth, fastapi" in created_embedding.content_snapshot

    no_change_response = client.patch(f"/api/v1/posts/{post_id}", json={})
    assert no_change_response.status_code == 200
    unchanged_embedding = get_post_embedding(post_id)
    assert unchanged_embedding.content_hash == created_embedding.content_hash
    assert unchanged_embedding.attempt_count == 1

    like_response = client.post(f"/api/v1/posts/{post_id}/like")
    assert like_response.status_code == 200
    liked_embedding = get_post_embedding(post_id)
    assert liked_embedding.content_hash == created_embedding.content_hash
    assert liked_embedding.attempt_count == 1

    update_response = client.patch(
        f"/api/v1/posts/{post_id}",
        json={"content": "Session 인증, JWT 인증, CSRF 방어 흐름을 함께 정리합니다."},
    )
    assert update_response.status_code == 200
    updated_embedding = get_post_embedding(post_id)
    assert updated_embedding.status == EMBEDDING_STATUS_COMPLETED
    assert updated_embedding.content_hash != created_embedding.content_hash
    assert updated_embedding.attempt_count == 2
    assert "CSRF 방어 흐름" in updated_embedding.content_snapshot


def test_embedding_failure_keeps_post_write_successful_and_marks_failed() -> None:
    app.dependency_overrides[get_embedding_provider] = lambda: FailingEmbeddingProvider()
    client = TestClient(app)
    register_and_login(client)

    create_response = client.post(
        "/api/v1/posts",
        json={
            "title": "장애 상황 기록",
            "content": "embedding provider 장애가 발생했습니다.",
            "post_type": "policy",
        },
    )

    assert create_response.status_code == 201
    post_id = create_response.json()["id"]
    failed_embedding = get_post_embedding(post_id)
    assert failed_embedding.status == EMBEDDING_STATUS_FAILED
    assert failed_embedding.embedding is None
    assert failed_embedding.attempt_count == 1
    assert failed_embedding.error_message == "embedding provider is down"

    update_response = client.patch(
        f"/api/v1/posts/{post_id}",
        json={"title": "장애 상황 기록 수정"},
    )

    assert update_response.status_code == 200
    updated_failed_embedding = get_post_embedding(post_id)
    assert updated_failed_embedding.status == EMBEDDING_STATUS_FAILED
    assert updated_failed_embedding.embedding is None
    assert updated_failed_embedding.attempt_count == 2
    assert "title: 장애 상황 기록 수정" in updated_failed_embedding.content_snapshot
