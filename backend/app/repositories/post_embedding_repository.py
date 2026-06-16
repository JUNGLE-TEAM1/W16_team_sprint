from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, selectinload

from backend.app.db.vector import ensure_pgvector_schema, vector_literal
from backend.app.models.post import Post
from backend.app.models.post_embedding import PostEmbedding


class PostEmbeddingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, *, post_id: int, source_text: str, vector: list[float]) -> PostEmbedding:
        has_pgvector = ensure_pgvector_schema(self.db)
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
        if has_pgvector:
            self.db.execute(
                text("UPDATE post_embeddings SET embedding = CAST(:vector AS vector) WHERE post_id = :post_id"),
                {"vector": vector_literal(vector), "post_id": post_id},
            )
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

    def count_support_vectors(self) -> int:
        if self.db.get_bind().dialect.name != "postgresql":
            statement = (
                select(func.count(PostEmbedding.post_id))
                .join(Post, Post.id == PostEmbedding.post_id)
                .where(Post.author_name == "data-bot")
            )
            return self.db.scalar(statement) or 0

        ensure_pgvector_schema(self.db)
        statement = text(
            """
            SELECT count(*)
            FROM post_embeddings pe
            JOIN posts p ON p.id = pe.post_id
            WHERE p.author_name = 'data-bot'
              AND pe.embedding IS NOT NULL
            """
        )
        return int(self.db.execute(statement).scalar_one() or 0)

    def search_similar_support_cards(
        self,
        *,
        query_vector: list[float],
        limit: int,
    ) -> list[tuple[float, PostEmbedding, Post]]:
        if self.db.get_bind().dialect.name != "postgresql":
            return []

        ensure_pgvector_schema(self.db)
        rows = self.db.execute(
            text(
                """
                SELECT
                    pe.post_id,
                    1 - (pe.embedding <=> CAST(:query_vector AS vector)) AS score
                FROM post_embeddings pe
                JOIN posts p ON p.id = pe.post_id
                WHERE p.author_name = 'data-bot'
                  AND pe.embedding IS NOT NULL
                ORDER BY pe.embedding <=> CAST(:query_vector AS vector)
                LIMIT :limit
                """
            ),
            {"query_vector": vector_literal(query_vector), "limit": limit},
        ).all()
        if not rows:
            return []

        scores_by_post_id = {int(row.post_id): float(row.score) for row in rows}
        post_ids = list(scores_by_post_id)
        statement = (
            select(PostEmbedding, Post)
            .join(Post, Post.id == PostEmbedding.post_id)
            .options(selectinload(Post.tags))
            .where(Post.id.in_(post_ids))
        )
        pairs_by_post_id = {
            post.id: (embedding, post)
            for embedding, post in self.db.execute(statement).all()
        }

        results: list[tuple[float, PostEmbedding, Post]] = []
        for post_id in post_ids:
            pair = pairs_by_post_id.get(post_id)
            if pair is None:
                continue
            embedding, post = pair
            results.append((scores_by_post_id[post_id], embedding, post))
        return results
