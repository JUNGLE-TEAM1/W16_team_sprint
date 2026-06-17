from datetime import datetime
from enum import Enum

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


class PetCareAdviceRequest(BaseModel):
    title: str = Field(default="", max_length=120)
    content: str = Field(default="", max_length=10000)
    tags: list[str] = Field(default_factory=list)
    life_cycle: str | None = Field(default=None, max_length=80)
    department: str | None = Field(default=None, max_length=80)
    location_region: str | None = Field(default=None, max_length=80)

    @field_validator("title", "content")
    @classmethod
    def strip_pet_care_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("tags")
    @classmethod
    def normalize_pet_care_tags(cls, tags: list[str]) -> list[str]:
        return normalize_tag_names(tags)

    @field_validator("life_cycle", "department", "location_region")
    @classmethod
    def strip_pet_care_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @model_validator(mode="after")
    def validate_pet_care_query_length(self) -> "PetCareAdviceRequest":
        query_length = len(f"{self.title}{self.content}".strip())
        if query_length < MIN_RAG_QUERY_LENGTH:
            raise ValueError(
                f"title and content must contain at least {MIN_RAG_QUERY_LENGTH} characters"
            )
        return self


class PetCareSourceChunk(BaseModel):
    chunk_id: int
    document_id: int
    title: str
    content_preview: str
    question: str | None = None
    answer_preview: str | None = None
    department: str | None = None
    disease: str | None = None
    life_cycle: str | None = None
    source_kind: str
    split: str
    similarity: float


class PetCareHospitalCandidate(BaseModel):
    name: str
    address: str | None = None
    road_address: str | None = None
    phone: str | None = None
    distance_meters: int | None = None
    place_url: str | None = None
    source: str = "kakao_local"


class PetCareAdviceStatus(str, Enum):
    completed = "completed"
    stale = "stale"


class PetCareAdviceResponse(BaseModel):
    id: int | None = None
    post_id: int | None = None
    status: PetCareAdviceStatus = PetCareAdviceStatus.completed
    generated_at: datetime | None = None
    answer: str
    action_plan: list[str]
    safety_note: str
    sources: list[PetCareSourceChunk]
    hospital_candidates: list[PetCareHospitalCandidate] = Field(default_factory=list)
