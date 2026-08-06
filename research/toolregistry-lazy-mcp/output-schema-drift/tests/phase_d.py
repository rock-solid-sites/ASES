#!/usr/bin/env python
"""Phase: Test D — input-valid / output-invalid isolation.

Fresh proxy process, fresh registry.  Same diverging setup as Test C
(cached conforming manifest, backend response_mode=diverging).

Purpose: explicitly confirm the INPUT is valid against the cached input
schema BEFORE the call, so the failure is provably NOT an input-validation
failure.  This isolates the claim: identifier-first validate-before-spawn
lets this call through (input valid), the backend IS spawned, and the call
fails only after the backend responds with a non-conforming shape.

Recorded:
* ``input_valid`` — jsonschema validation of {"a":2,"b":3} against the
  cached manifest's input_schema for ``add``.
* spawn happened before the failure (backend_up epoch > call start).
* the failure message verbatim (should be the same MCPError as Test C).
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
    validate_input_against_manifest,
    versions_line,
)
from toolregistry import ToolRegistry  # noqa: E402

PHASE = "test-d"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
MANIFEST = HERE / "manifest.json"

ARGS = {"a": 2, "b": 3}


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(f"manifest={MANIFEST.name} backend_schema_mode=conforming backend_response_mode=diverging")
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()

    # ---- explicit input validation against the CACHED input schema ----
    input_valid, input_detail = validate_input_against_manifest(MANIFEST, "add", ARGS)
    hlog(f"TESTD_INPUT_VALIDATION input_valid={input_valid} detail={input_detail}")
    if not input_valid:
        hlog("TESTD_ABORT input invalid per cached schema; test would not isolate output drift")
        sys.exit(2)

    registry = ToolRegistry(name="testd")
    transport = make_transport(
        str(PROXY_LOG),
        manifest=str(MANIFEST),
        backend_schema_mode="conforming",
        backend_response_mode="diverging",
    )

    hlog("TESTD_BEGIN register")
    t0 = common.now_ms()
    reg_error = None
    try:
        registry.register_from_mcp(transport)
        reg_ok = True
    except Exception as exc:
        reg_ok = False
        reg_error = exc
    t1 = common.now_ms()
    hlog(f"TESTD_REGISTER result={'ok' if reg_ok else 'FAILED'} delta_ms={t1 - t0} error={reg_error!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)

    print_manifest_schemas(MANIFEST)

    hlog("TESTD_BEGIN call")
    call_start = common.now_ms()
    outcome = invoke_recorded(registry, "add", dict(ARGS), label="add(2,3)")

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns = events(proxy_lines, "backend_spawn_start")
    ups = events(proxy_lines, "backend_up")
    hlog(
        f"TESTD_SPAWN backend_spawn_count={len(spawns)} backend_up_count={len(ups)} "
        f"proxy_processes={len(proxy_pids(proxy_lines))}"
    )
    first_spawn = first_event(proxy_lines, "backend_spawn_start")
    if first_spawn:
        hlog(
            f"TESTD_SPAWNED_BEFORE_FAILURE first_spawn_epoch={first_spawn[0]} "
            f"call_start_epoch={call_start} -> backend spawned {first_spawn[0] - call_start} ms after call invocation"
        )
    if outcome is not None and hasattr(outcome, "message"):
        hlog(f"TESTD_ERROR_RESULT message_verbatim={outcome.message!r}")

    fail_ok = (
        input_valid
        and outcome is not None
        and not hasattr(outcome, "result")
        and hasattr(outcome, "message")
        and len(spawns) >= 1
    )
    hlog(f"TESTD_RESULT pass={fail_ok}")
    registry.close()
    hlog(f"phase_done phase={PHASE} test_d_pass={fail_ok}")
    sys.exit(0 if fail_ok else 1)


if __name__ == "__main__":
    main()
