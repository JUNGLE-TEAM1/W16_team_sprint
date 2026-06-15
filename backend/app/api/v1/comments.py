from fastapi import APIRouter, Depends, status

from backend.app.api.dependencies import get_comment_service
from backend.app.api.v1.auth import get_session_user
from backend.app.models.user import User
from backend.app.schemas.comment import CommentCreate, CommentRead
from backend.app.services.comment_service import CommentService

router = APIRouter(tags=["comments"])


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    post_id: int,
    payload: CommentCreate,
    current_user: User = Depends(get_session_user),
    service: CommentService = Depends(get_comment_service),
) -> CommentRead:
    return service.create(post_id=post_id, payload=payload, author_id=current_user.id)


@router.get("/posts/{post_id}/comments", response_model=list[CommentRead])
def list_comments(
    post_id: int,
    service: CommentService = Depends(get_comment_service),
) -> list[CommentRead]:
    return service.list_by_post(post_id)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_session_user),
    service: CommentService = Depends(get_comment_service),
) -> None:
    service.delete(comment_id=comment_id, author_id=current_user.id)
