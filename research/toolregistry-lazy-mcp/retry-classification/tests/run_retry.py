#!/usr/bin/env python
"""Driver: run each retry-classification phase as a clean subprocess.

Each phase is its own process (fresh registry, fresh proxy processes),
matching the "run each test as its own clean session" rule.  Captures each
phase's stdout+stderr into logs/<phase>-harness.log (proxy + backend log
lines are inherited by these streams too) and prints a concise summary per
phase.

Run:  /tmp/toolregistry-venv/bin/python tests/run_retry.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
TESTS_DIR = Path(__file__).resolve().parent

PHASES = [
    ("test-1-control", "phase_1_control.py"),
    ("test-2-classified", "phase_2_classified.py"),
    ("test-3-connection", "phase_3_connection.py"),
    ("test-3b-proxy-retry", "phase_3b_proxy_retry.py"),
]


def main() -> None:
    LOGS_DIR.mkdir(exist_ok=True)
    failures = []
    for phase, script in PHASES:
        harness_log = LOGS_DIR / f"{phase}-harness.log"
        print(f"=== {phase}: {script} -> {harness_log.name} ===", flush=True)
        with open(harness_log, "w", encoding="utf-8") as fh:
            proc = subprocess.run(
                [sys.executable, str(TESTS_DIR / script)],
                stdout=fh,
                stderr=subprocess.STDOUT,
                text=True,
            )
        print(f"=== {phase}: exit={proc.returncode}", flush=True)
        if proc.returncode != 0:
            failures.append(phase)
        tail = harness_log.read_text(encoding="utf-8").splitlines()
        verdicts = [ln for ln in tail if "RESULT" in ln or "phase_done" in ln]
        for ln in verdicts[-6:]:
            print(f"    {ln}", flush=True)
        # Echo the measurement lines (INVOKE deltas + spawn/proxy counters)
        # so each driver run leaves a self-contained numeric record even
        # when the per-phase harness logs are overwritten by the next run.
        for ln in tail:
            if "|INVOKE|" in ln or "|_SPAWN_COUNTS " in ln or "INVOKE_THREAD_DONE" in ln:
                print(f"    {ln.split('|', 3)[-1]}", flush=True)

    if failures:
        print(f"DRIVER FAILURES: {failures}", flush=True)
        sys.exit(1)
    print("DRIVER OK: all phases completed", flush=True)


if __name__ == "__main__":
    main()
