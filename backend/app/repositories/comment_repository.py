from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from backend.app.models.comment import Comment


class CommentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, comment: Comment) -> Comment:
        self.db.add(comment)
        self.db.flush()
        self.db.refresh(comment)
        return comment

    def list_by_post(self, post_id: int) -> list[Comment]:
        statement = (
            select(Comment)
            .options(joinedload(Comment.author))
            .where(Comment.post_id == post_id)
            .order_by(Comment.created_at.asc())
        )
        return list(self.db.scalars(statement))

    def get(self, comment_id: int) -> Comment | None:
        statement = select(Comment).options(joinedload(Comment.author)).where(Comment.id == comment_id)
        return self.db.scalars(statement).first()

    def delete(self, comment: Comment) -> None:
        self.db.delete(comment)
