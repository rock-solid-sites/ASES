#!/usr/bin/env python
"""Phase A1 — CONTROL: C2 scenario against the ORIGINAL #213 drift proxy.

Matched-run baseline for the Option A comparison.  Setup is exactly the
#213 Test C2 scenario: cached manifest declares ``{"sum": ...}`` for ``add``,
backend ``schema_mode=diverging`` + ``response_mode=diverging`` (internally
consistent — only the cached manifest is stale), proxy = the UNMODIFIED
output-schema-drift/proxy.py.

Expected (reconfirming #213 C2): 2 backend spawns, 2 persistent proxies,
reconnect-retry fires, caller-visible ``ErrorResult`` whose message carries
the SDK's ``RuntimeError`` schema-validation text.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_c2 as common  # noqa: E402
from common_c2 import (  # noqa: E402
    DRIFT_PROXY,
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

PHASE = "phase-a1-control"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
MANIFEST = HERE / "manifest.json"


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(
        f"proxy=CONTROL({DRIFT_PROXY.name}) manifest={MANIFEST.name} "
        f"backend_schema_mode=diverging backend_response_mode=diverging"
    )
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()

    registry = ToolRegistry(name="a1control")
    transport = make_transport(
        str(PROXY_LOG),
        proxy_path=DRIFT_PROXY,
        manifest=str(MANIFEST),
        backend_schema_mode="diverging",
        backend_response_mode="diverging",
    )

    hlog("A1_BEGIN register")
    t0 = common.now_ms()
    try:
        registry.register_from_mcp(transport)
        reg_ok = True
        reg_error = None
    except Exception as exc:
        reg_ok = False
        reg_error = exc
    t1 = common.now_ms()
    hlog(f"A1_REGISTER result={'ok' if reg_ok else 'FAILED'} delta_ms={t1 - t0} error={reg_error!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)

    print_manifest_schemas(MANIFEST)

    hlog("A1_BEGIN call")
    outcome = invoke_recorded(registry, "add", {"a": 2, "b": 3}, label="add(2,3)")

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns = events(proxy_lines, "backend_spawn_start")
    ups = events(proxy_lines, "backend_up")
    failures = events(proxy_lines, "backend_call_failed")
    pids = proxy_pids(proxy_lines)
    persistent_proxies = max(0, len(pids) - 1)
    reconnect_fired = len(pids) > 2
    hlog(
        f"A1_SPAWN_COUNTS backend_spawn_count={len(spawns)} backend_up_count={len(ups)} "
        f"backend_call_failed_count={len(failures)} proxy_processes={len(pids)} "
        f"persistent_proxies={persistent_proxies} reconnect_fired={reconnect_fired} "
        f"proxy_pids={pids}"
    )
    for epoch, msg in events(proxy_lines, "proxy_started"):
        hlog(f"A1_PROXY_STARTED epoch={epoch} msg={msg}")

    error_ok = (
        outcome is not None
        and hasattr(outcome, "message")
        and common.SCHEMA_VALIDATION_MARKER in outcome.message
    )
    hlog(
        f"A1_RESULT pass={error_ok} spawns={len(spawns)} proxies={len(pids)} "
        f"reconnect={reconnect_fired} error_marker_present={error_ok}"
    )
    registry.close()
    hlog(f"phase_done phase={PHASE} control_c2_pass={error_ok}")
    sys.exit(0 if error_ok else 1)


if __name__ == "__main__":
    main()
