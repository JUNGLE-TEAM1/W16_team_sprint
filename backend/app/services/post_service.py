from __future__ import annotations

from typing import Protocol

from fastapi import status

from backend.app.core.errors import AppError
from backend.app.models.post import Post
from backend.app.repositories.post_embedding_repository import PostEmbeddingRepository
from backend.app.models.tag import Tag
from backend.app.schemas.post import PostCreate, PostListResponse, PostRead, PostUpdate
from backend.app.services.embedding_provider import EmbeddingProvider
from backend.app.services.rag_service import build_embedding_text, post_embedding_metadata


class PostRepositoryPort(Protocol):
    def create(self, post: Post) -> Post:
        pass

    def list(
        self,
        *,
        tag: str | None = None,
        q: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[Post], int]:
        pass

    def get(self, post_id: int) -> Post | None:
        pass

    def delete(self, post: Post) -> None:
        pass

    def resolve_tags(self, names: list[str]) -> list[Tag]:
        pass


class UnitOfWork(Protocol):
    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass


class PostService:
    def __init__(
        self,
        posts: PostRepositoryPort,
        unit_of_work: UnitOfWork,
        embeddings: PostEmbeddingRepository | None = None,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self.posts = posts
        self.unit_of_work = unit_of_work
        self.embeddings = embeddings
        self.embedding_provider = embedding_provider

    def create(self, payload: PostCreate, user_id: int) -> Post:
        post = Post(title=payload.title, content=payload.content, user_id=user_id)
        post.tags = self.posts.resolve_tags(self._normalize_tags(payload.tags))
        try:
            saved_post = self.posts.create(post)
            self.unit_of_work.commit()
            self._sync_embedding(saved_post)
            return saved_post
        except Exception:
            self.unit_of_work.rollback()
            raise

    def list(
        self,
        *,
        tag: str | None = None,
        q: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> PostListResponse:
        posts, total = self.posts.list(tag=tag, q=q, page=page, size=size)
        pages = (total + size - 1) // size if total else 0
        return PostListResponse(
            items=[PostRead.model_validate(post) for post in posts],
            total=total,
            page=page,
            size=size,
            pages=pages,
        )

    def get(self, post_id: int) -> Post:
        post = self.posts.get(post_id)
        if post is None:
            raise AppError(
                code="POST_NOT_FOUND",
                message="게시글을 찾을 수 없습니다.",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"post_id": post_id},
            )
        return post

    def update(self, post_id: int, payload: PostUpdate, user_id: int) -> Post:
        post = self.get(post_id)
        self._ensure_owner(post, user_id)
        post.title = payload.title
        post.content = payload.content
        post.tags = self.posts.resolve_tags(self._normalize_tags(payload.tags))
        try:
            self.unit_of_work.commit()
            self._sync_embedding(post)
            return post
        except Exception:
            self.unit_of_work.rollback()
            raise

    def delete(self, post_id: int, user_id: int) -> None:
        post = self.get(post_id)
        self._ensure_owner(post, user_id)
        try:
            self.posts.delete(post)
            self.unit_of_work.commit()
        except Exception:
            self.unit_of_work.rollback()
            raise

    def _ensure_owner(self, post: Post, user_id: int) -> None:
        if post.user_id != user_id:
            raise AppError(
                code="POST_FORBIDDEN",
                message="게시글을 수정하거나 삭제할 권한이 없습니다.",
                status_code=status.HTTP_403_FORBIDDEN,
                details={"post_id": post.id},
            )

    def _normalize_tags(self, tags: list[str]) -> list[str]:
        normalized_tags: list[str] = []
        seen_tags: set[str] = set()
        for tag in tags:
            normalized_tag = tag.strip().lower()
            if not normalized_tag or normalized_tag in seen_tags:
                continue
            normalized_tags.append(normalized_tag)
            seen_tags.add(normalized_tag)
        return normalized_tags

    def _sync_embedding(self, post: Post) -> None:
        if self.embeddings is None or self.embedding_provider is None:
            return

        content_snapshot = build_embedding_text(post.title, post.content, [tag.name for tag in post.tags])
        metadata = post_embedding_metadata(post)
        try:
            embedding = self.embedding_provider.embed(content_snapshot)
            self.embeddings.upsert_ready(
                post=post,
                embedding=embedding,
                content_snapshot=content_snapshot,
                metadata=metadata,
                model_name=self.embedding_provider.model_name,
            )
            self.unit_of_work.commit()
        except Exception as exc:
            self.unit_of_work.rollback()
            try:
                self.embeddings.upsert_failed(
                    post=post,
                    content_snapshot=content_snapshot,
                    metadata=metadata,
                    model_name=self.embedding_provider.model_name,
                    error=str(exc),
                )
                self.unit_of_work.commit()
            except Exception:
                self.unit_of_work.rollback()
