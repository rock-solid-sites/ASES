#!/usr/bin/env python
"""Mutable-tool-set backend for Test 5 (catalog invalidation / stale baseline).

The tool set is read from a JSON control file at every ``tools/list``, so the
harness can change the backend's capabilities at runtime (e.g. remove `add`
and add `sub`) without restarting the process. The control file layout:

    {"tools": [{"name": "add", ...}, ...]}

``tools/call`` for a name absent from the current control file returns an
isError result (unknown tool) rather than raising — that keeps the failure
inside ToolRegistry's result path where the harness can observe it, and
distinguishes "backend says unknown tool" from a connection failure.

This backend is a Test-5-only characterization instrument. Stdio transport.
"""

from __future__ import annotations

import json
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


def _current_tools(control_file: str) -> list[dict]:
    """Read the control file; on any read error return [] and log."""
    try:
        with open(control_file, encoding="utf-8") as fh:
            data = json.load(fh)
        return list(data.get("tools", []))
    except Exception as exc:
        _log(f"control_file_error path={control_file} exc={type(exc).__name__}:{exc}")
        return []


def _tool_defs(control_file: str) -> list[Tool]:
    defs = []
    for t in _current_tools(control_file):
        defs.append(
            Tool(
                name=t["name"],
                description=t.get("description", "No description."),
                inputSchema=t.get("inputSchema", {"type": "object", "properties": {}}),
            )
        )
    return defs


def _make_server(control_file: str) -> Server:
    async def on_list_tools(ctx, params) -> ListToolsResult:
        tools = _tool_defs(control_file)
        _log(f"tool_list control={control_file} tools={[t.name for t in tools]}")
        return ListToolsResult(tools=tools)

    async def on_call_tool(ctx, params) -> CallToolResult:
        args = params.arguments or {}
        current = {t["name"] for t in _current_tools(control_file)}
        _log(f"tool_call name={params.name} known={params.name in current} arguments={args!r}")
        if params.name not in current:
            # The tool is not in the CURRENT backend tool set: explicit
            # application error (unknown tool), NOT a connection failure.
            return CallToolResult(
                content=[TextContent(type="text", text=f"error: unknown tool {params.name!r}")],
                isError=True,
            )
        if params.name == "add":
            a, b = args.get("a"), args.get("b")
            if a is None or b is None:
                return CallToolResult(
                    content=[TextContent(type="text", text="error: missing a or b")],
                    isError=True,
                )
            try:
                result = float(a) + float(b)
            except (TypeError, ValueError) as exc:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"error: {exc}")],
                    isError=True,
                )
            return CallToolResult(content=[TextContent(type="text", text=str(result))])
        if params.name == "sub":
            a, b = args.get("a"), args.get("b")
            try:
                result = float(a) - float(b)
            except (TypeError, ValueError) as exc:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"error: {exc}")],
                    isError=True,
                )
            return CallToolResult(content=[TextContent(type="text", text=str(result))])
        # Unknown tool: explicit application error, NOT a connection failure.
        return CallToolResult(
            content=[TextContent(type="text", text=f"error: unknown tool {params.name!r}")],
            isError=True,
        )

    return Server(
        "lazy-backend-5a",
        version="1.0.0",
        on_list_tools=on_list_tools,
        on_call_tool=on_call_tool,
    )


async def _main() -> None:
    control_file = os.environ.get("BACKEND_5A_CONTROL_FILE", "")
    server = _make_server(control_file)
    pid = os.getpid()
    pid_file = os.environ.get("BACKEND_PID_FILE")
    if pid_file:
        try:
            with open(pid_file, "w", encoding="utf-8") as fh:
                fh.write(str(pid))
            _log(f"pid_file_written path={pid_file} pid={pid}")
        except OSError as exc:
            _log(f"pid_file_write_error path={pid_file} error={exc}")
    _log(f"backend_5a_started pid={pid} control_file={control_file}")
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
