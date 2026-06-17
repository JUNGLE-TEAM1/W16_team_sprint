from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from zipfile import ZipFile

from sqlalchemy.orm import Session

from backend.app.models.knowledge import KNOWLEDGE_STATUS_COMPLETED, KnowledgeChunk, KnowledgeDocument
from backend.app.repositories.knowledge_repository import KnowledgeRepository
from backend.app.services.embedding_service import EmbeddingProvider
from backend.app.services.knowledge_rag_index import KnowledgeVectorIndex

AIHUB_DATASET_NAME = "aihub_pet_care"
SOURCE_KIND_QA = "qa"
SOURCE_KIND_CORPUS = "corpus"


@dataclass(frozen=True)
class AihubDocumentPayload:
    source_kind: str
    split: str
    department: str | None
    disease: str | None
    life_cycle: str | None
    title: str
    source_path: str
    source_file: str
    source_entry: str
    source_external_id: str
    content_hash: str
    metadata: dict[str, Any]
    chunks: list["AihubChunkPayload"]


@dataclass(frozen=True)
class AihubChunkPayload:
    chunk_index: int
    source_kind: str
    split: str
    department: str | None
    disease: str | None
    life_cycle: str | None
    title: str
    question: str | None
    answer: str | None
    content: str
    content_hash: str
    metadata: dict[str, Any]


@dataclass
class AihubImportStats:
    documents_created: int = 0
    documents_updated: int = 0
    documents_skipped: int = 0
    chunks_created: int = 0
    chunks_embedded: int = 0
    chunks_failed: int = 0
    chunks_skipped: int = 0
    chunks_reindexed: int = 0


AihubProgressCallback = Callable[[int, int, AihubImportStats], None]


