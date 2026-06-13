from typing import Protocol

from fastapi import status

from backend.app.core.errors import AppError
from backend.app.models.post import Post
from backend.app.schemas.post import PostCreate


class PostRepositoryPort(Protocol):
    def create(self, post: Post) -> Post:
        pass

    def list(self) -> list[Post]:
        pass

    def get(self, post_id: int) -> Post | None:
        pass


class UnitOfWork(Protocol):
    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass


class PostService:
    def __init__(self, posts: PostRepositoryPort, unit_of_work: UnitOfWork) -> None:
        self.posts = posts
        self.unit_of_work = unit_of_work

    def create(self, payload: PostCreate) -> Post:
        post = Post(**payload.model_dump())
        try:
            saved_post = self.posts.create(post)
            self.unit_of_work.commit()
            return saved_post
        except Exception:
            self.unit_of_work.rollback()
            raise

    def list(self) -> list[Post]:
        return self.posts.list()

    def get(self, post_id: int) -> Post:
        post = self.posts.get(post_id)
        if post is None:
            raise AppError(
                code="POST_NOT_FOUND",
                message="게시글을 찾을 수 없습니다.",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"post_id": post_id},
            )
        return post
