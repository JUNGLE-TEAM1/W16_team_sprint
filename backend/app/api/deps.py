from fastapi import Depends, Header, Request, status
from sqlalchemy.orm import Session

from backend.app.core.errors import AppError
from backend.app.core.security import decode_access_token
from backend.app.core.time import utc_now
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.repositories.user_repository import SessionRepository, UserRepository


def get_current_user(
    request: Request,
    authorization: str | None = Header(default=None),
    x_csrf_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    users = UserRepository(db)
    if authorization and authorization.lower().startswith("bearer "):
        payload = decode_access_token(authorization.split(" ", 1)[1])
        if payload is None:
            raise AppError("AUTHENTICATION_FAILED", "Access token is invalid or expired", status.HTTP_401_UNAUTHORIZED)
        user = users.get(int(payload["sub"]))
        if user is None:
            raise AppError("AUTHENTICATION_FAILED", "User does not exist", status.HTTP_401_UNAUTHORIZED)
        return user

    session_id = request.cookies.get("session_id")
    if not session_id:
        raise AppError("AUTHENTICATION_REQUIRED", "Login is required", status.HTTP_401_UNAUTHORIZED)
    session = SessionRepository(db).get_active_session(session_id, utc_now())
    if session is None:
        raise AppError("AUTHENTICATION_FAILED", "Session is invalid or expired", status.HTTP_401_UNAUTHORIZED)
    if request.method in {"POST", "PUT", "PATCH", "DELETE"} and x_csrf_token != session.csrf_token:
        raise AppError("CSRF_FAILED", "CSRF token is missing or invalid", status.HTTP_403_FORBIDDEN)
    user = users.get(session.user_id)
    if user is None:
        raise AppError("AUTHENTICATION_FAILED", "User does not exist", status.HTTP_401_UNAUTHORIZED)
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise AppError("FORBIDDEN", "Admin permission is required", status.HTTP_403_FORBIDDEN)
    return user
