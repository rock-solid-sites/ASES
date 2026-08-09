#!/usr/bin/env python
"""Aggregate per-run JSON results into report-ready tables (stdout).

Loads every result JSON under logs/ and prints:
  - Test 2 table (conditions A/B)
  - Test 3 sweep table (N x mode x teardown)
  - Test 4 category breakdown
  - Test 5a/5b key observations
  - Test 6 boundary table
Uses only committed log artifacts. Stdio-only scope assumed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
LOGS = HERE / "logs"


def load(p: Path) -> dict:
    with open(p) as fh:
        return json.load(fh)


def row3(r: dict) -> str:
    res = r.get("resident_after", {})
    peak = r.get("peak", {})
    threads = res.get("threads", {})
    return (
        f"| {r['n']} | {r['order']} | {r['teardown']} | {r['calling_mode']} "
        f"| {peak.get('peak_proxies')} | {res.get('proxy_count')} "
        f"| {peak.get('peak_backends')} | {res.get('backend_count')} "
        f"| {res.get('proxy_rss_kb')} | {res.get('backend_rss_kb')} "
        f"| {round(r.get('acquisition_ms', 0))} "
        f"| {threads.get('async_runtime_threads')} | {r.get('backend_spawn_count')} |"
    )


def main() -> None:
    print("=== TEST 2 ===")
    t2 = LOGS / "test2"
    for cond in ("A", "B"):
        f = t2 / f"test2-cond{cond}.json"
        if f.exists():
            r = load(f)
            res = r["resident_after"]
            peak = r["peak"]
            print(
                f"Condition {cond}: peakP={peak['peak_proxies']} resP={res['proxy_count']} "
                f"peakB={peak['peak_backends']} resB={res['backend_count']} "
                f"proxyRSS={res['proxy_rss_kb']} backendRSS={res['backend_rss_kb']} "
                f"acq_ms={round(r['acquisition_ms'])} backendSpawns={r['backend_spawn_count']} "
                f"asyncThreads={res['threads']['async_runtime_threads']}"
            )

    print("=== TEST 3 (header: N|Mode|Teardown|CallMode|PeakP|ResP|PeakB|ResB|ProxyRSS|BackendRSS|AcqMs|AsyncThreads|BackendSpawns) ===")
    t3 = LOGS / "test3"
    if t3.exists():
        for f in sorted(t3.glob("*.json")):
            r = load(f)
            print(row3(r))

    print("=== TEST 4 ===")
    t4 = LOGS / "test4"
    for teardown in ("off", "on"):
        f = t4 / f"test4-teardown-{teardown}.json"
        if f.exists():
            r = load(f)
            c = r["categories"]
            res = r["resident_after_calls"]
            print(
                f"teardown={teardown}: called_backends={c['called_backends_resident']} "
                f"called_proxies={c['called_proxies_resident']} "
                f"never_called_proxies={c['refreshed_never_called_proxies_resident']} "
                f"(resP={res['proxy_count']} resB={res['backend_count']} "
                f"proxyRSS={res['proxy_rss_kb']} backendRSS={res['backend_rss_kb']})"
            )
            print(f"  identity: {json.dumps(r['identity'], indent=2)}")

    print("=== TEST 5 ===")
    t5 = LOGS / "test5"
    for sub in ("5a", "5b"):
        f = t5 / sub / f"test{sub}.json"
        if f.exists():
            r = load(f)
            print(f"{sub}: {json.dumps({k: v for k, v in r.items() if k not in ('resident_before_change', 'resident_after_notify', 'resident_before_first_use', 'resident_after_first_use')}, indent=2)}")
            for k in ("resident_before_change", "resident_after_notify", "resident_before_first_use", "resident_after_first_use"):
                if k in r:
                    print(f"  {k}: proxies={r[k]['proxy_count']} backends={r[k]['backend_count']}")

    print("=== TEST 6 ===")
    t6 = LOGS / "test6"
    f = t6 / "test6.json"
    if f.exists():
        r = load(f)
        for k in ("resident_catalog_no_teardown", "resident_catalog_after_teardown",
                  "resident_after_call", "resident_after_call_teardown"):
            v = r[k]
            print(f"{k}: proxies={v['proxy_count']} backends={v['backend_count']}")


if __name__ == "__main__":
    main()
