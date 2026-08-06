#!/usr/bin/env python
"""Capture ``tools/list`` from the real backend into ``manifest.json``.

Evidence step: run the real backend once, dump its ``tools/list`` to the
static manifest that the lazy proxy serves from cache.  This mirrors what
an identifier-first system would snapshot ahead of time.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = Path(__file__).resolve().parent
BACKEND_PATH = HERE / "backend.py"
MANIFEST_PATH = HERE / "manifest.json"


async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=[str(BACKEND_PATH)])
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.list_tools()
    tools = [t.model_dump(mode="json") for t in result.tools]
    manifest = {
        "captured_with": {
            "python": sys.executable,
            "backend": str(BACKEND_PATH),
            "toolcount": len(tools),
        },
        "tools": tools,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"captured {len(tools)} tool(s) -> {MANIFEST_PATH}")
    for t in tools:
        print(f"  - {t['name']}: {t.get('description', '')[:60]}")


if __name__ == "__main__":
    asyncio.run(main())
