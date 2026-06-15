from fastapi import APIRouter, Depends, Query, status

from backend.app.api.dependencies import get_post_service
from backend.app.api.v1.auth import get_session_user
from backend.app.models.user import User
from backend.app.schemas.post import PostCreate, PostPage, PostRead, PostSearchType, PostSortType, PostUpdate
from backend.app.services.post_service import PostService

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    current_user: User = Depends(get_session_user),
    service: PostService = Depends(get_post_service),
) -> PostRead:
    return service.create(payload, author_id=current_user.id)


@router.get("", response_model=PostPage)
def list_posts(
    q: str | None = Query(default=None),
    search_type: PostSearchType = Query(default=PostSearchType.title_content),
    tag: str | None = Query(default=None),
    sort: PostSortType = Query(default=PostSortType.latest),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=9, ge=1, le=50),
    service: PostService = Depends(get_post_service),
) -> PostPage:
    return service.list(q=q, search_type=search_type, tag=tag, sort=sort, page=page, size=size)


@router.get("/{post_id}", response_model=PostRead)
def get_post(
    post_id: int,
    service: PostService = Depends(get_post_service),
) -> PostRead:
    return service.get(post_id)


@router.patch("/{post_id}", response_model=PostRead)
def update_post(
    post_id: int,
    payload: PostUpdate,
    current_user: User = Depends(get_session_user),
    service: PostService = Depends(get_post_service),
) -> PostRead:
    return service.update(post_id=post_id, payload=payload, author_id=current_user.id)


@router.post("/{post_id}/like", response_model=PostRead)
def like_post(
    post_id: int,
    _current_user: User = Depends(get_session_user),
    service: PostService = Depends(get_post_service),
) -> PostRead:
    return service.like(post_id=post_id)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    current_user: User = Depends(get_session_user),
    service: PostService = Depends(get_post_service),
) -> None:
    service.delete(post_id=post_id, author_id=current_user.id)
