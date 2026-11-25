#!/usr/bin/env python3
"""Source-bound admission checks using the real native owner and F4 fixture."""
from __future__ import annotations

import concurrent.futures
import hashlib
import importlib.util
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

def load_publication_probe():
    path = REPO / "docs/research/phase-ii-native-publication-reconcile/probe.py"
    spec = importlib.util.spec_from_file_location("native_publication_probe", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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


def complete_readback(fx, ids):
    return baseline.readback(fx, ids)


def immutable_cut(before, after):
    before_native = before["owner"]["reply"]["snapshot"]["state"]["native_owner"]
    after_native = after["owner"]["reply"]["snapshot"]["state"]["native_owner"]
    return (before_native == after_native and before["owner_tree"] == after["owner_tree"] and
            before["f1"] == after["f1"] and before["journal"] == after["journal"] and
            before["witness"]["body"]["current"] == after["witness"]["body"]["current"] and
            before["witness"]["body"]["revision"] == after["witness"]["body"]["revision"])


def lifecycle_readback(fx):
    owner, owner_process = baseline.owner_read(fx["owner_root"])
    snapshot = owner["reply"]["snapshot"]
    inventory = snapshot["inventory"]
    inventory_cut = {key: inventory[key] for key in
                     ("dependencies", "files", "integrity_check", "live",
                      "objects_directory_exists", "reconstruction_status", "sealed", "unknown_files")}
    return {"owner": owner, "owner_process": owner_process,
            "owner_state": snapshot["state"], "owner_selector": snapshot["selector"],
            "owner_generation": snapshot["generation"], "owner_inventory_cut": inventory_cut,
            "owner_tree": probe.tree(Path(fx["owner_root"])),
            "f1": probe.f1_raw(Path(fx["prepared"]["f1_root"]) / "store.sqlite"),
            "l6_tree": probe.tree(Path(fx["owner_root"]) / "protected"),
            "journal": probe.native.blob(fx["f4"].journal),
            "witness": fx["f4"].witness_call("/status")}


def immutable_lifecycle_cut(before, after):
    return (before["owner_state"] == after["owner_state"] and
            before["owner_selector"] == after["owner_selector"] and
            before["owner_generation"] == after["owner_generation"] and
            before["owner_inventory_cut"] == after["owner_inventory_cut"] and
            before["owner_tree"] == after["owner_tree"] and
            before["f1"] == after["f1"] and before["l6_tree"] == after["l6_tree"] and
            before["journal"] == after["journal"] and
            before["witness"]["status"] == after["witness"]["status"] and
            before["witness"]["body"]["current"] == after["witness"]["body"]["current"] and
            before["witness"]["body"]["revision"] == after["witness"]["body"]["revision"])


def guarded_eof(fx, request_id, lifecycle_at_gate=False):
    f4 = fx["f4"]
    owner_root = fx["owner_root"]
    envelope, before, _ = baseline.refresh_envelope(owner_root, request_id)
    journal = probe.native.blob(f4.journal)
    witness = f4.witness_call("/status")
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(f4.submit, envelope)
        gate = json.loads(f4.sink.read(timeout=15))
        need(gate.get("event") == "GATE" and gate.get("stage") == "guarded", "A1: real guarded gate missing")
        owner_at_gate = read_owner(owner_root)
        lifecycle = None
        if lifecycle_at_gate:
            lifecycle_before = lifecycle_readback(fx)
            contender = probe.OwnerProcess(owner_root)
            try:
                refusal = contender.call({"op": "seal"})
                observed = contender.call({"op": "read"})
            finally:
                contender.close()
            native_after = observed["reply"]["snapshot"]["state"]["native_owner"]
            lifecycle_after = lifecycle_readback(fx)
            refusal_body = refusal.get("reply", {})
            need(refusal_body.get("result") == "DENY" and
                 refusal_body.get("error") == "OperationalError" and
                 refusal_body.get("reason") == "database is locked" and
                 refusal_body.get("owner_selection_changed") is False and
                 refusal_body.get("durable_phase_changed") is False,
                 f"lifecycle: seal was not denied specifically by the held owner/F1 guard: {refusal}")
            need(native_after == owner_at_gate,
                 "lifecycle: a refused concurrent transition altered the owner")
            need(immutable_lifecycle_cut(lifecycle_before, lifecycle_after),
                 "lifecycle: concurrent seal denial changed the full protected cut")
            lifecycle = {"owner_at_gate": owner_at_gate, "refusal": refusal,
                         "before": lifecycle_before, "observed": observed,
                         "after": lifecycle_after, "process": contender.meta}
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
            "owner_at_gate": owner_at_gate, "lifecycle_at_gate": lifecycle,
            "gate": gate, "response": response, "effect_after": event,
            "journal_before": journal, "journal_after": probe.native.blob(f4.journal),
            "witness_before": witness, "witness_after": witness_after}


