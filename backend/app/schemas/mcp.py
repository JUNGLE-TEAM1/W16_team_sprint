from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from backend.app.schemas.post import normalize_tag_names

MIN_EXTERNAL_REFERENCE_QUERY_LENGTH = 20
EXTERNAL_REFERENCE_LIMIT = 3


class JsonRpcRequest(BaseModel):
    jsonrpc: Literal["2.0"]
    id: str | int | None = None
    method: str
    params: dict[str, Any] | None = None


class ExternalReferenceSearchArguments(BaseModel):
    title: str = Field(default="", max_length=120)
    content: str = Field(default="", max_length=10000)
    tags: list[str] = Field(default_factory=list)
    limit: int = Field(default=EXTERNAL_REFERENCE_LIMIT, ge=1, le=5)

    @field_validator("title", "content")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        return normalize_tag_names(tags)

    @model_validator(mode="after")
    def validate_query_length(self) -> "ExternalReferenceSearchArguments":
        query_length = len(f"{self.title}{self.content}".strip())
        if query_length < MIN_EXTERNAL_REFERENCE_QUERY_LENGTH:
            raise ValueError(
                f"title and content must contain at least {MIN_EXTERNAL_REFERENCE_QUERY_LENGTH} characters"
            )
        return self


class ExternalReferenceItem(BaseModel):
    title: str
    url: str
    source: str
    summary: str
    tags: list[str] = Field(default_factory=list)
    score: int | None = None
    answer_count: int | None = None
    is_answered: bool | None = None


class ExternalReferenceSearchResult(BaseModel):
    items: list[ExternalReferenceItem]
