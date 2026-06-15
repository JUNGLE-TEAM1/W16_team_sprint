from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)
    author_name: str = Field(default="anonymous", min_length=1, max_length=40)


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    user_id: int | None = None
    content: str
    author_name: str
    created_at: datetime
