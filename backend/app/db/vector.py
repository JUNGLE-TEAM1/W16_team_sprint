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
    return True


def vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(f"{component:.9g}" for component in vector) + "]"
