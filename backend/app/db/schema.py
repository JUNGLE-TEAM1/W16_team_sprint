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
    with engine.begin() as connection:
        if "post_type" not in post_columns:
            connection.execute(
                text("ALTER TABLE posts ADD COLUMN post_type VARCHAR(20) NOT NULL DEFAULT 'case'")
            )
        if "visibility" not in post_columns:
            connection.execute(
                text("ALTER TABLE posts ADD COLUMN visibility VARCHAR(20) NOT NULL DEFAULT 'private'")
            )
            connection.execute(
                text("UPDATE posts SET visibility = 'public' WHERE post_type IN ('policy', 'facility')")
            )
        if "comment_policy" not in post_columns:
            connection.execute(
                text("ALTER TABLE posts ADD COLUMN comment_policy VARCHAR(20) NOT NULL DEFAULT 'none'")
            )
        if "rag_scope" not in post_columns:
            connection.execute(
                text("ALTER TABLE posts ADD COLUMN rag_scope VARCHAR(20) NOT NULL DEFAULT 'excluded'")
            )
            connection.execute(
                text("UPDATE posts SET rag_scope = 'public' WHERE post_type IN ('policy', 'facility')")
            )
        if "region" not in post_columns:
            connection.execute(text("ALTER TABLE posts ADD COLUMN region VARCHAR(80)"))
        if "source_name" not in post_columns:
            connection.execute(text("ALTER TABLE posts ADD COLUMN source_name VARCHAR(120)"))
        if "source_url" not in post_columns:
            connection.execute(text("ALTER TABLE posts ADD COLUMN source_url TEXT"))
        if "source_external_id" not in post_columns:
            connection.execute(text("ALTER TABLE posts ADD COLUMN source_external_id VARCHAR(120)"))
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS ix_posts_source_external_id ON posts (source_external_id)")
        )
        connection.execute(
            text(
                "UPDATE posts SET visibility = 'public', comment_policy = 'none', rag_scope = 'public' "
                "WHERE post_type IN ('policy', 'facility')"
            )
        )
        connection.execute(
            text(
                "UPDATE posts SET visibility = 'public', comment_policy = 'public', rag_scope = 'excluded' "
                "WHERE post_type = 'case'"
            )
        )

    if "post_embeddings" not in table_names:
        post_embeddings_exists = False
    else:
        post_embeddings_exists = True

    if "pet_care_advices" in table_names:
        advice_columns = {column["name"] for column in inspector.get_columns("pet_care_advices")}
        with engine.begin() as connection:
            if "hospital_candidates" not in advice_columns:
                connection.execute(
                    text(
                        "ALTER TABLE pet_care_advices "
                        "ADD COLUMN hospital_candidates JSON NOT NULL DEFAULT '[]'"
                    )
                )

    if not post_embeddings_exists:
        return

    embedding_columns = {column["name"] for column in inspector.get_columns("post_embeddings")}
    with engine.begin() as connection:
        connection.execute(
            text(
                "DELETE FROM post_embeddings USING posts "
                "WHERE post_embeddings.post_id = posts.id "
                "AND NOT (posts.visibility = 'public' AND posts.rag_scope = 'public' "
                "AND posts.post_type IN ('policy', 'facility'))"
            )
        )
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
