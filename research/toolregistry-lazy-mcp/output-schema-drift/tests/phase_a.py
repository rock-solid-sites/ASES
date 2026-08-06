#!/usr/bin/env python
"""Phase: Test A — baseline reconfirmation (cached output_schema: null).

Fresh proxy process, fresh registry.

The cached manifest is ``manifest-null.json`` — captured with
``BACKEND_SCHEMA_MODE=none`` so the ``add`` tool's ``output_schema`` is
null, exactly reproducing the #196 manifest.json:30 situation.

To make the contrast with Tests C/D maximally sharp, the backend is run in
``response_mode=diverging``: it returns structured content
``{"result": <n>}`` — the SAME shape that fails in Tests C/D.  With a null
declared output schema neither validating client (proxy's client against
the live backend listing, ToolRegistry's client against the cached
manifest) validates, so the call must succeed regardless of returned
shape.  (#196 already established text-only success under a null schema;
this run establishes the "structured but non-conforming" success case.)
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
    first_event,
    hlog,
    invoke_recorded,
    make_transport,
    print_manifest_schemas,
    read_proxy_log,
    versions_line,
)
from toolregistry import ToolRegistry  # noqa: E402

PHASE = "test-a"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
MANIFEST = HERE / "manifest-null.json"


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(f"manifest={MANIFEST.name} backend_schema_mode=none backend_response_mode=diverging")
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()

    registry = ToolRegistry(name="testa")
    transport = make_transport(
        str(PROXY_LOG),
        manifest=str(MANIFEST),
        backend_schema_mode="none",
        backend_response_mode="diverging",
    )

    hlog("TESTA_BEGIN register")
    t0 = common.now_ms()
    reg_error = None
    try:
        registry.register_from_mcp(transport)
        reg_ok = True
    except Exception as exc:
        reg_ok = False
        reg_error = exc
    t1 = common.now_ms()
    hlog(f"TESTA_REGISTER result={'ok' if reg_ok else 'FAILED'} delta_ms={t1 - t0} error={reg_error!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)

    print_manifest_schemas(MANIFEST)

    # Call the tool: backend returns structured {"result": n} which does NOT
    # conform to any schema — but the cached manifest declares no schema, so
    # the call must succeed.
    hlog("TESTA_BEGIN call")
    outcome = invoke_recorded(registry, "add", {"a": 2, "b": 3}, label="add(2,3)")

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns = count_events(proxy_lines, "backend_spawn_start")
    ups = count_events(proxy_lines, "backend_up")
    responses = [l for l in proxy_lines if l[1].startswith("response tools/call")]
    hlog(
        f"TESTA_PROXY backend_spawn_count={spawns} backend_up_count={ups} "
        f"response_count={len(responses)} proxy_processes={len(common.proxy_pids(proxy_lines))}"
    )

    ok = outcome is not None and hasattr(outcome, "result") and outcome.result == "5.0"
    hlog(f"TESTA_RESULT pass={ok}")
    registry.close()
    hlog(f"phase_done phase={PHASE} test_a_pass={ok}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
