#!/usr/bin/env python
"""Phase: Test B — matching schema (cached output_schema conforms to live).

Fresh proxy process, fresh registry.

The cached manifest is ``manifest.json`` — captured with
``BACKEND_SCHEMA_MODE=conforming`` so ``add`` declares
``output_schema={"type":"object","properties":{"sum":...},"required":["sum"]}``.

The backend runs in ``response_mode=conforming``: it returns structured
content ``{"sum": <n>}`` which conforms to the declared schema at BOTH
validating points (proxy's client against the live backend listing,
ToolRegistry's client against the cached manifest).  The call must succeed
cleanly.  Success latency is recorded for the Test C comparison.
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
    hlog,
    invoke_recorded,
    make_transport,
    print_manifest_schemas,
    read_proxy_log,
    versions_line,
)
from toolregistry import ToolRegistry  # noqa: E402

PHASE = "test-b"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
MANIFEST = HERE / "manifest.json"


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(f"manifest={MANIFEST.name} backend_schema_mode=conforming backend_response_mode=conforming")
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()

    registry = ToolRegistry(name="testb")
    transport = make_transport(
        str(PROXY_LOG),
        manifest=str(MANIFEST),
        backend_schema_mode="conforming",
        backend_response_mode="conforming",
    )

    hlog("TESTB_BEGIN register")
    t0 = common.now_ms()
    reg_error = None
    try:
        registry.register_from_mcp(transport)
        reg_ok = True
    except Exception as exc:
        reg_ok = False
        reg_error = exc
    t1 = common.now_ms()
    hlog(f"TESTB_REGISTER result={'ok' if reg_ok else 'FAILED'} delta_ms={t1 - t0} error={reg_error!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)

    print_manifest_schemas(MANIFEST)

    hlog("TESTB_BEGIN call")
    outcome = invoke_recorded(registry, "add", {"a": 2, "b": 3}, label="add(2,3)")

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns = count_events(proxy_lines, "backend_spawn_start")
    ups = count_events(proxy_lines, "backend_up")
    forwards = count_events(proxy_lines, "forward tools/call")
    responses = [l for l in proxy_lines if l[1].startswith("response tools/call")]
    hlog(
        f"TESTB_PROXY backend_spawn_count={spawns} backend_up_count={ups} "
        f"forward_count={forwards} response_count={len(responses)} "
        f"proxy_processes={len(common.proxy_pids(proxy_lines))}"
    )

    ok = outcome is not None and hasattr(outcome, "result") and outcome.result == "5.0"
    hlog(f"TESTB_RESULT pass={ok}")
    registry.close()
    hlog(f"phase_done phase={PHASE} test_b_pass={ok}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
