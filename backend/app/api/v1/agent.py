from fastapi import APIRouter

from backend.app.api.dependencies import AgentServiceDependency
from backend.app.schemas.agent import AgentWritingAssistRequest, AgentWritingAssistResponse

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/writing-assist", response_model=AgentWritingAssistResponse)
def assist_writing(
    payload: AgentWritingAssistRequest,
    service: AgentServiceDependency,
) -> AgentWritingAssistResponse:
    return service.assist_writing(payload)
