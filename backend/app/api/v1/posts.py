from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.post import PostCreate, PostRead
from backend.app.services.post_service import PostService

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(payload: PostCreate, db: Session = Depends(get_db)) -> PostRead:
    return PostService(db).create(payload)


@router.post("/protected", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_protected_post(
    payload: PostCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PostRead:
    secured_payload = payload.model_copy(update={"author_name": user.email})
    return PostService(db).create(secured_payload)


@router.get("", response_model=list[PostRead])
def list_posts(db: Session = Depends(get_db)) -> list[PostRead]:
    return PostService(db).list()


@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: int, db: Session = Depends(get_db)) -> PostRead:
    return PostService(db).get(post_id)
