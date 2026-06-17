from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from backend.app.models.knowledge import (
    KNOWLEDGE_STATUS_COMPLETED,
    KNOWLEDGE_STATUS_FAILED,
    KnowledgeChunk,
    KnowledgeDocument,
)


@dataclass(frozen=True)
class KnowledgeSearchRow:
    chunk_id: int
    document_id: int
    title: str
    content: str
    question: str | None
    answer: str | None
    department: str | None
    disease: str | None
    life_cycle: str | None
    source_kind: str
    split: str
    similarity: float
    metadata: dict[str, Any]


class KnowledgeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_document_by_external_id(self, source_external_id: str) -> KnowledgeDocument | None:
        statement = (
            select(KnowledgeDocument)
            .options(joinedload(KnowledgeDocument.chunks))
            .where(KnowledgeDocument.source_external_id == source_external_id)
        )
        return self.db.execute(statement).unique().scalar_one_or_none()

    def save_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        self.db.add(document)
        self.db.flush()
        self.db.refresh(document)
        return document

    def replace_chunks(self, document: KnowledgeDocument, chunks: list[KnowledgeChunk]) -> list[KnowledgeChunk]:
        if document.id is not None:
            self.db.execute(delete(KnowledgeChunk).where(KnowledgeChunk.document_id == document.id))
            self.db.flush()
        document.chunks = chunks
        self.db.add(document)
        self.db.flush()
        for chunk in chunks:
            self.db.refresh(chunk)
        return chunks

    def update_chunk_completed(
        self,
        chunk: KnowledgeChunk,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> KnowledgeChunk:
        chunk.embedding = embedding
        chunk.status = KNOWLEDGE_STATUS_COMPLETED
        chunk.error_message = None
        chunk.attempt_count += 1
        chunk.chunk_metadata = metadata
        self.db.add(chunk)
        self.db.flush()
        return chunk

    def update_chunk_failed(
        self,
        chunk: KnowledgeChunk,
        error_message: str,
        metadata: dict[str, Any],
    ) -> KnowledgeChunk:
        chunk.embedding = None
        chunk.status = KNOWLEDGE_STATUS_FAILED
        chunk.error_message = error_message[:2000]
        chunk.attempt_count += 1
        chunk.chunk_metadata = metadata
        self.db.add(chunk)
        self.db.flush()
        return chunk

    def hydrate_search_rows(
        self,
        scored_chunk_ids: list[tuple[int, float]],
        limit: int,
    ) -> list[KnowledgeSearchRow]:
        score_by_chunk_id = dict(scored_chunk_ids)
        if not score_by_chunk_id:
            return []

        statement = (
            select(KnowledgeChunk)
            .where(KnowledgeChunk.id.in_(score_by_chunk_id.keys()))
        )
        chunks = {
            chunk.id: chunk
            for chunk in self.db.execute(statement).scalars()
        }
        rows: list[KnowledgeSearchRow] = []
        for chunk_id, similarity in scored_chunk_ids:
            chunk = chunks.get(chunk_id)
            if chunk is None:
                continue
            rows.append(
                KnowledgeSearchRow(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    title=chunk.title,
                    content=chunk.content,
                    question=chunk.question,
                    answer=chunk.answer,
                    department=chunk.department,
                    disease=chunk.disease,
                    life_cycle=chunk.life_cycle,
                    source_kind=chunk.source_kind,
                    split=chunk.split,
                    similarity=similarity,
                    metadata=chunk.chunk_metadata,
                )
            )
            if len(rows) >= limit:
                break
        return rows
