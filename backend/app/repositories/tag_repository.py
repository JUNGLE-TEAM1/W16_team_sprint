from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.tag import Tag


class TagRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, tag: Tag) -> Tag:
        self.db.add(tag)
        self.db.flush()
        self.db.refresh(tag)
        return tag

    def list(self) -> list[Tag]:
        statement = select(Tag).order_by(Tag.name.asc())
        return list(self.db.scalars(statement))

    def get_by_name(self, name: str) -> Tag | None:
        statement = select(Tag).where(Tag.name == name)
        return self.db.scalars(statement).first()

    def get_or_create_many(self, names: list[str]) -> list[Tag]:
        tags: list[Tag] = []
        for name in names:
            existing_tag = self.get_by_name(name)
            if existing_tag is not None:
                tags.append(existing_tag)
                continue

            tags.append(self.create(Tag(name=name)))
        return tags
