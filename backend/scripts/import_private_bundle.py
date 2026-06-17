from argparse import ArgumentParser
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert

from app.database import SessionLocal, create_tables
from app.models import AnnalsArticle, AnnalsChunk
from scripts.private_bundle import (
    ARTICLE_COLUMNS,
    ARTICLES_MEMBER,
    CHUNK_COLUMNS,
    CHUNKS_MEMBER,
    BUNDLE_SCHEMA_VERSION,
    batched,
    count_rows,
    iter_jsonl_member,
    read_manifest,
    resolve_bundle_path,
)


BATCH_SIZE = 500


def upsert_articles(rows: list[dict]) -> None:
    if not rows:
        return
    statement = insert(AnnalsArticle).values(rows)
    statement = statement.on_conflict_do_update(
        constraint="uq_annals_articles_article_id",
        set_={column: getattr(statement.excluded, column) for column in ARTICLE_COLUMNS if column != "article_id"},
    )
    with SessionLocal() as db:
        db.execute(statement)
        db.commit()


def upsert_chunks(rows: list[dict]) -> None:
    if not rows:
        return
    statement = insert(AnnalsChunk).values(rows)
    statement = statement.on_conflict_do_update(
        constraint="uq_annals_chunks_chunk_id",
        set_={column: getattr(statement.excluded, column) for column in CHUNK_COLUMNS if column != "chunk_id"},
    )
    with SessionLocal() as db:
        db.execute(statement)
        db.commit()


def clear_annals_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(AnnalsChunk))
        db.execute(delete(AnnalsArticle))
        db.commit()


def should_skip_import(skip_if_present: bool) -> bool:
    if not skip_if_present:
        return False
    with SessionLocal() as db:
        counts = count_rows(db)
    return counts["annals_articles"] > 0 and counts["annals_chunks"] > 0


def import_bundle(bundle_path: Path, *, force: bool, skip_if_present: bool) -> None:
    create_tables()
    if should_skip_import(skip_if_present):
        print("Private bundle import skipped because annals data already exists.")
        return

    manifest = read_manifest(bundle_path)
    schema_version = manifest.get("schema_version")
    if schema_version != BUNDLE_SCHEMA_VERSION:
        raise RuntimeError(
            f"Unsupported bundle schema_version {schema_version}; expected {BUNDLE_SCHEMA_VERSION}."
        )

    if force:
        clear_annals_data()

    imported_articles = 0
    for batch in batched(iter_jsonl_member(bundle_path, ARTICLES_MEMBER), BATCH_SIZE):
        upsert_articles(batch)
        imported_articles += len(batch)

    imported_chunks = 0
    for batch in batched(iter_jsonl_member(bundle_path, CHUNKS_MEMBER), BATCH_SIZE):
        upsert_chunks(batch)
        imported_chunks += len(batch)

    print(f"Imported {imported_articles} articles and {imported_chunks} chunks from {bundle_path}")


def main() -> None:
    parser = ArgumentParser(description="Import a team-only precomputed RAG zip bundle.")
    parser.add_argument("--bundle", default=None, help="Bundle zip path. Defaults to ANNALS_PRIVATE_BUNDLE_ZIP.")
    parser.add_argument("--force", action="store_true", help="Clear existing annals rows before importing.")
    parser.add_argument("--skip-missing", action="store_true", help="Do nothing when the bundle zip is absent.")
    parser.add_argument("--skip-if-present", action="store_true", help="Do nothing when annals rows already exist.")
    args = parser.parse_args()

    bundle_path = resolve_bundle_path(args.bundle)
    if not bundle_path.exists():
        if args.skip_missing:
            print(f"Private bundle not found at {bundle_path}; starting without precomputed RAG data.")
            create_tables()
            return
        raise FileNotFoundError(f"Private bundle not found: {bundle_path}")

    import_bundle(bundle_path, force=args.force, skip_if_present=args.skip_if_present)


if __name__ == "__main__":
    main()
