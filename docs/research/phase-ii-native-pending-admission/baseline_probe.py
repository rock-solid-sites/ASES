#!/usr/bin/env python3
"""Prove the pinned NativeAdmission pending-reservation baseline with real services."""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OWNERSHIP = REPO / "docs/research/phase-ii-native-ownership"
RECONCILE = REPO / "docs/research/phase-ii-native-publication-reconcile/reconcile.py"
OBSERVE = REPO / "docs/research/phase-ii-native-local-observation/observe_local.py"
sys.path.insert(0, str(OWNERSHIP))
import probe


def source_hashes():
    paths = {
        "native_owner": OWNERSHIP / "native_owner.py",
        "native_sink": OWNERSHIP / "native_sink.py",
        "owner_cli": OWNERSHIP / "owner_cli.py",
        "probe": OWNERSHIP / "probe.py",
        "unix_transport": OWNERSHIP / "unix_transport.py",
        "retry_candidate": REPO / "docs/research/phase-i-effect-retry/candidate.py",
        "admission": REPO / "docs/research/phase-i-effect-admission/admission.py",
        "admission_sink": REPO / "docs/research/phase-i-effect-admission/admission_sink.py",
        "composed_sink": REPO / "docs/research/phase-i-composed-effects/composed_sink.py",
        "continuation_sink": REPO / "docs/research/phase-i-continuation-stack/continuation_sink.py",
        "cold_sink": REPO / "docs/research/phase-i-cold-activation/cold_sink.py",
        "reconcile": RECONCILE,
        "observe_local": OBSERVE,
    }
    return {name: {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                   "size": path.stat().st_size}
            for name, path in paths.items()}


def owner_read(root):
    owner = probe.OwnerProcess(root)
    frame = owner.call({"op": "read"})
    owner.close()
    return frame, owner.meta


def owner_effects(frame):
    return frame["reply"]["snapshot"]["state"]["native_owner"]["effects"]


def refresh_envelope(owner_root, request_id):
    frame, process = owner_read(owner_root)
    snapshot = frame["reply"]["snapshot"]
    return probe.native_envelope(snapshot, request_id), frame, process


def gated_eof(f4, owner_root, request_id, first=False):
    envelope, owner_before, owner_before_process = refresh_envelope(owner_root, request_id)
    journal_before = probe.native.blob(f4.journal)
    witness_before = f4.witness_call("/status")
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(f4.submit, envelope)
        gate_line = f4.sink.read(timeout=15)
        gate = json.loads(gate_line)
        if gate.get("event") != "GATE" or gate.get("stage") != "guarded":
            raise RuntimeError("expected actual NativeAdmission guarded gate: " + probe.canonical(gate))
        owner_at_gate, owner_gate_process = owner_read(owner_root)
        journal_at_gate = probe.native.blob(f4.journal)
        witness_at_gate = f4.witness_call("/status")
        # EOF is the real inherited admission gate behavior, not a synthesized exception.
        f4.sink.p.stdin.close()
        response = future.result(timeout=15)
    owner_after, owner_after_process = owner_read(owner_root)
    journal_after = probe.native.blob(f4.journal)
    witness_after = f4.witness_call("/status")
    return {
        "request_id": request_id, "envelope": envelope,
        "owner_before": owner_before, "owner_before_process": owner_before_process,
        "journal_before": journal_before, "witness_before": witness_before,
        "gate": gate, "owner_at_gate": owner_at_gate,
        "owner_gate_process": owner_gate_process,
        "journal_at_gate": journal_at_gate, "witness_at_gate": witness_at_gate,
        "response": response,
        "owner_after": owner_after, "owner_after_process": owner_after_process,
        "journal_after": journal_after, "witness_after": witness_after,
        "sink_process": f4.sink.meta,
    }


