from fastapi import APIRouter, Query, Response, status

from backend.app.api.auth_dependencies import CurrentAuthContext
from backend.app.api.dependencies import PostServiceDependency
from backend.app.schemas.post import PostCreate, PostListResponse, PostRead, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    context: CurrentAuthContext,
    service: PostServiceDependency,
) -> PostRead:
    return service.create(payload, context.user)


@router.get("", response_model=PostListResponse)
def list_posts(
    service: PostServiceDependency,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=50),
    q: str | None = Query(default=None, min_length=1),
    tag: str | None = Query(default=None, min_length=1),
) -> PostListResponse:
    return service.list(page=page, size=size, query=q, tag=tag)


@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: int, service: PostServiceDependency) -> PostRead:
    return service.get(post_id)


@router.patch("/{post_id}", response_model=PostRead)
def update_post(
    post_id: int,
    payload: PostUpdate,
    context: CurrentAuthContext,
    service: PostServiceDependency,
) -> PostRead:
    return service.update(post_id, payload, context.user)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    context: CurrentAuthContext,
    service: PostServiceDependency,
) -> Response:
    service.delete(post_id, context.user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
