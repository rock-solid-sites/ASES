#!/usr/bin/env python3
"""Actual native F4 pending-publication reconciliation histories."""
from __future__ import annotations

import argparse
import concurrent.futures
import importlib.util
import json
import os
from pathlib import Path
import select
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BASE_PATH = REPO / "docs/research/phase-ii-native-ownership/probe.py"
RECONCILE = HERE / "reconcile.py"
PROCESSES = []


def load_base():
    spec = importlib.util.spec_from_file_location("native_publication_base", BASE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


base = load_base()
native = base.native


def sha(raw: bytes) -> str:
    return base.sha(raw)


def canonical(value) -> str:
    return base.canonical(value)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def source_manifest() -> dict:
    files = {
        "f1_repaired": base.REPAIRED_F1,
        "native_owner": base.HERE / "native_owner.py",
        "owner_cli": base.OWNER_CLI,
        "native_f4_sink": base.NATIVE_SINK,
        "unix_transport": base.UNIX_TRANSPORT,
        "reconcile": RECONCILE,
        "f4_cut_witness": REPO / "docs/research/phase-i-sol-integration/evidence/sources/receipt/research/phase-i-t18-sink-order-20261103/published-cut/cut_sink.py",
        "l5_core": base.L5 / "l5_integrated.py",
        "l6_store": base.L6 / "store.py",
    }
    return {key: {"path": str(path), "sha256": sha(path.read_bytes())}
            for key, path in files.items() if path.is_file()}


def prepare(out: Path, label: str, gate="after-append"):
    root = out / "state" / label
    setup = base.setup_native_f3(root, world="A", activate=True)
    owner_root = Path(setup["owner_root"])
    owner_snapshot = setup["owner_ready"]["snapshot"]
    witness_root = owner_snapshot["state"]["native_owner"]["domain_id"]
    f4 = base.NativeF4(root / "f4", owner_root, witness_root, gate=gate)
    owner_reader = base.OwnerProcess(owner_root)
    snapshot = owner_reader.call({"op": "read"})["reply"]["snapshot"]
    owner_reader.close()
    request_id = witness_root + ":publication-reconcile-" + label
    envelope = base.native_envelope(snapshot, request_id)
    return {"root": root, "setup": setup, "owner_root": owner_root,
            "witness_root": witness_root, "f4": f4, "snapshot": snapshot,
            "request_id": request_id, "envelope": envelope}


def append_eof(case: dict):
    f4 = case["f4"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        pending = pool.submit(f4.submit, case["envelope"])
        line = f4.sink.read(timeout=15)
        gate = json.loads(line)
        if gate.get("event") != "GATE" or gate.get("stage") != "after-append":
            raise RuntimeError("expected actual after-append gate: " + canonical(gate))
        owner = base.OwnerProcess(case["owner_root"])
        owner_local = owner.snapshot()
        owner.close()
        f4.sink.p.stdin.close()
        error_reply = pending.result(timeout=15)
    # The actual sink process still owns sink-writer.lock after returning the
    # EOF failure. The privileged command must refuse before inspecting the
    # witness or changing any durable store.
    _busy_proc, busy = run_reconcile(case["owner_root"], case["request_id"])
    dead = f4.sink.close(True)
    return {"gate": gate, "owner_local": owner_local, "error_reply": error_reply,
            "busy_guard_reconcile": busy, "dead_sink": dead,
            "journal_after_eof": native.blob(f4.journal),
            "witness_after_eof": f4.witness_call("/status")}


def run_reconcile(owner_root: Path, request_id: str, gate=False, timeout=20):
    argv = [sys.executable, "-B", str(RECONCILE), str(owner_root), request_id]
    if gate:
        argv += ["--test-gate", "after-confirmed-publication-before-settlement"]
    meta = {"argv": argv, "start_ns": time.monotonic_ns()}
    proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, bufsize=0)
    meta["pid"] = proc.pid
    PROCESSES.append(meta)
    first = select.select([proc.stdout], [], [], timeout)[0]
    if not first:
        proc.kill(); meta["exit"] = proc.wait(timeout=5)
        meta["stderr"] = proc.stderr.read().decode(errors="replace")
        raise TimeoutError("reconciler produced no frame")
    raw1 = proc.stdout.readline(4 * 1024 * 1024).decode(errors="replace")
    try: value1 = json.loads(raw1)
    except json.JSONDecodeError: value1 = None
    meta["frames"] = [{"ns": time.monotonic_ns(), "raw": raw1, "value": value1}]
    if gate and isinstance(value1, dict) and value1.get("event") == "GATE":
        meta["gate"] = value1
        return proc, meta
    meta["result"] = value1
    meta["exit"] = proc.wait(timeout=timeout)
    meta["stderr"] = proc.stderr.read().decode(errors="replace")
    meta["exit_ns"] = time.monotonic_ns()
    return None, meta


def finish_reconciler(proc, meta, kill=False):
    if proc.poll() is None:
        if kill:
            proc.kill()
        else:
            proc.stdin.write(b"continue\n"); proc.stdin.flush()
    if not kill and select.select([proc.stdout], [], [], 10)[0]:
        raw = proc.stdout.readline(4 * 1024 * 1024).decode(errors="replace")
        try: value = json.loads(raw)
        except json.JSONDecodeError: value = None
        meta.setdefault("frames", []).append({"ns": time.monotonic_ns(), "raw": raw, "value": value})
        meta["result"] = value
    meta["exit"] = proc.wait(timeout=15)
    meta["exit_ns"] = time.monotonic_ns()
    meta["stderr"] = proc.stderr.read().decode(errors="replace")
    return meta


def snapshot(case):
    f4 = case["f4"]
    owner = base.OwnerProcess(case["owner_root"])
    owner_view = owner.snapshot()
    owner.close()
    return {"journal": native.blob(f4.journal), "owner_tree": base.tree(case["owner_root"]),
            "owner_view": owner_view,
            "witness": f4.witness_call("/status"), "f4_tree": base.tree(f4.root)}


def primary_history(out: Path):
    case = prepare(out, "primary")
    eof = append_eof(case)
    f4 = case["f4"]
    before = {"journal": native.blob(f4.journal), "owner_tree": base.tree(case["owner_root"]),
              "witness": f4.witness_call("/status")}
    cold_ready = f4.cold_restart()
    cold_process = f4.sink.close(True)
    cold_snapshot = f4.snapshot()
    owner = base.OwnerProcess(case["owner_root"])
    local_owner_snapshot = owner.call({"op": "read"})["reply"]["snapshot"]
    registrations = [r["id"] for r in
                     local_owner_snapshot["state"]["native_owner"]["registrations"]]
    seal_before_disposition = owner.call({"op": "seal"})
    pending_disposition = {"child": owner.call({"op": "dispose_child", "unit": "D"}),
                           "content": [owner.call({"op": "dispose_content", "id": rid})
                                       for rid in registrations]}
    before_reconcile_owner = owner.call({"op": "read"})["reply"]["snapshot"]
    owner.close()
    reconcile_proc, reconcile = run_reconcile(case["owner_root"], case["request_id"])
    if reconcile_proc:
        raise RuntimeError("normal reconciliation unexpectedly stopped at test gate")
    before_idempotent = {"journal": native.blob(f4.journal),
                         "owner_tree": base.tree(case["owner_root"]),
                         "witness": f4.witness_call("/status")}
    second_proc, second_reconcile = run_reconcile(case["owner_root"], case["request_id"])
    if second_proc:
        raise RuntimeError("idempotent replay unexpectedly stopped at test gate")
    idempotent_state = {"journal": native.blob(f4.journal),
                        "owner_tree": base.tree(case["owner_root"]),
                        "witness": f4.witness_call("/status")}
    # Preserve a proof of ordinary cold startup after settlement. This path
    # starts sealed and must not issue another publication.
    cold_after = f4.cold_restart()
    recovered_sink_ready = cold_after
    exact_retry = f4.submit(case["envelope"])
    after_retry = f4.snapshot()
    owner = base.OwnerProcess(case["owner_root"])
    transitions = {"seal": owner.call({"op": "seal"}),
                   "move": owner.call({"op": "move"}),
                   "activate": owner.call({"op": "activate"})}
    moved = owner.call({"op": "read"})["reply"]["snapshot"]
    new_envelope = base.native_envelope(moved, case["witness_root"] + ":fresh-after-seal-move")
    denied_new_id = f4.submit(new_envelope, authority_version=2)
    transitions["seal_for_disposition"] = owner.call({"op": "seal"})
    transitions["dispose_child"] = owner.call({"op": "dispose_child", "unit": "D"})
    transitions["dispose_content"] = [owner.call({"op": "dispose_content", "id": rid})
                                       for rid in registrations]
    owner_after_disposition = owner.call({"op": "read"})["reply"]["snapshot"]
    owner.close()
    owner_final_reader = base.OwnerProcess(case["owner_root"])
    owner_final = owner_final_reader.snapshot()
    owner_final_reader.close()
    f1_before = base.f1_raw(Path(case["setup"]["f1_root"]) / "store.sqlite")
    result = {"setup": case["setup"], "request_id": case["request_id"],
            "envelope": case["envelope"], "f4_lifecycle": f4.lifecycle_calls,
            "witness_init": f4.witness_init, "append_eof": eof,
            "cold_refusal_ready": cold_ready, "cold_refusal_process": cold_process,
            "state_after_cold_refusal": cold_snapshot, "before_reconcile": before,
            "owner_before_reconcile": before_reconcile_owner,
            "seal_before_pending_disposition": seal_before_disposition,
            "pending_disposition": pending_disposition,
            "reconcile": reconcile, "idempotent_reconcile": second_reconcile,
            "before_idempotent": before_idempotent,
            "idempotent_state": idempotent_state,
            "cold_ready_after_reconcile": recovered_sink_ready,
            "exact_historical_retry": exact_retry, "after_exact_retry": after_retry,
            "source_transitions": transitions, "fresh_id_after_move": new_envelope,
            "fresh_id_denial": denied_new_id,
            "owner_after_disposition": owner_after_disposition,
            "f1_before": f1_before, "owner_final": owner_final,
            "f4_final": f4.snapshot(), "f4_tree": base.tree(f4.root),
            "owner_tree": base.tree(case["owner_root"]),
            "f1_after": base.f1_raw(Path(case["setup"]["f1_root"]) / "store.sqlite")}
    f4.close(True)
    return result


def validate_primary(result):
    request_id = result["request_id"]
    append = result["append_eof"]
    need(append["gate"].get("event") == "GATE" and append["gate"].get("stage") == "after-append",
         "actual after-append EOF gate was not captured")
    need(append["busy_guard_reconcile"].get("result", {}).get("status") == "refused-writer-guard-busy",
         "live native sink did not exclude reconciliation")
    cold_refusal = result["cold_refusal_ready"]
    need(cold_refusal.get("ready") is False and cold_refusal.get("reason") == "published-cut-unavailable"
         and cold_refusal.get("local_parse_complete") is True,
         "ordinary cold startup did not retain the real pending-publication refusal")
    reconciliation = result["reconcile"].get("result", {})
    need(reconciliation.get("status") == "published" and reconciliation.get("cas_count") == 1,
         "exact pending effect did not reconcile through one publication CAS")
    protocol = reconciliation.get("protocol", [])
    need([entry.get("path") for entry in protocol] == ["/check", "/publish", "/check", "/check"]
         and len({entry.get("request", {}).get("nonce") for entry in protocol}) == 4,
         "reconciliation did not use one fresh observation, one CAS, confirmation and settlement proof")
    replay = result["idempotent_reconcile"].get("result", {})
    need(replay.get("status") == "published" and replay.get("cas_count") == 0
         and [entry.get("path") for entry in replay.get("protocol", [])] == ["/check", "/check", "/check"],
         "published replay did not prove the full matching cut without another CAS")
    need(result["idempotent_state"]["journal"]["sha256"] ==
         result["before_reconcile"]["journal"]["sha256"],
         "idempotent reconciliation appended or changed journal bytes")
    need(result["idempotent_state"]["owner_tree"] == result["before_idempotent"]["owner_tree"],
         "published replay changed the selected native owner records")
    need(result["cold_ready_after_reconcile"].get("ready") is True,
         "ordinary cold startup did not accept the now-matching historical cut")
    need(result["exact_historical_retry"].get("response", {}).get("status") == 200
         and result["exact_historical_retry"]["response"]["body"].get("outcome") == "already-accepted",
         "exact historical ID did not return the existing event after source move")
    need(result["exact_historical_retry"]["before"]["sha256"] ==
         result["exact_historical_retry"]["after"]["sha256"] ==
         result["before_reconcile"]["journal"]["sha256"],
         "reconciliation or exact historical retry changed journal bytes")
    need(result["owner_after_disposition"]["state"]["native_owner"]["effects"][request_id]["status"] == "published",
         "owner effect did not settle to published")
    need(all(item.get("reply", {}).get("result") == "DENY"
             and item.get("reply", {}).get("reason") in
             {"pending-in-domain-effect", "native-dependent-or-effect-remains"}
             for item in (result["pending_disposition"]["child"], *result["pending_disposition"]["content"])),
         "pending native effect failed to block disposal before settlement")
    need(result["fresh_id_denial"].get("response", {}).get("status") == 409
         and result["fresh_id_denial"]["response"]["body"].get("reason") == "native-current-path-denied",
         "new ID after source move was not denied by current native authority")
    disposed = result["source_transitions"]["dispose_content"]
    need(result["source_transitions"]["dispose_child"].get("reply", {}).get("result") == "COMMITTED"
         and all(item.get("reply", {}).get("result") == "COMMITTED" for item in disposed),
         "normal native disposition did not complete after owner settlement")
    need(result["f1_before"]["integrity"] == result["f1_after"]["integrity"] == "ok"
         and result["f1_before"]["retained"] == result["f1_after"]["retained"],
         "F1 observations changed during native reconciliation/disposition")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"refusing nonempty evidence directory: {out}")
    out.mkdir(parents=True, exist_ok=True)
    raw = {"schema": "ases4-native-publication-reconcile-v1", "started_ns": time.monotonic_ns(),
           "sources": source_manifest(), "cases": {}, "processes": PROCESSES}
    try:
        raw["cases"]["primary"] = primary_history(out)
        validate_primary(raw["cases"]["primary"])
        raw["status"] = "PASS"
    except BaseException as error:
        raw["failure"] = {"type": type(error).__name__, "message": str(error),
                          "traceback": traceback.format_exc()}
        raw["status"] = "PROBE_FAILED"
        raw["processes"] = PROCESSES
        (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
        raise
    raw["finished_ns"] = time.monotonic_ns()
    (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": raw["status"], "raw": str(out / "raw.json")}, sort_keys=True))


if __name__ == "__main__":
    main()
