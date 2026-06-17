from sqlalchemy.orm import Session

from app.services.llm import generate_grounded_draft, rerank_evidence
from app.services.mcp_client import get_annals_articles_via_mcp
from app.services.query_filters import build_retrieval_query, extract_search_filters
from app.services.search import search_annals_articles, tokenize_query


async def run_post_creation_agent(db: Session, question: str) -> dict:
    trace: list[dict] = []

    keywords = tokenize_query(question)
    filters = extract_search_filters(question)
    retrieval_query = build_retrieval_query(question, filters)
    trace.append(
        {
            "step": "question_analysis",
            "keywords": keywords,
            "filters": filters.to_trace(),
            "retrieval_query": retrieval_query,
        }
    )

    search_results = search_annals_articles(db, question, limit=8)
    trace.append(
        {
            "step": "rag_search",
            "article_ids": [article.article_id for article in search_results],
        }
    )

    evidence = await get_annals_articles_via_mcp([article.article_id for article in search_results])
    trace.append(
        {
            "step": "mcp_tool_lookup",
            "transport": "stdio",
            "server": "annals-board",
            "tool": "get_annals_article",
            "count": len(evidence),
        }
    )

    rerank_result = await rerank_evidence(question, evidence, max_items=3)
    selected_evidence = rerank_result["selected_evidence"]
    trace.append(
        {
            "step": "evidence_rerank",
            "selected_article_ids": rerank_result["selected_ids"],
            "rejected_article_ids": rerank_result["rejected_ids"],
            "reason": rerank_result["reason"],
        }
    )

    draft = await generate_grounded_draft(question, selected_evidence)
    trace.append({"step": "llm_draft", "used_evidence_count": len(selected_evidence)})
    trace.append({"step": "tag_recommendation", "tags": draft["tags"]})

    return {
        "summary": draft["summary"],
        "interpretation": draft["interpretation"],
        "tags": draft["tags"],
        "evidence": selected_evidence,
        "trace": trace,
    }
