#!/usr/bin/env python
"""Phase: Test C — diverging schema, first exposure (the key measurement).

Fresh proxy process, fresh registry.

Setup: same cached manifest as Test B (``manifest.json`` — conforming
output_schema {"sum": number} captured when the backend declared the
schema).  The backend is then reconfigured (``response_mode=diverging``)
so its ACTUAL response is structured content ``{"result": n}`` which does
NOT conform — WITHOUT re-capturing the manifest.  The backend still
*declares* the conforming schema (``schema_mode=conforming``), matching
the brief's "change the backend's runtime return shape without
re-capturing".

Recorded:
(a) exact exception type + message verbatim (from the ErrorResult that
    ``registry.invoke`` returns; ToolRegistry 0.15.0 never raises).
(b) was the backend spawned BEFORE the failure?  (compare proxy log
    ``backend_spawn_start`` epoch vs harness failure epoch).
(c) elapsed ms from call invocation to failure — vs Test B success latency
    and #196 cold-start numbers (2155-2761 ms, n=3, max 2761 ms).
(d) does the exception surface cleanly, or as a lower-level protocol error
    / timeout / hang?  Watch whether ToolRegistry's own reconnect-retry
    layer (connection.py:106) fires — it closes the proxy client and
    spawns a FRESH proxy process (visible as a second ``proxy_started`` in
    the same log) — and whether the proxy's own internal retry
    (proxy.py ``BackendClient.call``) respawns the backend (visible as a
    second ``backend_spawn_start``).  Both are part of the cost.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_drift as common  # noqa: E402
from common_drift import (  # noqa: E402
    HERE,
    LOGS_DIR,
    count_events,
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

PHASE = "test-c"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
MANIFEST = HERE / "manifest.json"


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(f"manifest={MANIFEST.name} backend_schema_mode=conforming backend_response_mode=diverging")
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()

    registry = ToolRegistry(name="testc")
    transport = make_transport(
        str(PROXY_LOG),
        manifest=str(MANIFEST),
        backend_schema_mode="conforming",
        backend_response_mode="diverging",
    )

    hlog("TESTC_BEGIN register")
    t0 = common.now_ms()
    reg_error = None
    try:
        registry.register_from_mcp(transport)
        reg_ok = True
    except Exception as exc:
        reg_ok = False
        reg_error = exc
    t1 = common.now_ms()
    hlog(f"TESTC_REGISTER result={'ok' if reg_ok else 'FAILED'} delta_ms={t1 - t0} error={reg_error!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)

    print_manifest_schemas(MANIFEST)

    # ---- the key call: cached schema declares {"sum": ...}, backend
    # returns {"result": ...} ----
    hlog("TESTC_BEGIN call")
    call_start = common.now_ms()
    outcome = invoke_recorded(registry, "add", {"a": 2, "b": 3}, label="add(2,3)")

    # ---- post-hoc analysis of the proxy log ----
    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns = events(proxy_lines, "backend_spawn_start")
    ups = events(proxy_lines, "backend_up")
    failures = events(proxy_lines, "backend_call_failed")
    handler_errors = events(proxy_lines, "call_tool_handler_error")
    retry_ok = events(proxy_lines, "backend_call_retry_succeeded")
    pids = proxy_pids(proxy_lines)

    hlog(
        f"TESTC_SPAWN_COUNTS backend_spawn_count={len(spawns)} backend_up_count={len(ups)} "
        f"backend_call_failed_count={len(failures)} retry_succeeded_count={len(retry_ok)} "
        f"proxy_processes={len(pids)} proxy_pids={pids}"
    )
    for epoch, msg in spawns:
        hlog(f"TESTC_SPAWN_EVENT epoch={epoch} msg={msg}")
    for epoch, msg in ups:
        hlog(f"TESTC_UP_EVENT epoch={epoch} msg={msg}")
    for epoch, msg in failures:
        hlog(f"TESTC_FAILURE_EVENT epoch={epoch} msg={msg}")
    for epoch, msg in handler_errors:
        hlog(f"TESTC_HANDLER_ERROR_EVENT epoch={epoch} msg={msg}")
    for epoch, msg in events(proxy_lines, "proxy_started"):
        hlog(f"TESTC_PROXY_STARTED epoch={epoch} msg={msg}")

    # (b) was the backend spawned before the failure surfaced?
    first_spawn = first_event(proxy_lines, "backend_spawn_start")
    if first_spawn:
        hlog(
            f"TESTC_WAS_SPAWNED_BEFORE_FAILURE backend_first_spawn_epoch={first_spawn[0]} "
            f"call_start_epoch={call_start} -> backend spawned "
            f"{first_spawn[0] - call_start} ms after call invocation"
        )

    # Log the outcome detail for the report: exact exception type + message.
    if outcome is not None:
        if hasattr(outcome, "message"):
            hlog(f"TESTC_ERROR_RESULT message_verbatim={outcome.message!r}")
        elif hasattr(outcome, "result"):
            hlog(f"TESTC_UNEXPECTED_SUCCESS result={outcome.result!r}")
    else:
        hlog("TESTC_OUTCOME none (raised inside invoke, recorded above)")

    fail_ok = outcome is not None and not hasattr(outcome, "result") and hasattr(outcome, "message")
    hlog(f"TESTC_RESULT pass={fail_ok} (expected: failure; observed: {type(outcome).__name__})")
    registry.close()
    hlog(f"phase_done phase={PHASE} test_c_pass={fail_ok}")
    sys.exit(0 if fail_ok else 1)


if __name__ == "__main__":
    main()
