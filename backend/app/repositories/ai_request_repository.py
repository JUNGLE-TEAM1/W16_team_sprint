from sqlalchemy.orm import Session

from backend.app.models.ai_request import AiRequest


class AiRequestRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, request: AiRequest) -> AiRequest:
        self.db.add(request)
        self.db.flush()
        self.db.refresh(request)
        return request
