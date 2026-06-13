from datetime import datetime

from sqlalchemy.orm import Session

from backend.app.models.user_session import UserSession


class SessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, session: UserSession) -> UserSession:
        self.db.add(session)
        self.db.flush()
        self.db.refresh(session)
        return session

    def get(self, session_id: str) -> UserSession | None:
        return self.db.get(UserSession, session_id)

    def revoke(self, session: UserSession, revoked_at: datetime) -> None:
        session.revoked_at = revoked_at
        self.db.flush()

    def rotate_refresh_token(
        self,
        session: UserSession,
        *,
        refresh_token_hash: str,
        csrf_token: str,
        expires_at: datetime,
    ) -> UserSession:
        session.refresh_token_hash = refresh_token_hash
        session.csrf_token = csrf_token
        session.expires_at = expires_at
        self.db.flush()
        self.db.refresh(session)
        return session
