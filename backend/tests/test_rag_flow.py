from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from backend.app.db.base import Base
from backend.app.db.seeds import seed_demo_users, seed_support_cards
from backend.app.db.session import engine
from backend.app.db.vector import vector_literal
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


def test_rag_assist_finds_suwon_policy_cards() -> None:
    response = client.post(
        "/api/v1/rag/assist",
        json={
            "title": "수원시 청년 월세 상담",
            "content": "경기도 수원시 거주 24세 청년이고 월세 60만 원을 내고 있습니다.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stored_vectors"] == 3
    assert body["embedding_dimensions"] == 1536
    assert body["llm_provider"] == "none"
    assert body["llm_model"] == "rule-fallback"
    assert body["llm_used"] is False
    assert "청년월세지원사업" in body["matches"][0]["title"]
    assert body["matches"][0]["score"] >= 0.55
    assert body["mvp_highlight"]["post_id"] == body["matches"][0]["post_id"]
    assert "청년월세지원사업" in body["mvp_highlight"]["title"]
    assert "월세/주거비 부담" in body["mvp_highlight"]["why_it_fits"]
    assert body["recommendation"]


def test_rag_assist_does_not_store_consultation_request_or_embedding() -> None:
    with Session(engine) as db:
        posts_before = db.scalar(select(func.count(Post.id)))
        embeddings_before = db.scalar(select(func.count(PostEmbedding.post_id)))

    response = client.post(
        "/api/v1/rag/assist",
        json={
            "title": "수원시 거주 24세 청년 월세 상담",
            "content": "경기도 수원시 거주 24세 청년이고 월세 60만 원을 내고 있습니다. 소득은 없습니다.",
            "top_k": 5,
            "include_references": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stored_vectors"] == 3
    assert body["matches"]

    with Session(engine) as db:
        posts_after = db.scalar(select(func.count(Post.id)))
        embeddings_after = db.scalar(select(func.count(PostEmbedding.post_id)))

    assert posts_after == posts_before
    assert embeddings_after == embeddings_before


def test_rag_assist_scores_financial_need_above_generic_cards() -> None:
    response = client.post(
        "/api/v1/rag/assist",
        json={
            "title": "수원시 청년 정책 지원 상담",
            "content": "현재 24세이며 경제적 어려움이 있습니다. 수원시 청년 지원 정책 중 생활비나 월세 부담을 줄일 수 있는 제도를 알고 싶습니다.",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "청년월세지원사업" in body["matches"][0]["title"]
    assert body["matches"][0]["score"] >= 0.55
    assert body["mvp_highlight"]["post_id"] == body["matches"][0]["post_id"]
    assert "매칭률" in body["mvp_highlight"]["why_highlight"]
    assert all("창업" not in match["title"] for match in body["matches"][:1])


def test_pgvector_match_support_cards_rpc_is_available() -> None:
    if engine.dialect.name != "postgresql":
        pytest.skip("pgvector RPC is only created for PostgreSQL")

    query_vector = vector_literal([1.0] + [0.0] * 1535)
    with Session(engine) as db:
        exists = db.execute(
            text("SELECT count(*) FROM pg_proc WHERE proname = 'match_support_cards'")
        ).scalar_one()
        hnsw_index = db.execute(
            text(
                "SELECT indexdef FROM pg_indexes "
                "WHERE tablename = 'post_embeddings' "
                "AND indexname = 'ix_post_embeddings_embedding_hnsw'"
            )
        ).scalar_one_or_none()
        rows = db.execute(
            text(
                "SELECT post_id, score "
                "FROM match_support_cards(CAST(:query_vector AS vector), :limit)"
            ),
            {"query_vector": query_vector, "limit": 3},
        ).all()

    assert exists >= 1
    assert hnsw_index is not None
    assert "USING hnsw" in hnsw_index
    assert "vector_cosine_ops" in hnsw_index
    assert rows
    assert all(row.post_id for row in rows)


def test_rag_assist_uses_openai_llm_when_api_key_is_configured(monkeypatch) -> None:
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
        assert "수원" in query_text
        assert matches
        return {
            "recommendation": "수원시 청년정책 카드와 상담 조건을 확인해 신청 가능성이 높은 순서로 안내했습니다.",
            "match_summaries": [
                {
                    "post_id": matches[0].post_id,
                    "summary": "수원시 청년정책 조건과 연결된 후보 카드입니다.",
                }
            ],
        }

    monkeypatch.setattr(rag_service.RagService, "_request_llm_assist", fake_request_llm_assist)

    response = client.post(
        "/api/v1/rag/assist",
        json={
            "title": "수원 청년 지원 상담",
            "content": "수원시에 사는 청년이 받을 수 있는 지원을 찾고 싶습니다.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["llm_provider"] == "openai"
    assert body["llm_model"] == "gpt-test"
    assert body["llm_used"] is True
    assert body["recommendation"] == "수원시 청년정책 카드와 상담 조건을 확인해 신청 가능성이 높은 순서로 안내했습니다."
    assert body["matches"][0]["summary"] == "수원시 청년정책 조건과 연결된 후보 카드입니다."


def test_rag_assist_accepts_structured_llm_recommendation(monkeypatch) -> None:
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
        return {
            "recommendation": {
                "text": "청년월세지원사업을 먼저 확인하세요.",
                "application_checklist": ["수원시 거주 여부 확인", "사업기간 확인"],
                "contact_info": {"phone": "031-000-0000"},
            },
            "match_summaries": [
                {
                    "post_id": matches[0].post_id,
                    "summary": {"text": "청년월세지원사업 후보입니다."},
                }
            ],
        }

    monkeypatch.setattr(rag_service.RagService, "_request_llm_assist", fake_request_llm_assist)

    response = client.post(
        "/api/v1/rag/assist",
        json={
            "title": "수원 청년 월세 상담",
            "content": "수원시 거주 청년이고 월세 지원을 찾고 있습니다.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["llm_used"] is True
    assert "청년월세지원사업" in body["recommendation"]
    assert "수원시 거주 여부 확인" in body["recommendation"]
    assert body["matches"][0]["summary"] == "청년월세지원사업 후보입니다."


def test_rag_assist_falls_back_when_openai_llm_fails(monkeypatch) -> None:
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
            "title": "수원 청년 월세 상담",
            "content": "수원시 거주 청년이고 월세 지원을 찾고 있습니다.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["llm_provider"] == "none"
    assert body["llm_model"] == "rule-fallback"
    assert body["llm_used"] is False
    assert body["recommendation"]


def test_rag_assist_returns_reference_materials(monkeypatch) -> None:
    from backend.app.schemas.rag import RagReference
    from backend.app.services import rag_service

    def fake_fetch_reference_materials(*, query_text, matches, reference_urls):
        assert "수원" in query_text
        assert matches
        assert reference_urls == ["https://infuser.odcloud.kr/oas/docs?namespace=15089956/v1"]
        return [
            RagReference(
                title="경기도 수원시 청년지원사업 API",
                url="https://infuser.odcloud.kr/oas/docs?namespace=15089956/v1",
                source="공공데이터포털",
                excerpt="수원시 청년지원사업 상세설명 공공데이터 참고자료입니다.",
            )
        ]

    monkeypatch.setattr(rag_service, "fetch_reference_materials", fake_fetch_reference_materials)

    response = client.post(
        "/api/v1/rag/assist",
        json={
            "title": "수원 청년 월세 지원",
            "content": "수원시 청년정책 출처를 함께 확인하고 싶습니다.",
            "reference_urls": ["https://infuser.odcloud.kr/oas/docs?namespace=15089956/v1"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["references"] == [
        {
            "title": "경기도 수원시 청년지원사업 API",
            "url": "https://infuser.odcloud.kr/oas/docs?namespace=15089956/v1",
            "source": "공공데이터포털",
            "excerpt": "수원시 청년지원사업 상세설명 공공데이터 참고자료입니다.",
        }
    ]
