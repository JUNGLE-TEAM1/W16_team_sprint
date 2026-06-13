from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.repositories.post_repository import PostRepository
from backend.app.services.post_service import PostService


def get_post_service(db: Session = Depends(get_db)) -> PostService:
    posts = PostRepository(db)
    return PostService(db=db, posts=posts)
