#!/usr/bin/env python
"""TEST 4 — Sparse-Use Workload (principal scenario): N=20, K=3.

Acquire the full 20-tool catalog at init without invoking; invoke exactly 3
selected tools; reach steady state (second call per tool); measure residency
in THREE categories, proxy and backend kept SEPARATE:
  (1) called tools' backends (3) — persistence expected, not a defect;
  (2) called tools' proxies (3) — remain resident post-call (persistent);
  (3) refreshed-but-never-called tools' proxies (17) — THE HEADLINE NUMBER:
      desired ~0 resident.
Teardown OFF and ON (immediate disconnect-after-list boundary; ON closes
every connection manager after the measurement).

ADDENDUM D: connector identity/reuse — record proxy pid + backend pid per
called connector across catalog acquisition -> first call -> second call, to
distinguish 3 correctly-reused active connectors from 3 new + 3 abandoned.

Calling mode: SYNC (matches round-1 style); daemon-thread profile recorded.
Stdio only.
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
    clean_orphans,
    pct_line,
    parse_proxy_log,
    persistence,
    snapshot,
    versions,
    write_json,
    PeakMonitor,
)

from toolregistry import ToolRegistry  # noqa: E402
from toolregistry._async_runtime import AsyncRuntime  # noqa: E402

RUN_LABEL = "test4"
N = 20
K = 3
CALLED = ["c0", "c7", "c15"]


def _conn_for(reg: ToolRegistry, cid: str):
    idx = int(cid.lstrip("c"))
    return reg._mcp_integrations[idx]._connections[0]


def _read_pid_file(path: Path):
    try:
        return int(path.read_text().strip())
    except Exception:
        return None


def run_variant(reg: ToolRegistry, conn_ids, transports, log_dir, teardown_on: bool) -> dict:
    # --- catalog acquisition: register + refresh (nothing invoked yet) ---
    for cid in conn_ids:
        reg.register_from_mcp(transports[cid], namespace=cid)
    refresh_ok = 0
    for cid in conn_ids:
        try:
            AsyncRuntime.run_sync(_conn_for(reg, cid).list_tools())
            refresh_ok += 1
        except Exception as exc:
            pct_line(f"REFRESH_ERROR cid={cid} exc={type(exc).__name__}:{exc}")
    pct_line(f"TEST4 variant teardown={teardown_on} registered={len(conn_ids)} refreshed_ok={refresh_ok}")

    # --- addendum D: identity at acquisition (no persistent process yet) ---
    identity = {
        cid: {
            "acquisition_proxy_pid": None,
            "call1_proxy_pid": None,
            "call2_proxy_pid": None,
            "call1_backend_pid": None,
            "call2_backend_pid": None,
        }
        for cid in CALLED
    }

    # --- invoke the K=3 selected tools twice each (steady state) ---
    for cid in CALLED:
        tool = f"{cid}-add"
        pct_line(f"TEST4 call1 {tool}")
        r1 = reg.invoke(tool, {"a": 1, "b": 2})
        pct_line(f"TEST4 call1 result={getattr(r1, 'result', r1)}")
        # proxy pid: the LATEST proxy_started in this connector's log
        recs = parse_proxy_log(log_dir / f"{cid}-proxy.log")
        starts = [r for r in recs if r["msg"].startswith("proxy_started")]
        if starts:
            last = starts[-1]["msg"]
            identity[cid]["call1_proxy_pid"] = int(last.split("pid=")[1].split(" ")[0])
        identity[cid]["call1_backend_pid"] = _read_pid_file(log_dir / f"{cid}-backend.pid")

    for cid in CALLED:
        tool = f"{cid}-add"
        r2 = reg.invoke(tool, {"a": 3, "b": 4})
        pct_line(f"TEST4 call2 result={getattr(r2, 'result', r2)}")
        recs = parse_proxy_log(log_dir / f"{cid}-proxy.log")
        starts = [r for r in recs if r["msg"].startswith("proxy_started")]
        if starts:
            last = starts[-1]["msg"]
            identity[cid]["call2_proxy_pid"] = int(last.split("pid=")[1].split(" ")[0])
        identity[cid]["call2_backend_pid"] = _read_pid_file(log_dir / f"{cid}-backend.pid")

    time.sleep(GRACE_SECONDS)
    resident_after_calls = snapshot()

    if teardown_on:
        for cid in conn_ids:
            try:
                _conn_for(reg, cid).close_sync()
            except Exception as exc:
                pct_line(f"TEARDOWN_ERROR cid={cid} exc={type(exc).__name__}:{exc}")
        time.sleep(GRACE_SECONDS)
        resident_after_teardown = snapshot()
    else:
        resident_after_teardown = None
        # Cleanup (NOT measurement): close every manager so this variant's
        # persistent connectors cannot orphan into the next variant's
        # snapshots. Without this, the next variant measures 3 stale
        # proxies/backends from this variant in addition to its own.
        # This is itself a lifecycle observation: ToolRegistry persistent
        # connections are NOT auto-closed when the registry is dropped while
        # the AsyncRuntime daemon thread lives (see report Finding on
        # idle-connector reclamation).
        for cid in conn_ids:
            try:
                _conn_for(reg, cid).close_sync()
            except Exception as exc:
                pct_line(f"CLEANUP_ERROR cid={cid} exc={type(exc).__name__}:{exc}")
        time.sleep(GRACE_SECONDS)

    # --- category breakdown from resident pids ---
    called_backends = [
        p for cid in CALLED
        if (p := identity[cid]["call2_backend_pid"]) in resident_after_calls["backend_pids"]
    ]
    called_proxies = [
        p for cid in CALLED
        if (p := identity[cid]["call2_proxy_pid"]) in resident_after_calls["proxy_pids"]
    ]
    never_called_proxies = [
        p for p in resident_after_calls["proxy_pids"] if p not in called_proxies
    ]

    result = {
        "label": f"test4-teardown-{'on' if teardown_on else 'off'}",
        "n": N,
        "k": K,
        "called": CALLED,
        "teardown": "on" if teardown_on else "off",
        "calling_mode": "sync",
        "catalog_tools": sorted(reg.list_tools()),
        "refreshed_ok": refresh_ok,
        "identity": identity,
        "resident_after_calls": resident_after_calls,
        "resident_after_teardown": resident_after_teardown,
        "categories": {
            "called_backends_resident": len(called_backends),
            "called_backend_pids": sorted(called_backends),
            "called_proxies_resident": len(called_proxies),
            "called_proxy_pids": sorted(called_proxies),
            "refreshed_never_called_proxies_resident": len(never_called_proxies),
            "refreshed_never_called_proxy_pids": sorted(never_called_proxies),
            "other_proxy_pids_unclassified": sorted(
                set(resident_after_calls["proxy_pids"]) - set(called_proxies) - set(never_called_proxies)
            ),
        },
        "versions": versions(),
        "persistence": persistence(),
        "grace_seconds": GRACE_SECONDS,
    }
    return result


def main() -> None:
    base = HERE / "logs" / RUN_LABEL
    base.mkdir(parents=True, exist_ok=True)
    orphan_count = clean_orphans()
    pct_line(f"TEST4 begin versions={versions()} pre_cleaned_orphans={orphan_count}")

    results = []
    for teardown_on in (False, True):
        log_dir = base / f"teardown-{'on' if teardown_on else 'off'}"
        log_dir.mkdir(parents=True, exist_ok=True)
        for stale in list(log_dir.glob("*.log")) + list(log_dir.glob("*.pid")):
            stale.unlink()
        reg = ToolRegistry()
        conn_ids = [f"c{i}" for i in range(N)]
        transports = {cid: build_transport(cid, log_dir) for cid in conn_ids}
        res = run_variant(reg, conn_ids, transports, log_dir, teardown_on)
        results.append(res)
        write_json(base / f"test4-teardown-{'on' if teardown_on else 'off'}.json", res)
        pct_line(
            f"TEST4 result teardown={'on' if teardown_on else 'off'} "
            f"called_backends={res['categories']['called_backends_resident']} "
            f"called_proxies={res['categories']['called_proxies_resident']} "
            f"never_called_proxies={res['categories']['refreshed_never_called_proxies_resident']}"
        )

    off = results[0]
    on = results[1]
    pct_line(
        f"TEST4 summary headline_teardown_off="
        f"{off['categories']['refreshed_never_called_proxies_resident']} "
        f"headline_teardown_on="
        f"{on['categories']['refreshed_never_called_proxies_resident']} "
        f"reuse_consistent="
        f"{all(off['identity'][c]['call1_proxy_pid'] == off['identity'][c]['call2_proxy_pid'] and off['identity'][c]['call1_backend_pid'] == off['identity'][c]['call2_backend_pid'] for c in CALLED)}"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
