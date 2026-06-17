from dataclasses import dataclass
import re

from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import AnnalsArticle, AnnalsChunk
from app.services.embeddings import embed_texts
from app.services.query_filters import SearchFilters, build_retrieval_query, extract_search_filters


KEYWORD_STOPWORDS = {
    "관련",
    "자료",
    "기록",
    "찾아줘",
    "찾아",
    "알려줘",
    "알려",
    "정리해줘",
    "정리",
    "설명해줘",
    "설명",
    "요약해줘",
    "요약",
    "대한",
    "대해",
}
IMPORTANT_ONE_CHAR_KEYWORDS = {"난"}
PARTICLES = ("으로", "에서", "에게", "한테", "부터", "까지", "처럼", "보다", "의", "이", "가", "은", "는", "을", "를", "에", "와", "과", "로")


@dataclass(frozen=True)
class RankedHit:
    article_id: str
    score: float


def tokenize_query(query: str) -> list[str]:
    raw_tokens = re.findall(r"[0-9A-Za-z가-힣一-龥]+", query)
    tokens: list[str] = []
    seen = set()
    for raw_token in raw_tokens:
        for token in _token_candidates(raw_token):
            if token in KEYWORD_STOPWORDS or token in seen:
                continue
            if len(token) >= 2 or token in IMPORTANT_ONE_CHAR_KEYWORDS:
                tokens.append(token)
                seen.add(token)
    return tokens[:10]


def _token_candidates(token: str) -> list[str]:
    candidates = [token]
    for particle in PARTICLES:
        if token.endswith(particle) and len(token) > len(particle) + 1:
            candidates.append(token[: -len(particle)])
            break
    return candidates


def _keyword_phrases(query: str) -> list[str]:
    raw_tokens = re.findall(r"[0-9A-Za-z가-힣一-龥]+", query)
    meaningful_tokens = []
    for token in raw_tokens:
        if token in KEYWORD_STOPWORDS:
            continue
        if len(token) >= 2 or token in IMPORTANT_ONE_CHAR_KEYWORDS:
            meaningful_tokens.append(token)

    phrases = []
    if len(meaningful_tokens) >= 2:
        phrases.append(" ".join(meaningful_tokens[:4]))
    return phrases[:2]


def _score_article(article: AnnalsArticle, terms: list[str], phrases: list[str] | None = None) -> int:
    phrases = phrases or []
    title = article.title.lower()
    content = article.content.lower()
    subjects = " ".join(article.subject_classes or []).lower()
    score = 0
    for phrase in phrases:
        lowered_phrase = phrase.lower()
        if lowered_phrase in title:
            score += 120
        if lowered_phrase in content:
            score += 30 * content.count(lowered_phrase)
        if lowered_phrase in subjects:
            score += 20

    for term in terms:
        lowered = term.lower()
        if lowered in title:
            score += 20
        if lowered in content:
            score += min(content.count(lowered), 10)
        if lowered in subjects:
            score += 10
    return score


def _vector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(str(number) for number in embedding) + "]"


def _has_vector_chunks(db: Session, embedding_model: str) -> bool:
    return bool(
        db.scalar(
            select(func.count(AnnalsChunk.id)).where(AnnalsChunk.embedding_model == embedding_model).limit(1)
        )
    )


def _metadata_where(filters: SearchFilters, table_alias: str = "a") -> tuple[list[str], dict]:
    where_clauses: list[str] = []
    params: dict = {}
    if filters.king:
        where_clauses.append(f"{table_alias}.king = :king")
        params["king"] = filters.king
    if filters.source_file:
        where_clauses.append(f"{table_alias}.source_file = :source_file")
        params["source_file"] = filters.source_file
    return where_clauses, params


def _articles_by_ids(db: Session, article_ids: list[str]) -> list[AnnalsArticle]:
    if not article_ids:
        return []
    articles = list(db.scalars(select(AnnalsArticle).where(AnnalsArticle.article_id.in_(article_ids))))
    articles_by_id = {article.article_id: article for article in articles}
    return [articles_by_id[article_id] for article_id in article_ids if article_id in articles_by_id]


