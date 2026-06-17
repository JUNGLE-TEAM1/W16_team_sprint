from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from backend.app.db.base import Base
from backend.app.db.schema import ensure_development_schema


RAG_PROTECTED_TABLES = {
    "knowledge_documents",
    "knowledge_chunks",
    "langchain_pg_collection",
    "langchain_pg_embedding",
}

APP_RESET_TABLES = [
    "comments",
    "post_likes",
    "post_tags",
    "pet_care_advices",
    "post_embeddings",
    "auth_sessions",
    "refresh_tokens",
    "posts",
    "tags",
    "users",
]


def reset_app_data_only(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)
    ensure_development_schema(engine)

    existing_tables = set(inspect(engine).get_table_names())
    reset_tables = [table for table in APP_RESET_TABLES if table in existing_tables]
    protected = RAG_PROTECTED_TABLES.intersection(reset_tables)
    if protected:
        table_list = ", ".join(sorted(protected))
        raise RuntimeError(f"RAG knowledge base tables are protected from reset: {table_list}")

    if not reset_tables:
        return

    quoted_tables = ", ".join(f'"{table}"' for table in reset_tables)
    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE TABLE {quoted_tables} RESTART IDENTITY CASCADE"))
