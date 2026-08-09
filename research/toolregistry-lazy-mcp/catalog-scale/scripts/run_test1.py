#!/usr/bin/env python
"""TEST 1 — Catalog Acquisition Without Backend Activation (scope guard).

For each N in [1,5,10,20,50]: register N connectors, perform catalog
acquisition (session-init refresh via each connection manager's temp
list_tools), capture proxy-start and backend-start events, wait settlement,
record residency.

PASS criterion: backend_spawn_count == 0 (proxy count is NOT the criterion).
If ANY real backend starts during acquisition, STOP and investigate — that
invalidates the lazy-backend premise.

Calling mode: SYNC (register_from_mcp + AsyncRuntime.run_sync refresh),
sequential. Stdio only.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    GRACE_SECONDS,
    build_transport,
    connector_timings,
    count_events,
    pct_line,
    persistence,
    scan_procs,
    snapshot,
    versions,
    write_json,
    PeakMonitor,
)

from toolregistry import ToolRegistry  # noqa: E402
from toolregistry._async_runtime import AsyncRuntime  # noqa: E402

NS = [1, 5, 10, 20, 50]
RUN_LABEL = "test1"


def run_n(n: int, base_log_dir: Path) -> dict:
    pct_line(f"TEST1 n={n} begin")
    # Fresh per-N log dir: proxy log files are append-mode, so reusing a dir
    # across N sweeps would accumulate counts from earlier runs.
    log_dir = base_log_dir / f"n{n}"
    log_dir.mkdir(parents=True, exist_ok=True)
    for stale in log_dir.glob("*.log"):
        stale.unlink()
    for stale in log_dir.glob("*.pid"):
        stale.unlink()
    reg = ToolRegistry()
    conn_ids = [f"c{i}" for i in range(n)]
    transports = {cid: build_transport(cid, log_dir) for cid in conn_ids}

    monitor = PeakMonitor()
    monitor.start()

    # 1. Registration (discovery) — sync sequential
    t0 = time.time()
    for cid in conn_ids:
        reg.register_from_mcp(transports[cid], namespace=cid)
    register_ms = (time.time() - t0) * 1000

    # 2. Catalog acquisition / session-init refresh — temp list_tools per connector
    refresh_results: dict[str, str] = {}
    t1 = time.time()
    for cid in conn_ids:
        conn = _conn_for(reg, cid)
        try:
            tools = AsyncRuntime.run_sync(conn.list_tools())
            refresh_results[cid] = ",".join(sorted(t.name for t in tools)) or "EMPTY"
        except Exception as exc:  # addendum E: record failure separately
            refresh_results[cid] = f"ERROR:{type(exc).__name__}:{exc}"
    refresh_ms = (time.time() - t1) * 1000

    peak = monitor.stop()
    time.sleep(GRACE_SECONDS)
    resident = snapshot()

    # 3. Event counts from proxy logs
    log_files = [log_dir / f"{cid}-proxy.log" for cid in conn_ids]
    events = count_events(
        log_files,
        ["proxy_started", "backend_spawn_start", "backend_up", "backend_spawn_failed"],
    )
    timings = connector_timings(log_dir, conn_ids)

    result = {
        "n": n,
        "calling_mode": "sync",
        "acquisition_order": "sequential",
        "register_ms": round(register_ms, 1),
        "refresh_ms": round(refresh_ms, 1),
        "total_acquisition_ms": round(register_ms + refresh_ms, 1),
        "events": events,
        "backend_spawn_count": events["backend_spawn_start"],
        "pass": events["backend_spawn_start"] == 0,
        "peak": peak,
        "resident_after": resident,
        "refresh_results": refresh_results,
        "timings_sample": {cid: timings[cid] for cid in conn_ids if cid in timings},
        "grace_seconds": GRACE_SECONDS,
        "versions": versions(),
        "persistence": persistence(),
    }
    pct_line(f"TEST1 n={n} pass={result['pass']} backend_spawns={events['backend_spawn_start']} "
             f"proxy_starts={events['proxy_started']} resident_proxies={resident['proxy_count']} "
             f"resident_backends={resident['backend_count']}")
    write_json(log_dir / f"{RUN_LABEL}-n{n}.json", result)
    return result


def _conn_for(reg: ToolRegistry, cid: str):
    """Fetch the connection manager for connector cid.

    register_from_mcp appends ONE MCPIntegration per call (registration.py:143);
    each integration holds ONE MCPConnectionManager (integration.py:323).
    With n registrations the manager for c{i} is at index i.
    """
    idx = int(cid.lstrip("c"))
    return reg._mcp_integrations[idx]._connections[0]


def main() -> None:
    pct_line(f"TEST1 begin versions={versions()} python={sys.executable}")
    log_dir = HERE / "logs" / RUN_LABEL
    log_dir.mkdir(parents=True, exist_ok=True)
    results = [run_n(n, log_dir) for n in NS]
    all_pass = all(r["pass"] for r in results)
    pct_line(f"TEST1 done all_pass={all_pass}")
    if not all_pass:
        pct_line("TEST1 FAIL: a backend started during acquisition — lazy premise invalidated")
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
