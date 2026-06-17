from fastapi.testclient import TestClient

from backend.app.api.dependencies import get_location_search_provider
from backend.app.db.session import engine
from backend.app.main import app
from backend.app.schemas.mcp import (
    AnimalHospitalItem,
    AnimalHospitalSearchResult,
    FindNearbyAnimalHospitalsArguments,
    GeocodeRegionArguments,
    GeocodeRegionResult,
    RegionLocation,
)
from backend.app.services.kakao_local_service import LocationSearchError
from backend.tests.db_reset import reset_app_data_only


class FakeLocationSearchProvider:
    def geocode_region(self, payload: GeocodeRegionArguments) -> GeocodeRegionResult:
        return GeocodeRegionResult(
            location=RegionLocation(
                region_text=payload.region_text,
                normalized_address="서울 마포구",
                x=126.901,
                y=37.566,
                region_1depth_name="서울",
                region_2depth_name="마포구",
            )
        )

    def find_nearby_animal_hospitals(
        self,
        payload: FindNearbyAnimalHospitalsArguments,
    ) -> AnimalHospitalSearchResult:
        location = None
        if payload.region_text:
            location = self.geocode_region(GeocodeRegionArguments(region_text=payload.region_text)).location
        return AnimalHospitalSearchResult(
            location=location,
            items=[
                AnimalHospitalItem(
                    name="마포튼튼동물병원",
                    address="서울 마포구 망원동 1",
                    road_address="서울 마포구 월드컵로 1",
                    phone="02-000-0000",
                    distance_meters=720,
                    place_url="https://place.map.kakao.com/1",
                    x=126.902,
                    y=37.567,
                )
            ],
        )


class FailingLocationSearchProvider:
    def geocode_region(self, payload: GeocodeRegionArguments) -> GeocodeRegionResult:
        raise LocationSearchError("boom")

    def find_nearby_animal_hospitals(
        self,
        payload: FindNearbyAnimalHospitalsArguments,
    ) -> AnimalHospitalSearchResult:
        raise LocationSearchError("boom")


def setup_function() -> None:
    app.dependency_overrides.clear()
    reset_app_data_only(engine)


def use_fake_location_search(provider=None) -> None:  # noqa: ANN001
    app.dependency_overrides[get_location_search_provider] = (
        lambda: provider or FakeLocationSearchProvider()
    )


def register_and_login(client: TestClient) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "team1",
            "password": "password123",
            "display_name": "Team One",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/session/login",
        json={"username": "team1", "password": "password123"},
    )
    assert login_response.status_code == 200


def json_rpc_request(method: str, params: dict | None = None) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": "test-1",
        "method": method,
        "params": params or {},
    }


def test_mcp_requires_session() -> None:
    use_fake_location_search()
    client = TestClient(app)

    response = client.post("/api/v1/mcp", json=json_rpc_request("tools/list"))

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "SESSION_REQUIRED"


def test_mcp_lists_pet_care_location_tools() -> None:
    use_fake_location_search()
    client = TestClient(app)
    register_and_login(client)

    response = client.post("/api/v1/mcp", json=json_rpc_request("tools/list"))

    assert response.status_code == 200
    body = response.json()
    tool_names = [tool["name"] for tool in body["result"]["tools"]]
    assert tool_names == ["geocode_region", "find_nearby_animal_hospitals"]
    assert all("inputSchema" in tool for tool in body["result"]["tools"])


def test_mcp_geocode_region_tool_returns_location() -> None:
    use_fake_location_search()
    client = TestClient(app)
    register_and_login(client)

    response = client.post(
        "/api/v1/mcp",
        json=json_rpc_request(
            "tools/call",
            {
                "name": "geocode_region",
                "arguments": {"region_text": "서울 마포구"},
            },
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert "error" not in body
    location = body["result"]["structuredContent"]["location"]
    assert location["normalized_address"] == "서울 마포구"
    assert location["region_2depth_name"] == "마포구"


def test_mcp_find_nearby_animal_hospitals_tool_returns_places() -> None:
    use_fake_location_search()
    client = TestClient(app)
    register_and_login(client)

    response = client.post(
        "/api/v1/mcp",
        json=json_rpc_request(
            "tools/call",
            {
                "name": "find_nearby_animal_hospitals",
                "arguments": {
                    "region_text": "서울 마포구",
                    "radius_meters": 5000,
                    "limit": 5,
                },
            },
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert "error" not in body
    items = body["result"]["structuredContent"]["items"]
    assert items[0]["name"] == "마포튼튼동물병원"
    assert items[0]["source"] == "kakao_local"
    assert items[0]["place_url"] == "https://place.map.kakao.com/1"


def test_mcp_returns_json_rpc_error_for_unknown_tool() -> None:
    use_fake_location_search()
    client = TestClient(app)
    register_and_login(client)

    response = client.post(
        "/api/v1/mcp",
        json=json_rpc_request(
            "tools/call",
            {
                "name": "unknown_tool",
                "arguments": {},
            },
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["error"]["code"] == -32602
    assert body["error"]["data"]["code"] == "MCP_TOOL_NOT_FOUND"


def test_mcp_returns_json_rpc_error_for_invalid_arguments() -> None:
    use_fake_location_search()
    client = TestClient(app)
    register_and_login(client)

    response = client.post(
        "/api/v1/mcp",
        json=json_rpc_request(
            "tools/call",
            {
                "name": "find_nearby_animal_hospitals",
                "arguments": {},
            },
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["error"]["code"] == -32602
    assert body["error"]["data"]["code"] == "MCP_INVALID_TOOL_ARGUMENTS"


def test_mcp_returns_json_rpc_error_when_location_search_fails() -> None:
    use_fake_location_search(FailingLocationSearchProvider())
    client = TestClient(app)
    register_and_login(client)

    response = client.post(
        "/api/v1/mcp",
        json=json_rpc_request(
            "tools/call",
            {
                "name": "geocode_region",
                "arguments": {"region_text": "서울 마포구"},
            },
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["error"]["code"] == -32000
    assert body["error"]["data"]["code"] == "MCP_LOCATION_SEARCH_FAILED"
