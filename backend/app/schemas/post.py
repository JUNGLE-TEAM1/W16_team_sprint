from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


MAX_TAGS_PER_POST = 5
MAX_TAG_LENGTH = 30


class PostSearchType(str, Enum):
    title = "title"
    content = "content"
    title_content = "title_content"
    author = "author"


def normalize_tag_names(tags: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        name = tag.strip().lower()
        if not name:
            continue
        if len(name) > MAX_TAG_LENGTH:
            raise ValueError(f"tag must be {MAX_TAG_LENGTH} characters or fewer")
        if name not in seen:
            normalized.append(name)
            seen.add(name)
    if len(normalized) > MAX_TAGS_PER_POST:
        raise ValueError(f"at most {MAX_TAGS_PER_POST} tags are allowed")
    return normalized


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=10000)
    tags: list[str] = Field(default_factory=list)

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        return normalize_tag_names(tags)


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    content: str | None = Field(default=None, min_length=1, max_length=10000)
    tags: list[str] | None = None

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str] | None) -> list[str] | None:
        if tags is None:
            return None
        return normalize_tag_names(tags)


class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    author_id: int
    author_display_name: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class PostPage(BaseModel):
    items: list[PostRead]
    page: int
    size: int
    total: int
    total_pages: int
