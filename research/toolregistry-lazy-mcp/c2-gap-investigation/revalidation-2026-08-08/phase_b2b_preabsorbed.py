#!/usr/bin/env python
"""Phase B2b — Option B boundary: schema PRE-ABSORBED before the drift call.

Same question A2b answered for Option A, now for Option B: does the
SchemaAwareConnectionManager interception still fire when the stale schema
was already absorbed by ToolRegistry's client BEFORE the drifted tool is
first called?

Pattern (copied from A2b): the harness calls ``multiply`` first (no output
schema, succeeds), which triggers a full ``tools/list`` re-absorb of the
STALE manifest into the persistent session — so when ``add`` is called, the
stale ``{"sum": ...}`` schema is already in ``_tool_output_schemas`` and
there is NO cache-miss re-list.  Under Option B the interception sits at the
``_call_persistent`` reconnect trigger (upstream of absorption state), so
the expected result is the same as fresh B2: the schema-validation
RuntimeError is classified TERMINAL — re-raised without reconnect — and the
caller receives the verbatim ``ErrorResult`` at 1 backend spawn / 1
persistent proxy / no reconnect.

This phase also carries the two Option-B test-depth additions that mirror
A2 (G6): a WARM repeat call on the intercepted session (add again — expected
to fail identically and fast, no new spawns) and an OTHER-TOOL-untouched
check (multiply after the failures — expected SUCCESS, schema untouched).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
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
from intercept_poc import (  # noqa: E402
    SchemaAwareConnectionManager,
    register_with_connection,
)
from toolregistry import ToolRegistry  # noqa: E402

PHASE = "phase-b2b-preabsorbed"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
MANIFEST = HERE / "manifest.json"


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(
        f"proxy=CONTROL({DRIFT_PROXY.name}) manifest={MANIFEST.name} "
        f"backend_schema_mode=diverging backend_response_mode=diverging "
        f"interception=SchemaAwareConnectionManager(register_with_connection) "
        f"call_order=multiply-first-then-add (pre-absorb stale schema)"
    )
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()

    registry = ToolRegistry(name="b2bpre")
    transport = make_transport(
        str(PROXY_LOG),
        proxy_path=DRIFT_PROXY,
        manifest=str(MANIFEST),
        backend_schema_mode="diverging",
        backend_response_mode="diverging",
    )
    connection = SchemaAwareConnectionManager(transport=transport, persistent=True)

    hlog("B2B_BEGIN register")
    t0 = common.now_ms()
    try:
        register_with_connection(registry, transport, connection)
        reg_ok = True
        reg_error = None
    except Exception as exc:
        reg_ok = False
        reg_error = exc
    t1 = common.now_ms()
    hlog(f"B2B_REGISTER result={'ok' if reg_ok else 'FAILED'} delta_ms={t1 - t0} error={reg_error!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)

    # multiply first — absorbs the FULL stale manifest (incl. add's stale
    # schema) into ToolRegistry's persistent session.
    hlog("B2B_BEGIN pre-absorb call multiply")
    outcome_multiply = invoke_recorded(registry, "multiply", {"a": 4, "b": 5}, label="multiply(4,5)")
    hlog("B2B_BEGIN drift call add (schema already absorbed)")
    outcome_add1 = invoke_recorded(registry, "add", {"a": 2, "b": 3}, label="add(2,3)")
    hlog("B2B_BEGIN warm repeat add (intercepted session)")
    outcome_add2 = invoke_recorded(registry, "add", {"a": 1, "b": 1}, label="add(1,1)")
    hlog("B2B_BEGIN other-tool multiply after failure")
    outcome_multiply2 = invoke_recorded(registry, "multiply", {"a": 6, "b": 7}, label="multiply(6,7)")

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns = events(proxy_lines, "backend_spawn_start")
    pids = proxy_pids(proxy_lines)
    persistent = max(0, len(pids) - 1)
    hlog(
        f"B2B_SPAWN_COUNTS backend_spawn_count={len(spawns)} proxy_processes={len(pids)} "
        f"persistent_proxies={persistent} reconnect_fired={len(pids) > 2} "
        f"schema_validation_failures={connection.schema_validation_failures} proxy_pids={pids}"
    )
    for epoch, msg in events(proxy_lines, "proxy_started"):
        hlog(f"B2B_PROXY_STARTED epoch={epoch} msg={msg}")

    # Interception fired pre-absorbed: the add calls were classified terminal
    # (each produces an ErrorResult with the verbatim schema text), no
    # reconnect, 1 spawn / 1 persistent proxy total.
    add1_error = (
        outcome_add1 is not None
        and hasattr(outcome_add1, "message")
        and common.SCHEMA_VALIDATION_MARKER in outcome_add1.message
    )
    add2_error = (
        outcome_add2 is not None
        and hasattr(outcome_add2, "message")
        and common.SCHEMA_VALIDATION_MARKER in outcome_add2.message
    )
    other_success = outcome_multiply2 is not None and hasattr(outcome_multiply2, "result")
    multiply_ok = outcome_multiply is not None and hasattr(outcome_multiply, "result")
    interception_effective = (
        len(spawns) == 1
        and not (len(pids) > 2)
        and connection.schema_validation_failures >= 2
    )
    error_preserved = add1_error and add2_error
    pass_ok = (
        multiply_ok
        and add1_error
        and add2_error
        and other_success
        and interception_effective
        and error_preserved
    )
    hlog(
        f"B2B_RESULT pass={pass_ok} preabsorb_interception_fired={interception_effective} "
        f"add1_error_preserved={add1_error} warm_add_error_preserved={add2_error} "
        f"other_tool_success={other_success} spawns={len(spawns)} proxies={len(pids)} "
        f"reconnect={len(pids) > 2} schema_validation_failures={connection.schema_validation_failures}"
    )
    try:
        connection.close_sync()
    except Exception:
        pass
    registry.close()
    hlog(f"phase_done phase={PHASE} interception_preabsorbed_pass={pass_ok}")
    sys.exit(0 if pass_ok else 1)


if __name__ == "__main__":
    main()
