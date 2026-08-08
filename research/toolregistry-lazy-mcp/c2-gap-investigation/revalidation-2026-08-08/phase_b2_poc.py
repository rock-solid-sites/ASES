#!/usr/bin/env python
"""Phase B2 — Option B PoC: interception via SchemaAwareConnectionManager.

Same C2 scenario (cached manifest ``{"sum": ...}``, backend schema_mode=
diverging + response_mode=diverging) against the UNMODIFIED #213 drift
proxy, but registration goes through :func:`intercept_poc.register_with_connection`
so the schema-validation RuntimeError is intercepted at ToolRegistry's
client layer and does NOT reach the reconnect-retry logic.

Measures: backend spawn count, persistent proxy count, reconnect fired,
caller-visible outcome type/message, and the PoC subclass's own
``schema_validation_failures`` counter.  Expected if the interception works:
1 backend spawn, 1 persistent proxy, reconnect NOT fired, and the caller
still receives the verbatim schema error (the call cannot succeed while the
served manifest is stale — interception removes the amplification, not the
mismatch).
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

PHASE = "phase-b2-poc"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
MANIFEST = HERE / "manifest.json"


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(
        f"proxy=CONTROL({DRIFT_PROXY.name}) manifest={MANIFEST.name} "
        f"backend_schema_mode=diverging backend_response_mode=diverging "
        f"interception=SchemaAwareConnectionManager(register_with_connection)"
    )
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()

    registry = ToolRegistry(name="b2poc")
    transport = make_transport(
        str(PROXY_LOG),
        proxy_path=DRIFT_PROXY,
        manifest=str(MANIFEST),
        backend_schema_mode="diverging",
        backend_response_mode="diverging",
    )
    connection = SchemaAwareConnectionManager(transport=transport, persistent=True)

    hlog("B2_BEGIN register")
    t0 = common.now_ms()
    try:
        register_with_connection(registry, transport, connection)
        reg_ok = True
        reg_error = None
    except Exception as exc:
        reg_ok = False
        reg_error = exc
    t1 = common.now_ms()
    hlog(f"B2_REGISTER result={'ok' if reg_ok else 'FAILED'} delta_ms={t1 - t0} error={reg_error!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)

    hlog("B2_BEGIN call")
    outcome = invoke_recorded(registry, "add", {"a": 2, "b": 3}, label="add(2,3)")

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns = events(proxy_lines, "backend_spawn_start")
    ups = events(proxy_lines, "backend_up")
    pids = proxy_pids(proxy_lines)
    persistent = max(0, len(pids) - 1)
    hlog(
        f"B2_SPAWN_COUNTS backend_spawn_count={len(spawns)} backend_up_count={len(ups)} "
        f"proxy_processes={len(pids)} persistent_proxies={persistent} "
        f"reconnect_fired={len(pids) > 2} proxy_pids={pids} "
        f"schema_validation_failures={connection.schema_validation_failures}"
    )
    for epoch, msg in events(proxy_lines, "proxy_started"):
        hlog(f"B2_PROXY_STARTED epoch={epoch} msg={msg}")

    error_preserved = (
        outcome is not None
        and hasattr(outcome, "message")
        and common.SCHEMA_VALIDATION_MARKER in outcome.message
    )
    interception_effective = (
        len(spawns) == 1
        and not (len(pids) > 2)
        and connection.schema_validation_failures >= 1
    )
    pass_ok = error_preserved and interception_effective
    hlog(
        f"B2_RESULT pass={pass_ok} spawns={len(spawns)} proxies={len(pids)} "
        f"reconnect={len(pids) > 2} error_preserved={error_preserved} "
        f"interception_effective={interception_effective}"
    )
    try:
        connection.close_sync()
    except Exception:
        pass
    registry.close()
    hlog(f"phase_done phase={PHASE} interception_poc_pass={pass_ok}")
    sys.exit(0 if pass_ok else 1)


if __name__ == "__main__":
    main()
