from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.repositories.comment_repository import CommentRepository
from backend.app.repositories.post_embedding_repository import PostEmbeddingRepository
from backend.app.repositories.post_repository import PostRepository
from backend.app.services.comment_service import CommentService
from backend.app.services.embedding_provider import EmbeddingProvider, LocalSentenceTransformerEmbeddingProvider
from backend.app.services.post_service import PostService
from backend.app.services.rag_service import RagService
from backend.app.services.summary_provider import OllamaSummaryProvider, SummaryProvider


def get_comment_repository(db: Annotated[Session, Depends(get_db)]) -> CommentRepository:
    return CommentRepository(db)


def get_post_repository(db: Annotated[Session, Depends(get_db)]) -> PostRepository:
    return PostRepository(db)


def get_post_embedding_repository(db: Annotated[Session, Depends(get_db)]) -> PostEmbeddingRepository:
    return PostEmbeddingRepository(db)


def get_embedding_provider() -> EmbeddingProvider:
    return LocalSentenceTransformerEmbeddingProvider()


def get_summary_provider() -> SummaryProvider:
    return OllamaSummaryProvider()


def get_post_service(
    posts: Annotated[PostRepository, Depends(get_post_repository)],
    embeddings: Annotated[PostEmbeddingRepository, Depends(get_post_embedding_repository)],
    embedding_provider: Annotated[EmbeddingProvider, Depends(get_embedding_provider)],
    unit_of_work: Annotated[Session, Depends(get_db)],
) -> PostService:
    return PostService(
        posts=posts,
        embeddings=embeddings,
        embedding_provider=embedding_provider,
        unit_of_work=unit_of_work,
    )


def get_comment_service(
    comments: Annotated[CommentRepository, Depends(get_comment_repository)],
    posts: Annotated[PostRepository, Depends(get_post_repository)],
    unit_of_work: Annotated[Session, Depends(get_db)],
) -> CommentService:
    return CommentService(comments=comments, posts=posts, unit_of_work=unit_of_work)


def get_rag_service(
    embeddings: Annotated[PostEmbeddingRepository, Depends(get_post_embedding_repository)],
    embedding_provider: Annotated[EmbeddingProvider, Depends(get_embedding_provider)],
    summary_provider: Annotated[SummaryProvider, Depends(get_summary_provider)],
) -> RagService:
    return RagService(
        embeddings=embeddings,
        embedding_provider=embedding_provider,
        summary_provider=summary_provider,
    )


CommentServiceDependency = Annotated[CommentService, Depends(get_comment_service)]
PostServiceDependency = Annotated[PostService, Depends(get_post_service)]
RagServiceDependency = Annotated[RagService, Depends(get_rag_service)]
