from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from backend.app.models.comment import Comment
from backend.app.models.post import Post
from backend.app.models.tag import Tag
from backend.app.models.user import User
from backend.app.schemas.post import PostSearchType, PostSortType


class PostRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, post: Post) -> Post:
        self.db.add(post)
        self.db.flush()
        self.db.refresh(post)
        return post

    def list(
        self,
        q: str | None,
        search_type: PostSearchType,
        tag: str | None,
        sort: PostSortType,
        page: int,
        size: int,
    ) -> tuple[list[Post], int]:
        comment_count = self._comment_count_expression()
        statement = select(Post, comment_count.label("comment_count")).join(Post.author)
        count_statement = select(func.count(func.distinct(Post.id))).select_from(Post).join(Post.author)

        if tag:
            statement = statement.join(Post.tag_entities)
            count_statement = count_statement.join(Post.tag_entities)

        conditions = []
        if q:
            pattern = f"%{q}%"
            if search_type == PostSearchType.title:
                conditions.append(Post.title.ilike(pattern))
            elif search_type == PostSearchType.content:
                conditions.append(Post.content.ilike(pattern))
            elif search_type == PostSearchType.author:
                conditions.append(or_(User.username.ilike(pattern), User.display_name.ilike(pattern)))
            else:
                conditions.append(or_(Post.title.ilike(pattern), Post.content.ilike(pattern)))

        if tag:
            conditions.append(Tag.name == tag)

        if conditions:
            statement = statement.where(*conditions)
            count_statement = count_statement.where(*conditions)

        total = self.db.scalar(count_statement) or 0
        offset = (page - 1) * size
        statement = (
            statement.options(joinedload(Post.author), joinedload(Post.tag_entities))
            .order_by(*self._order_by(sort, comment_count))
            .offset(offset)
            .limit(size)
        )
        rows = self.db.execute(statement).unique().all()
        posts = []
        for post, comment_count_value in rows:
            post.comment_count = int(comment_count_value)
            posts.append(post)
        return posts, total

    def get(self, post_id: int) -> Post | None:
        comment_count = self._comment_count_expression()
        statement = (
            select(Post, comment_count.label("comment_count"))
            .options(joinedload(Post.author), joinedload(Post.tag_entities))
            .where(Post.id == post_id)
        )
        row = self.db.execute(statement).unique().first()
        if row is None:
            return None
        post, comment_count_value = row
        post.comment_count = int(comment_count_value)
        return post

    def delete(self, post: Post) -> None:
        self.db.delete(post)

    @staticmethod
    def _comment_count_expression():
        return (
            select(func.count(Comment.id))
            .where(Comment.post_id == Post.id)
            .correlate(Post)
            .scalar_subquery()
        )

    @staticmethod
    def _order_by(sort: PostSortType, comment_count):
        if sort == PostSortType.comment_count:
            return (comment_count.desc(), Post.created_at.desc(), Post.id.desc())
        if sort == PostSortType.like_count:
            return (Post.like_count.desc(), Post.created_at.desc(), Post.id.desc())
        return (Post.created_at.desc(), Post.id.desc())
