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


class PostSortType(str, Enum):
    latest = "latest"
    comment_count = "comment_count"
    like_count = "like_count"


class PostType(str, Enum):
    policy = "policy"
    facility = "facility"
    case = "case"


class PostVisibility(str, Enum):
    public = "public"
    private = "private"


class PostCommentPolicy(str, Enum):
    none = "none"
    public = "public"
    private = "private"


class PostRagScope(str, Enum):
    public = "public"
    excluded = "excluded"


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
    post_type: PostType = PostType.case
    region: str | None = Field(default=None, max_length=80)
    source_name: str | None = Field(default=None, max_length=120)
    source_url: str | None = Field(default=None, max_length=500)
    source_external_id: str | None = Field(default=None, max_length=120)

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        return normalize_tag_names(tags)

    @field_validator("region", "source_name", "source_url", "source_external_id")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    content: str | None = Field(default=None, min_length=1, max_length=10000)
    tags: list[str] | None = None
    post_type: PostType | None = None
    visibility: PostVisibility | None = None
    comment_policy: PostCommentPolicy | None = None
    rag_scope: PostRagScope | None = None
    region: str | None = Field(default=None, max_length=80)
    source_name: str | None = Field(default=None, max_length=120)
    source_url: str | None = Field(default=None, max_length=500)
    source_external_id: str | None = Field(default=None, max_length=120)

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str] | None) -> list[str] | None:
        if tags is None:
            return None
        return normalize_tag_names(tags)

    @field_validator("region", "source_name", "source_url", "source_external_id")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    author_id: int
    author_display_name: str
    post_type: PostType
    visibility: PostVisibility
    comment_policy: PostCommentPolicy
    rag_scope: PostRagScope
    region: str | None
    source_name: str | None
    source_url: str | None
    source_external_id: str | None
    comment_count: int
    like_count: int
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class PostPage(BaseModel):
    items: list[PostRead]
    page: int
    size: int
    total: int
    total_pages: int
