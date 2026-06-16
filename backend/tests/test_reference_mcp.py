import os
import sys
from contextlib import AsyncExitStack
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.mark.anyio
async def test_reference_mcp_server_exposes_fetch_tool() -> None:
    env = os.environ.copy()
    env["REFERENCE_FETCH_ENABLED"] = "false"

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "backend.app.mcp.reference_server"],
        cwd=Path(__file__).resolve().parents[2],
        env=env,
    )

    async with AsyncExitStack() as exit_stack:
        read_stream, write_stream = await exit_stack.enter_async_context(stdio_client(server_params))
        session = await exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool(
            "fetch_reference_materials",
            {
                "query_text": "수원 청년 월세 지원",
                "matches": [],
                "reference_urls": ["https://infuser.odcloud.kr/oas/docs?namespace=15089956/v1"],
            },
        )

    assert "fetch_reference_materials" in {tool.name for tool in tools.tools}
    assert result.isError is False
