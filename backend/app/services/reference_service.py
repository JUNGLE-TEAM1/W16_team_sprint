from __future__ import annotations

import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from backend.app.core.config import settings
from backend.app.schemas.rag import RagMatch, RagReference


def fetch_reference_materials(
    *,
    query_text: str,
    matches: list[RagMatch],
    reference_urls: list[str] | None = None,
) -> list[RagReference]:
    if not settings.reference_fetch_enabled:
        return []

    try:
        payloads = _run_mcp_call(
            _call_reference_mcp(
                query_text=query_text,
                matches=[_match_payload(match) for match in matches],
                reference_urls=reference_urls or [],
            )
        )
    except Exception:
        return []

    return _reference_models(payloads)


async def _call_reference_mcp(
    *,
    query_text: str,
    matches: list[dict[str, Any]],
    reference_urls: list[str],
) -> list[dict[str, Any]]:
    project_root = Path(__file__).resolve().parents[3]
    env = os.environ.copy()
    env.setdefault("REFERENCE_FETCH_ENABLED", str(settings.reference_fetch_enabled).lower())
    env.setdefault("REFERENCE_API_URL", settings.reference_api_url)
    env.setdefault("REFERENCE_MAX_ITEMS", str(settings.reference_max_items))
    env.setdefault("REFERENCE_TIMEOUT_SECONDS", str(settings.reference_timeout_seconds))

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "backend.app.mcp.reference_server"],
        cwd=project_root,
        env=env,
    )

    async with AsyncExitStack() as exit_stack:
        read_stream, write_stream = await exit_stack.enter_async_context(stdio_client(server_params))
        session = await exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        await session.initialize()
        result = await session.call_tool(
            "fetch_reference_materials",
            {
                "query_text": query_text,
                "matches": matches,
                "reference_urls": reference_urls,
            },
        )

    return _tool_result_payloads(result)


def _run_mcp_call(coro) -> list[dict[str, Any]]:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    raise RuntimeError("Synchronous RAG reference lookup cannot run inside an active event loop")


def _tool_result_payloads(result: Any) -> list[dict[str, Any]]:
    structured = getattr(result, "structuredContent", None) or getattr(
        result, "structured_content", None
    )
    if isinstance(structured, list):
        return [item for item in structured if isinstance(item, dict)]
    if isinstance(structured, dict):
        raw_items = structured.get("references") or structured.get("result") or structured.get("items")
        if isinstance(raw_items, list):
            return [item for item in raw_items if isinstance(item, dict)]

    for content in getattr(result, "content", []):
        text = getattr(content, "text", None)
        if not isinstance(text, str):
            continue
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
        if isinstance(parsed, dict):
            raw_items = parsed.get("references") or parsed.get("result") or parsed.get("items")
            if isinstance(raw_items, list):
                return [item for item in raw_items if isinstance(item, dict)]

    return []


def _match_payload(match: RagMatch) -> dict[str, Any]:
    return {
        "post_id": match.post_id,
        "title": match.title,
        "excerpt": match.excerpt,
        "score": match.score,
        "duplicate_risk": match.duplicate_risk,
        "summary": match.summary,
        "tags": [{"id": tag.id, "name": tag.name} for tag in match.tags],
    }


def _reference_models(payloads: list[dict[str, Any]]) -> list[RagReference]:
    references: list[RagReference] = []
    for payload in payloads:
        title = _clean(payload.get("title"))
        url = _clean(payload.get("url"))
        source = _clean(payload.get("source")) or "mcp-reference"
        excerpt = _clean(payload.get("excerpt")) or title
        if not title or not url:
            continue
        references.append(
            RagReference(
                title=title[:120],
                url=url,
                source=source[:80],
                excerpt=excerpt[:260],
            )
        )
    return references


def _clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
