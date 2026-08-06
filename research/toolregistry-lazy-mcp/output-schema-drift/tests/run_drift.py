#!/usr/bin/env python
"""Driver: run each output-schema-drift phase as a clean subprocess.

Each phase is its own process (fresh registry, fresh proxy processes),
matching the "run each test as its own clean session" rule.  Test E and
Test F intentionally share a session WITHIN their phase scripts (E: the
repeat happens in the same session as its reproduced Test C call; F: the
unrelated tool is called in the same session as the failure).

Captures each phase's stdout+stderr into logs/<phase>-harness.log
(proxy + backend log lines are inherited by these streams too) and
prints a concise summary per phase.

Run:  /tmp/toolregistry-venv/bin/python tests/run_drift.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
TESTS_DIR = Path(__file__).resolve().parent

PHASES = [
    ("test-a", "phase_a.py"),
    ("test-b", "phase_b.py"),
    ("test-c", "phase_c.py"),
    ("test-c2", "phase_c2.py"),
    ("test-c3", "phase_c3.py"),
    ("test-d", "phase_d.py"),
    ("test-e", "phase_e.py"),
    ("test-f", "phase_f.py"),
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
