from app.services.llm import _select_evidence_by_ids, fallback_rerank_evidence


def test_select_evidence_by_ids_preserves_llm_order() -> None:
    evidence = [
        {"article_id": "a1", "title": "첫 기사"},
        {"article_id": "a2", "title": "둘째 기사"},
        {"article_id": "a3", "title": "셋째 기사"},
    ]

    selected = _select_evidence_by_ids(evidence, ["a3", "a1", "missing"], max_items=2)

    assert [item["article_id"] for item in selected] == ["a3", "a1"]


def test_fallback_rerank_uses_search_order() -> None:
    evidence = [
        {"article_id": "a1", "title": "첫 기사"},
        {"article_id": "a2", "title": "둘째 기사"},
        {"article_id": "a3", "title": "셋째 기사"},
    ]

    result = fallback_rerank_evidence(evidence, max_items=2)

    assert result["selected_ids"] == ["a1", "a2"]
    assert result["rejected_ids"] == ["a3"]
