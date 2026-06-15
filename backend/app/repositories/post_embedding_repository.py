from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.post import Post
from backend.app.models.post_embedding import PostEmbedding


class PostEmbeddingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert_ready(
        self,
        *,
        post: Post,
        embedding: list[float],
        content_snapshot: str,
        metadata: dict,
        model_name: str,
    ) -> PostEmbedding:
        record = self._get_by_post_id(post.id)
        if record is None:
            record = PostEmbedding(post_id=post.id)
            self.db.add(record)
        record.embedding = embedding
        record.content_snapshot = content_snapshot
        record.embedding_metadata = metadata
        record.model_name = model_name
        record.status = "ready"
        record.last_error = None
        return record

    def upsert_failed(
        self,
        *,
        post: Post,
        content_snapshot: str,
        metadata: dict,
        model_name: str,
        error: str,
    ) -> PostEmbedding:
        record = self._get_by_post_id(post.id)
        if record is None:
            record = PostEmbedding(post_id=post.id, retry_count=0)
            self.db.add(record)
        record.content_snapshot = content_snapshot
        record.embedding_metadata = metadata
        record.model_name = model_name
        record.status = "failed"
        record.last_error = error[:1000]
        record.retry_count = (record.retry_count or 0) + 1
        return record

    def find_similar(
        self,
        *,
        query_embedding: list[float],
        limit: int,
    ) -> list[tuple[PostEmbedding, float]]:
        distance = PostEmbedding.embedding.cosine_distance(query_embedding)
        statement = (
            select(PostEmbedding, (1 - distance).label("similarity"))
            .options(selectinload(PostEmbedding.post).selectinload(Post.tags))
            .where(PostEmbedding.status == "ready", PostEmbedding.embedding.is_not(None))
            .order_by(distance)
            .limit(limit)
        )
        rows = self.db.execute(statement).all()
        return [(record, float(similarity)) for record, similarity in rows]

    def _get_by_post_id(self, post_id: int) -> PostEmbedding | None:
        return self.db.scalar(select(PostEmbedding).where(PostEmbedding.post_id == post_id))
