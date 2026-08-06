#!/usr/bin/env python
"""Phase: Test 2 -- MODIFIED proxy (proxy_classified.py), same drift scenario.

Identical setup to Test 1 (cached manifest.json, backend schema_mode=
conforming + response_mode=diverging) but the transport points at
``proxy_classified.py``, which classifies the schema-validation failure as
terminal and returns a normal MCP tool-error response (isError=True) instead
of raising.

Expected per the hypothesis:
  (a) backend spawn count = 1, persistent proxy count = 1 (+1 registration),
      reconnect-retry does NOT fire (proxy_started count == 2: registration
      temp + one persistent).
  (b) caller-visible outcome is ToolRegistry 0.15.0's stringified
      CallToolResult repr carrying is_error=True + the full schema error
      (captured verbatim); NOT an ErrorResult (see report: ToolRegistry
      stringifies isError responses -- the classification removes the
      exception that produced the ErrorResult).
  (c) failure latency vs Test 1 control and vs #213 success baseline.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_retry as common  # noqa: E402
from common_retry import (  # noqa: E402
    CLASSIFIED_ERROR_MARKERS,
    CLASSIFIED_PROXY,
    HERE,
    LOGS_DIR,
    events,
    first_event,
    hlog,
    invoke_recorded,
    make_transport,
    print_manifest_schemas,
    proxy_pids,
    read_proxy_log,
    versions_line,
)
from toolregistry import ToolRegistry  # noqa: E402

PHASE = "test-2-classified"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
MANIFEST = HERE / "manifest.json"


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(
        f"proxy=MODIFIED({CLASSIFIED_PROXY.name}) "
        f"manifest={MANIFEST.name} backend_schema_mode=conforming backend_response_mode=diverging"
    )
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()

    registry = ToolRegistry(name="test2")
    transport = make_transport(
        str(PROXY_LOG),
        proxy_path=CLASSIFIED_PROXY,
        manifest=str(MANIFEST),
        backend_schema_mode="conforming",
        backend_response_mode="diverging",
    )

    hlog("TEST2_BEGIN register")
    t0 = common.now_ms()
    reg_error = None
    try:
        registry.register_from_mcp(transport)
        reg_ok = True
    except Exception as exc:
        reg_ok = False
        reg_error = exc
    t1 = common.now_ms()
    hlog(f"TEST2_REGISTER result={'ok' if reg_ok else 'FAILED'} delta_ms={t1 - t0} error={reg_error!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)

    print_manifest_schemas(MANIFEST)

    hlog("TEST2_BEGIN call")
    outcome = invoke_recorded(registry, "add", {"a": 2, "b": 3}, label="add(2,3)")

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns = events(proxy_lines, "backend_spawn_start")
    ups = events(proxy_lines, "backend_up")
    failures = events(proxy_lines, "backend_call_failed")
    schema_failures = events(proxy_lines, "backend_schema_validation_failed")
    classified_responses = events(proxy_lines, "call_tool_classified_schema_failure")
    retry_ok = events(proxy_lines, "backend_call_retry_succeeded")
    handler_errors = events(proxy_lines, "call_tool_handler_error")
    pids = proxy_pids(proxy_lines)

    persistent_proxies = max(0, len(pids) - 1)  # minus the registration-time temp proxy
    reconnect_fired = len(pids) > 2

    hlog(
        f"TEST2_SPAWN_COUNTS backend_spawn_count={len(spawns)} backend_up_count={len(ups)} "
        f"backend_call_failed_count={len(failures)} backend_schema_validation_failed_count={len(schema_failures)} "
        f"classified_response_count={len(classified_responses)} retry_succeeded_count={len(retry_ok)} "
        f"handler_error_count={len(handler_errors)} "
        f"proxy_processes={len(pids)} persistent_proxies={persistent_proxies} "
        f"reconnect_fired={reconnect_fired} proxy_pids={pids}"
    )
    for epoch, msg in spawns:
        hlog(f"TEST2_SPAWN_EVENT epoch={epoch} msg={msg}")
    for epoch, msg in ups:
        hlog(f"TEST2_UP_EVENT epoch={epoch} msg={msg}")
    for epoch, msg in schema_failures:
        hlog(f"TEST2_SCHEMA_FAILURE_EVENT epoch={epoch} msg={msg}")
    for epoch, msg in classified_responses:
        hlog(f"TEST2_CLASSIFIED_RESPONSE_EVENT epoch={epoch} msg={msg}")
    for epoch, msg in events(proxy_lines, "proxy_started"):
        hlog(f"TEST2_PROXY_STARTED epoch={epoch} msg={msg}")

    first_spawn = first_event(proxy_lines, "backend_spawn_start")
    if first_spawn:
        hlog(f"TEST2_FIRST_SPAWN epoch={first_spawn[0]} msg={first_spawn[1]}")

    # (d) was the caller-visible error still clear + attributable?
    error_preserved = False
    if outcome is not None:
        if hasattr(outcome, "message"):
            error_preserved = any(marker in outcome.message for marker in CLASSIFIED_ERROR_MARKERS)
        elif hasattr(outcome, "result"):
            result_str = repr(outcome.result)
            error_preserved = all(marker in result_str for marker in CLASSIFIED_ERROR_MARKERS)

    fail_ok = (
        outcome is not None
        and len(spawns) == 1
        and not reconnect_fired
        and error_preserved
    )
    hlog(
        f"TEST2_RESULT pass={fail_ok} "
        f"(expected: 1 backend spawn, no reconnect, error text preserved; observed: "
        f"spawns={len(spawns)} reconnect={reconnect_fired} error_preserved={error_preserved})"
    )
    registry.close()
    hlog(f"phase_done phase={PHASE} test2_classified_pass={fail_ok}")
    sys.exit(0 if fail_ok else 1)


if __name__ == "__main__":
    main()
