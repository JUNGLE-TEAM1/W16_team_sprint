from argparse import ArgumentParser
import json
import zipfile

from sqlalchemy import select

from app.config import get_settings
from app.database import SessionLocal, create_tables
from app.models import AnnalsArticle, AnnalsChunk
from scripts.private_bundle import (
    ARTICLE_COLUMNS,
    ARTICLES_MEMBER,
    BUNDLE_SCHEMA_VERSION,
    CHUNK_COLUMNS,
    CHUNKS_MEMBER,
    MANIFEST_MEMBER,
    count_rows,
    resolve_bundle_path,
    row_from_model,
    utc_timestamp,
    write_jsonl_member,
)


def main() -> None:
    parser = ArgumentParser(description="Export precomputed private RAG data to a team-only zip bundle.")
    parser.add_argument("--output", default=None, help="Output zip path. Defaults to ANNALS_PRIVATE_BUNDLE_ZIP.")
    args = parser.parse_args()

    bundle_path = resolve_bundle_path(args.output)
    bundle_path.parent.mkdir(parents=True, exist_ok=True)

    create_tables()
    settings = get_settings()
    with SessionLocal() as db:
        counts = count_rows(db)
        manifest = {
            "schema_version": BUNDLE_SCHEMA_VERSION,
            "created_at": utc_timestamp(),
            "embedding_model": settings.openai_embedding_model,
            "embedding_dimensions": settings.openai_embedding_dimensions,
            "counts": counts,
            "members": [ARTICLES_MEMBER, CHUNKS_MEMBER],
        }

        article_rows = (
            row_from_model(article, ARTICLE_COLUMNS)
            for article in db.scalars(select(AnnalsArticle).order_by(AnnalsArticle.article_id)).yield_per(500)
        )
        chunk_rows = (
            row_from_model(chunk, CHUNK_COLUMNS)
            for chunk in db.scalars(select(AnnalsChunk).order_by(AnnalsChunk.article_id, AnnalsChunk.chunk_index)).yield_per(500)
        )

        with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            archive.writestr(
                MANIFEST_MEMBER,
                json.dumps(manifest, ensure_ascii=False, indent=2),
            )
            exported_articles = write_jsonl_member(archive, ARTICLES_MEMBER, article_rows)
            exported_chunks = write_jsonl_member(archive, CHUNKS_MEMBER, chunk_rows)

    print(f"Exported {exported_articles} articles and {exported_chunks} chunks to {bundle_path}")


if __name__ == "__main__":
    main()