def _rank_vector_articles(
    db: Session,
    query: str,
    limit: int,
    filters: SearchFilters,
) -> list[RankedHit]:
    embedding = embed_texts([query])[0]
    filter_clauses, filter_params = _metadata_where(filters)
    where_sql = " AND ".join(["c.embedding_model = :embedding_model", *filter_clauses])
    rows = list(
        db.execute(
            text(
                f"""
                SELECT article_id, distance
                FROM (
                    SELECT
                        c.article_id,
                        MIN(c.embedding <=> CAST(:embedding AS vector)) AS distance
                    FROM annals_chunks c
                    JOIN annals_articles a ON a.article_id = c.article_id
                    WHERE {where_sql}
                    GROUP BY c.article_id
                    ORDER BY distance
                    LIMIT :limit
                ) ranked
                ORDER BY distance
                """
            ),
            {
                "embedding": _vector_literal(embedding),
                "embedding_model": get_settings().openai_embedding_model,
                "limit": limit,
                **filter_params,
            },
        ).mappings()
    )
    return [
        RankedHit(article_id=row["article_id"], score=max(0.0, 1.0 - float(row["distance"])))
        for row in rows
    ]


def search_annals_articles_by_vector(
    db: Session,
    query: str,
    limit: int = 3,
    filters: SearchFilters | None = None,
) -> list[AnnalsArticle]:
    filters = filters or SearchFilters()
    ranked_hits = _rank_vector_articles(db, query, limit, filters)
    return _articles_by_ids(db, [hit.article_id for hit in ranked_hits])


def _rank_keyword_articles(
    db: Session,
    query: str,
    limit: int,
    filters: SearchFilters,
) -> list[RankedHit]:
    terms = tokenize_query(query)
    phrases = _keyword_phrases(query)

    conditions = []
    if filters.king:
        conditions.append(AnnalsArticle.king == filters.king)
    if filters.source_file:
        conditions.append(AnnalsArticle.source_file == filters.source_file)

    if not terms and not phrases:
        return []

    keyword_conditions = []
    for phrase in phrases:
        like_phrase = f"%{phrase}%"
        keyword_conditions.append(AnnalsArticle.title.ilike(like_phrase))
        keyword_conditions.append(AnnalsArticle.content.ilike(like_phrase))
    for term in terms:
        like_term = f"%{term}%"
        keyword_conditions.append(AnnalsArticle.title.ilike(like_term))
        keyword_conditions.append(AnnalsArticle.content.ilike(like_term))

    statement = select(AnnalsArticle).where(*conditions, or_(*keyword_conditions)).limit(max(limit * 80, 200))
    candidates = list(db.scalars(statement))
    scored_candidates = [
        RankedHit(article_id=article.article_id, score=min(_score_article(article, terms, phrases) / 100, 2.0))
        for article in candidates
    ]
    scored_candidates = [hit for hit in scored_candidates if hit.score > 0]
    scored_candidates.sort(key=lambda hit: hit.score, reverse=True)
    return scored_candidates[:limit]


def search_annals_articles_by_keyword(
    db: Session,
    query: str,
    limit: int = 3,
    filters: SearchFilters | None = None,
) -> list[AnnalsArticle]:
    filters = filters or SearchFilters()
    ranked_hits = _rank_keyword_articles(db, query, limit, filters)
    return _articles_by_ids(db, [hit.article_id for hit in ranked_hits])


def _merge_ranked_hits(vector_hits: list[RankedHit], keyword_hits: list[RankedHit], limit: int) -> list[str]:
    scores: dict[str, float] = {}
    for hit in vector_hits:
        scores[hit.article_id] = scores.get(hit.article_id, 0.0) + hit.score
    for hit in keyword_hits:
        scores[hit.article_id] = scores.get(hit.article_id, 0.0) + hit.score

    ranked_article_ids = sorted(scores, key=lambda article_id: scores[article_id], reverse=True)
    return ranked_article_ids[:limit]


def search_annals_articles(db: Session, query: str, limit: int = 3) -> list[AnnalsArticle]:
    settings = get_settings()
    filters = extract_search_filters(query)
    retrieval_query = build_retrieval_query(query, filters)
    candidate_limit = max(limit * 5, 20)

    vector_hits: list[RankedHit] = []
    if settings.openai_api_key and _has_vector_chunks(db, settings.openai_embedding_model):
        try:
            vector_hits = _rank_vector_articles(db, retrieval_query, candidate_limit, filters)
        except Exception:
            pass

    keyword_hits = _rank_keyword_articles(db, retrieval_query, candidate_limit, filters)
    ranked_article_ids = _merge_ranked_hits(vector_hits, keyword_hits, limit)
    return _articles_by_ids(db, ranked_article_ids)
