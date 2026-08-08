#!/usr/bin/env python
"""Sequential driver: run tests 2..6 in order, each as a fresh subprocess.

Tests share nothing (fresh registries, fresh log dirs). Stdio only. Runs
from the pinned venv. Exit code reflects any failure; individual test
scripts exit 0 on success.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SCRIPTS = HERE / "scripts"
TESTS = [
    ("test2", "run_test2.py"),
    ("test3", "run_test3.py"),
    ("test4", "run_test4.py"),
    ("test5", "run_test5.py"),
    ("test6", "run_test6.py"),
]


def main() -> None:
    print("RUN_ALL begin", flush=True)
    selected = sys.argv[1:] or [label for label, _ in TESTS]
    for label, script in TESTS:
        if label not in selected:
            print(f"RUN_ALL skipping {label}", flush=True)
            continue
        log_dir = HERE / "logs" / label
        log_dir.mkdir(parents=True, exist_ok=True)
        run_log = log_dir / "run.log"
        print(f"RUN_ALL starting {label}", flush=True)
        with open(run_log, "w") as fh:
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / script)],
                stdout=fh, stderr=subprocess.STDOUT,
            )
        print(f"RUN_ALL finished {label} rc={proc.returncode}", flush=True)
        if proc.returncode != 0:
            print(f"RUN_ALL FAILED at {label} rc={proc.returncode}", flush=True)
            sys.exit(proc.returncode)
    print("RUN_ALL done", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
