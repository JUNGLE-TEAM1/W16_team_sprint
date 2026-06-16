from pydantic import BaseModel, Field

from backend.app.schemas.tag import TagRead


class RagAssistRequest(BaseModel):
    title: str = Field(default="", max_length=120)
    content: str = Field(default="", max_length=5000)
    top_k: int = Field(default=5, ge=1, le=10)
    include_references: bool = False
    reference_urls: list[str] = Field(default_factory=list, max_length=5)


class RagMatch(BaseModel):
    post_id: int
    title: str
    excerpt: str
    score: float
    duplicate_risk: str
    summary: str
    tags: list[TagRead]


class RagReference(BaseModel):
    title: str
    url: str
    source: str
    excerpt: str


class RagAssistResponse(BaseModel):
    embedding_dimensions: int
    embedding_provider: str
    embedding_model: str
    llm_provider: str
    llm_model: str
    llm_used: bool
    stored_vectors: int
    duplicate_warning: bool
    recommendation: str
    matches: list[RagMatch]
    references: list[RagReference]
