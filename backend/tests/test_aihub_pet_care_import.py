import json
from pathlib import Path
from zipfile import ZipFile

from sqlalchemy.orm import Session

from backend.app.db.session import engine
from backend.app.models.knowledge import KNOWLEDGE_STATUS_COMPLETED, KnowledgeChunk, KnowledgeDocument
from backend.app.repositories.knowledge_repository import KnowledgeRepository
from backend.app.services.aihub_pet_care_import_service import AihubPetCareImportService, AihubPetCareParser
from backend.app.services.embedding_service import MockEmbeddingProvider
from backend.app.services.knowledge_rag_index import KnowledgeVectorIndex
from backend.tests.db_reset import reset_app_data_only


def setup_function() -> None:
    reset_app_data_only(engine)


def write_sample_aihub_data(root: Path) -> Path:
    qa_dir = root / "Training" / "02.라벨링데이터"
    source_dir = root / "Validation" / "01.원천데이터"
    qa_dir.mkdir(parents=True)
    source_dir.mkdir(parents=True)

    with ZipFile(qa_dir / "TL_질의응답데이터_내과.zip", "w") as archive:
        archive.writestr(
            "qa-1.json",
            json.dumps(
                {
                    "meta": {
                        "lifeCycle": "자견",
                        "department": "내과",
                        "disease": "기관지염",
                    },
                    "qa": {
                        "instruction": "보호자 질문에 답해줘.",
                        "input": "5개월 강아지가 켁켁 기침을 해요.",
                        "output": "습도를 조절하고 처방 약을 먹이며 악화되면 병원에 상담하세요.",
                    },
                },
                ensure_ascii=False,
            ),
        )

    with ZipFile(source_dir / "VS_말뭉치데이터_내과.zip", "w") as archive:
        archive.writestr(
            "source-1.json",
            json.dumps(
                {
                    "title": "개의 기관지염 관리",
                    "author": "AIHub",
                    "publisher": "AIHub",
                    "department": "내과",
                    "disease": "기관지염은 기침과 호흡기 증상을 동반할 수 있습니다.\n"
                    "보호자는 습도, 식욕, 활력, 호흡 상태를 관찰해야 합니다.",
                },
                ensure_ascii=False,
            ),
        )
    return root


def sample_external_ids(data_dir: Path) -> list[str]:
    return [
        document.source_external_id
        for document in AihubPetCareParser(data_dir).iter_documents()
    ]


def delete_sample_knowledge(data_dir: Path) -> None:
    external_ids = sample_external_ids(data_dir)
    with Session(engine) as db:
        rows = (
            db.query(KnowledgeDocument)
            .filter(KnowledgeDocument.source_external_id.in_(external_ids))
            .all()
        )
        for row in rows:
            db.delete(row)
        db.commit()


def count_sample_documents(db: Session, data_dir: Path) -> int:
    return (
        db.query(KnowledgeDocument)
        .filter(KnowledgeDocument.source_external_id.in_(sample_external_ids(data_dir)))
        .count()
    )


def count_sample_chunks(db: Session, data_dir: Path, completed_only: bool = False) -> int:
    query = (
        db.query(KnowledgeChunk)
        .join(KnowledgeDocument)
        .filter(KnowledgeDocument.source_external_id.in_(sample_external_ids(data_dir)))
    )
    if completed_only:
        query = query.filter(KnowledgeChunk.status == KNOWLEDGE_STATUS_COMPLETED)
    return query.count()


def test_aihub_parser_reads_qa_and_source_zip_files(tmp_path: Path) -> None:
    data_dir = write_sample_aihub_data(tmp_path)
    documents = AihubPetCareParser(data_dir, chunk_size=80, chunk_overlap=10).iter_documents()

    assert len(documents) == 2
    qa_document = next(document for document in documents if document.source_kind == "qa")
    source_document = next(document for document in documents if document.source_kind == "corpus")

    assert qa_document.split == "Training"
    assert qa_document.department == "내과"
    assert qa_document.life_cycle == "자견"
    assert qa_document.chunks[0].question == "5개월 강아지가 켁켁 기침을 해요."
    assert "답변:" in qa_document.chunks[0].content

    assert source_document.split == "Validation"
    assert source_document.department == "내과"
    assert source_document.chunks
    assert all(chunk.source_kind == "corpus" for chunk in source_document.chunks)


def test_aihub_import_is_idempotent_and_embeds_chunks(tmp_path: Path) -> None:
    data_dir = write_sample_aihub_data(tmp_path)
    delete_sample_knowledge(data_dir)

    with Session(engine) as db:
        provider = MockEmbeddingProvider()
        service = AihubPetCareImportService(
            db=db,
            repository=KnowledgeRepository(db),
            embedding_provider=provider,
            rag_index=KnowledgeVectorIndex(db=db, embedding_provider=provider, collection_name="test_pet_care_import"),
        )

        first_stats = service.import_dir(data_dir)
        second_stats = service.import_dir(data_dir)

    assert first_stats.documents_created == 2
    assert first_stats.chunks_created >= 2
    assert first_stats.chunks_embedded == first_stats.chunks_created
    assert second_stats.documents_skipped == 2

    with Session(engine) as db:
        assert count_sample_documents(db, data_dir) == 2
        assert count_sample_chunks(db, data_dir) == first_stats.chunks_created
        assert count_sample_chunks(db, data_dir, completed_only=True) == first_stats.chunks_created


def test_aihub_import_retries_existing_pending_chunks(tmp_path: Path) -> None:
    data_dir = write_sample_aihub_data(tmp_path)
    delete_sample_knowledge(data_dir)

    with Session(engine) as db:
        without_embeddings = AihubPetCareImportService(
            db=db,
            repository=KnowledgeRepository(db),
        )
        first_stats = without_embeddings.import_dir(data_dir)

    assert first_stats.documents_created == 2
    assert first_stats.chunks_created >= 2
    assert first_stats.chunks_skipped == first_stats.chunks_created

    with Session(engine) as db:
        provider = MockEmbeddingProvider()
        with_embeddings = AihubPetCareImportService(
            db=db,
            repository=KnowledgeRepository(db),
            embedding_provider=provider,
            rag_index=KnowledgeVectorIndex(db=db, embedding_provider=provider, collection_name="test_pet_care_retry"),
        )
        second_stats = with_embeddings.import_dir(data_dir)

    assert second_stats.documents_skipped == 2
    assert second_stats.chunks_embedded == first_stats.chunks_created
    assert second_stats.chunks_created == 0

    with Session(engine) as db:
        assert count_sample_documents(db, data_dir) == 2
        assert count_sample_chunks(db, data_dir) == first_stats.chunks_created
        assert count_sample_chunks(db, data_dir, completed_only=True) == first_stats.chunks_created
