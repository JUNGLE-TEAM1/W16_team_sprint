from __future__ import annotations

from collections.abc import Iterable

from langchain_core.documents import Document
from langchain_postgres import PGVector
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from backend.app.core.config import settings
from backend.app.models.post import Post
from backend.app.repositories.embedding_repository import RelatedPostRow
from backend.app.services.embedding_service import EmbeddingProvider, as_langchain_embeddings


class LangChainPostVectorIndex:
    def __init__(
        self,
        db: Session,
        embedding_provider: EmbeddingProvider,
        connection: str = settings.database_url,
        collection_name: str = settings.langchain_rag_collection_name,
    ) -> None:
        self.db = db
        self.embedding_provider = embedding_provider
        self.connection = connection
        self.collection_name = collection_name
        self._vector_store: PGVector | None = None

    def upsert_post(
        self,
        post: Post,
        content_snapshot: str,
        embedding: list[float],
        metadata: dict,
    ) -> None:
        document = self._build_document(post, content_snapshot, metadata)
        self._store().add_embeddings(
            texts=[document.page_content],
            embeddings=[embedding],
            metadatas=[document.metadata],
            ids=[self._document_id(post.id)],
        )

    def delete_post(self, post_id: int) -> None:
        self._store().delete(ids=[self._document_id(post_id)])

    def find_related_posts(
        self,
        query_text: str,
        limit: int,
        min_similarity: float,
        exclude_post_id: int | None = None,
    ) -> list[RelatedPostRow]:
        results = self._store().similarity_search_with_score(
            query=query_text,
            k=max(limit * 5, 10),
        )
        scored_post_ids: list[tuple[int, float]] = []
        seen_post_ids: set[int] = set()
        for document, score in results:
            post_id = self._metadata_post_id(document.metadata)
            if post_id is None or post_id in seen_post_ids:
                continue
            if exclude_post_id is not None and post_id == exclude_post_id:
                continue
            similarity = round(self._distance_to_similarity(float(score)), 6)
            if similarity < min_similarity:
                continue
            scored_post_ids.append((post_id, similarity))
            seen_post_ids.add(post_id)

        return self._hydrate_related_posts(scored_post_ids, limit)

    def _store(self) -> PGVector:
        if self._vector_store is None:
            self._vector_store = PGVector(
                embeddings=as_langchain_embeddings(self.embedding_provider),
                connection=self.connection,
                collection_name=self.collection_name,
                use_jsonb=True,
            )
        return self._vector_store

    def _hydrate_related_posts(
        self,
        scored_post_ids: Iterable[tuple[int, float]],
        limit: int,
    ) -> list[RelatedPostRow]:
        score_by_post_id = dict(scored_post_ids)
        if not score_by_post_id:
            return []

        statement = (
            select(Post)
            .options(joinedload(Post.tag_entities))
            .where(
                Post.id.in_(score_by_post_id.keys()),
                Post.visibility == "public",
                Post.rag_scope == "public",
                Post.post_type.in_(["policy", "facility"]),
            )
        )
        posts = {
            post.id: post
            for post in self.db.execute(statement).unique().scalars()
        }
        rows: list[RelatedPostRow] = []
        for post_id, similarity in score_by_post_id.items():
            post = posts.get(post_id)
            if post is None:
                continue
            rows.append(
                RelatedPostRow(
                    post_id=post.id,
                    title=post.title,
                    content_preview=post.content[:240],
                    content_for_summary=post.content[:1200],
                    tags=post.tags,
                    similarity=similarity,
                )
            )
            if len(rows) >= limit:
                break
        return rows

    @staticmethod
    def _build_document(post: Post, content_snapshot: str, metadata: dict) -> Document:
        return Document(
            page_content=content_snapshot,
            metadata={
                **metadata,
                "post_id": post.id,
                "title": post.title,
                "tags": post.tags,
                "author_id": post.author_id,
                "post_type": post.post_type,
                "visibility": post.visibility,
                "rag_scope": post.rag_scope,
                "region": post.region,
                "source_name": post.source_name,
                "source_external_id": post.source_external_id,
            },
        )

    @staticmethod
    def _document_id(post_id: int) -> str:
        return f"post:{post_id}"

    @staticmethod
    def _metadata_post_id(metadata: dict) -> int | None:
        value = metadata.get("post_id")
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return None

    @staticmethod
    def _distance_to_similarity(distance: float) -> float:
        return max(0.0, min(1.0, 1.0 - distance))
