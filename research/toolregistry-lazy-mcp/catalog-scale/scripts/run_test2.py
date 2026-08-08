#!/usr/bin/env python
"""TEST 2 — Catalog Refresh Residency (single N=10).

Full acquisition (register + session-init refresh), invoke nothing.
Measured SEPARATELY for proxies and backends: peak process count,
resident-after count, RSS, acquisition duration.

  Condition A = normal/current behavior (no explicit reclamation).
  Condition B = immediate proxy teardown (disconnect right after returning
                catalog; diagnostic boundary only).
Expected under B: proxy residency ~= 0, backend residency = 0.
Failure under B indicates the proxy's own connection lifecycle misbehaves.

Calling mode: SYNC (sequential) for both conditions; daemon-thread count
recorded per addendum B. Stdio only.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from acquire import run_acquisition  # noqa: E402
from common import clean_orphans, pct_line, write_json  # noqa: E402

RUN_LABEL = "test2"
N = 10


def main() -> None:
    base = HERE / "logs" / RUN_LABEL
    base.mkdir(parents=True, exist_ok=True)
    orphan_count = clean_orphans()
    pct_line(f"TEST2 begin pre_cleaned_orphans={orphan_count}")

    runs = {}
    for cond, teardown in (("A", False), ("B", True)):
        log_dir = base / f"condition-{cond}"
        log_dir.mkdir(parents=True, exist_ok=True)
        for stale in list(log_dir.glob("*.log")) + list(log_dir.glob("*.pid")):
            stale.unlink()
        result = run_acquisition(N, "sequential", teardown, log_dir, f"test2-cond{cond}")
        runs[cond] = result
        write_json(base / f"{RUN_LABEL}-cond{cond}.json", result)

    a, b = runs["A"], runs["B"]
    pct_line(
        f"TEST2 summary condA resident_proxies={a['resident_after']['proxy_count']} "
        f"resident_backends={a['resident_after']['backend_count']} "
        f"condB resident_proxies={b['resident_after']['proxy_count']} "
        f"resident_backends={b['resident_after']['backend_count']} "
        f"backend_spawns_A={a['events']['backend_spawn_start']} "
        f"backend_spawns_B={b['events']['backend_spawn_start']}"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
