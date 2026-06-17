from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.api.dependencies import (
    get_embedding_provider,
    get_location_search_provider,
    get_pet_care_advice_provider,
)
from backend.app.db.session import engine
from backend.app.main import app
from backend.app.repositories.knowledge_repository import KnowledgeRepository
from backend.app.schemas.ai import PetCareAdviceRequest
from backend.app.schemas.mcp import (
    AnimalHospitalItem,
    AnimalHospitalSearchResult,
    FindNearbyAnimalHospitalsArguments,
    GeocodeRegionArguments,
    GeocodeRegionResult,
    RegionLocation,
)
from backend.app.services.aihub_pet_care_import_service import AihubPetCareImportService
from backend.app.services.embedding_service import MockEmbeddingProvider
from backend.app.services.knowledge_rag_index import KnowledgeVectorIndex
from backend.tests.db_reset import reset_app_data_only
from backend.tests.test_aihub_pet_care_import import delete_sample_knowledge, write_sample_aihub_data


class MockPetCareAdviceProvider:
    def generate(  # noqa: ANN001
        self,
        payload: PetCareAdviceRequest,
        sources,
        hospital_candidates,
        hospital_guidance_note,
    ):
        return (
            f"{payload.title} 질문은 검색된 AIHub 근거와 관련이 있습니다. 확정 진단은 피하고 증상 변화를 관찰하세요.",
            ["기침 빈도와 호흡 상태를 기록하세요.", "증상이 악화되면 수의사에게 문의하세요."],
        )


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
        return AnimalHospitalSearchResult(
            location=self.geocode_region(GeocodeRegionArguments(region_text=payload.region_text or "서울 마포구")).location,
            items=[
                AnimalHospitalItem(
                    name="마포튼튼동물병원",
                    address="서울 마포구 망원동 1",
                    road_address="서울 마포구 월드컵로 1",
                    phone="02-000-0000",
                    distance_meters=720,
                    place_url="https://place.map.kakao.com/1",
                )
            ],
        )


def setup_function() -> None:
    app.dependency_overrides.clear()
    reset_app_data_only(engine)


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


def import_sample_knowledge(data_dir: Path) -> None:
    with Session(engine) as db:
        provider = MockEmbeddingProvider()
        service = AihubPetCareImportService(
            db=db,
            repository=KnowledgeRepository(db),
            embedding_provider=provider,
            rag_index=KnowledgeVectorIndex(db=db, embedding_provider=provider),
        )
        service.import_dir(data_dir)


def test_pet_care_advice_requires_session() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/ai/pet-care/advice",
        json={
            "title": "강아지가 기침해요",
            "content": "5개월 강아지가 켁켁 기침을 반복합니다.",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "SESSION_REQUIRED"


def test_pet_care_advice_returns_answer_action_plan_and_sources(tmp_path: Path) -> None:
    data_dir = write_sample_aihub_data(tmp_path)
    delete_sample_knowledge(data_dir)
    import_sample_knowledge(data_dir)
    app.dependency_overrides[get_embedding_provider] = lambda: MockEmbeddingProvider()
    app.dependency_overrides[get_pet_care_advice_provider] = lambda: MockPetCareAdviceProvider()
    client = TestClient(app)
    register_and_login(client)

    response = client.post(
        "/api/v1/ai/pet-care/advice",
        json={
            "title": "강아지가 기침해요",
            "content": "5개월 강아지가 켁켁 기침을 반복합니다. 병원에 바로 가야 할까요?",
            "tags": ["기침", "자견", "내과"],
            "life_cycle": "자견",
            "department": "내과",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "확정 진단" in body["safety_note"]
    assert "강아지가 기침해요" in body["answer"]
    assert body["action_plan"] == ["기침 빈도와 호흡 상태를 기록하세요.", "증상이 악화되면 수의사에게 문의하세요."]
    assert body["sources"]
    assert body["hospital_candidates"] == []
    assert body["sources"][0]["department"] == "내과"
    assert body["sources"][0]["source_kind"] in {"qa", "corpus"}


def test_pet_care_advice_is_saved_loaded_and_marked_stale(tmp_path: Path) -> None:
    data_dir = write_sample_aihub_data(tmp_path)
    delete_sample_knowledge(data_dir)
    import_sample_knowledge(data_dir)
    app.dependency_overrides[get_embedding_provider] = lambda: MockEmbeddingProvider()
    app.dependency_overrides[get_pet_care_advice_provider] = lambda: MockPetCareAdviceProvider()
    app.dependency_overrides[get_location_search_provider] = lambda: FakeLocationSearchProvider()
    client = TestClient(app)
    register_and_login(client)

    post_response = client.post(
        "/api/v1/posts",
        json={
            "title": "강아지가 기침해요",
            "content": "5개월 강아지가 켁켁 기침을 반복합니다. 병원에 바로 가야 할까요?",
            "tags": ["기침", "자견", "내과"],
            "region": "서울 마포구",
        },
    )
    assert post_response.status_code == 201
    post_id = post_response.json()["id"]

    create_response = client.post(f"/api/v1/ai/pet-care/posts/{post_id}/advice")
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["id"] is not None
    assert created["post_id"] == post_id
    assert created["status"] == "completed"
    assert created["sources"]
    assert created["hospital_candidates"][0]["name"] == "마포튼튼동물병원"

    loaded_response = client.get(f"/api/v1/ai/pet-care/posts/{post_id}/advice")
    assert loaded_response.status_code == 200
    assert loaded_response.json()["id"] == created["id"]

    repeated_response = client.post(f"/api/v1/ai/pet-care/posts/{post_id}/advice")
    assert repeated_response.status_code == 200
    assert repeated_response.json()["id"] == created["id"]
    assert repeated_response.json()["generated_at"] == created["generated_at"]

    update_response = client.patch(
        f"/api/v1/posts/{post_id}",
        json={
            "title": "강아지가 기침하고 콧물도 있어요",
            "content": "5개월 강아지가 켁켁 기침을 반복하고 콧물도 납니다.",
            "tags": ["기침", "콧물", "자견"],
            "region": "서울 마포구",
        },
    )
    assert update_response.status_code == 200

    stale_response = client.get(f"/api/v1/ai/pet-care/posts/{post_id}/advice")
    assert stale_response.status_code == 200
    assert stale_response.json()["status"] == "stale"

    regenerate_response = client.post(f"/api/v1/ai/pet-care/posts/{post_id}/advice")
    assert regenerate_response.status_code == 200
    assert regenerate_response.json()["status"] == "completed"
