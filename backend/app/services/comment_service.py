from fastapi import status
from sqlalchemy.orm import Session

from backend.app.core.errors import AppError
from backend.app.models.comment import Comment
from backend.app.repositories.comment_repository import CommentRepository
from backend.app.repositories.post_repository import PostRepository
from backend.app.schemas.comment import CommentCreate


class CommentService:
    def __init__(
        self,
        db: Session,
        comments: CommentRepository,
        posts: PostRepository,
    ) -> None:
        self.db = db
        self.comments = comments
        self.posts = posts

    def create(self, post_id: int, payload: CommentCreate, author_id: int) -> Comment:
        self._get_post_or_raise(post_id)
        comment = Comment(
            post_id=post_id,
            author_id=author_id,
            content=payload.content,
        )
        saved_comment = self.comments.create(comment)
        self.db.commit()
        return saved_comment

    def list_by_post(self, post_id: int) -> list[Comment]:
        self._get_post_or_raise(post_id)
        return self.comments.list_by_post(post_id)

    def delete(self, comment_id: int, author_id: int) -> None:
        comment = self.comments.get(comment_id)
        if comment is None:
            raise AppError(
                code="COMMENT_NOT_FOUND",
                message="댓글을 찾을 수 없습니다.",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"comment_id": comment_id},
            )
        if comment.author_id != author_id:
            raise AppError(
                code="COMMENT_FORBIDDEN",
                message="댓글 작성자만 삭제할 수 있습니다.",
                status_code=status.HTTP_403_FORBIDDEN,
                details={"comment_id": comment_id},
            )

        self.comments.delete(comment)
        self.db.commit()

    def _get_post_or_raise(self, post_id: int) -> None:
        if self.posts.get(post_id) is None:
            raise AppError(
                code="POST_NOT_FOUND",
                message="게시글을 찾을 수 없습니다.",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"post_id": post_id},
            )
