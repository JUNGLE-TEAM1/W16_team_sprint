from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.repositories.post_repository import PostRepository
from backend.app.services.post_service import PostService


def get_post_repository(db: Annotated[Session, Depends(get_db)]) -> PostRepository:
    return PostRepository(db)


def get_post_service(
    posts: Annotated[PostRepository, Depends(get_post_repository)],
    unit_of_work: Annotated[Session, Depends(get_db)],
) -> PostService:
    return PostService(posts=posts, unit_of_work=unit_of_work)


PostServiceDependency = Annotated[PostService, Depends(get_post_service)]
