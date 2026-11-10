#!/usr/bin/env python3
"""Independent raw-evidence checks for the bounded ASES-4 native probe."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    args = parser.parse_args()
    raw_path = args.raw.resolve()
    raw = json.loads(raw_path.read_text())
    need(raw.get("schema") == "ases4-native-owner-probe-v1", "raw schema")
    need(raw.get("status") == "PASS", "native probe did not pass")
    sources = raw.get("sources")
    need(isinstance(sources, dict) and sources, "source manifest missing")
    for name, source in sources.items():
        path = Path(source["path"])
        if not path.is_absolute():
            path = REPO / path
        need(path.is_file(), f"source missing: {name}")
        need(sha(path.read_bytes()) == source.get("sha256"), f"source changed: {name}")
    need(isinstance(raw.get("processes"), list), "process evidence missing")
    for process in raw["processes"]:
        need(isinstance(process.get("pid"), int), "process PID missing")
        need(isinstance(process.get("frames"), list), "process frames missing")
        if "exit" in process:
            need(isinstance(process.get("exit_ns"), int), "process exit timestamp missing")
    cases = raw.get("cases")
    need(isinstance(cases, dict) and cases, "native cases missing")
    # Per-case raw-state assertions are added as each frozen history is exercised.
    result = {"status": "PASS", "case_count": len(cases), "source_count": len(sources),
              "raw_sha256": sha(raw_path.read_bytes())}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, sort_keys=True), file=sys.stderr)
        raise
