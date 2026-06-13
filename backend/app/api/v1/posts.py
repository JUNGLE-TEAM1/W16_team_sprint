from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.repositories.post_repository import PostRepository
from backend.app.schemas.post import PostCreate, PostRead
from backend.app.services.post_service import PostService

router = APIRouter(prefix="/posts", tags=["posts"])


def get_post_service(db: Session = Depends(get_db)) -> PostService:
    posts = PostRepository(db)
    return PostService(db=db, posts=posts)


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    service: PostService = Depends(get_post_service),
) -> PostRead:
    return service.create(payload)


@router.get("", response_model=list[PostRead])
def list_posts(service: PostService = Depends(get_post_service)) -> list[PostRead]:
    return service.list()


@router.get("/{post_id}", response_model=PostRead)
def get_post(
    post_id: int,
    service: PostService = Depends(get_post_service),
) -> PostRead:
    return service.get(post_id)
