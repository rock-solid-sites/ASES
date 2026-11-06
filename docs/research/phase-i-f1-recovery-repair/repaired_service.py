#!/usr/bin/env python3
"""Isolated experimental C11 wrapper; original service/core remain unchanged."""
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
import threading

sys.dont_write_bytecode = True  # Preserve the pinned source capture's exact file set.

ORIGINAL = Path(__file__).resolve().parent.parent / "phase-i-sol-integration/evidence/sources/f1/docs/research/phase-i-f1/c11-sqlite/c11_service.py"
spec = importlib.util.spec_from_file_location("original_c11_repair_dependency", ORIGINAL)
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
persistent = original.persistent


def encode(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":"))


def bound_record(bundle, content):
    if not isinstance(bundle, dict) or set(bundle) != {"accepted_content", "required"}:
        return None
    required = bundle["required"]
    if (not isinstance(bundle["accepted_content"], str) or bundle["accepted_content"] != content
            or not isinstance(required, dict) or set(required) != set(original.FIELDS)
            or not all(isinstance(required[key], str) for key in original.FIELDS)):
        return None
    return json.loads(encode(bundle))  # Retain exact values, detached from configuration objects.


def current_record(db):
    current = original.query(db)
    if current["status"] == "not_accepted":
        return None
    if current["status"] != "available":
        raise ValueError("incompatible-current-accepted-pair")
    return dict(accepted_content=current["accepted_content"], required=current["required"])


def prepare(path):
    """Explicit trusted schema preparation; ordinary recovery never calls this."""
    store = persistent.Store(str(path), "work", "independent")
    db = store.db
    try:
        db.execute("BEGIN IMMEDIATE")
        record = current_record(db)
        db.execute("CREATE TABLE IF NOT EXISTS retained_observations(record TEXT PRIMARY KEY)")
        if record is not None:
            db.execute("INSERT OR IGNORE INTO retained_observations VALUES(?)", (encode(record),))
        db.execute("COMMIT")
    except BaseException:
        if db.in_transaction:
            db.execute("ROLLBACK")
        raise
    finally:
        db.close()


def serve(config):
    if config.get("observation_mode", "atomic") != "atomic":
        raise ValueError("only-atomic-repaired-profile")

    class Store(persistent.Store):
        pending = None

        def __init__(self):
            super().__init__(config["path"], config["root"], config["profile"])
            self.db.execute("SELECT record FROM retained_observations LIMIT 0")
            self.db = original.Trace(self.db, Path(config["trace"]))

        def write(self, state):
            super().write(state)
            if self.pending is not None:
                raw = encode(self.pending)
                self.db.execute("INSERT INTO consumer_observations(id,record) VALUES(1,?) "
                                "ON CONFLICT(id) DO UPDATE SET record=excluded.record", (raw,))
                self.db.execute("INSERT OR IGNORE INTO retained_observations VALUES(?)", (raw,))

    class Boundary(persistent.Boundary):
        def __init__(self):
            self.store = Store()
            self.profile = config["profile"]
            self.lock = threading.Lock()

        def propose(self, current, context, q):
            self.store.pending = None
            candidate = super().propose(current, context, q)
            if candidate is None:
                return None
            retained = current_record(self.store.db)
            if retained is not None and self.store.db.execute(
                    "SELECT 1 FROM retained_observations WHERE record=?", (encode(retained),)).fetchone() is None:
                return None  # Do not hide a missing required historical record.
            if q.kind == "accept" or candidate.content != current.content:
                if "acceptance_bundle" in config:
                    self.store.pending = bound_record(config["acceptance_bundle"], candidate.content)
                    if self.store.pending is None:
                        return None
                elif candidate.content != current.content or retained is None:
                    return None
                # Otherwise reaccept unchanged content while retaining its existing pair.
            return candidate

        def resolve(self, context, q, gate):
            result = super().resolve(context, q, gate)
            return dict(result, consumer_query=original.query(self.store.db))

    persistent.serve(config, Boundary())


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--prepare":
        prepare(Path(sys.argv[2]))
    elif len(sys.argv) == 3 and sys.argv[1] == "--reader":
        original.reader(sys.argv[2])
    else:
        serve(json.loads(sys.argv[1], object_pairs_hook=original.core.unique_object))
