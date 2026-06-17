from types import SimpleNamespace

from app import main
from app.main import _decode_offer_sdp


def test_decode_offer_sdp_preserves_terminal_crlf() -> None:
    sdp = "v=0\r\no=- 123 2 IN IP4 127.0.0.1\r\na=end-of-candidates\r\n"

    decoded = _decode_offer_sdp(sdp.encode("utf-8"))

    assert decoded == sdp
    assert decoded.endswith("\r\n")


def test_realtime_session_config_enables_audio_conversation(monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "get_settings",
        lambda: SimpleNamespace(openai_realtime_model="test-realtime", openai_realtime_voice="marin"),
    )
    post = SimpleNamespace(
        title="테스트 게시글",
        question="태조는 어떤 왕인가?",
        ai_summary="태조에 대한 요약",
        ai_interpretation="태조에 대한 해석",
    )

    config = main._realtime_session_config(post, [], [])

    assert config["model"] == "test-realtime"
    assert config["output_modalities"] == ["audio"]
    assert "존댓말" in config["instructions"]
    assert "대화하듯 자연스럽게 시작" in config["instructions"]
    assert "실록 근거는 아니지만" not in config["instructions"]
    assert config["audio"]["input"]["transcription"]["model"] == "gpt-4o-mini-transcribe"
    assert config["audio"]["input"]["turn_detection"]["type"] == "server_vad"
    assert config["audio"]["input"]["turn_detection"]["create_response"] is False
    assert config["audio"]["output"]["voice"] == "marin"


def test_realtime_route_events_use_conversational_voice() -> None:
    retrieve_instruction = main._route_events("retrieve")[0]["response"]["instructions"]
    out_of_scope_instruction = main._route_events("out_of_scope")[0]["response"]["instructions"]

    assert "관련 실록 기록을 더 확인해보겠다고 안내합니다" not in retrieve_instruction
    assert "안내합니다" not in retrieve_instruction
    assert "잠시만요, 기록의 맥락을 보고 말씀드리겠습니다." in retrieve_instruction
    assert "다른 말은 덧붙이지 마세요" in retrieve_instruction
    assert "존댓말" in out_of_scope_instruction
    assert "실록 근거로 확인되는 내용은 아니지만" not in out_of_scope_instruction
    assert "기록에서 바로 확인되는 내용은 아닙니다만" in out_of_scope_instruction


def test_realtime_search_query_prioritizes_newly_mentioned_king() -> None:
    post = SimpleNamespace(
        title="태조는 위대한 왕인가?",
        question="태조가 조선을 건국했다지만, 정말 위대한 왕일까?",
        ai_summary="태조는 조선 건국과 제도 정비의 근거가 있다.",
        ai_interpretation="정도전과 조선경국전이 국가 기틀을 마련했다.",
    )

    query = main._realtime_search_query(post, "그럼 태종 때도 비슷한 사례가 있었어?")

    assert "태종" in query
    assert "태조" not in query
    assert "이성계" not in query
    assert "건국" in query


def test_voice_message_out_keeps_chat_metadata() -> None:
    message = SimpleNamespace(
        id=7,
        session_id=3,
        post_id=2,
        author=SimpleNamespace(username="tester"),
        role="assistant",
        content="기록상으로는 태조의 즉위 명분이 중요하게 다뤄집니다.",
        route_action="retrieve",
        route_reason="추가 기록을 확인했습니다.",
        search_query="태조 즉위 명분",
        evidence_article_ids=["T001", "T002"],
        created_at="2026-06-17T12:00:00+09:00",
    )

    output = main._voice_message_out(message)

    assert output.role == "assistant"
    assert output.username == "tester"
    assert output.route_action == "retrieve"
    assert output.evidence_article_ids == ["T001", "T002"]
