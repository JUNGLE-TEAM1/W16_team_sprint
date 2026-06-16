from __future__ import annotations

from fastapi import status

from backend.app.core.errors import AppError
from backend.app.repositories.embedding_repository import PostEmbeddingRepository
from backend.app.schemas.ai import (
    RELATED_POST_LIMIT,
    RELATED_POST_MIN_SIMILARITY,
    RelatedPostItem,
    RelatedPostsRequest,
    RelatedPostsResponse,
)
from backend.app.services.embedding_service import PostEmbeddingService
from backend.app.services.rag_summary_service import RagSummaryProvider


class RagService:
    def __init__(
        self,
        embeddings: PostEmbeddingRepository,
        embedding_service: PostEmbeddingService,
        summary_provider: RagSummaryProvider | None = None,
        limit: int = RELATED_POST_LIMIT,
        min_similarity: float = RELATED_POST_MIN_SIMILARITY,
    ) -> None:
        self.embeddings = embeddings
        self.embedding_service = embedding_service
        self.summary_provider = summary_provider
        self.limit = limit
        self.min_similarity = min_similarity

    def find_related_posts(self, payload: RelatedPostsRequest) -> RelatedPostsResponse:
        query_text = self.embedding_service.build_text(
            title=payload.title,
            content=payload.content,
            tags=payload.tags,
        )
        try:
            query_embedding = self.embedding_service.embed(query_text)
        except Exception as exc:
            raise AppError(
                code="RAG_EMBEDDING_FAILED",
                message="유사 게시글 검색을 위한 embedding 생성에 실패했습니다.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                details={},
            ) from exc

        rows = self.embeddings.find_related_posts(
            query_embedding=query_embedding,
            limit=self.limit,
            min_similarity=self.min_similarity,
            exclude_post_id=payload.exclude_post_id,
        )
        summaries: dict[int, str] = {}
        if self.summary_provider is not None and rows:
            try:
                summaries = self.summary_provider.summarize(payload, rows)
            except Exception:
                summaries = {}

        return RelatedPostsResponse(
            items=[
                RelatedPostItem(
                    post_id=row.post_id,
                    title=row.title,
                    content_preview=row.content_preview,
                    tags=row.tags,
                    similarity=row.similarity,
                    summary=summaries.get(row.post_id),
                )
                for row in rows
            ]
        )
