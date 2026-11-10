#!/usr/bin/env python3
"""Independent raw-evidence checks; intentionally does not import candidate.py."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SOURCES = HERE.parent / "phase-i-sol-integration/evidence/sources/f4/research/phase-i-t18-sink-order-20261103"
PINS = {
    "published-cut/cut_sink.py": "394b68a4617a1c57c87ca0ad1babbd236d2dc3fc6bbf93b98b03ca39e8e08601",
    "managed-revocation/managed_sink.py": "7134618da4241942f2343748e44ae3d3e339e6d5f22c0681f539d404d0c8247f",
    "run.py": "6b1d759b87b13d32bdc7c5f31a64c15d5a63296d77bc2f16ecc6b0e7795a9d59",
}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def journal(case):
    snap = case["capture"]["journal"]
    raw = bytes.fromhex(snap["raw_hex"])
    need(sha(raw) == snap["sha256"], "journal raw digest")
    need(len(raw) == snap["size"], "journal size")
    events = [json.loads(line, object_pairs_hook=unique_pairs) for line in raw.splitlines()]
    need(events == snap["events"], "journal decoded-event identity")
    last = 0
    for event in events:
        need(type(event.get("seq")) is int and event["seq"] > last, "journal sequence")
        last = event["seq"]
        if event.get("event") == "effect_accepted":
            payload = event.get("payload")
            request_id = event.get("request_id")
            need(type(payload) is str and type(request_id) is str, "effect identity types")
            need(sha(payload.encode("utf-8")) == event.get("payload_sha256"), "effect payload digest")
    return raw, events


def replay_authority(events):
    state = dict(created=False, granted=False, active=False, authority_version=0, holder="old")
    for event in events:
        need(event.get("profile") == "flat-managed-v1" and event.get("unit") == "C"
             and event.get("position") == "p", "effect journal profile")
        name = event.get("event")
        if name == "managed_created":
            need(not state["created"] and event.get("current_version") == 0
                 and event.get("holder") == "old", "create transition")
            state["created"] = True
        elif name == "managed_granted":
            need(state["created"] and not state["granted"]
                 and event.get("previous_version") == state["authority_version"]
                 and event.get("current_version") == state["authority_version"] + 1
                 and event.get("right") == "write" and event.get("allow") is True,
                 "grant transition")
            state["authority_version"] += 1
            state["granted"], state["active"] = True, False
        elif name == "managed_activated":
            need(state["created"] and state["granted"] and not state["active"]
                 and event.get("current_version") == state["authority_version"], "activation transition")
            state["active"] = True
        elif name == "managed_revoked":
            need(state["created"] and state["granted"]
                 and event.get("current_version") == state["authority_version"]
                 and event.get("right") == "write", "revoke transition")
            state["granted"] = state["active"] = False
        elif name == "effect_accepted":
            need(state["created"] and state["granted"] and state["active"]
                 and event.get("accepted_under_version") == state["authority_version"],
                 "effect authorization transition")
            if event.get("check_mode") == "managed-use-current":
                need(event.get("presented_version") == state["authority_version"], "effect presented version")
            else:
                raise ValueError("unexpected effect check mode")
        else:
            raise ValueError("unexpected durable effect journal event: " + str(name))
    return state


def effect_events(case):
    return [event for event in case["capture"]["journal"]["events"]
            if event.get("event") == "effect_accepted"]


def unique_effect_ids(case):
    ids = [event["request_id"] for event in effect_events(case)]
    need(len(ids) == len(set(ids)), "duplicate effect ID in candidate history")


def check_observation(case, frame_key):
    frame = case[frame_key]
    reply = frame["response"]
    need(frame["status"] == 200 and reply["outcome"] == "already-accepted", frame_key + " observation")
    status = case["capture"]["sink_status"]
    proof = next((entry for entry in status["cut_protocol_log"]
                  if entry.get("path") == "/check"
                  and entry.get("response", {}).get("revision") == reply["verified_revision"]
                  and entry.get("response", {}).get("current", {}).get("journal_sha256") == reply["verified_journal_sha256"]), None)
    need(proof is not None and proof.get("valid") is True
         and proof["response"].get("allowed") is True, frame_key + " fresh witness proof")
    return reply


def check_capture(case):
    captured = case["capture"]
    need(captured["witness"]["status"] == 200, "witness status captured")
    for frame in captured["frames"]:
        if "journal_after_sha256" in frame:
            need(len(frame["journal_after_sha256"]) == 64
                 and len(frame["journal_before_sha256"]) == 64,
                 "frame before/after journal digests")
    raw, events = journal(case)
    authority = replay_authority(events)
    expected = {"created": authority["created"], "granted": authority["granted"],
                "active": authority["active"], "authority_version": authority["authority_version"],
                "holder": authority["holder"]}
    witness_cut = captured["witness"]["response"].get("current")
    if witness_cut is not None:
        need(witness_cut["authority"] == expected, "witness current authority matches raw replay")
    return raw, events


def main(path):
    raw = json.loads(Path(path).read_text())
    need(raw["execution"] == "PASS", "probe did not pass")
    need(raw["pin"] == "9226cd4b8cd155a1d1b8e6b0495c0e1b99b941b9", "receipt source pin")
    for rel, expected in PINS.items():
        need(sha((SOURCES / rel).read_bytes()) == expected, "pinned source digest " + rel)
    candidate_key = next((key for key in raw["source_hashes"] if key.endswith("/candidate.py")), None)
    probe_key = next((key for key in raw["source_hashes"] if key.endswith("/probe.py")), None)
    need(candidate_key and probe_key, "candidate/probe hashes")
    need(sha((HERE / "candidate.py").read_bytes()) == raw["source_hashes"][candidate_key], "candidate source hash")
    need(sha((HERE / "probe.py").read_bytes()) == raw["source_hashes"][probe_key], "probe source hash")
    cases = raw["cases"]
    need(set(cases) == {"baseline-lost-reply", "candidate-same-process", "candidate-cold-retry",
                        "kill-before-append", "kill-after-append", "kill-after-publication",
                        "remote-rejection", "witness-restart-empty", "duplicate-journal"}, "case set")

    baseline = cases["baseline-lost-reply"]
    check_capture(baseline)
    need(baseline["first"]["status"] == 503
         and baseline["first"]["response"]["local_control_committed"] is True,
         "baseline lost reply must preserve uncertainty")
    need(baseline["retry"]["status"] == 201, "baseline same-ID retry accepted again")
    need([e["seq"] for e in effect_events(baseline)] == [4, 5], "baseline duplicate effect history")
    dropped = [x for x in baseline["capture"]["proxy_log"]
               if x.get("path") == "/publish" and x.get("response_dropped_after_upstream_commit")]
    need(len(dropped) == 1 and dropped[0]["upstream_status"] == 200
         and dropped[0]["upstream_response"].get("published") is True,
         "baseline witness really committed before reply drop")

    same = cases["candidate-same-process"]
    check_capture(same)
    unique_effect_ids(same)
    need(same["first"]["status"] == 503
         and same["first"]["response"]["local_control_committed"] is True,
         "candidate first publication uncertainty")
    need(len([x for x in same["capture"]["proxy_log"] if x.get("response_dropped_after_upstream_commit")]) == 1,
         "candidate actual reply drop")
    check_observation(same, "retry")
    need(same["retry"]["journal_after_sha256"] == same["retry"]["journal_before_sha256"],
         "same-process observation appends no bytes")
    need(same["conflict"]["status"] == 409
         and same["conflict"]["response"]["outcome"] == "request-id-conflict"
         and same["conflict"]["journal_after_sha256"] == same["conflict"]["journal_before_sha256"],
         "exact-payload conflict changes no journal bytes")
    need(same["new_id"]["status"] == 201, "new ID preserves fresh authorized operation")
    need(same["stale_new_id"]["status"] == 409
         and same["stale_new_id"]["journal_after_sha256"] == same["stale_new_id"]["journal_before_sha256"],
         "invalid current authority changes no journal bytes")
    observed = check_observation(same, "post_revoke_observation")
    need(observed["accepted_authority_version"] == 1 and observed["verified_revision"] == 7,
         "old effect observation preserves original authority after revoke")
    need(same["empty_id"]["status"] == 400 and len(effect_events(same)) == 2,
         "empty request ID rejected without acceptance")

    cold = cases["candidate-cold-retry"]
    check_capture(cold)
    unique_effect_ids(cold)
    check_observation(cold, "retry")
    need(cold["first"]["status"] == 503 and cold["restart"].get("ready") is True
         and len(effect_events(cold)) == 1, "cold retry after lost receipt stays at one effect")

    before = cases["kill-before-append"]
    check_capture(before)
    unique_effect_ids(before)
    need(before["kill"]["owner_exit"] == -9 and before["kill"]["gate"]["stage"] == "before-append"
         and not [e for e in before["kill"]["journal_at_gate"]["events"] if e.get("event") == "effect_accepted"],
         "actual preappend kill leaves effect absent")
    need(before["restart"].get("ready") is True and before["follow"]["status"] == 201,
         "safe preappend restart permits valid new operation")

    after = cases["kill-after-append"]
    check_capture(after)
    unique_effect_ids(after)
    need(after["kill"]["owner_exit"] == -9 and after["kill"]["gate"]["stage"] == "after-append"
         and len(effect_events(after)) == 1, "actual postappend kill preserves local committed effect")
    need(after["restart"].get("ready") is False
         and after["restart"].get("reason") == "published-cut-unavailable",
         "postappend/prepublication cold recovery refuses divergent cut")

    published = cases["kill-after-publication"]
    check_capture(published)
    unique_effect_ids(published)
    need(published["kill"]["owner_exit"] == -9
         and published["kill"]["gate"]["stage"] == "after-publication-before-reply",
         "actual kill after publication before client reply")
    check_observation(published, "retry")
    need(published["restart"].get("ready") is True and len(effect_events(published)) == 1,
         "postpublication cold observation has one effect")

    rejected = cases["remote-rejection"]
    check_capture(rejected)
    unique_effect_ids(rejected)
    first_reply = rejected["first"]["response"]
    need(rejected["first"]["status"] == 503
         and first_reply["outcome"] == "cut-publication-rejected"
         and first_reply["local_control_committed"] is True
         and first_reply["remote_publication"] == "rejected",
         "explicit remote rejection distinguished without denying local commit")
    need(rejected["conflict"]["status"] == 409
         and rejected["conflict"]["response"]["outcome"] == "request-id-conflict"
         and rejected["conflict_unchanged_journal"] is True,
         "ID conflict remains decidable before an unresolved witness check")
    need(rejected["exact_retry"]["status"] == 503
         and rejected["exact_retry"]["response"]["outcome"] == "retry-observation-unresolved"
         and rejected["exact_retry"]["response"]["local_control_committed"] is True
         and rejected["exact_retry_unchanged_journal"] is True,
         "unresolved exact retry preserves committed-local ambiguity")
    witness_publish = [x for x in rejected["capture"]["witness"]["response"]["log"]
                       if x.get("path") == "/publish"]
    need(witness_publish and witness_publish[-1]["status"] == 503
         and witness_publish[-1]["response"].get("published") is False,
         "rejection is a real witness reply")
    need(rejected["blocked"]["status"] == 503
         and rejected["blocked_request_unchanged_journal"] is True,
         "divergent state blocks subsequent append")
    need(rejected["restart"].get("ready") is False, "divergent state blocks cold readiness")

    restarted = cases["witness-restart-empty"]
    check_capture(restarted)
    unique_effect_ids(restarted)
    need(restarted["sink_restart"].get("ready") is False
         and restarted["sink_restart"].get("reason") == "published-cut-unavailable",
         "empty in-memory witness restart does not reset genesis")

    duplicate = cases["duplicate-journal"]
    raw_journal, events = journal(duplicate)
    duplicates = [e for e in events if e.get("event") == "effect_accepted"]
    need(len(duplicates) == 2 and duplicates[0]["request_id"] == duplicates[1]["request_id"],
         "legacy duplicate journal fixture")
    need(duplicate["candidate_restart"].get("ready") is False
         and duplicate["candidate_restart"].get("reason") == "duplicate effect request_id in journal",
         "preexisting duplicate ID journal refused")

    # Every process used in the probe must be reaped and stderr-clean.
    for process in raw["processes"]:
        need("exit" in process and process["exit_ns"] > process["start_ns"], "process exit/reap evidence")
        need(not process["stderr"], "child stderr")
    print(json.dumps({"verdict": "PASS", "cases": len(cases),
                      "baseline_duplicate": len(effect_events(baseline)),
                      "candidate_effect_counts": {name: len(effect_events(cases[name]))
                                                  for name in cases if name != "duplicate-journal"},
                      "explicit_rejection": first_reply["publication_reason"],
                      "unresolved": ["single-writer/root custody", "honest live witness", "witness durability/rollback", "external side-effect delivery"]},
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: check.py evidence/raw.json")
    main(sys.argv[1])
