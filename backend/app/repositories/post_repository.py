from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.post import Post


class PostRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, post: Post) -> Post:
        self.db.add(post)
        self.db.flush()
        self.db.refresh(post)
        return post

    def list(self) -> list[Post]:
        statement = select(Post).order_by(Post.created_at.desc())
        return list(self.db.scalars(statement))

    def get(self, post_id: int) -> Post | None:
        return self.db.get(Post, post_id)
