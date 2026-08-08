#!/usr/bin/env python
"""Phase A2 — Option A: C2 scenario against proxy_self_heal.py, N=1.

Same C2 setup as the control (cached manifest ``{"sum": ...}``, backend
schema_mode=diverging + response_mode=diverging) but the proxy is the
self-healing proxy with heal threshold 1.  Repeated calls to the affected
tool across one session, then the unrelated tool.

Measures, per call: backend spawn increment, persistent proxy count,
reconnect fired, heal events, outcome class, latency.  Also captures the
served-manifest snapshots from ``tools/list`` to verify OTHER tools are
untouched by the heal.

Expected best case (N=1): the proxy detects the drift on the FIRST call's
response (served-manifest self-check), heals before returning, and
ToolRegistry's cache-miss re-absorb (session.py:1086) picks up the corrected
schema — so call 1 succeeds at 1 spawn / 1 persistent proxy with no
reconnect, and later calls are warm (0 new spawns).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_c2 as common  # noqa: E402
from common_c2 import (  # noqa: E402
    HERE,
    LOGS_DIR,
    SELF_HEAL_PROXY,
    count_events,
    events,
    extract_heal_events,
    extract_served_snapshots,
    hlog,
    invoke_recorded,
    make_transport,
    print_manifest_schemas,
    proxy_pids,
    read_proxy_log,
    versions_line,
)
from toolregistry import ToolRegistry  # noqa: E402

PHASE = "phase-a2-selfheal-c2"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
HEAL_STATE = LOGS_DIR / f"{PHASE}-heal-state.json"
MANIFEST = HERE / "manifest.json"

# Calls: add first (drift exposure), add again (warm), multiply (other tool).
CALLS = [
    ("add", {"a": 2, "b": 3}, "add(2,3)"),
    ("add", {"a": 1, "b": 1}, "add(1,1)"),
    ("multiply", {"a": 4, "b": 5}, "multiply(4,5)"),
]


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(
        f"proxy=SELF_HEAL({SELF_HEAL_PROXY.name}) manifest={MANIFEST.name} "
        f"heal_threshold=1 heal_state={HEAL_STATE.name} "
        f"backend_schema_mode=diverging backend_response_mode=diverging"
    )
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()
    if HEAL_STATE.exists():
        HEAL_STATE.unlink()

    registry = ToolRegistry(name="a2selfheal")
    transport = make_transport(
        str(PROXY_LOG),
        proxy_path=SELF_HEAL_PROXY,
        manifest=str(MANIFEST),
        backend_schema_mode="diverging",
        backend_response_mode="diverging",
        heal_state=str(HEAL_STATE),
        heal_threshold="1",
    )

    hlog("A2_BEGIN register")
    t0 = common.now_ms()
    try:
        registry.register_from_mcp(transport)
        reg_ok = True
        reg_error = None
    except Exception as exc:
        reg_ok = False
        reg_error = exc
    t1 = common.now_ms()
    hlog(f"A2_REGISTER result={'ok' if reg_ok else 'FAILED'} delta_ms={t1 - t0} error={reg_error!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)

    print_manifest_schemas(MANIFEST)

    prev_spawns = 0
    prev_heals = 0
    outcomes = []
    for name, kwargs, label in CALLS:
        hlog(f"A2_BEGIN call {label}")
        outcome = invoke_recorded(registry, name, kwargs, label=label)
        outcomes.append(outcome)
        proxy_lines = read_proxy_log(PROXY_LOG)
        spawns = events(proxy_lines, "backend_spawn_start")
        heals = extract_heal_events(proxy_lines)
        pids = proxy_pids(proxy_lines)
        persistent = max(0, len(pids) - 1)
        spawn_increment = len(spawns) - prev_spawns
        heal_increment = len(heals) - prev_heals
        hlog(
            f"A2_CALL_METRICS label={label} spawn_increment={spawn_increment} "
            f"cumulative_spawns={len(spawns)} persistent_proxies={persistent} "
            f"proxy_processes={len(pids)} reconnect_fired={len(pids) > 2} "
            f"heal_increment={heal_increment} cumulative_heals={len(heals)}"
        )
        prev_spawns = len(spawns)
        prev_heals = len(heals)

    proxy_lines = read_proxy_log(PROXY_LOG)
    heals = extract_heal_events(proxy_lines)
    for epoch, msg in heals:
        hlog(f"A2_HEAL_EVENT epoch={epoch} msg={msg}")
    snapshots = extract_served_snapshots(proxy_lines)
    hlog(f"A2_SERVED_SNAPSHOTS count={len(snapshots)}")
    for snap in snapshots:
        hlog(f"A2_SERVED {snap}")

    spawns = events(proxy_lines, "backend_spawn_start")
    pids = proxy_pids(proxy_lines)

    # Verdict: first call success + spawns bounded at 1 for call 1 + other
    # tool untouched (multiply still succeeds, its schema stays None).
    first_success = outcomes[0] is not None and hasattr(outcomes[0], "result")
    other_success = outcomes[2] is not None and hasattr(outcomes[2], "result")
    heal_occurred = len(heals) >= 1
    pass_ok = first_success and other_success and heal_occurred and len(spawns) <= 3
    hlog(
        f"A2_RESULT pass={pass_ok} first_call_success={first_success} "
        f"other_tool_success={other_success} heal_occurred={heal_occurred} "
        f"total_spawns={len(spawns)} proxy_processes={len(pids)}"
    )
    registry.close()
    hlog(f"phase_done phase={PHASE} selfheal_c2_pass={pass_ok}")
    sys.exit(0 if pass_ok else 1)


if __name__ == "__main__":
    main()
