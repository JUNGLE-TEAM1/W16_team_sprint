from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

DEFAULT_HOSPITAL_SEARCH_RADIUS_METERS = 5000
MAX_HOSPITAL_SEARCH_RADIUS_METERS = 20000
DEFAULT_HOSPITAL_SEARCH_LIMIT = 5


class JsonRpcRequest(BaseModel):
    jsonrpc: Literal["2.0"]
    id: str | int | None = None
    method: str
    params: dict[str, Any] | None = None


class GeocodeRegionArguments(BaseModel):
    region_text: str = Field(min_length=2, max_length=120)

    @field_validator("region_text")
    @classmethod
    def strip_region_text(cls, value: str) -> str:
        stripped = value.strip()
        if len(stripped) < 2:
            raise ValueError("region_text must contain at least 2 characters")
        return stripped


class FindNearbyAnimalHospitalsArguments(BaseModel):
    region_text: str | None = Field(default=None, max_length=120)
    x: float | None = None
    y: float | None = None
    radius_meters: int = Field(
        default=DEFAULT_HOSPITAL_SEARCH_RADIUS_METERS,
        ge=100,
        le=MAX_HOSPITAL_SEARCH_RADIUS_METERS,
    )
    limit: int = Field(default=DEFAULT_HOSPITAL_SEARCH_LIMIT, ge=1, le=10)

    @field_validator("region_text")
    @classmethod
    def strip_optional_region_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @model_validator(mode="after")
    def require_region_or_coordinates(self) -> "FindNearbyAnimalHospitalsArguments":
        if self.region_text:
            return self
        if self.x is not None and self.y is not None:
            return self
        raise ValueError("region_text or both x and y are required")


class RegionLocation(BaseModel):
    region_text: str
    normalized_address: str
    x: float
    y: float
    region_1depth_name: str | None = None
    region_2depth_name: str | None = None
    region_3depth_name: str | None = None


class AnimalHospitalItem(BaseModel):
    name: str
    address: str | None = None
    road_address: str | None = None
    phone: str | None = None
    distance_meters: int | None = None
    place_url: str | None = None
    x: float | None = None
    y: float | None = None
    source: Literal["kakao_local"] = "kakao_local"


class GeocodeRegionResult(BaseModel):
    location: RegionLocation


class AnimalHospitalSearchResult(BaseModel):
    location: RegionLocation | None = None
    items: list[AnimalHospitalItem]
