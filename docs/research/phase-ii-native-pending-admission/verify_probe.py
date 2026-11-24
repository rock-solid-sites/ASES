#!/usr/bin/env python3
"""Source-bound admission checks using the real native owner and F4 fixture."""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "phase-ii-native-ownership"))
sys.path.insert(0, str(HERE))
import baseline_probe as baseline
import probe


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def source_hashes():
    paths = [HERE.parent / "phase-ii-native-ownership/native_owner.py",
             HERE.parent / "phase-ii-native-ownership/native_sink.py",
             REPO / "docs/research/phase-i-effect-admission/admission.py",
             REPO / "docs/research/phase-i-effect-admission/admission_sink.py"]
    return {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def read_owner(root):
    frame, _ = baseline.owner_read(root)
    return frame["reply"]["snapshot"]["state"]["native_owner"]


def guarded_eof(f4, owner_root, request_id):
    envelope, before, _ = baseline.refresh_envelope(owner_root, request_id)
    journal = probe.native.blob(f4.journal)
    witness = f4.witness_call("/status")
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(f4.submit, envelope)
        gate = json.loads(f4.sink.read(timeout=15))
        need(gate.get("event") == "GATE" and gate.get("stage") == "guarded", "A1: real guarded gate missing")
        f4.sink.p.stdin.close()
        response = future.result(timeout=15)
    owner = read_owner(owner_root)
    event = owner["effects"].get(request_id)
    need(event is not None and event["status"] == "reserved" and "seq" not in event,
         "A1: guarded EOF did not retain exactly the unresolved reservation")
    need(probe.native.blob(f4.journal)["sha256"] == journal["sha256"], "A1: journal changed before append")
    witness_after = f4.witness_call("/status")
    need(witness_after["body"]["current"] == witness["body"]["current"] and
         witness_after["body"]["revision"] == witness["body"]["revision"], "A1: witness cut changed")
    need(response["response"]["body"].get("outcome") == "native-effect-requires-reconciliation",
         "A1: uncertainty response was not preserved")
    return {"request_id": request_id, "envelope": envelope, "owner_before": before,
            "gate": gate, "response": response, "effect_after": event,
            "journal_before": journal, "journal_after": probe.native.blob(f4.journal),
            "witness_before": witness, "witness_after": witness_after}


def case_pending_bound(out):
    fx = baseline.fixture(out, "a1-a3", gate=True)
    aid = fx["witness_root"] + ":A"
    bids = [fx["witness_root"] + ":B", fx["witness_root"] + ":C"]
    case = {"a1": guarded_eof(fx["f4"], fx["owner_root"], aid)}
    case["old_sink_stopped"] = fx["f4"].sink.close(True)
    case["cold_ready"] = fx["f4"].cold_restart()
    case["reopen"] = [fx["f4"].call("/replace", {"holder": "pending-admission-test"}),
                      fx["f4"].call("/activate", {"authority_version": 2})]
    before = {"owner": read_owner(fx["owner_root"]),
              "journal": probe.native.blob(fx["f4"].journal),
              "witness": fx["f4"].witness_call("/status"),
              "f1": probe.f1_raw(Path(fx["prepared"]["f1_root"]) / "store.sqlite"),
              "l6": probe.tree(Path(fx["owner_root"]) / "protected")}
    replies = []
    for request_id in bids:
        envelope, _, _ = baseline.refresh_envelope(fx["owner_root"], request_id)
        replies.append(fx["f4"].submit(envelope, authority_version=2))
    after = {"owner": read_owner(fx["owner_root"]),
             "journal": probe.native.blob(fx["f4"].journal),
             "witness": fx["f4"].witness_call("/status"),
             "f1": probe.f1_raw(Path(fx["prepared"]["f1_root"]) / "store.sqlite"),
             "l6": probe.tree(Path(fx["owner_root"]) / "protected")}
    need(all(r["response"]["status"] == 409 and
             r["response"]["body"].get("outcome") == "admission-denied" and
             r["response"]["body"].get("local_control_committed") is False and
             "pending" in r["response"]["body"].get("reason", "") for r in replies),
         "A2/A3: fresh IDs were not truthfully denied before reservation")
    need(set(before["owner"]["effects"]) == {aid} == set(after["owner"]["effects"]),
         "A2/A3: pending effects grew on rejected IDs")
    need(before["owner"]["selected"] == after["owner"]["selected"] and
         before["journal"] == after["journal"] and
         before["witness"]["body"]["current"] == after["witness"]["body"]["current"] and
         before["witness"]["body"]["revision"] == after["witness"]["body"]["revision"] and
         before["f1"] == after["f1"] and before["l6"] == after["l6"],
         "A2: rejected admission mutated protected readbacks")
    case.update({"before_rejections": before, "replies": replies, "after_rejections": after})
    fx["f4"].close(True)
    return case


def case_sequential(out):
    fx = baseline.fixture(out, "a4-sequential", gate=False)
    ids = [fx["witness_root"] + ":A", fx["witness_root"] + ":B"]
    replies = []
    for request_id in ids:
        envelope, _, _ = baseline.refresh_envelope(fx["owner_root"], request_id)
        replies.append(fx["f4"].submit(envelope))
    owner = read_owner(fx["owner_root"])
    events = [json.loads(line) for line in fx["f4"].journal.read_text().splitlines()]
    need(all(owner["effects"][i]["status"] == "published" for i in ids), "A4: sequential effects not published")
    need(len([event for event in events if event.get("event") == "effect_accepted"]) == 2,
         "A4: expected two distinct accepted journal events")
    fx["f4"].close(True)
    return {"ids": ids, "replies": replies, "effects": {i: owner["effects"][i] for i in ids},
            "journal_events": events}


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_probe.py OUTPUT_DIRECTORY")
    out = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=False)
    raw = {"schema": "ases4-native-pending-admission-verify-v1", "source_hashes": source_hashes(),
           "started_ns": time.monotonic_ns(), "status": "RUNNING", "cases": {}}
    try:
        raw["cases"]["A1-A3"] = case_pending_bound(out)
        raw["cases"]["A4"] = case_sequential(out)
        raw["status"] = "PASS"
    except BaseException as error:
        raw["status"] = "FAIL"
        raw["failure"] = {"type": type(error).__name__, "message": str(error)}
        raise
    finally:
        raw["finished_ns"] = time.monotonic_ns()
        (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": raw["status"], "raw": str(out / "raw.json")}, sort_keys=True))


if __name__ == "__main__":
    main()
