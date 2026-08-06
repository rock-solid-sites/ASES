#!/usr/bin/env python
"""Capture ``tools/list`` from the drift backend into a manifest JSON.

Evidence step: run the real backend once, dump its ``tools/list`` to the
static manifest that the lazy proxy serves from cache.  This mirrors what
an identifier-first system would snapshot ahead of time.

The declared output schema of the ``add`` tool is controlled by the
``BACKEND_SCHEMA_MODE`` env var (``none`` | ``conforming`` | ``diverging``),
so the operator can capture a null-schema manifest (Test A baseline) or a
conforming-schema manifest (Tests B-F) without editing backend code.

Usage:
    BACKEND_SCHEMA_MODE=conforming  .../venv/bin/python capture_manifest.py  # -> manifest.json
    BACKEND_SCHEMA_MODE=none        .../venv/bin/python capture_manifest.py  # -> manifest-null.json
Output file is chosen by ``--out`` / ``MANIFEST_OUT`` env; default
``manifest.json`` (conforming mode) or ``manifest-null.json`` (none mode).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = Path(__file__).resolve().parent
BACKEND_PATH = HERE / "backend.py"


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=None, help="output manifest path")
    args = parser.parse_args()

    schema_mode = os.environ.get("BACKEND_SCHEMA_MODE", "conforming")
    if args.out:
        out_path = Path(args.out)
    elif schema_mode == "none":
        out_path = HERE / "manifest-null.json"
    else:
        out_path = HERE / "manifest.json"

    backend_env = dict(os.environ)
    backend_env["BACKEND_SCHEMA_MODE"] = schema_mode
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(BACKEND_PATH)],
        env=backend_env,
    )
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.list_tools()
    tools = [t.model_dump(mode="json") for t in result.tools]
    manifest = {
        "captured_with": {
            "python": sys.executable,
            "backend": str(BACKEND_PATH),
            "schema_mode": schema_mode,
            "toolcount": len(tools),
        },
        "tools": tools,
    }
    out_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"captured {len(tools)} tool(s) (schema_mode={schema_mode}) -> {out_path}")
    for t in tools:
        print(f"  - {t['name']}: output_schema={json.dumps(t.get('output_schema'))}")


if __name__ == "__main__":
    asyncio.run(main())
