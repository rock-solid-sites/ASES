#!/usr/bin/env python
"""Lazy stdio MCP proxy with proxy-side self-healing (#228 Option A).

This is the #213 output-schema-drift ``proxy.py`` (itself the #196 proxy)
copied into the c2-gap-investigation worktree and extended with a
**self-healing** behaviour, documented here so the report can state the
deltas precisely:

DELTA A (self-healing): the proxy validates every forwarded backend
response's ``structured_content`` against the **proxy's OWN served
manifest** ``output_schema`` for that tool (in addition to the mcp SDK's
normal validation against the backend's live schema, which happens inside
``BackendClient.call``).  When a response does NOT conform to the schema
the proxy itself serves:

  * a per-tool **consecutive-failure counter** is incremented (reset to 0
    whenever a response conforms);
  * when the counter reaches ``PROXY_HEAL_THRESHOLD`` (default 1 = strictest
    policy; the brief says start at N=1 before testing looser), the proxy
    **self-heals**: it re-lists the LIVE backend via its existing client
    session (``BackendClient.list_live_tools``), captures the tool's live
    declared ``output_schema``, and updates the proxy's OWN in-memory served
    manifest to match — so subsequent ``tools/list`` responses (and hence
    ToolRegistry's cache-miss re-absorb, ``mcp/client/session.py:1276``)
    carry the corrected schema;
  * every heal event is logged (what changed, when, which call triggered
    it) as ``self_heal`` lines.

The heal is persisted to ``PROXY_HEAL_STATE`` (a JSON file the proxy reads
at startup instead of the static manifest), so a ToolRegistry
reconnect-respawned proxy process also serves the corrected schema — this
is what lets the retried call after a reconnect succeed instead of failing
again with the same stale schema.

DELTA B (intermittent test support): ``PROXY_BACKEND_SCRIPT`` env var,
optional, lets the tests point the proxy at a backend variant (used by the
intermittent-drift flapping check).  Defaults to ``backend.py`` next to this
file, byte-identical to the #213 backend.

DELTA C (classification, optional): ``PROXY_CLASSIFY_SCHEMA=1`` restores the
#217 retry-classification behaviour on top of self-healing — a schema-
validation failure detected by the proxy's OWN client (Test C signature:
the backend violates its own live declared schema, so the mcp SDK raises
``RuntimeError("Invalid structured content returned by tool ...")`` inside
``BackendClient.call``) is treated as TERMINAL: no respawn, and a normal MCP
tool-error response (``CallToolResult(isError=True, ...)``) is returned
instead of a raise.  This exists so the intermittent-drift flapping check
can measure whether self-healing preserves the #217 benefit ("must not be
made worse") — without it, a plain self-heal proxy regresses Test-C-style
intermittent drift to the #213 4x cost.  For the C2 scenario (backend
internally consistent) this delta never fires.

Everything else is byte-for-byte the #213 drift proxy: lazy spawn on first
``tools/call``, one reused session, respawn + single retry on ACTUAL
connection failures, cached ``tools/list`` served statically (until a heal
updates it), no notifications, ``PROXY_MANIFEST`` / ``BACKEND_*`` env
passthrough.

Environment variables understood by the proxy:
    PROXY_LOG_FILE       : optional path to append proxy log lines to.
    PROXY_MANIFEST       : optional path to the cached manifest to serve
                           (default: ./manifest.json).
    PROXY_HEAL_STATE     : optional path to a JSON file that, when present,
                           is loaded at startup INSTEAD of the static
                           manifest (the persisted healed manifest); the
                           proxy also writes it after every heal.
    PROXY_HEAL_THRESHOLD : optional int, consecutive schema-validation
                           failures per tool that trigger a heal (default 1).
    PROXY_BACKEND_SCRIPT : optional path to the backend script (default:
                           ./backend.py).
    PROXY_BACKEND_TIMEOUT: optional float, seconds to wait for the backend
                           initialize handshake (default 10.0).
    PROXY_CALL_TIMEOUT   : optional float, seconds to bound one forwarded
                           tools/call including its respawn retry
                           (default 15.0).
    BACKEND_*            : passed through to the backend subprocess
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
from mcp.types import CallToolResult, ListToolsResult, Tool
from mcp_types import NotificationParams

HERE = Path(__file__).resolve().parent
MANIFEST_PATH = Path(os.environ.get("PROXY_MANIFEST", str(HERE / "manifest.json")))
HEAL_STATE_PATH = os.environ.get("PROXY_HEAL_STATE")
HEAL_THRESHOLD = int(os.environ.get("PROXY_HEAL_THRESHOLD", "1"))
CLASSIFY_SCHEMA = os.environ.get("PROXY_CLASSIFY_SCHEMA", "0") == "1"
BACKEND_PATH = Path(
    os.environ.get("PROXY_BACKEND_SCRIPT", str(HERE / "backend.py"))
)

# The mcp SDK's output-schema validation raises exactly this RuntimeError
# (mcp/client/session.py validate_tool_result) when the backend's response
# violates the schema the proxy's OWN client session absorbed from the
# backend's LIVE declaration.  Real connection failures surface as
# MCPError(-32000, 'Connection closed') — never this message — so the
# signature cleanly separates the terminal schema-validation class from
# connection failures (verified empirically in #217).
_SCHEMA_VALIDATION_MARKER = "Invalid structured content returned by tool"

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


def _load_healed_manifest() -> list[Tool] | None:
    """Load the persisted healed manifest if present (returns None otherwise).

    The file is the same shape as the static manifest (a JSON object with a
    ``tools`` list, or a bare list).  Used at startup so a reconnect-respawned
    proxy serves the corrected schema.
    """
    if not HEAL_STATE_PATH:
        return None
    p = Path(HEAL_STATE_PATH)
    if not p.exists():
        return None
    try:
        with open(p, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        _log(f"heal_state_load_error path={p} error={exc!r}")
        return None
    tools = raw.get("tools", raw) if isinstance(raw, dict) else raw
    try:
        healed = [Tool.model_validate(t) for t in tools]
    except Exception as exc:
        _log(f"heal_state_parse_error path={p} error={exc!r}")
        return None
    _log(
        f"heal_state_loaded path={p.name} "
        f"tools={[t.name for t in healed]} "
        f"schemas={[t.output_schema for t in healed]}"
    )
    return healed


def _persist_healed_manifest(tools: list[Tool]) -> None:
    if not HEAL_STATE_PATH:
        return
    p = Path(HEAL_STATE_PATH)
    payload = {
        "captured_with": {
            "healed_by": "proxy_self_heal.py",
            "healed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "toolcount": len(tools),
        },
        "tools": [t.model_dump(mode="json") for t in tools],
    }
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        _log(f"heal_state_written path={p} tools={[t.name for t in tools]}")
    except OSError as exc:
        _log(f"heal_state_write_error path={p} error={exc!r}")


def _validate_against_served(tool: Tool, result: CallToolResult) -> str | None:
    """Validate a backend response against the proxy's OWN served schema.

    Returns None when the response conforms (or the tool declares no output
    schema, or the response has no structured content to validate); returns
    the jsonschema error message otherwise.  This is DELTA A's drift signal:
    the proxy can detect a stale cached manifest even when the backend is
    internally consistent (C2: declaration and behaviour both diverged),
    because the response no longer matches what the proxy itself serves.
    """
    schema = tool.output_schema
    if schema is None:
        return None
    structured = result.structured_content
    if structured is None:
        return f"served schema requires structured content, backend returned none"
    import jsonschema

    try:
        jsonschema.validate(instance=structured, schema=schema)
        return None
    except jsonschema.ValidationError as exc:
        return exc.message


def _is_schema_validation_error(exc: BaseException) -> bool:
    return (
        isinstance(exc, RuntimeError)
        and _SCHEMA_VALIDATION_MARKER in str(exc)
    )


class SchemaValidationFailure(Exception):
    """Internal marker (DELTA C, classification): backend responded but its
    result failed schema validation in the proxy's OWN client.

    Raised by :class:`BackendClient` instead of the raw ``RuntimeError`` so
    ``on_call_tool`` can convert it into a normal MCP tool-error response
    when classification is enabled.
    """


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
        # #213 delta: pass through ALL BACKEND_* env vars so the drift
        # backend's schema/response modes can be controlled per test.
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

    async def list_live_tools(self) -> list[Tool]:
        """DELTA A: re-list the LIVE backend's tools to capture the real schema."""
        await self.ensure_ready()
        assert self._session is not None
        listing = await self._session.list_tools()
        _log(
            f"live_tools_listed instance_id={self._instance_id} "
            f"tools={[t.name for t in listing.tools]} "
            f"schemas={[t.output_schema for t in listing.tools]}"
        )
        return list(listing.tools)

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
        """Forward one tool call; on connection failure respawn and retry once.

        DELTA C: when ``PROXY_CLASSIFY_SCHEMA=1``, a schema-validation failure
        raised by the proxy's OWN client (the backend violated its own live
        declared schema — Test C signature) is TERMINAL: no respawn/retry,
        re-raised as :class:`SchemaValidationFailure`.  Any other failure
        (actual connection loss) keeps the #213 behaviour: close, respawn,
        single retry.
        """
        await self.ensure_ready()
        assert self._session is not None
        try:
            result = await self._session.call_tool(name, arguments)
            return result
        except Exception as exc:
            if CLASSIFY_SCHEMA and _is_schema_validation_error(exc):
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


