from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.post import Post
from backend.app.models.tag import Tag


class PostRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, post: Post) -> Post:
        self.db.add(post)
        self.db.flush()
        self.db.refresh(post)
        return post

    def list(
        self,
        *,
        page: int,
        size: int,
        query: str | None = None,
        tag: str | None = None,
    ) -> tuple[list[Post], int]:
        filters = []
        if query:
            pattern = f"%{query}%"
            filters.append(or_(Post.title.ilike(pattern), Post.content.ilike(pattern)))

        statement = select(Post).options(selectinload(Post.tags))
        count_statement = select(func.count(Post.id))

        if tag:
            normalized_tag = tag.strip().lower()
            statement = statement.join(Post.tags).where(Tag.name == normalized_tag)
            count_statement = count_statement.join(Post.tags).where(Tag.name == normalized_tag)

        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)

        total = self.db.scalar(count_statement) or 0
        items = self.db.scalars(
            statement.order_by(Post.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        ).all()
        return list(items), total

    def get(self, post_id: int) -> Post | None:
        statement = (
            select(Post)
            .options(selectinload(Post.tags))
            .where(Post.id == post_id)
        )
        return self.db.scalars(statement).first()

    def delete(self, post: Post) -> None:
        self.db.delete(post)
        self.db.flush()
