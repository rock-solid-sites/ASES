#!/usr/bin/env python3
"""Native owner-seal versus current F4 append histories."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import time
import traceback
import concurrent.futures

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OWNERSHIP = REPO / "docs/research/phase-ii-native-ownership/probe.py"
spec = importlib.util.spec_from_file_location("native_ownership_helpers", OWNERSHIP)
helpers = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = helpers
spec.loader.exec_module(helpers)
CONTENT = helpers.CONTENT


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sqlite_snapshot(path: Path, queries: dict[str, str]) -> dict:
    """Consistent read-only SQLite snapshot plus a serialised DB image."""
    uri = path.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True, timeout=2) as source:
        source.execute("BEGIN")
        result = {name: source.execute(sql).fetchall() for name, sql in queries.items()}
        integrity = source.execute("PRAGMA integrity_check").fetchone()[0]
        memory = sqlite3.connect(":memory:")
        source.backup(memory)
        image = memory.serialize()
        memory.close()
        source.rollback()
    return {"path": str(path), "queries": result, "integrity_check": integrity,
            "snapshot_sha256": sha(image), "snapshot_size": len(image), "snapshot_raw_hex": image.hex()}


def direct_owner_snapshot(owner_root: Path, f1_path: Path) -> dict:
    """Read selected immutable CURRENT state and F1/L6 directly, avoiding owner.read()."""
    protected = owner_root / "protected"
    current_raw = (protected / "CURRENT").read_bytes()
    selector = current_raw.decode().strip()
    record_raw = (protected / selector).read_bytes()
    state = json.loads(record_raw)
    l6root = protected
    l6 = sqlite_snapshot(l6root / "catalog.sqlite", {
        "unit": "SELECT live,sealed FROM unit",
        "dependencies": "SELECT name,kind,sha256,size,disposed FROM dependencies ORDER BY name",
    })
    f1 = sqlite_snapshot(f1_path, {
        "kernel": "SELECT id,root,profile,version,view FROM kernel ORDER BY id",
        "selected": "SELECT id,record FROM consumer_observations ORDER BY id",
        "retained": "SELECT record FROM retained_observations ORDER BY record",
    })
    files = {}
    object_root = protected / "objects"
    for path in sorted(object_root.iterdir()):
        raw = path.read_bytes()
        files[path.name] = {"raw_hex": raw.hex(), "sha256": sha(raw), "size": len(raw),
                            "inode": path.stat().st_ino, "mode": path.stat().st_mode & 0o777}
    return {
        "observed_ns": time.monotonic_ns(), "current_raw_hex": current_raw.hex(),
        "selector": selector, "record_raw_hex": record_raw.hex(), "record_sha256": sha(record_raw),
        "state": state, "native_owner": state["native_owner"], "current_ingress": state["current_ingress"],
        "record_files": helpers.tree(protected), "f1_sqlite": f1, "l6_sqlite": l6,
        "l6_files": files,
    }


def journal_snapshot(f4) -> dict:
    raw = f4.journal.read_bytes()
    events = [json.loads(line) for line in raw.splitlines() if line]
    return {"path": str(f4.journal), "raw_hex": raw.hex(), "sha256": sha(raw),
            "size": len(raw), "events": events}


def read_until_gate(f4, expected: str) -> dict:
    line = f4.sink.read(timeout=20)
    frame = json.loads(line)
    if frame.get("event") != "GATE" or frame.get("stage") != expected:
        raise RuntimeError(f"expected F4 gate {expected}, got {frame!r}")
    return frame


def advance_to_reply(f4, future) -> tuple[list[dict], dict]:
    gates = []
    while True:
        try:
            value = future.result(timeout=0.2)
            return gates, value
        except concurrent.futures.TimeoutError:
            line = f4.sink.read(timeout=20)
            frame = json.loads(line)
            if frame.get("event") == "GATE":
                gates.append(frame)
                f4.sink.p.stdin.write(b"continue\n")
                f4.sink.p.stdin.flush()
            else:
                raise RuntimeError(f"unexpected native sink frame during append: {frame!r}")


def append_call(f4, envelope: dict) -> dict:
    before = journal_snapshot(f4)
    request = {"authority_version": 1, "request_id": envelope["request_id"],
               "payload": canonical(envelope)}
    try:
        response = f4.http(f4.sink_socket, "/submit", request)
    except Exception as error:
        response = {"transport_error": type(error).__name__ + ":" + str(error)}
    return {"path": "/submit", "request": request, "envelope": envelope,
            "before": before, "response": response, "after": journal_snapshot(f4)}


def start_append(f4, envelope: dict, pool):
    before = journal_snapshot(f4)
    request = {"authority_version": 1, "request_id": envelope["request_id"],
               "payload": canonical(envelope)}
    future = pool.submit(f4.call, "/submit", request)
    gate = read_until_gate(f4, "guarded" if envelope.get("request_id", "").endswith("append-first")
                           else "before-admission")
    return {"path": "/submit", "request": request, "envelope": envelope,
            "before": before, "gate": gate}, future


def submit_with_gate(f4, envelope: dict) -> dict:
    request = {"authority_version": 1, "request_id": envelope["request_id"],
               "payload": canonical(envelope)}
    if f4.config.get("gate") != "before-admission":
        return {"request": request, "gate": None, "result": f4.call("/submit", request)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(f4.call, "/submit", request)
        gate = read_until_gate(f4, "before-admission")
        f4.sink.p.stdin.write(b"continue\n")
        f4.sink.p.stdin.flush()
        return {"request": request, "gate": gate, "result": future.result(timeout=15)}


def f4_cut_capture(f4) -> dict:
    """Capture journal bytes and current local/published cuts around exact-ID retry."""
    return {"journal": journal_snapshot(f4),
            "sink_status": f4.http(f4.sink_socket, "/status"),
            "witness_status": f4.http(f4.witness_socket, "/status")}


def create_history(out: Path, label: str) -> dict:
    case_root = out / "state" / label
    setup = helpers.setup_native_f3(case_root, world="A", activate=True)
    owner_root = Path(setup["owner_root"])
    f1_path = Path(setup["f1_root"]) / "store.sqlite"
    witness_root = "native-revocation-" + label + "-" + str(time.monotonic_ns())
    f4 = helpers.NativeF4(case_root / "f4", owner_root, witness_root,
                          gate="guarded" if label == "append-first" else "before-admission")
    owner = helpers.OwnerProcess(owner_root)
    initial_reply = owner.call({"op": "read"})
    initial_snapshot = initial_reply["reply"]["snapshot"]
    owner.close()
    envelope = helpers.native_envelope(initial_snapshot, witness_root + (":append-first" if label == "append-first" else ":seal-first"))
    case = {"label": label, "setup": setup, "f4_lifecycle": f4.lifecycle_calls,
            "witness_init": f4.witness_init, "initial_owner_snapshot": initial_snapshot,
            "initial_owner_direct": direct_owner_snapshot(owner_root, f1_path),
            "initial_envelope": envelope, "authority_version": 1,
            "f4_config": f4.config, "f4_processes": {"sink": f4.sink.meta, "witness": f4.witness.meta}}

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        append_meta, future = start_append(f4, envelope, pool)
        case["append_attempt"] = append_meta
        case["owner_at_gate"] = direct_owner_snapshot(owner_root, f1_path)
        case["journal_at_gate"] = journal_snapshot(f4)
        contender = helpers.OwnerProcess(owner_root)
        case["contender"] = {"request": {"op": "seal"}, "reply": contender.call({"op": "seal"}),
                              "process": contender.meta}
        contender.close()
        case["owner_after_contender"] = direct_owner_snapshot(owner_root, f1_path)
        case["journal_after_contender"] = journal_snapshot(f4)
        if label == "append-first":
            # Release the existing guarded gate. Capture and release later native gates.
            f4.sink.p.stdin.write(b"continue\n")
            f4.sink.p.stdin.flush()
            gates, append_reply = advance_to_reply(f4, future)
            case["append_later_gates"] = gates
            case["append_reply"] = append_reply
            case["owner_after_append"] = direct_owner_snapshot(owner_root, f1_path)
            case["journal_after_append"] = journal_snapshot(f4)
            owner = helpers.OwnerProcess(owner_root)
            case["seal_retry"] = owner.call({"op": "seal"})
            case["owner_after_seal"] = direct_owner_snapshot(owner_root, f1_path)
            case["move"] = owner.call({"op": "move"})
            case["activate"] = owner.call({"op": "activate"})
            after_move_snapshot = owner.call({"op": "read"})["reply"]["snapshot"]
            case["post_move_owner_snapshot"] = after_move_snapshot
            case["current_envelope"] = helpers.native_envelope(after_move_snapshot, witness_root + ":after-move")
            owner.close()
            case["denied_current"] = submit_with_gate(f4, case["current_envelope"])
            case["owner_after_current_denial"] = direct_owner_snapshot(owner_root, f1_path)
            case["historical_exact_retry_before"] = f4_cut_capture(f4)
            case["historical_exact_retry"] = f4.submit(envelope, authority_version=1)
            case["historical_exact_retry_after"] = f4_cut_capture(f4)
            case["historical_status"] = f4.http(f4.sink_socket, "/status")
        else:
            owner = helpers.OwnerProcess(owner_root)
            case["seal"] = case["contender"]["reply"]
            case["owner_after_seal"] = direct_owner_snapshot(owner_root, f1_path)
            f4.sink.p.stdin.write(b"continue\n")
            f4.sink.p.stdin.flush()
            gates, append_reply = advance_to_reply(f4, future)
            case["append_later_gates"] = gates
            case["append_reply"] = append_reply
            case["owner_after_denial"] = direct_owner_snapshot(owner_root, f1_path)
            case["journal_after_denial"] = journal_snapshot(f4)
            # While sealed the stale envelope and a newly selected envelope both fail.
            case["fresh_sealed_snapshot"] = owner.call({"op": "read"})["reply"]["snapshot"]
            case["fresh_sealed_envelope"] = helpers.native_envelope(
                case["fresh_sealed_snapshot"], witness_root + ":fresh-sealed")
            case["denied_fresh_sealed"] = submit_with_gate(f4, case["fresh_sealed_envelope"])
            case["move"] = owner.call({"op": "move"})
            case["activate"] = owner.call({"op": "activate"})
            current_snapshot = owner.call({"op": "read"})["reply"]["snapshot"]
            case["post_move_owner_snapshot"] = current_snapshot
            case["current_envelope"] = helpers.native_envelope(current_snapshot, witness_root + ":after-move")
            owner.close()
            case["denied_current"] = submit_with_gate(f4, case["current_envelope"])
            case["owner_after_current_denial"] = direct_owner_snapshot(owner_root, f1_path)
            case["historical_status"] = f4.http(f4.sink_socket, "/status")

    case["journal_final"] = journal_snapshot(f4)
    case["f4_final_snapshot"] = f4.snapshot()
    case["owner_tree_final"] = helpers.tree(owner_root)
    case["f1_final"] = helpers.f1_raw(f1_path)
    case["processes"] = helpers.PROCESSES
    f4.close(True)
    return case


def source_manifest() -> dict:
    # Keep the frozen native-owner probe's core provenance and add the exact
    # F4 composition modules that this history executes, plus this probe.
    result = helpers.source_manifest()
    research = REPO / "docs/research"
    receipt = (research / "phase-i-sol-integration/evidence/sources/receipt"
               / "research/phase-i-t18-sink-order-20261103")
    paths = {
        "native_revocation_probe": HERE / "probe.py",
        "native_ownership_probe": OWNERSHIP,
        "native_helpers": helpers.NATIVE_HELPERS_PATH,
        "f4_continuation_sink": research / "phase-i-continuation-stack/continuation_sink.py",
        "f4_composed_sink": research / "phase-i-composed-effects/composed_sink.py",
        "f4_cold_factory": research / "phase-i-cold-activation/cold_sink.py",
        "f4_admission_sink": research / "phase-i-effect-admission/admission_sink.py",
        "f4_admission": research / "phase-i-effect-admission/admission.py",
        "f4_retry_candidate": research / "phase-i-effect-retry/candidate.py",
        "f4_published_cut_sink": receipt / "published-cut/cut_sink.py",
        "f4_managed_sink": receipt / "managed-revocation/managed_sink.py",
        "f4_managed_base": receipt / "run.py",
        "f1_bootstrap_service": (helpers.repair.ORIGINAL.parent.parent.parent
                                  / "kernel-0/kernel0_recovery_service.py"),
    }
    for name, path in paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"required source provenance input missing: {path}")
        result[name] = {"path": str(path.relative_to(REPO)), "sha256": sha(path.read_bytes())}
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=HERE / "evidence/run-01")
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"refusing nonempty output directory: {out}")
    out.mkdir(parents=True, exist_ok=True)
    raw = {"schema": "ases4-native-revocation-append-v1", "started_ns": time.monotonic_ns(),
           "sources": source_manifest(), "cases": {}, "status": "RUNNING"}
    try:
        raw["cases"]["append_first"] = create_history(out, "append-first")
        raw["cases"]["seal_first"] = create_history(out, "seal-first")
        raw["status"] = "PASS"
    except BaseException as error:
        raw["status"] = "PROBE_FAILED"
        raw["failure"] = {"type": type(error).__name__, "message": str(error),
                          "traceback": traceback.format_exc(), "processes": helpers.PROCESSES}
        (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
        raise
    raw["finished_ns"] = time.monotonic_ns()
    (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": raw["status"], "raw": str(out / "raw.json")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
