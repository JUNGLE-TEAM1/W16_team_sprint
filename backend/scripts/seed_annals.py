from argparse import ArgumentParser
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

from app.config import get_settings
from app.database import SessionLocal, create_tables
from app.models import AnnalsArticle, AnnalsChunk, User
from app.services.chunking import chunk_article
from app.services.embeddings import embed_texts
from app.services.xml_parser import parse_annals_file


def first_xml_file(xml_dir: Path) -> Path:
    preferred = xml_dir / "2nd_waa_101.xml"
    if preferred.exists():
        return preferred
    candidates = sorted(xml_dir.glob("*.xml"))
    if not candidates:
        raise FileNotFoundError(f"No XML files found in {xml_dir}")
    return candidates[0]


def seed_articles(xml_path: Path, limit: int) -> int:
    articles = parse_annals_file(xml_path, limit=limit)
    rows = [
        {
            "article_id": article.article_id,
            "source_file": article.source_file,
            "title": article.title,
            "king": article.king,
            "reign_date": article.reign_date,
            "date": article.date,
            "content": article.content,
            "official_url": article.official_url,
            "subject_classes": article.subject_classes,
        }
        for article in articles
    ]

    if not rows:
        return 0

    statement = insert(AnnalsArticle).values(rows)
    update_fields = {
        column: getattr(statement.excluded, column)
        for column in [
            "source_file",
            "title",
            "king",
            "reign_date",
            "date",
            "content",
            "official_url",
            "subject_classes",
        ]
    }
    statement = statement.on_conflict_do_update(
        constraint="uq_annals_articles_article_id",
        set_=update_fields,
    )

    with SessionLocal() as db:
        db.execute(statement)
        if not db.query(User).filter(User.username == "demo").first():
            db.add(User(username="demo", password_hash="demo-password-not-for-production"))
        db.commit()
    return len(rows)


def seed_chunks(article_ids: list[str]) -> int:
    if not article_ids:
        return 0

    settings = get_settings()
    with SessionLocal() as db:
        articles = list(
            db.scalars(
                select(AnnalsArticle)
                .where(AnnalsArticle.article_id.in_(article_ids))
                .order_by(AnnalsArticle.article_id)
            )
        )

        chunks = [chunk for article in articles for chunk in chunk_article(article)]
        if not chunks:
            return 0

        embeddings = embed_texts([chunk.chunk_text for chunk in chunks])
        rows = [
            {
                "chunk_id": chunk.chunk_id,
                "article_id": chunk.article_id,
                "chunk_index": chunk.chunk_index,
                "chunk_text": chunk.chunk_text,
                "embedding": embedding,
                "embedding_model": settings.openai_embedding_model,
                "token_count_estimate": chunk.token_count_estimate,
            }
            for chunk, embedding in zip(chunks, embeddings, strict=True)
        ]

        db.execute(delete(AnnalsChunk).where(AnnalsChunk.article_id.in_(article_ids)))
        statement = insert(AnnalsChunk).values(rows)
        update_fields = {
            column: getattr(statement.excluded, column)
            for column in [
                "article_id",
                "chunk_index",
                "chunk_text",
                "embedding",
                "embedding_model",
                "token_count_estimate",
            ]
        }
        statement = statement.on_conflict_do_update(
            constraint="uq_annals_chunks_chunk_id",
            set_=update_fields,
        )
        db.execute(statement)
        db.commit()
        return len(rows)


def main() -> None:
    parser = ArgumentParser(description="Seed Joseon Annals articles into PostgreSQL.")
    parser.add_argument("--xml-dir", default=get_settings().annals_xml_dir)
    parser.add_argument("--xml-file", default=None)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--skip-embeddings", action="store_true")
    args = parser.parse_args()

    create_tables()
    xml_path = Path(args.xml_file) if args.xml_file else first_xml_file(Path(args.xml_dir))
    articles = parse_annals_file(xml_path, limit=args.limit)
    article_ids = [article.article_id for article in articles]
    count = seed_articles(xml_path, limit=args.limit)
    print(f"Seeded {count} annals articles from {xml_path}")
    if args.skip_embeddings:
        print("Skipped annals chunks and embeddings.")
        return
    chunk_count = seed_chunks(article_ids)
    print(f"Seeded {chunk_count} annals chunks with embeddings.")


if __name__ == "__main__":
    main()
