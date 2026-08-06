#!/usr/bin/env python
"""Driver: run each validation phase as a clean subprocess.

Each phase is its own process (fresh registry, fresh proxy processes),
matching the "each numbered test as its own clean session" rule — with
Tests 1-3 intentionally sharing one session inside phase123.py, per the
brief's "continue the same session/registry" instructions.

Captures each phase's stdout+stderr into logs/<phase>-harness.log
(proxy + backend log lines are inherited by these streams too) and
prints a concise summary per phase.

Run:  /tmp/toolregistry-venv/bin/python tests/run_tests.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
TESTS_DIR = Path(__file__).resolve().parent

PHASES = [
    ("tests1-3", "phase123.py", True),
    ("test4", "phase4.py", True),
    ("test5", "phase5.py", True),
    ("baseline-always-on", "baseline_always_on.py", True),
]


def main() -> None:
    LOGS_DIR.mkdir(exist_ok=True)
    failures = []
    for phase, script, _required in PHASES:
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
        # Echo the phase's final verdict lines for quick scanning.
        tail = harness_log.read_text(encoding="utf-8").splitlines()
        verdicts = [ln for ln in tail if "RESULT" in ln or "phase_done" in ln]
        for ln in verdicts[-8:]:
            print(f"    {ln}", flush=True)

    if failures:
        print(f"DRIVER FAILURES: {failures}", flush=True)
        sys.exit(1)
    print("DRIVER OK: all phases completed", flush=True)


if __name__ == "__main__":
    main()
