from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.post import Post
from backend.app.models.post_embedding import PostEmbedding


class PostEmbeddingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, *, post_id: int, source_text: str, vector: list[float]) -> PostEmbedding:
        embedding = self.db.get(PostEmbedding, post_id)
        if embedding is None:
            embedding = PostEmbedding(
                post_id=post_id,
                source_text=source_text,
                vector_json=json.dumps(vector),
            )
            self.db.add(embedding)
        else:
            embedding.source_text = source_text
            embedding.vector_json = json.dumps(vector)
            embedding.updated_at = datetime.utcnow()

        self.db.flush()
        return embedding

    def list_with_posts(self) -> list[tuple[PostEmbedding, Post]]:
        statement = (
            select(PostEmbedding, Post)
            .join(Post, Post.id == PostEmbedding.post_id)
            .options(selectinload(Post.tags))
            .order_by(PostEmbedding.updated_at.desc())
        )
        return list(self.db.execute(statement).all())

    def post_ids(self) -> set[int]:
        statement = select(PostEmbedding.post_id)
        return set(self.db.scalars(statement))
