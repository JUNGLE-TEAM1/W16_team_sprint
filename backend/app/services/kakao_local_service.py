from __future__ import annotations

from typing import Any, Protocol

import httpx

from backend.app.core.config import settings
from backend.app.schemas.mcp import (
    AnimalHospitalItem,
    AnimalHospitalSearchResult,
    FindNearbyAnimalHospitalsArguments,
    GeocodeRegionArguments,
    GeocodeRegionResult,
    RegionLocation,
)


class LocationSearchError(Exception):
    pass


class LocationSearchProvider(Protocol):
    def geocode_region(self, payload: GeocodeRegionArguments) -> GeocodeRegionResult:
        raise NotImplementedError

    def find_nearby_animal_hospitals(
        self,
        payload: FindNearbyAnimalHospitalsArguments,
    ) -> AnimalHospitalSearchResult:
        raise NotImplementedError


class KakaoLocalProvider:
    def __init__(
        self,
        api_key: str | None = settings.kakao_rest_api_key,
        api_base_url: str = settings.kakao_local_api_base_url,
        timeout_seconds: float = settings.kakao_local_timeout_seconds,
    ) -> None:
        self.api_key = api_key
        self.api_base_url = api_base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def geocode_region(self, payload: GeocodeRegionArguments) -> GeocodeRegionResult:
        documents = self._get_json(
            path="/v2/local/search/address.json",
            params={"query": payload.region_text, "size": 1},
        ).get("documents", [])
        if not documents:
            raise LocationSearchError("region geocode returned no result")

        document = documents[0]
        return GeocodeRegionResult(location=self._to_location(payload.region_text, document))

    def find_nearby_animal_hospitals(
        self,
        payload: FindNearbyAnimalHospitalsArguments,
    ) -> AnimalHospitalSearchResult:
        location: RegionLocation | None = None
        x = payload.x
        y = payload.y
        if payload.region_text:
            location = self.geocode_region(GeocodeRegionArguments(region_text=payload.region_text)).location
            x = location.x
            y = location.y

        if x is None or y is None:
            raise LocationSearchError("coordinates are required for hospital search")

        data = self._get_json(
            path="/v2/local/search/keyword.json",
            params={
                "query": "동물병원",
                "x": str(x),
                "y": str(y),
                "radius": payload.radius_meters,
                "sort": "distance",
                "size": payload.limit,
            },
        )
        documents = data.get("documents", [])
        if not isinstance(documents, list):
            documents = []

        return AnimalHospitalSearchResult(
            location=location,
            items=[self._to_hospital_item(item) for item in documents if isinstance(item, dict)],
        )

    def _get_json(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            raise LocationSearchError("KAKAO_REST_API_KEY is not configured")

        headers = {"Authorization": f"KakaoAK {self.api_key}"}
        try:
            response = httpx.get(
                f"{self.api_base_url}{path}",
                params=params,
                headers=headers,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LocationSearchError("kakao local api request failed") from exc

        data = response.json()
        if not isinstance(data, dict):
            raise LocationSearchError("kakao local api returned invalid response")
        return data

    def _to_location(self, region_text: str, document: dict[str, Any]) -> RegionLocation:
        address = document.get("address") if isinstance(document.get("address"), dict) else {}
        road_address = document.get("road_address") if isinstance(document.get("road_address"), dict) else {}
        address_name = (
            str(document.get("address_name") or "")
            or str(address.get("address_name") or "")
            or str(road_address.get("address_name") or "")
        )

        return RegionLocation(
            region_text=region_text,
            normalized_address=address_name,
            x=float(document.get("x") or address.get("x") or road_address.get("x")),
            y=float(document.get("y") or address.get("y") or road_address.get("y")),
            region_1depth_name=str(address.get("region_1depth_name") or road_address.get("region_1depth_name") or "") or None,
            region_2depth_name=str(address.get("region_2depth_name") or road_address.get("region_2depth_name") or "") or None,
            region_3depth_name=str(address.get("region_3depth_name") or road_address.get("region_3depth_name") or "") or None,
        )

    @staticmethod
    def _to_hospital_item(item: dict[str, Any]) -> AnimalHospitalItem:
        distance = item.get("distance")
        return AnimalHospitalItem(
            name=str(item.get("place_name") or "이름 없는 동물병원"),
            address=str(item.get("address_name") or "") or None,
            road_address=str(item.get("road_address_name") or "") or None,
            phone=str(item.get("phone") or "") or None,
            distance_meters=int(distance) if str(distance).isdigit() else None,
            place_url=str(item.get("place_url") or "") or None,
            x=float(item["x"]) if item.get("x") else None,
            y=float(item["y"]) if item.get("y") else None,
        )
