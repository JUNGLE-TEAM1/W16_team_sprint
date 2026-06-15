from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Index, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    Index("ix_post_tags_tag_id_post_id", "tag_id", "post_id"),
)


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (Index("ix_tags_name", "name", unique=True),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    posts = relationship("Post", secondary=post_tags, back_populates="tags")
