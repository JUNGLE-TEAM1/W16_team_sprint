from pydantic import BaseModel, Field, field_validator, model_validator

from backend.app.schemas.post import PostType, normalize_tag_names

MIN_RAG_QUERY_LENGTH = 20
RELATED_POST_LIMIT = 3
RELATED_POST_MIN_SIMILARITY = 0.5


class RelatedPostsRequest(BaseModel):
    title: str = Field(default="", max_length=120)
    content: str = Field(default="", max_length=10000)
    tags: list[str] = Field(default_factory=list)
    post_type: PostType = PostType.case
    region: str | None = Field(default=None, max_length=80)
    exclude_post_id: int | None = Field(default=None, ge=1)

    @field_validator("title", "content")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        return normalize_tag_names(tags)

    @field_validator("region")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @model_validator(mode="after")
    def validate_query_length(self) -> "RelatedPostsRequest":
        query_length = len(f"{self.title}{self.content}".strip())
        if query_length < MIN_RAG_QUERY_LENGTH:
            raise ValueError(
                f"title and content must contain at least {MIN_RAG_QUERY_LENGTH} characters"
            )
        return self


class RelatedPostItem(BaseModel):
    post_id: int
    title: str
    content_preview: str
    tags: list[str]
    similarity: float
    summary: str | None = None


class RelatedPostsResponse(BaseModel):
    items: list[RelatedPostItem]
