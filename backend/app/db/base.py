from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event, text


class Base(DeclarativeBase):
    pass


@event.listens_for(Base.metadata, "before_create")
def create_pgvector_extension(target, connection, **kw) -> None:
    if connection.dialect.name == "postgresql":
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
