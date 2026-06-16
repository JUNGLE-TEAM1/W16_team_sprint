from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.app.api.dependencies import get_external_reference_provider
from backend.app.db.base import Base
from backend.app.db.session import engine
from backend.app.main import app
from backend.app.schemas.mcp import ExternalReferenceItem, ExternalReferenceSearchArguments
from backend.app.services.external_reference_service import ExternalReferenceError


class FakeExternalReferenceProvider:
    def search(self, payload: ExternalReferenceSearchArguments) -> list[ExternalReferenceItem]:
        return [
            ExternalReferenceItem(
                title=f"{payload.title} 관련 Stack Overflow 질문",
                url="https://stackoverflow.com/questions/1/example",
                source="Stack Overflow",
                summary="답변 2개 · 점수 5 · 채택된 답변이 있습니다.",
                tags=["fastapi", "auth"],
                score=5,
                answer_count=2,
                is_answered=True,
            )
        ]


class FailingExternalReferenceProvider:
    def search(self, payload: ExternalReferenceSearchArguments) -> list[ExternalReferenceItem]:
        raise ExternalReferenceError("boom")


def setup_function() -> None:
    app.dependency_overrides.clear()
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS refresh_tokens CASCADE"))
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def use_fake_external_references(provider=None) -> None:  # noqa: ANN001
    app.dependency_overrides[get_external_reference_provider] = (
        lambda: provider or FakeExternalReferenceProvider()
    )


def register_and_login(client: TestClient) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "team1",
            "password": "password123",
            "display_name": "Team One",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/session/login",
        json={"username": "team1", "password": "password123"},
    )
    assert login_response.status_code == 200


def json_rpc_request(method: str, params: dict | None = None) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": "test-1",
        "method": method,
        "params": params or {},
    }


def test_mcp_requires_session() -> None:
    use_fake_external_references()
    client = TestClient(app)

    response = client.post("/api/v1/mcp", json=json_rpc_request("tools/list"))

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "SESSION_REQUIRED"


def test_mcp_lists_external_reference_tool() -> None:
    use_fake_external_references()
    client = TestClient(app)
    register_and_login(client)

    response = client.post("/api/v1/mcp", json=json_rpc_request("tools/list"))

    assert response.status_code == 200
    body = response.json()
    tool = body["result"]["tools"][0]
    assert tool["name"] == "search_external_references"
    assert "inputSchema" in tool


def test_mcp_search_external_references_tool_returns_cards() -> None:
    use_fake_external_references()
    client = TestClient(app)
    register_and_login(client)

    response = client.post(
        "/api/v1/mcp",
        json=json_rpc_request(
            "tools/call",
            {
                "name": "search_external_references",
                "arguments": {
                    "title": "FastAPI Session 인증 흐름",
                    "content": "쿠키 기반 세션 인증과 의존성 주입 흐름을 정리합니다.",
                    "tags": ["fastapi", "auth"],
                },
            },
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert "error" not in body
    items = body["result"]["structuredContent"]["items"]
    assert items[0]["source"] == "Stack Overflow"
    assert items[0]["answer_count"] == 2
    assert items[0]["is_answered"] is True


def test_mcp_returns_json_rpc_error_for_unknown_tool() -> None:
    use_fake_external_references()
    client = TestClient(app)
    register_and_login(client)

    response = client.post(
        "/api/v1/mcp",
        json=json_rpc_request(
            "tools/call",
            {
                "name": "unknown_tool",
                "arguments": {},
            },
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["error"]["code"] == -32602
    assert body["error"]["data"]["code"] == "MCP_TOOL_NOT_FOUND"


def test_mcp_returns_json_rpc_error_for_invalid_arguments() -> None:
    use_fake_external_references()
    client = TestClient(app)
    register_and_login(client)

    response = client.post(
        "/api/v1/mcp",
        json=json_rpc_request(
            "tools/call",
            {
                "name": "search_external_references",
                "arguments": {
                    "title": "짧음",
                    "content": "부족",
                },
            },
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["error"]["code"] == -32602
    assert body["error"]["data"]["code"] == "MCP_INVALID_TOOL_ARGUMENTS"


def test_mcp_returns_json_rpc_error_when_external_search_fails() -> None:
    use_fake_external_references(FailingExternalReferenceProvider())
    client = TestClient(app)
    register_and_login(client)

    response = client.post(
        "/api/v1/mcp",
        json=json_rpc_request(
            "tools/call",
            {
                "name": "search_external_references",
                "arguments": {
                    "title": "FastAPI Session 인증 흐름",
                    "content": "쿠키 기반 세션 인증과 의존성 주입 흐름을 정리합니다.",
                },
            },
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["error"]["code"] == -32000
    assert body["error"]["data"]["code"] == "MCP_EXTERNAL_REFERENCE_FAILED"
