from types import SimpleNamespace

from app.services.mcp_client import _parse_tool_payload


def test_parse_tool_payload_reads_json_text_content() -> None:
    result = SimpleNamespace(content=[SimpleNamespace(text='{"article_id": "waa_001"}')])

    payload = _parse_tool_payload(result)

    assert payload == {"article_id": "waa_001"}
