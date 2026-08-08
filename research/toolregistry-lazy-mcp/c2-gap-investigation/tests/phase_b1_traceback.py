#!/usr/bin/env python
"""Phase B1 — Option B: reproduce C2 with FULL tracebacks captured.

Reproduces the #213 Test C2 scenario (cached manifest ``{"sum": ...}``,
backend schema_mode=diverging + response_mode=diverging) against the
UNMODIFIED #213 drift proxy, exactly as before — but with runtime
instrumentation at the ToolRegistry client boundary so the COMPLETE call
stack is captured, not just the top-level ``ErrorResult.message``.

Instrumentation (runtime monkeypatch in the harness process only; the
installed packages are not modified): ``MCPClient.call_tool`` is wrapped to
print ``traceback.format_exc()`` whenever an exception crosses ToolRegistry's
client boundary.  The traceback frames show the full chain from the
reconnect trigger (connection.py:106 catch in ``_call_persistent``, the
calling frame) down to where the schema-validation exception actually
originates (``mcp/client/session.py:1110`` ``validate_tool_result``) —
answering "SDK code vs ToolRegistry code" with evidence.
"""

from __future__ import annotations

import sys
import time
import traceback as tb_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_c2 as common  # noqa: E402
from common_c2 import (  # noqa: E402
    DRIFT_PROXY,
    HERE,
    LOGS_DIR,
    events,
    hlog,
    invoke_recorded,
    make_transport,
    proxy_pids,
    read_proxy_log,
    versions_line,
)
from toolregistry import ToolRegistry  # noqa: E402
import toolregistry.integrations.mcp.client as tr_client  # noqa: E402

PHASE = "phase-b1-traceback"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
MANIFEST = HERE / "manifest.json"


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(
        f"proxy=CONTROL({DRIFT_PROXY.name}) manifest={MANIFEST.name} "
        f"backend_schema_mode=diverging backend_response_mode=diverging "
        f"instrumentation=MCPClient.call_tool"
    )
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()

    # --- runtime instrumentation: capture full traceback at the client
    # boundary, both for the FIRST attempt (which triggers the reconnect)
    # and the retried attempt (which surfaces to the caller). -----------
    _orig_call_tool = tr_client.MCPClient.call_tool

    async def traced_call_tool(self, name, arguments):
        try:
            return await _orig_call_tool(self, name, arguments)
        except Exception as exc:
            hlog(
                f"B1_TRACE_AT_MCPCLIENT type={type(exc).__name__} msg={exc!r} "
                f"tool={name}"
            )
            hlog("B1_TRACEBACK_BEGIN")
            for line in tb_module.format_exc().splitlines():
                hlog(f"B1_TB {line}")
            hlog("B1_TRACEBACK_END")
            raise

    tr_client.MCPClient.call_tool = traced_call_tool

    registry = ToolRegistry(name="b1trace")
    transport = make_transport(
        str(PROXY_LOG),
        proxy_path=DRIFT_PROXY,
        manifest=str(MANIFEST),
        backend_schema_mode="diverging",
        backend_response_mode="diverging",
    )

    hlog("B1_BEGIN register")
    try:
        registry.register_from_mcp(transport)
        reg_ok = True
    except Exception as exc:
        reg_ok = False
        hlog(f"B1_REGISTER_FAILED error={exc!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)

    hlog("B1_BEGIN call")
    outcome = invoke_recorded(registry, "add", {"a": 2, "b": 3}, label="add(2,3)")

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns = events(proxy_lines, "backend_spawn_start")
    ups = events(proxy_lines, "backend_up")
    pids = proxy_pids(proxy_lines)
    persistent = max(0, len(pids) - 1)
    hlog(
        f"B1_SPAWN_COUNTS backend_spawn_count={len(spawns)} backend_up_count={len(ups)} "
        f"proxy_processes={len(pids)} persistent_proxies={persistent} "
        f"reconnect_fired={len(pids) > 2} proxy_pids={pids}"
    )
    for epoch, msg in events(proxy_lines, "proxy_started"):
        hlog(f"B1_PROXY_STARTED epoch={epoch} msg={msg}")

    error_ok = (
        outcome is not None
        and hasattr(outcome, "message")
        and common.SCHEMA_VALIDATION_MARKER in outcome.message
    )
    hlog(
        f"B1_RESULT pass={error_ok} spawns={len(spawns)} proxies={len(pids)} "
        f"reconnect={len(pids) > 2} error_marker_present={error_ok}"
    )
    registry.close()
    hlog(f"phase_done phase={PHASE} traceback_c2_pass={error_ok}")
    sys.exit(0 if error_ok else 1)


if __name__ == "__main__":
    main()
