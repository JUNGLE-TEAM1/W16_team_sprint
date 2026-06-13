from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.auth import AuthSession, RefreshToken


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

    def create_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        self.db.add(refresh_token)
        self.db.flush()
        self.db.refresh(refresh_token)
        return refresh_token

    def get_refresh_token_by_hash(self, token_hash: str) -> RefreshToken | None:
        statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        return self.db.scalars(statement).first()

    def revoke_refresh_token(self, refresh_token: RefreshToken, revoked_at: datetime) -> None:
        refresh_token.revoked_at = revoked_at
        self.db.add(refresh_token)
