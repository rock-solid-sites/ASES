#!/usr/bin/env python3
"""Independent read-only audit of this review's captured T18 probe output."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = HERE / "raw.json"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def rows(step):
    raw = bytes.fromhex(step["journal"]["raw_hex"])
    assert step["journal"]["exists"] and raw.endswith(b"\n")
    assert sha(raw) == step["journal"]["sha256"]
    events = [json.loads(line) for line in raw.splitlines()]
    assert all(type(event.get("seq")) is int and isinstance(event.get("event"), str)
               for event in events)
    assert all(a["seq"] < b["seq"] for a, b in zip(events, events[1:]))
    return events


def main():
    data = json.loads(RAW.read_bytes())
    source = ROOT / "research/phase-i-t18-sink-order-20261103/managed-revocation/managed_sink.py"
    runner = ROOT / "research/phase-i-t18-sink-order-20261103/managed-revocation/probe.py"
    base = ROOT / "research/phase-i-t18-sink-order-20261103/run.py"
    fixture = ROOT / "docs/architecture/core-substrate/fixtures-f2/fixtures.json"
    checks = {
        "execution_commit_matches_pre_run_head": data["execution_sha"] == "7ed639cd0fc8c938dbc68eb8ca1892e54900713c",
        "fixture_hash_matches": sha(fixture.read_bytes()) == data["fixture_sha256"],
        "managed_sink_hash_matches": sha(source.read_bytes()) == data["source_sha256"],
        "imported_runner_hash_matches": sha(base.read_bytes()) == data["base_sha256"],
        "probe_hash_matches": sha(runner.read_bytes()) == data["runner_sha256"],
        "one_child_sink_at_a_time": data["environment"]["max_child_concurrency"] == 1,
        "bounded_address_space": data["environment"]["address_space_limit"] == 268435456,
        "all_processes_killed_restart_refused_and_journals_unchanged": all(
            case["exit"] == -9 and case["restart"]["exit"] != 0
            and not case["restart"]["stdout"].strip()
            and case["restart"]["journal_after"] == case["final_journal"]
            for case in data["cases"].values()),
        "all_response_timestamps_monotone": all(
            all(a["end_ns"] < b["start_ns"] for a, b in zip(case["steps"], case["steps"][1:]))
            for case in data["cases"].values()),
        "all_journals_integral_monotone_and_effect_views_match": True,
        "all_success_acks_reference_same_persisted_event": True,
    }
    for case in data["cases"].values():
        for step in case["steps"]:
            events = rows(step)
            effects = [event for event in events if event["event"] == "effect_accepted"]
            assert effects == step["observed"]["effects"]
            if step["response"]["status"] in (200, 201):
                seq = step["response"]["body"]["event_seq"]
                observed = [event for event in step["observed"]["events"] if event["seq"] == seq]
                persisted = [event for event in events if event["seq"] == seq]
                assert len(observed) == len(persisted) == 1 and observed[0] == persisted[0]

    ref = data["cases"]["reference"]
    ref_steps = {step["label"]: step for step in ref["steps"]}
    revoke, post = ref_steps["revoke"], ref_steps["post-revoke"]
    revoke_event = next(event for event in rows(revoke) if event["event"] == "managed_revoked")
    denial = max((event for event in post["observed"]["events"]
                  if event["event"] == "managed_rejected" and event.get("path") == "/submit"),
                 key=lambda event: event["seq"])
    checks["acknowledged_revoke_precedes_later_request"] = (
        revoke["response"]["status"] == 200 and revoke["end_ns"] < post["start_ns"])
    checks["revoke_state_and_event_precede_denial"] = (
        revoke["observed"]["granted"] is False and revoke["observed"]["active"] is False
        and revoke_event["seq"] < denial["seq"])
    checks["reference_old_write_rejected_without_x_effect"] = (
        post["response"]["status"] == 409
        and not any(event["payload"] == "x" for event in post["observed"]["effects"]))

    mutant = data["cases"]["equality_only"]
    mutant_steps = {step["label"]: step for step in mutant["steps"]}
    mutant_post = mutant_steps["post-revoke"]
    checks["equality_only_mutation_detected_by_stale_use"] = (
        mutant_steps["revoke"]["end_ns"] < mutant_post["start_ns"]
        and mutant_post["response"]["status"] == 201
        and any(event["payload"] == "x" and event["request_id"] == "post-revoke"
                for event in mutant_post["observed"]["effects"]))

    exact = data["cases"]["exact_obligation"]
    exact_steps = {step["label"]: step for step in exact["steps"]}
    commit = next(event for event in rows(exact_steps["commit-before-fixture"])
                  if event["event"] == "obligation_committed")
    replacement = next(event for event in rows(exact_steps["replace"])
                       if event["event"] == "managed_replaced")
    delivery = next(event for event in rows(exact_steps["m"]) if event["event"] == "effect_accepted")
    checks["replacement_ack_precedes_delivery_request"] = (
        exact_steps["replace"]["response"]["status"] == 200
        and exact_steps["replace"]["end_ns"] < exact_steps["m"]["start_ns"])
    checks["replacement_makes_current_use_inactive"] = (
        exact_steps["replacement-inactive"]["response"]["status"] == 409
        and exact_steps["replacement-inactive"]["observed"]["authority_version"] == 2
        and exact_steps["replacement-inactive"]["observed"]["active"] is False)
    checks["post_replacement_exact_delivery_matches_prior_commit"] = (
        exact_steps["m"]["response"]["status"] == 201
        and delivery["payload"] == commit["payload"] == "x"
        and delivery["obligation_id"] == commit["obligation_id"] == "m"
        and delivery["payload_sha256"] == commit["payload_sha256"]
        and delivery["check_mode"] == "committed-exact-obligation"
        and delivery["accepted_under_version"] == 2 and replacement["seq"] < delivery["seq"])

    result = {
        "schema": "independent-t18-revocation-audit.v1",
        "verdict": "SUPPORTED_WITHIN_SELECTED_FLAT_C_P_TRUSTED_LOCAL_MANAGER_SCOPE",
        "basis": "Independent audit of one bounded probe output plus direct source and fixture inspection; no separate implementation or cross-family independence claim.",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "cases": {name: {"fixture_id": case["fixture_id"], "variant": case["variant"],
                          "step_count": len(case["steps"]), "sink_exit": case["exit"],
                          "restart_exit": case["restart"]["exit"]}
                  for name, case in data["cases"].items()},
        "limitations": [
            "Unauthenticated loopback manager routes are assumed trusted; caller isolation was not tested.",
            "Only one revoke and one holder replacement were exercised.",
            "No crash at ACK boundaries, recovery, rollback resistance, power loss, remote sink, arbitrary sink, or host confinement claim.",
            "Managed sink only; no full F2/F4/native enforcement claim.",
        ],
    }
    (HERE / "check.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"all_checks_pass": result["all_checks_pass"],
                      "failed": [name for name, passed in checks.items() if not passed]},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
