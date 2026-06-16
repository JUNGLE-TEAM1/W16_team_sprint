from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from backend.app.core.config import settings
from backend.app.mcp.reference_fetcher import fetch_reference_payloads

mcp = FastMCP("Sprint Reference Materials")


@mcp.tool()
def fetch_reference_materials(
    query_text: str,
    matches: list[dict[str, Any]],
    reference_urls: list[str] | None = None,
) -> list[dict[str, str]]:
    """Fetch official documentation and external API references for a RAG draft."""
    return fetch_reference_payloads(
        query_text=query_text,
        matches=matches,
        reference_urls=reference_urls or [],
        enabled=settings.reference_fetch_enabled,
        api_url=settings.reference_api_url,
        max_items=settings.reference_max_items,
        timeout_seconds=settings.reference_timeout_seconds,
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
