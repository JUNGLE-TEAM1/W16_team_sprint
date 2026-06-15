from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def ensure_development_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if "posts" not in table_names:
        return

    post_columns = {column["name"] for column in inspector.get_columns("posts")}
    if "like_count" not in post_columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE posts ADD COLUMN like_count INTEGER NOT NULL DEFAULT 0")
            )

    if "post_embeddings" not in table_names:
        return

    embedding_columns = {column["name"] for column in inspector.get_columns("post_embeddings")}
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE post_embeddings ALTER COLUMN embedding DROP NOT NULL"))
        if "content_hash" not in embedding_columns:
            connection.execute(
                text("ALTER TABLE post_embeddings ADD COLUMN content_hash VARCHAR(64) NOT NULL DEFAULT ''")
            )
        if "status" not in embedding_columns:
            connection.execute(
                text(
                    "ALTER TABLE post_embeddings "
                    "ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending'"
                )
            )
        if "error_message" not in embedding_columns:
            connection.execute(text("ALTER TABLE post_embeddings ADD COLUMN error_message TEXT"))
        if "attempt_count" not in embedding_columns:
            connection.execute(
                text("ALTER TABLE post_embeddings ADD COLUMN attempt_count INTEGER NOT NULL DEFAULT 0")
            )
