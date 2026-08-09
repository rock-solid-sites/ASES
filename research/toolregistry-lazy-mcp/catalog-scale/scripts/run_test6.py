#!/usr/bin/env python
"""TEST 6 — Immediate Teardown as a Boundary Condition.

Immediate teardown answers: 'if the runtime explicitly disconnects the
catalog-acquisition proxy right away, does physical residency disappear?'

Boundary demonstration in one session (N=10, K=1), proxy/backend SEPARATE:
  1. Catalog-refresh workload (register 10 + refresh 10, nothing invoked):
     resident-after under NO teardown (natural/default), then under
     IMMEDIATE teardown (close all managers) — both measured.
  2. Called-connector workload: invoke 1 tool (K=1) -> resident = 1 proxy +
     1 backend (persistence expected); then immediate teardown -> measure
     again (expect 0/0 — residency fully reclaimable by teardown).

Interpretation rule (from the brief): if immediate teardown suffices for the
catalog-refresh workload, the eventual idle-timeout feature is a POLICY
optimization, not a prerequisite for the core scaling claim. If even
immediate teardown leaves substantial residency, that is a more fundamental
lifecycle problem.

This is the crude immediate-disconnect-after-list boundary case — NOT the
full configurable idle-timeout feature (out of scope).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    GRACE_SECONDS,
    build_transport,
    clean_orphans,
    pct_line,
    persistence,
    snapshot,
    versions,
    write_json,
    PeakMonitor,
)

from toolregistry import ToolRegistry  # noqa: E402
from toolregistry._async_runtime import AsyncRuntime  # noqa: E402

RUN_LABEL = "test6"
N = 10


def _conn_for(reg: ToolRegistry, cid: str):
    idx = int(cid.lstrip("c"))
    return reg._mcp_integrations[idx]._connections[0]


def main() -> None:
    base = HERE / "logs" / RUN_LABEL
    base.mkdir(parents=True, exist_ok=True)
    log_dir = base / "run"
    log_dir.mkdir(parents=True, exist_ok=True)
    for stale in list(log_dir.glob("*.log")) + list(log_dir.glob("*.pid")):
        stale.unlink()

    pct_line(f"TEST6 begin versions={versions()}")
    orphan_count = clean_orphans()
    pct_line(f"TEST6 pre_cleaned_orphans={orphan_count}")
    reg = ToolRegistry()
    conn_ids = [f"c{i}" for i in range(N)]
    transports = {cid: build_transport(cid, log_dir) for cid in conn_ids}

    # --- phase 1: catalog-refresh workload, no teardown ---
    for cid in conn_ids:
        reg.register_from_mcp(transports[cid], namespace=cid)
    for cid in conn_ids:
        AsyncRuntime.run_sync(_conn_for(reg, cid).list_tools())
    time.sleep(GRACE_SECONDS)
    resident_catalog_no_teardown = snapshot()
    pct_line(
        f"TEST6 catalog_refresh no_teardown proxies={resident_catalog_no_teardown['proxy_count']} "
        f"backends={resident_catalog_no_teardown['backend_count']}"
    )

    # --- phase 2: immediate teardown of all managers (catalog-refresh side) ---
    for cid in conn_ids:
        _conn_for(reg, cid).close_sync()
    time.sleep(GRACE_SECONDS)
    resident_catalog_after_teardown = snapshot()
    pct_line(
        f"TEST6 catalog_refresh after_teardown proxies={resident_catalog_after_teardown['proxy_count']} "
        f"backends={resident_catalog_after_teardown['backend_count']}"
    )

    # --- phase 3: invoke 1 tool -> persistence expected ---
    monitor = PeakMonitor()
    monitor.start()
    r1 = reg.invoke("c0-add", {"a": 1, "b": 2})
    monitor.stop()
    pct_line(f"TEST6 call result={getattr(r1, 'result', r1)}")
    time.sleep(GRACE_SECONDS)
    resident_called = snapshot()
    pct_line(
        f"TEST6 after_call proxies={resident_called['proxy_count']} "
        f"backends={resident_called['backend_count']}"
    )

    # --- phase 4: immediate teardown of the called connector ---
    for cid in conn_ids:
        _conn_for(reg, cid).close_sync()
    time.sleep(GRACE_SECONDS)
    resident_called_after_teardown = snapshot()
    pct_line(
        f"TEST6 after_call_teardown proxies={resident_called_after_teardown['proxy_count']} "
        f"backends={resident_called_after_teardown['backend_count']}"
    )

    result = {
        "test": "6",
        "n": N,
        "k": 1,
        "calling_mode": "sync",
        "teardown_meaning": "immediate disconnect-after-list (crude boundary; NOT the idle-timeout feature)",
        "resident_catalog_no_teardown": resident_catalog_no_teardown,
        "resident_catalog_after_teardown": resident_catalog_after_teardown,
        "resident_after_call": resident_called,
        "resident_after_call_teardown": resident_called_after_teardown,
        "call_result": getattr(r1, "result", r1),
        "versions": versions(),
        "persistence": persistence(),
        "grace_seconds": GRACE_SECONDS,
    }
    write_json(base / "test6.json", result)
    pct_line(
        f"TEST6 done catalog_default={resident_catalog_no_teardown['proxy_count']} "
        f"catalog_teardown={resident_catalog_after_teardown['proxy_count']} "
        f"called_default={resident_called['proxy_count']}/{resident_called['backend_count']} "
        f"called_teardown={resident_called_after_teardown['proxy_count']}/{resident_called_after_teardown['backend_count']}"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
