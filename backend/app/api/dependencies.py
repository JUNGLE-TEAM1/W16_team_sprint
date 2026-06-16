from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.repositories.comment_repository import CommentRepository
from backend.app.repositories.post_embedding_repository import PostEmbeddingRepository
from backend.app.repositories.post_repository import PostRepository
from backend.app.repositories.tag_repository import TagRepository
from backend.app.services.agent_service import AgentService
from backend.app.services.comment_service import CommentService
from backend.app.services.post_service import PostService
from backend.app.services.rag_service import RagService
from backend.app.services.tag_service import TagService


def get_comment_repository(db: Annotated[Session, Depends(get_db)]) -> CommentRepository:
    return CommentRepository(db)


def get_post_repository(db: Annotated[Session, Depends(get_db)]) -> PostRepository:
    return PostRepository(db)


def get_post_embedding_repository(
    db: Annotated[Session, Depends(get_db)],
) -> PostEmbeddingRepository:
    return PostEmbeddingRepository(db)


def get_tag_repository(db: Annotated[Session, Depends(get_db)]) -> TagRepository:
    return TagRepository(db)


def get_post_service(
    posts: Annotated[PostRepository, Depends(get_post_repository)],
    tags: Annotated[TagRepository, Depends(get_tag_repository)],
    embeddings: Annotated[PostEmbeddingRepository, Depends(get_post_embedding_repository)],
    unit_of_work: Annotated[Session, Depends(get_db)],
) -> PostService:
    return PostService(posts=posts, tags=tags, embeddings=embeddings, unit_of_work=unit_of_work)


def get_comment_service(
    comments: Annotated[CommentRepository, Depends(get_comment_repository)],
    posts: Annotated[PostRepository, Depends(get_post_repository)],
    unit_of_work: Annotated[Session, Depends(get_db)],
) -> CommentService:
    return CommentService(comments=comments, posts=posts, unit_of_work=unit_of_work)


def get_tag_service(tags: Annotated[TagRepository, Depends(get_tag_repository)]) -> TagService:
    return TagService(tags=tags)


def get_agent_service() -> AgentService:
    return AgentService()


def get_rag_service(
    posts: Annotated[PostRepository, Depends(get_post_repository)],
    embeddings: Annotated[PostEmbeddingRepository, Depends(get_post_embedding_repository)],
    unit_of_work: Annotated[Session, Depends(get_db)],
) -> RagService:
    return RagService(posts=posts, embeddings=embeddings, unit_of_work=unit_of_work)


PostServiceDependency = Annotated[PostService, Depends(get_post_service)]
CommentServiceDependency = Annotated[CommentService, Depends(get_comment_service)]
TagServiceDependency = Annotated[TagService, Depends(get_tag_service)]
AgentServiceDependency = Annotated[AgentService, Depends(get_agent_service)]
RagServiceDependency = Annotated[RagService, Depends(get_rag_service)]
