from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.tag import Tag


class TagRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[Tag]:
        statement = select(Tag).order_by(Tag.name.asc())
        return list(self.db.scalars(statement))

    def get_by_name(self, name: str) -> Tag | None:
        statement = select(Tag).where(Tag.name == name)
        return self.db.scalars(statement).first()

    def get_or_create(self, name: str) -> Tag:
        tag = self.get_by_name(name)
        if tag is not None:
            return tag

        tag = Tag(name=name)
        self.db.add(tag)
        self.db.flush()
        self.db.refresh(tag)
        return tag

    def get_or_create_many(self, names: list[str]) -> list[Tag]:
        return [self.get_or_create(name) for name in names]
