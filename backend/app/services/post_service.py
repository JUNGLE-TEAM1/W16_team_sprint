from __future__ import annotations

from typing import Protocol

from fastapi import status

from backend.app.core.errors import AppError
from backend.app.models.post import Post
from backend.app.models.post_embedding import PostEmbedding
from backend.app.models.tag import Tag
from backend.app.models.user import User
from backend.app.schemas.post import PostCreate, PostListResponse, PostUpdate
from backend.app.services.rag_service import RagService


class PostRepositoryPort(Protocol):
    def create(self, post: Post) -> Post:
        pass

    def list(
        self,
        *,
        page: int,
        size: int,
        query: str | None = None,
        tag: str | None = None,
    ) -> tuple[list[Post], int]:
        pass

    def get(self, post_id: int) -> Post | None:
        pass

    def delete(self, post: Post) -> None:
        pass


class TagRepositoryPort(Protocol):
    def get_or_create_many(self, names: list[str]) -> list[Tag]:
        pass


class PostEmbeddingRepositoryPort(Protocol):
    def upsert(self, *, post_id: int, source_text: str, vector: list[float]) -> PostEmbedding:
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
        tags: TagRepositoryPort,
        embeddings: PostEmbeddingRepositoryPort,
        unit_of_work: UnitOfWork,
    ) -> None:
        self.posts = posts
        self.tags = tags
        self.embeddings = embeddings
        self.unit_of_work = unit_of_work

    def create(self, payload: PostCreate, user: User) -> Post:
        post = Post(
            title=payload.title,
            content=payload.content,
            author_name=user.email,
            user_id=user.id,
            tags=self.tags.get_or_create_many(self._normalize_tag_names(payload.tag_names)),
        )
        try:
            saved_post = self.posts.create(post)
            if self._should_index_post(saved_post):
                RagService(self.posts, self.embeddings, self.unit_of_work).index_post(saved_post)
            self.unit_of_work.commit()
            return saved_post
        except Exception:
            self.unit_of_work.rollback()
            raise

    def list(
        self,
        *,
        page: int,
        size: int,
        query: str | None = None,
        tag: str | None = None,
    ) -> PostListResponse:
        items, total = self.posts.list(
            page=page,
            size=size,
            query=query.strip() if query else None,
            tag=tag.strip().lower() if tag else None,
        )
        pages = (total + size - 1) // size if total else 0
        return PostListResponse(items=items, page=page, size=size, total=total, pages=pages)

    def get(self, post_id: int) -> Post:
        post = self.posts.get(post_id)
        if post is None:
            raise AppError(
                code="POST_NOT_FOUND",
                message="지원 카드나 상담 케이스를 찾을 수 없습니다.",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"post_id": post_id},
            )
        return post

    def update(self, post_id: int, payload: PostUpdate, user: User) -> Post:
        post = self.get(post_id)
        self._require_post_owner(post, user)

        update_data = payload.model_dump(exclude_unset=True)
        if "title" in update_data:
            post.title = payload.title or post.title
        if "content" in update_data:
            post.content = payload.content or post.content
        if payload.tag_names is not None:
            post.tags = self.tags.get_or_create_many(self._normalize_tag_names(payload.tag_names))

        try:
            if self._should_index_post(post):
                RagService(self.posts, self.embeddings, self.unit_of_work).index_post(post)
            self.unit_of_work.commit()
            return self.get(post.id)
        except Exception:
            self.unit_of_work.rollback()
            raise

    def delete(self, post_id: int, user: User) -> None:
        post = self.get(post_id)
        self._require_post_owner(post, user)

        try:
            self.posts.delete(post)
            self.unit_of_work.commit()
        except Exception:
            self.unit_of_work.rollback()
            raise

    def _require_post_owner(self, post: Post, user: User) -> None:
        if user.role == "admin":
            return
        if post.user_id == user.id:
            return
        raise AppError(
            code="FORBIDDEN",
            message="지원 카드나 상담 케이스를 변경할 권한이 없습니다.",
            status_code=status.HTTP_403_FORBIDDEN,
            details={"post_id": post.id},
        )

    def _normalize_tag_names(self, tag_names: list[str]) -> list[str]:
        normalized_names: list[str] = []
        for tag_name in tag_names:
            normalized_name = tag_name.strip().lower().lstrip("#")
            if normalized_name and normalized_name not in normalized_names:
                normalized_names.append(normalized_name)
        return normalized_names[:8]

    def _should_index_post(self, post: Post) -> bool:
        return post.author_name == "data-bot"
