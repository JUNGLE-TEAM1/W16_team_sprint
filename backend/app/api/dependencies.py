from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.repositories.comment_repository import CommentRepository
from backend.app.repositories.embedding_repository import PostEmbeddingRepository
from backend.app.repositories.post_repository import PostRepository
from backend.app.repositories.tag_repository import TagRepository
from backend.app.services.comment_service import CommentService
from backend.app.services.embedding_service import EmbeddingProvider, OpenAIEmbeddingProvider, PostEmbeddingService
from backend.app.services.post_service import PostService


def get_embedding_provider() -> EmbeddingProvider:
    return OpenAIEmbeddingProvider()


def get_post_service(
    db: Session = Depends(get_db),
    embedding_provider: EmbeddingProvider = Depends(get_embedding_provider),
) -> PostService:
    posts = PostRepository(db)
    tags = TagRepository(db)
    embeddings = PostEmbeddingRepository(db)
    embedding_service = PostEmbeddingService(embedding_provider)
    return PostService(
        db=db,
        posts=posts,
        tags=tags,
        embeddings=embeddings,
        embedding_service=embedding_service,
    )


def get_comment_service(db: Session = Depends(get_db)) -> CommentService:
    posts = PostRepository(db)
    comments = CommentRepository(db)
    return CommentService(db=db, posts=posts, comments=comments)
