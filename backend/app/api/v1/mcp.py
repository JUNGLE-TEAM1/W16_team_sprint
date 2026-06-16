from typing import Any

from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_mcp_service
from backend.app.api.v1.auth import get_session_user
from backend.app.models.user import User
from backend.app.services.mcp_service import McpService

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.post("")
def handle_mcp_request(
    payload: dict[str, Any],
    _current_user: User = Depends(get_session_user),
    service: McpService = Depends(get_mcp_service),
) -> dict[str, Any]:
    return service.handle(payload)