class SelfHealingManifest:
    """Mutable served-manifest state with per-tool failure counters (DELTA A).

    The proxy serves this instead of a static list, so a heal can update the
    schema for one tool without touching any other tool.
    """

    def __init__(self, tools: list[Tool]) -> None:
        self.tools: list[Tool] = tools
        self.failure_counts: dict[str, int] = {}

    def snapshot(self) -> dict[str, Any]:
        return {
            t.name: (t.output_schema if isinstance(t.output_schema, dict) else None)
            for t in self.tools
        }

    def find(self, name: str) -> Tool | None:
        for t in self.tools:
            if t.name == name:
                return t
        return None

    def heal_tool_schema(self, name: str, live_schema: Any) -> None:
        """Replace the served output_schema for one tool with the live schema."""
        for i, t in enumerate(self.tools):
            if t.name == name:
                new_tool = t.model_copy(update={"output_schema": live_schema})
                self.tools[i] = new_tool
                self.failure_counts[name] = 0
                return

    def reset_failure(self, name: str) -> None:
        self.failure_counts[name] = 0


async def _main() -> None:
    # Startup manifest: the persisted healed state (if any) wins over the
    # static cached manifest, so a reconnect-respawned proxy keeps serving
    # the corrected schema.
    healed = _load_healed_manifest()
    manifest = SelfHealingManifest(healed if healed is not None else _load_manifest())
    backend_client = BackendClient()
    backend_timeout = float(os.environ.get("PROXY_BACKEND_TIMEOUT", "10.0"))

    _log(
        "proxy_started "
        f"pid={os.getpid()} "
        f"python={sys.executable} "
        f"manifest={MANIFEST_PATH.name} "
        f"heal_threshold={HEAL_THRESHOLD} "
        f"heal_state={'on' if HEAL_STATE_PATH else 'off'} "
        f"manifest_tools={[t.name for t in manifest.tools]} "
        "backend=not_started "
        "notifications=never"
    )

    async def on_list_tools(ctx, params) -> ListToolsResult:
        _log(
            f"request tools/list backend_connected={backend_client.connected} "
            f"served={manifest.snapshot()}"
        )
        return ListToolsResult(tools=manifest.tools)

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
            # DELTA C: normal MCP tool-error response, NOT a raise.  The
            # backend responded but its result failed the proxy's OWN client
            # validation (Test C signature).  Returning isError=True keeps the
            # stdio dispatcher from emitting a JSON-RPC error, so ToolRegistry
            # 0.15.0's _call_persistent sees a normal CallToolResult and its
            # reconnect-retry (connection.py:106) does not fire.
            _log(
                f"call_tool_classified_schema_failure name={name} "
                f"returning_tool_error_response msg={exc!r}"
            )
            return CallToolResult(
                content=[{"type": "text", "text": str(exc)}],
                isError=True,
            )
        except Exception as exc:
            _log(f"call_tool_handler_error type={type(exc).__name__} msg={exc!r}")
            await backend_client.close()
            raise

        # ---- DELTA A: self-heal detection + heal ----------------------
        served_tool = manifest.find(name)
        if served_tool is not None:
            mismatch = _validate_against_served(served_tool, result)
            if mismatch is None:
                manifest.reset_failure(name)
                _log(
                    f"self_check ok name={name} "
                    f"failure_counts={manifest.failure_counts}"
                )
            else:
                prev_count = manifest.failure_counts.get(name, 0) + 1
                manifest.failure_counts[name] = prev_count
                _log(
                    f"self_check_failed name={name} consecutive={prev_count} "
                    f"threshold={HEAL_THRESHOLD} mismatch={mismatch!r} "
                    f"served_schema={served_tool.output_schema}"
                )
                if prev_count >= HEAL_THRESHOLD:
                    before = manifest.snapshot()
                    live_tools = await backend_client.list_live_tools()
                    live_tool = next((t for t in live_tools if t.name == name), None)
                    if live_tool is not None and live_tool.output_schema != served_tool.output_schema:
                        manifest.heal_tool_schema(name, live_tool.output_schema)
                        _persist_healed_manifest(manifest.tools)
                        after = manifest.snapshot()
                        _log(
                            f"self_heal name={name} trigger_call={name}({arguments!r}) "
                            f"before_schema={before.get(name)!r} "
                            f"after_schema={after.get(name)!r} "
                            f"live_schema={live_tool.output_schema} "
                            f"served_after={after}"
                        )
                    else:
                        _log(
                            f"self_heal_skipped name={name} live_schema_matches_served_or_missing "
                            f"live_schema={getattr(live_tool, 'output_schema', None)!r}"
                        )
        # -----------------------------------------------------------------

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
