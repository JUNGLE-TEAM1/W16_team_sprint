import pytest

from app.services import llm


class DummySettings:
    openai_api_key = None
    openai_model = "test-model"


@pytest.mark.anyio
async def test_discussion_stream_uses_fallback_without_api_key(monkeypatch) -> None:
    monkeypatch.setattr(llm, "get_settings", lambda: DummySettings())

    chunks = [
        chunk
        async for chunk in llm.stream_discussion_reply(
            "이 근거를 어떻게 토론하면 좋을까?",
            {
                "title": "테스트 게시글",
                "question": "테스트 질문",
                "ai_summary": "테스트 요약",
                "ai_interpretation": "테스트 해석",
            },
            [],
            [],
        )
    ]

    assert chunks
    assert "임시 토론 답변" in "".join(chunks)
