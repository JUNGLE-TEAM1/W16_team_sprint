from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def ensure_development_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    if "posts" not in inspector.get_table_names():
        return

    post_columns = {column["name"] for column in inspector.get_columns("posts")}
    if "like_count" in post_columns:
        return

    with engine.begin() as connection:
        connection.execute(
            text("ALTER TABLE posts ADD COLUMN like_count INTEGER NOT NULL DEFAULT 0")
        )
