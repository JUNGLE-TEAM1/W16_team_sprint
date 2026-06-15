from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.auth import AuthSession


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_session(self, auth_session: AuthSession) -> AuthSession:
        self.db.add(auth_session)
        self.db.flush()
        self.db.refresh(auth_session)
        return auth_session

    def get_session_by_token_hash(self, token_hash: str) -> AuthSession | None:
        statement = select(AuthSession).where(AuthSession.token_hash == token_hash)
        return self.db.scalars(statement).first()

    def delete_session(self, auth_session: AuthSession) -> None:
        self.db.delete(auth_session)