def case_pending_bound(out):
    fx = baseline.fixture(out, "a1-a3", gate=True)
    aid = fx["witness_root"] + ":A"
    bid = fx["witness_root"] + ":B"
    cid = fx["witness_root"] + ":C"
    case = {"a1": guarded_eof(fx, aid, lifecycle_at_gate=True)}
    case["old_sink_stopped"] = fx["f4"].sink.close(True)
    case["cold_ready"] = fx["f4"].cold_restart()
    case["reopen"] = [fx["f4"].call("/replace", {"holder": "pending-admission-test"}),
                      fx["f4"].call("/activate", {"authority_version": 2})]
    same_a_before = complete_readback(fx, [aid])
    same_a_exact = fx["f4"].submit(case["a1"]["envelope"], authority_version=2)
    same_a_after_exact = complete_readback(fx, [aid])
    exact_body = same_a_exact["response"]["body"]
    need(same_a_exact["response"]["status"] == 409 and
         exact_body.get("outcome") == "admission-denied" and
         exact_body.get("reason") == "stale-native-selector" and
         exact_body.get("local_control_committed") is False,
         f"same-A exact retry did not preserve the recorded stale-selector denial: {same_a_exact}")
    need(immutable_cut(same_a_before, same_a_after_exact),
         "same-A exact retry after post-reservation failure changed the protected cut")
    refreshed_envelope, _, _ = baseline.refresh_envelope(fx["owner_root"], aid)
    need(refreshed_envelope != case["a1"]["envelope"] and
         refreshed_envelope["request_id"] == case["a1"]["envelope"]["request_id"] == aid and
         refreshed_envelope["l5"] != case["a1"]["envelope"]["l5"],
         "same-A refreshed retry did not use a distinct envelope with the current L5 selector")
    same_a_refreshed = fx["f4"].submit(refreshed_envelope, authority_version=2)
    same_a_after = complete_readback(fx, [aid])
    refreshed_body = same_a_refreshed["response"]["body"]
    need(same_a_refreshed["response"]["status"] == 503 and
         refreshed_body.get("outcome") == "native-effect-requires-reconciliation" and
         refreshed_body.get("reason") ==
         "native-effect-requires-reconciliation:native-effect-already-reserved" and
         "local_control_committed" in refreshed_body and
         refreshed_body["local_control_committed"] is None,
         f"same-A refreshed retry was not preserved as uncertainty: {same_a_refreshed}")
    need(immutable_cut(same_a_after_exact, same_a_after),
         "same-A refreshed retry after post-reservation failure changed the protected cut")
    need(same_a_after["effects"][aid] is not None and
         same_a_after["effects"][aid]["status"] == "reserved" and
         "seq" not in same_a_after["effects"][aid],
         "same-A retries after post-reservation failure changed the unresolved reservation")
    case["same_A_retry"] = {"exact_envelope": case["a1"]["envelope"],
                            "exact_response": same_a_exact, "before": same_a_before,
                            "after_exact": same_a_after_exact,
                            "refreshed_envelope": refreshed_envelope,
                            "refreshed_response": same_a_refreshed, "after": same_a_after}
    rejection_histories = []
    for label, request_id in (("fresh-B", bid), ("same-B-retry", bid), ("fresh-C", cid)):
        before = complete_readback(fx, [aid, bid, cid])
        envelope, _, _ = baseline.refresh_envelope(fx["owner_root"], request_id)
        response = fx["f4"].submit(envelope, authority_version=2)
        after = complete_readback(fx, [aid, bid, cid])
        body = response["response"]["body"]
        need(response["response"]["status"] == 409 and body.get("outcome") == "admission-denied" and
             body.get("local_control_committed") is False and "pending" in body.get("reason", ""),
             f"A2/A3 {label}: refusal classification/attribution was not truthful: {response}")
        need(immutable_cut(before, after), f"A2/A3 {label}: protected readback changed after refusal")
        need(after["effects"][aid] is not None and after["effects"][bid] is None and
             after["effects"][cid] is None,
             f"A2/A3 {label}: owner added an effect for the refused ID")
        rejection_histories.append({"case": label, "request_id": request_id, "envelope": envelope,
                                    "response": response, "before": before, "after": after,
                                    "same_id_as_previous": label == "same-B-retry"})
    case["rejection_histories"] = rejection_histories
    case["independent_owner_control"] = case_independent_owner(out, fx, aid)
    owner_proc = probe.OwnerProcess(fx["owner_root"])
    case["seal"] = owner_proc.call({"op": "seal"})
    case["dispose_child"] = owner_proc.call({"op": "dispose_child", "unit": "D"})
    owner_proc.close()
    case["owner_process"] = owner_proc.meta
    need(case["seal"]["reply"].get("result") == "COMMITTED", "A6: pending reservation unexpectedly blocked seal")
    need(case["dispose_child"]["reply"].get("result") == "DENY" and
         "pending-in-domain-effect" in str(case["dispose_child"]["reply"].get("reason")),
         "A6: pending reservation did not block child disposal")
    fx["f4"].sink.close(True)
    case["strict_reconcile"] = baseline.cli(baseline.RECONCILE, fx["owner_root"], aid)
    case["observe_local"] = baseline.cli(baseline.OBSERVE, fx["owner_root"], aid)
    case["after_recovery_refusals"] = {"owner": read_owner(fx["owner_root"]),
                                       "journal": probe.native.blob(fx["f4"].journal),
                                       "witness": fx["f4"].witness_call("/status")}
    need(case["strict_reconcile"]["frame"].get("status") == "refused" and
         case["observe_local"]["frame"].get("status") == "refused",
         "A6: strict recovery invented an event for the eventless reservation")
    need(set(case["after_recovery_refusals"]["owner"]["effects"]) == {aid} and
         case["after_recovery_refusals"]["owner"]["effects"][aid]["status"] == "reserved" and
         case["after_recovery_refusals"]["journal"]["sha256"] == before["journal"]["sha256"],
         "A6: recovery refusal altered the pending owner record or journal")
    case["final_cut"] = {"owner": case["after_recovery_refusals"]["owner"],
                         "journal": case["after_recovery_refusals"]["journal"],
                         "witness": case["after_recovery_refusals"]["witness"]}
    fx["f4"].close(True)
    return case


