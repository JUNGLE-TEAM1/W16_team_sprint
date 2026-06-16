from __future__ import annotations

import argparse
import json
from pathlib import Path

from sqlalchemy.orm import Session

from backend.app import models  # noqa: F401
from backend.app.core.config import ROOT_DIR
from backend.app.db.base import Base
from backend.app.db.schema import ensure_development_schema
from backend.app.db.session import engine
from backend.app.repositories.embedding_repository import PostEmbeddingRepository
from backend.app.repositories.post_repository import PostRepository
from backend.app.repositories.tag_repository import TagRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.services.embedding_service import MockEmbeddingProvider, OpenAIEmbeddingProvider, PostEmbeddingService
from backend.app.services.langchain_rag_index import LangChainPostVectorIndex
from backend.app.services.post_service import PostService
from backend.app.services.public_support_import_service import (
    PublicSupportImportService,
    PublicSupportRecord,
)

DEFAULT_SEED_FILE = ROOT_DIR / "backend" / "app" / "data" / "public_support_seed.json"


def main() -> None:
    args = parse_args()
    records = load_records(args.file, args.limit)

    if args.dry_run:
        print(
            f"validated records={len(records)} file={args.file} "
            f"embedding_provider={args.embedding_provider}"
        )
        return

    Base.metadata.create_all(bind=engine)
    ensure_development_schema(engine)

    with Session(engine) as db:
        import_service = build_import_service(db, args.embedding_provider)
        result = import_service.import_records(records)
        db.commit()

    print(
        "public support seed import complete: "
        f"created={result.created}, updated={result.updated}, skipped={result.skipped}, "
        f"data_bot_id={result.data_bot_id}, embedding_provider={args.embedding_provider}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import public support/facility seed cards.")
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_SEED_FILE,
        help="Path to a JSON array of public support records.",
    )
    parser.add_argument(
        "--embedding-provider",
        choices=["none", "mock", "openai"],
        default="none",
        help=(
            "Embedding strategy for imported public cards. "
            "Use none for fast DB seed, mock for local tests, openai for real RAG."
        ),
    )
    parser.add_argument("--limit", type=int, default=None, help="Import only the first N records.")
    parser.add_argument("--dry-run", action="store_true", help="Validate records without writing DB rows.")
    return parser.parse_args()


def load_records(path: Path, limit: int | None = None) -> list[PublicSupportRecord]:
    with path.open(encoding="utf-8") as file:
        raw_records = json.load(file)

    if not isinstance(raw_records, list):
        raise ValueError("seed file must contain a JSON array")

    selected_records = raw_records[:limit] if limit is not None else raw_records
    return [PublicSupportRecord.from_mapping(record) for record in selected_records]


def build_import_service(db: Session, embedding_provider_name: str) -> PublicSupportImportService:
    posts = PostRepository(db)
    tags = TagRepository(db)
    users = UserRepository(db)

    embedding_provider = None
    if embedding_provider_name == "mock":
        embedding_provider = MockEmbeddingProvider()
    elif embedding_provider_name == "openai":
        embedding_provider = OpenAIEmbeddingProvider()

    if embedding_provider is None:
        post_service = PostService(db=db, posts=posts, tags=tags)
    else:
        post_service = PostService(
            db=db,
            posts=posts,
            tags=tags,
            embeddings=PostEmbeddingRepository(db),
            embedding_service=PostEmbeddingService(embedding_provider),
            rag_index=LangChainPostVectorIndex(db=db, embedding_provider=embedding_provider),
        )

    return PublicSupportImportService(
        users=users,
        posts=posts,
        post_service=post_service,
    )


if __name__ == "__main__":
    main()
