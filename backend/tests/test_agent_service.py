from backend.app.schemas.agent import AgentWritingAssistRequest
from backend.app.services.agent_service import AgentService
from backend.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_writing_agent_suggests_draft_and_tags() -> None:
    result = AgentService().assist_writing(
        AgentWritingAssistRequest(
            title="서울 청년 월세 상담",
            content="서울 거주 24세 취준생이고 소득 없음 상태에서 월세 60만 원을 내고 있습니다.",
            tag_names=["청년"],
        )
    )

    assert result.provider == "none"
    assert result.model == "rule-life-support-agent"
    assert result.suggested_title == "서울 청년 월세 상담"
    assert "상담 정리" in result.suggested_content
    assert "청년" in result.suggested_tag_names
    assert "주거" in result.suggested_tag_names
    assert "저소득" in result.suggested_tag_names
    assert len(result.outline) == 3
    assert len(result.next_questions) == 3


def test_writing_agent_endpoint_returns_suggestion() -> None:
    response = client.post(
        "/api/v1/agent/writing-assist",
        json={
            "title": "마포구 복지시설 상담",
            "content": "마포구에 살고 있고 가까운 복지관 상담을 받고 싶습니다.",
            "tag_names": ["마포구"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "none"
    assert body["model"] == "rule-life-support-agent"
    assert body["suggested_title"] == "마포구 복지시설 상담"
    assert "마포구" in body["suggested_tag_names"]
    assert "복지시설" in body["suggested_tag_names"]
