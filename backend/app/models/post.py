from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.tag import post_tags


class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (Index("ix_posts_created_at", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    post_type: Mapped[str] = mapped_column(String(20), nullable=False, default="case", server_default="case")
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="private", server_default="private")
    comment_policy: Mapped[str] = mapped_column(String(20), nullable=False, default="none", server_default="none")
    rag_scope: Mapped[str] = mapped_column(String(20), nullable=False, default="excluded", server_default="excluded")
    region: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_external_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    like_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    author: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
    )
    likes: Mapped[list["PostLike"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
    )
    tag_entities: Mapped[list["Tag"]] = relationship(
        secondary=post_tags,
        back_populates="posts",
    )
    embedding: Mapped["PostEmbedding | None"] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        uselist=False,
    )
    pet_care_advice: Mapped["PetCareAdvice | None"] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        uselist=False,
    )

    @property
    def author_display_name(self) -> str:
        return self.author.display_name

    @property
    def tags(self) -> list[str]:
        return [tag.name for tag in sorted(self.tag_entities, key=lambda tag: tag.name)]

    @property
    def comment_count(self) -> int:
        if "_comment_count" in self.__dict__:
            return self.__dict__["_comment_count"]
        return len(self.comments)

    @comment_count.setter
    def comment_count(self, value: int) -> None:
        self.__dict__["_comment_count"] = value
