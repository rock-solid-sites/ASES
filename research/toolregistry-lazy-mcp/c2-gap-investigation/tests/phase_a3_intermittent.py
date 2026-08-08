#!/usr/bin/env python
"""Phase A3 — Option A: INTERMITTENT-drift flapping check.

Three sub-scenarios, each a fresh registry + proxy session, all against
``proxy_self_heal.py`` with heal threshold 1 and the intermittent backend
(``backend_intermittent.py``, ``response_mode=alternating``):

  A3a — schema_mode=none:    the backend DECLARES no output schema (so the
        proxy's own client passes every response) and responses alternate
        conforming/diverging.  The served-manifest self-check is the ONLY
        gate that sees the alternation.  Question: does the heal correct the
        served schema once and converge, or flap back and forth?
  A3b — schema_mode=conforming + classification ON (composite): the #217
        intermittent scenario.  Diverging responses fail at the proxy's OWN
        client (Test C signature) and are classified as terminal isError —
        the served schema must stay untouched (no heal, no flap), and the
        cost must equal #217's 1 spawn / no reconnect.
  A3c — schema_mode=conforming + classification OFF (plain self-heal):
        same intermittent scenario WITHOUT the #217 classification delta.
        Documents whether self-healing alone regresses intermittent drift
        relative to retry-classification ("must not be made worse").
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_c2 as common  # noqa: E402
from common_c2 import (  # noqa: E402
    HERE,
    INTERMITTENT_BACKEND,
    LOGS_DIR,
    SELF_HEAL_PROXY,
    events,
    extract_heal_events,
    hlog,
    invoke_recorded,
    make_transport,
    proxy_pids,
    read_proxy_log,
    versions_line,
)
from toolregistry import ToolRegistry  # noqa: E402

MANIFEST = HERE / "manifest.json"
CALLS = [
    ("add", {"a": 2, "b": 3}, "add(2,3)"),
    ("add", {"a": 4, "b": 5}, "add(4,5)"),
    ("add", {"a": 6, "b": 7}, "add(6,7)"),
    ("add", {"a": 8, "b": 9}, "add(8,9)"),
]


def run_sub_scenario(
    tag: str,
    *,
    schema_mode: str,
    classify: bool,
) -> bool:
    phase = f"phase-a3-{tag}"
    proxy_log = LOGS_DIR / f"{phase}-proxy.log"
    heal_state = LOGS_DIR / f"{phase}-heal-state.json"
    if proxy_log.exists():
        proxy_log.unlink()
    if heal_state.exists():
        heal_state.unlink()

    hlog(f"=== A3_SUBSCENARIO {tag} schema_mode={schema_mode} classify={classify} ===")
    registry = ToolRegistry(name=f"a3{tag}")
    transport = make_transport(
        str(proxy_log),
        proxy_path=SELF_HEAL_PROXY,
        manifest=str(MANIFEST),
        backend_schema_mode=schema_mode,
        backend_response_mode="alternating",
        backend_script=INTERMITTENT_BACKEND,
        heal_state=str(heal_state),
        heal_threshold="1",
        classify_schema=classify,
    )
    try:
        registry.register_from_mcp(transport)
    except Exception as exc:
        hlog(f"A3_REGISTER_FAILED tag={tag} error={exc!r}")
        return False
    time.sleep(0.3)

    outcomes = []
    for name, kwargs, label in CALLS:
        outcome = invoke_recorded(registry, name, kwargs, label=f"{tag}:{label}")
        outcomes.append(outcome)

    lines = read_proxy_log(proxy_log)
    spawns = events(lines, "backend_spawn_start")
    schema_failures = events(lines, "backend_schema_validation_failed")
    classified = events(lines, "call_tool_classified_schema_failure")
    heals = extract_heal_events(lines)
    pids = proxy_pids(lines)
    persistent = max(0, len(pids) - 1)
    hlog(
        f"A3_METRICS tag={tag} spawns={len(spawns)} persistent_proxies={persistent} "
        f"reconnect_fired={len(pids) > 2} heal_events={len(heals)} "
        f"schema_failure_classified={len(classified)} "
        f"backend_schema_validation_failed={len(schema_failures)}"
    )
    for epoch, msg in heals:
        hlog(f"A3_HEAL tag={tag} epoch={epoch} msg={msg}")

    heal_event_count = len(heals)
    if tag == "a3a":
        # Converge: at most one heal event (first mismatch -> live no-schema),
        # and no heal-back (a second heal would mean flapping).
        pass_ok = heal_event_count <= 1
    elif tag in ("a3b", "a3c"):
        # No served-schema change expected at all (the alternation is caught
        # at the proxy's own client, not the served check).
        pass_ok = heal_event_count == 0
    else:  # pragma: no cover
        pass_ok = False
    hlog(f"A3_RESULT tag={tag} pass={pass_ok} heal_events={heal_event_count}")
    registry.close()
    return pass_ok


def main() -> None:
    hlog(f"phase_start phase=phase-a3-intermittent {versions_line()}")
    results = {}
    results["a3a"] = run_sub_scenario("a3a", schema_mode="none", classify=False)
    results["a3b"] = run_sub_scenario("a3b", schema_mode="conforming", classify=True)
    results["a3c"] = run_sub_scenario("a3c", schema_mode="conforming", classify=False)
    all_ok = all(results.values())
    hlog(f"A3_OVERALL pass={all_ok} results={results}")
    hlog(f"phase_done phase=phase-a3-intermittent all_subscenarios_pass={all_ok}")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
