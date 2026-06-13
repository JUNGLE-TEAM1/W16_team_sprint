from datetime import timedelta

from fastapi import status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.errors import AppError
from backend.app.core.security import (
    create_access_token,
    hash_password,
    hash_token,
    issue_opaque_token,
    verify_password,
)
from backend.app.core.time import utc_now
from backend.app.models.user import RefreshToken, User, UserSession
from backend.app.repositories.user_repository import SessionRepository, UserRepository
from backend.app.schemas.auth import LoginRequest, TokenPair, UserCreate


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.sessions = SessionRepository(db)

    def register(self, payload: UserCreate) -> User:
        if self.users.get_by_email(payload.email) is not None:
            raise AppError("EMAIL_ALREADY_REGISTERED", "Email is already registered", status.HTTP_409_CONFLICT)
        user = User(email=payload.email, password_hash=hash_password(payload.password), role=payload.role)
        saved = self.users.create(user)
        self.db.commit()
        return saved

    def login(self, payload: LoginRequest) -> tuple[User, TokenPair]:
        user = self.users.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise AppError("INVALID_CREDENTIALS", "Invalid email or password", status.HTTP_401_UNAUTHORIZED)
        pair = self._issue_login_tokens(user)
        self.db.commit()
        return user, pair

    def refresh(self, refresh_token: str) -> TokenPair:
        now = utc_now()
        stored = self.sessions.get_active_refresh_token(hash_token(refresh_token), now)
        if stored is None:
            raise AppError("INVALID_REFRESH_TOKEN", "Refresh token is invalid or expired", status.HTTP_401_UNAUTHORIZED)
        user = self.users.get(stored.user_id)
        if user is None:
            raise AppError("USER_NOT_FOUND", "User no longer exists", status.HTTP_401_UNAUTHORIZED)
        stored.revoked_at = now
        pair = self._issue_login_tokens(user)
        self.db.commit()
        return pair

    def _issue_login_tokens(self, user: User) -> TokenPair:
        now = utc_now()
        session_id = issue_opaque_token()
        csrf_token = issue_opaque_token()
        refresh_token = issue_opaque_token()
        self.sessions.create_session(
            UserSession(
                user_id=user.id,
                session_id=session_id,
                csrf_token=csrf_token,
                expires_at=now + timedelta(seconds=settings.refresh_token_seconds),
            )
        )
        self.sessions.create_refresh_token(
            RefreshToken(
                user_id=user.id,
                token_hash=hash_token(refresh_token),
                expires_at=now + timedelta(seconds=settings.refresh_token_seconds),
            )
        )
        return TokenPair(
            access_token=create_access_token(user.id, user.role),
            refresh_token=refresh_token,
            session_id=session_id,
            csrf_token=csrf_token,
        )
