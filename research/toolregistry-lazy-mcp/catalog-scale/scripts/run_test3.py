#!/usr/bin/env python
"""TEST 3 — Scaling Sweep.

N = 1, 5, 10, 20, 50. For every N: sequential AND concurrent acquisition,
teardown off AND on — four conditions per N (20 runs).

Recorded per run: peak/resident-after proxy count, peak/resident-after
backend count, proxy RSS, backend RSS, acquisition wall-clock duration,
catalog ops completed, proxy starts, backend starts, connect / tools/list
round-trip / disconnect timing.

DECISIVE MEASUREMENT: resident-after state (NOT peak — concurrency
legitimately raises peak). Desired: resident-after approx flat as N
increases with K=0. Undesired: resident-after grows proportionally with N.

Calling modes: sequential -> SYNC; concurrent -> ASYNC (recorded per run).
Stdio only.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from acquire import run_acquisition  # noqa: E402
from common import clean_orphans, pct_line, write_json  # noqa: E402

RUN_LABEL = "test3"
NS = [1, 5, 10, 20, 50]
ORDERS = ["sequential", "concurrent"]
TEARDOWNS = [False, True]


def main() -> None:
    base = HERE / "logs" / RUN_LABEL
    base.mkdir(parents=True, exist_ok=True)
    orphan_count = clean_orphans()
    pct_line(f"TEST3 begin pre_cleaned_orphans={orphan_count}")

    results: list[dict] = []
    for n in NS:
        for order in ORDERS:
            for teardown in TEARDOWNS:
                tag = f"n{n}-{order}-{'on' if teardown else 'off'}"
                log_dir = base / tag
                log_dir.mkdir(parents=True, exist_ok=True)
                for stale in list(log_dir.glob("*.log")) + list(log_dir.glob("*.pid")):
                    stale.unlink()
                result = run_acquisition(n, order, teardown, log_dir, tag)
                results.append(result)
                write_json(base / f"{tag}.json", result)

    pct_line("TEST3 done rows=" + str(len(results)))
    # Compact resident-after table for quick inspection
    pct_line("TEST3 table label|order|teardown|peakP|resP|peakB|resB|backendSpawns")
    for r in results:
        pct_line(
            f"TEST3 {r['label']}|{r['order']}|{r['teardown']}|"
            f"{r['peak']['peak_proxies']}|{r['resident_after']['proxy_count']}|"
            f"{r['peak']['peak_backends']}|{r['resident_after']['backend_count']}|"
            f"{r['events']['backend_spawn_start']}"
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
