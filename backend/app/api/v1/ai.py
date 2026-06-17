from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_pet_care_advice_service, get_rag_service
from backend.app.api.v1.auth import get_optional_session_user, get_session_user
from backend.app.models.user import User
from backend.app.schemas.ai import (
    PetCareAdviceRequest,
    PetCareAdviceResponse,
    RelatedPostsRequest,
    RelatedPostsResponse,
)
from backend.app.services.pet_care_advice_service import PetCareAdviceService
from backend.app.services.rag_service import RagService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/rag/related-posts", response_model=RelatedPostsResponse)
def find_related_posts(
    payload: RelatedPostsRequest,
    _current_user: User = Depends(get_session_user),
    service: RagService = Depends(get_rag_service),
) -> RelatedPostsResponse:
    return service.find_related_posts(payload)


@router.post("/pet-care/advice", response_model=PetCareAdviceResponse)
def create_pet_care_advice(
    payload: PetCareAdviceRequest,
    _current_user: User = Depends(get_session_user),
    service: PetCareAdviceService = Depends(get_pet_care_advice_service),
) -> PetCareAdviceResponse:
    return service.create_advice(payload)


@router.get("/pet-care/posts/{post_id}/advice", response_model=PetCareAdviceResponse | None)
def get_pet_care_post_advice(
    post_id: int,
    current_user: User | None = Depends(get_optional_session_user),
    service: PetCareAdviceService = Depends(get_pet_care_advice_service),
) -> PetCareAdviceResponse | None:
    return service.get_stored_advice(
        post_id=post_id,
        viewer_id=current_user.id if current_user else None,
    )


@router.post("/pet-care/posts/{post_id}/advice", response_model=PetCareAdviceResponse)
def create_pet_care_post_advice(
    post_id: int,
    current_user: User = Depends(get_session_user),
    service: PetCareAdviceService = Depends(get_pet_care_advice_service),
) -> PetCareAdviceResponse:
    return service.create_advice_for_post(post_id=post_id, viewer_id=current_user.id)
