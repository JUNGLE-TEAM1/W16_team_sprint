from backend.app.mcp.reference_fetcher import (
    _is_allowed_reference_url,
    _parse_external_api_payload,
    _rank_official_candidates,
    _reference_urls,
)


def test_parse_external_api_payload_accepts_common_shapes() -> None:
    references = _parse_external_api_payload(
        {
            "results": [
                {
                    "title": "FastAPI security",
                    "url": "https://fastapi.tiangolo.com/tutorial/security/",
                    "source": "docs-api",
                    "description": "Official FastAPI security material.",
                }
            ]
        }
    )

    assert len(references) == 1
    assert references[0]["title"] == "FastAPI security"
    assert references[0]["source"] == "docs-api"
    assert references[0]["excerpt"] == "Official FastAPI security material."


def test_rank_official_candidates_uses_draft_and_match_tags() -> None:
    candidates = _rank_official_candidates(
        query_text="JWT Bearer auth keeps returning 401",
        matches=[
            {
                "post_id": 1,
                "title": "FastAPI auth note",
                "excerpt": "Check current_user dependency.",
                "score": 0.8,
                "duplicate_risk": "high",
                "summary": "Authentication issue.",
                "tags": [{"id": 1, "name": "fastapi"}],
            }
        ],
    )

    assert candidates
    assert candidates[0].source == "FastAPI docs"


def test_reference_urls_deduplicates_and_blocks_local_targets() -> None:
    references = _reference_urls(
        [
            "https://fastapi.tiangolo.com/tutorial/security/",
            "https://fastapi.tiangolo.com/tutorial/security",
            "http://localhost:8000/private",
            "http://127.0.0.1:8000/private",
        ]
    )

    assert references == ["https://fastapi.tiangolo.com/tutorial/security/"]
    assert _is_allowed_reference_url("https://react.dev/learn") is True
    assert _is_allowed_reference_url("http://localhost:8000/private") is False
