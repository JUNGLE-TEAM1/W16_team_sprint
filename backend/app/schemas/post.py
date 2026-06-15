from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.tag import TagRead


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1)
    tag_names: list[str] = Field(default_factory=list, max_length=8)


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    content: str | None = Field(default=None, min_length=1)
    tag_names: list[str] | None = Field(default=None, max_length=8)


class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None = None
    title: str
    content: str
    author_name: str
    created_at: datetime
    updated_at: datetime
    tags: list[TagRead] = Field(default_factory=list)


class PostListResponse(BaseModel):
    items: list[PostRead]
    page: int
    size: int
    total: int
    pages: int
