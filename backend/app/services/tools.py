from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AnnalsArticle


def get_annals_article(db: Session, article_id: str) -> AnnalsArticle | None:
    return db.scalar(select(AnnalsArticle).where(AnnalsArticle.article_id == article_id))


def article_to_tool_payload(article: AnnalsArticle) -> dict:
    return {
        "article_id": article.article_id,
        "title": article.title,
        "king": article.king,
        "reign_date": article.reign_date,
        "date": article.date,
        "content": article.content,
        "official_url": article.official_url,
        "subject_classes": article.subject_classes,
    }
