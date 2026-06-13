from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.db.session import get_db
from backend.app.models.ai_request import AiRequest
from backend.app.models.user import User
from backend.app.schemas.ai_request import AiRequestCreate, AiRequestRead
from backend.app.services.ai_request_service import AiRequestService

router = APIRouter(prefix="/ai/requests", tags=["ai-requests"])


@router.post("", response_model=AiRequestRead, status_code=status.HTTP_201_CREATED)
def create_ai_request(
    payload: AiRequestCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AiRequest:
    return AiRequestService(db).create(payload, user)
