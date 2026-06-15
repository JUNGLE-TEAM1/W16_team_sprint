from __future__ import annotations

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
        tag: str | None = None,
        q: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[Post], int]:
        conditions = []
        normalized_tag = tag.strip().lower() if tag else None
        normalized_q = q.strip().lower() if q else None

        statement = select(Post).options(selectinload(Post.tags))
        count_statement = select(func.count(func.distinct(Post.id))).select_from(Post)

        if normalized_tag:
            statement = statement.join(Post.tags)
            count_statement = count_statement.join(Post.tags)
            conditions.append(func.lower(Tag.name) == normalized_tag)

        if normalized_q:
            pattern = f"%{normalized_q}%"
            conditions.append(
                or_(
                    func.lower(Post.title).like(pattern),
                    func.lower(Post.content).like(pattern),
                )
            )

        if conditions:
            statement = statement.where(*conditions)
            count_statement = count_statement.where(*conditions)

        offset = (page - 1) * size
        statement = statement.distinct().order_by(Post.created_at.desc()).offset(offset).limit(size)
        total = self.db.scalar(count_statement) or 0
        return list(self.db.scalars(statement)), total

    def get(self, post_id: int) -> Post | None:
        statement = select(Post).options(selectinload(Post.tags)).where(Post.id == post_id)
        return self.db.scalar(statement)

    def delete(self, post: Post) -> None:
        self.db.delete(post)

    def resolve_tags(self, names: list[str]) -> list[Tag]:
        if not names:
            return []

        existing_tags = self.db.scalars(select(Tag).where(Tag.name.in_(names))).all()
        tags_by_name = {tag.name: tag for tag in existing_tags}

        for name in names:
            if name not in tags_by_name:
                tag = Tag(name=name)
                self.db.add(tag)
                tags_by_name[name] = tag

        return [tags_by_name[name] for name in names]
