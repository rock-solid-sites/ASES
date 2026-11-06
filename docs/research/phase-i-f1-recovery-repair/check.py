#!/usr/bin/env python3
"""Read-only independent contract checker. Never imports service acceptance logic."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

FIELDS = {"identity_genesis", "created_by", "project", "consumer_evidence"}
A, B = "accepted\x00one\n", "accepted\x00zero\n"


def need(value, reason):
    if not value:
        raise ValueError(reason)


def key(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":"))


def validate_record(record):
    need(isinstance(record, dict) and set(record) == {"accepted_content", "required"}, "record shape")
    need(isinstance(record["accepted_content"], str), "content type")
    required = record["required"]
    need(isinstance(required, dict) and set(required) == FIELDS and
         all(isinstance(x, str) for x in required.values()), "opaque observations shape")


def rows(observation):
    need(observation["returncode"] == 0 and not observation["stderr"], "independent reader failed")
    snapshot = observation["snapshot"]
    need(json.loads(observation["stdout"]) == snapshot, "reader stdout differs")
    raw = bytes.fromhex(snapshot["raw_hex"])
    need(hashlib.sha256(raw).hexdigest() == snapshot["sha256"], "snapshot digest")
    decoded = json.loads(raw)
    need(decoded == snapshot["rows"] and decoded["integrity"] == "ok", "snapshot rows/integrity")
    return decoded


def accepted(state, require_history=False):
    need(state["kernel"][:3] == ["work", "independent", 1], "root/profile/schema")
    value = json.loads(state["kernel"][3])["content"]
    record = json.loads(state["observation"])
    validate_record(record)
    need(value == record["accepted_content"], "committed content/evidence are incompatible")
    retained = state["retained"]
    if retained is not None:
        records = [json.loads(s) for s in retained]
        for old in records:
            validate_record(old)
        need(len({key(x) for x in records}) == len(records), "duplicate retained pair")
        need(key(record) in {key(x) for x in records}, "current accepted pair not retained")
    else:
        need(not require_history, "missing retained observations")
    return record


def retention(before, after):
    retained = {key(json.loads(x)) for x in after["retained"]}
    need({key(json.loads(x)) for x in before["retained"]} <= retained, "previous accepted observations disappeared")


def outcome(operation, expected):
    need(operation["response"] is not None and operation["response"]["outcome"] == expected, "operation outcome: expected " + expected)


def check_case(label, case, mode):
    history = mode != "original"
    prefix = rows(case["prefix"]["independent"])
    accepted(prefix, history and not label.startswith("prepare-original") and label != "no-auto-prepare")
    final = rows(case["final"])
    if label in ("prepare-original-incompatible", "no-auto-prepare"):
        need(case["attempt"]["exit"] != 0, "unsupported recovery/preparation accepted")
        need(rows(case["before"]) == final, "refusal changed retained state")
        return dict(disposition="REFUSED_UNCHANGED")
    final_record = accepted(final, history)
    if history and prefix["retained"] is not None:
        retention(prefix, final)
    if label == "prepare-original-valid":
        before = rows(case["before"])
        need(case["attempt"]["exit"] == 0 and final["kernel"] == before["kernel"] and
             final["observation"] == before["observation"], "explicit preparation changed accepted pair")
        need({key(json.loads(x)) for x in final["retained"]} == {key(accepted(before))}, "preparation did not retain original pair")
        return dict(disposition="PREPARED_EXACT_ORIGINAL_PAIR")
    op = case["operation"]
    if label in ("cold-missing", "legacy-unbound", "same-content-invalid", "stale-subject") or label.startswith("invalid-"):
        outcome(op, "deny")
        before = rows(case["before"]) if label == "stale-subject" else prefix
        need(final == before, "denied acceptance changed rows")
    elif label == "readonly":
        outcome(op, "read")
        need(final == prefix, "read-only recovery changed rows")
    elif label == "unchanged":
        outcome(op, "commit")
        need(final == prefix, "unchanged reacceptance replaced evidence")
    elif label == "config-nonaccept":
        outcome(op, "commit")
        need(final["observation"] == prefix["observation"] and final["retained"] == prefix["retained"], "configuration rewrote accepted observations")
    elif label in ("cold-fresh", "failed-then-valid"):
        outcome(op, "commit")
        need(final_record["accepted_content"] == B and final_record["required"]["consumer_evidence"] == "B:consumer_evidence", "fresh accepted meaning differs")
        if label == "failed-then-valid":
            outcome(case["denied"], "deny")
            if case.get("after_denial") is not None:
                need(rows(case["after_denial"]) == prefix, "invalid input changed state")
            else:  # The earlier original capture predates the added intermediate reader.
                reply = case["denied"]["response"]
                need(reply["state"] == json.loads(prefix["kernel"][3]) and
                     reply["consumer_query"]["required"] == accepted(prefix)["required"], "invalid input reported changed state")
    elif label == "same-bytes-worlds":
        outcome(op, "commit")
        outcome(case["duplicate"], "commit")
        need(final_record["accepted_content"] == A and final_record["required"]["consumer_evidence"] == "C:consumer_evidence", "opaque world collapsed")
        need(final == rows(case["after_first"]), "duplicate/recovery lost or changed accepted pair")
        old_pairs = [json.loads(x) for x in final["retained"] if json.loads(x)["accepted_content"] == A]
        need(len(old_pairs) == 2, "same-byte evidence worlds not both retained")
        for recovery in case["recoveries"]:
            outcome(recovery["read"], "read")
            outcome(recovery["reaccept"], "commit")
    elif label.startswith("kill-"):
        need(op["response"] is None, "killed request got an ACK")
        if label == "kill-prepared":
            need(final == prefix, "uncommitted pair survived kill")
        else:
            need(final_record["accepted_content"] == B and final_record["required"]["consumer_evidence"] == "B:consumer_evidence", "committed pair lost after kill")
    elif label.startswith("fail-"):
        need(op["response"] is None and rows(case["after_operation"]) == prefix, "failed SQL changed authoritative pair")
        outcome(case["later_valid"], "commit")
        need(final_record["accepted_content"] == B, "valid acceptance failed after transaction rollback")
    else:
        raise ValueError("unclassified case " + label)
    return dict(disposition="CONTRACT_SATISFIED", retained_pairs=None if final["retained"] is None else len(final["retained"]))


def process_checks(data):
    for process in data["processes"]:
        need(process["start_ns"] < process["ready_ns"] < process["exit_ns"], "process lifecycle")
        sql = [e["sql"] for e in process["sql"]]
        gate = process.get("observed_gate")
        if gate:
            need(process["exit"] == -9 and gate["marker_hex"] == "47" and
                 process["ready_ns"] < gate["ns"] < process["exit_ns"], "actual kill gate evidence")
            need(("COMMIT" in sql) == (gate["stage"] == "durable"), "gate/commit order")
        if "injected-transaction-failure" in process["stderr"]:
            need("ROLLBACK" in sql and "COMMIT" not in sql, "failed SQL did not roll back")


def physical_readback(capture, data):
    checked = []
    for name, case in data["cases"].items():
        expected = rows(case["final"])
        path = capture / "state" / name / "store.sqlite"
        with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
            kernel = list(db.execute("SELECT root,profile,version,view FROM kernel WHERE id=1").fetchone())
            obs = db.execute("SELECT record FROM consumer_observations WHERE id=1").fetchone()[0]
            retained = [r[0] for r in db.execute("SELECT record FROM retained_observations ORDER BY record")] if expected["retained"] is not None else None
        need(kernel == expected["kernel"] and obs == expected["observation"] and retained == expected["retained"], "physical SQLite readback differs")
        checked.append(name)
    return checked


def rewrite_snapshot(observation, change):
    state = observation["snapshot"]["rows"]
    change(state)
    raw = json.dumps(state, sort_keys=True).encode()
    observation["snapshot"].update(raw_hex=raw.hex(), sha256=hashlib.sha256(raw).hexdigest())
    observation["stdout"] = json.dumps(observation["snapshot"], sort_keys=True) + "\n"


def controls(case):
    mutations = [
        ("lost-old-evidence", lambda c: rewrite_snapshot(c["final"], lambda s: s.update(retained=[key(json.loads(s["observation"]))]))),
        ("unbound-new-content", lambda c: rewrite_snapshot(c["final"], lambda s: s.update(observation=c["prefix"]["independent"]["snapshot"]["rows"]["observation"]))),
        ("swapped-opaque-world", lambda c: rewrite_snapshot(c["final"], lambda s: s.update(observation=key(dict(json.loads(s["observation"]), required={f: "A:" + f for f in FIELDS}))))),
        ("false-denial", lambda c: c["operation"]["response"].update(outcome="deny")),
        ("corrupt-snapshot", lambda c: c["final"]["snapshot"].update(sha256="0" * 64)),
    ]
    results = []
    for label, mutate in mutations:
        value = copy.deepcopy(case)
        mutate(value)
        try:
            check_case("cold-fresh", value, "repaired")
        except (ValueError, KeyError, TypeError) as error:
            results.append(dict(name=label, outcome="REJECTED", reason=str(error)))
        else:
            raise ValueError("invalid evidence control escaped: " + label)
    check_case("cold-fresh", case, "repaired")
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("capture", type=Path)
    parser.add_argument("--controls", action="store_true")
    args = parser.parse_args()
    data = json.loads((args.capture / "raw.json").read_text())
    need(data["execution"] == "PASS", "incomplete execution is not a contract result")
    failures, cases = {}, {}
    process_checks(data)
    for name, case in data["cases"].items():
        try:
            cases[name] = check_case(name, case, data.get("mode", "original"))
        except (ValueError, KeyError, TypeError) as error:
            failures[name] = str(error)
    result = dict(case_results=cases, contract_violations=failures, satisfies_tested_contract=not failures,
                  sqlite_readbacks=physical_readback(args.capture, data), oracle="independent rules; no repair import; same investigator, no clean-room claim")
    if args.controls:
        result["invalid_evidence_controls"] = controls(data["cases"]["cold-fresh"])
    print(json.dumps(result, sort_keys=True, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
