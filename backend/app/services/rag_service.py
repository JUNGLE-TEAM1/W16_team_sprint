from __future__ import annotations

from backend.app.core.config import settings
from backend.app.models.post import Post
from backend.app.repositories.post_embedding_repository import PostEmbeddingRepository
from backend.app.schemas.rag import SimilarPostItem, SimilarPostsRequest, SimilarPostsResponse
from backend.app.services.embedding_provider import EmbeddingProvider
from backend.app.services.summary_provider import SummaryProvider


class RagService:
    def __init__(
        self,
        *,
        embeddings: PostEmbeddingRepository,
        embedding_provider: EmbeddingProvider,
        summary_provider: SummaryProvider,
    ) -> None:
        self.embeddings = embeddings
        self.embedding_provider = embedding_provider
        self.summary_provider = summary_provider

    def recommend_similar_posts(self, payload: SimilarPostsRequest) -> SimilarPostsResponse:
        query_text = build_embedding_text(payload.title, payload.content, payload.tags)
        query_embedding = self.embedding_provider.embed(query_text)
        rows = self.embeddings.find_similar(query_embedding=query_embedding, limit=payload.limit)
        items = [
            SimilarPostItem(
                post_id=record.post.id,
                title=record.post.title,
                preview=_preview(record.post.content),
                similarity=round(similarity, 4),
                similarity_level=similarity_level(similarity),
                tags=[tag.name for tag in record.post.tags],
            )
            for record, similarity in rows
        ]
        summary_error = None
        try:
            summary = self.summary_provider.summarize(
                query=query_text,
                contexts=[item.model_dump() for item in items],
            )
        except Exception as exc:
            summary_error = str(exc)[:500]
            summary = fallback_summary(items)

        return SimilarPostsResponse(
            summary=summary,
            summary_error=summary_error,
            items=items,
            message=_message(items),
        )


def build_embedding_text(title: str, content: str, tags: list[str]) -> str:
    normalized_tags = ", ".join(tag.strip().lower() for tag in tags if tag.strip())
    return "\n".join(
        [
            f"제목: {title.strip()}",
            f"본문: {content.strip()}",
            f"태그: {normalized_tags}",
        ]
    ).strip()


def post_embedding_metadata(post: Post) -> dict:
    return {
        "title": post.title,
        "tags": [tag.name for tag in post.tags],
    }


def similarity_level(similarity: float) -> str:
    if similarity >= settings.rag_high_similarity:
        return "high"
    if similarity >= settings.rag_medium_similarity:
        return "medium"
    return "low"


def fallback_summary(items: list[SimilarPostItem]) -> str:
    if not items:
        return "비슷한 게시글을 찾지 못했습니다."
    top_item = items[0]
    return f'비슷한 글 {len(items)}개를 찾았습니다. 가장 가까운 글은 "{top_item.title}"입니다.'


def _preview(content: str, max_length: int = 140) -> str:
    normalized = " ".join(content.split())
    if len(normalized) <= max_length:
        return normalized
    return f"{normalized[:max_length].rstrip()}..."


def _message(items: list[SimilarPostItem]) -> str:
    if not items:
        return "비슷한 게시글이 없습니다."
    return f"비슷한 게시글 {len(items)}개를 찾았습니다."
