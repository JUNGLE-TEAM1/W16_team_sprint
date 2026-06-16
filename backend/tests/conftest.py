from types import SimpleNamespace
import math

import pytest


TEST_SUWON_POLICY_CARDS = [
    {
        "title": "[수원청년/2025] 청년월세지원사업",
        "content": (
            "사업명: 청년월세지원사업\n"
            "사업내용: 경기도 수원시 월세 계약 체결 중인 1인 가구 미혼 청년에게 월 10만원 임차료 지원\n"
            "사업기간: 2025-03-02 ~ 2025-10-31\n"
            "지역: 경기도 수원시\n"
            "전화번호: 031-5191-3958\n"
            "상세 URL: http://www.swyouth.kr"
        ),
        "tags": ["수원시", "경기도", "청년", "청년정책", "2025", "주거", "월세", "복지"],
    },
    {
        "title": "[수원청년/2025] 취업준비청년 교통비 지원",
        "content": (
            "사업명: 취업준비청년 교통비 지원\n"
            "사업내용: 수원시 청년 구직자의 면접과 구직활동 교통비 부담 완화\n"
            "사업기간: 2025-04-01 ~ 2025-12-31\n"
            "지역: 경기도 수원시\n"
            "전화번호: 031-228-3955"
        ),
        "tags": ["수원시", "경기도", "청년", "청년정책", "2025", "취업", "교통"],
    },
    {
        "title": "[수원청년/2025] 청년 창업 지원",
        "content": (
            "사업명: 청년 창업 지원\n"
            "사업내용: 수원시 청년 창업자의 사업화 교육과 컨설팅 지원\n"
            "사업기간: 2025-01-01 ~ 2025-12-31\n"
            "지역: 경기도 수원시\n"
            "전화번호: 031-228-3272"
        ),
        "tags": ["수원시", "경기도", "청년", "청년정책", "2025", "창업", "교육", "상담"],
    },
]


@pytest.fixture(autouse=True)
def use_local_ai_settings(monkeypatch) -> None:
    local_settings = SimpleNamespace(
        embedding_provider="local",
        openai_api_key="",
        openai_base_url="https://api.openai.com/v1",
        openai_embedding_model="text-embedding-3-small",
        openai_embedding_dimensions=1536,
        openai_llm_model="gpt-test",
        openai_llm_max_output_tokens=300,
        openai_timeout_seconds=1,
        reference_fetch_enabled=False,
        reference_api_url="",
        reference_max_items=3,
        reference_timeout_seconds=1,
    )

    from backend.app.core import embedding
    from backend.app.db import seeds
    from backend.app.services import agent_service, rag_service

    def fake_embed_text(value: str) -> list[float]:
        normalized = value.lower()
        vector = [0.0] * 1536
        weighted_keywords = (
            (0, 1.0, ("수원", "수원시")),
            (1, 1.0, ("청년", "24세", "취준생", "구직자")),
            (2, 3.0, ("월세", "임차", "임차료", "주거")),
            (3, 3.0, ("취업", "구직", "면접", "일자리", "교통비")),
            (4, 3.0, ("창업", "사업화", "스타트업")),
            (5, 2.0, ("경제", "어려움", "생활비", "소득", "지원금")),
            (6, 1.5, ("교육", "강의", "컨설팅")),
        )
        for index, weight, keywords in weighted_keywords:
            if any(keyword in normalized for keyword in keywords):
                vector[index] = weight
        norm = math.sqrt(sum(component * component for component in vector))
        return [component / norm for component in vector] if norm else vector

    monkeypatch.setattr(embedding, "settings", local_settings)
    monkeypatch.setattr(agent_service, "settings", local_settings)
    monkeypatch.setattr(rag_service, "settings", local_settings)
    monkeypatch.setattr(embedding, "embed_text", fake_embed_text)
    monkeypatch.setattr(seeds, "embed_text", fake_embed_text)
    monkeypatch.setattr(rag_service, "embed_text", fake_embed_text)
    monkeypatch.setattr(seeds, "fetch_suwon_youth_policy_cards", lambda: TEST_SUWON_POLICY_CARDS)
