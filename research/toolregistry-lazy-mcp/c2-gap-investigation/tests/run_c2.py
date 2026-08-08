#!/usr/bin/env python
"""Driver: run each c2-gap-investigation phase as a clean subprocess.

Each phase is its own process (fresh registry, fresh proxy processes).
Captures each phase's stdout+stderr into logs/<phase>-harness.log and
prints a concise summary per phase.

Run:  /tmp/toolregistry-venv/bin/python tests/run_c2.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
TESTS_DIR = Path(__file__).resolve().parent

PHASES = [
    # Option A
    ("phase-a1-control", "phase_a1_control.py"),
    ("phase-a2-selfheal-c2", "phase_a2_selfheal_c2.py"),
    ("phase-a3-intermittent", "phase_a3_intermittent.py"),
    # Option B
    ("phase-b1-traceback", "phase_b1_traceback.py"),
    ("phase-b2-poc", "phase_b2_poc.py"),
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

    if failures:
        print(f"DRIVER FAILURES: {failures}", flush=True)
        sys.exit(1)
    print("DRIVER OK: all phases completed", flush=True)


if __name__ == "__main__":
    main()
