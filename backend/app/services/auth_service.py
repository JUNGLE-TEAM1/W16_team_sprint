from dataclasses import dataclass
from datetime import timedelta
from typing import Protocol
from uuid import uuid4

from fastapi import status

from backend.app.core.config import settings
from backend.app.core.errors import AppError
from backend.app.core.security import (
    create_jwt,
    decode_jwt,
    hash_password,
    hash_secret,
    random_token,
    utc_now,
    verify_password,
)
from backend.app.models.user import User
from backend.app.models.user_session import UserSession
from backend.app.schemas.auth import LoginRequest, SignupRequest, TokenResponse


class UserRepositoryPort(Protocol):
    def create(self, user: User) -> User:
        pass

    def get(self, user_id: int) -> User | None:
        pass

    def get_by_email(self, email: str) -> User | None:
        pass


class SessionRepositoryPort(Protocol):
    def create(self, session: UserSession) -> UserSession:
        pass

    def get(self, session_id: str) -> UserSession | None:
        pass

    def revoke(self, session: UserSession, revoked_at) -> None:
        pass

    def rotate_refresh_token(
        self,
        session: UserSession,
        *,
        refresh_token_hash: str,
        csrf_token: str,
        expires_at,
    ) -> UserSession:
        pass


class UnitOfWork(Protocol):
    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass


@dataclass(frozen=True)
class AuthContext:
    user: User
    session_id: str
    token_payload: dict


class AuthService:
    def __init__(
        self,
        users: UserRepositoryPort,
        sessions: SessionRepositoryPort,
        unit_of_work: UnitOfWork,
    ) -> None:
        self.users = users
        self.sessions = sessions
        self.unit_of_work = unit_of_work

    def signup(self, payload: SignupRequest) -> TokenResponse:
        email = payload.email.strip().lower()
        if self.users.get_by_email(email) is not None:
            raise AppError(
                code="EMAIL_ALREADY_REGISTERED",
                message="이미 가입된 이메일입니다.",
                status_code=status.HTTP_409_CONFLICT,
                details={"email": email},
            )

        user = User(
            email=email,
            password_hash=hash_password(payload.password),
            role="member",
        )

        try:
            self.users.create(user)
            session = self._create_session(user)
            self.sessions.create(session)
            tokens = self._issue_tokens(user=user, session=session)
            self.sessions.rotate_refresh_token(
                session,
                refresh_token_hash=hash_secret(tokens.refresh_token),
                csrf_token=tokens.csrf_token,
                expires_at=utc_now() + timedelta(seconds=settings.refresh_token_seconds),
            )
            self.unit_of_work.commit()
            return tokens
        except Exception:
            self.unit_of_work.rollback()
            raise

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.users.get_by_email(payload.email.strip().lower())
        if user is None or not verify_password(payload.password, user.password_hash):
            raise AppError(
                code="INVALID_CREDENTIALS",
                message="이메일 또는 비밀번호가 올바르지 않습니다.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        session = self._create_session(user)

        try:
            self.sessions.create(session)
            tokens = self._issue_tokens(user=user, session=session)
            self.sessions.rotate_refresh_token(
                session,
                refresh_token_hash=hash_secret(tokens.refresh_token),
                csrf_token=tokens.csrf_token,
                expires_at=utc_now() + timedelta(seconds=settings.refresh_token_seconds),
            )
            self.unit_of_work.commit()
            return tokens
        except Exception:
            self.unit_of_work.rollback()
            raise

    def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_jwt(refresh_token, expected_type="refresh")
        session = self._get_active_session(payload["sid"])

        if hash_secret(refresh_token) != session.refresh_token_hash:
            raise AppError(
                code="REFRESH_TOKEN_REUSED",
                message="저장된 refresh token과 일치하지 않습니다.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        user = self._get_user(int(payload["sub"]))

        try:
            tokens = self._issue_tokens(user=user, session=session)
            self.sessions.rotate_refresh_token(
                session,
                refresh_token_hash=hash_secret(tokens.refresh_token),
                csrf_token=tokens.csrf_token,
                expires_at=utc_now() + timedelta(seconds=settings.refresh_token_seconds),
            )
            self.unit_of_work.commit()
            return tokens
        except Exception:
            self.unit_of_work.rollback()
            raise

    def authenticate_access_token(self, access_token: str) -> AuthContext:
        payload = decode_jwt(access_token, expected_type="access")
        session = self._get_active_session(payload["sid"])
        user = self._get_user(int(payload["sub"]))

        if session.user_id != user.id:
            raise AppError(
                code="SESSION_USER_MISMATCH",
                message="토큰 사용자와 세션 사용자가 일치하지 않습니다.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        return AuthContext(user=user, session_id=session.id, token_payload=payload)

    def verify_csrf_token(self, session_id: str, csrf_token: str | None) -> None:
        session = self._get_active_session(session_id)
        if csrf_token is None or csrf_token != session.csrf_token:
            raise AppError(
                code="CSRF_TOKEN_INVALID",
                message="CSRF 토큰이 없거나 일치하지 않습니다.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

    def logout(self, session_id: str) -> None:
        session = self._get_active_session(session_id)
        try:
            self.sessions.revoke(session, utc_now())
            self.unit_of_work.commit()
        except Exception:
            self.unit_of_work.rollback()
            raise

    def _create_session(self, user: User) -> UserSession:
        return UserSession(
            id=str(uuid4()),
            user_id=user.id,
            refresh_token_hash="pending",
            csrf_token=random_token(),
            expires_at=utc_now() + timedelta(seconds=settings.refresh_token_seconds),
        )

    def _issue_tokens(self, *, user: User, session: UserSession) -> TokenResponse:
        refresh_jti = str(uuid4())
        csrf_token = random_token()
        access_token = create_jwt(
            subject=user.id,
            role=user.role,
            token_type="access",
            session_id=session.id,
            expires_delta=timedelta(seconds=settings.access_token_seconds),
        )
        refresh_token = create_jwt(
            subject=user.id,
            role=user.role,
            token_type="refresh",
            session_id=session.id,
            expires_delta=timedelta(seconds=settings.refresh_token_seconds),
            jwt_id=refresh_jti,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_seconds,
            refresh_expires_in=settings.refresh_token_seconds,
            session_id=session.id,
            csrf_token=csrf_token,
        )

    def _get_user(self, user_id: int) -> User:
        user = self.users.get(user_id)
        if user is None:
            raise AppError(
                code="USER_NOT_FOUND",
                message="사용자를 찾을 수 없습니다.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        return user

    def _get_active_session(self, session_id: str) -> UserSession:
        session = self.sessions.get(session_id)
        if session is None or session.revoked_at is not None or session.expires_at < utc_now():
            raise AppError(
                code="SESSION_INVALID",
                message="세션이 없거나 만료/폐기되었습니다.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        return session
