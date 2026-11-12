#!/usr/bin/env python3
"""Actual native journal-fsync / owner-local-sequence observation histories."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
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
NATIVE_SINK = REPO / "docs/research/phase-ii-native-ownership/native_sink.py"
RECONCILE_DIR = REPO / "docs/research/phase-ii-native-publication-reconcile"
RECONCILE = RECONCILE_DIR / "reconcile.py"
OBSERVE = HERE / "observe_local.py"
TEST_SINK = HERE / "test_sink_gate.py"
PARENT_PROBE = RECONCILE_DIR / "probe.py"
PROCESSES = []


def load_base():
    spec = importlib.util.spec_from_file_location("native_local_observation_base", BASE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


base = load_base()
native = base.native
native_sink = base.load_module("native_local_observation_native_sink", NATIVE_SINK)


def canonical(value):
    return base.canonical(value)


def sha(raw: bytes):
    return hashlib.sha256(raw).hexdigest()


def need(condition, reason):
    if not condition:
        raise AssertionError(reason)


def source_manifest():
    sources = {
        "probe": HERE / "probe.py",
        "test_sink_gate": TEST_SINK,
        "observe_local": OBSERVE,
        "reconcile": RECONCILE,
        "parent_probe": PARENT_PROBE,
        "native_owner_probe": BASE_PATH,
        "native_owner": base.HERE / "native_owner.py",
        "owner_cli": base.OWNER_CLI,
        "native_sink": NATIVE_SINK,
        "unix_transport": base.UNIX_TRANSPORT,
        "f1_repaired": base.REPAIRED_F1,
        "f4_cut_witness": REPO / "docs/research/phase-i-sol-integration/evidence/sources/receipt/research/phase-i-t18-sink-order-20261103/published-cut/cut_sink.py",
        "l5_core": base.L5 / "l5_integrated.py",
        "l6_store": base.L6 / "store.py",
    }
    return {name: {"path": str(path), "sha256": sha(path.read_bytes())}
            for name, path in sources.items() if path.is_file()}


class ObservationF4(base.NativeF4):
    """Existing NativeF4 fixture with only its real sink process wrapped."""

    def __init__(self, *args, **kwargs):
        self.use_test_sink_gate = True
        super().__init__(*args, **kwargs)

    def start(self, recover: bool):
        socket_name = "sink-cold.sock" if recover else "sink.sock"
        self.sink_socket = self.socket_dir / socket_name
        argv = [sys.executable, "-B", str(TEST_SINK), "--sink",
                "recover" if recover else "fresh", str(self.journal),
                str(self.witness_port), "published-cut", self.witness_root,
                str(self.config_path)]
        self.sink = base.UnixChild(argv, self.sink_socket, self.witness_socket)
        self.port = self.sink.ready.get("port", 0)
        return self.sink.ready


def owner_view(owner_root: Path):
    process = base.OwnerProcess(owner_root)
    view = process.snapshot()
    process.close()
    return view


def prepare(out: Path, label: str, native_gate=None):
    root = out / "state" / label
    setup = base.setup_native_f3(root, world="A", activate=True)
    owner_root = Path(setup["owner_root"])
    initial_owner = setup["owner_ready"]["snapshot"]
    witness_root = initial_owner["state"]["native_owner"]["domain_id"]
    f4 = ObservationF4(root / "f4", owner_root, witness_root, gate=native_gate)
    owner = base.OwnerProcess(owner_root)
    attached = owner.call({"op": "read"})["reply"]["snapshot"]
    owner.close()
    request_id = witness_root + ":local-observation:" + label
    envelope = base.native_envelope(attached, request_id)
    return {"root": root, "setup": setup, "owner_root": owner_root,
            "witness_root": witness_root, "f4": f4, "request_id": request_id,
            "envelope": envelope, "attached_owner": attached}


def retry_state(journal: Path):
    # This is the actual pinned parser/index used by F4 and both commands.
    return native_sink.composed.retry.RetryState(journal, True)


def make_fs_invalid_gap(case):
    f4 = case["f4"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        request = pool.submit(f4.submit, case["envelope"])
        line = f4.sink.read(timeout=15)
        gate = json.loads(line)
        if gate.get("event") != "GATE" or gate.get("stage") != "before-owner-local-observation":
            raise RuntimeError("wrapper did not pause immediately before the original local callback: "
                               + canonical(gate))
        journal_at_gate = native.blob(f4.journal)
        parsed = retry_state(f4.journal)
        event = parsed.request_index.get(case["request_id"])
        owner_at_gate = owner_view(case["owner_root"])
        witness_at_gate = f4.witness_call("/status")
        # The callback has not run. Kill the retained actual service process.
        killed_sink = f4.sink.close(True)
        transport_result = request.result(timeout=15)
    parsed_after = retry_state(f4.journal)
    return {"gate": gate, "journal_at_gate": journal_at_gate,
            "actual_parsed_event": event, "actual_parser_event_count": len(parsed.events),
            "actual_effect_count": len(parsed.effects), "owner_at_gate": owner_at_gate,
            "witness_at_gate": witness_at_gate, "killed_sink": killed_sink,
            "submit_transport_result": transport_result,
            "journal_after_kill": native.blob(f4.journal),
            "actual_index_after_kill": parsed_after.request_index.get(case["request_id"])}


def command(script: Path, owner_root: Path, request_id: str, gate=None, timeout=20):
    argv = [sys.executable, "-B", str(script), str(owner_root), request_id]
    if gate:
        argv += ["--test-gate", gate]
    meta = {"argv": argv, "start_ns": time.monotonic_ns()}
    proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, bufsize=0)
    meta["pid"] = proc.pid
    PROCESSES.append(meta)
    if not select.select([proc.stdout], [], [], timeout)[0]:
        proc.kill(); meta["exit"] = proc.wait(timeout=5)
        meta["stderr"] = proc.stderr.read().decode(errors="replace")
        raise TimeoutError("native command produced no frame")
    first_raw = proc.stdout.readline(4 * 1024 * 1024).decode(errors="replace")
    try: first = json.loads(first_raw)
    except json.JSONDecodeError: first = None
    meta["frames"] = [{"ns": time.monotonic_ns(), "raw": first_raw, "value": first}]
    if gate and isinstance(first, dict) and first.get("event") == "GATE":
        return proc, meta
    meta["result"] = first
    meta["exit"] = proc.wait(timeout=timeout)
    meta["exit_ns"] = time.monotonic_ns()
    meta["stderr"] = proc.stderr.read().decode(errors="replace")
    return None, meta


def finish_command(proc, meta, action="continue"):
    if proc.poll() is None:
        if action == "kill":
            proc.kill()
        elif action == "eof":
            proc.stdin.close()
        else:
            proc.stdin.write(b"continue\n"); proc.stdin.flush()
    if action == "continue" and select.select([proc.stdout], [], [], 15)[0]:
        raw = proc.stdout.readline(4 * 1024 * 1024).decode(errors="replace")
        try: value = json.loads(raw)
        except json.JSONDecodeError: value = None
        meta["frames"].append({"ns": time.monotonic_ns(), "raw": raw, "value": value})
        meta["result"] = value
    meta["exit"] = proc.wait(timeout=15)
    meta["exit_ns"] = time.monotonic_ns()
    meta["stderr"] = proc.stderr.read().decode(errors="replace")
    return meta


def case_snapshot(case):
    return {"journal": native.blob(case["f4"].journal),
            "owner": owner_view(case["owner_root"]),
            "witness": case["f4"].witness_call("/status")}


def strict_default_refusal(case):
    before = case_snapshot(case)
    _proc, result = command(RECONCILE, case["owner_root"], case["request_id"])
    after = case_snapshot(case)
    return {"before": before, "command": result, "after": after}


def fsync_gap_history(out: Path):
    case = prepare(out, "fsync-gap")
    gap = make_fs_invalid_gap(case)
    f1root = Path(case["setup"]["f1_root"])
    f1_before_world_change = base.f1_raw(f1root / "store.sqlite")
    changed_bundle = base.repair.configuration("C", base.CONTENT, True)["acceptance_bundle"]
    f1_change = base.native_f1_accept(f1root, changed_bundle, base.CONTENT)
    owner = base.OwnerProcess(case["owner_root"])
    seal_for_new_world = owner.call({"op": "seal"})
    accept_new_world = owner.call({"op": "accept"})
    after_new_world = owner.call({"op": "read"})["reply"]["snapshot"]
    old_registration = case["envelope"]["import_id"]
    retained_before_move = {item["id"]: item["status"] for item in
                            after_new_world["state"]["native_owner"]["registrations"]}
    source_transitions = {"seal_before_new_world": seal_for_new_world,
                          "move": owner.call({"op": "move"}),
                          "activate": owner.call({"op": "activate"})}
    current_owner_before_observation = owner.call({"op": "read"})["reply"]["snapshot"]
    owner.close()
    f1_after_world_change = base.f1_raw(f1root / "store.sqlite")
    owner_before_observation = owner_view(case["owner_root"])
    f1_witness_before_observation = case["f4"].witness_call("/status")
    journal_before_observation = native.blob(case["f4"].journal)
    strict = strict_default_refusal(case)
    _proc, observation = command(OBSERVE, case["owner_root"], case["request_id"])
    after_observation = case_snapshot(case)
    owner_after_observation = after_observation["owner"]
    exact_replay = case["f4"].cold_restart()
    # Ordinary recovered startup is sealed; reopen via its actual management
    # API after the old event has already been observed and settled.
    reopen = [case["f4"].call("/replace", {"holder": "local-observation-recovery"}),
              case["f4"].call("/activate", {"authority_version": 2})]
    current_envelope = base.native_envelope(
        owner_after_observation, case["witness_root"] + ":new-current-world-after-move")
    fresh_denial = case["f4"].submit(current_envelope, authority_version=2)
    before_historical = native.blob(case["f4"].journal)
    historical_result = case["f4"].submit(case["envelope"], authority_version=2)
    after_historical = native.blob(case["f4"].journal)
    owner_final = owner_view(case["owner_root"])
    final = case_snapshot(case)
    result = {"setup": case["setup"], "request_id": case["request_id"],
              "envelope": case["envelope"], "gap": gap, "strict_refusal": strict,
              "observer": observation, "after_observation": after_observation,
              "owner_before_observation": owner_before_observation,
              "owner_after_observation": owner_after_observation,
              "journal_before_observation": journal_before_observation,
              "witness_before_observation": f1_witness_before_observation,
              "ordinary_cold_ready": exact_replay, "f4_reopen": reopen,
              "f1_before_world_change": f1_before_world_change,
              "f1_changed_world_accept": f1_change,
              "f1_after_world_change": f1_after_world_change,
              "seal_for_new_world": seal_for_new_world,
              "owner_accept_new_world": accept_new_world,
              "owner_after_new_world": after_new_world,
              "retained_registrations_before_move": retained_before_move,
              "old_registration_id": old_registration,
              "source_transitions": source_transitions,
              "current_owner_before_observation": current_owner_before_observation,
              "current_envelope": current_envelope,
              "fresh_current_denial": fresh_denial,
              "historical_journal_before": before_historical,
              "historical_result": historical_result,
              "historical_journal_after": after_historical,
              "owner_final": owner_final, "final": final}
    case["f4"].close(True)
    return result


def observer_kill_retry(out: Path):
    case = prepare(out, "observer-kill-before-publication")
    gap = make_fs_invalid_gap(case)
    strict_before = strict_default_refusal(case)
    proc, gated = command(OBSERVE, case["owner_root"], case["request_id"],
                          gate="after-local-observation-before-publication")
    if proc is None:
        raise RuntimeError("observer did not pause after actual local selection")
    at_gate = case_snapshot(case)
    killed = finish_command(proc, gated, action="kill")
    strict_retry = command(RECONCILE, case["owner_root"], case["request_id"])[1]
    after = case_snapshot(case)
    case["f4"].close(True)
    return {"setup": case["setup"], "request_id": case["request_id"], "gap": gap,
            "strict_before_observation": strict_before, "gate": gated.get("frames", [])[0]["value"],
            "at_gate": at_gate, "killed_observer": killed,
            "strict_retry": strict_retry, "after": after}


def reserved_only_control(out: Path):
    case = prepare(out, "reserved-only", native_gate="guarded")
    f4 = case["f4"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        pending = pool.submit(f4.submit, case["envelope"])
        line = f4.sink.read(timeout=15)
        gate = json.loads(line)
        if gate.get("event") != "GATE" or gate.get("stage") != "guarded":
            raise RuntimeError("guarded pre-append gate did not occur: " + canonical(gate))
        journal_at_gate = native.blob(f4.journal)
        owner_at_gate = owner_view(case["owner_root"])
        f4.sink.close(True)
        response = pending.result(timeout=15)
    _proc, strict = command(RECONCILE, case["owner_root"], case["request_id"])
    _proc, observed = command(OBSERVE, case["owner_root"], case["request_id"])
    after = case_snapshot(case)
    f4.close(True)
    return {"setup": case["setup"], "request_id": case["request_id"],
            "gate": gate, "journal_at_gate": journal_at_gate,
            "owner_at_gate": owner_at_gate, "submit_result": response,
            "strict_reconcile": strict, "observer": observed, "after": after}


def mismatched_payload_control(out: Path):
    case = prepare(out, "mismatched-payload")
    gap = make_fs_invalid_gap(case)
    owner = native_sink.Owner(case["owner_root"])
    selector, state = owner.selected()
    effect = state["native_owner"]["effects"][case["request_id"]]
    old_hash = effect["payload_sha256"]
    selected_path = case["owner_root"] / "protected" / selector
    prior_selected_bytes = selected_path.read_bytes()
    effect["payload_sha256"] = "0" * 64 if old_hash != "0" * 64 else "1" * 64
    changed_bytes = (canonical(state) + "\n").encode()
    with selected_path.open("r+b") as stream:
        stream.write(changed_bytes)
        stream.truncate()
        stream.flush()
        os.fsync(stream.fileno())
    changed_selected_record = base.file_record(selected_path)
    before = case_snapshot(case)
    _proc, observer = command(OBSERVE, case["owner_root"], case["request_id"])
    after = case_snapshot(case)
    case["f4"].close(True)
    return {"setup": case["setup"], "request_id": case["request_id"], "gap": gap,
            "owner_selected_after_mutation": changed_selected_record,
            "owner_selected_original": {"raw_hex": prior_selected_bytes.hex(),
                                         "sha256": sha(prior_selected_bytes),
                                         "size": len(prior_selected_bytes)},
            "control_change": {"previous_payload_sha256": old_hash,
                               "selected_payload_sha256": effect["payload_sha256"]},
            "before_observation": before, "observer": observer, "after_observation": after}


def parent_regression(out: Path):
    destination = out / "parent-reconciliation-regression"
    argv = [sys.executable, "-B", str(PARENT_PROBE), "--out", str(destination)]
    meta = {"argv": argv, "start_ns": time.monotonic_ns()}
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
    meta["pid"] = proc.pid
    PROCESSES.append(meta)
    stdout, stderr = proc.communicate(timeout=120)
    meta["exit"] = proc.returncode
    meta["exit_ns"] = time.monotonic_ns()
    meta["stdout"] = stdout.decode(errors="replace")
    meta["stderr"] = stderr.decode(errors="replace")
    probe_raw_path = destination / "raw.json"
    probe_raw = json.loads(probe_raw_path.read_text()) if probe_raw_path.is_file() else None
    return {"process": meta, "raw_path": str(probe_raw_path), "raw": probe_raw}


def validate_gap(case):
    request_id = case["request_id"]
    gap = case["gap"]
    parsed_event = gap["actual_parsed_event"]
    need(gap["gate"].get("stage") == "before-owner-local-observation"
         and gap["gate"].get("event_seq") == parsed_event.get("seq") == 4
         and parsed_event.get("event") == "effect_accepted",
         "test wrapper did not stop at the genuine fsync/callback boundary")
    need(gap["actual_effect_count"] == 1 and gap["actual_parser_event_count"] == 4
         and gap["actual_index_after_kill"] == parsed_event,
         "actual RetryState parser/index did not retain the single complete fsynced event")
    owner_state = gap["owner_at_gate"]["state"]["native_owner"]
    reservation = owner_state["effects"][request_id]
    need(reservation.get("status") == "reserved" and "seq" not in reservation,
         "native owner callback ran before the process was killed at its gate")
    raw_journal = bytes.fromhex(gap["journal_at_gate"]["raw_hex"])
    prefix = raw_journal[:raw_journal.rfind(b"\n", 0, len(raw_journal) - 1) + 1]
    witness_current = gap["witness_at_gate"]["body"]["current"]
    need(gap["journal_at_gate"]["sha256"] == gap["journal_after_kill"]["sha256"]
         and witness_current["journal_sha256"] == sha(prefix)
         and witness_current["journal_sha256"] != gap["journal_at_gate"]["sha256"],
         "fsync-gap journal or preceding witness cut did not remain exact")


def validate_primary(case):
    validate_gap(case)
    strict = case["strict_refusal"]["command"].get("result", {})
    need(strict.get("status") == "refused"
         and case["strict_refusal"]["before"]["journal"]["sha256"] ==
         case["strict_refusal"]["after"]["journal"]["sha256"]
         and case["strict_refusal"]["before"]["owner"]["state"] ==
         case["strict_refusal"]["after"]["owner"]["state"]
         and case["strict_refusal"]["before"]["witness"]["body"]["current"] ==
         case["strict_refusal"]["after"]["witness"]["body"]["current"],
         "strict reconciler did not refuse reserved/no-sequence without mutation")
    observer = case["observer"].get("result", {})
    need(observer.get("status") == "published"
         and observer.get("observation_status") == "local"
         and observer.get("event_seq") == case["gap"]["actual_parsed_event"]["seq"],
         "opt-in observer did not select the sequence from the actual indexed journal event")
    before = case["gap"]["journal_at_gate"]
    after = case["after_observation"]["journal"]
    event = case["gap"]["actual_parsed_event"]
    final_parser = retry_state(Path(case["setup"]["owner_root"]).parents[0] / "f4" / "sink-effects.jsonl")
    need(before["sha256"] == after["sha256"] and len(final_parser.effects) == 1
         and final_parser.request_index[case["request_id"]]["seq"] == event["seq"],
         "local observation appended a second effect or changed the actual journal")
    final_effect = case["after_observation"]["owner"]["state"]["native_owner"]["effects"][case["request_id"]]
    need(final_effect.get("status") == "published" and final_effect.get("seq") == event["seq"],
         "observed event did not settle the same actual sequence")
    need(case["ordinary_cold_ready"].get("ready") is True,
         "ordinary cold startup did not accept the now-published actual full cut")

    old_pair = case["f1_before_world_change"]["pair"]
    current_pair = case["f1_after_world_change"]["pair"]
    f1_after = case["f1_after_world_change"]
    need(old_pair["accepted_content"] == current_pair["accepted_content"]
         == base.CONTENT and old_pair != current_pair
         and old_pair in [json.loads(item) for item in f1_after["retained"]]
         and current_pair in [json.loads(item) for item in f1_after["retained"]],
         "same-content changed F1 world did not retain both old and current observations")
    registrations = case["owner_after_new_world"]["state"]["native_owner"]["registrations"]
    owner_before_observation = case["owner_before_observation"]["state"]["native_owner"]
    owner_after_observation = case["owner_after_observation"]["state"]["native_owner"]
    current_registration = next(item for item in registrations
                                if item["id"] == owner_before_observation["selected"])
    need(case["old_registration_id"] in case["retained_registrations_before_move"]
         and len(registrations) >= 2
         and next(item for item in registrations if item["id"] == case["old_registration_id"])["status"] == "live",
         "changed current world did not preserve the old native registration")
    need(current_registration["pair"] == current_pair
         and case["old_registration_id"] != owner_before_observation["selected"]
         and case["owner_before_observation"]["state"]["native_owner"]["epoch"] ==
         case["owner_after_observation"]["state"]["native_owner"]["epoch"]
         and case["owner_before_observation"]["state"]["native_owner"]["selected"] ==
         case["owner_after_observation"]["state"]["native_owner"]["selected"]
         and case["journal_before_observation"]["sha256"] == case["after_observation"]["journal"]["sha256"],
         "observer changed current epoch/selection or appended while consuming the old world")
    need(case["fresh_current_denial"]["response"].get("status") == 409
         and case["fresh_current_denial"]["response"]["body"].get("reason") == "native-current-path-denied",
         "fresh current-world request did not reach and fail native current admission")
    f4_status = case["final"]["witness"]["body"]["current"]["authority"]
    current_owner = case["owner_after_observation"]
    need(f4_status["authority_version"] == 2
         and case["current_envelope"]["epoch"] == current_owner["state"]["native_owner"]["epoch"]
         and case["current_envelope"]["l5"] == current_owner["generation"],
         "fresh denial did not use current F4 version and current native owner generation")
    historical = case["historical_result"]["response"]
    need(historical.get("status") == 200 and historical["body"].get("outcome") == "already-accepted"
         and historical["body"].get("event_seq") == event["seq"]
         and case["historical_journal_before"]["sha256"] == case["historical_journal_after"]["sha256"],
         "old exact ID was not an unchanged historical observation after source move")
    f1_initial = case["f1_before_world_change"]
    need(f1_after["integrity"] == f1_initial["integrity"] == "ok"
         and f1_after["retained"] != [],
         "F1 integrity/retained observations were lost during source movement")


def validate_controls(cases):
    killed = cases["observer-kill-retry"]
    validate_gap(killed)
    gate = killed["gate"]
    need(gate.get("phase") == "after-local-observation-before-publication",
         "observer did not reach its committed-local/prepublication gate")
    at_gate_effect = killed["at_gate"]["owner"]["state"]["native_owner"]["effects"][killed["request_id"]]
    need(at_gate_effect.get("status") == "local" and at_gate_effect.get("seq") == 4
         and killed["at_gate"]["witness"]["body"]["current"]["journal_sha256"] !=
         killed["at_gate"]["journal"]["sha256"],
         "kill gate did not preserve local selection before publication")
    retry = killed["strict_retry"].get("result", {})
    after_effect = killed["after"]["owner"]["state"]["native_owner"]["effects"][killed["request_id"]]
    local_events = [item for item in killed["after"]["owner"]["state"].get("events", [])
                    if item.get("op") == "native-effect-locally-accepted"
                    and item.get("request_id") == killed["request_id"]]
    need(retry.get("status") == "published" and after_effect.get("status") == "published"
         and after_effect.get("seq") == 4 and len(local_events) == 1
         and killed["at_gate"]["journal"]["sha256"] == killed["after"]["journal"]["sha256"],
         "strict retry duplicated observation or append after the observer was killed")

    reserved = cases["reserved-only"]
    reserved_effect = reserved["owner_at_gate"]["state"]["native_owner"]["effects"][reserved["request_id"]]
    need(reserved["gate"].get("stage") == "guarded" and reserved_effect.get("status") == "reserved"
         and "seq" not in reserved_effect
         and reserved["strict_reconcile"].get("result", {}).get("status") == "refused"
         and reserved["observer"].get("result", {}).get("status") == "refused"
         and reserved["journal_at_gate"]["sha256"] == reserved["after"]["journal"]["sha256"]
         and reserved["owner_at_gate"]["state"] == reserved["after"]["owner"]["state"],
         "reserved-only request without a journal event was not retained/refused")
    no_event_state = retry_state(Path(reserved["setup"]["owner_root"]).parents[0] /
                                 "f4" / "sink-effects.jsonl")
    need(reserved["request_id"] not in no_event_state.request_index,
         "reserved-only control unexpectedly has a matching parsed journal event")

    mismatch = cases["mismatched-payload"]
    need(mismatch["control_change"]["previous_payload_sha256"] !=
         mismatch["control_change"]["selected_payload_sha256"]
         and mismatch["observer"].get("result", {}).get("status") == "refused"
         and mismatch["before_observation"]["journal"]["sha256"] ==
         mismatch["after_observation"]["journal"]["sha256"]
         and mismatch["before_observation"]["owner"]["state"] ==
         mismatch["after_observation"]["owner"]["state"],
         "mismatched reservation payload hash did not refuse without further mutation")
    if "parent-regression" in cases:
        parent = cases["parent-regression"]
        need(parent["process"]["exit"] == 0 and parent["raw"].get("status") == "PASS",
             "full parent reconciliation regression probe did not pass")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--skip-parent-regression", action="store_true",
                        help="development runs only; final PASS requires the one parent regression run")
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"refusing nonempty evidence directory: {out}")
    out.mkdir(parents=True, exist_ok=True)
    raw = {"schema": "ases4-native-local-observation-v1", "started_ns": time.monotonic_ns(),
           "sources": source_manifest(), "cases": {}, "processes": PROCESSES,
           "status": "RUNNING", "parent_regression_skipped": bool(args.skip_parent_regression)}
    try:
        raw["cases"]["fsync-gap"] = fsync_gap_history(out)
        (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
        validate_primary(raw["cases"]["fsync-gap"])
        raw["cases"]["observer-kill-retry"] = observer_kill_retry(out)
        (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
        raw["cases"]["reserved-only"] = reserved_only_control(out)
        (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
        raw["cases"]["mismatched-payload"] = mismatched_payload_control(out)
        (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
        validate_controls(raw["cases"])
        if not args.skip_parent_regression:
            raw["cases"]["parent-regression"] = parent_regression(out)
            (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
            validate_controls(raw["cases"])
        raw["status"] = "LOCAL_CASES_PASS_REGRESSION_NOT_RUN" if args.skip_parent_regression else "PASS"
    except BaseException as error:
        raw["failure"] = {"type": type(error).__name__, "message": str(error),
                          "traceback": traceback.format_exc()}
        raw["status"] = "PROBE_FAILED"
        raw["processes"] = PROCESSES
        (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
        raise
    raw["finished_ns"] = time.monotonic_ns()
    raw["processes"] = PROCESSES
    (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": raw["status"], "raw": str(out / "raw.json")}, sort_keys=True))


if __name__ == "__main__":
    main()
