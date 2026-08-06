#!/usr/bin/env python
"""Phase: Test C3 (supplementary) — bare-number non-conforming shape.

Fresh proxy process, fresh registry.

Same cached manifest as Test C/C2 (``manifest.json`` — conforming
output_schema {"sum": number}).  The backend is configured
``schema_mode=none`` (declares NO output schema, so the proxy's own client
does not validate and passes the response through) and
``response_mode=bare`` (returns ``structured_content=<n>``, a bare JSON
number).  ToolRegistry's client then validates the bare number against the
CACHED schema {"sum": ...} and must fail with a different jsonschema
message ("is not of type 'object'") — the brief's "or a bare number"
alternative non-conforming shape.
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

PHASE = "test-c3"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
MANIFEST = HERE / "manifest.json"


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(f"manifest={MANIFEST.name} backend_schema_mode=none backend_response_mode=bare")
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()

    registry = ToolRegistry(name="testc3")
    transport = make_transport(
        str(PROXY_LOG),
        manifest=str(MANIFEST),
        backend_schema_mode="none",
        backend_response_mode="bare",
    )

    hlog("TESTC3_BEGIN register")
    t0 = common.now_ms()
    reg_error = None
    try:
        registry.register_from_mcp(transport)
        reg_ok = True
    except Exception as exc:
        reg_ok = False
        reg_error = exc
    t1 = common.now_ms()
    hlog(f"TESTC3_REGISTER result={'ok' if reg_ok else 'FAILED'} delta_ms={t1 - t0} error={reg_error!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)

    print_manifest_schemas(MANIFEST)

    hlog("TESTC3_BEGIN call")
    outcome = invoke_recorded(registry, "add", {"a": 2, "b": 3}, label="add(2,3)")

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns = events(proxy_lines, "backend_spawn_start")
    hlog(
        f"TESTC3_SPAWN backend_spawn_count={len(spawns)} "
        f"proxy_processes={len(proxy_pids(proxy_lines))}"
    )
    for epoch, msg in events(proxy_lines, "response tools/call"):
        hlog(f"TESTC3_RESPONSE epoch={epoch} msg={msg}")

    if outcome is not None and hasattr(outcome, "message"):
        hlog(f"TESTC3_ERROR_RESULT message_verbatim={outcome.message!r}")

    fail_ok = outcome is not None and not hasattr(outcome, "result") and hasattr(outcome, "message")
    hlog(f"TESTC3_RESULT pass={fail_ok}")
    registry.close()
    hlog(f"phase_done phase={PHASE} test_c3_pass={fail_ok}")
    sys.exit(0 if fail_ok else 1)


if __name__ == "__main__":
    main()
