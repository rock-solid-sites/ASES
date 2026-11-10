#!/usr/bin/env python3
"""Native-process evidence for the bounded admission/retry composition."""
import argparse
import concurrent.futures
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import traceback

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ADMISSION_DIR = HERE.parent / "phase-i-effect-admission"
RETRY_DIR = HERE.parent / "phase-i-effect-retry"
COMPOSED_SINK = HERE / "composed_sink.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


admit = load("composed_admission_probe", ADMISSION_DIR / "probe.py")
retry_probe = load("composed_retry_probe", RETRY_DIR / "probe.py")
n = admit.n
admit.SINK = COMPOSED_SINK
retry_probe.CANDIDATE = RETRY_DIR / "candidate.py"
CONTENT = admit.CONTENT
PROCESSES = []


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(path):
    return n.blob(path)


def safe_http(port, path):
    try:
        return n.http(port, path)
    except Exception as error:
        return dict(transport_error=type(error).__name__ + ":" + str(error))


def setup(out, name, attenuated=False):
    return admit.setup_case(Path(out) / "state" / name, name, attenuated=attenuated)


def source_rights(tree):
    selector = bytes.fromhex(tree["protected/CURRENT"]["raw_hex"]).decode().strip()
    state = json.loads(bytes.fromhex(tree["protected/" + selector]["raw_hex"]))
    units, unit = state["work_units"], "D"
    rights, enabled, seen = {"read", "write"}, True, set()
    while unit is not None:
        if unit not in units or unit in seen:
            return False
        seen.add(unit)
        current = units[unit]
        enabled = enabled and current["active"] and not current["sealed"]
        rights &= set(current["grants"])
        rights &= set(current.get("latent_ceiling", rights))
        unit = current["parent"]
    return bool(enabled and state["current_ingress"] == "W-L5" and "write" in rights), state


def result_frame(case, sink, before, extras=None):
    value = dict(label=Path(case["root"]).name, before=before,
                 after=dict(f1=admit.tree(Path(case["root"]) / "f1"),
                            l5=admit.tree(Path(case["root"]) / "l5"),
                            l6=admit.tree(Path(case["root"]) / "l6")),
                 envelope=case["envelope"], config=case["config"],
                 calls=sink.calls, local=blob(sink.journal),
                 witness=safe_http(sink.wp, "/status"), sink_status=(
                     safe_http(sink.port, "/status") if sink.port else None),
                 sink_process=sink.sink.meta, witness_process=sink.witness.meta)
    if extras:
        value.update(extras)
    return value


def start(case, gate=None):
    config = copy.deepcopy(case["config"])
    if gate:
        config["gate"] = gate
    case = dict(case, config=config)
    before = dict(f1=admit.tree(Path(case["root"]) / "f1"),
                  l5=admit.tree(Path(case["root"]) / "l5"),
                  l6=admit.tree(Path(case["root"]) / "l6"))
    sink = admit.Sink(Path(case["root"]) / "f4", config, recover=False)
    return case, before, sink


def stop(sink, kill=True):
    process = sink.sink.close(kill)
    return copy.deepcopy(process)


def fresh_cold(case, sink):
    old_identity = [sink.journal.stat().st_dev, sink.journal.stat().st_ino]
    stopped = stop(sink, True)
    sink.start(recover=True)
    ready = copy.deepcopy(sink.sink.ready)
    now_identity = [sink.journal.stat().st_dev, sink.journal.stat().st_ino]
    return dict(stopped_process=stopped, ready=ready,
                journal_identity_before=old_identity, journal_identity_after=now_identity,
                witness_pid=sink.witness.p.pid)


def submit(case, sink, envelope=None):
    return sink.submit(envelope or case["envelope"])


def case_allowed(out):
    case = setup(out, "allowed")
    case, before, sink = start(case)
    try:
        first = submit(case, sink)
        return result_frame(case, sink, before, dict(first=first))
    finally:
        sink.close()