def cli(script, owner_root, request_id):
    argv = [sys.executable, "-B", str(script), str(owner_root), request_id]
    started = time.monotonic_ns()
    result = subprocess.run(argv, capture_output=True, text=True, timeout=30, check=False)
    frame = None
    try:
        frame = json.loads(result.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        pass
    return {"argv": argv, "start_ns": started, "end_ns": time.monotonic_ns(),
            "returncode": result.returncode, "stdout": result.stdout,
            "stderr": result.stderr, "frame": frame}


def fixture(out, label, gate=True):
    case_root = out / "state" / label
    case_root.mkdir(parents=True)
    prepared = probe.setup_native_f3(case_root / "native", world="A", activate=True)
    owner_root = Path(prepared["owner_root"])
    ready_snapshot = prepared["owner_ready"]["snapshot"]
    witness_root = ready_snapshot["state"]["native_owner"]["domain_id"]
    f4 = probe.NativeF4(case_root / "f4", owner_root, witness_root,
                        gate="guarded" if gate else None)
    return {"prepared": prepared, "owner_root": owner_root, "witness_root": witness_root,
            "f4": f4}


def readback(fx, ids):
    owner, owner_process = owner_read(fx["owner_root"])
    f1 = probe.f1_raw(Path(fx["prepared"]["f1_root"]) / "store.sqlite")
    journal = probe.native.blob(fx["f4"].journal)
    witness = fx["f4"].witness_call("/status")
    effects = owner_effects(owner)
    return {"owner": owner, "owner_process": owner_process, "effects": {i: effects.get(i) for i in ids},
            "owner_tree": probe.tree(fx["owner_root"]), "f1": f1,
            "journal": journal, "witness": witness,
            "f4_status": fx["f4"].snapshot(),
            "sink_process": fx["f4"].sink.meta, "witness_process": fx["f4"].witness.meta}


def run_two_guarded_eof(out):
    fx = fixture(out, "two-guarded-eof")
    ids = [fx["witness_root"] + ":guarded-eof-A", fx["witness_root"] + ":guarded-eof-B"]
    case = {"setup": fx["prepared"], "witness_root": fx["witness_root"],
            "lifecycle": fx["f4"].lifecycle_calls, "witness_init": fx["f4"].witness_init,
            "events": []}
    try:
        case["events"].append(gated_eof(fx["f4"], fx["owner_root"], ids[0], first=True))
        case["events"].append(gated_eof(fx["f4"], fx["owner_root"], ids[1]))
        # The live sink owns the existing writer guard for its lifetime.
        # Stop that actual process before exercising the recovery CLIs.
        case["sink_stopped_before_refusal_commands"] = fx["f4"].sink.close(True)
        case["before_refusal_commands"] = readback(fx, ids)
        case["strict_reconcile_A"] = cli(RECONCILE, fx["owner_root"], ids[0])
        case["observe_local_A"] = cli(OBSERVE, fx["owner_root"], ids[0])
        case["after_refusal_commands"] = readback(fx, ids)
        owner = probe.OwnerProcess(fx["owner_root"])
        case["seal_while_pending"] = owner.call({"op": "seal"})
        case["dispose_child_while_pending"] = owner.call({"op": "dispose_child", "unit": "D"})
        case["after_disposition_attempts"] = owner.call({"op": "read"})
        owner.close()
        case["owner_process_after_disposition"] = owner.meta
        case["final"] = readback(fx, ids)
        case["status"] = "CAPTURED"
    finally:
        fx["f4"].close(True)
    return case


def run_normal_b_after_unknown(out):
    fx = fixture(out, "normal-B-after-A-unknown")
    aid = fx["witness_root"] + ":unknown-A"
    bid = fx["witness_root"] + ":normal-B"
    case = {"setup": fx["prepared"], "witness_root": fx["witness_root"],
            "lifecycle": fx["f4"].lifecycle_calls, "witness_init": fx["f4"].witness_init}
    try:
        case["unknown_A"] = gated_eof(fx["f4"], fx["owner_root"], aid, first=True)
        # Existing actual cold restart clears only the test gate and replays the actual empty journal.
        case["old_sink_stopped_before_cold_restart"] = fx["f4"].sink.close(True)
        case["cold_ready"] = fx["f4"].cold_restart()
        case["reopen"] = [fx["f4"].call("/replace", {"holder": "pending-admission-baseline"}),
                          fx["f4"].call("/activate", {"authority_version": 2})]
        envelope, before_owner, owner_process = refresh_envelope(fx["owner_root"], bid)
        case["fresh_B_envelope"] = envelope
        case["owner_before_B"] = before_owner
        case["owner_before_B_process"] = owner_process
        case["journal_before_B"] = probe.native.blob(fx["f4"].journal)
        case["witness_before_B"] = fx["f4"].witness_call("/status")
        case["normal_B"] = fx["f4"].submit(envelope, authority_version=2)
        case["after_B"] = readback(fx, [aid, bid])
        case["status"] = "CAPTURED"
    finally:
        fx["f4"].close(True)
    return case


def main(argv):
    if len(argv) != 2:
        raise SystemExit("usage: baseline_probe.py OUTPUT_DIRECTORY")
    out = Path(argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=False)
    raw = {"schema": "ases4-native-pending-admission-baseline-v1",
           "status": "RUNNING", "started_ns": time.monotonic_ns(),
           "source_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                                             capture_output=True, text=True, check=True).stdout.strip(),
           "source_hashes": source_hashes(), "python": sys.version,
           "platform": {key: getattr(os.uname(), key) for key in
                        ("sysname", "nodename", "release", "version", "machine")},
           "cases": {}}
    try:
        raw["cases"]["two_guarded_eof"] = run_two_guarded_eof(out)
        raw["cases"]["normal_B_after_unknown"] = run_normal_b_after_unknown(out)
        raw["status"] = "CAPTURED"
    except BaseException as error:
        raw["status"] = "PROBE_FAILED"
        raw["failure"] = {"type": type(error).__name__, "message": str(error),
                          "traceback": traceback.format_exc()}
    raw["finished_ns"] = time.monotonic_ns()
    (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": raw["status"], "raw": str(out / "raw.json")}, sort_keys=True))
    return 0 if raw["status"] == "CAPTURED" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
