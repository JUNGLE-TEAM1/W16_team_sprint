from sqlalchemy.orm import Session

from backend.app.models.ai_request import AiRequest
from backend.app.models.user import User
from backend.app.repositories.ai_request_repository import AiRequestRepository
from backend.app.schemas.ai_request import AiRequestCreate


class AiRequestService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.requests = AiRequestRepository(db)

    def create(self, payload: AiRequestCreate, user: User) -> AiRequest:
        result = f"AI draft for user {user.id}: {payload.prompt[:80]}"
        request = AiRequest(requester_id=user.id, prompt=payload.prompt, result=result, status="completed")
        saved = self.requests.create(request)
        self.db.commit()
        return saved
