from pydantic import BaseModel, Field

from backend.app.core.config import settings


class SimilarPostsRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    limit: int = Field(default=settings.rag_default_limit, ge=1, le=settings.rag_max_limit)


class SimilarPostItem(BaseModel):
    post_id: int
    title: str
    preview: str
    similarity: float
    similarity_level: str
    tags: list[str]


class SimilarPostsResponse(BaseModel):
    summary: str
    summary_error: str | None = None
    items: list[SimilarPostItem]
    message: str
