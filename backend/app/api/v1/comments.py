from fastapi import APIRouter, Response, status

from backend.app.api.auth_dependencies import CurrentAuthContext
from backend.app.api.dependencies import CommentServiceDependency
from backend.app.schemas.comment import CommentCreate, CommentRead

router = APIRouter(tags=["comments"])


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    post_id: int,
    payload: CommentCreate,
    context: CurrentAuthContext,
    service: CommentServiceDependency,
) -> CommentRead:
    return service.create(post_id, payload, context.user)


@router.get("/posts/{post_id}/comments", response_model=list[CommentRead])
def list_comments(post_id: int, service: CommentServiceDependency) -> list[CommentRead]:
    return service.list_by_post(post_id)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    context: CurrentAuthContext,
    service: CommentServiceDependency,
) -> Response:
    service.delete(comment_id, context.user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
