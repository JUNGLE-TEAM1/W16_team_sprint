from fastapi import APIRouter

from backend.app.api.auth_dependencies import CurrentAuthContext
from backend.app.api.dependencies import RagServiceDependency
from backend.app.schemas.rag import SimilarPostsRequest, SimilarPostsResponse

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/similar-posts", response_model=SimilarPostsResponse)
def recommend_similar_posts(
    payload: SimilarPostsRequest,
    _: CurrentAuthContext,
    service: RagServiceDependency,
) -> SimilarPostsResponse:
    return service.recommend_similar_posts(payload)
