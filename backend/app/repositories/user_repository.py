from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.user import RefreshToken, User, UserSession


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def list(self) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.id.asc())))


class SessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_session(self, session: UserSession) -> UserSession:
        self.db.add(session)
        self.db.flush()
        return session

    def get_active_session(self, session_id: str, now: datetime) -> UserSession | None:
        return self.db.scalar(
            select(UserSession).where(
                UserSession.session_id == session_id,
                UserSession.revoked_at.is_(None),
                UserSession.expires_at > now,
            )
        )

    def create_refresh_token(self, token: RefreshToken) -> RefreshToken:
        self.db.add(token)
        self.db.flush()
        return token

    def get_active_refresh_token(self, token_hash: str, now: datetime) -> RefreshToken | None:
        return self.db.scalar(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > now,
            )
        )
