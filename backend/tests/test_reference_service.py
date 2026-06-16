from types import SimpleNamespace

from backend.app.services.reference_service import _reference_models, _tool_result_payloads


def test_tool_result_payloads_reads_mcp_structured_content() -> None:
    result = SimpleNamespace(
        structuredContent={
            "result": [
                {
                    "title": "온통청년 청년정책API",
                    "url": "https://www.data.go.kr/data/15143273/openapi.do",
                    "source": "공공데이터포털",
                    "excerpt": "청년정책 공공데이터입니다.",
                }
            ]
        },
        content=[],
    )

    payloads = _tool_result_payloads(result)

    assert payloads[0]["title"] == "온통청년 청년정책API"


def test_reference_models_filters_invalid_mcp_payloads() -> None:
    references = _reference_models(
        [
            {
                "title": "복지로 복지서비스 안내",
                "url": "https://www.bokjiro.go.kr/",
                "source": "복지로",
                "excerpt": "복지서비스 검색 포털입니다.",
            },
            {"title": "Missing URL"},
        ]
    )

    assert len(references) == 1
    assert references[0].url == "https://www.bokjiro.go.kr/"
