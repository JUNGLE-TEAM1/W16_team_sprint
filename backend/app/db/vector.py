from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.core.embedding import embedding_dimensions


def ensure_pgvector_schema(db: Session) -> bool:
    if db.get_bind().dialect.name != "postgresql":
        return False

    dimensions = embedding_dimensions()
    db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    db.execute(
        text(
            f"ALTER TABLE post_embeddings "
            f"ADD COLUMN IF NOT EXISTS embedding vector({dimensions})"
        )
    )
    db.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS ix_post_embeddings_embedding_hnsw
            ON post_embeddings
            USING hnsw (embedding vector_cosine_ops)
            WHERE embedding IS NOT NULL
            """
        )
    )
    db.execute(
        text(
            f"""
            CREATE OR REPLACE FUNCTION match_support_cards(
                query_embedding vector({dimensions}),
                match_count integer
            )
            RETURNS TABLE(post_id integer, score double precision)
            LANGUAGE sql
            STABLE
            AS $$
                SELECT
                    pe.post_id,
                    (1 - (pe.embedding <=> query_embedding))::double precision AS score
                FROM post_embeddings pe
                JOIN posts p ON p.id = pe.post_id
                WHERE p.author_name = 'data-bot'
                  AND pe.embedding IS NOT NULL
                ORDER BY pe.embedding <=> query_embedding
                LIMIT match_count
            $$;
            """
        )
    )
    return True


def vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(f"{component:.9g}" for component in vector) + "]"
