from dataclasses import dataclass
import re

from app.models import AnnalsArticle


MAX_CHUNK_CHARS = 3000
MIN_BODY_CHARS = 800
SENTENCE_RE = re.compile(r"[^。]+。?")


@dataclass(frozen=True)
class ArticleChunk:
    chunk_id: str
    article_id: str
    chunk_index: int
    chunk_text: str
    token_count_estimate: int


def estimate_token_count(text: str) -> int:
    # This is only for rough cost/length tracking. The model does exact tokenization later.
    return max(1, len(text) // 2)


def build_chunk_prefix(article: AnnalsArticle) -> str:
    subject_text = ", ".join(article.subject_classes or [])
    parts = [
        f"제목: {article.title}",
        f"왕: {article.king or '미상'}",
        f"날짜: {article.date or article.reign_date or '미상'}",
    ]
    if subject_text:
        parts.append(f"분류: {subject_text}")
    return "\n".join(parts)


def build_chunk_text(article: AnnalsArticle, content: str | None = None) -> str:
    return f"{build_chunk_prefix(article)}\n원문: {content if content is not None else article.content}"


def split_content(content: str, body_limit: int) -> list[str]:
    if len(content) <= body_limit:
        return [content]

    chunks: list[str] = []
    current = ""
    sentences = [match.group(0).strip() for match in SENTENCE_RE.finditer(content) if match.group(0).strip()]
    if not sentences:
        sentences = [content]

    for sentence in sentences:
        if len(sentence) > body_limit:
            if current:
                chunks.append(current.strip())
                current = ""
            for start in range(0, len(sentence), body_limit):
                chunks.append(sentence[start : start + body_limit].strip())
            continue

        candidate = f"{current} {sentence}".strip() if current else sentence
        if len(candidate) > body_limit:
            chunks.append(current.strip())
            current = sentence
        else:
            current = candidate

    if current:
        chunks.append(current.strip())
    return [chunk for chunk in chunks if chunk]


def chunk_article(article: AnnalsArticle) -> list[ArticleChunk]:
    prefix = build_chunk_prefix(article)
    body_limit = max(MIN_BODY_CHARS, MAX_CHUNK_CHARS - len(prefix) - len("\n원문: "))
    content_chunks = split_content(article.content, body_limit)

    return [
        ArticleChunk(
            chunk_id=f"{article.article_id}_{index}",
            article_id=article.article_id,
            chunk_index=index,
            chunk_text=build_chunk_text(article, content),
            token_count_estimate=estimate_token_count(build_chunk_text(article, content)),
        )
        for index, content in enumerate(content_chunks)
    ]
