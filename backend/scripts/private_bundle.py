import io
import json
import zipfile
from collections.abc import Iterable, Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import AnnalsArticle, AnnalsChunk


BUNDLE_SCHEMA_VERSION = 1
DEFAULT_BUNDLE_NAME = "annals_private_bundle.zip"
ARTICLES_MEMBER = "annals_articles.jsonl"
CHUNKS_MEMBER = "annals_chunks.jsonl"
MANIFEST_MEMBER = "manifest.json"

ARTICLE_COLUMNS = [
    "article_id",
    "source_file",
    "title",
    "king",
    "reign_date",
    "date",
    "content",
    "official_url",
    "subject_classes",
]
CHUNK_COLUMNS = [
    "chunk_id",
    "article_id",
    "chunk_index",
    "chunk_text",
    "embedding",
    "embedding_model",
    "token_count_estimate",
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_bundle_path(path_value: str | None = None) -> Path:
    raw_path = path_value or get_settings().annals_private_bundle_zip or f"data/{DEFAULT_BUNDLE_NAME}"
    bundle_path = Path(raw_path).expanduser()
    if bundle_path.is_absolute():
        return bundle_path
    return project_root() / bundle_path


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def row_from_model(model: Any, columns: Iterable[str]) -> dict[str, Any]:
    return {column: getattr(model, column) for column in columns}


def count_rows(db: Session) -> dict[str, int]:
    return {
        "annals_articles": db.scalar(select(func.count(AnnalsArticle.id))) or 0,
        "annals_chunks": db.scalar(select(func.count(AnnalsChunk.id))) or 0,
    }


def read_manifest(bundle_path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(bundle_path) as archive:
        with archive.open(MANIFEST_MEMBER) as raw_file:
            return json.load(raw_file)


def iter_jsonl_member(bundle_path: Path, member_name: str) -> Iterator[dict[str, Any]]:
    with zipfile.ZipFile(bundle_path) as archive:
        if member_name not in archive.namelist():
            raise FileNotFoundError(f"{member_name} is missing from {bundle_path}")
        with archive.open(member_name) as raw_file:
            text_file = io.TextIOWrapper(raw_file, encoding="utf-8")
            for line in text_file:
                stripped = line.strip()
                if stripped:
                    yield json.loads(stripped)


def write_jsonl_member(
    archive: zipfile.ZipFile,
    member_name: str,
    rows: Iterable[dict[str, Any]],
) -> int:
    count = 0
    with archive.open(member_name, "w") as raw_file:
        text_file = io.TextIOWrapper(raw_file, encoding="utf-8")
        for row in rows:
            text_file.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            text_file.write("\n")
            count += 1
        text_file.flush()
    return count


def batched(rows: Iterable[dict[str, Any]], batch_size: int) -> Iterator[list[dict[str, Any]]]:
    batch: list[dict[str, Any]] = []
    for row in rows:
        batch.append(row)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
