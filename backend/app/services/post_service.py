from __future__ import annotations

import logging
from math import ceil

from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.errors import AppError
from backend.app.models.post import Post
from backend.app.models.post_like import PostLike
from backend.app.repositories.embedding_repository import PostEmbeddingRepository
from backend.app.repositories.pet_care_advice_repository import PetCareAdviceRepository
from backend.app.repositories.post_repository import PostRepository
from backend.app.repositories.tag_repository import TagRepository
from backend.app.schemas.post import PostCreate, PostPage, PostSearchType, PostSortType, PostUpdate
from backend.app.services.embedding_service import PostEmbeddingService
from backend.app.services.langchain_rag_index import LangChainPostVectorIndex

logger = logging.getLogger(__name__)


class PostService:
    def __init__(
        self,
        db: Session,
        posts: PostRepository,
        tags: TagRepository | None = None,
        embeddings: PostEmbeddingRepository | None = None,
        pet_care_advices: PetCareAdviceRepository | None = None,
        embedding_service: PostEmbeddingService | None = None,
        rag_index: LangChainPostVectorIndex | None = None,
    ) -> None:
        self.db = db
        self.posts = posts
        self.tags = tags
        self.embeddings = embeddings
        self.pet_care_advices = pet_care_advices
        self.embedding_service = embedding_service
        self.rag_index = rag_index

    def create(self, payload: PostCreate, author_id: int) -> Post:
        data = payload.model_dump(exclude={"tags"})
        data.update(self._default_policy_for_type(payload.post_type))
        post = Post(**data, author_id=author_id)
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

    def list_my_consultations(self, author_id: int, page: int, size: int) -> PostPage:
        posts, total = self.posts.list_private_cases_by_author(
            author_id=author_id,
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

    def get(self, post_id: int, viewer_id: int | None = None) -> Post:
        post = self.posts.get(post_id)
        if post is None or not self._can_view(post, viewer_id):
            raise AppError(
                code="POST_NOT_FOUND",
                message="상담 질문을 찾을 수 없습니다.",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"post_id": post_id},
            )
        return post

    def update(self, post_id: int, payload: PostUpdate, author_id: int) -> Post:
        post = self.posts.get(post_id)
        if post is None:
            raise self._not_found(post_id)
        self._ensure_author(post, author_id)
        before_embedding_hash = self._build_embedding_hash(post)

        changes = payload.model_dump(exclude_unset=True)
        tag_names = changes.pop("tags", None)
        should_mark_advice_stale = self._should_mark_advice_stale(changes, tag_names)
        changes.update(self._default_policy_for_type(changes.get("post_type", post.post_type)))
        for field, value in changes.items():
            setattr(post, field, value)
        if tag_names is not None:
            post.tag_entities = self._get_tags(tag_names)

        if should_mark_advice_stale and self.pet_care_advices is not None:
            self.pet_care_advices.mark_stale(post.id)
        if self._embedding_content_changed(post, before_embedding_hash):
            self._sync_embedding(post)
        elif not self._is_rag_indexable(post):
            self._delete_embedding(post.id)
        self.db.commit()
        self.db.refresh(post)
        return post

    def like(self, post_id: int, user_id: int) -> Post:
        post = self.get(post_id, viewer_id=user_id)
        if post.visibility != "public":
            raise AppError(
                code="POST_LIKE_DISABLED",
                message="공개 상담 질문에만 관심 등록을 할 수 있습니다.",
                status_code=status.HTTP_403_FORBIDDEN,
                details={"post_id": post_id},
            )
        if self.db.get(PostLike, {"post_id": post_id, "user_id": user_id}) is not None:
            return post

        self.db.add(PostLike(post_id=post_id, user_id=user_id))
        post.like_count += 1
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
        return self.get(post_id)

    def delete(self, post_id: int, author_id: int) -> None:
        post = self.posts.get(post_id)
        if post is None:
            raise self._not_found(post_id)
        self._ensure_author(post, author_id)
        self._delete_embedding(post.id)
        self.posts.delete(post)
        self.db.commit()

    @staticmethod
    def _ensure_author(post: Post, user_id: int) -> None:
        if post.author_id != user_id:
            raise AppError(
                code="POST_FORBIDDEN",
                message="작성자만 수정하거나 삭제할 수 있습니다.",
                status_code=status.HTTP_403_FORBIDDEN,
                details={"post_id": post.id},
            )

    @staticmethod
    def _not_found(post_id: int) -> AppError:
        return AppError(
            code="POST_NOT_FOUND",
            message="상담 질문을 찾을 수 없습니다.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"post_id": post_id},
        )

    @staticmethod
    def _default_policy_for_type(post_type: object) -> dict[str, str]:
        normalized_type = str(getattr(post_type, "value", post_type))
        if normalized_type in {"policy", "facility"}:
            return {
                "visibility": "public",
                "comment_policy": "none",
                "rag_scope": "public",
            }
        return {
            "visibility": "public",
            "comment_policy": "public",
            "rag_scope": "excluded",
        }

    @staticmethod
    def _can_view(post: Post, viewer_id: int | None) -> bool:
        if post.visibility == "public":
            return True
        return viewer_id is not None and post.author_id == viewer_id

    def _get_tags(self, tag_names: list[str]) -> list:
        if not tag_names:
            return []
        if self.tags is None:
            return []
        return self.tags.get_or_create_many(tag_names)

    def _sync_embedding(self, post: Post) -> None:
        if self.embeddings is None or self.embedding_service is None:
            return
        if not self._is_rag_indexable(post):
            self._delete_embedding(post.id)
            return

        content_snapshot = self.embedding_service.build_post_text(post)
        content_hash = self.embedding_service.build_content_hash(content_snapshot)
        metadata = self.embedding_service.build_metadata(post)
        try:
            embedding = self.embedding_service.embed(content_snapshot)
            if self.rag_index is not None:
                self.rag_index.upsert_post(
                    post=post,
                    content_snapshot=content_snapshot,
                    embedding=embedding,
                    metadata=metadata,
                )
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

    def _delete_embedding(self, post_id: int) -> None:
        if self.rag_index is None:
            return
        try:
            self.rag_index.delete_post(post_id)
        except Exception as exc:
            logger.warning("Post vector index delete failed for post_id=%s: %s", post_id, exc)

    def _build_embedding_hash(self, post: Post) -> str | None:
        if self.embedding_service is None or not self._is_rag_indexable(post):
            return None
        content_snapshot = self.embedding_service.build_post_text(post)
        return self.embedding_service.build_content_hash(content_snapshot)

    def _embedding_content_changed(self, post: Post, previous_hash: str | None) -> bool:
        if self.embedding_service is None or self.embeddings is None:
            return False
        current_hash = self._build_embedding_hash(post)
        return current_hash != previous_hash

    @staticmethod
    def _is_rag_indexable(post: Post) -> bool:
        return (
            post.visibility == "public"
            and post.rag_scope == "public"
            and post.post_type in {"policy", "facility"}
        )

    @staticmethod
    def _should_mark_advice_stale(changes: dict, tag_names: list[str] | None) -> bool:
        advice_sensitive_fields = {"title", "content", "region"}
        return tag_names is not None or any(field in changes for field in advice_sensitive_fields)
