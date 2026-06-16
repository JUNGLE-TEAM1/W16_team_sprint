from types import SimpleNamespace

import httpx
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.base import Base
from backend.app.db.seeds import seed_demo_users, seed_support_cards
from backend.app.db.session import engine
from backend.app.main import app
from backend.app.models.post import Post
from backend.app.models.post_embedding import PostEmbedding

client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_demo_users(engine)
    seed_support_cards(engine)


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
            "title": "[청년/주거] 서울시 청년월세 지원",
            "content": "서울 거주 청년의 월세 부담을 줄이기 위한 주거비 지원 카드입니다.",
            "tag_names": ["청년", "주거", "월세", "서울"],
        },
    )
    assert first_post.status_code == 201

    second_post = client.post(
        "/api/v1/posts",
        headers=headers,
        json={
            "title": "[노인/돌봄] 노인맞춤돌봄서비스",
            "content": "어르신 안부 확인과 생활교육, 서비스 연계를 제공합니다.",
            "tag_names": ["노인", "돌봄"],
        },
    )
    assert second_post.status_code == 201

    response = client.post(
        "/api/v1/rag/assist",
        json={
            "title": "서울 청년 월세 상담",
            "content": "서울 거주 24세 취준생이고 월세 60만 원을 내고 있습니다.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stored_vectors"] == 50
    assert body["embedding_dimensions"] == 1536
    assert body["llm_provider"] == "none"
    assert body["llm_model"] == "rule-fallback"
    assert body["llm_used"] is False
    assert any("청년월세" in match["title"] or "청년수당" in match["title"] for match in body["matches"])
    assert body["matches"][0]["score"] > 0
    assert body["recommendation"]


def test_rag_assist_does_not_store_consultation_request_or_embedding() -> None:
    with Session(engine) as db:
        posts_before = db.scalar(select(func.count(Post.id)))
        embeddings_before = db.scalar(select(func.count(PostEmbedding.post_id)))

    response = client.post(
        "/api/v1/rag/assist",
        json={
            "title": "서울 거주 24세 취준생 월세 상담",
            "content": "서울 거주 24세 취준생이고 월세 60만 원을 내고 있습니다. 소득은 없습니다.",
            "top_k": 5,
            "include_references": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stored_vectors"] == 50
    assert body["matches"]

    with Session(engine) as db:
        posts_after = db.scalar(select(func.count(Post.id)))
        embeddings_after = db.scalar(select(func.count(PostEmbedding.post_id)))

    assert posts_after == posts_before
    assert embeddings_after == embeddings_before


def test_rag_assist_uses_openai_llm_when_api_key_is_configured(monkeypatch) -> None:
    headers = auth_headers()
    created = client.post(
        "/api/v1/posts",
        headers=headers,
        json={
            "title": "RAG duplicate assist with LLM",
            "content": "Use embeddings for support cards, then use an LLM to write the recommendation.",
            "tag_names": ["청년", "복지"],
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
            reference_fetch_enabled=False,
            reference_api_url="",
            reference_max_items=3,
            reference_timeout_seconds=1,
        ),
    )

    def fake_request_llm_assist(self, *, query_text, matches, references, duplicate_warning):
        assert "지원" in query_text
        assert matches
        return {
            "recommendation": "청년 지원 카드와 상담 조건을 확인해 신청 가능성이 높은 순서로 안내했습니다.",
            "match_summaries": [
                {
                    "post_id": matches[0].post_id,
                    "summary": "청년 지원 조건과 연결된 후보 카드입니다.",
                }
            ],
        }

    monkeypatch.setattr(rag_service.RagService, "_request_llm_assist", fake_request_llm_assist)

    response = client.post(
        "/api/v1/rag/assist",
        json={
            "title": "청년 지원 상담",
            "content": "서울 청년이 받을 수 있는 지원을 찾고 싶습니다.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["llm_provider"] == "openai"
    assert body["llm_model"] == "gpt-test"
    assert body["llm_used"] is True
    assert body["recommendation"] == "청년 지원 카드와 상담 조건을 확인해 신청 가능성이 높은 순서로 안내했습니다."
    assert body["matches"][0]["summary"] == "청년 지원 조건과 연결된 후보 카드입니다."


def test_rag_assist_falls_back_when_openai_llm_fails(monkeypatch) -> None:
    headers = auth_headers()
    created = client.post(
        "/api/v1/posts",
        headers=headers,
        json={
            "title": "[청년/주거] 서울시 청년월세 지원",
            "content": "서울 청년 주거비 부담을 낮추기 위한 지원 카드입니다.",
            "tag_names": ["청년", "주거", "서울"],
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
            reference_fetch_enabled=False,
            reference_api_url="",
            reference_max_items=3,
            reference_timeout_seconds=1,
        ),
    )

    def fake_request_llm_assist(self, *, query_text, matches, references, duplicate_warning):
        raise httpx.ConnectError("network unavailable")

    monkeypatch.setattr(rag_service.RagService, "_request_llm_assist", fake_request_llm_assist)

    response = client.post(
        "/api/v1/rag/assist",
        json={
            "title": "서울 청년 월세 상담",
            "content": "서울 거주 청년이고 월세 지원을 찾고 있습니다.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["llm_provider"] == "none"
    assert body["llm_model"] == "rule-fallback"
    assert body["llm_used"] is False
    assert body["recommendation"]


def test_rag_assist_returns_reference_materials(monkeypatch) -> None:
    headers = auth_headers()
    created = client.post(
        "/api/v1/posts",
        headers=headers,
        json={
            "title": "[청년/주거] 서울시 청년월세 지원",
            "content": "서울 청년 주거비 지원은 공공데이터와 정책 출처를 확인해야 합니다.",
            "tag_names": ["청년", "주거"],
        },
    )
    assert created.status_code == 201

    from backend.app.schemas.rag import RagReference
    from backend.app.services import rag_service

    def fake_fetch_reference_materials(*, query_text, matches, reference_urls):
        assert "청년" in query_text
        assert matches
        assert reference_urls == ["https://www.data.go.kr/data/15143273/openapi.do"]
        return [
            RagReference(
                title="온통청년 청년정책API",
                url="https://www.data.go.kr/data/15143273/openapi.do",
                source="공공데이터포털",
                excerpt="청년정책 공공데이터 참고자료입니다.",
            )
        ]

    monkeypatch.setattr(rag_service, "fetch_reference_materials", fake_fetch_reference_materials)

    response = client.post(
        "/api/v1/rag/assist",
        json={
            "title": "서울 청년 월세 지원",
            "content": "청년 주거 정책 출처를 함께 확인하고 싶습니다.",
            "reference_urls": ["https://www.data.go.kr/data/15143273/openapi.do"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["references"] == [
        {
            "title": "온통청년 청년정책API",
            "url": "https://www.data.go.kr/data/15143273/openapi.do",
            "source": "공공데이터포털",
            "excerpt": "청년정책 공공데이터 참고자료입니다.",
        }
    ]
