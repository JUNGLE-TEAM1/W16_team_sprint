from fastapi import APIRouter, Cookie, Depends, Response, status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.repositories.auth_repository import AuthRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.auth import (
    AuthUserResponse,
    LoginRequest,
    UserCreate,
    UserRead,
)
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    users = UserRepository(db)
    auth = AuthRepository(db)
    return AuthService(db=db, users=users, auth=auth)


def get_session_user(
    session_token: str | None = Cookie(default=None, alias=settings.session_cookie_name),
    service: AuthService = Depends(get_auth_service),
) -> User:
    return service.get_user_by_session_token(session_token)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserCreate,
    service: AuthService = Depends(get_auth_service),
) -> User:
    return service.register(payload)


@router.post("/session/login", response_model=AuthUserResponse)
def session_login(
    payload: LoginRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> AuthUserResponse:
    login = service.login_with_session(payload)
    response.set_cookie(
        key=settings.session_cookie_name,
        value=login.session_token,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
        max_age=settings.session_expire_hours * 60 * 60,
    )
    return AuthUserResponse(user=login.user)


@router.get("/session/me", response_model=UserRead)
def session_me(current_user: User = Depends(get_session_user)) -> User:
    return current_user


@router.post("/session/logout", status_code=status.HTTP_204_NO_CONTENT)
def session_logout(
    response: Response,
    session_token: str | None = Cookie(default=None, alias=settings.session_cookie_name),
    service: AuthService = Depends(get_auth_service),
) -> Response:
    service.logout_session(session_token)
    response.status_code = status.HTTP_204_NO_CONTENT
    response.delete_cookie(settings.session_cookie_name, path="/")
    return response
