from types import SimpleNamespace

import pytest

from app.services import realtime_orchestrator
from app.services.realtime_orchestrator import fallback_realtime_route, route_realtime_turn


def test_fallback_realtime_route_rejects_out_of_scope_question() -> None:
    decision = fallback_realtime_route("삼겹살과 목살 중 뭐가 더 맛있어?", [])

    assert decision["action"] == "out_of_scope"
    assert decision["search_query"] == ""


def test_fallback_realtime_route_retrieves_joseon_expansion_question() -> None:
    decision = fallback_realtime_route(
        "그럼 태종 때도 비슷한 사례가 있었어?",
        [{"article_id": "waa_001", "title": "태조 관련 기사"}],
    )

    assert decision["action"] == "retrieve"
    assert "태종" in decision["search_query"]


def test_fallback_realtime_route_clarifies_vague_expansion_without_evidence() -> None:
    decision = fallback_realtime_route("그럼 태종 때도 비슷한 사례가 있었어?", [])

    assert decision["action"] == "clarify"
    assert decision["search_query"] == ""


def test_fallback_realtime_route_uses_current_context_for_followup() -> None:
    decision = fallback_realtime_route(
        "이 기록에서 태조가 왜 재검토하라고 한 거야?",
        [{"article_id": "waa_001", "title": "태조 관련 기사"}],
    )

    assert decision["action"] == "current_context"


@pytest.mark.anyio
async def test_route_realtime_turn_keeps_retrieve_when_llm_says_out_of_scope(monkeypatch) -> None:
    class DummyCompletions:
        async def create(self, **kwargs):
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content='{"action":"out_of_scope","search_query":"","reason":"잘못된 범위 밖 판단"}'
                        )
                    )
                ]
            )

    class DummyClient:
        def __init__(self, api_key):
            self.chat = SimpleNamespace(completions=DummyCompletions())

    monkeypatch.setattr(
        realtime_orchestrator,
        "get_settings",
        lambda: SimpleNamespace(openai_api_key="test-key", openai_model="test-model"),
    )
    monkeypatch.setattr(realtime_orchestrator, "AsyncOpenAI", DummyClient)

    decision = await route_realtime_turn(
        "그럼 태종 때도 비슷한 사례가 있었어?",
        {"title": "테스트", "question": "테스트"},
        [{"article_id": "waa_001", "title": "태조 관련 기사"}],
    )

    assert decision["action"] == "retrieve"
