from __future__ import annotations

from typing import Protocol

from backend.app.models.tag import Tag


class TagRepositoryPort(Protocol):
    def list(self) -> list[Tag]:
        pass


class TagService:
    def __init__(self, tags: TagRepositoryPort) -> None:
        self.tags = tags

    def list(self) -> list[Tag]:
        return self.tags.list()
