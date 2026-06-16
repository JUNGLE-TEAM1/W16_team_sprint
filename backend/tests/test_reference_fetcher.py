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
                    "title": "서울시 청년월세 지원",
                    "url": "https://housing.seoul.go.kr/",
                    "source": "policy-api",
                    "description": "서울 청년 주거비 지원 자료입니다.",
                }
            ]
        }
    )

    assert len(references) == 1
    assert references[0]["title"] == "서울시 청년월세 지원"
    assert references[0]["source"] == "policy-api"
    assert references[0]["excerpt"] == "서울 청년 주거비 지원 자료입니다."


def test_rank_official_candidates_uses_draft_and_match_tags() -> None:
    candidates = _rank_official_candidates(
        query_text="서울 거주 24세 취준생이고 월세 지원과 청년 주거 정책이 필요합니다.",
        matches=[
            {
                "post_id": 1,
                "title": "[청년/주거] 서울시 청년월세 지원",
                "excerpt": "청년 주거비와 월세 부담을 낮추는 정책입니다.",
                "score": 0.8,
                "duplicate_risk": "high",
                "summary": "청년 주거 지원 상담입니다.",
                "tags": [{"id": 1, "name": "청년"}, {"id": 2, "name": "주거"}],
            }
        ],
    )

    assert candidates
    assert candidates[0].title == "한국고용정보원 온통청년 청년정책API"


def test_reference_urls_deduplicates_and_blocks_local_targets() -> None:
    references = _reference_urls(
        [
            "https://www.data.go.kr/data/15143273/openapi.do",
            "https://www.data.go.kr/data/15143273/openapi.do/",
            "http://localhost:8000/private",
            "http://127.0.0.1:8000/private",
        ]
    )

    assert references == ["https://www.data.go.kr/data/15143273/openapi.do"]
    assert _is_allowed_reference_url("https://www.bokjiro.go.kr/") is True
    assert _is_allowed_reference_url("http://localhost:8000/private") is False
