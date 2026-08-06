#!/usr/bin/env python
"""Phase: Test 1 -- CONTROL, reconfirm the 4x multiplier (#213 Test C).

Runs the ORIGINAL unmodified #213 drift proxy (output-schema-drift/proxy.py)
with the exact Test C scenario: cached manifest.json (conforming output
schema {"sum": ...}), backend schema_mode=conforming + response_mode=diverging
(returns structured_content {"result": n}).

Expected (per #213): 4 backend spawns, 2 persistent proxies (+1
registration proxy), reconnect-retry fires (proxy_started count > 2), an
ErrorResult whose message starts "MCPError: Error executing add: Invalid
structured content returned by tool add: ...".

Recorded: backend spawn count, proxy process count, reconnect-fire YES/NO,
failure latency, error message verbatim.  This is the before baseline for
the Test 1 vs Test 2 comparison.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_retry as common  # noqa: E402
from common_retry import (  # noqa: E402
    DRIFT_PROXY,
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

PHASE = "test-1-control"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
MANIFEST = HERE / "manifest.json"


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(
        f"proxy=ORIGINAL_drift({DRIFT_PROXY.name}) "
        f"manifest={MANIFEST.name} backend_schema_mode=conforming backend_response_mode=diverging"
    )
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()

    registry = ToolRegistry(name="test1")
    transport = make_transport(
        str(PROXY_LOG),
        proxy_path=DRIFT_PROXY,
        manifest=str(MANIFEST),
        backend_schema_mode="conforming",
        backend_response_mode="diverging",
    )

    hlog("TEST1_BEGIN register")
    t0 = common.now_ms()
    reg_error = None
    try:
        registry.register_from_mcp(transport)
        reg_ok = True
    except Exception as exc:
        reg_ok = False
        reg_error = exc
    t1 = common.now_ms()
    hlog(f"TEST1_REGISTER result={'ok' if reg_ok else 'FAILED'} delta_ms={t1 - t0} error={reg_error!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)

    print_manifest_schemas(MANIFEST)

    hlog("TEST1_BEGIN call")
    outcome = invoke_recorded(registry, "add", {"a": 2, "b": 3}, label="add(2,3)")

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns = events(proxy_lines, "backend_spawn_start")
    ups = events(proxy_lines, "backend_up")
    failures = events(proxy_lines, "backend_call_failed")
    handler_errors = events(proxy_lines, "call_tool_handler_error")
    schema_failures = events(proxy_lines, "backend_schema_validation_failed")
    pids = proxy_pids(proxy_lines)

    persistent_proxies = max(0, len(pids) - 1)  # minus the registration-time temp proxy
    reconnect_fired = len(pids) > 2

    hlog(
        f"TEST1_SPAWN_COUNTS backend_spawn_count={len(spawns)} backend_up_count={len(ups)} "
        f"backend_call_failed_count={len(failures)} backend_schema_validation_failed_count={len(schema_failures)} "
        f"proxy_processes={len(pids)} persistent_proxies={persistent_proxies} "
        f"reconnect_fired={reconnect_fired} proxy_pids={pids}"
    )
    for epoch, msg in spawns:
        hlog(f"TEST1_SPAWN_EVENT epoch={epoch} msg={msg}")
    for epoch, msg in ups:
        hlog(f"TEST1_UP_EVENT epoch={epoch} msg={msg}")
    for epoch, msg in failures:
        hlog(f"TEST1_FAILURE_EVENT epoch={epoch} msg={msg}")
    for epoch, msg in events(proxy_lines, "proxy_started"):
        hlog(f"TEST1_PROXY_STARTED epoch={epoch} msg={msg}")

    first_spawn = first_event(proxy_lines, "backend_spawn_start")
    if first_spawn:
        hlog(f"TEST1_FIRST_SPAWN epoch={first_spawn[0]} msg={first_spawn[1]}")

    fail_ok = outcome is not None and hasattr(outcome, "message")
    hlog(
        f"TEST1_RESULT pass={fail_ok} (expected: ErrorResult with MCPError message; "
        f"observed: {type(outcome).__name__})"
    )
    registry.close()
    hlog(f"phase_done phase={PHASE} test1_control_pass={fail_ok}")
    sys.exit(0 if fail_ok else 1)


if __name__ == "__main__":
    main()
