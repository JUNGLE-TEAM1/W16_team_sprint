from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import require_admin
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.auth import UserRead

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserRead])
def list_users(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> list[User]:
    return UserRepository(db).list()
