#!/usr/bin/env python
"""Trivial stdio MCP backend exposing one ``add(a, b)`` tool.

This is the "real backend" that the lazy proxy defers spawning until the
first ``tools/call``.  It is a plain MCP server over stdio using the
official ``mcp`` SDK (mcp 2.0.0 in the pinned test venv).

Every line this process writes to stderr is a log line (protocol traffic
goes over stdout).  Log lines are prefixed ``BACKEND|`` so they can be
distinguished from proxy and harness lines when streams are captured
together.  The process logs its PID at startup so tests can identify and
kill it directly (Test 4).
"""

from __future__ import annotations

import os
import sys
import time

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool


def _log(msg: str) -> None:
    now = time.time()
    epoch_ms = int(now * 1000)
    iso = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(now)) + f".{epoch_ms % 1000:03d}Z"
    print(f"BACKEND|{iso}|epoch_ms={epoch_ms}|{msg}", file=sys.stderr, flush=True)


def _add(a: float, b: float) -> float:
    return a + b


def _make_server() -> Server:
    async def on_list_tools(ctx, params) -> ListToolsResult:
        return ListToolsResult(
            tools=[
                Tool(
                    name="add",
                    description="Add two numbers and return the sum.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "a": {"type": "number", "description": "First addend"},
                            "b": {"type": "number", "description": "Second addend"},
                        },
                        "required": ["a", "b"],
                    },
                )
            ]
        )

    async def on_call_tool(ctx, params) -> CallToolResult:
        args = params.arguments or {}
        a = args.get("a")
        b = args.get("b")
        _log(f"tool_call name={params.name} arguments={args!r}")
        if a is None or b is None:
            return CallToolResult(
                content=[TextContent(type="text", text="error: missing a or b")],
                isError=True,
            )
        try:
            result = _add(float(a), float(b))
        except (TypeError, ValueError) as exc:
            return CallToolResult(
                content=[TextContent(type="text", text=f"error: {exc}")],
                isError=True,
            )
        _log(f"tool_call_result name={params.name} result={result!r}")
        return CallToolResult(content=[TextContent(type="text", text=str(result))])

    return Server(
        "lazy-backend",
        version="1.0.0",
        on_list_tools=on_list_tools,
        on_call_tool=on_call_tool,
    )


async def _main() -> None:
    server = _make_server()
    pid = os.getpid()
    # Evidence hook: when the proxy spawns us it passes BACKEND_PID_FILE so
    # the harness can locate and kill this exact process (Test 4).
    pid_file = os.environ.get("BACKEND_PID_FILE")
    if pid_file:
        try:
            with open(pid_file, "w", encoding="utf-8") as fh:
                fh.write(str(pid))
            _log(f"pid_file_written path={pid_file} pid={pid}")
        except OSError as exc:
            _log(f"pid_file_write_error path={pid_file} error={exc}")
    _log(
        "backend_started "
        f"pid={pid} "
        f"python={sys.executable}"
    )
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
    _log("backend_stdin_closed_exiting")


if __name__ == "__main__":
    import asyncio

    asyncio.run(_main())
