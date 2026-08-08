#!/usr/bin/env python
"""Generic catalog-acquisition + residency measurement.

Used by Tests 2, 3, and 6. One call to run_acquisition performs:
  register N connectors (discovery via temp MCPClient, the same path
  ToolRegistry uses for registration — source: integration.py:331),
  session-init refresh via each connection manager's temp list_tools
  (connection.py:73),
  optional explicit teardown (close every connection manager right after
  the refresh returns — immediate disconnect-after-list),
  peak sampling during the acquisition, grace-period settlement, then a
  resident-after snapshot with proxy/backend counts kept SEPARATE.

Calling modes (addendum B):
  sequential -> SYNC (register_from_mcp + AsyncRuntime.run_sync refresh);
                the shared 'async-runtime' daemon thread appears once.
  concurrent -> ASYNC (register_from_mcp_async + asyncio.gather); the
                harness's own loop runs everything; no 'async-runtime'
                thread is created by ToolRegistry.
The sync API cannot be made truly concurrent: every sync entry point
funnels through the single shared AsyncRuntime loop, which serializes the
coroutines (source: _async_runtime.py:72). Recording this mapping per run
is part of the experimental controls.
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    GRACE_SECONDS,
    build_transport,
    connector_timings,
    count_events,
    pct_line,
    snapshot,
    versions,
    PeakMonitor,
)

from toolregistry import ToolRegistry  # noqa: E402
from toolregistry._async_runtime import AsyncRuntime  # noqa: E402


def _conn_for(reg: ToolRegistry, cid: str):
    """The MCPConnectionManager registered for connector cid (index == cid)."""
    idx = int(cid.lstrip("c"))
    return reg._mcp_integrations[idx]._connections[0]


def _acquire_sync(reg: ToolRegistry, conn_ids: list[str], transports: dict) -> dict:
    refresh_results: dict[str, str] = {}
    t_reg = time.time()
    for cid in conn_ids:
        reg.register_from_mcp(transports[cid], namespace=cid)
    register_ms = (time.time() - t_reg) * 1000

    t_ref = time.time()
    for cid in conn_ids:
        conn = _conn_for(reg, cid)
        try:
            tools = AsyncRuntime.run_sync(conn.list_tools())
            refresh_results[cid] = ",".join(sorted(t.name for t in tools)) or "EMPTY"
        except Exception as exc:  # addendum E: record failures separately
            refresh_results[cid] = f"ERROR:{type(exc).__name__}:{exc}"
    refresh_ms = (time.time() - t_ref) * 1000
    return {"register_ms": register_ms, "refresh_ms": refresh_ms, "refresh_results": refresh_results}


async def _acquire_async(reg: ToolRegistry, conn_ids: list[str], transports: dict) -> dict:
    refresh_results: dict[str, str] = {}
    t_reg = time.time()
    for cid in conn_ids:
        await reg.register_from_mcp_async(transports[cid], namespace=cid)
    register_ms = (time.time() - t_reg) * 1000

    conns = {cid: _conn_for(reg, cid) for cid in conn_ids}

    async def _refresh(cid: str):
        try:
            tools = await conns[cid].list_tools()
            return cid, ",".join(sorted(t.name for t in tools)) or "EMPTY"
        except Exception as exc:
            return cid, f"ERROR:{type(exc).__name__}:{exc}"

    t_ref = time.time()
    for cid, label in await asyncio.gather(*(_refresh(c) for c in conn_ids)):
        refresh_results[cid] = label
    refresh_ms = (time.time() - t_ref) * 1000
    return {"register_ms": register_ms, "refresh_ms": refresh_ms, "refresh_results": refresh_results}


def _teardown_sync(reg: ToolRegistry, conn_ids: list[str]) -> None:
    for cid in conn_ids:
        try:
            _conn_for(reg, cid).close_sync()
        except Exception as exc:
            pct_line(f"TEARDOWN sync error cid={cid} exc={type(exc).__name__}:{exc}")


async def _teardown_async(reg: ToolRegistry, conn_ids: list[str]) -> None:
    for cid in conn_ids:
        try:
            await _conn_for(reg, cid).close()
        except Exception as exc:
            pct_line(f"TEARDOWN async error cid={cid} exc={type(exc).__name__}:{exc}")


def run_acquisition(
    n: int,
    order: str,
    teardown: bool,
    log_dir: Path,
    label: str,
) -> dict:
    """One acquisition run. `order` in {sequential, concurrent};
    `teardown` in {off, on}; mode derived from order (seq->sync, con->async)."""
    mode = "sync" if order == "sequential" else "async"
    conn_ids = [f"c{i}" for i in range(n)]
    transports = {cid: build_transport(cid, log_dir) for cid in conn_ids}

    reg = ToolRegistry()
    monitor = PeakMonitor()
    monitor.start()

    t0 = time.time()
    if mode == "sync":
        acq = _acquire_sync(reg, conn_ids, transports)
    else:
        acq = asyncio.run(_acquire_async(reg, conn_ids, transports))
    acquisition_ms = (time.time() - t0) * 1000

    if teardown:
        t_td = time.time()
        if mode == "sync":
            _teardown_sync(reg, conn_ids)
        else:
            asyncio.run(_teardown_async(reg, conn_ids))
        teardown_ms = (time.time() - t_td) * 1000
    else:
        teardown_ms = None

    peak = monitor.stop()
    time.sleep(GRACE_SECONDS)
    resident = snapshot()

    log_files = [log_dir / f"{cid}-proxy.log" for cid in conn_ids]
    events = count_events(
        log_files,
        ["proxy_started", "backend_spawn_start", "backend_up", "backend_spawn_failed"],
    )
    timings = connector_timings(log_dir, conn_ids)

    result = {
        "label": label,
        "n": n,
        "order": order,
        "teardown": "on" if teardown else "off",
        "calling_mode": mode,
        "register_ms": round(acq["register_ms"], 1),
        "refresh_ms": round(acq["refresh_ms"], 1),
        "acquisition_ms": round(acquisition_ms, 1),
        "teardown_ms": teardown_ms,
        "events": events,
        "backend_spawn_count": events["backend_spawn_start"],
        "peak": peak,
        "resident_after": resident,
        "refresh_results": acq["refresh_results"],
        "timings_sample": {cid: timings[cid] for cid in conn_ids if cid in timings},
        "grace_seconds": GRACE_SECONDS,
        "versions": versions(),
    }
    pct_line(
        f"RESULT label={label} n={n} order={order} teardown={'on' if teardown else 'off'} "
        f"mode={mode} peak_proxies={peak['peak_proxies']} resident_proxies={resident['proxy_count']} "
        f"resident_backends={resident['backend_count']} backend_spawns={events['backend_spawn_start']} "
        f"acq_ms={round(acquisition_ms, 0)}"
    )
    return result
