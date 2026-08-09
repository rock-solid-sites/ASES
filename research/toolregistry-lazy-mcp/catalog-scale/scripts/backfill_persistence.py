#!/usr/bin/env python
"""Deterministic persistence-field backfill for already-committed result JSONs.

Context (settle task #306): the measurement scripts now record the
source-verified persistence config in every per-run result dict
(common.persistence(), addendum B). Tests 1 and 2 were re-run with the
patched scripts so their JSONs are genuine artifacts. Tests 3-6 and
threadcheck were NOT re-run: their measured values (timings, PIDs, RSS,
acq_ms) are what the report tables cite, and re-running would change those
values and silently invalidate the report's committed tables.

The persistence value is a CONFIG CONSTANT, not a measurement: every run in
this corpus used the default persistent=True (verified against the installed
toolregistry 0.15.0 source at registration.py:94,167 and connection.py:37).
This script inserts ONLY that documented constant into result JSONs that lack
it, preserving every measured field. The transformation is deterministic and
re-derivable: run it again on a clean corpus and the output is identical.

Usage: /tmp/toolregistry-venv/bin/python scripts/backfill_persistence.py
Stdio-only corpus; does not touch control-*.json (backend manifests, not
per-run result JSONs).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # .../catalog-scale
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import persistence  # noqa: E402


def main() -> None:
    logs = HERE / "logs"
    candidates = sorted(logs.glob("**/*.json"))
    changed: list[str] = []
    skipped: list[str] = []

    for path in candidates:
        # control-*.json are static backend manifests, not per-run result JSONs.
        if path.name.startswith("control-"):
            skipped.append(str(path.relative_to(HERE)))
            continue
        with open(path, encoding="utf-8") as fh:
            obj = json.load(fh)
        if "persistence" in obj:
            skipped.append(str(path.relative_to(HERE)))
            continue
        obj["persistence"] = persistence()
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2, default=str)
            fh.write("\n")
        changed.append(str(path.relative_to(HERE)))

    print(f"BACKFILL changed={len(changed)} skipped={len(skipped)}")
    for rel in changed:
        print(f"  +persistence {rel}")
    for rel in skipped:
        print(f"  =already/control {rel}")


if __name__ == "__main__":
    main()
