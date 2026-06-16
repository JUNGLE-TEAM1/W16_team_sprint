from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from backend.app.schemas.mcp import (
    ExternalReferenceSearchArguments,
    ExternalReferenceSearchResult,
    JsonRpcRequest,
)
from backend.app.services.external_reference_service import (
    ExternalReferenceError,
    ExternalReferenceProvider,
)

SEARCH_EXTERNAL_REFERENCES_TOOL = "search_external_references"


class McpService:
    def __init__(self, external_references: ExternalReferenceProvider) -> None:
        self.external_references = external_references

    def handle(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            request = JsonRpcRequest.model_validate(payload)
        except ValidationError as exc:
            return self._error(
                request_id=payload.get("id") if isinstance(payload, dict) else None,
                code=-32600,
                message="Invalid JSON-RPC request",
                data={"code": "MCP_INVALID_REQUEST", "details": self._validation_errors(exc)},
            )

        if request.method == "initialize":
            return self._result(request.id, self._initialize_result())
        if request.method == "tools/list":
            return self._result(request.id, {"tools": [self._search_external_references_tool()]})
        if request.method == "tools/call":
            return self._call_tool(request)

        return self._error(
            request_id=request.id,
            code=-32601,
            message="Method not found",
            data={"code": "MCP_METHOD_NOT_FOUND", "method": request.method},
        )

    def _call_tool(self, request: JsonRpcRequest) -> dict[str, Any]:
        params = request.params or {}
        tool_name = params.get("name")
        arguments = params.get("arguments") or {}

        if tool_name != SEARCH_EXTERNAL_REFERENCES_TOOL:
            return self._error(
                request_id=request.id,
                code=-32602,
                message="Unknown tool",
                data={"code": "MCP_TOOL_NOT_FOUND", "tool": tool_name},
            )

        try:
            payload = ExternalReferenceSearchArguments.model_validate(arguments)
        except ValidationError as exc:
            return self._error(
                request_id=request.id,
                code=-32602,
                message="Invalid tool arguments",
                data={"code": "MCP_INVALID_TOOL_ARGUMENTS", "details": self._validation_errors(exc)},
            )

        try:
            items = self.external_references.search(payload)
        except ExternalReferenceError:
            return self._error(
                request_id=request.id,
                code=-32000,
                message="외부 참고자료를 불러오지 못했습니다.",
                data={"code": "MCP_EXTERNAL_REFERENCE_FAILED"},
            )

        result = ExternalReferenceSearchResult(items=items)
        count = len(result.items)
        return self._result(
            request.id,
            {
                "tool": SEARCH_EXTERNAL_REFERENCES_TOOL,
                "content": [
                    {
                        "type": "text",
                        "text": f"외부 참고자료 {count}건을 찾았습니다.",
                    }
                ],
                "structuredContent": result.model_dump(),
            },
        )

    def _initialize_result(self) -> dict[str, Any]:
        return {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "ai-knowledge-board-mcp",
                "version": "0.1.0",
            },
        }

    def _search_external_references_tool(self) -> dict[str, Any]:
        return {
            "name": SEARCH_EXTERNAL_REFERENCES_TOOL,
            "description": "작성 중인 게시글의 제목, 본문, 태그를 바탕으로 외부 개발 참고자료를 검색합니다.",
            "inputSchema": ExternalReferenceSearchArguments.model_json_schema(),
        }

    def _result(self, request_id: str | int | None, result: dict[str, Any]) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }

    def _error(
        self,
        request_id: str | int | None,
        code: int,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message,
                "data": data or {},
            },
        }

    def _validation_errors(self, exc: ValidationError) -> list[dict[str, Any]]:
        errors: list[dict[str, Any]] = []
        for error in exc.errors():
            safe_error = dict(error)
            ctx = safe_error.get("ctx")
            if isinstance(ctx, dict):
                safe_error["ctx"] = {key: str(value) for key, value in ctx.items()}
            errors.append(safe_error)
        return errors
