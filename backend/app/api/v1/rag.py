from fastapi import APIRouter

from backend.app.api.dependencies import RagServiceDependency
from backend.app.schemas.rag import RagAssistRequest, RagAssistResponse

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/assist", response_model=RagAssistResponse)
def assist_writing(payload: RagAssistRequest, service: RagServiceDependency) -> RagAssistResponse:
    return service.assist(payload)
