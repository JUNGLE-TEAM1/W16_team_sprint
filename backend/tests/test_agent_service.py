from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.agent import AgentWritingAssistRequest
from backend.app.services.agent_service import AgentService

client = TestClient(app)


def test_writing_agent_suggests_suwon_youth_draft_and_tags() -> None:
    result = AgentService().assist_writing(
        AgentWritingAssistRequest(
            title="수원시 청년 월세 상담",
            content="수원시 거주 24세 취준생이고 소득 없음 상태에서 월세 60만 원을 내고 있습니다.",
            tag_names=["청년"],
        )
    )

    assert result.provider == "none"
    assert result.model == "rule-suwon-youth-agent"
    assert result.suggested_title == "수원시 청년 월세 상담"
    assert "상담 정리" in result.suggested_content
    assert "청년" in result.suggested_tag_names
    assert "수원시" in result.suggested_tag_names
    assert "주거" in result.suggested_tag_names
    assert len(result.outline) == 3
    assert len(result.next_questions) == 3


def test_writing_agent_endpoint_returns_suwon_suggestion() -> None:
    response = client.post(
        "/api/v1/agent/writing-assist",
        json={
            "title": "수원 청년 창업 상담",
            "content": "수원시에 살고 있고 청년 창업 지원과 교육을 받고 싶습니다.",
            "tag_names": ["수원시"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "none"
    assert body["model"] == "rule-suwon-youth-agent"
    assert body["suggested_title"] == "수원 청년 창업 상담"
    assert "수원시" in body["suggested_tag_names"]
    assert "창업" in body["suggested_tag_names"]
