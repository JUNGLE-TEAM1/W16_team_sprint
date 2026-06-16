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
                    "title": "경기도 수원시 청년지원사업",
                    "url": "https://infuser.odcloud.kr/oas/docs?namespace=15089956/v1",
                    "source": "policy-api",
                    "description": "수원시 청년지원사업 상세설명 자료입니다.",
                }
            ]
        }
    )

    assert len(references) == 1
    assert references[0]["title"] == "경기도 수원시 청년지원사업"
    assert references[0]["source"] == "policy-api"
    assert references[0]["excerpt"] == "수원시 청년지원사업 상세설명 자료입니다."


def test_rank_official_candidates_uses_query_and_match_tags() -> None:
    candidates = _rank_official_candidates(
        query_text="수원시 거주 24세 청년이고 월세 지원과 청년정책이 필요합니다.",
        matches=[
            {
                "post_id": 1,
                "title": "[수원청년/2025] 청년월세지원사업",
                "excerpt": "수원시 청년에게 월세 임차료를 지원합니다.",
                "score": 0.8,
                "duplicate_risk": "high",
                "summary": "수원시 청년 주거 지원 상담입니다.",
                "tags": [{"id": 1, "name": "청년"}, {"id": 2, "name": "수원시"}],
            }
        ],
    )

    assert candidates
    assert candidates[0].title == "경기도 수원시 청년지원사업 상세설명 API"


def test_reference_urls_deduplicates_and_blocks_local_targets() -> None:
    references = _reference_urls(
        [
            "https://infuser.odcloud.kr/oas/docs?namespace=15089956/v1",
            "https://infuser.odcloud.kr/oas/docs?namespace=15089956/v1",
            "http://localhost:8000/private",
            "http://127.0.0.1:8000/private",
        ]
    )

    assert references == ["https://infuser.odcloud.kr/oas/docs?namespace=15089956/v1"]
    assert _is_allowed_reference_url("https://www.suwon.go.kr/") is True
    assert _is_allowed_reference_url("http://localhost:8000/private") is False
