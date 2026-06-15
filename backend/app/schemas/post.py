from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)


class PostUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)


class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    created_at: datetime
    tags: list[str] = Field(default_factory=list)

    @field_validator("tags", mode="before")
    @classmethod
    def tag_models_to_names(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [item if isinstance(item, str) else item.name for item in value]
        return value


class PostListResponse(BaseModel):
    items: list[PostRead]
    total: int
    page: int
    size: int
    pages: int