def case_denied_and_negative(out):
    case = setup(out, "moved-denied", attenuated=True)
    case, before, sink = start(case)
    try:
        denied = submit(case, sink)
        composed = result_frame(case, sink, before, dict(denied=denied))
    finally:
        sink.close()

    # The exact same source-denied request is accepted by retry-only's flat
    # contract, demonstrating that the admission hook contributes the denial.
    source_allowed, _ = source_rights(before["l5"])
    payload = admit.canonical(case["envelope"])
    history = retry_probe.History("retry-only-source-denied", Path(out) / "state/retry-only",
                                  candidate=True)
    try:
        flat = history.submit(case["envelope"]["request_id"], payload)
        retry_only = dict(source_allowed=source_allowed, source_l5=before["l5"],
                          submitted_payload=payload, result=flat[2], capture=history.result())
    finally:
        history.close()
    return dict(composed=composed, retry_only=retry_only)


def case_lost_receipt_l6_cold(out):
    case = setup(out, "lost-receipt-l6-cold")
    case, before, sink = start(case)
    try:
        fault = sink.wcall("/fault", reject_publish=False, drop_publish_reply_once=True)
        first = submit(case, sink)
        effect_cut = blob(sink.journal)
        l6_before = admit.tree(Path(case["root"]) / "l6")
        change = admit.l6_change(case, "remove")
        l6_after = admit.tree(Path(case["root"]) / "l6")
        same = submit(case, sink)
        same_after = blob(sink.journal)

        conflict_envelope = copy.deepcopy(case["envelope"])
        conflict_envelope["epoch"] += ":conflict"
        conflict = submit(case, sink, conflict_envelope)
        conflict_after = blob(sink.journal)

        new_envelope = copy.deepcopy(case["envelope"])
        new_envelope["request_id"] += ":new-after-removal"
        new_id = submit(case, sink, new_envelope)
        new_after = blob(sink.journal)
        cold = fresh_cold(case, sink)
        same_cold = submit(case, sink)
        cold_after = blob(sink.journal)
        return result_frame(case, sink, before, dict(fault=fault, first=first,
            journal_after_first=effect_cut, l6_change=change, l6_before=l6_before,
            l6_after=l6_after, same_retry=same, journal_after_same=same_after,
            conflict=conflict, journal_after_conflict=conflict_after,
            new_id_after_removal=new_id, new_id_envelope=new_envelope,
            journal_after_new_id=new_after, cold=cold, same_retry_after_cold=same_cold,
            journal_after_cold_retry=cold_after))
    finally:
        sink.close()


def case_revoke(out):
    case = setup(out, "revoke-history")
    case, before, sink = start(case)
    try:
        first = submit(case, sink)
        after_first = blob(sink.journal)
        revoke = sink.call("/revoke", {})
        after_revoke = blob(sink.journal)
        old = submit(case, sink)
        after_old = blob(sink.journal)
        new_envelope = copy.deepcopy(case["envelope"])
        new_envelope["request_id"] += ":after-revoke"
        new_id = submit(case, sink, new_envelope)
        after_new = blob(sink.journal)
        return result_frame(case, sink, before, dict(first=first, journal_after_first=after_first,
            revoke=revoke, journal_after_revoke=after_revoke, old_observation=old,
            journal_after_old_observation=after_old, new_envelope=new_envelope,
            new_after_revoke=new_id, journal_after_new=after_new))
    finally:
        sink.close()


