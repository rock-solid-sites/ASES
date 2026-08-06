#!/usr/bin/env python
"""Trivial stdio MCP backend for the output-schema-drift investigation.

This is the "real backend" that the lazy proxy defers spawning until the
first ``tools/call``.  It is a plain MCP server over stdio using the
official ``mcp`` SDK (mcp 2.0.0 in the pinned test venv).

It extends the #196 backend with two controlled dimensions so the drift
test can change the backend's behaviour between manifest-capture time and
call time WITHOUT re-capturing:

* ``BACKEND_SCHEMA_MODE``  -- what the backend's ``tools/list`` DECLARES as
  the ``add`` tool's ``output_schema``:
    ``none``        : no output_schema (field None)         [Test A baseline]
    ``conforming``  : {"type":"object", ... "sum": number}  [Test B-F]
    ``diverging``   : {"type":"object", ... "result": number} [supplementary C2]
* ``BACKEND_RESPONSE_MODE`` -- what the backend RETURNS for ``add``:
    ``text``        : text content only, ``structured_content`` None (the
                      #196 behaviour; works only when no output_schema is
                      declared by the validating client)
    ``conforming``  : ``structured_content={"sum": <n>}``
    ``diverging``   : ``structured_content={"result": <n>}`` (does NOT
                      conform to the cached {\"sum\": ...} schema)
    ``bare``        : ``structured_content=<n>`` (a bare number; fails the
                      ``{"type":"object"}`` root requirement)

A second tool ``multiply(a, b)`` has NO output_schema declaration in any
mode; it is the unrelated tool used by Test F (blast radius) to check
whether a drift failure poisons the registry beyond the one failed call.

Every line this process writes to stderr is a log line (protocol traffic
goes over stdout).  Log lines are prefixed ``BACKEND|`` so they can be
distinguished from proxy and harness lines when streams are captured
together.  The process logs its PID at startup so tests can identify it.
"""

from __future__ import annotations

import os
import sys
import time

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool

SCHEMA_CONFORMING: dict = {
    "type": "object",
    "properties": {"sum": {"type": "number", "description": "The sum of a and b"}},
    "required": ["sum"],
}
SCHEMA_DIVERGING: dict = {
    "type": "object",
    "properties": {"result": {"type": "number", "description": "The result"}},
    "required": ["result"],
}


def _log(msg: str) -> None:
    now = time.time()
    epoch_ms = int(now * 1000)
    iso = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(now)) + f".{epoch_ms % 1000:03d}Z"
    print(f"BACKEND|{iso}|epoch_ms={epoch_ms}|{msg}", file=sys.stderr, flush=True)


def _add(a: float, b: float) -> float:
    return a + b


def _multiply(a: float, b: float) -> float:
    return a * b


def _add_output_schema(mode: str) -> dict | None:
    if mode == "conforming":
        return SCHEMA_CONFORMING
    if mode == "diverging":
        return SCHEMA_DIVERGING
    return None  # "none"


def _add_call_result(a: float, b: float, mode: str) -> CallToolResult:
    """Build the CallToolResult for ``add`` per the configured response mode.

    ``structured_content`` is the field the mcp 2.0.0 client
    ``validate_tool_result`` validates against the tool's declared
    ``output_schema`` (mcp/client/session.py:1096-1100).  The text content
    is always present so the only variable is the structured shape.
    """
    value = _add(a, b)
    text = TextContent(type="text", text=str(value))
    if mode == "text":
        return CallToolResult(content=[text])
    if mode == "conforming":
        return CallToolResult(content=[text], structured_content={"sum": value})
    if mode == "diverging":
        return CallToolResult(content=[text], structured_content={"result": value})
    if mode == "bare":
        return CallToolResult(content=[text], structured_content=value)
    raise ValueError(f"unknown response mode {mode!r}")


def _make_server() -> Server:
    schema_mode = os.environ.get("BACKEND_SCHEMA_MODE", "conforming")
    response_mode = os.environ.get("BACKEND_RESPONSE_MODE", "conforming")
    _log(
        f"configured schema_mode={schema_mode} response_mode={response_mode}"
    )

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
                    output_schema=_add_output_schema(schema_mode),
                ),
                Tool(
                    name="multiply",
                    description="Multiply two numbers and return the product.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "a": {"type": "number", "description": "First factor"},
                            "b": {"type": "number", "description": "Second factor"},
                        },
                        "required": ["a", "b"],
                    },
                    output_schema=None,
                ),
            ]
        )

    async def on_call_tool(ctx, params) -> CallToolResult:
        args = params.arguments or {}
        name = params.name
        _log(f"tool_call name={name} arguments={args!r}")
        if name == "multiply":
            a = args.get("a")
            b = args.get("b")
            if a is None or b is None:
                return CallToolResult(
                    content=[TextContent(type="text", text="error: missing a or b")],
                    isError=True,
                )
            try:
                product = _multiply(float(a), float(b))
            except (TypeError, ValueError) as exc:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"error: {exc}")],
                    isError=True,
                )
            result = CallToolResult(
                content=[TextContent(type="text", text=str(product))],
                structured_content={"product": product},
            )
            _log(f"tool_call_result name={name} result={product!r} structured={'product'}")
            return result
        # add (default)
        a = args.get("a")
        b = args.get("b")
        if a is None or b is None:
            return CallToolResult(
                content=[TextContent(type="text", text="error: missing a or b")],
                isError=True,
            )
        try:
            a_f = float(a)
            b_f = float(b)
        except (TypeError, ValueError) as exc:
            return CallToolResult(
                content=[TextContent(type="text", text=f"error: {exc}")],
                isError=True,
            )
        result = _add_call_result(a_f, b_f, response_mode)
        _log(
            f"tool_call_result name={name} result={_add(a_f, b_f)!r} "
            f"response_mode={response_mode} structured={result.structured_content!r}"
        )
        return result

    return Server(
        "lazy-backend-drift",
        version="1.1.0",
        on_list_tools=on_list_tools,
        on_call_tool=on_call_tool,
    )


async def _main() -> None:
    server = _make_server()
    pid = os.getpid()
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
