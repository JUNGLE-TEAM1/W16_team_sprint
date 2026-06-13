from fastapi import status
from sqlalchemy.orm import Session

from backend.app.core.errors import AppError
from backend.app.models.post import Post
from backend.app.repositories.post_repository import PostRepository
from backend.app.schemas.post import PostCreate


class PostService:
    def __init__(self, db: Session, posts: PostRepository) -> None:
        self.db = db
        self.posts = posts

    def create(self, payload: PostCreate) -> Post:
        post = Post(**payload.model_dump())
        saved_post = self.posts.create(post)
        self.db.commit()
        return saved_post

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
