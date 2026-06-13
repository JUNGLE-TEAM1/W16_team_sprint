from typing import Annotated, Callable

from fastapi import Depends, Header, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.core.errors import AppError
from backend.app.db.session import get_db
from backend.app.repositories.session_repository import SessionRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.services.auth_service import AuthContext, AuthService

bearer_scheme = HTTPBearer(auto_error=False)


def get_user_repository(db: Annotated[Session, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


def get_session_repository(db: Annotated[Session, Depends(get_db)]) -> SessionRepository:
    return SessionRepository(db)


def get_auth_service(
    users: Annotated[UserRepository, Depends(get_user_repository)],
    sessions: Annotated[SessionRepository, Depends(get_session_repository)],
    unit_of_work: Annotated[Session, Depends(get_db)],
) -> AuthService:
    return AuthService(users=users, sessions=sessions, unit_of_work=unit_of_work)


AuthServiceDependency = Annotated[AuthService, Depends(get_auth_service)]


def get_current_auth_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    service: AuthServiceDependency,
) -> AuthContext:
    if credentials is None:
        raise AppError(
            code="AUTH_REQUIRED",
            message="Authorization Bearer 토큰이 필요합니다.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return service.authenticate_access_token(credentials.credentials)


CurrentAuthContext = Annotated[AuthContext, Depends(get_current_auth_context)]


def require_csrf_token(
    context: CurrentAuthContext,
    service: AuthServiceDependency,
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> AuthContext:
    service.verify_csrf_token(context.session_id, x_csrf_token)
    return context


CsrfProtectedContext = Annotated[AuthContext, Depends(require_csrf_token)]


def require_role(role: str) -> Callable[[CurrentAuthContext], AuthContext]:
    def dependency(context: CurrentAuthContext) -> AuthContext:
        if context.user.role != role:
            raise AppError(
                code="FORBIDDEN",
                message="요청한 리소스에 접근할 권한이 없습니다.",
                status_code=status.HTTP_403_FORBIDDEN,
                details={"required_role": role, "current_role": context.user.role},
            )
        return context

    return dependency
