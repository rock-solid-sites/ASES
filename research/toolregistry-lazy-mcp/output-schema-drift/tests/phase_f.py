#!/usr/bin/env python
"""Phase: Test F — blast radius after a drift failure.

Fresh proxy process, fresh registry (same diverging setup as Test C).

Sequence in ONE session:
1. Call ``add`` -> fails with the output-schema-drift error (as C/D).
2. Call a DIFFERENT, unrelated tool, ``multiply(4, 5)``, whose manifest
   matches its backend (no output_schema declared anywhere, so it cannot
   itself fail validation).  Records whether it succeeds normally.
3. Re-check ``registry.list_tools()`` and call ``add`` again to see
   whether the drift failure poisoned registry state beyond the one failed
   call (connection left bad, whole server marked failed, subsequent
   same-server calls blocked).
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
    hlog,
    invoke_recorded,
    make_transport,
    print_manifest_schemas,
    proxy_pids,
    read_proxy_log,
    versions_line,
)
from toolregistry import ToolRegistry  # noqa: E402

PHASE = "test-f"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
MANIFEST = HERE / "manifest.json"


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(f"manifest={MANIFEST.name} backend_schema_mode=conforming backend_response_mode=diverging")
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()

    registry = ToolRegistry(name="testf")
    transport = make_transport(
        str(PROXY_LOG),
        manifest=str(MANIFEST),
        backend_schema_mode="conforming",
        backend_response_mode="diverging",
    )

    hlog("TESTF_BEGIN register")
    t0 = common.now_ms()
    reg_error = None
    try:
        registry.register_from_mcp(transport)
        reg_ok = True
    except Exception as exc:
        reg_ok = False
        reg_error = exc
    t1 = common.now_ms()
    hlog(f"TESTF_REGISTER result={'ok' if reg_ok else 'FAILED'} delta_ms={t1 - t0} error={reg_error!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)

    print_manifest_schemas(MANIFEST)
    registered = registry.list_tools()
    hlog(f"TESTF_REGISTERED list_tools={registered}")

    # ---- 1. the failing call (reproduces C/D) ----
    hlog("TESTF_ADD_CALL_BEGIN (expected drift failure)")
    outcome_add = invoke_recorded(registry, "add", {"a": 2, "b": 3}, label="add(2,3)")
    add_failed = outcome_add is not None and not hasattr(outcome_add, "result")
    if outcome_add is not None and hasattr(outcome_add, "message"):
        hlog(f"TESTF_ADD_ERROR message_verbatim={outcome_add.message!r}")

    # ---- 2. unrelated tool, matching manifest ----
    hlog("TESTF_MULTIPLY_CALL_BEGIN (unrelated tool, matching manifest)")
    outcome_mult = invoke_recorded(registry, "multiply", {"a": 4, "b": 5}, label="multiply(4,5)")
    mult_ok = outcome_mult is not None and hasattr(outcome_mult, "result") and outcome_mult.result == "20.0"

    # ---- 3. registry still usable? add again ----
    hlog("TESTF_ADD_AGAIN_CALL_BEGIN (same failing tool, after unrelated success)")
    outcome_add2 = invoke_recorded(registry, "add", {"a": 1, "b": 1}, label="add(1,1)")
    add2_failed = outcome_add2 is not None and not hasattr(outcome_add2, "result")

    discovered = registry.list_tools()
    hlog(f"TESTF_AFTER list_tools={discovered}")

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns = len(events(proxy_lines, "backend_spawn_start"))
    ups = len(events(proxy_lines, "backend_up"))
    responses = [l for l in proxy_lines if l[1].startswith("response tools/call")]
    forwards = events(proxy_lines, "forward tools/call")
    hlog(
        f"TESTF_PROXY backend_spawn_count={spawns} backend_up_count={ups} "
        f"forward_count={len(forwards)} success_response_count={len(responses)} "
        f"proxy_processes={len(proxy_pids(proxy_lines))}"
    )
    for epoch, msg in forwards:
        hlog(f"TESTF_FORWARD epoch={epoch} msg={msg}")

    pass_f = add_failed and mult_ok and add2_failed and "multiply" in discovered
    hlog(f"TESTF_RESULT pass={pass_f} (add failed; multiply succeeded; add fails again)")
    registry.close()
    hlog(f"phase_done phase={PHASE} test_f_pass={pass_f}")
    sys.exit(0 if pass_f else 1)


if __name__ == "__main__":
    main()
