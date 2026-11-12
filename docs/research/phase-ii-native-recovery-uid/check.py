#!/usr/bin/env python3
"""Check captured UID-custodied native recovery evidence from raw records."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys


def need(ok, message):
    if not ok:
        raise ValueError(message)


def status_identity(value, uid, label):
    need(isinstance(value, dict), label + " /proc status missing")
    need(value.get("Uid", "").split() == [str(uid)] * 4,
         label + " UID real/effective/saved/fs mismatch")
    need(value.get("Gid", "").split() == [str(uid)] * 4,
         label + " GID real/effective/saved/fs mismatch")
    need(value.get("Groups") == "", label + " has supplemental groups")
    need(value.get("CapPrm") == "0000000000000000"
         and value.get("CapEff") == "0000000000000000",
         label + " retains permitted/effective capabilities")
    need(value.get("NoNewPrivs") == "1", label + " lacks no-new-privileges")
    # CapBnd is deliberately recorded and syntax-checked, not assumed empty.
    need(re.fullmatch(r"[0-9a-fA-F]+", value.get("CapBnd", "")) is not None,
         label + " missing actual CapBnd observation")


def denied_os(result, label, allowed=(13,)):
    need(isinstance(result, dict) and result.get("result") == "denied",
         label + " did not record an OS denial")
    need(result.get("errno") in allowed, label + " denial was not the expected OS denial")


def cli_refusal(value, event, label):
    need(isinstance(value, dict), label + " raw CLI attempt missing")
    need(value.get("returncode", 0) != 0, label + " unexpectedly exited successfully")
    need(isinstance(value.get("argv"), list) and len(value["argv"]) == 4,
         label + " did not invoke the actual fixed CLI")
    stdout, stderr = value.get("stdout", ""), value.get("stderr", "")
    need(isinstance(stdout, str) and isinstance(stderr, str), label + " stdio not retained")
    need("ModuleNotFoundError" not in stdout + stderr
         and "ImportError" not in stdout + stderr
         and "SyntaxError" not in stdout + stderr,
         label + " failed import/syntax instead of reaching protected storage")
    frame = value.get("frame")
    need(isinstance(frame, dict) and frame.get("event") == event,
         label + " structured CLI refusal frame missing")
    need(frame.get("status") in ("refused", "refused-writer-guard-busy"),
         label + " did not refuse the protected owner operation")
    # The CLI catches permission failures into JSON; require that actual error
    # classification or EACCES text survived into the structured result.
    reason = str(frame.get("reason", "")) + " " + str(frame.get("error", ""))
    need(frame.get("error") == "PermissionError" or "Permission denied" in reason,
         label + " refusal did not reach actual protected-store permission check")
    return frame


def check_worker(case, case_name):
    audit = case.get("worker_audit")
    need(isinstance(audit, dict) and audit.get("event") == "UID_RECOVERY_WORKER_AUDIT",
         case_name + " one-shot worker audit frame missing")
    need(audit.get("uid") == audit.get("euid") == 2001,
         case_name + " direct audit ran outside UID 2001")
    status_identity(audit.get("process_status"), 2001, case_name + " worker")
    status_identity(audit.get("owner_process_status"), 2000, case_name + " manager")
    descriptors = audit.get("descriptors")
    need(isinstance(descriptors, list) and {d.get("fd") for d in descriptors} >= {0, 1, 2},
         case_name + " worker FD records incomplete")
    need(all("error" not in d for d in descriptors), case_name + " worker FD classification incomplete")
    actual_writable = [d for d in descriptors
                       if d.get("kind") == "regular" and d.get("access_mode") in (1, 2)]
    need(actual_writable == audit.get("writable_authority_regular_fds") == [],
         case_name + " worker has a writable regular authority FD")
    direct = audit.get("direct")
    need(isinstance(direct, dict), case_name + " direct access checks missing")
    denied_os(direct.get("owner_current_open"), case_name + " protected CURRENT open")
    denied_os(direct.get("sink_socket"), case_name + " sink Unix socket")
    denied_os(direct.get("witness_socket"), case_name + " witness Unix socket")
    strict = cli_refusal(direct.get("reconcile"), "native-publication-reconcile",
                         case_name + " strict CLI")
    observed = cli_refusal(direct.get("observe_local"), "native-local-observation",
                           case_name + " observe-local CLI")
    need(direct["reconcile"]["argv"][-1] == case.get("request_id")
         and direct["observe_local"]["argv"][-1] == case.get("request_id"),
         case_name + " direct CLI request differs from fixture ID")

    manager_fds = direct.get("owner_process_fds")
    need(isinstance(manager_fds, dict)
         and manager_fds.get("result") in ("denied", "listed"),
         case_name + " read-only manager FD inspection missing")

    descendant = audit.get("fork_exec_descendant")
    need(isinstance(descendant, dict) and descendant.get("returncode") == 0,
         case_name + " fork/exec descendant did not complete")
    value = descendant.get("value")
    need(isinstance(value, dict), case_name + " descendant raw result missing")
    status_identity(value.get("status"), 2001, case_name + " descendant")
    descfds = value.get("descriptors")
    need(isinstance(descfds, list) and {d.get("fd") for d in descfds} >= {0, 1, 2},
         case_name + " descendant FD records incomplete")
    need(not any(d.get("kind") == "regular" and d.get("access_mode") in (1, 2)
                 for d in descfds), case_name + " descendant has writable regular FD")
    denied_os(value.get("direct_owner_current_open"), case_name + " descendant protected CURRENT")
    denied_os(value.get("sink_socket"), case_name + " descendant sink socket")
    denied_os(value.get("witness_socket"), case_name + " descendant witness socket")
    need(value.get("status", {}).get("setuid", {}).get("result") == "denied"
         and value["status"]["setuid"].get("errno") == 1,
         case_name + " descendant acquired manager UID")
    for name, event in (("strict", "native-publication-reconcile"),
                        ("observer", "native-local-observation")):
        cli_refusal(value.get("direct_cli", {}).get(name), event,
                    case_name + " descendant " + name + " CLI")
    return audit


def denial_cut(snapshot, label):
    need(isinstance(snapshot, dict), label + " manager snapshot missing")
    owner_frame = snapshot.get("owner_frame")
    need(isinstance(owner_frame, dict) and isinstance(owner_frame.get("reply"), dict),
         label + " actual owner read frame missing")
    owner_state = owner_frame["reply"].get("snapshot")
    need(isinstance(owner_state, dict), label + " actual owner snapshot missing")
    for key in ("owner_tree", "f1", "journal", "witness"):
        need(key in snapshot, label + " lacks actual " + key + " record")
    return {"owner": owner_state, "owner_tree": snapshot["owner_tree"],
            "f1": snapshot["f1"], "journal": snapshot["journal"],
            "witness": snapshot["witness"]}


def record_bytes(record, label):
    need(isinstance(record, dict), label + " byte record missing")
    raw = bytes.fromhex(record.get("raw_hex", ""))
    need(len(raw) == record.get("size")
         and hashlib.sha256(raw).hexdigest() == record.get("sha256"),
         label + " raw bytes/digest/size mismatch")
    return raw


def owner_snapshot(snapshot, label):
    frame = snapshot.get("owner_frame") if isinstance(snapshot, dict) else None
    need(isinstance(frame, dict) and isinstance(frame.get("reply"), dict),
         label + " owner response missing")
    value = frame["reply"].get("snapshot")
    need(isinstance(value, dict) and isinstance(value.get("state"), dict),
         label + " owner state missing")
    return value


def validate_recovery(case, name):
    recovery = case.get("recovery")
    need(isinstance(recovery, dict), name + " manager recovery record missing")
    command = recovery.get("command")
    need(isinstance(command, dict) and command.get("returncode") == 0,
         name + " manager recovery command did not exit successfully")
    frame = command.get("frame")
    expected_event = ("native-publication-reconcile" if name == "local"
                      else "native-local-observation")
    need(isinstance(frame, dict) and frame.get("event") == expected_event
         and frame.get("status") == "published",
         name + " manager recovery CLI did not report publication")
    before, after = recovery.get("before"), recovery.get("after")
    before_owner = owner_snapshot(before, name + " pre-recovery")
    after_owner = owner_snapshot(after, name + " post-recovery")
    request_id = case["request_id"]
    effects_before = before_owner["state"]["native_owner"]["effects"]
    effects_after = after_owner["state"]["native_owner"]["effects"]
    pending = effects_before.get(request_id, {})
    expected_pending = "local" if name == "local" else "reserved"
    need(pending.get("status") == expected_pending,
         name + " recovery did not begin from the actual pending owner state")
    effect = effects_after.get(request_id, {})
    need(effect.get("status") == "published" and type(effect.get("seq")) is int,
         name + " reported CLI success while owner effect remains pending")
    raw_before = record_bytes(before.get("journal"), name + " pre-recovery journal")
    raw_after = record_bytes(after.get("journal"), name + " post-recovery journal")
    need(raw_before == raw_after, name + " recovery appended or altered journal bytes")
    events = [json.loads(line) for line in raw_after.splitlines() if line]
    accepted = [event for event in events if event.get("event") == "effect_accepted"
                and event.get("request_id") == request_id]
    need(len(accepted) == 1 and accepted[0].get("seq") == effect["seq"],
         name + " owner settlement is not bound to the single actual journal event")
    event = accepted[0]
    need(effect.get("payload_sha256") == hashlib.sha256(event["payload"].encode()).hexdigest(),
         name + " owner publication is not bound to the event payload")
    witness = after.get("witness", {}).get("body", {}).get("current")
    need(isinstance(witness, dict)
         and witness.get("journal_sha256") == hashlib.sha256(raw_after).hexdigest(),
         name + " settlement lacks fresh full-cut witness confirmation")
    cold = recovery.get("cold_restart_ready")
    need(isinstance(cold, dict) and cold.get("ready") is True,
         name + " ordinary cold restart did not accept the actual published cut")
    return {"recovery": recovery, "event": event, "effect": effect}


def check(raw):
    need(isinstance(raw, dict) and raw.get("status") == "PASS", "native recovery driver did not pass")
    need(set(raw.get("cases", {})) == {"local", "reserved"}, "both native recovery histories required")
    for name in ("local", "reserved"):
        case = raw["cases"][name]
        need(case.get("request_id") and case.get("case_kind") == name,
             name + " actual fixture identity missing")
        check_worker(case, name)
        management = case.get("worker_management_attempt")
        need(isinstance(management, dict), name + " mediated management denial missing")
        decision = management.get("driver_decision", {})
        need(decision.get("result") == "DENY", name + " worker management request was not denied")
        need(management.get("controller_op_count_before") == management.get("controller_op_count_after"),
             name + " denied management request reached UID 2000 controller")
        before = case.get("manager_before_denials")
        after = case.get("manager_after_denials")
        need(isinstance(before, dict) and isinstance(after, dict),
             name + " actual before/after denial snapshots missing")
        need(denial_cut(before, name + " before denial") == denial_cut(after, name + " after denial"),
             name + " denied worker attempts changed owner/F1/material/journal/witness state")
        validate_recovery(case, name)
    return {"status": "PASS", "checked_cases": ["local", "reserved"],
            "checked_direct_worker_audits": 2}


def fake_success_with_pending_owner(value):
    case = value["cases"]["local"]
    recovery = case["recovery"]
    frame = recovery["command"].setdefault("frame", {})
    frame.update(event="native-publication-reconcile", status="published")
    before = owner_snapshot(recovery["before"], "negative-control before")
    after = owner_snapshot(recovery["after"], "negative-control after")
    request_id = case["request_id"]
    actual_pending = copy.deepcopy(before["state"]["native_owner"]["effects"][request_id])
    after["state"]["native_owner"]["effects"][request_id] = actual_pending


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("--controls", action="store_true")
    args = parser.parse_args()
    raw = json.loads(args.raw.read_text(encoding="utf-8"))
    result = check(raw)
    if args.controls:
        cases = []
        mutants = (
            ("allowed-worker-management", lambda v: v["cases"]["local"]["worker_management_attempt"].
             update(driver_decision={"result": "ALLOW"})),
            ("success-frame-with-pending-owner", fake_success_with_pending_owner),
        )
        for name, mutate in mutants:
            altered = copy.deepcopy(raw)
            mutate(altered)
            try:
                check(altered)
            except (ValueError, KeyError, TypeError):
                cases.append({"name": name, "rejected": True})
            else:
                raise ValueError("checker accepted negative control: " + name)
        result["negative_controls"] = cases
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, sort_keys=True))
        raise SystemExit(1)
