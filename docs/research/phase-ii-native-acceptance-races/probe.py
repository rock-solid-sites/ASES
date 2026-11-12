#!/usr/bin/env python3
"""Bounded native F3 acceptance and overlapping F1 producer histories."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OWNERSHIP = REPO / "docs/research/phase-ii-native-ownership/probe.py"
spec = importlib.util.spec_from_file_location("native_ownership_acceptance_helpers", OWNERSHIP)
helpers = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = helpers
spec.loader.exec_module(helpers)
repair = helpers.repair
CONTENT = helpers.CONTENT


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sqlite_snapshot(path: Path, queries: dict[str, str]) -> dict:
    """Consistent SQLite read snapshot and serialized database image."""
    uri = path.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True, timeout=2) as source:
        source.execute("BEGIN")
        rows = {name: source.execute(sql).fetchall() for name, sql in queries.items()}
        integrity = source.execute("PRAGMA integrity_check").fetchone()[0]
        target = sqlite3.connect(":memory:")
        source.backup(target)
        image = target.serialize()
        target.close()
        source.rollback()
    return {"path": str(path), "queries": rows, "integrity_check": integrity,
            "snapshot_raw_hex": image.hex(), "snapshot_size": len(image),
            "snapshot_sha256": sha(image)}


def direct_owner_snapshot(owner_root: Path, f1_path: Path) -> dict:
    """Selected CURRENT, F1 and L6 direct reads; no owner read process required."""
    protected = owner_root / "protected"
    current_raw = (protected / "CURRENT").read_bytes()
    selector = current_raw.decode().strip()
    record_raw = (protected / selector).read_bytes()
    state = json.loads(record_raw)
    f1 = sqlite_snapshot(f1_path, {
        "kernel": "SELECT id,root,profile,version,view FROM kernel ORDER BY id",
        "selected": "SELECT id,record FROM consumer_observations ORDER BY id",
        "retained": "SELECT record FROM retained_observations ORDER BY record",
    })
    l6 = sqlite_snapshot(protected / "catalog.sqlite", {
        "unit": "SELECT live,sealed FROM unit",
        "dependencies": "SELECT name,kind,sha256,size,disposed FROM dependencies ORDER BY name",
    })
    files = {}
    objects = protected / "objects"
    if objects.exists():
        for path in sorted(objects.iterdir()):
            raw = path.read_bytes()
            files[path.name] = {"raw_hex": raw.hex(), "sha256": sha(raw),
                                "size": len(raw), "inode": path.stat().st_ino,
                                "mode": path.stat().st_mode & 0o777}
    return {"observed_ns": time.monotonic_ns(), "current_raw_hex": current_raw.hex(),
            "selector": selector, "record_raw_hex": record_raw.hex(),
            "record_sha256": sha(record_raw), "state": state,
            "native_owner": state["native_owner"], "current_ingress": state["current_ingress"],
            "record_files": helpers.tree(protected), "f1_sqlite": f1,
            "l6_sqlite": l6, "l6_files": files}


def f1_snapshot(path: Path) -> dict:
    raw = helpers.f1_raw(path)
    raw["sqlite"] = sqlite_snapshot(path, {
        "kernel": "SELECT id,root,profile,version,view FROM kernel ORDER BY id",
        "selected": "SELECT id,record FROM consumer_observations ORDER BY id",
        "retained": "SELECT record FROM retained_observations ORDER BY record",
    })
    raw["observed_ns"] = time.monotonic_ns()
    return raw


def f4_journal(f4) -> dict:
    raw = f4.journal.read_bytes()
    events = [json.loads(line) for line in raw.splitlines() if line]
    return {"path": str(f4.journal), "raw_hex": raw.hex(), "sha256": sha(raw),
            "size": len(raw), "events": events}


def pair_bundle(world: str) -> dict:
    if world in repair.WORLDS:
        return repair.configuration(world, CONTENT, True)["acceptance_bundle"]
    return {"accepted_content": CONTENT,
            "required": {field: f"{world}:{field}" for field in repair.FIELDS}}


def setup_a_world(case_root: Path) -> dict:
    """Create an actual F1 world A and native A registration, then activate D."""
    f1_root, owner_root = case_root / "f1", case_root / "owner"
    boot = helpers.setup_f1(f1_root)
    before_a = f1_snapshot(f1_root / "store.sqlite")
    establish = helpers.establish_owner(owner_root, f1_root / "store.sqlite")
    f1_a = helpers.native_f1_accept(f1_root, pair_bundle("A"), CONTENT)
    after_f1_a = f1_snapshot(f1_root / "store.sqlite")
    owner = helpers.OwnerProcess(owner_root)
    accepted_a = owner.call({"op": "accept"})
    activated_a = owner.call({"op": "activate"})
    selected_a = owner.call({"op": "read"})["reply"]["snapshot"]
    process = owner.close()
    return {"f1_setup": boot, "f1_before_a": before_a, "establish": establish,
            "f1_accept_a": f1_a, "f1_after_a": after_f1_a,
            "owner_accept_a": accepted_a, "owner_activate_a": activated_a,
            "owner_selected_a": selected_a, "owner_process_a": process,
            "owner_root": str(owner_root), "f1_root": str(f1_root)}


def prepare_c_world(case_root: Path) -> tuple[dict, dict]:
    setup = setup_a_world(case_root)
    owner_root, f1_root = Path(setup["owner_root"]), Path(setup["f1_root"])
    sealer = helpers.OwnerProcess(owner_root)
    setup["seal_before_c"] = sealer.call({"op": "seal"})
    setup["owner_after_seal_a"] = direct_owner_snapshot(owner_root, f1_root / "store.sqlite")
    setup["owner_seal_process"] = sealer.close()
    setup["f1_accept_c"] = helpers.native_f1_accept(f1_root, pair_bundle("C"), CONTENT)
    setup["f1_after_c"] = f1_snapshot(f1_root / "store.sqlite")
    setup["owner_before_c_accept"] = direct_owner_snapshot(owner_root, f1_root / "store.sqlite")
    return setup, {"owner_root": owner_root, "f1_root": f1_root,
                   "f1_path": f1_root / "store.sqlite"}


def duplicate_acceptance(out: Path) -> dict:
    root = out / "state" / "duplicate-acceptance"
    setup, paths = prepare_c_world(root)
    before = direct_owner_snapshot(paths["owner_root"], paths["f1_path"])
    initiator = helpers.OwnerProcess(paths["owner_root"])
    contender = helpers.OwnerProcess(paths["owner_root"])
    started_ns = time.monotonic_ns()
    gate = initiator.call({"op": "accept", "gate": "material-prepared"})
    gate_ns = time.monotonic_ns()
    if gate.get("event") != "GATE" or gate.get("phase", gate.get("stage")) != "material-prepared":
        raise RuntimeError(f"native C acceptance did not reach material-prepared: {gate!r}")
    at_gate = direct_owner_snapshot(paths["owner_root"], paths["f1_path"])
    contender_before = direct_owner_snapshot(paths["owner_root"], paths["f1_path"])
    contender_started_ns = time.monotonic_ns()
    refused = contender.call({"op": "accept"})
    contender_finished_ns = time.monotonic_ns()
    after_contender = direct_owner_snapshot(paths["owner_root"], paths["f1_path"])
    f1_at_gate = f1_snapshot(paths["f1_path"])
    release_ns = time.monotonic_ns()
    committed = initiator.resume()
    commit_ns = time.monotonic_ns()
    initiator_process = initiator.close()
    after_first = direct_owner_snapshot(paths["owner_root"], paths["f1_path"])
    f1_after_first = f1_snapshot(paths["f1_path"])
    before_duplicate = direct_owner_snapshot(paths["owner_root"], paths["f1_path"])
    duplicate_started_ns = time.monotonic_ns()
    duplicate = contender.call({"op": "accept"})
    duplicate_finished_ns = time.monotonic_ns()
    after_duplicate = direct_owner_snapshot(paths["owner_root"], paths["f1_path"])
    f1_after_duplicate = f1_snapshot(paths["f1_path"])
    contender_process = contender.close()
    return {"label": "duplicate-acceptance", "setup": setup,
            "owner_before_guard": before, "initiator_process_before_gate": gate,
            "initiator_gate": gate, "gate_ns": gate_ns, "initiator_started_ns": started_ns,
            "owner_at_gate": at_gate, "contender_before_request": contender_before,
            "contender_request": {"op": "accept", "started_ns": contender_started_ns,
                                  "finished_ns": contender_finished_ns},
            "contender_reply": refused, "owner_after_contender": after_contender,
            "f1_at_gate": f1_at_gate, "release_ns": release_ns,
            "first_accept_reply": committed, "first_accept_commit_ns": commit_ns,
            "initiator_process": initiator_process, "owner_after_first_accept": after_first,
            "f1_after_first_accept": f1_after_first,
            "owner_before_duplicate_retry": before_duplicate,
            "duplicate_retry_request": {"op": "accept", "started_ns": duplicate_started_ns,
                                        "finished_ns": duplicate_finished_ns},
            "duplicate_retry_reply": duplicate,
            "owner_after_duplicate_retry": after_duplicate,
            "f1_after_duplicate_retry": f1_after_duplicate,
            "contender_process": contender_process}


def producer_overlap(out: Path) -> dict:
    root = out / "state" / "producer-overlap"
    setup, paths = prepare_c_world(root)
    owner_root, f1_root, f1_path = paths["owner_root"], paths["f1_root"], paths["f1_path"]
    before = direct_owner_snapshot(owner_root, f1_path)
    initiator = helpers.OwnerProcess(owner_root)
    # Start the real F1 producer service before the owner gate so process
    # startup cannot masquerade as a request overlapping the held guards.
    producer_holder = repair.Holder(helpers.REPAIRED_F1, f1_root,
                                    {"acceptance_bundle": pair_bundle("D")})
    gate_started_ns = time.monotonic_ns()
    gate = initiator.call({"op": "accept", "gate": "material-prepared"})
    gate_ns = time.monotonic_ns()
    if gate.get("event") != "GATE" or gate.get("phase", gate.get("stage")) != "material-prepared":
        raise RuntimeError(f"producer overlap C acceptance did not reach gate: {gate!r}")
    owner_at_gate = direct_owner_snapshot(owner_root, f1_path)
    f1_before_producer = f1_snapshot(f1_path)
    operation = {"request": "actual-f1-accept-world-D", "content_bytes_equal": True,
                 "requested_bundle": pair_bundle("D"), "gate_ns": gate_ns,
                 "producer_process_ready_ns": producer_holder.meta.get("ready_ns"),
                 "producer_process": producer_holder.meta}

    def update_f1_d():
        started = time.monotonic_ns()
        try:
            response = producer_holder.call("accept", CONTENT)
            process = producer_holder.close()
            return {"started_ns": started, "finished_ns": time.monotonic_ns(),
                    "result": {"response": response,
                               "operation": producer_holder.meta["operations"][-1],
                               "process": process}, "error": None}
        except BaseException as error:
            try:
                process = producer_holder.close()
            except BaseException:
                process = producer_holder.meta
            return {"started_ns": started, "finished_ns": time.monotonic_ns(),
                    "result": None, "error": {"type": type(error).__name__, "message": str(error),
                                                "traceback": traceback.format_exc(),
                                                "process": process}}

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    producer_future = executor.submit(update_f1_d)
    # Give the real producer call a short bounded chance to return while the
    # F1/L6 owner guards remain held, exposing either its busy response or a
    # request that is still pending at release.
    concurrent.futures.wait([producer_future], timeout=0.25)
    f1_at_gate_before_release = f1_snapshot(f1_path)
    owner_at_gate_after_request = direct_owner_snapshot(owner_root, f1_path)
    # Record actual completion state immediately before releasing the first
    # owner; snapshots above are taken while the real F1/L6 guards remain held.
    observed_complete = producer_future.done()
    observation_ns = time.monotonic_ns()
    release_ns = time.monotonic_ns()
    operation.update({"observed_complete_before_release": observed_complete,
                      "observation_ns": observation_ns, "release_ns": release_ns,
                      "disposition_at_release": "completed" if observed_complete else "pending"})
    committed_c = initiator.resume()
    commit_ns = time.monotonic_ns()
    initiator_process = initiator.close()
    producer_first = producer_future.result(timeout=10)
    executor.shutdown(wait=True)
    operation["first_attempt"] = producer_first
    operation["response_ns"] = producer_first.get("finished_ns")
    if producer_first.get("error"):
        operation["observed_outcome"] = "producer-error"
    elif producer_first["finished_ns"] > release_ns and not observed_complete:
        operation["observed_outcome"] = "pending-at-release-committed-after-release"
    elif producer_first["finished_ns"] <= release_ns:
        operation["observed_outcome"] = "completed-before-release"
    else:
        operation["observed_outcome"] = "completed-after-release"
    after_c_accept = direct_owner_snapshot(owner_root, f1_path)
    f1_after_first_attempt = f1_snapshot(f1_path)
    retry = None
    d_required = pair_bundle("D")["required"]
    selected_required = (f1_after_first_attempt.get("selected") or {}).get("required")
    if producer_first.get("error") or selected_required != d_required:
        retry_started_ns = time.monotonic_ns()
        retry = helpers.native_f1_accept(f1_root, pair_bundle("D"), CONTENT)
        operation["retry"] = {"started_ns": retry_started_ns, "finished_ns": time.monotonic_ns(),
                               "result": retry}
    f1_after_producer = f1_snapshot(f1_path)
    owner_after_producer = direct_owner_snapshot(owner_root, f1_path)

    # The selected F3 identity remains C while actual F1 now selects D.
    activate_d_path = helpers.OwnerProcess(owner_root)
    activation = activate_d_path.call({"op": "activate"})
    selected_c_active = activate_d_path.call({"op": "read"})["reply"]["snapshot"]
    activate_process = activate_d_path.close()
    f4_root = root / "f4"
    witness_root = "native-acceptance-races-producer-overlap-" + str(time.monotonic_ns())
    f4 = helpers.NativeF4(f4_root, owner_root, witness_root)
    current_c_owner = helpers.OwnerProcess(owner_root)
    current_c_snapshot = current_c_owner.call({"op": "read"})["reply"]["snapshot"]
    c_envelope = helpers.native_envelope(current_c_snapshot, witness_root + ":c-world-mismatch")
    c_before = direct_owner_snapshot(owner_root, f1_path)
    f1_before_c_denial = f1_snapshot(f1_path)
    journal_before_c_denial = f4_journal(f4)
    c_denied = f4.submit(c_envelope, authority_version=1)
    c_after = direct_owner_snapshot(owner_root, f1_path)
    f1_after_c_denial = f1_snapshot(f1_path)
    journal_after_c_denial = f4_journal(f4)
    current_c_owner.close()

    owner_d = helpers.OwnerProcess(owner_root)
    seal_before_d = owner_d.call({"op": "seal"})
    after_seal_c = direct_owner_snapshot(owner_root, f1_path)
    f1_before_owner_d = f1_snapshot(f1_path)
    accept_d = owner_d.call({"op": "accept"})
    after_accept_d = direct_owner_snapshot(owner_root, f1_path)
    f1_after_owner_d = f1_snapshot(f1_path)
    activate_d = owner_d.call({"op": "activate"})
    d_snapshot = owner_d.call({"op": "read"})["reply"]["snapshot"]
    d_envelope = helpers.native_envelope(d_snapshot, witness_root + ":d-world-authorized")
    before_d_effect = direct_owner_snapshot(owner_root, f1_path)
    f1_before_d_effect = f1_snapshot(f1_path)
    journal_before_d_effect = f4_journal(f4)
    d_effect = f4.submit(d_envelope, authority_version=1)
    after_d_effect = direct_owner_snapshot(owner_root, f1_path)
    f1_after_d_effect = f1_snapshot(f1_path)
    journal_after_d_effect = f4_journal(f4)
    owner_d_process = owner_d.close()

    result = {"label": "producer-overlap", "setup": setup,
              "owner_before_guard": before, "owner_gate_request_started_ns": gate_started_ns,
              "initiator_gate": gate, "gate_ns": gate_ns, "owner_at_gate": owner_at_gate,
              "owner_at_gate_after_producer_request": owner_at_gate_after_request,
              "f1_before_producer": f1_before_producer,
              "f1_at_gate_before_release": f1_at_gate_before_release,
              "producer_operation": operation, "release_ns": release_ns,
              "first_c_accept_reply": committed_c, "first_c_accept_commit_ns": commit_ns,
              "initiator_process": initiator_process,
              "owner_after_c_accept": after_c_accept,
              "f1_after_first_producer_attempt": f1_after_first_attempt,
              "producer_retry": retry, "f1_after_producer": f1_after_producer,
              "owner_after_producer": owner_after_producer,
              "activate_c_path_reply": activation, "selected_c_active_snapshot": selected_c_active,
              "activate_c_path_process": activate_process,
              "f4_lifecycle": f4.lifecycle_calls, "witness_init": f4.witness_init,
              "f4_config": f4.config, "c_envelope": c_envelope,
              "owner_before_c_mismatch": c_before, "f1_before_c_mismatch": f1_before_c_denial,
              "journal_before_c_mismatch": journal_before_c_denial,
              "c_mismatch_request": c_denied,
              "owner_after_c_mismatch": c_after, "f1_after_c_mismatch": f1_after_c_denial,
              "journal_after_c_mismatch": journal_after_c_denial,
              "seal_c_before_d": seal_before_d, "owner_after_seal_c": after_seal_c,
              "f1_before_d_accept": f1_before_owner_d,
              "accept_d_reply": accept_d, "owner_after_d_accept": after_accept_d,
              "f1_after_d_accept": f1_after_owner_d,
              "activate_d_reply": activate_d, "d_envelope": d_envelope,
              "owner_before_d_effect": before_d_effect, "f1_before_d_effect": f1_before_d_effect,
              "journal_before_d_effect": journal_before_d_effect,
              "d_effect_request": d_effect, "owner_after_d_effect": after_d_effect,
              "f1_after_d_effect": f1_after_d_effect,
              "journal_after_d_effect": journal_after_d_effect,
              "f4_final_snapshot": f4.snapshot(), "f4_calls": f4.calls,
              "owner_final_tree": helpers.tree(owner_root), "f1_final": helpers.f1_raw(f1_path),
              "owner_d_process": owner_d_process}
    f4.close(True)
    return result


def source_manifest() -> dict:
    result = helpers.source_manifest()
    research = REPO / "docs/research"
    receipt = (research / "phase-i-sol-integration/evidence/sources/receipt"
               / "research/phase-i-t18-sink-order-20261103")
    paths = {
        "native_acceptance_probe": HERE / "probe.py",
        "native_ownership_probe": OWNERSHIP,
        "native_helpers": helpers.NATIVE_HELPERS_PATH,
        "f1_holder_probe": repair.HERE / "probe.py",
        "f4_continuation_sink": research / "phase-i-continuation-stack/continuation_sink.py",
        "f4_composed_sink": research / "phase-i-composed-effects/composed_sink.py",
        "f4_cold_factory": research / "phase-i-cold-activation/cold_sink.py",
        "f4_admission_sink": research / "phase-i-effect-admission/admission_sink.py",
        "f4_admission": research / "phase-i-effect-admission/admission.py",
        "f4_retry_candidate": research / "phase-i-effect-retry/candidate.py",
        "f4_published_cut_sink": receipt / "published-cut/cut_sink.py",
        "f4_managed_sink": receipt / "managed-revocation/managed_sink.py",
        "f4_managed_base": receipt / "run.py",
        "f1_bootstrap_service": (repair.ORIGINAL.parent.parent.parent
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
    raw = {"schema": "ases4-native-acceptance-races-v1", "started_ns": time.monotonic_ns(),
           "sources": source_manifest(), "cases": {}, "status": "RUNNING"}
    try:
        raw["cases"]["duplicate_acceptance"] = duplicate_acceptance(out)
        raw["cases"]["producer_overlap"] = producer_overlap(out)
        raw["status"] = "PASS"
    except BaseException as error:
        raw["status"] = "PROBE_FAILED"
        raw["failure"] = {"type": type(error).__name__, "message": str(error),
                          "traceback": traceback.format_exc(), "processes": helpers.PROCESSES}
        (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
        raise
    raw["finished_ns"] = time.monotonic_ns()
    raw["processes"] = helpers.PROCESSES
    (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": raw["status"], "raw": str(out / "raw.json")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
