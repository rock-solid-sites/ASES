#!/usr/bin/env python
"""Phase: Test C2 (supplementary) — pure cached-manifest drift.

Fresh proxy process, fresh registry.

Setup: same cached manifest as Test C (``manifest.json`` — conforming
output_schema {"sum": number}).  Unlike Test C, the BACKEND'S OWN
declaration has also drifted: ``schema_mode=diverging`` (it now lists
``output_schema={"result": ...}``) and ``response_mode=diverging`` (it
returns ``{"result": n}``).  So the backend is internally CONSISTENT
(declares what it returns) and only the CACHED MANIFEST is stale.

Consequence: the proxy's own client validates the backend response against
the backend's LIVE schema ({"result": ...}) and PASSES; the result flows
through to ToolRegistry, whose client validates against the CACHED schema
({"sum": ...}) and raises the RuntimeError directly — the exact mechanism
cited in the #196 grounding (mcp/client/session.py:1096-1100).

This variant isolates the purest identifier-first drift scenario from
Test C's (backend violates its own still-declared schema).  It also
exercises the SDK's output-schema cache-miss re-list (the ToolRegistry
client issues ``tools/list`` to the proxy on its first call, absorbing the
CACHED manifest schema, then validates against it).
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

PHASE = "test-c2"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
MANIFEST = HERE / "manifest.json"


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(f"manifest={MANIFEST.name} backend_schema_mode=diverging backend_response_mode=diverging")
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()

    registry = ToolRegistry(name="testc2")
    transport = make_transport(
        str(PROXY_LOG),
        manifest=str(MANIFEST),
        backend_schema_mode="diverging",
        backend_response_mode="diverging",
    )

    hlog("TESTC2_BEGIN register")
    t0 = common.now_ms()
    reg_error = None
    try:
        registry.register_from_mcp(transport)
        reg_ok = True
    except Exception as exc:
        reg_ok = False
        reg_error = exc
    t1 = common.now_ms()
    hlog(f"TESTC2_REGISTER result={'ok' if reg_ok else 'FAILED'} delta_ms={t1 - t0} error={reg_error!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)

    print_manifest_schemas(MANIFEST)

    hlog("TESTC2_BEGIN call")
    outcome = invoke_recorded(registry, "add", {"a": 2, "b": 3}, label="add(2,3)")

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns = events(proxy_lines, "backend_spawn_start")
    ups = events(proxy_lines, "backend_up")
    failures = events(proxy_lines, "backend_call_failed")
    hlog(
        f"TESTC2_SPAWN backend_spawn_count={len(spawns)} backend_up_count={len(ups)} "
        f"backend_call_failed_count={len(failures)} proxy_processes={len(proxy_pids(proxy_lines))}"
    )
    for epoch, msg in events(proxy_lines, "proxy_started"):
        hlog(f"TESTC2_PROXY_STARTED epoch={epoch} msg={msg}")
    for epoch, msg in events(proxy_lines, "request tools/list"):
        hlog(f"TESTC2_LIST_REQUEST epoch={epoch} msg={msg}")

    if outcome is not None:
        if hasattr(outcome, "message"):
            hlog(f"TESTC2_ERROR_RESULT message_verbatim={outcome.message!r}")
        elif hasattr(outcome, "result"):
            hlog(f"TESTC2_UNEXPECTED_SUCCESS result={outcome.result!r}")

    fail_ok = outcome is not None and not hasattr(outcome, "result") and hasattr(outcome, "message")
    hlog(f"TESTC2_RESULT pass={fail_ok}")
    registry.close()
    hlog(f"phase_done phase={PHASE} test_c2_pass={fail_ok}")
    sys.exit(0 if fail_ok else 1)


if __name__ == "__main__":
    main()
