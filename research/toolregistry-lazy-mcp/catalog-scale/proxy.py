#!/usr/bin/env python
"""Lazy stdio MCP proxy (dual role: server to ToolRegistry, client to backend).

Purpose
-------
Evidence-only probe for ``ToolRegistry.register_from_mcp()`` against an MCP
server that defers starting the real backend until the first ``tools/call``.
This proxy is NOT a product; it is a minimal instrument to answer one
question: does ToolRegistry's registration + invocation survive a lazy,
identifier-first backend with no changes to ToolRegistry itself?

Behaviour
---------
1. ``initialize`` handshake is answered by the ``mcp`` SDK server runner
   without touching the real backend.  Capabilities are derived from the
   registered handlers; ``notification_options`` is left at the default so
   the proxy advertises ``tools.listChanged: false`` (no change-notification
   support) and never sends any notification to its client.
2. Every ``tools/list`` is answered from the static cached ``manifest.json``.
3. On the first ``tools/call`` the backend subprocess is spawned, a client
   session is established, the call is forwarded and the result returned
   verbatim.  The backend client session is reused for subsequent calls.
4. If a forwarded call fails (e.g. the backend process was killed out from
   under the proxy — Test 4), the proxy closes the dead session, respawns
   the backend, and retries the call exactly once.  A second failure is
   propagated to the client.

Logging
-------
Protocol traffic is on stdout (owned by ToolRegistry).  All log lines go to
stderr and, if the ``PROXY_LOG_FILE`` env var is set, are also appended to
that file.  Every log line carries an ISO timestamp with milliseconds and an
epoch_ms field so cross-process timing with the harness is exact.

Environment variables understood by the proxy:
    PROXY_LOG_FILE      : optional path to append proxy log lines to.
    PROXY_BACKEND_TIMEOUT: optional float, seconds to wait for the backend
                           initialize handshake (default 10.0).
    PROXY_CALL_TIMEOUT  : optional float, seconds to bound one forwarded
                          tools/call including its respawn retry
                          (default 15.0).  Defensive: the SDK client raises
                          promptly on a dead session, but this guarantees a
                          hung backend cannot wedge the proxy.
    BACKEND_INSTANCE_ID : passed through to the backend, which logs it.
    BACKEND_PID_FILE    : passed through; the backend writes its PID here.
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
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, ListToolsResult, Tool
from mcp_types import NotificationParams

HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "manifest.json"
BACKEND_PATH = HERE / "backend.py"

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
        except OSError as exc:  # never let logging break the proxy
            print(f"PROXY|log_file_write_error={exc}", file=sys.stderr, flush=True)


def _load_manifest() -> list[Tool]:
    with open(MANIFEST_PATH, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    tools = raw.get("tools", raw) if isinstance(raw, dict) else raw
    return [Tool.model_validate(t) for t in tools]


class BackendClient:
    """Lazy client session to the real backend, reused across calls."""

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
    def spawn_count(self) -> int:
        return self._spawn_count

    @property
    def instance_id(self) -> str | None:
        return self._instance_id

    async def ensure_ready(self) -> None:
        """Spawn the backend and open a client session if not already connected."""
        if self._session is not None:
            return
        self._spawn_count += 1
        self._instance_id = f"be-{self._spawn_count}-{os.getpid()}-{int(time.time() * 1000) % 100000}"
        env = {
            "BACKEND_INSTANCE_ID": self._instance_id,
        }
        if "BACKEND_PID_FILE" in os.environ:
            env["BACKEND_PID_FILE"] = os.environ["BACKEND_PID_FILE"]
        params = StdioServerParameters(
            command=sys.executable,
            args=[str(BACKEND_PATH)],
            env=env,
        )
        _log(f"backend_spawn_start instance_id={self._instance_id} spawn_count={self._spawn_count}")
        spawn_start = time.time()
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
        spawn_ms = (time.time() - spawn_start) * 1000
        _log(
            f"backend_up instance_id={self._instance_id} spawn_count={self._spawn_count} "
            f"init_ms={spawn_ms:.1f}"
        )

    async def close(self) -> None:
        """Tear down the backend session and process."""
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

    async def call(self, name: str, arguments: dict[str, Any]) -> CallToolResult:
        """Forward one tool call; on connection failure respawn and retry once."""
        await self.ensure_ready()
        assert self._session is not None
        try:
            result = await self._session.call_tool(name, arguments)
            return result
        except Exception as exc:
            _log(
                f"backend_call_failed type={type(exc).__name__} msg={exc!r} "
                f"attempt=1 respawning"
            )
            await self.close()
            await self.ensure_ready()
            assert self._session is not None
            try:
                result = await self._session.call_tool(name, arguments)
                _log("backend_call_retry_succeeded")
                return result
            except Exception as exc2:
                _log(
                    f"backend_call_failed type={type(exc2).__name__} msg={exc2!r} "
                    f"attempt=2 giving_up"
                )
                raise


async def _main() -> None:
    manifest_tools = _load_manifest()
    backend_client = BackendClient()
    backend_timeout = float(os.environ.get("PROXY_BACKEND_TIMEOUT", "10.0"))

    _log(
        "proxy_started "
        f"pid={os.getpid()} "
        f"python={sys.executable} "
        f"manifest_tools={[t.name for t in manifest_tools]} "
        "backend=not_started "
        "notifications=never"
    )

    async def on_list_tools(ctx, params) -> ListToolsResult:
        _log(f"request tools/list backend_connected={backend_client.connected}")
        result = ListToolsResult(tools=manifest_tools)
        _log(
            f"response tools/list backend_connected={backend_client.connected} "
            f"tool_count={len(manifest_tools)}"
        )
        return result

    async def on_call_tool(ctx, params) -> CallToolResult:
        name = params.name
        arguments = dict(params.arguments or {})
        _log(
            f"request tools/call name={name} arguments={arguments!r} "
            f"backend_connected={backend_client.connected}"
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
        call_timeout = float(os.environ.get("PROXY_CALL_TIMEOUT", "15.0"))
        try:
            result = await asyncio.wait_for(
                backend_client.call(name, arguments),
                timeout=call_timeout,
            )
        except asyncio.TimeoutError:
            _log(f"backend_call_timeout_after_ms={call_timeout * 1000:.0f} closing_dead_client")
            await backend_client.close()
            raise
        except Exception as exc:
            _log(f"call_tool_handler_error type={type(exc).__name__} msg={exc!r}")
            await backend_client.close()
            raise
        _log(f"response tools/call name={name} ok={not getattr(result, 'isError', False)}")
        return result

    async def on_initialized_notification(ctx, params) -> None:
        _log("notification received notifications/initialized (client handshake done)")

    server = Server(
        "lazy-proxy",
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
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
    _log("connection_closed exiting")


if __name__ == "__main__":
    asyncio.run(_main())
