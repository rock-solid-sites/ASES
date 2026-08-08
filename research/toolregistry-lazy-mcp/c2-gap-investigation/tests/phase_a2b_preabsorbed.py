#!/usr/bin/env python
"""Phase A2b — Option A boundary: schema PRE-ABSORBED before the drift call.

Same C2 setup as A2 but with a session where the stale schema was already
absorbed by ToolRegistry's client BEFORE the drifted tool is first called:
the harness calls ``multiply`` first (no output_schema, succeeds), which
triggers a full ``tools/list`` re-absorb of the STALE manifest — so when
``add`` is then called, ``add`` IS in the client's ``_tool_output_schemas``
(stale ``{"sum": ...}``) and there is NO cache-miss re-list to pick up the
proxy's mid-call heal.  Expected: the first ``add`` call still surfaces the
RuntimeError (reconnect-retry fires), but the healed manifest is persisted
so the retried call succeeds.  This characterises the "one wasted call
cycle per drift event" boundary that N=1 avoids in the fresh-session case.
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
    events,
    extract_heal_events,
    hlog,
    invoke_recorded,
    make_transport,
    print_manifest_schemas,
    proxy_pids,
    read_proxy_log,
    versions_line,
)
from toolregistry import ToolRegistry  # noqa: E402

PHASE = "phase-a2b-preabsorbed"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
HEAL_STATE = LOGS_DIR / f"{PHASE}-heal-state.json"
MANIFEST = HERE / "manifest.json"


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(
        f"proxy=SELF_HEAL({SELF_HEAL_PROXY.name}) manifest={MANIFEST.name} "
        f"heal_threshold=1 heal_state={HEAL_STATE.name} "
        f"backend_schema_mode=diverging backend_response_mode=diverging "
        f"call_order=multiply-first-then-add (pre-absorb stale schema)"
    )
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()
    if HEAL_STATE.exists():
        HEAL_STATE.unlink()

    registry = ToolRegistry(name="a2bpre")
    transport = make_transport(
        str(PROXY_LOG),
        proxy_path=SELF_HEAL_PROXY,
        manifest=str(MANIFEST),
        backend_schema_mode="diverging",
        backend_response_mode="diverging",
        heal_state=str(HEAL_STATE),
        heal_threshold="1",
    )

    hlog("A2B_BEGIN register")
    try:
        registry.register_from_mcp(transport)
        reg_ok = True
    except Exception as exc:
        reg_ok = False
        hlog(f"A2B_REGISTER_FAILED error={exc!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)
    print_manifest_schemas(MANIFEST)

    # multiply first — absorbs the FULL stale manifest (incl. add's stale
    # schema) into ToolRegistry's persistent session.
    hlog("A2B_BEGIN pre-absorb call multiply")
    outcome_multiply = invoke_recorded(registry, "multiply", {"a": 4, "b": 5}, label="multiply(4,5)")
    hlog("A2B_BEGIN drift call add (schema already absorbed)")
    outcome_add1 = invoke_recorded(registry, "add", {"a": 2, "b": 3}, label="add(2,3)")
    hlog("A2B_BEGIN repeat add (post-heal)")
    outcome_add2 = invoke_recorded(registry, "add", {"a": 1, "b": 1}, label="add(1,1)")

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns = events(proxy_lines, "backend_spawn_start")
    heals = extract_heal_events(proxy_lines)
    pids = proxy_pids(proxy_lines)
    persistent = max(0, len(pids) - 1)
    hlog(
        f"A2B_SPAWN_COUNTS backend_spawn_count={len(spawns)} proxy_processes={len(pids)} "
        f"persistent_proxies={persistent} reconnect_fired={len(pids) > 2} "
        f"heal_events={len(heals)} proxy_pids={pids}"
    )
    for epoch, msg in heals:
        hlog(f"A2B_HEAL epoch={epoch} msg={msg}")

    multiply_ok = outcome_multiply is not None and hasattr(outcome_multiply, "result")
    add1_ok = outcome_add1 is not None and hasattr(outcome_add1, "result")
    add2_ok = outcome_add2 is not None and hasattr(outcome_add2, "result")
    pass_ok = (
        multiply_ok
        and add1_ok  # the pre-absorbed first add call recovers via the
        # reconnect-retry against the persisted healed manifest
        and add2_ok
        and len(heals) >= 1
    )
    hlog(
        f"A2B_RESULT pass={pass_ok} multiply_ok={multiply_ok} add1_ok={add1_ok} "
        f"add2_ok={add2_ok} heal_events={len(heals)} total_spawns={len(spawns)}"
    )
    registry.close()
    hlog(f"phase_done phase={PHASE} preabsorbed_pass={pass_ok}")
    sys.exit(0 if pass_ok else 1)


if __name__ == "__main__":
    main()
