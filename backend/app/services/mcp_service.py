from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from backend.app.schemas.mcp import (
    FindNearbyAnimalHospitalsArguments,
    GeocodeRegionArguments,
    JsonRpcRequest,
)
from backend.app.services.kakao_local_service import (
    LocationSearchError,
    LocationSearchProvider,
)

GEOCODE_REGION_TOOL = "geocode_region"
FIND_NEARBY_ANIMAL_HOSPITALS_TOOL = "find_nearby_animal_hospitals"


class McpService:
    def __init__(self, location_search: LocationSearchProvider) -> None:
        self.location_search = location_search

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
            return self._result(
                request.id,
                {"tools": [self._geocode_region_tool(), self._find_nearby_animal_hospitals_tool()]},
            )
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

        if tool_name == GEOCODE_REGION_TOOL:
            return self._call_geocode_region(request, arguments)
        if tool_name == FIND_NEARBY_ANIMAL_HOSPITALS_TOOL:
            return self._call_find_nearby_animal_hospitals(request, arguments)

        return self._error(
            request_id=request.id,
            code=-32602,
            message="Unknown tool",
            data={"code": "MCP_TOOL_NOT_FOUND", "tool": tool_name},
        )

    def _call_geocode_region(self, request: JsonRpcRequest, arguments: dict[str, Any]) -> dict[str, Any]:
        try:
            payload = GeocodeRegionArguments.model_validate(arguments)
        except ValidationError as exc:
            return self._error(
                request_id=request.id,
                code=-32602,
                message="Invalid tool arguments",
                data={"code": "MCP_INVALID_TOOL_ARGUMENTS", "details": self._validation_errors(exc)},
            )

        try:
            result = self.location_search.geocode_region(payload)
        except LocationSearchError:
            return self._error(
                request_id=request.id,
                code=-32000,
                message="지역 정보를 불러오지 못했습니다.",
                data={"code": "MCP_LOCATION_SEARCH_FAILED"},
            )

        return self._result(
            request.id,
            {
                "tool": GEOCODE_REGION_TOOL,
                "content": [
                    {
                        "type": "text",
                        "text": f"{result.location.normalized_address} 지역 좌표를 찾았습니다.",
                    }
                ],
                "structuredContent": result.model_dump(),
            },
        )

    def _call_find_nearby_animal_hospitals(
        self,
        request: JsonRpcRequest,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            payload = FindNearbyAnimalHospitalsArguments.model_validate(arguments)
        except ValidationError as exc:
            return self._error(
                request_id=request.id,
                code=-32602,
                message="Invalid tool arguments",
                data={"code": "MCP_INVALID_TOOL_ARGUMENTS", "details": self._validation_errors(exc)},
            )

        try:
            result = self.location_search.find_nearby_animal_hospitals(payload)
        except LocationSearchError:
            return self._error(
                request_id=request.id,
                code=-32000,
                message="동물병원 정보를 불러오지 못했습니다.",
                data={"code": "MCP_LOCATION_SEARCH_FAILED"},
            )

        count = len(result.items)
        return self._result(
            request.id,
            {
                "tool": FIND_NEARBY_ANIMAL_HOSPITALS_TOOL,
                "content": [
                    {
                        "type": "text",
                        "text": f"동물병원 후보 {count}건을 찾았습니다.",
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
                "name": "pet-care-board-mcp",
                "version": "0.1.0",
            },
        }

    def _geocode_region_tool(self) -> dict[str, Any]:
        return {
            "name": GEOCODE_REGION_TOOL,
            "description": "보호자가 입력한 지역 문자열을 Kakao Local API 기반 좌표와 주소 정보로 정규화합니다.",
            "inputSchema": GeocodeRegionArguments.model_json_schema(),
        }

    def _find_nearby_animal_hospitals_tool(self) -> dict[str, Any]:
        return {
            "name": FIND_NEARBY_ANIMAL_HOSPITALS_TOOL,
            "description": "보호자 지역 또는 좌표를 기준으로 가까운 동물병원 후보를 조회합니다.",
            "inputSchema": FindNearbyAnimalHospitalsArguments.model_json_schema(),
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
