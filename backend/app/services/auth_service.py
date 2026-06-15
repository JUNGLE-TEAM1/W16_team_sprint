from dataclasses import dataclass
from datetime import timedelta

from fastapi import status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.errors import AppError
from backend.app.core.security import (
    create_opaque_token,
    hash_password,
    hash_token,
    utcnow,
    verify_password,
)
from backend.app.models.auth import AuthSession
from backend.app.models.user import User
from backend.app.repositories.auth_repository import AuthRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.auth import LoginRequest, UserCreate


@dataclass(frozen=True)
class SessionLogin:
    user: User
    session_token: str


class AuthService:
    def __init__(
        self,
        db: Session,
        users: UserRepository,
        auth: AuthRepository,
    ) -> None:
        self.db = db
        self.users = users
        self.auth = auth

    def register(self, payload: UserCreate) -> User:
        if self.users.get_by_username(payload.username) is not None:
            raise AppError(
                code="USERNAME_ALREADY_EXISTS",
                message="이미 사용 중인 username입니다.",
                status_code=status.HTTP_409_CONFLICT,
                details={"username": payload.username},
            )

        user = User(
            username=payload.username,
            password_hash=hash_password(payload.password),
            display_name=payload.display_name,
        )
        saved_user = self.users.create(user)
        self.db.commit()
        return saved_user

    def login_with_session(self, payload: LoginRequest) -> SessionLogin:
        user = self._authenticate(payload)
        session_token = create_opaque_token()
        auth_session = AuthSession(
            user_id=user.id,
            token_hash=hash_token(session_token),
            expires_at=utcnow() + timedelta(hours=settings.session_expire_hours),
        )
        self.auth.create_session(auth_session)
        self.db.commit()
        return SessionLogin(user=user, session_token=session_token)

    def get_user_by_session_token(self, session_token: str | None) -> User:
        if not session_token:
            raise self._unauthorized("SESSION_REQUIRED", "세션 쿠키가 필요합니다.")

        auth_session = self.auth.get_session_by_token_hash(hash_token(session_token))
        if auth_session is None or auth_session.expires_at <= utcnow():
            raise self._unauthorized("INVALID_SESSION", "유효하지 않은 세션입니다.")

        user = self.users.get(auth_session.user_id)
        if user is None:
            raise self._unauthorized("INVALID_SESSION", "유효하지 않은 세션입니다.")
        return user

    def logout_session(self, session_token: str | None) -> None:
        if session_token:
            auth_session = self.auth.get_session_by_token_hash(hash_token(session_token))
            if auth_session is not None:
                self.auth.delete_session(auth_session)
                self.db.commit()

    def _authenticate(self, payload: LoginRequest) -> User:
        user = self.users.get_by_username(payload.username)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise self._unauthorized("INVALID_CREDENTIALS", "username 또는 password가 올바르지 않습니다.")
        return user

    @staticmethod
    def _unauthorized(code: str, message: str) -> AppError:
        return AppError(
            code=code,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
