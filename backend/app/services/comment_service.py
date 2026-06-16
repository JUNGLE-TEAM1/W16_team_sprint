from typing import Protocol

from fastapi import status

from backend.app.core.errors import AppError
from backend.app.models.comment import Comment
from backend.app.models.post import Post
from backend.app.models.user import User
from backend.app.schemas.comment import CommentCreate


class CommentRepositoryPort(Protocol):
    def create(self, comment: Comment) -> Comment:
        pass

    def list_by_post(self, post_id: int) -> list[Comment]:
        pass

    def get(self, comment_id: int) -> Comment | None:
        pass

    def delete(self, comment: Comment) -> None:
        pass


class PostLookupPort(Protocol):
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
        posts: PostLookupPort,
        unit_of_work: UnitOfWork,
    ) -> None:
        self.comments = comments
        self.posts = posts
        self.unit_of_work = unit_of_work

    def create(self, post_id: int, payload: CommentCreate, user: User) -> Comment:
        self._ensure_post_exists(post_id)
        comment = Comment(
            post_id=post_id,
            user_id=user.id,
            content=payload.content,
            author_name=user.email,
        )
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

    def delete(self, comment_id: int, user: User) -> None:
        comment = self.comments.get(comment_id)
        if comment is None:
            raise AppError(
                code="COMMENT_NOT_FOUND",
                message="상담 메모를 찾을 수 없습니다.",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"comment_id": comment_id},
            )
        if user.role != "admin" and comment.user_id != user.id:
            raise AppError(
                code="FORBIDDEN",
                message="상담 메모를 삭제할 권한이 없습니다.",
                status_code=status.HTTP_403_FORBIDDEN,
                details={"comment_id": comment_id},
            )

        try:
            self.comments.delete(comment)
            self.unit_of_work.commit()
        except Exception:
            self.unit_of_work.rollback()
            raise

    def _ensure_post_exists(self, post_id: int) -> None:
        if self.posts.get(post_id) is None:
            raise AppError(
                code="POST_NOT_FOUND",
                message="지원 카드나 상담 케이스를 찾을 수 없습니다.",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"post_id": post_id},
            )
