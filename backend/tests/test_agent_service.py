from backend.app.schemas.agent import AgentWritingAssistRequest
from backend.app.services.agent_service import AgentService
from backend.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_writing_agent_suggests_draft_and_tags() -> None:
    result = AgentService().assist_writing(
        AgentWritingAssistRequest(
            title="MCP 참고자료 Agent",
            content="공식 문서와 외부 API에서 참고자료를 가져와 글쓰기 초안을 보강한다.",
            tag_names=["mcp"],
        )
    )

    assert result.provider == "none"
    assert result.model == "rule-writing-agent"
    assert result.suggested_title == "MCP 참고자료 Agent"
    assert "정리 방향" in result.suggested_content
    assert "mcp" in result.suggested_tag_names
    assert "agent" in result.suggested_tag_names
    assert len(result.outline) == 3
    assert len(result.next_questions) == 3


def test_writing_agent_endpoint_returns_suggestion() -> None:
    response = client.post(
        "/api/v1/agent/writing-assist",
        json={
            "title": "Agent 글쓰기 도우미",
            "content": "게시글 초안과 태그를 빠르게 추천한다.",
            "tag_names": ["agent"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "none"
    assert body["model"] == "rule-writing-agent"
    assert body["suggested_title"] == "Agent 글쓰기 도우미"
    assert "agent" in body["suggested_tag_names"]
