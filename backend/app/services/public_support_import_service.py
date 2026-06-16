from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Literal

from backend.app.core.security import hash_password
from backend.app.models.user import User
from backend.app.repositories.post_repository import PostRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.post import PostCreate, PostUpdate, normalize_tag_names
from backend.app.services.post_service import PostService

PublicSupportType = Literal["policy", "facility"]

DATA_BOT_USERNAME = "data-bot"
DATA_BOT_DISPLAY_NAME = "공공데이터"


@dataclass(frozen=True)
class PublicSupportRecord:
    source_external_id: str
    post_type: PublicSupportType
    title: str
    content: str
    tags: list[str]
    region: str | None = None
    source_name: str | None = None
    source_url: str | None = None

    @classmethod
    def from_mapping(cls, value: dict) -> "PublicSupportRecord":
        post_type = str(value.get("post_type", "")).strip()
        if post_type not in {"policy", "facility"}:
            raise ValueError("post_type must be policy or facility")

        source_external_id = str(value.get("source_external_id", "")).strip()
        title = str(value.get("title", "")).strip()
        content = str(value.get("content", "")).strip()
        if not source_external_id:
            raise ValueError("source_external_id is required")
        if not title:
            raise ValueError("title is required")
        if not content:
            raise ValueError("content is required")

        raw_tags = value.get("tags", [])
        if not isinstance(raw_tags, list):
            raise ValueError("tags must be a list")

        return cls(
            source_external_id=source_external_id,
            post_type=post_type,  # type: ignore[arg-type]
            title=title,
            content=content,
            tags=normalize_tag_names([str(tag) for tag in raw_tags]),
            region=_optional_text(value.get("region")),
            source_name=_optional_text(value.get("source_name")),
            source_url=_optional_text(value.get("source_url")),
        )


@dataclass(frozen=True)
class PublicSupportImportResult:
    created: int
    updated: int
    skipped: int
    data_bot_id: int


class PublicSupportImportService:
    def __init__(
        self,
        users: UserRepository,
        posts: PostRepository,
        post_service: PostService,
    ) -> None:
        self.users = users
        self.posts = posts
        self.post_service = post_service

    def import_records(self, records: list[PublicSupportRecord]) -> PublicSupportImportResult:
        data_bot = self._get_or_create_data_bot()
        created = 0
        updated = 0
        skipped = 0

        for record in records:
            existing_post = self.posts.get_by_source_external_id(record.source_external_id)
            if existing_post is None:
                self.post_service.create(self._to_create_payload(record), author_id=data_bot.id)
                created += 1
                continue

            if not self._record_changed(existing_post, record):
                skipped += 1
                continue

            self.post_service.update(
                post_id=existing_post.id,
                payload=self._to_update_payload(record),
                author_id=existing_post.author_id,
            )
            updated += 1

        return PublicSupportImportResult(
            created=created,
            updated=updated,
            skipped=skipped,
            data_bot_id=data_bot.id,
        )

    def _get_or_create_data_bot(self) -> User:
        user = self.users.get_by_username(DATA_BOT_USERNAME)
        if user is not None:
            return user

        user = User(
            username=DATA_BOT_USERNAME,
            password_hash=hash_password(secrets.token_urlsafe(32)),
            display_name=DATA_BOT_DISPLAY_NAME,
        )
        return self.users.create(user)

    @staticmethod
    def _to_create_payload(record: PublicSupportRecord) -> PostCreate:
        return PostCreate(
            title=record.title,
            content=record.content,
            tags=record.tags,
            post_type=record.post_type,
            region=record.region,
            source_name=record.source_name,
            source_url=record.source_url,
            source_external_id=record.source_external_id,
        )

    @staticmethod
    def _to_update_payload(record: PublicSupportRecord) -> PostUpdate:
        return PostUpdate(
            title=record.title,
            content=record.content,
            tags=record.tags,
            post_type=record.post_type,
            region=record.region,
            source_name=record.source_name,
            source_url=record.source_url,
            source_external_id=record.source_external_id,
        )

    @staticmethod
    def _record_changed(existing_post, record: PublicSupportRecord) -> bool:  # noqa: ANN001
        return (
            existing_post.title != record.title
            or existing_post.content != record.content
            or existing_post.post_type != record.post_type
            or existing_post.region != record.region
            or existing_post.source_name != record.source_name
            or existing_post.source_url != record.source_url
            or existing_post.source_external_id != record.source_external_id
            or set(existing_post.tags) != set(record.tags)
        )


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
