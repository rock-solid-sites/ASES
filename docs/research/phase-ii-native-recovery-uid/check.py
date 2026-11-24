#!/usr/bin/env python3
"""Check captured UID-custodied native recovery evidence from raw records."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
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


def check_descriptor_records(entries, label):
    need(isinstance(entries, list) and {item.get("fd") for item in entries} >= {0, 1, 2},
         label + " FD records incomplete")
    need(len({item.get("fd") for item in entries}) == len(entries),
         label + " duplicate descriptor numbers")
    for item in entries:
        if "error" in item:
            # Directory iteration can capture its own just-closed descriptor.
            # Depending on whether the proc symlink or the descriptor is
            # checked first, the bounded fd 3 enumerator can report ENOENT or
            # EBADF after the directory iterator closes. No other FD error is
            # accepted; in particular standard pipe descriptors must fstat.
            need(item.get("fd") == 3 and item.get("errno") in (2, 9),
                 label + " descriptor classification failed")
        else:
            need(item.get("kind") in ("regular", "directory", "socket", "other")
                 and item.get("access_mode") in (0, 1, 2),
                 label + " descriptor facts incomplete")
    writable = [item for item in entries if item.get("kind") == "regular"
                and item.get("access_mode") in (1, 2)]
    return writable


def cli_refusal(value, event, label, script_name):
    need(isinstance(value, dict), label + " raw CLI attempt missing")
    need(value.get("returncode", 0) != 0, label + " unexpectedly exited successfully")
    need(isinstance(value.get("argv"), list) and len(value["argv"]) == 5
         and value["argv"][2].endswith(script_name),
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
    actual_writable = check_descriptor_records(descriptors, case_name + " worker")
    need(actual_writable == audit.get("writable_authority_regular_fds") == [],
         case_name + " worker has a writable regular authority FD")
    direct = audit.get("direct")
    need(isinstance(direct, dict), case_name + " direct access checks missing")
    denied_os(direct.get("owner_current_open"), case_name + " protected CURRENT open")
    denied_os(direct.get("sink_socket"), case_name + " sink Unix socket")
    denied_os(direct.get("witness_socket"), case_name + " witness Unix socket")
    strict = cli_refusal(direct.get("reconcile"), "native-publication-reconcile",
                         case_name + " strict CLI", "reconcile.py")
    observed = cli_refusal(direct.get("observe_local"), "native-local-observation",
                           case_name + " observe-local CLI", "observe_local.py")
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
    need(not check_descriptor_records(descfds, case_name + " descendant"),
         case_name + " descendant has writable regular FD")
    denied_os(value.get("direct_owner_current_open"), case_name + " descendant protected CURRENT")
    denied_os(value.get("sink_socket"), case_name + " descendant sink socket")
    denied_os(value.get("witness_socket"), case_name + " descendant witness socket")
    need(value.get("status", {}).get("setuid", {}).get("result") == "denied"
         and value["status"]["setuid"].get("errno") == 1,
         case_name + " descendant acquired manager UID")
    for name, event in (("strict", "native-publication-reconcile"),
                        ("observer", "native-local-observation")):
        cli_refusal(value.get("direct_cli", {}).get(name), event,
                    case_name + " descendant " + name + " CLI",
                    "reconcile.py" if name == "strict" else "observe_local.py")
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
    stable_owner = copy.deepcopy(owner_state)
    # Owner inventory observations and witness request nonces are per-read
    # metadata; compare the selected state/material and current witness cut.
    inventory = stable_owner.get("inventory", {})
    if isinstance(inventory, dict):
        inventory.pop("observation_ns", None)
    witness = snapshot["witness"]
    need(isinstance(witness, dict) and isinstance(witness.get("body", {}).get("current"), dict),
         label + " actual witness current cut missing")
    stable_witness = {"status": witness.get("status"),
                      "current": witness["body"]["current"]}
    return {"owner": stable_owner, "owner_tree": snapshot["owner_tree"],
            "f1": snapshot["f1"], "journal": snapshot["journal"],
            "witness": stable_witness}


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


def validate_initial_effect(case, name):
    result = case.get("initial_effect", {}).get("first_write")
    need(isinstance(result, dict), name + " actual first native effect/gate missing")
    gate = result.get("gate", {})
    expected_gate = "after-append" if name == "local" else "before-owner-local-observation"
    need(gate.get("event") == "GATE" and gate.get("stage") == expected_gate,
         name + " did not reach the required actual native sink gate")
    journal = record_bytes(result.get("journal_at_gate"), name + " gated journal")
    events = [json.loads(line) for line in journal.splitlines() if line]
    matching = [event for event in events if event.get("event") == "effect_accepted"
                and event.get("request_id") == case["request_id"]]
    need(len(matching) == 1, name + " gate lacks one actual complete accepted event")
    event = matching[0]
    need(result.get("indexed_event_at_gate") == event,
         name + " complete journal event is not the exact actual RetryState index entry")
    owner_frame = result.get("owner_at_gate", {})
    owner_state = owner_frame.get("reply", {}).get("snapshot", {}).get("state", {})
    effect = owner_state.get("native_owner", {}).get("effects", {}).get(case["request_id"], {})
    if name == "local":
        need(effect.get("status") == "local" and effect.get("seq") == event.get("seq"),
             "post-append EOF did not preserve the actual owner-local sequence")
    else:
        need(effect.get("status") == "reserved" and "seq" not in effect,
             "fsync-gap gate did not preserve reserved/no-sequence owner state")
    witness_current = result.get("witness_at_gate", {}).get("body", {}).get("current", {})
    prefix = journal[:journal.rfind(b"\n", 0, len(journal) - 1) + 1]
    need(witness_current.get("journal_sha256") == hashlib.sha256(prefix).hexdigest()
         and witness_current.get("journal_sha256") != hashlib.sha256(journal).hexdigest(),
         name + " witness did not remain at the actual preceding journal prefix")
    dead = result.get("dead_sink", {})
    need(type(dead.get("exit")) is int and dead["exit"] != 0,
         name + " retained sink process was not stopped at the actual gate")
    return event


def validate_transition_and_history(case, name, event):
    transition = case.get("transition", {})
    need(transition.get("event") == "RESPONSE" and transition.get("op") == "transition",
         name + " manager transition frame missing")
    for operation in (transition.get("f4_replace"), transition.get("f4_activate")):
        response = operation.get("response", {}) if isinstance(operation, dict) else {}
        need(response.get("status") == 200
             and response.get("body", {}).get("authority_version") == 2,
             name + " current F4 authority did not reach actual version 2")
    activate_request = transition["f4_activate"].get("request", {})
    need(activate_request.get("authority_version") == 2,
         name + " F4 activation did not request the actual current version")
    steps = transition.get("native_steps", [])
    need(len(steps) == 3, name + " actual native seal/move/activate steps missing")
    moved = owner_snapshot(transition.get("after", {}), name + " post-transition")
    native = moved["state"]["native_owner"]
    need(moved["state"].get("work_units", {}).get("C", {}).get("parent") == "Q",
         name + " source move did not update actual native work-unit path")

    denial = case.get("fresh_denial", {})
    route = denial.get("route", {}).get("driver_decision", {})
    need(route.get("event") == "RESPONSE" and route.get("op") == "write",
         name + " fresh-ID request did not pass the ordinary mediated write route")
    current = denial.get("controller_effect", {}).get("current_write", {})
    request_id = case["request_id"] + "-fresh"
    envelope = current.get("envelope", {})
    need(current.get("request_id") == request_id
         and envelope.get("request_id") == request_id
         and request_id != event.get("request_id"),
         name + " current-use attempt did not use a new worker-selected ID")
    selected = next((item for item in native.get("registrations", [])
                     if item.get("id") == native.get("selected")), None)
    need(selected is not None and envelope.get("epoch") == native.get("epoch")
         and envelope.get("import_id") == native.get("selected")
         and envelope.get("pair") == selected.get("pair"),
         name + " fresh envelope is not derived from actual current native epoch/selector")
    call = current.get("call", {})
    response = call.get("response", {})
    need(response.get("status") == 409
         and response.get("body", {}).get("reason") == "native-current-path-denied",
         name + " actual F4 reply is not the native path denial")
    need(record_bytes(call.get("before"), name + " fresh request journal before")
         == record_bytes(call.get("after"), name + " fresh request journal after"),
         name + " denied fresh ID appended journal bytes")
    request = call.get("request", {})
    need(request.get("authority_version") == 2,
         name + " fresh current-ID attempt did not use current F4 authority")

    historical = case.get("exact_old", {})
    indexed = historical.get("actual_index_event", {})
    old_request = historical.get("request", {})
    old_call = historical.get("call", {}).get("response", {})
    need(indexed == event and old_request.get("request_id") == event.get("request_id")
         and old_request.get("payload") == event.get("payload")
         and old_request.get("authority_version") == event.get("accepted_under_version") == 1,
         name + " old ID was not replayed with its exact original protected payload/version")
    need(old_call.get("status") == 200
         and old_call.get("body", {}).get("outcome") == "already-accepted"
         and old_call.get("body", {}).get("event_seq") == event.get("seq"),
         name + " exact old ID did not return its historical accepted result")
    need(record_bytes(historical.get("before"), name + " historical retry before")
         == record_bytes(historical.get("after"), name + " historical retry after"),
         name + " exact historical replay appended journal bytes")


def validate_two_worker_seam(case):
    name = "worker-seam"
    need(case.get("case_kind") == name, "two-worker fixture identity missing")
    writes = case.get("writes")
    need(isinstance(writes, list) and len(writes) == 2,
         "two distinct mediated worker writes are required")
    ids = [item.get("request_id") for item in writes]
    pids = [item.get("worker_pid") for item in writes]
    need(len(set(ids)) == 2 and all(isinstance(value, str) and value for value in ids),
         "worker requests must use distinct fresh IDs")
    need(len(set(pids)) == 2 and all(type(value) is int for value in pids),
         "requests must come from distinct worker processes")
    need(len(case.get("controller_forwarded_operations", [])) == 2,
         "exactly two writes reached the UID-2000 controller")

    start = case.get("owner_start_snapshot")
    start_owner = owner_snapshot(start, name + " initial")
    start_native = start_owner["state"]["native_owner"]
    need(start_native.get("effects") == {}, "fresh worker-seam owner already has effects")
    need(record_bytes(start.get("journal"), name + " initial journal") == b"",
         "worker-seam journal was not empty before the first worker")

    envelopes = []
    expected_prior = b""
    for item in writes:
        label = item["label"]
        request_id = item["request_id"]
        expected_shape = {"op": "write", "payload": request_id}
        need(item.get("request_shape") == expected_shape,
             label + " request shape differs from the fixed D-write interface")
        route = item.get("route", {})
        need(route.get("input", {}).get("request") == expected_shape,
             label + " worker did not emit the recorded request shape")
        decision = route.get("driver_decision", {})
        frame = item.get("controller_frame", {})
        need(decision == frame and frame.get("event") == "RESPONSE"
             and frame.get("op") == "write",
             label + " owner response did not return through the mediated route")
        status_identity(item.get("worker_status_at_start"), 2001, label + " worker")
        final_process = case.get("worker_processes", {}).get(label, {})
        need(final_process.get("pid") == item["worker_pid"] and final_process.get("exit") == 0,
             label + " worker was not cleanly reaped")

        record = frame.get("worker_seam_write", {})
        need(record.get("request_id") == request_id
             and record.get("owner_request") == {"op": "read"},
             label + " manager owner-read input is missing or mismatched")
        owner_before = owner_snapshot(record.get("before", {}), label + " owner before")
        owner_after = owner_snapshot(record.get("after", {}), label + " owner after")
        before_native = owner_before["state"]["native_owner"]
        after_native = owner_after["state"]["native_owner"]
        need(before_native.get("selected") == after_native.get("selected") == start_native.get("selected")
             and before_native.get("epoch") == after_native.get("epoch") == start_native.get("epoch"),
             label + " owner selection or epoch changed during a mediated write")
        need(owner_before["state"].get("current_ingress") == owner_after["state"].get("current_ingress")
             == start_owner["state"].get("current_ingress"),
             label + " current ingress changed during a mediated write")

        envelope = record.get("envelope", {})
        envelopes.append(envelope)
        submission = record.get("f4_submission", {})
        request = submission.get("request", {})
        need(set(request) == {"authority_version", "request_id", "payload"}
             and request.get("authority_version") == 1
             and request.get("request_id") == request_id,
             label + " exact F4 owner input differs from the fixed current-write request")
        payload = json.loads(request.get("payload", "null"))
        need(payload == envelope and payload.get("request_id") == request_id,
             label + " F4 payload differs from the manager-derived current envelope")
        need(not ({"worker_pid", "execution_id", "attachment_id", "execution"} & set(payload)),
             label + " current envelope unexpectedly contains execution identity")
        response = submission.get("response", {})
        body = response.get("body", {})
        need(response.get("status") == 201
             and body.get("owner_effect", {}).get("status") == "published"
             and body.get("outcome") in ("accepted", "published"),
             label + " actual native effect was not accepted and published")

        before = record_bytes(submission.get("before"), label + " F4 journal before")
        after = record_bytes(submission.get("after"), label + " F4 journal after")
        need(before == expected_prior and len(after) > len(before),
             label + " did not append after the prior durable journal cut")
        events = [json.loads(line) for line in after.splitlines() if line]
        matching = [event for event in events
                    if event.get("event") == "effect_accepted" and event.get("request_id") == request_id]
        need(len(matching) == 1, label + " journal lacks one actual accepted event for its fresh ID")
        event = matching[0]
        need(body.get("event_seq") == event.get("seq")
             and body.get("owner_effect", {}).get("seq") == event.get("seq"),
             label + " owner result is not bound to the durable journal sequence")
        effect = after_native.get("effects", {}).get(request_id, {})
        need(effect.get("status") == "published" and effect.get("seq") == event.get("seq"),
             label + " owner readback does not retain the published effect")
        witness = record.get("after", {}).get("witness", {}).get("body", {}).get("current", {})
        need(witness.get("journal_sha256") == hashlib.sha256(after).hexdigest(),
             label + " durable append lacks the matching current witness cut")
        need(record.get("after", {}).get("f1", {}).get("integrity") == "ok",
             label + " F1 readback integrity is not okay")
        expected_prior = after

    need(all(set(envelope) == {"kind", "import_id", "epoch", "pair", "l5", "request_id"}
             for envelope in envelopes), "manager-derived envelope shape changed")
    need({key: value for key, value in envelopes[0].items() if key != "request_id"}
         == {key: value for key, value in envelopes[1].items() if key != "request_id"},
         "the two workers were not evaluated against the same current authority inputs")
    final = owner_snapshot(case.get("owner_final_snapshot", {}), name + " final")
    final_effects = final["state"]["native_owner"].get("effects", {})
    need(all(final_effects.get(request_id, {}).get("status") == "published" for request_id in ids),
         "final durable owner readback does not contain both published IDs")
    return {"case": name, "distinct_worker_processes": 2,
            "distinct_published_effects": 2,
            "execution_specific_authority": "not represented by captured request/envelope"}


def check_outer(outer):
    need(isinstance(outer, dict), "bounded Docker outer record missing")
    base_id = "sha256:b5ba49a53a9c5ad0d0fc3c2c925773589e0d8912cd8077eca91af0bb4ab5e335"
    need(outer.get("image_id") == base_id, "container did not use pinned #27 image")
    image = outer.get("image", {})
    need(image.get("Id") == base_id and image.get("Size") == 119614344
         and image.get("GraphDriver") == "vfs", "base image identity/size/storage changed")
    need(outer.get("docker_socket") == "unix:///var/run/docker.sock",
         "runner did not select the explicit local Docker socket")
    constraints = outer.get("container_constraints", {})
    need(constraints.get("network") == "none" and constraints.get("cpus") == 1
         and constraints.get("memory") == "512m" and constraints.get("pids_limit") == 32
         and constraints.get("cap_drop") == ["ALL"]
         and set(constraints.get("cap_add", [])) == {"CHOWN", "DAC_OVERRIDE", "SETUID", "SETGID"}
         and constraints.get("no_new_privileges") is True
         and constraints.get("mounts") == [] and constraints.get("ports") == [],
         "container constraints differ from the frozen UID route")
    need(outer.get("runner_status") == "PASS", "bounded runner did not complete")
    need(outer.get("source_commit_verified") is True,
         "runner did not verify staged files against the pinned source commit")
    commands = outer.get("docker_commands", [])
    need(isinstance(commands, list) and commands, "raw Docker command log missing")
    argv_list = [item.get("argv", []) for item in commands]
    for argv in argv_list:
        need(argv[:2] == ["docker", "--host=unix:///var/run/docker.sock"],
             "Docker command escaped the explicit local socket")
        need(item_success(commands[argv_list.index(argv)]), "Docker command failed")
        need(not any(arg in ("--privileged", "--mount", "--volume", "-v", "--publish", "-p")
                     or arg.startswith(("--mount=", "--volume=", "--publish=")) for arg in argv),
             "unexpected mount/publication/privileged Docker option")
    flat = [arg for argv in argv_list for arg in argv]
    need(not any(("build" in argv or "pull" in argv) for argv in argv_list),
         "runner built or pulled an image")
    need(sum(1 for argv in argv_list if "container" in argv and "create" in argv) == 1
         and sum(1 for argv in argv_list if len(argv) > 2 and argv[2] == "cp") == 1
         and sum(1 for argv in argv_list if len(argv) > 2 and argv[2] == "start") == 1,
         "runner did not use one create/copy/start container lifecycle")
    create = next(argv for argv in argv_list if "create" in argv)
    for flag in ("--network=none", "--cpus=1", "--memory=512m", "--pids-limit=32",
                 "--cap-drop=ALL", "--cap-add=CHOWN", "--cap-add=DAC_OVERRIDE",
                 "--cap-add=SETUID", "--cap-add=SETGID", "--security-opt=no-new-privileges"):
        need(flag in create, "container create omitted " + flag)
    need(outer.get("container_id") and outer.get("label_value") == outer.get("container_name")
         and outer.get("label_key") == "org.ases4.uid-recovery-task",
         "unique task container label/identity missing")
    inspection = outer.get("container_inspection", {})
    need(inspection.get("Id", "").startswith(outer["container_id"])
         and inspection.get("label") == outer.get("label_value")
         and inspection.get("State", {}).get("ExitCode") == 0,
         "actual container exit/label inspection did not pass")
    cleanup = outer.get("cleanup", {})
    need(cleanup.get("exit") == 0, "exact task container cleanup failed")
    preflight = outer.get("cleanup_preflight_inspection", {})
    try:
        preflight_item = json.loads(preflight.get("stdout", ""))[0]
    except (json.JSONDecodeError, IndexError, TypeError):
        preflight_item = {}
    labels = preflight_item.get("Config", {}).get("Labels", {}) or {}
    need(preflight.get("exit") == 0
         and preflight_item.get("Id") == outer.get("container_id")
         and preflight_item.get("Name", "").lstrip("/") == outer.get("container_name")
         and labels.get(outer.get("label_key")) == outer.get("label_value"),
         "cleanup did not recheck the exact container ID/name/unique label")
    need(outer.get("start_attach", {}).get("exit") == 0,
         "container start/attach did not complete successfully")
    commit = outer.get("source_commit", "")
    need(re.fullmatch(r"[0-9a-f]{40}", commit) is not None, "source commit pin missing")
    staged = outer.get("staged_sources", {})
    required = {
        "docs/research/phase-ii-native-publication-reconcile/reconcile.py",
        "docs/research/phase-ii-native-local-observation/observe_local.py",
        "docs/research/phase-ii-native-local-observation/test_sink_gate.py",
        "docs/research/phase-ii-native-recovery-uid/fixture/driver.py",
        "docs/research/phase-ii-native-recovery-uid/fixture/owner_controller.py",
        "docs/research/phase-ii-native-recovery-uid/fixture/worker.py",
    }
    need(required <= set(staged), "staged runtime source manifest incomplete")
    repo = Path(__file__).resolve().parents[3]
    for source_path, metadata in staged.items():
        need(source_path.startswith("docs/research/") and ".." not in Path(source_path).parts,
             "unexpected staged source path")
        need(metadata.get("mode") == "0644" and metadata.get("container_uid") == 0
             and metadata.get("container_gid") == 0, "runtime source mode/owner differs")
        source = subprocess.run(["git", "show", commit + ":" + source_path], cwd=repo,
                                capture_output=True, check=True).stdout
        need(hashlib.sha256(source).hexdigest() == metadata.get("sha256")
             and len(source) == metadata.get("size"), "staged source hash mismatch: " + source_path)


def item_success(command):
    return command.get("exit") == 0


def check(raw):
    need(isinstance(raw, dict) and raw.get("status") == "PASS", "native recovery driver did not pass")
    need(set(raw.get("cases", {})) == {"local", "reserved", "worker_seam"},
         "native recovery histories and two-worker seam case are required")
    check_outer(raw.get("outer"))
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
        event = validate_initial_effect(case, name)
        validate_recovery(case, name)
        validate_transition_and_history(case, name, event)
    worker_seam = validate_two_worker_seam(raw["cases"]["worker_seam"])
    return {"status": "PASS", "checked_cases": ["local", "reserved", "worker_seam"],
            "checked_direct_worker_audits": 2, "worker_seam": worker_seam}


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
