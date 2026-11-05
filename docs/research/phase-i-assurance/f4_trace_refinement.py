#!/usr/bin/env python3
"""Independent F4 publication and receipt-history projection.

Reconstructs one serial observer history from raw journal bytes, process
responses and witness publication receipts. Does not import source checkers.
Remote witness observations are conditional, not nonrollback proof.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path


class BadF4Trace(Exception):
    pass


def need(ok, reason):
    if not ok:
        raise BadF4Trace(reason)


def journal(snapshot):
    need(snapshot.get("exists") is True, "journal snapshot missing")
    try:
        blob = bytes.fromhex(snapshot["raw_hex"])
    except (TypeError, KeyError, ValueError) as exc:
        raise BadF4Trace("journal raw bytes missing") from exc
    need(blob.endswith(b"\n") and
         hashlib.sha256(blob).hexdigest() == snapshot["sha256"], "journal raw digest/framing mismatch")
    rows = [json.loads(line) for line in blob.splitlines()]
    need(rows and [r["seq"] for r in rows] == list(range(1, len(rows) + 1)),
         "journal durable event sequence is not contiguous")
    return rows


def last_publish(step):
    pubs = [e for e in step["observed"]["cut_protocol_log"] if e["path"] == "/publish"]
    need(pubs, "no publication history")
    return pubs[-1]


def validate_steps(original, failures_allowed=True):
    """Track each local journal append, remote publish, and client ACK separately."""
    need(original["ready_ns"] > original["start_ns"], "process never became ready")
    previous_end = original["ready_ns"]
    previous_rows = journal(original["ready_journal"]) if original["ready_journal"]["exists"] else []
    previous_hash = original["ready_journal"]["sha256"] if original["ready_journal"]["exists"] else None
    previous_revision = None
    result = []
    for step in original["steps"]:
        need(previous_end < step["start_ns"] < step["end_ns"] < original["exit_ns"],
             "operation order or process lifecycle broken")
        previous_end = step["end_ns"]
        rows = journal(step["journal"])
        need(rows[:len(previous_rows)] == previous_rows, "local durable journal prefix rewritten")
        pub = last_publish(step)
        response = step["response"]
        status = response["status"]
        candidate = pub["request"]["candidate"]
        if status in (200, 201):
            body = response["body"]
            need(len(rows) == len(previous_rows) + 1,
                 "successful ACK did not correspond to exactly one new committed event")
            need(body["event_seq"] == rows[-1]["seq"], "ACK sequence not final durable event")
            need(body["published_journal_sha256"] == step["journal"]["sha256"] ==
                 candidate["journal_sha256"], "published hash differs from ACK/raw journal")
            need(pub["status"] == 200 and pub["transport_valid"] is True and
                 pub["valid"] is True and pub["response"]["published"] is True,
                 "success without validated publication receipt")
            need(body["published_revision"] == pub["response"]["revision"] and
                 pub["response"]["current"]["journal_sha256"] == step["journal"]["sha256"],
                 "ACK revision/current cut not actually returned")
            if previous_revision is not None:
                need(body["published_revision"] == previous_revision + 1,
                     "publication revision skipped, duplicated or rolled back")
            previous_revision = body["published_revision"]
            result.append({"event": step["label"], "transition": "local_commit/publish/ack",
                           "event_seq": rows[-1]["seq"], "published_revision": previous_revision})
        else:
            need(failures_allowed and status == 503, "unexpected failed operation")
            locally_committed = response["body"]["local_control_committed"]
            need(type(locally_committed) is bool, "missing definite local commit flag")
            need(len(rows) == len(previous_rows) + (1 if locally_committed else 0),
                 "failure response inconsistent with local journal changes")
            if not locally_committed:
                need(step["journal"]["sha256"] == previous_hash, "failed no-commit changed journal")
            result.append({"event": step["label"], "transition": "local_commit/unknown_or_rejected" if locally_committed
                           else "operation_refused", "event_seq": rows[-1]["seq"]})
        # For an effect ACK, independently check the exact appended request identity/payload.
        if status == 201:
            expected = step["request"]
            need(rows[-1]["event"] == "effect_accepted" and
                 rows[-1]["request_id"] == expected["request_id"] and
                 rows[-1]["payload"] == expected["payload"],
                 "effect ACK not tied to exact durable request")
        previous_rows = rows
        previous_hash = step["journal"]["sha256"]
    return result


def check_receipt(c):
    result = validate_steps(c["original"])
    observations = c["original"]["steps"]
    by = {s["label"]: s for s in observations}
    need(set(by) == {"create", "grant", "activate", "earlier-ack", "receipt-z",
                     "next-after-outcome"}, "receipt trial step coverage changed")
    need(c["witness_alive"] and c["witness"]["pid"] ==
         c["witness_before"]["pid"] == c["witness_after_z"]["pid"] ==
         c["witness_final"]["pid"], "remote witness process was swapped")
    z = by["receipt-z"]
    remote = [e for e in c["witness_after_z"]["log"] if e["path"] == "/publish"][-1]
    local = last_publish(z)
    need(remote["request"] == local["request"], "remote and local exchange identity mismatch")
    need(remote["response"]["current"] == c["witness_after_z"]["current"],
         "recorded remote current cut differs from witness status")
    need(journal(c["after_z"])[-1]["request_id"] == "receipt-z",
         "z local event not persisted")
    before = c["witness_before"]
    after = c["witness_after_z"]
    if c["kind"] == "rejected":
        need(z["response"]["status"] == 503 and
             z["response"]["body"]["local_control_committed"] is True and
             remote["status"] == 503 and remote["reply_suppressed"] is False and
             remote["response"]["published"] is False, "publication rejection altered")
        need(after["revision"] == before["revision"] and
             after["current"] == before["current"], "rejected publication advanced witness")
        need(by["next-after-outcome"]["response"]["status"] == 503 and
             by["next-after-outcome"]["response"]["body"]["local_control_committed"] is False,
             "divergent later write was accepted")
        refusal = c["startup_refusal"]["frame"]
        need(refusal["ready"] is False and
             refusal["witness_observation"]["response"]["allowed"] is False,
             "divergent cold process unexpectedly ready")
        result.append({"event": "cold_start", "transition": "refused_after_known_remote_rejection"})
    else:
        need(remote["status"] == 200 and remote["response"]["published"] is True and
             after["revision"] == before["revision"] + 1 and
             after["current"]["journal_sha256"] == c["after_z"]["sha256"],
             "remote witness did not actually advance")
        if c["kind"] == "lost":
            need(remote["reply_suppressed"] is True and z["response"]["status"] == 503 and
                 z["response"]["body"]["local_control_committed"] is True and
                 local["response"] is None and local["status"] is None and
                 not local["transport_valid"] and not local["valid"] and
                 bool(local["error"]), "lost remote response was treated as acknowledged")
            result.append({"event": "receipt-z", "transition": "remote_publish_succeeded/local_receipt_unknown"})
        else:
            need(c["kind"] == "positive" and remote["reply_suppressed"] is False and
                 z["response"]["status"] == 201 and local["valid"] is True,
                 "positive control did not validate remote receipt")
        later = by["next-after-outcome"]
        fresh = [e for e in later["observed"]["cut_protocol_log"]
                 if e["path"] == "/check" and e["start_ns"] > z["end_ns"]]
        need(fresh and fresh[-1]["valid"] and
             fresh[-1]["request"]["nonce"] != local["request"]["nonce"] and
             fresh[-1]["request"]["candidate"]["journal_sha256"] == c["after_z"]["sha256"],
             "later operation accepted without distinct fresh-cut check")
        need(later["response"]["status"] == 201, "later matching-cut acceptance missing")
        need(journal(c["cold"]["ready_journal"])[-1]["request_id"] == "fresh-after-restart",
             "recovery did not retain and advance actual later events")
    return {"verdict": "CONSISTENT", "steps": result,
            "scope": "one witness process and local root, no external nonrollback guarantee"}


def check_cut(c):
    result = validate_steps(c["original"])
    by = {s["label"]: s for s in c["original"]["steps"]}
    need({"create", "grant", "activate", "cut-x", "cut-q"}.issubset(by),
         "cut trial missing accepted management/effect operations")
    need(c["witness_alive"] and c["witness_after_ack"]["current"]["journal_sha256"] ==
         c["acknowledged_journal"]["sha256"] ==
         c["after_ack_status"]["actual_cut"]["journal_sha256"],
         "witness did not hold acknowledged journal cut")
    if c["kind"] == "positive":
        need(c["recovered"]["ready_journal"]["sha256"] ==
             c["original"]["final_journal"]["sha256"],
             "positive restart replaced selected journal")
        require_new = [s["label"] for s in c["recovered"]["steps"]]
        need("cut-y" in require_new and
             c["witness_status"]["current"] == c["cold"]["ready_status"]["actual_cut"],
             "recovered accepting process did not publish current cut")
        result.append({"event": "cold_recovery", "transition": "matching_cut_accepted"})
    else:
        refusal = c["startup_refusal"]
        frame = refusal["frame"]
        need(refusal["exit"] == 1 and frame["ready"] is False and
             frame["reason"] == "published-cut-unavailable" and
             frame["local_cut"]["journal_sha256"] !=
             frame["witness_observation"]["response"]["current"]["journal_sha256"] and
             frame["witness_observation"]["response"]["allowed"] is False,
             "cold startup failed to refuse mismatching cut")
        need(c["before_refusal"]["sha256"] ==
             refusal["journal_after"]["sha256"], "startup refusal rewrote local journal")
        if c["kind"] == "publication_rejected":
            need(by["local-unACKed-z"]["response"]["status"] == 503 and
                 by["local-unACKed-z"]["response"]["body"]["local_control_committed"] is True and
                 by["blocked-later"]["response"]["body"]["local_control_committed"] is False,
                 "failed publication did not preserve unACKed local record")
        elif c["kind"] in ("rollback", "forged_same_sequence"):
            need(c["controlled_fault"]["after"]["sha256"] ==
                 c["before_refusal"]["sha256"], "controlled fault bytes changed before refusal")
        else:
            raise BadF4Trace("unrecognized controlled fault case")
        result.append({"event": "cold_recovery", "transition": "mismatching_cut_refused"})
    return {"verdict": "CONSISTENT", "steps": result,
            "scope": "publication and refusal history only; not nonrollback witness proof"}


CASES = {
    "receipt": (check_receipt, {"lost", "positive", "rejected"}),
    "cut": (check_cut, {"positive", "rollback", "forged_same_sequence", "publication_rejected"}),
}


def mutate(kind, cases):
    base = cases["positive"]
    operations = [
        ("duplicate_ACK_sequence", lambda c: c["original"]["steps"][0]["response"]["body"].update(event_seq=2)),
        ("incorrect_published_hash", lambda c: c["original"]["steps"][1]["response"]["body"].update(published_journal_sha256="0" * 64)),
        ("reordered_events", lambda c: c["original"]["steps"].reverse()),
        ("unbound_publication", lambda c: last_publish(c["original"]["steps"][0])["request"]["candidate"].update(journal_sha256="0" * 64)),
        ("missing_publish_receipt", lambda c: last_publish(c["original"]["steps"][0]).update(valid=False)),
        ("tampered_journal_digest", lambda c: c["original"]["steps"][0]["journal"].update(sha256="0" * 64)),
    ]
    checker = CASES[kind][0]
    checks = []
    for label, transform in operations:
        x = copy.deepcopy(base)
        transform(x)
        try:
            checker(x)
        except (BadF4Trace, TypeError, ValueError, KeyError, IndexError):
            checks.append({"mutation": label, "outcome": "REJECTED"})
        else:
            raise BadF4Trace("invalid publication history escaped: " + label)
    return checks


def audit(kind, raw):
    checker, expected = CASES[kind]
    need(set(raw["cases"]) == expected, "source case coverage changed")
    hist = {k: checker(v) for k, v in sorted(raw["cases"].items())}
    invalid = mutate(kind, raw["cases"])
    need(len(invalid) == 6, "mutation coverage dropped")
    return {"case": kind, "histories": hist, "invalid_history_controls": invalid,
            "oracle_qualification": "independent selected trace projection; no universal refinement or nonrollback proof"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case", choices=tuple(CASES), required=True)
    p.add_argument("--raw", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(audit(a.case, json.loads(a.raw.read_text())), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
