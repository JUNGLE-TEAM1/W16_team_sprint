from __future__ import annotations

from langchain_core.documents import Document
from langchain_postgres import PGVector
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.knowledge import KnowledgeChunk
from backend.app.repositories.knowledge_repository import KnowledgeRepository, KnowledgeSearchRow
from backend.app.services.embedding_service import EmbeddingProvider, as_langchain_embeddings


class KnowledgeVectorIndex:
    def __init__(
        self,
        db: Session,
        embedding_provider: EmbeddingProvider,
        connection: str = settings.database_url,
        collection_name: str = settings.pet_care_rag_collection_name,
    ) -> None:
        self.db = db
        self.embedding_provider = embedding_provider
        self.connection = connection
        self.collection_name = collection_name
        self._vector_store: PGVector | None = None

    def upsert_chunk(
        self,
        chunk: KnowledgeChunk,
        embedding: list[float],
        metadata: dict,
    ) -> None:
        document = self._build_document(chunk, metadata)
        self._store().add_embeddings(
            texts=[document.page_content],
            embeddings=[embedding],
            metadatas=[document.metadata],
            ids=[self._document_id(chunk.id)],
        )

    def find_related_chunks(
        self,
        query_text: str,
        repository: KnowledgeRepository,
        limit: int,
        min_similarity: float,
    ) -> list[KnowledgeSearchRow]:
        results = self._store().similarity_search_with_score(
            query=query_text,
            k=max(limit * 5, 10),
        )
        scored_chunk_ids: list[tuple[int, float]] = []
        seen_chunk_ids: set[int] = set()
        for document, score in results:
            chunk_id = self._metadata_chunk_id(document.metadata)
            if chunk_id is None or chunk_id in seen_chunk_ids:
                continue
            similarity = round(self._distance_to_similarity(float(score)), 6)
            if similarity < min_similarity:
                continue
            scored_chunk_ids.append((chunk_id, similarity))
            seen_chunk_ids.add(chunk_id)
        return repository.hydrate_search_rows(scored_chunk_ids, limit)

    def _store(self) -> PGVector:
        if self._vector_store is None:
            self._vector_store = PGVector(
                embeddings=as_langchain_embeddings(self.embedding_provider),
                connection=self.connection,
                collection_name=self.collection_name,
                use_jsonb=True,
            )
        return self._vector_store

    @staticmethod
    def _build_document(chunk: KnowledgeChunk, metadata: dict) -> Document:
        return Document(
            page_content=chunk.content,
            metadata={
                **metadata,
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "title": chunk.title,
                "source_kind": chunk.source_kind,
                "split": chunk.split,
                "department": chunk.department,
                "disease": chunk.disease,
                "life_cycle": chunk.life_cycle,
            },
        )

    @staticmethod
    def _document_id(chunk_id: int) -> str:
        return f"knowledge:{chunk_id}"

    @staticmethod
    def _metadata_chunk_id(metadata: dict) -> int | None:
        value = metadata.get("chunk_id")
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return None

    @staticmethod
    def _distance_to_similarity(distance: float) -> float:
        return max(0.0, min(1.0, 1.0 - distance))
