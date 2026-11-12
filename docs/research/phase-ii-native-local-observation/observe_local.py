#!/usr/bin/env python3
"""Explicit local observation of one actual native journal effect."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sqlite3
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
RECONCILE_PATH = HERE.parent / "phase-ii-native-publication-reconcile" / "reconcile.py"


def load_reconciler():
    spec = importlib.util.spec_from_file_location("native_local_observation_reconciler", RECONCILE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("reconciler-source-unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main(argv):
    gate = None
    if len(argv) == 5 and argv[3] == "--test-gate":
        gate = argv[4]
        if gate not in ("after-local-observation-before-publication",
                        "after-confirmed-publication-before-settlement"):
            raise SystemExit("usage: observe_local.py OWNER_ROOT REQUEST_ID [--test-gate PHASE]")
    elif len(argv) != 3:
        raise SystemExit("usage: observe_local.py OWNER_ROOT REQUEST_ID [--test-gate PHASE]")
    reconciler = load_reconciler()
    try:
        result = reconciler.observe_local(Path(argv[1]), argv[2], gate)
    except BlockingIOError:
        result = dict(status="refused-writer-guard-busy", reason="existing F4 writer guard is held")
    except (ValueError, OSError, KeyError, TypeError, sqlite3.Error, RuntimeError) as error:
        result = dict(status="refused", reason=str(error), error=type(error).__name__)
    import json
    print(json.dumps(dict(event="native-local-observation", **result), sort_keys=True), flush=True)
    return 0 if result.get("status") == "published" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
