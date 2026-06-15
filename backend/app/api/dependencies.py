from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.repositories.comment_repository import CommentRepository
from backend.app.repositories.post_repository import PostRepository
from backend.app.repositories.tag_repository import TagRepository
from backend.app.services.comment_service import CommentService
from backend.app.services.post_service import PostService


def get_post_service(db: Session = Depends(get_db)) -> PostService:
    posts = PostRepository(db)
    tags = TagRepository(db)
    return PostService(db=db, posts=posts, tags=tags)


def get_comment_service(db: Session = Depends(get_db)) -> CommentService:
    posts = PostRepository(db)
    comments = CommentRepository(db)
    return CommentService(db=db, posts=posts, comments=comments)
