#!/usr/bin/env python
"""Lazy stdio MCP proxy with live-manifest + list_changed support (Test 5 only).

Same lazy backbone as proxy.py (static manifest before backend connect, backend
spawn on first call, one reused backend session), plus two Test-5
characterization capabilities:

1. LIVE manifest: when the backend IS connected, ``tools/list`` returns the
   backend's CURRENT tool list (re-read from the backend session) instead of
   the cached manifest, so a refresh can observe backend-side changes.
   When the backend is NOT connected, the static manifest is served (this is
   the identifier-first property: catalog knowledge without activation).

2. ``_emit_list_changed`` control tool: calling it sends
   ``notifications/tools/list_changed`` to the client (ToolRegistry) via the
   mcp 2.0.0 session API (mcp/server/connection.py:441). It does not touch the
   backend.

Used by Test 5a (invalidation: does the registry receive/act on the signal?)
and Test 5b (stale-catalog baseline: no signal emitted). Stdio only.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, ListToolsResult, Tool
from mcp_types import NotificationParams

HERE = Path(__file__).resolve().parent
BACKEND_PATH = HERE / "backend_5a.py"

_START_EPOCH_MS = int(time.time() * 1000)


def _log(msg: str) -> None:
    now = time.time()
    epoch_ms = int(now * 1000)
    rel_ms = epoch_ms - _START_EPOCH_MS
    iso = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(now)) + f".{epoch_ms % 1000:03d}Z"
    line = f"PROXY|{iso}|epoch_ms={epoch_ms}|rel_ms={rel_ms:>8}|{msg}"
    print(line, file=sys.stderr, flush=True)
    log_file = os.environ.get("PROXY_LOG_FILE")
    if log_file:
        try:
            with open(log_file, "a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        except OSError:
            pass


def _load_manifest() -> list[Tool]:
    path = os.environ.get("PROXY_5A_MANIFEST", str(HERE / "manifest_5a.json"))
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    tools = raw.get("tools", raw) if isinstance(raw, dict) else raw
    return [Tool.model_validate(t) for t in tools]


class BackendClient:
    """Lazy client session to backend_5a.py, reused across calls."""

    def __init__(self) -> None:
        self._cm = None
        self._session_cm = None
        self._session: ClientSession | None = None
        self._spawn_count = 0
        self._instance_id: str | None = None

    @property
    def connected(self) -> bool:
        return self._session is not None

    @property
    def session(self) -> ClientSession | None:
        return self._session

    @property
    def spawn_count(self) -> int:
        return self._spawn_count

    @property
    def instance_id(self) -> str | None:
        return self._instance_id

    async def ensure_ready(self) -> None:
        if self._session is not None:
            return
        self._spawn_count += 1
        self._instance_id = f"be5a-{self._spawn_count}-{os.getpid()}-{int(time.time() * 1000) % 100000}"
        env = {"BACKEND_INSTANCE_ID": self._instance_id}
        if "BACKEND_PID_FILE" in os.environ:
            env["BACKEND_PID_FILE"] = os.environ["BACKEND_PID_FILE"]
        if "BACKEND_5A_CONTROL_FILE" in os.environ:
            env["BACKEND_5A_CONTROL_FILE"] = os.environ["BACKEND_5A_CONTROL_FILE"]
        params = StdioServerParameters(command=sys.executable, args=[str(BACKEND_PATH)], env=env)
        _log(f"backend_spawn_start instance_id={self._instance_id} spawn_count={self._spawn_count}")
        self._cm = stdio_client(params)
        try:
            read_stream, write_stream = await self._cm.__aenter__()
            self._session = ClientSession(read_stream, write_stream)
            self._session_cm = self._session.__aenter__()
            await self._session_cm
            await self._session.initialize()
        except Exception:
            _log("backend_spawn_failed")
            raise
        _log(f"backend_up instance_id={self._instance_id} spawn_count={self._spawn_count}")

    async def close(self) -> None:
        if self._session_cm is not None:
            try:
                await self._session_cm.__aexit__(None, None, None)
            except Exception:
                pass
            self._session_cm = None
        if self._cm is not None:
            try:
                await self._cm.__aexit__(None, None, None)
            except Exception:
                pass
            self._cm = None
        self._session = None
        _log(f"backend_client_closed instance_id={self._instance_id}")


async def _main() -> None:
    manifest_tools = _load_manifest()
    backend_client = BackendClient()
    backend_timeout = float(os.environ.get("PROXY_BACKEND_TIMEOUT", "10.0"))

    _log(
        "proxy_5a_started "
        f"pid={os.getpid()} "
        f"manifest_tools={[t.name for t in manifest_tools]} "
        "backend=not_started"
    )

    async def on_list_tools(ctx, params) -> ListToolsResult:
        if backend_client.connected:
            try:
                live = await backend_client.session.list_tools()
                _log(
                    f"request tools/list backend_connected=True live_tools={[t.name for t in live.tools]}"
                )
                return live
            except Exception as exc:
                _log(f"live_list_error type={type(exc).__name__} falling_back_to_manifest")
        _log(f"request tools/list backend_connected=False manifest_tools={[t.name for t in manifest_tools]}")
        return ListToolsResult(tools=manifest_tools)

    async def on_call_tool(ctx, params) -> CallToolResult:
        name = params.name
        arguments = dict(params.arguments or {})
        _log(f"request tools/call name={name} arguments={arguments!r} backend_connected={backend_client.connected}")
        if name == "_emit_list_changed":
            # Control tool: notify the client that the tool list changed.
            # Does NOT touch the backend. ctx.session.send_tool_list_changed
            # sends notifications/tools/list_changed (mcp/server/connection.py:441).
            try:
                await ctx.session.send_tool_list_changed()
                _log("sent notifications/tools/list_changed")
            except Exception as exc:
                _log(f"send_list_changed_error type={type(exc).__name__} msg={exc!r}")
            return CallToolResult(
                content=[{"type": "text", "text": "emitted notifications/tools/list_changed"}]
            )
        try:
            await asyncio.wait_for(backend_client.ensure_ready(), timeout=backend_timeout)
        except asyncio.TimeoutError:
            _log("backend_ready_timeout")
            return CallToolResult(
                content=[{"type": "text", "text": f"error: backend did not become ready in {backend_timeout}s"}],
                isError=True,
            )
        _log(f"forward tools/call name={name} to backend instance={backend_client.instance_id}")
        try:
            result = await backend_client.session.call_tool(name, arguments)
        except Exception as exc:
            _log(f"call_tool_handler_error type={type(exc).__name__} msg={exc!r}")
            await backend_client.close()
            raise
        _log(f"response tools/call name={name} ok={not getattr(result, 'isError', False)}")
        return result

    async def on_initialized_notification(ctx, params) -> None:
        _log("notification received notifications/initialized (client handshake done)")

    server = Server(
        "lazy-proxy-5a",
        version="1.0.0",
        on_list_tools=on_list_tools,
        on_call_tool=on_call_tool,
    )
    server.add_notification_handler(
        "notifications/initialized",
        NotificationParams,
        on_initialized_notification,
    )

    _log("server_ready waiting_for_client")
    # Declare tools.listChanged support so the emission in on_call_tool is a
    # supported-capability signal, not a wire-format accident.
    init_options = server.create_initialization_options(
        notification_options=NotificationOptions(tools_changed=True)
    )
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            init_options,
        )
    _log("connection_closed exiting")


if __name__ == "__main__":
    asyncio.run(_main())
