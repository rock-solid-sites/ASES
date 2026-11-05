#!/usr/bin/env python3
"""Experimental event-by-event refinement of selected F1/F3 probe histories.

Reads source-specific raw process evidence but NEVER imports source-specific
check.py. Maintains small independent abstract states at observed linearization
boundaries. Includes adversarial history edits; finite traces are not proof of
all possible implementation executions.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path


class BadTrace(Exception):
    pass


def need(condition, reason):
    if not condition:
        raise BadTrace(reason)


def decode(snapshot, field="raw_hex", digest="sha256"):
    need(isinstance(snapshot, dict), "missing raw snapshot")
    try:
        raw = bytes.fromhex(snapshot[field])
        need(hashlib.sha256(raw).hexdigest() == snapshot[digest], "raw digest mismatch")
        return raw
    except (KeyError, TypeError, ValueError) as exc:
        raise BadTrace("missing/invalid raw bytes") from exc


def steps_log():
    log = []
    def add(event, detail):
        log.append({"step": len(log) + 1, "event": event, "abstract": detail})
    return log, add


def f1_history(c):
    log, add = steps_log()
    boot = c["bootstrap"]["calls"]
    need(len(boot) == 2 and [b["request"]["kind"] for b in boot] == ["establish", "grant"],
         "bootstrap event identity")
    for i, event in enumerate(boot):
        need(event["start_ns"] < event["end_ns"], "bootstrap interval")
        if i:
            need(boot[i-1]["end_ns"] < event["start_ns"], "bootstrap operation reordering")
        need(event["response"]["outcome"] == "commit", "bootstrap not accepted")
        add("bootstrap_" + event["request"]["kind"],
            {"content": event["response"]["state"]["content"],
             "evidence": event["response"]["consumer_query"]["required"]})
    old = boot[-1]["response"]["consumer_query"]
    content = old["accepted_content"]
    binding = {"accepted_content": content, "required": old["required"]}
    need(old["status"] == "available", "initial evidence unavailable")
    writer = c["writer"]
    accept = c["accept"]
    need(boot[-1]["end_ns"] < writer["start_ns"] < writer["ready_ns"] <
         accept["start_ns"] < accept["end_ns"] < writer["exit_ns"], "writer/accept lifecycle")
    need(accept["request"]["kind"] == "accept", "incorrect accepted-operation identity")
    new_content = accept["request"]["value"]
    new_binding = {"accepted_content": new_content,
                   "required": c["declared_original_observations"]}
    add("writer_ready", {"content": content, "binding": binding})
    tx = False
    update = False
    insert = False
    pending_content = None
    pending_binding = None
    commits = 0
    nupdate = ninsert = 0
    prior_end = accept["start_ns"]
    for e in c["writer_trace"]:
        need(e["pid"] == writer["pid"], "SQL entry from wrong process")
        need(prior_end < e["start_ns"] < e["end_ns"] < writer["exit_ns"],
             "SQL event reordered, duplicated or outside writer lifetime")
        prior_end = e["end_ns"]
        op = e["sql"]
        if op == "BEGIN":
            need(not tx and e["in_transaction"] is True, "nested/invalid BEGIN")
            tx = True
            update = insert = False
            pending_content = pending_binding = None
        elif op == "UPDATE":
            need(tx and not update and e["in_transaction"] is True, "invalid UPDATE")
            nupdate += 1
            update = True
            pending_content = new_content
        elif op == "INSERT":
            need(tx and not insert and e["in_transaction"] is True, "invalid INSERT")
            ninsert += 1
            insert = True
            pending_binding = new_binding
        elif op == "COMMIT":
            need(tx and e["in_transaction"] is False, "COMMIT without transaction")
            need(update or insert, "empty write transaction")
            if update:
                content = pending_content
            if insert:
                binding = pending_binding
            tx = False
            commits += 1
        else:
            raise BadTrace("unexpected SQL operation: " + str(op))
        add("sqlite_" + op.lower(), {"content": content, "binding": binding,
                                      "in_transaction": tx, "pending_update": update if tx else False,
                                      "pending_insert": insert if tx else False})
    need(nupdate == 1, "expected single protected content UPDATE")
    need(commits <= 2 and ninsert <= 1, "unexpected write count")
    gate = c["gate"]
    if gate is not None:
        need(writer["exit"] == -9 and gate["pid"] == writer["pid"] and
             gate["raw_hex"] == "47" and gate["stage"] in ("prepared", "durable") and
             prior_end < gate["observed_ns"] < writer["exit_ns"],
             "process cut not backed by gate/kill order")
        need(accept["response"] is None and bool(accept.get("error")), "claimed no ACK contradicted")
        if gate["stage"] == "prepared":
            need(tx and commits == 0, "prepared cut after durable commit")
        else:
            need(commits >= 1 and not tx, "durable cut before commit/inside transaction")
        add("actual_sigkill", {"stage": gate["stage"], "commits": commits})
    else:
        need(not tx and accept["response"]["outcome"] == "commit" and
             accept["response"]["consumer_query"]["accepted_content"] == new_content and
             commits >= 1, "accepted ACK without complete write")
        add("ack_delivered", {"content": content, "binding": binding})
    # Crash destroys uncommitted staging but cannot erase a successful SQLite commit.
    if tx:
        add("rollback_uncommitted_sql", {"content": content, "binding": binding})
    need(writer["exit_ns"] < c["recovered"]["start_ns"] <
         c["recovered_query"]["start_ns"] < c["recovered_query"]["end_ns"] <
         c["independent_reader"]["start_ns"], "recovery/independent reader order")
    raw = c["independent_reader"]["observation"]
    view = json.loads(decode({"raw_hex": raw["view_utf8_hex"], "sha256": raw["view_sha256"]}))
    stored = json.loads(decode({"raw_hex": raw["observation_utf8_hex"],
                                "sha256": raw["observation_sha256"]}))
    need(raw["integrity"] == "ok" and
         c["independent_reader"]["exit"] == 0 and
         view == raw["view"] == c["recovered_query"]["response"]["state"],
         "independent reader does not match recovered raw view")
    query = c["recovered_query"]["response"]["consumer_query"]
    need(view["content"] == content == query["accepted_content"],
         "recovered content not equal to committed abstract content")
    need(stored == binding, "stored opaque evidence differs from committed abstract binding")
    need("observations" not in c["recovered"]["config"],
         "recovered process supplied original acceptance evidence")
    paired = (binding["accepted_content"] == content)
    if paired:
        need(query["status"] == "available" and query["required"] == binding["required"],
             "accepted paired evidence not available")
    else:
        need(query["status"] == "incompatible_required_observations" and
             query["required"] is None, "split commit was hidden")
    if gate is None:
        need(paired and binding == new_binding, "ACK despite missing content/evidence pair")
    add("recovery_read", {"content": content, "binding": binding,
                          "status": query["status"], "paired": paired})
    return {"verdict": "CONSISTENT" if paired else "COUNTEREXAMPLE",
            "steps": log, "counterexample": None if paired else "split-content-and-opaque-evidence-commit"}


def selected_state(snapshot):
    files = snapshot["files"]
    selected = snapshot["selected"]
    need(selected in files and "CURRENT" in files, "selected/current record missing")
    need(decode(files["CURRENT"]).decode().strip() == selected, "CURRENT disagrees with selected")
    state = json.loads(decode(files[selected]))
    need(state == snapshot["state"], "selected record differs from decoded state")
    return state


def l5_history(c):
    log, add = steps_log()
    ch = c["children"]
    need(len(ch) == 2, "expected writer and cold reader processes")
    old = c["before"]
    after = c["after_process"]
    initial = selected_state(old)
    need(old["ns"] < ch[0]["start_ns"] < ch[0]["ready_ns"] < ch[0]["exit_ns"] <
         after["ns"] < ch[1]["start_ns"] < ch[1]["ready_ns"] <
         c["activation"]["start_ns"] < c["activation"]["end_ns"] <
         c["write"]["start_ns"] < c["write"]["end_ns"] < ch[1]["exit_ns"],
         "move/recovery/activation/write history not serializable")
    need(initial["work_units"]["C"]["parent"] == "P", "not an original P-root starting state")
    add("old_selected", {"selected": old["selected"], "parent_c": "P"})
    move = c.get("move_observation")
    if move is not None:
        need(move in ch[0]["events"], "move event absent from observed child transcript")
        frame = move["frame"]
        need(frame["pid"] == ch[0]["pid"], "move event wrong process")
        if frame["event"] == "GATE":
            need(ch[0]["exit"] == -9 and ch[0]["ready_ns"] <
                 frame["ns"] < ch[0]["exit_ns"], "gated move process was not killed")
            gate_state = selected_state(frame["snapshot"])
            need(gate_state["work_units"]["C"]["parent"] in ("P", "Q"),
                 "invalid gate selector")
            add("move_gate_then_kill", {"selected": frame["snapshot"]["selected"]})
        else:
            need(frame["event"] == "RESPONSE" and
                 frame["result"]["reply"]["result"] == "COMMITTED",
                 "ungated move was not accepted")
            add("move_ack", {"result": "COMMITTED"})
    actual = selected_state(after)
    need(actual["work_units"]["C"]["parent"] in ("P", "Q"), "invalid post-loss parent")
    for name, info in old["files"].items():
        if name.startswith("objects/"):
            need(name in after["files"] and after["files"][name]["sha256"] == info["sha256"],
                 "accepted object lost across move")
    moved = actual["work_units"]["C"]["parent"] == "Q"
    if moved:
        need(actual["work_units"]["D"]["parent"] == "C", "descendant no longer under C")
    else:
        need(actual == initial, "old-selector recovery changed old record")
    add("cold_selected", {"selected": after["selected"], "parent_c": "Q" if moved else "P"})
    cold = c["cold_ready"]
    need(cold in ch[1]["events"] and cold["frame"]["event"] == "READY" and
         cold["frame"]["snapshot"]["state"] == actual and
         cold["frame"]["snapshot"]["selected"] == after["selected"],
         "cold process failed to reconstruct selected record")
    add("cold_ready", {"selected": after["selected"]})
    activation = c["activation"]
    write = c["write"]
    need(activation in ch[1]["events"] and write in ch[1]["events"],
         "activation/write response absent from child transcript")
    need(activation["frame"]["event"] == write["frame"]["event"] == "RESPONSE" and
         activation["frame"]["request"]["op"] == "activate" and
         write["frame"]["request"]["op"] == "write" and
         activation["frame"]["result"]["reply"]["result"] == "COMMITTED",
         "activation/write event identity")
    activated = activation["frame"]["snapshot"]
    active_state = selected_state(activated)
    need(active_state["events"] == actual["events"] +
         [active_state["events"][-1]] and
         active_state["events"][-1]["op"] == "separately-authorized_activation",
         "activation was not a separately authorized event")
    need(active_state["work_units"]["C"]["parent"] == actual["work_units"]["C"]["parent"],
         "activation altered move target")
    need(activation["frame"]["result"]["reply"]["record"] == activated["selected"] and
         activation["frame"]["result"]["reply"]["record_sha256"] ==
         activated["files"][activated["selected"]]["sha256"],
         "activation receipt not bound to published selected bytes")
    add("activation_published", {"selected": activated["selected"],
                                 "parent_c": active_state["work_units"]["C"]["parent"]})
    observed = write["frame"]["snapshot"]
    need(selected_state(observed) == active_state and
         observed["selected"] == activated["selected"],
         "write state differs from activated state")
    need(write["frame"]["result"]["reply"]["allowed"] is
         ("write" in observed["permissions"]["D"]), "D write result inconsistent with observed rights")
    allowed = write["frame"]["result"]["reply"]["allowed"]
    need((observed["effect_raw_hex"] is not None) == allowed, "effect materialization mismatches decision")
    need(c["final"]["effect_raw_hex"] == observed["effect_raw_hex"] and
         c["final"]["selected"] == observed["selected"] and
         selected_state(c["final"]) == active_state, "final effect/recovery state disagrees")
    add("D_write", {"allowed": allowed, "effect": observed["effect_raw_hex"] is not None})
    ceiling_safe = (not moved or
                    (actual["work_units"]["C"].get("latent_ceiling") == ["read"] and
                     actual["work_units"]["D"].get("latent_ceiling") == ["read"]))
    counterexample = moved and (not ceiling_safe or allowed)
    return {"verdict": "COUNTEREXAMPLE" if counterexample else "CONSISTENT",
            "counterexample": "selected-half-move-and-authorized-dependent-write" if counterexample else None,
            "steps": log}


def validate_sql(event):
    timeline = event["sql_trace"]
    require_ = need
    require_(isinstance(timeline, list), "missing SQL timeline")
    prev = -1
    for entry in timeline:
        require_(isinstance(entry["ns"], int) and entry["ns"] > prev,
                 "SQL statement timeline not strictly ordered")
        prev = entry["ns"]
    return [entry["sql"] for entry in timeline]


def matching_child_event(c, frame):
    return any(event.get("frame") == frame for child in c["children"]
               for event in child.get("events", []))


def l6_history(c):
    log, add = steps_log()
    final = c["final_before_exit"]
    need(final["integrity_check"] == "ok", "final SQLite integrity check failed")
    for name, file in final["files"].items():
        need(len(decode(file)) == file["size"], "physical file size inconsistent")
        need(any(d["name"] == name and d["sha256"] == file["sha256"]
                 and d["disposed"] == 0 for d in final["dependencies"]),
             "physical file without durable dependency")
    add("initial_inventory", {"live": True, "dependency": False})
    removal = c["removal"]["frame"]
    need(matching_child_event(c, removal), "removal response not in child transcript")
    removal_sql = validate_sql(removal)
    if c["kind"] == "creator-first":
        creator = c["creator_ack"]["frame"]
        need(matching_child_event(c, creator), "creator ACK not in transcript")
        create_sql = validate_sql(creator)
        need(creator["end_ns"] < removal["start_ns"], "creator first precedence lost")
        need("BEGIN IMMEDIATE" in create_sql and "COMMIT" in create_sql,
             "creator ACK without SQLite commit")
        need(creator["reply"]["result"] == "COMMITTED", "creator ACK altered")
        need(creator["snapshot"]["live"] and creator["snapshot"]["dependencies"],
             "creator checkpoint lacks accepted dependency")
        add("creator_commit", {"live": True, "dependency": True})
        need(removal["reply"]["result"] == "DENY" and "ROLLBACK" in removal_sql,
             "prior dependent object did not block remove")
        need(final["live"] and bool(final["dependencies"]), "creator-first lost dependency")
        add("removal_refused", {"live": True, "dependency": True})
        verdict = "CONSISTENT"
    else:
        gate = c["gate"]["frame"]
        creator = c["creator_attempt"]["frame"]
        need(matching_child_event(c, c["gate"]["frame"]) and
             matching_child_event(c, creator), "gated competing operation missing transcript")
        create_sql = validate_sql(creator)
        need(gate["ns"] < creator["start_ns"] < creator["end_ns"] < removal["end_ns"],
             "creator/removal overlap precedence lost")
        need(gate["local_dependency_rows"] == 0, "inventory scan not empty at gate")
        need(removal["reply"]["result"] == "COMMITTED" and "COMMIT" in removal_sql,
             "removal did not actually commit")
        guarded = gate["in_transaction"] is True
        add("scan_empty", {"lock_held": guarded})
        if guarded:
            need("BEGIN IMMEDIATE" in removal_sql and
                 "BEGIN IMMEDIATE" in create_sql and "COMMIT" not in create_sql and
                 creator["reply"]["result"] == "DENY" and
                 creator["reply"]["sqlite_errorcode"] == 5 and
                 creator["reply"]["sqlite_errorname"] == "SQLITE_BUSY",
                 "guarded writer not denied by SQLite contention")
            add("creator_busy", {"dependency": False, "lock_held": True})
            need(not final["live"] and not final["files"] and not final["dependencies"],
                 "guarded removal stranded object")
            verdict = "CONSISTENT"
        else:
            need("BEGIN IMMEDIATE" not in validate_sql(gate) and
                 "BEGIN IMMEDIATE" in create_sql and "COMMIT" in create_sql and
                 creator["reply"]["result"] == "COMMITTED", "detached creator did not commit")
            add("creator_commit", {"dependency": True, "lock_held": False})
            need(not final["live"] and final["files"] and final["dependencies"],
                 "expected detached counterexample absent")
            verdict = "COUNTEREXAMPLE"
        add("remove_commit", {"live": False, "dependency": bool(final["dependencies"])})
        need(c["kind"] == ("guarded" if guarded else "detached"), "gate lock state/case mismatch")
        need(creator["snapshot"]["live"], "creator observation not live")
    need(removal["snapshot"]["live"] == final["live"] and
         removal["snapshot"]["files"] == final["files"] and
         removal["snapshot"]["dependencies"] == final["dependencies"],
         "removal snapshot differs from final observed state")
    return {"verdict": verdict,
            "counterexample": "detached-empty-scan-removal-with-stranded-dependency" if verdict == "COUNTEREXAMPLE" else None,
            "steps": log}


SPECS = {
    "f1": (f1_history, {"atomic-A", "atomic-B", "atomic-before", "split-ack", "split-gap"},
           {"split-gap"}),
    "l5": (l5_history, {"after_record", "after_selector", "before_record", "split-mutant",
                        "uninterrupted", "write-positive"}, {"split-mutant"}),
    "l6": (l6_history, {"creator-first", "detached", "guarded"}, {"detached"}),
}


def mutations(kind, cases):
    """Planted invalid histories; all must be rejected, not merely reclassified."""
    positives = {"f1": "atomic-A", "l5": "after_selector", "l6": "guarded"}
    base = cases[positives[kind]]
    specimens = []
    if kind == "f1":
        specimens = [
            ("missing_SQL_commit", lambda x: x["writer_trace"].pop()),
            ("duplicate_SQL_update", lambda x: x["writer_trace"].insert(2, copy.deepcopy(x["writer_trace"][1]))),
            ("wrong_writer_pid", lambda x: x["writer_trace"][0].update(pid=-1)),
            ("wrong_recovery_content", lambda x: x["independent_reader"]["observation"]["view"].update(content="forged")),
            ("premature_ACK", lambda x: x["accept"].update(response={"outcome":"commit"})),
            ("reordered_bootstrap", lambda x: x["bootstrap"]["calls"].reverse()),
        ]
    elif kind == "l5":
        specimens = [
            ("missing_move_transcript", lambda x: x["children"][0]["events"].pop()),
            ("selector_not_selected_raw", lambda x: x["after_process"].update(selected="record-000001.json")),
            ("cold_reconstruction_mismatch", lambda x: x["cold_ready"]["frame"]["snapshot"].update(selected="bad")),
            ("write_before_activation", lambda x: x["write"].update(start_ns=x["activation"]["start_ns"])),
            ("unauthorized_D_write", lambda x: x["write"]["frame"]["result"]["reply"].update(allowed=True)),
            ("missing_activation_event", lambda x: x["children"][1]["events"].pop(1)),
        ]
    else:
        specimens = [
            ("gate_lock_bypass", lambda x: x["gate"]["frame"].update(in_transaction=False)),
            ("missing_creator_transcript", lambda x: x["children"][1]["events"].pop(1)),
            ("SQL_commit_forgery", lambda x: x["creator_attempt"]["frame"]["sql_trace"].append(
                {"ns":x["creator_attempt"]["frame"]["end_ns"]+1, "sql":"COMMIT"})),
            ("creator_before_scan", lambda x: x["creator_attempt"]["frame"].update(start_ns=0)),
            ("stranded_guarded_dependency", lambda x: x["final_before_exit"]["dependencies"].append(
                {"name":"z","sha256":"0"*64,"disposed":0})),
            ("removal_not_committed", lambda x: x["removal"]["frame"]["reply"].update(result="DENY")),
        ]
    checks = []
    checker = SPECS[kind][0]
    for label, transform in specimens:
        case = copy.deepcopy(base)
        transform(case)
        try:
            checker(case)
        except (BadTrace, KeyError, TypeError, ValueError, IndexError):
            checks.append({"mutation": label, "outcome": "REJECTED"})
        else:
            raise BadTrace("invalid history escaped: " + label)
    return checks


def audit(kind, data):
    checker, expected, counterexamples = SPECS[kind]
    need(set(data["cases"]) == expected, "case set changed")
    histories = {}
    for name, value in sorted(data["cases"].items()):
        observed = checker(value)
        need(observed["verdict"] == ("COUNTEREXAMPLE" if name in counterexamples else "CONSISTENT"),
             "unexpected history verdict: " + name)
        histories[name] = observed
    negative_controls = mutations(kind, data["cases"])
    need(len(negative_controls) == 6, "mutation coverage changed")
    return {"case_family": kind, "histories": histories,
            "invalid_history_controls": negative_controls,
            "qualification": "selected event-by-event observed history mapping, source pinned; not universal refinement proof"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True, choices=tuple(SPECS))
    parser.add_argument("--raw", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.case, json.loads(args.raw.read_text())),
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
