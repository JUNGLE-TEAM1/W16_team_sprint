from fastapi import APIRouter, status

from backend.app.api.dependencies import PostServiceDependency
from backend.app.schemas.post import PostCreate, PostRead

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(payload: PostCreate, service: PostServiceDependency) -> PostRead:
    return service.create(payload)


@router.get("", response_model=list[PostRead])
def list_posts(service: PostServiceDependency) -> list[PostRead]:
    return service.list()


@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: int, service: PostServiceDependency) -> PostRead:
    return service.get(post_id)
