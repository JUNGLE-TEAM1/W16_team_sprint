from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from backend.app.models.post_embedding import (
    EMBEDDING_STATUS_COMPLETED,
    EMBEDDING_STATUS_FAILED,
    PostEmbedding,
)


@dataclass(frozen=True)
class RelatedPostRow:
    post_id: int
    title: str
    content_preview: str
    content_for_summary: str
    tags: list[str]
    similarity: float


class PostEmbeddingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_post_id(self, post_id: int) -> PostEmbedding | None:
        statement = select(PostEmbedding).where(PostEmbedding.post_id == post_id)
        return self.db.scalar(statement)

    def upsert_completed(
        self,
        post_id: int,
        embedding: list[float],
        content_snapshot: str,
        content_hash: str,
        metadata: dict[str, Any],
    ) -> PostEmbedding:
        row = self._get_or_create(post_id)
        row.embedding = embedding
        row.content_snapshot = content_snapshot
        row.content_hash = content_hash
        row.embedding_metadata = metadata
        row.status = EMBEDDING_STATUS_COMPLETED
        row.error_message = None
        row.attempt_count += 1
        row.updated_at = datetime.utcnow()
        self.db.flush()
        return row

    def upsert_failed(
        self,
        post_id: int,
        content_snapshot: str,
        content_hash: str,
        metadata: dict[str, Any],
        error_message: str,
    ) -> PostEmbedding:
        row = self._get_or_create(post_id)
        row.embedding = None
        row.content_snapshot = content_snapshot
        row.content_hash = content_hash
        row.embedding_metadata = metadata
        row.status = EMBEDDING_STATUS_FAILED
        row.error_message = error_message[:1000]
        row.attempt_count += 1
        row.updated_at = datetime.utcnow()
        self.db.flush()
        return row

    def _get_or_create(self, post_id: int) -> PostEmbedding:
        row = self.get_by_post_id(post_id)
        if row is not None:
            return row

        row = PostEmbedding(
            post_id=post_id,
            embedding=None,
            content_snapshot="",
            content_hash="",
            embedding_metadata={},
        )
        self.db.add(row)
        self.db.flush()
        return row

    def find_related_posts(
        self,
        query_embedding: list[float],
        limit: int,
        min_similarity: float,
        exclude_post_id: int | None = None,
    ) -> list[RelatedPostRow]:
        statement = text(
            """
            WITH candidates AS (
                SELECT
                    posts.id AS post_id,
                    posts.title AS title,
                    posts.content AS content,
                    1 - (
                        post_embeddings.embedding <=> CAST(:query_embedding AS vector)
                    ) AS similarity
                FROM post_embeddings
                JOIN posts ON posts.id = post_embeddings.post_id
                WHERE post_embeddings.status = :completed_status
                  AND post_embeddings.embedding IS NOT NULL
                  AND (
                    CAST(:exclude_post_id AS INTEGER) IS NULL
                    OR posts.id <> CAST(:exclude_post_id AS INTEGER)
                  )
            )
            SELECT
                candidates.post_id,
                candidates.title,
                LEFT(candidates.content, :preview_length) AS content_preview,
                LEFT(candidates.content, :summary_length) AS content_for_summary,
                candidates.similarity,
                COALESCE(
                    ARRAY_AGG(tags.name ORDER BY tags.name)
                        FILTER (WHERE tags.name IS NOT NULL),
                    ARRAY[]::varchar[]
                ) AS tags
            FROM candidates
            LEFT JOIN post_tags ON post_tags.post_id = candidates.post_id
            LEFT JOIN tags ON tags.id = post_tags.tag_id
            WHERE candidates.similarity >= :min_similarity
            GROUP BY
                candidates.post_id,
                candidates.title,
                candidates.content,
                candidates.similarity
            ORDER BY candidates.similarity DESC, candidates.post_id DESC
            LIMIT :limit
            """
        )
        rows = self.db.execute(
            statement,
            {
                "completed_status": EMBEDDING_STATUS_COMPLETED,
                "exclude_post_id": exclude_post_id,
                "limit": limit,
                "min_similarity": min_similarity,
                "preview_length": 240,
                "summary_length": 1200,
                "query_embedding": self._to_vector_literal(query_embedding),
            },
        ).mappings()
        return [
            RelatedPostRow(
                post_id=int(row["post_id"]),
                title=str(row["title"]),
                content_preview=str(row["content_preview"]),
                content_for_summary=str(row["content_for_summary"]),
                tags=list(row["tags"] or []),
                similarity=round(float(row["similarity"]), 6),
            )
            for row in rows
        ]

    @staticmethod
    def _to_vector_literal(embedding: list[float]) -> str:
        return "[" + ",".join(str(float(value)) for value in embedding) + "]"
