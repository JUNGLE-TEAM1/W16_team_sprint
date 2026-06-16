from types import SimpleNamespace

from backend.app.services.reference_service import _reference_models, _tool_result_payloads


def test_tool_result_payloads_reads_mcp_structured_content() -> None:
    result = SimpleNamespace(
        structuredContent={
            "result": [
                {
                    "title": "FastAPI security",
                    "url": "https://fastapi.tiangolo.com/tutorial/security/",
                    "source": "FastAPI docs",
                    "excerpt": "Official security reference.",
                }
            ]
        },
        content=[],
    )

    payloads = _tool_result_payloads(result)

    assert payloads[0]["title"] == "FastAPI security"


def test_reference_models_filters_invalid_mcp_payloads() -> None:
    references = _reference_models(
        [
            {
                "title": "React docs",
                "url": "https://react.dev/learn",
                "source": "React docs",
                "excerpt": "Official React guide.",
            },
            {"title": "Missing URL"},
        ]
    )

    assert len(references) == 1
    assert references[0].url == "https://react.dev/learn"
