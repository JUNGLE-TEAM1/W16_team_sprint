from sqlalchemy import inspect, text

from backend.app.db.base import Base
from backend.app.db.schema import ensure_development_schema
from backend.app.db.session import engine
from backend.app.models.post_embedding import EMBEDDING_DIMENSIONS
from backend.app.models.knowledge import KNOWLEDGE_EMBEDDING_DIMENSIONS


def setup_function() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_development_schema(engine)


def test_post_embeddings_table_uses_pgvector_and_post_fk() -> None:
    inspector = inspect(engine)

    assert "post_embeddings" in inspector.get_table_names()

    with engine.connect() as connection:
        columns = set(
            connection.scalars(
                text(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'post_embeddings'
                    """
                )
            )
        )
        embedding_type = connection.scalar(
            text(
                """
                SELECT format_type(attribute.atttypid, attribute.atttypmod)
                FROM pg_attribute AS attribute
                JOIN pg_class AS class ON class.oid = attribute.attrelid
                WHERE class.relname = 'post_embeddings'
                  AND attribute.attname = 'embedding'
                """
            )
        )

    assert {
        "id",
        "post_id",
        "embedding",
        "content_snapshot",
        "content_hash",
        "status",
        "error_message",
        "attempt_count",
        "metadata",
        "created_at",
        "updated_at",
    } <= columns
    assert embedding_type == f"vector({EMBEDDING_DIMENSIONS})"

    foreign_keys = inspector.get_foreign_keys("post_embeddings")
    assert foreign_keys[0]["referred_table"] == "posts"
    assert foreign_keys[0]["constrained_columns"] == ["post_id"]
    assert foreign_keys[0]["referred_columns"] == ["id"]


def test_pgvector_extension_is_enabled() -> None:
    with engine.connect() as connection:
        installed_version = connection.scalar(
            text("SELECT installed_version FROM pg_available_extensions WHERE name = 'vector'")
        )

    assert installed_version is not None


def test_knowledge_tables_use_pgvector_and_document_fk() -> None:
    inspector = inspect(engine)

    assert "knowledge_documents" in inspector.get_table_names()
    assert "knowledge_chunks" in inspector.get_table_names()

    with engine.connect() as connection:
        chunk_columns = set(
            connection.scalars(
                text(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'knowledge_chunks'
                    """
                )
            )
        )
        embedding_type = connection.scalar(
            text(
                """
                SELECT format_type(attribute.atttypid, attribute.atttypmod)
                FROM pg_attribute AS attribute
                JOIN pg_class AS class ON class.oid = attribute.attrelid
                WHERE class.relname = 'knowledge_chunks'
                  AND attribute.attname = 'embedding'
                """
            )
        )

    assert {
        "id",
        "document_id",
        "chunk_index",
        "source_kind",
        "split",
        "department",
        "disease",
        "life_cycle",
        "title",
        "question",
        "answer",
        "content",
        "content_hash",
        "embedding",
        "status",
        "error_message",
        "attempt_count",
        "metadata",
        "created_at",
        "updated_at",
    } <= chunk_columns
    assert embedding_type == f"vector({KNOWLEDGE_EMBEDDING_DIMENSIONS})"

    foreign_keys = inspector.get_foreign_keys("knowledge_chunks")
    assert foreign_keys[0]["referred_table"] == "knowledge_documents"
    assert foreign_keys[0]["constrained_columns"] == ["document_id"]
    assert foreign_keys[0]["referred_columns"] == ["id"]