def case_independent_owner(out, pending_fx, pending_id):
    """A pending effect in one owner must not deny another owner's new effect."""
    independent = baseline.fixture(out, "a3-independent-owner", gate=False)
    request_id = independent["witness_root"] + ":independent-B"
    pending_before = complete_readback(pending_fx, [pending_id])
    independent_before = complete_readback(independent, [request_id])
    envelope, _, _ = baseline.refresh_envelope(independent["owner_root"], request_id)
    response = independent["f4"].submit(envelope)
    independent_after = complete_readback(independent, [request_id])
    pending_after = complete_readback(pending_fx, [pending_id])
    pending_effect = pending_after["effects"][pending_id]
    independent_effect = independent_after["effects"][request_id]
    need(pending_effect is not None and pending_effect["status"] == "reserved" and
         independent_before["owner"]["reply"]["snapshot"]["state"]["native_owner"]["domain_id"] !=
         pending_before["owner"]["reply"]["snapshot"]["state"]["native_owner"]["domain_id"],
         "A3 scope control did not use a distinct owner while A remained pending")
    need(response["response"]["status"] == 201 and independent_effect["status"] == "published",
         "A3 scope control: one owner's pending effect blocked a separate owner")
    need(immutable_cut(pending_before, pending_after),
         "A3 scope control: separate owner admission mutated the pending owner's state")
    independent["f4"].close(True)
    return {"pending_owner_id": pending_before["owner"]["reply"]["snapshot"]["state"]["native_owner"]["domain_id"],
            "pending_owner_effect": pending_effect,
            "independent_owner_before": independent_before, "independent_request_id": request_id,
            "independent_envelope": envelope, "independent_response": response,
            "independent_owner_after": independent_after, "pending_owner_after": pending_after}


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


def case_recovered_then_fresh(out):
    publication = load_publication_probe()
    case = publication.prepare(out, "a5-recovered-current-path")
    eof = publication.append_eof(case)
    _proc, reconcile = publication.run_reconcile(case["owner_root"], case["request_id"])
    need(reconcile.get("result", {}).get("status") == "published", "A5: actual journaled A did not reconcile")
    ready = case["f4"].cold_restart()
    reopen = [case["f4"].call("/replace", {"holder": "pending-admission-a5"}),
              case["f4"].call("/activate", {"authority_version": 2})]
    bid = case["witness_root"] + ":fresh-after-reconciliation"
    envelope, owner_before, _ = baseline.refresh_envelope(case["owner_root"], bid)
    fresh = case["f4"].submit(envelope, authority_version=2)
    owner_after_b = read_owner(case["owner_root"])
    replay = case["f4"].submit(case["envelope"], authority_version=2)
    events = [json.loads(line) for line in case["f4"].journal.read_text().splitlines()]
    need(fresh["response"]["status"] == 201 and
         owner_after_b["effects"][bid]["status"] == "published",
         "A5: fresh B blocked after A settled under eligible authority: " + json.dumps(fresh, sort_keys=True))
    need(replay["response"]["body"].get("outcome") == "already-accepted" and
         len([e for e in events if e.get("event") == "effect_accepted"]) == 2,
         "A5: exact historical A retry appended a second event or lost lookup")
    result = {"append_eof": eof, "reconcile": reconcile, "cold_ready": ready,
              "reopen": reopen, "fresh_id": bid, "fresh_envelope": envelope,
              "owner_before_fresh": owner_before, "fresh_B": fresh,
              "historical_A_replay": replay, "effects": {case["request_id"]: owner_after_b["effects"][case["request_id"]],
                                                            bid: owner_after_b["effects"][bid]},
              "journal_events": events}
    case["f4"].close(True)
    return result


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
        raw["cases"]["A5"] = case_recovered_then_fresh(out)
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