class AihubPetCareParser:
    def __init__(
        self,
        root_dir: Path,
        chunk_size: int = 1800,
        chunk_overlap: int = 200,
    ) -> None:
        self.root_dir = root_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def iter_documents(self) -> list[AihubDocumentPayload]:
        documents: list[AihubDocumentPayload] = []
        for zip_path in sorted(self.root_dir.rglob("*.zip")):
            documents.extend(self._iter_zip_documents(zip_path))
        return documents

    def _iter_zip_documents(self, zip_path: Path) -> list[AihubDocumentPayload]:
        documents: list[AihubDocumentPayload] = []
        with ZipFile(zip_path) as archive:
            for entry in sorted(name for name in archive.namelist() if name.endswith(".json")):
                with archive.open(entry) as file:
                    data = json.loads(file.read().decode("utf-8-sig"))
                documents.append(self._parse_json(zip_path, entry, data))
        return documents

    def _parse_json(self, zip_path: Path, entry: str, data: dict[str, Any]) -> AihubDocumentPayload:
        relative_zip_path = self._relative_path(zip_path)
        source_kind = self._source_kind(zip_path)
        split = self._split(zip_path)
        source_external_id = self._source_external_id(relative_zip_path, entry)

        if source_kind == SOURCE_KIND_QA:
            return self._parse_qa(
                zip_path=zip_path,
                relative_zip_path=relative_zip_path,
                entry=entry,
                source_external_id=source_external_id,
                split=split,
                data=data,
            )
        return self._parse_corpus(
            zip_path=zip_path,
            relative_zip_path=relative_zip_path,
            entry=entry,
            source_external_id=source_external_id,
            split=split,
            data=data,
        )

    def _parse_qa(
        self,
        zip_path: Path,
        relative_zip_path: str,
        entry: str,
        source_external_id: str,
        split: str,
        data: dict[str, Any],
    ) -> AihubDocumentPayload:
        meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
        qa = data.get("qa") if isinstance(data.get("qa"), dict) else {}
        question = str(qa.get("input") or "").strip()
        answer = str(qa.get("output") or "").strip()
        department = self._optional_text(meta.get("department"))
        disease = self._optional_text(meta.get("disease"))
        life_cycle = self._optional_text(meta.get("lifeCycle"))
        title = self._compact_title(question or disease or "반려견 질의응답")
        content = "\n".join(
            [
                f"진료과: {department or ''}",
                f"생애주기: {life_cycle or ''}",
                f"질환/주제: {disease or ''}",
                f"질문: {question}",
                f"답변: {answer}",
            ]
        ).strip()
        content_hash = self._hash(content)
        metadata = {
            "dataset": AIHUB_DATASET_NAME,
            "zip_path": relative_zip_path,
            "entry": entry,
            "instruction": qa.get("instruction"),
        }
        chunk = AihubChunkPayload(
            chunk_index=0,
            source_kind=SOURCE_KIND_QA,
            split=split,
            department=department,
            disease=disease,
            life_cycle=life_cycle,
            title=title,
            question=question,
            answer=answer,
            content=content,
            content_hash=content_hash,
            metadata=metadata,
        )
        return AihubDocumentPayload(
            source_kind=SOURCE_KIND_QA,
            split=split,
            department=department,
            disease=disease,
            life_cycle=life_cycle,
            title=title,
            source_path=str(zip_path),
            source_file=zip_path.name,
            source_entry=entry,
            source_external_id=source_external_id,
            content_hash=content_hash,
            metadata=metadata,
            chunks=[chunk],
        )

    def _parse_corpus(
        self,
        zip_path: Path,
        relative_zip_path: str,
        entry: str,
        source_external_id: str,
        split: str,
        data: dict[str, Any],
    ) -> AihubDocumentPayload:
        title = self._compact_title(str(data.get("title") or "반려견 말뭉치"))
        department = self._optional_text(data.get("department"))
        disease = self._optional_text(data.get("title"))
        body = str(data.get("disease") or "").strip()
        metadata = {
            "dataset": AIHUB_DATASET_NAME,
            "zip_path": relative_zip_path,
            "entry": entry,
            "author": data.get("author"),
            "publisher": data.get("publisher"),
        }
        chunks = [
            AihubChunkPayload(
                chunk_index=index,
                source_kind=SOURCE_KIND_CORPUS,
                split=split,
                department=department,
                disease=disease,
                life_cycle=None,
                title=title,
                question=None,
                answer=None,
                content=chunk_text,
                content_hash=self._hash(chunk_text),
                metadata={**metadata, "chunk_index": index},
            )
            for index, chunk_text in enumerate(self._split_text(body))
        ]
        content_hash = self._hash(body)
        return AihubDocumentPayload(
            source_kind=SOURCE_KIND_CORPUS,
            split=split,
            department=department,
            disease=disease,
            life_cycle=None,
            title=title,
            source_path=str(zip_path),
            source_file=zip_path.name,
            source_entry=entry,
            source_external_id=source_external_id,
            content_hash=content_hash,
            metadata=metadata,
            chunks=chunks,
        )

    def _split_text(self, text: str) -> list[str]:
        normalized = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        if not normalized:
            return []
        chunks: list[str] = []
        start = 0
        while start < len(normalized):
            end = min(len(normalized), start + self.chunk_size)
            chunk = normalized[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= len(normalized):
                break
            start = max(0, end - self.chunk_overlap)
        return chunks

    def _relative_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root_dir))
        except ValueError:
            return str(path)

    def _source_kind(self, zip_path: Path) -> str:
        path_text = str(zip_path)
        if "질의응답" in path_text or "라벨링" in path_text:
            return SOURCE_KIND_QA
        return SOURCE_KIND_CORPUS

    @staticmethod
    def _split(zip_path: Path) -> str:
        path_parts = set(zip_path.parts)
        if "Validation" in path_parts:
            return "Validation"
        return "Training"

    @staticmethod
    def _source_external_id(relative_zip_path: str, entry: str) -> str:
        return hashlib.sha256(f"{relative_zip_path}:{entry}".encode("utf-8")).hexdigest()

    @staticmethod
    def _hash(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    @staticmethod
    def _optional_text(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _compact_title(value: str, limit: int = 120) -> str:
        compact = " ".join(value.split()).strip()
        if len(compact) <= limit:
            return compact or "반려견 케어 문서"
        return compact[:limit].rsplit(" ", 1)[0].strip() or compact[:limit]


class AihubPetCareImportService:
    def __init__(
        self,
        db: Session,
        repository: KnowledgeRepository,
        embedding_provider: EmbeddingProvider | None = None,
        rag_index: KnowledgeVectorIndex | None = None,
    ) -> None:
        self.db = db
        self.repository = repository
        self.embedding_provider = embedding_provider
        self.rag_index = rag_index

    def import_dir(
        self,
        root_dir: Path,
        limit: int | None = None,
        commit_interval: int = 100,
        embedding_batch_size: int = 64,
        progress_interval: int | None = None,
        progress_callback: AihubProgressCallback | None = None,
    ) -> AihubImportStats:
        parser = AihubPetCareParser(root_dir)
        stats = AihubImportStats()
        documents = parser.iter_documents()
        if limit is not None:
            documents = documents[:limit]

        total = len(documents)
        pending_embedding_chunks: list[KnowledgeChunk] = []
        for index, payload in enumerate(documents, start=1):
            pending_embedding_chunks.extend(self._import_document(payload, stats))
            if embedding_batch_size > 0 and len(pending_embedding_chunks) >= embedding_batch_size:
                self._sync_embedding_batch(pending_embedding_chunks, stats)
                pending_embedding_chunks = []
            if commit_interval > 0 and index % commit_interval == 0:
                if pending_embedding_chunks:
                    self._sync_embedding_batch(pending_embedding_chunks, stats)
                    pending_embedding_chunks = []
                self.db.commit()
            if (
                progress_callback is not None
                and progress_interval is not None
                and progress_interval > 0
                and index % progress_interval == 0
            ):
                progress_callback(index, total, stats)
        if pending_embedding_chunks:
            self._sync_embedding_batch(pending_embedding_chunks, stats)
        self.db.commit()
        if progress_callback is not None:
            progress_callback(total, total, stats)
        return stats

    def _import_document(self, payload: AihubDocumentPayload, stats: AihubImportStats) -> list[KnowledgeChunk]:
        existing = self.repository.get_document_by_external_id(payload.source_external_id)
        if existing is not None and existing.content_hash == payload.content_hash:
            stats.documents_skipped += 1
            return self._sync_existing_chunks(existing, stats)

        document = existing or KnowledgeDocument(
            source_dataset=AIHUB_DATASET_NAME,
            source_kind=payload.source_kind,
            split=payload.split,
            department=payload.department,
            disease=payload.disease,
            life_cycle=payload.life_cycle,
            title=payload.title,
            source_path=payload.source_path,
            source_file=payload.source_file,
            source_entry=payload.source_entry,
            source_external_id=payload.source_external_id,
            content_hash=payload.content_hash,
            document_metadata=payload.metadata,
        )
        document.source_kind = payload.source_kind
        document.split = payload.split
        document.department = payload.department
        document.disease = payload.disease
        document.life_cycle = payload.life_cycle
        document.title = payload.title
        document.source_path = payload.source_path
        document.source_file = payload.source_file
        document.source_entry = payload.source_entry
        document.content_hash = payload.content_hash
        document.document_metadata = payload.metadata
        self.repository.save_document(document)

        chunks = [
            KnowledgeChunk(
                document_id=document.id,
                chunk_index=chunk.chunk_index,
                source_kind=chunk.source_kind,
                split=chunk.split,
                department=chunk.department,
                disease=chunk.disease,
                life_cycle=chunk.life_cycle,
                title=chunk.title,
                question=chunk.question,
                answer=chunk.answer,
                content=chunk.content,
                content_hash=chunk.content_hash,
                chunk_metadata=chunk.metadata,
            )
            for chunk in payload.chunks
        ]
        saved_chunks = self.repository.replace_chunks(document, chunks)
        stats.chunks_created += len(saved_chunks)
        if existing is None:
            stats.documents_created += 1
        else:
            stats.documents_updated += 1

        return saved_chunks

    def _sync_existing_chunks(self, document: KnowledgeDocument, stats: AihubImportStats) -> list[KnowledgeChunk]:
        if self.embedding_provider is None:
            stats.chunks_skipped += len(document.chunks)
            return []

        pending_chunks: list[KnowledgeChunk] = []
        for chunk in sorted(document.chunks, key=lambda item: item.chunk_index):
            if chunk.status == KNOWLEDGE_STATUS_COMPLETED and chunk.embedding is not None:
                self._reindex_completed_chunk(chunk, stats)
                continue
            pending_chunks.append(chunk)
        return pending_chunks

    def _sync_embedding_batch(self, chunks: list[KnowledgeChunk], stats: AihubImportStats) -> None:
        if not chunks:
            return
        if self.embedding_provider is None:
            stats.chunks_skipped += len(chunks)
            return

        try:
            embeddings = self.embedding_provider.embed_documents([chunk.content for chunk in chunks])
            if len(embeddings) != len(chunks):
                raise ValueError(
                    f"embedding batch size mismatch: expected {len(chunks)}, got {len(embeddings)}"
                )
        except Exception:
            for chunk in chunks:
                self._sync_embedding(chunk, stats)
            return

        for chunk, embedding in zip(chunks, embeddings, strict=True):
            self._complete_chunk_embedding(chunk, embedding, stats)

    def _reindex_completed_chunk(self, chunk: KnowledgeChunk, stats: AihubImportStats) -> None:
        if self.rag_index is None or chunk.embedding is None:
            stats.chunks_skipped += 1
            return

        metadata = self._metadata_for_chunk(chunk)
        try:
            self.rag_index.upsert_chunk(chunk=chunk, embedding=chunk.embedding, metadata=metadata)
            stats.chunks_reindexed += 1
        except Exception as exc:
            self.repository.update_chunk_failed(chunk, error_message=str(exc), metadata=metadata)
            stats.chunks_failed += 1

    def _sync_embedding(self, chunk: KnowledgeChunk, stats: AihubImportStats) -> None:
        if self.embedding_provider is None:
            stats.chunks_skipped += 1
            return
        metadata = self._metadata_for_chunk(chunk)
        try:
            embedding = self.embedding_provider.embed_query(chunk.content)
            self._complete_chunk_embedding(chunk, embedding, stats)
        except Exception as exc:
            self.repository.update_chunk_failed(chunk, error_message=str(exc), metadata=metadata)
            stats.chunks_failed += 1

    def _complete_chunk_embedding(
        self,
        chunk: KnowledgeChunk,
        embedding: list[float],
        stats: AihubImportStats,
    ) -> None:
        metadata = self._metadata_for_chunk(chunk)
        try:
            self.repository.update_chunk_completed(chunk, embedding=embedding, metadata=metadata)
            if self.rag_index is not None:
                self.rag_index.upsert_chunk(chunk=chunk, embedding=embedding, metadata=metadata)
            stats.chunks_embedded += 1
        except Exception as exc:
            self.repository.update_chunk_failed(chunk, error_message=str(exc), metadata=metadata)
            stats.chunks_failed += 1

    @staticmethod
    def _metadata_for_chunk(chunk: KnowledgeChunk) -> dict[str, Any]:
        return {
            **chunk.chunk_metadata,
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "source_kind": chunk.source_kind,
            "split": chunk.split,
            "department": chunk.department,
            "disease": chunk.disease,
            "life_cycle": chunk.life_cycle,
        }
