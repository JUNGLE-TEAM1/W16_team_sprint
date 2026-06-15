from fastapi import APIRouter, Query, status

from backend.app.api.auth_dependencies import CurrentAuthContext
from backend.app.api.dependencies import CommentServiceDependency, PostServiceDependency
from backend.app.schemas.comment import CommentCreate, CommentRead, CommentUpdate
from backend.app.schemas.post import PostCreate, PostListResponse, PostRead, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    context: CurrentAuthContext,
    service: PostServiceDependency,
) -> PostRead:
    return service.create(payload, user_id=context.user.id)


@router.get("", response_model=PostListResponse)
def list_posts(
    service: PostServiceDependency,
    tag: str | None = Query(default=None, min_length=1),
    q: str | None = Query(default=None, min_length=1),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=50),
) -> PostListResponse:
    return service.list(tag=tag, q=q, page=page, size=size)


@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: int, service: PostServiceDependency) -> PostRead:
    return service.get(post_id)


@router.put("/{post_id}", response_model=PostRead)
def update_post(
    post_id: int,
    payload: PostUpdate,
    context: CurrentAuthContext,
    service: PostServiceDependency,
) -> PostRead:
    return service.update(post_id, payload, user_id=context.user.id)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    context: CurrentAuthContext,
    service: PostServiceDependency,
) -> None:
    service.delete(post_id, user_id=context.user.id)


@router.post(
    "/{post_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    post_id: int,
    payload: CommentCreate,
    context: CurrentAuthContext,
    service: CommentServiceDependency,
) -> CommentRead:
    return service.create(post_id, payload, user_id=context.user.id)


@router.get("/{post_id}/comments", response_model=list[CommentRead])
def list_comments(post_id: int, service: CommentServiceDependency) -> list[CommentRead]:
    return service.list_by_post(post_id)


@router.put("/{post_id}/comments/{comment_id}", response_model=CommentRead)
def update_comment(
    post_id: int,
    comment_id: int,
    payload: CommentUpdate,
    context: CurrentAuthContext,
    service: CommentServiceDependency,
) -> CommentRead:
    return service.update(post_id, comment_id, payload, user_id=context.user.id)


@router.delete(
    "/{post_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    post_id: int,
    comment_id: int,
    context: CurrentAuthContext,
    service: CommentServiceDependency,
) -> None:
    service.delete(post_id, comment_id, user_id=context.user.id)
