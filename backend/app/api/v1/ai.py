from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_rag_service
from backend.app.api.v1.auth import get_session_user
from backend.app.models.user import User
from backend.app.schemas.ai import RelatedPostsRequest, RelatedPostsResponse
from backend.app.services.rag_service import RagService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/rag/related-posts", response_model=RelatedPostsResponse)
def find_related_posts(
    payload: RelatedPostsRequest,
    _current_user: User = Depends(get_session_user),
    service: RagService = Depends(get_rag_service),
) -> RelatedPostsResponse:
    return service.find_related_posts(payload)
