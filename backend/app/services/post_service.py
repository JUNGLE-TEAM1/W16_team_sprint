from __future__ import annotations

import logging
from math import ceil

from fastapi import status
from sqlalchemy.orm import Session

from backend.app.core.errors import AppError
from backend.app.models.post import Post
from backend.app.repositories.embedding_repository import PostEmbeddingRepository
from backend.app.repositories.post_repository import PostRepository
from backend.app.repositories.tag_repository import TagRepository
from backend.app.schemas.post import PostCreate, PostPage, PostSearchType, PostSortType, PostUpdate
from backend.app.services.embedding_service import PostEmbeddingService

logger = logging.getLogger(__name__)


class PostService:
    def __init__(
        self,
        db: Session,
        posts: PostRepository,
        tags: TagRepository | None = None,
        embeddings: PostEmbeddingRepository | None = None,
        embedding_service: PostEmbeddingService | None = None,
    ) -> None:
        self.db = db
        self.posts = posts
        self.tags = tags
        self.embeddings = embeddings
        self.embedding_service = embedding_service

    def create(self, payload: PostCreate, author_id: int) -> Post:
        post = Post(**payload.model_dump(exclude={"tags"}), author_id=author_id)
        post.tag_entities = self._get_tags(payload.tags)
        saved_post = self.posts.create(post)
        self._sync_embedding(saved_post)
        self.db.commit()
        return saved_post

    def list(
        self,
        q: str | None,
        search_type: PostSearchType,
        tag: str | None,
        sort: PostSortType,
        page: int,
        size: int,
    ) -> PostPage:
        normalized_q = q.strip() if q else None
        normalized_tag = tag.strip().lower() if tag else None
        posts, total = self.posts.list(
            q=normalized_q or None,
            search_type=search_type,
            tag=normalized_tag or None,
            sort=sort,
            page=page,
            size=size,
        )
        return PostPage(
            items=posts,
            page=page,
            size=size,
            total=total,
            total_pages=ceil(total / size) if total else 0,
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

    def update(self, post_id: int, payload: PostUpdate, author_id: int) -> Post:
        post = self.get(post_id)
        self._ensure_author(post, author_id)
        before_embedding_hash = self._build_embedding_hash(post)

        changes = payload.model_dump(exclude_unset=True)
        tag_names = changes.pop("tags", None)
        for field, value in changes.items():
            setattr(post, field, value)
        if tag_names is not None:
            post.tag_entities = self._get_tags(tag_names)

        if self._embedding_content_changed(post, before_embedding_hash):
            self._sync_embedding(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def like(self, post_id: int) -> Post:
        post = self.get(post_id)
        post.like_count += 1
        self.db.commit()
        return self.get(post_id)

    def delete(self, post_id: int, author_id: int) -> None:
        post = self.get(post_id)
        self._ensure_author(post, author_id)
        self.posts.delete(post)
        self.db.commit()

    @staticmethod
    def _ensure_author(post: Post, user_id: int) -> None:
        if post.author_id != user_id:
            raise AppError(
                code="POST_FORBIDDEN",
                message="게시글 작성자만 수정하거나 삭제할 수 있습니다.",
                status_code=status.HTTP_403_FORBIDDEN,
                details={"post_id": post.id},
            )

    def _get_tags(self, tag_names: list[str]) -> list:
        if not tag_names:
            return []
        if self.tags is None:
            return []
        return self.tags.get_or_create_many(tag_names)

    def _sync_embedding(self, post: Post) -> None:
        if self.embeddings is None or self.embedding_service is None:
            return

        content_snapshot = self.embedding_service.build_post_text(post)
        content_hash = self.embedding_service.build_content_hash(content_snapshot)
        metadata = self.embedding_service.build_metadata(post)
        try:
            embedding = self.embedding_service.embed(content_snapshot)
            self.embeddings.upsert_completed(
                post_id=post.id,
                embedding=embedding,
                content_snapshot=content_snapshot,
                content_hash=content_hash,
                metadata=metadata,
            )
        except Exception as exc:
            logger.warning("Post embedding sync failed for post_id=%s: %s", post.id, exc)
            self.embeddings.upsert_failed(
                post_id=post.id,
                content_snapshot=content_snapshot,
                content_hash=content_hash,
                metadata=metadata,
                error_message=str(exc),
            )

    def _build_embedding_hash(self, post: Post) -> str | None:
        if self.embedding_service is None:
            return None
        content_snapshot = self.embedding_service.build_post_text(post)
        return self.embedding_service.build_content_hash(content_snapshot)

    def _embedding_content_changed(self, post: Post, previous_hash: str | None) -> bool:
        if self.embedding_service is None or self.embeddings is None:
            return False
        current_hash = self._build_embedding_hash(post)
        return current_hash != previous_hash
