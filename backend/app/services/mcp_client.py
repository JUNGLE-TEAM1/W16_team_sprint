import json
import os
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import TextContent


def _mcp_server_params() -> StdioServerParameters:
    backend_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    python_path = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(backend_root) if not python_path else f"{backend_root}{os.pathsep}{python_path}"
    return StdioServerParameters(
        command=sys.executable,
        args=[str(backend_root / "app" / "mcp_server.py")],
        env=env,
    )


def _parse_tool_payload(result: object) -> dict:
    content = getattr(result, "content", [])
    if not content:
        return {}

    first_content = content[0]
    if isinstance(first_content, TextContent):
        return json.loads(first_content.text)
    text = getattr(first_content, "text", "")
    return json.loads(text) if text else {}


async def get_annals_article_via_mcp(article_id: str) -> dict | None:
    params = _mcp_server_params()
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool("get_annals_article", {"article_id": article_id})

    payload = _parse_tool_payload(result)
    if payload.get("error"):
        return None
    return payload


async def get_annals_articles_via_mcp(article_ids: list[str]) -> list[dict]:
    articles = []
    params = _mcp_server_params()
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            for article_id in article_ids:
                result = await session.call_tool("get_annals_article", {"article_id": article_id})
                payload = _parse_tool_payload(result)
                if payload and not payload.get("error"):
                    articles.append(payload)
    return articles
