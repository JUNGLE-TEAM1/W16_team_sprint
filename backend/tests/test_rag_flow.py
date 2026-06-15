from types import SimpleNamespace

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


def auth_headers() -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "member@sprint.local", "password": "password123"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_rag_assist_finds_similar_posts_and_reports_duplicate_risk() -> None:
    headers = auth_headers()
    first_post = client.post(
        "/api/v1/posts",
        headers=headers,
        json={
            "title": "FastAPI JWT 401 Unauthorized troubleshooting",
            "content": "Authorization Bearer header and current_user dependency can cause 401 errors.",
            "tag_names": ["fastapi", "jwt", "auth"],
        },
    )
    assert first_post.status_code == 201

    second_post = client.post(
        "/api/v1/posts",
        headers=headers,
        json={
            "title": "React list pagination UX",
            "content": "Render empty states, loading states, and search results in the post list.",
            "tag_names": ["react"],
        },
    )
    assert second_post.status_code == 201

    response = client.post(
        "/api/v1/rag/assist",
        json={
            "title": "FastAPI JWT authentication returns 401 Unauthorized",
            "content": "I want to check the Authorization Bearer token and current_user dependency.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stored_vectors"] == 2
    assert body["embedding_dimensions"] == 64
    assert body["llm_provider"] == "none"
    assert body["llm_model"] == "rule-fallback"
    assert body["llm_used"] is False
    assert body["matches"][0]["title"] == "FastAPI JWT 401 Unauthorized troubleshooting"
    assert body["matches"][0]["score"] > 0
    assert body["recommendation"]


def test_rag_assist_uses_openai_llm_when_api_key_is_configured(monkeypatch) -> None:
    headers = auth_headers()
    created = client.post(
        "/api/v1/posts",
        headers=headers,
        json={
            "title": "RAG duplicate assist with LLM",
            "content": "Use embeddings for candidates, then use an LLM to write the recommendation.",
            "tag_names": ["rag", "llm"],
        },
    )
    assert created.status_code == 201

    from backend.app.services import rag_service

    monkeypatch.setattr(
        rag_service,
        "settings",
        SimpleNamespace(
            openai_api_key="test-key",
            openai_base_url="https://api.openai.test/v1",
            openai_embedding_model="text-embedding-3-small",
            openai_llm_model="gpt-test",
            openai_llm_max_output_tokens=300,
            openai_timeout_seconds=1,
        ),
    )

    def fake_request_llm_assist(self, *, query_text, matches, duplicate_warning):
        assert "LLM" in query_text
        assert matches
        return {
            "recommendation": "LLM checked the similar RAG post and suggested a clearer angle for the new draft.",
            "match_summaries": [
                {
                    "post_id": matches[0].post_id,
                    "summary": "LLM-generated summary based on the candidate post.",
                }
            ],
        }

    monkeypatch.setattr(rag_service.RagService, "_request_llm_assist", fake_request_llm_assist)

    response = client.post(
        "/api/v1/rag/assist",
        json={
            "title": "LLM RAG duplicate check",
            "content": "I want the assist endpoint to use LLM output after embedding search.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["llm_provider"] == "openai"
    assert body["llm_model"] == "gpt-test"
    assert body["llm_used"] is True
    assert body["recommendation"] == (
        "LLM checked the similar RAG post and suggested a clearer angle for the new draft."
    )
    assert body["matches"][0]["summary"] == "LLM-generated summary based on the candidate post."
