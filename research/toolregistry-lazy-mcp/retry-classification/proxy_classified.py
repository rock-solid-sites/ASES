#!/usr/bin/env python
"""Lazy stdio MCP proxy for the retry-classification investigation (#217).

This is the #213 output-schema-drift ``proxy.py`` (itself the #196 proxy)
copied into the retry-classification worktree with EXACTLY the deltas
documented here, so the report can state them precisely and the test
isolates exactly one variable:

Delta 1 (classification): on a **schema-validation failure** — a result WAS
received from the backend but the proxy's own mcp client rejected it during
output-schema validation (``mcp/client/session.py`` ``validate_tool_result``
raises ``RuntimeError("Invalid structured content returned by tool ...")``) —
the proxy treats the failure as TERMINAL:

  * it does NOT run its reflexive respawn + single retry (the ``except
    Exception`` respawn path in ``BackendClient.call`` is bypassed for this
    failure class only);
  * it raises the internal marker :class:`SchemaValidationFailure` instead of
    the raw ``RuntimeError``, so the stdio dispatcher is never given an
    exception to convert into a JSON-RPC error response;
  * ``on_call_tool`` catches the marker and returns a **normal MCP tool-error
    response** — ``CallToolResult(isError=True, content=[text])`` with the
    full schema-error text — which ToolRegistry 0.15.0's
    ``_call_persistent`` (toolregistry/integrations/mcp/connection.py:106)
    returns without raising, so its catch-all reconnect-retry has nothing to
    treat as connection loss.

Delta 2 (test instrumentation only): ``PROXY_PID_FILE`` env var, optional,
writes this proxy process's pid at startup (same pattern as the backend's
``BACKEND_PID_FILE``).  Used by Test 3 to kill the persistent proxy
mid-call.  Not MCP behaviour; does not alter protocol handling.

Everything else is byte-for-byte the #213 drift proxy: lazy spawn on first
``tools/call``, one reused session, respawn + single retry on ACTUAL
connection failures (the ``except Exception`` path that is NOT the
schema-validation signature), cached ``tools/list`` served statically,
no notifications, ``PROXY_MANIFEST`` / ``BACKEND_*`` env passthrough.

Environment variables understood by the proxy:
    PROXY_LOG_FILE      : optional path to append proxy log lines to.
    PROXY_PID_FILE      : optional path to write this proxy's pid at start
                          (Delta 2, test instrumentation).
    PROXY_MANIFEST      : optional path to the cached manifest to serve
                          (default: ./manifest.json).
    PROXY_BACKEND_TIMEOUT: optional float, seconds to wait for the backend
                           initialize handshake (default 10.0).
    PROXY_CALL_TIMEOUT  : optional float, seconds to bound one forwarded
                          tools/call including its respawn retry
                          (default 15.0).
    BACKEND_*           : passed through to the backend subprocess
                          (BACKEND_INSTANCE_ID, BACKEND_PID_FILE,
                          BACKEND_SCHEMA_MODE, BACKEND_RESPONSE_MODE, ...).
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
from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool
from mcp_types import NotificationParams

HERE = Path(__file__).resolve().parent
MANIFEST_PATH = Path(os.environ.get("PROXY_MANIFEST", str(HERE / "manifest.json")))
BACKEND_PATH = HERE / "backend.py"

_START_EPOCH_MS = int(time.time() * 1000)

# The mcp SDK's output-schema validation raises exactly this RuntimeError
# (mcp/client/session.py validate_tool_result) when a result is received
# but does not conform to the tool's declared output schema.  Real
# connection failures surface as MCPError(-32000, 'Connection closed')
# / EOF / transport errors -- never this message -- so the signature cleanly
# separates the terminal schema-validation class from connection failures
# (verified empirically, see report §3.2).
_SCHEMA_VALIDATION_MARKER = "Invalid structured content returned by tool"


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


class SchemaValidationFailure(Exception):
    """Internal marker: backend responded, but its result failed schema validation.

    Raised by :class:`BackendClient` instead of the raw ``RuntimeError`` so
    ``on_call_tool`` can convert it into a normal MCP tool-error response and
    the stdio dispatcher never emits a JSON-RPC error response.
    """


def _is_schema_validation_error(exc: BaseException) -> bool:
    return (
        isinstance(exc, RuntimeError)
        and _SCHEMA_VALIDATION_MARKER in str(exc)
    )


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
            key: value
            for key, value in os.environ.items()
            if key.startswith("BACKEND_")
        }
        env.setdefault("BACKEND_INSTANCE_ID", self._instance_id)
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
        """Forward one tool call; classify schema failures, respawn on connection loss.

        Delta 1: a schema-validation failure (result received, rejected by the
        proxy's own output-schema validation) is TERMINAL -- no respawn, no
        retry -- and is re-raised as :class:`SchemaValidationFailure`.  Any
        other failure (actual connection loss) keeps the #213 behaviour:
        close, respawn, single retry.
        """
        await self.ensure_ready()
        assert self._session is not None
        try:
            result = await self._session.call_tool(name, arguments)
            return result
        except Exception as exc:
            if _is_schema_validation_error(exc):
                _log(
                    f"backend_schema_validation_failed type={type(exc).__name__} "
                    f"terminal=yes respawn=no instance_id={self._instance_id} "
                    f"msg={exc!r}"
                )
                raise SchemaValidationFailure(str(exc)) from exc
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

    pid_file = os.environ.get("PROXY_PID_FILE")
    if pid_file:
        try:
            with open(pid_file, "w", encoding="utf-8") as fh:
                fh.write(str(os.getpid()))
            _log(f"pid_file_written path={pid_file} pid={os.getpid()}")
        except OSError as exc:
            _log(f"pid_file_write_error path={pid_file} error={exc}")

    _log(
        "proxy_started "
        f"pid={os.getpid()} "
        f"python={sys.executable} "
        f"manifest={MANIFEST_PATH.name} "
        f"manifest_tools={[t.name for t in manifest_tools]} "
        "backend=not_started "
        "notifications=never"
    )

    async def on_list_tools(ctx, params) -> ListToolsResult:
        _log(f"request tools/list backend_connected={backend_client.connected}")
        return ListToolsResult(tools=manifest_tools)

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
        except SchemaValidationFailure as exc:
            # Delta 1: normal MCP tool-error response, NOT a raise.  The
            # backend responded; its result failed output-schema validation
            # against the cached schema.  Returning isError=True keeps the
            # stdio dispatcher from emitting a JSON-RPC error, so ToolRegistry
            # 0.15.0's _call_persistent sees a normal CallToolResult and its
            # reconnect-retry (connection.py:106) does not fire.
            _log(
                f"call_tool_classified_schema_failure name={name} "
                f"returning_tool_error_response msg={exc!r}"
            )
            return CallToolResult(
                content=[TextContent(type="text", text=str(exc))],
                isError=True,
            )
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
