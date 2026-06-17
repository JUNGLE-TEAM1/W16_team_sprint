from __future__ import annotations

import argparse
from pathlib import Path

from backend.app.core.config import settings
from backend.app.db.base import Base
from backend.app.db.schema import ensure_development_schema
from backend.app.db.session import SessionLocal, engine
from backend.app.repositories.knowledge_repository import KnowledgeRepository
from backend.app.services.aihub_pet_care_import_service import AihubPetCareImportService
from backend.app.services.embedding_service import MockEmbeddingProvider, OpenAIEmbeddingProvider
from backend.app.services.knowledge_rag_index import KnowledgeVectorIndex


def main() -> None:
    parser = argparse.ArgumentParser(description="Import AIHub pet-care corpus into the RAG knowledge base.")
    parser.add_argument("--data-dir", default=settings.aihub_pet_care_data_dir)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--commit-interval", type=int, default=100)
    parser.add_argument("--embedding-batch-size", type=int, default=64)
    parser.add_argument("--progress-interval", type=int, default=500)
    parser.add_argument(
        "--embedding-provider",
        choices=["openai", "mock", "none"],
        default="openai",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir).expanduser()
    if not data_dir.exists():
        raise SystemExit(f"AIHub data directory does not exist: {data_dir}")
    if args.embedding_provider == "openai" and not settings.openai_api_key:
        raise SystemExit("OPENAI_API_KEY is required when --embedding-provider openai")

    Base.metadata.create_all(bind=engine)
    ensure_development_schema(engine)

    db = SessionLocal()
    try:
        provider = None
        rag_index = None
        if args.embedding_provider == "openai":
            provider = OpenAIEmbeddingProvider()
            rag_index = KnowledgeVectorIndex(db=db, embedding_provider=provider)
        elif args.embedding_provider == "mock":
            provider = MockEmbeddingProvider()
            rag_index = KnowledgeVectorIndex(db=db, embedding_provider=provider)

        service = AihubPetCareImportService(
            db=db,
            repository=KnowledgeRepository(db),
            embedding_provider=provider,
            rag_index=rag_index,
        )
        print(
            "AIHub pet-care import started: "
            f"data_dir={data_dir}, "
            f"limit={args.limit}, "
            f"embedding_provider={args.embedding_provider}, "
            f"commit_interval={args.commit_interval}, "
            f"embedding_batch_size={args.embedding_batch_size}, "
            f"progress_interval={args.progress_interval}"
        )
        stats = service.import_dir(
            root_dir=data_dir,
            limit=args.limit,
            commit_interval=args.commit_interval,
            embedding_batch_size=args.embedding_batch_size,
            progress_interval=args.progress_interval,
            progress_callback=print_progress,
        )
    finally:
        db.close()

    print(
        "AIHub pet-care import complete: "
        f"documents_created={stats.documents_created}, "
        f"documents_updated={stats.documents_updated}, "
        f"documents_skipped={stats.documents_skipped}, "
        f"chunks_created={stats.chunks_created}, "
        f"chunks_embedded={stats.chunks_embedded}, "
        f"chunks_failed={stats.chunks_failed}, "
        f"chunks_skipped={stats.chunks_skipped}, "
        f"chunks_reindexed={stats.chunks_reindexed}"
    )


def print_progress(processed: int, total: int, stats) -> None:  # noqa: ANN001
    print(
        "AIHub pet-care import progress: "
        f"{processed}/{total} documents, "
        f"created={stats.documents_created}, "
        f"updated={stats.documents_updated}, "
        f"skipped={stats.documents_skipped}, "
        f"embedded={stats.chunks_embedded}, "
        f"failed={stats.chunks_failed}, "
        f"chunk_skipped={stats.chunks_skipped}, "
        f"reindexed={stats.chunks_reindexed}"
    )


if __name__ == "__main__":
    main()