def case_remote_rejection(out):
    case = setup(out, "remote-rejection")
    case, before, sink = start(case)
    try:
        fault = sink.wcall("/fault", reject_publish=True)
        first = submit(case, sink)
        after_first = blob(sink.journal)
        same = submit(case, sink)
        after_same = blob(sink.journal)
        witness_before_conflict = n.http(sink.wp, "/status")
        conflict_envelope = copy.deepcopy(case["envelope"])
        conflict_envelope["pair"]["required"]["project"] += ":conflict"
        conflict = submit(case, sink, conflict_envelope)
        witness_after_conflict = n.http(sink.wp, "/status")
        after_conflict = blob(sink.journal)
        stopped = stop(sink, True)
        sink.start(recover=True)
        cold_ready = copy.deepcopy(sink.sink.ready)
        return result_frame(case, sink, before, dict(fault=fault, first=first,
            journal_after_first=after_first, same_retry=same, journal_after_same=after_same,
            conflict=conflict, conflict_envelope=conflict_envelope,
            witness_before_conflict=witness_before_conflict,
            witness_after_conflict=witness_after_conflict,
            journal_after_conflict=after_conflict, stopped_process=stopped,
            cold_ready=cold_ready))
    finally:
        sink.close()


def case_kill_after_append(out):
    case = setup(out, "kill-after-local-append")
    old_gate = os.environ.get("ASES_RETRY_GATE")
    os.environ["ASES_RETRY_GATE"] = "after-append"
    try:
        case, before, sink = start(case)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(submit, case, sink)
                gate = json.loads(sink.sink.read())
                at_gate = blob(sink.journal)
                witness_at_gate = n.http(sink.wp, "/status")
                process = stop(sink, True)
                try:
                    reply = future.result(timeout=8)
                    transport_error = None
                except Exception as error:
                    reply = None
                    transport_error = type(error).__name__ + ":" + str(error)
            cold = n.Child([sys.executable, "-B", COMPOSED_SINK, "--sink", "recover",
                            sink.journal, str(sink.wp), "published-cut", case["config"]["import_id"],
                            sink.config_path])
            cold_ready = copy.deepcopy(cold.ready)
            cold_process = cold.close(True)
            return result_frame(case, sink, before, dict(gate=gate,
                journal_at_gate=at_gate, witness_at_gate=witness_at_gate,
                killed_process=process, request_reply=reply, transport_error=transport_error,
                cold_ready=cold_ready, cold_process=cold_process))
        finally:
            sink.close()
    finally:
        if old_gate is None:
            os.environ.pop("ASES_RETRY_GATE", None)
        else:
            os.environ["ASES_RETRY_GATE"] = old_gate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    out = parser.parse_args().out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    n.CHILDREN.clear(); n.PROCESSES.clear(); n.EVENTS.clear()
    admit.PROCESSES.clear(); retry_probe.PROCESSES.clear()
    data = dict(schema="ases.phase-i-composed-effects.v1",
        started_ns=time.monotonic_ns(), parent_commit=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
        adapter_sha256=sha(COMPOSED_SINK.read_bytes()),
        inputs={"admission_packet": sha((ADMISSION_DIR / "PACKET.md").read_bytes()),
                "retry_candidate": sha((RETRY_DIR / "candidate.py").read_bytes()),
                "admission_probe": sha((ADMISSION_DIR / "probe.py").read_bytes()),
                "retry_probe": sha((RETRY_DIR / "probe.py").read_bytes())},
        cases={})
    try:
        data["cases"]["allowed"] = case_allowed(out)
        data["cases"]["denied-and-retry-only-negative"] = case_denied_and_negative(out)
        data["cases"]["lost-receipt-l6-cold"] = case_lost_receipt_l6_cold(out)
        data["cases"]["revoke-history"] = case_revoke(out)
        data["cases"]["remote-rejection"] = case_remote_rejection(out)
        data["cases"]["kill-after-local-append"] = case_kill_after_append(out)
        data["execution"] = "PASS"
    except BaseException:
        data["execution"] = "ERROR"
        data["harness_error"] = traceback.format_exc()
    finally:
        data.update(processes=n.PROCESSES, events=n.EVENTS, finished_ns=time.monotonic_ns())
        (out / "raw.json").write_text(json.dumps(data, sort_keys=True, indent=2) + "\n")
    print(json.dumps(dict(execution=data["execution"], cases=len(data["cases"]), output=str(out)),
                     sort_keys=True))
    return 0 if data["execution"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
