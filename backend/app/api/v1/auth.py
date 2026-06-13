from fastapi import APIRouter, Cookie, Depends, Header, Response, status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.repositories.auth_repository import AuthRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.auth import (
    AccessTokenResponse,
    AuthUserResponse,
    LoginRequest,
    RefreshTokenRequest,
    TokenPairResponse,
    UserCreate,
    UserRead,
)
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    users = UserRepository(db)
    auth = AuthRepository(db)
    return AuthService(db=db, users=users, auth=auth)


def get_bearer_token(authorization: str | None = Header(default=None)) -> str | None:
    if authorization is None:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


def get_session_user(
    session_token: str | None = Cookie(default=None, alias=settings.session_cookie_name),
    service: AuthService = Depends(get_auth_service),
) -> User:
    return service.get_user_by_session_token(session_token)


def get_access_token_user(
    access_token: str | None = Depends(get_bearer_token),
    service: AuthService = Depends(get_auth_service),
) -> User:
    return service.get_user_by_access_token(access_token)


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
    response.delete_cookie(settings.session_cookie_name)
    return response


@router.post("/jwt/login", response_model=AccessTokenResponse)
def jwt_login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> AccessTokenResponse:
    user, access_token = service.login_with_access_token(payload)
    return AccessTokenResponse(access_token=access_token, user=user)


@router.get("/jwt/me", response_model=UserRead)
def jwt_me(current_user: User = Depends(get_access_token_user)) -> User:
    return current_user


@router.post("/token-pair/login", response_model=TokenPairResponse)
def token_pair_login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenPairResponse:
    token_pair = service.login_with_token_pair(payload)
    return TokenPairResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        user=token_pair.user,
    )


@router.post("/token-pair/refresh", response_model=TokenPairResponse)
def refresh_token_pair(
    payload: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenPairResponse:
    token_pair = service.refresh_token_pair(payload.refresh_token)
    return TokenPairResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        user=token_pair.user,
    )


@router.get("/token-pair/me", response_model=UserRead)
def token_pair_me(current_user: User = Depends(get_access_token_user)) -> User:
    return current_user


@router.post("/token-pair/logout", status_code=status.HTTP_204_NO_CONTENT)
def token_pair_logout(
    payload: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> None:
    service.revoke_refresh_token(payload.refresh_token)
