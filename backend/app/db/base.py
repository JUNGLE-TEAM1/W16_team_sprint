from sqlalchemy import event, text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


@event.listens_for(Base.metadata, "before_create")
def create_pgvector_extension(_, connection, **__) -> None:
    connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
