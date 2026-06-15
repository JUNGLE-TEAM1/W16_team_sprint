from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import UserDefinedType

from backend.app.db.base import Base

EMBEDDING_DIMENSIONS = 1536
EMBEDDING_STATUS_PENDING = "pending"
EMBEDDING_STATUS_COMPLETED = "completed"
EMBEDDING_STATUS_FAILED = "failed"


class Vector(UserDefinedType):
    cache_ok = True

    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions

    def get_col_spec(self, **_: Any) -> str:
        return f"vector({self.dimensions})"

    def bind_processor(self, dialect: Any):
        def process(value: list[float] | None) -> str | None:
            if value is None:
                return None
            return "[" + ",".join(str(float(item)) for item in value) + "]"

        return process

    def result_processor(self, dialect: Any, coltype: Any):
        def process(value: Any) -> list[float] | None:
            if value is None or isinstance(value, list):
                return value
            return [float(item) for item in str(value).strip("[]").split(",") if item]

        return process


class PostEmbedding(Base):
    __tablename__ = "post_embeddings"
    __table_args__ = (
        UniqueConstraint("post_id", name="uq_post_embeddings_post_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIMENSIONS), nullable=True)
    content_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=EMBEDDING_STATUS_PENDING,
        server_default=EMBEDDING_STATUS_PENDING,
        index=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    embedding_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    post: Mapped["Post"] = relationship(back_populates="embedding")
