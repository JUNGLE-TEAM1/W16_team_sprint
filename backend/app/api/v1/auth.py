from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import LoginRequest, RefreshRequest, TokenPair, UserCreate, UserRead
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    return AuthService(db).register(payload)


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> TokenPair:
    _, tokens = AuthService(db).login(payload)
    response.set_cookie("session_id", tokens.session_id, httponly=True, samesite="lax")
    response.set_cookie("csrf_token", tokens.csrf_token, httponly=False, samesite="lax")
    return tokens


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, response: Response, db: Session = Depends(get_db)) -> TokenPair:
    tokens = AuthService(db).refresh(payload.refresh_token)
    response.set_cookie("session_id", tokens.session_id, httponly=True, samesite="lax")
    response.set_cookie("csrf_token", tokens.csrf_token, httponly=False, samesite="lax")
    return tokens


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)) -> User:
    return user
