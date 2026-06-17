from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import UserDefinedType

from app.database import Base


class Vector(UserDefinedType):
    cache_ok = True

    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions

    def get_col_spec(self, **_: Any) -> str:
        return f"vector({self.dimensions})"

    def bind_processor(self, dialect: Any) -> Any:
        def process(value: list[float] | None) -> str | None:
            if value is None:
                return None
            return "[" + ",".join(str(number) for number in value) + "]"

        return process

    def result_processor(self, dialect: Any, coltype: Any) -> Any:
        def process(value: str | None) -> list[float] | None:
            if value is None:
                return None
            if isinstance(value, list):
                return value
            return [float(number) for number in value.strip("[]").split(",") if number]

        return process


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    posts: Mapped[list["Post"]] = relationship(back_populates="author")
    comments: Mapped[list["Comment"]] = relationship(back_populates="author")
    voice_sessions: Mapped[list["VoiceSession"]] = relationship(back_populates="author")
    voice_messages: Mapped[list["VoiceMessage"]] = relationship(back_populates="author")


class AnnalsArticle(Base):
    __tablename__ = "annals_articles"
    __table_args__ = (UniqueConstraint("article_id", name="uq_annals_articles_article_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[str] = mapped_column(String(80), index=True)
    source_file: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(500), index=True)
    king: Mapped[str] = mapped_column(String(80), nullable=True)
    reign_date: Mapped[str] = mapped_column(String(120), nullable=True)
    date: Mapped[str] = mapped_column(String(40), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    official_url: Mapped[str] = mapped_column(String(255))
    subject_classes: Mapped[list[str]] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chunks: Mapped[list["AnnalsChunk"]] = relationship(
        back_populates="article",
        cascade="all, delete-orphan",
    )


class AnnalsChunk(Base):
    __tablename__ = "annals_chunks"
    __table_args__ = (UniqueConstraint("chunk_id", name="uq_annals_chunks_chunk_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chunk_id: Mapped[str] = mapped_column(String(120), index=True)
    article_id: Mapped[str] = mapped_column(ForeignKey("annals_articles.article_id"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    chunk_text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536))
    embedding_model: Mapped[str] = mapped_column(String(120))
    token_count_estimate: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    article: Mapped[AnnalsArticle] = relationship(back_populates="chunks")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    question: Mapped[str] = mapped_column(Text)
    ai_summary: Mapped[str] = mapped_column(Text)
    ai_interpretation: Mapped[str] = mapped_column(Text)
    suggested_tags: Mapped[list[str]] = mapped_column(JSONB, default=list)
    evidence_article_ids: Mapped[list[str]] = mapped_column(JSONB, default=list)
    agent_trace: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    author: Mapped[User] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        order_by="Comment.created_at",
    )
    voice_sessions: Mapped[list["VoiceSession"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
    )
    voice_messages: Mapped[list["VoiceMessage"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        order_by="VoiceMessage.created_at",
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    post: Mapped[Post] = relationship(back_populates="comments")
    author: Mapped[User] = relationship(back_populates="comments")


class VoiceSession(Base):
    __tablename__ = "voice_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    post: Mapped[Post] = relationship(back_populates="voice_sessions")
    author: Mapped[User] = relationship(back_populates="voice_sessions")
    messages: Mapped[list["VoiceMessage"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="VoiceMessage.created_at",
    )


class VoiceMessage(Base):
    __tablename__ = "voice_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("voice_sessions.id"), index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(String(20), index=True)
    content: Mapped[str] = mapped_column(Text)
    route_action: Mapped[str] = mapped_column(String(40), nullable=True)
    route_reason: Mapped[str] = mapped_column(Text, nullable=True)
    search_query: Mapped[str] = mapped_column(String(240), nullable=True)
    evidence_article_ids: Mapped[list[str]] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped[VoiceSession] = relationship(back_populates="messages")
    post: Mapped[Post] = relationship(back_populates="voice_messages")
    author: Mapped[User] = relationship(back_populates="voice_messages")
