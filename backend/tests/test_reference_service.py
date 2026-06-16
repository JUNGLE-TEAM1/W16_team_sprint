from types import SimpleNamespace

from backend.app.services.reference_service import _reference_models, _tool_result_payloads


def test_tool_result_payloads_reads_mcp_structured_content() -> None:
    result = SimpleNamespace(
        structuredContent={
            "result": [
                {
                    "title": "경기도 수원시 청년지원사업 API",
                    "url": "https://infuser.odcloud.kr/oas/docs?namespace=15089956/v1",
                    "source": "공공데이터포털",
                    "excerpt": "수원시 청년지원사업 공공데이터입니다.",
                }
            ]
        },
        content=[],
    )

    payloads = _tool_result_payloads(result)

    assert payloads[0]["title"] == "경기도 수원시 청년지원사업 API"


def test_reference_models_filters_invalid_mcp_payloads() -> None:
    references = _reference_models(
        [
            {
                "title": "수원청년포털",
                "url": "http://www.swyouth.kr",
                "source": "수원청년포털",
                "excerpt": "수원시 청년지원사업 안내 사이트입니다.",
            },
            {"title": "Missing URL"},
        ]
    )

    assert len(references) == 1
    assert references[0].url == "http://www.swyouth.kr"
