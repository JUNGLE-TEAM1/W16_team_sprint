from datetime import datetime
from typing import Protocol

from fastapi import status

from backend.app.core.errors import AppError
from backend.app.models.comment import Comment
from backend.app.models.post import Post
from backend.app.schemas.comment import CommentCreate, CommentUpdate


class CommentRepositoryPort(Protocol):
    def create(self, comment: Comment) -> Comment:
        pass

    def list_by_post(self, post_id: int) -> list[Comment]:
        pass

    def get_for_post(self, post_id: int, comment_id: int) -> Comment | None:
        pass

    def delete(self, comment: Comment) -> None:
        pass


class PostReaderPort(Protocol):
    def get(self, post_id: int) -> Post | None:
        pass


class UnitOfWork(Protocol):
    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass


class CommentService:
    def __init__(
        self,
        comments: CommentRepositoryPort,
        posts: PostReaderPort,
        unit_of_work: UnitOfWork,
    ) -> None:
        self.comments = comments
        self.posts = posts
        self.unit_of_work = unit_of_work

    def create(self, post_id: int, payload: CommentCreate, user_id: int) -> Comment:
        self._ensure_post_exists(post_id)
        comment = Comment(**payload.model_dump(), post_id=post_id, user_id=user_id)
        try:
            saved_comment = self.comments.create(comment)
            self.unit_of_work.commit()
            return saved_comment
        except Exception:
            self.unit_of_work.rollback()
            raise

    def list_by_post(self, post_id: int) -> list[Comment]:
        self._ensure_post_exists(post_id)
        return self.comments.list_by_post(post_id)

    def update(
        self,
        post_id: int,
        comment_id: int,
        payload: CommentUpdate,
        user_id: int,
    ) -> Comment:
        comment = self.get_for_post(post_id, comment_id)
        self._ensure_owner(comment, user_id)
        comment.content = payload.content
        comment.updated_at = datetime.utcnow()
        try:
            self.unit_of_work.commit()
            return comment
        except Exception:
            self.unit_of_work.rollback()
            raise

    def delete(self, post_id: int, comment_id: int, user_id: int) -> None:
        comment = self.get_for_post(post_id, comment_id)
        self._ensure_owner(comment, user_id)
        try:
            self.comments.delete(comment)
            self.unit_of_work.commit()
        except Exception:
            self.unit_of_work.rollback()
            raise

    def get_for_post(self, post_id: int, comment_id: int) -> Comment:
        self._ensure_post_exists(post_id)
        comment = self.comments.get_for_post(post_id, comment_id)
        if comment is None:
            raise AppError(
                code="COMMENT_NOT_FOUND",
                message="댓글을 찾을 수 없습니다.",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"post_id": post_id, "comment_id": comment_id},
            )
        return comment

    def _ensure_post_exists(self, post_id: int) -> None:
        if self.posts.get(post_id) is None:
            raise AppError(
                code="POST_NOT_FOUND",
                message="게시글을 찾을 수 없습니다.",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"post_id": post_id},
            )

    def _ensure_owner(self, comment: Comment, user_id: int) -> None:
        if comment.user_id != user_id:
            raise AppError(
                code="COMMENT_FORBIDDEN",
                message="댓글을 수정하거나 삭제할 권한이 없습니다.",
                status_code=status.HTTP_403_FORBIDDEN,
                details={"comment_id": comment.id},
            )
