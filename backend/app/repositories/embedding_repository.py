from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.post_embedding import (
    EMBEDDING_STATUS_COMPLETED,
    EMBEDDING_STATUS_FAILED,
    PostEmbedding,
)


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
