#!/usr/bin/env python3
"""Raw-evidence assertions; deliberately does not import candidate code."""
import argparse
import hashlib
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def prefix_bytes(case, label):
    evidence = case["preserved_prefix"]
    raw = bytes.fromhex(evidence["journal_bytes_hex"])
    require(hashlib.sha256(raw).hexdigest() == evidence["journal_sha256"],
            label + ": captured journal hash does not match its bytes")
    rows = [json.loads(line) for line in raw.splitlines()]
    matches = []
    for row in rows:
        if row.get("event") != "effect_accepted" or not row.get("request_id", "").endswith(":x"):
            continue
        payload = json.loads(row["payload"])
        expected = evidence["expected_preloss_payload"]
        require(payload.get("content") == expected, label + ": pre-loss content bytes changed")
        require(hashlib.sha256(expected.encode()).hexdigest() == payload.get("content_sha256"),
                label + ": embedded pre-loss content hash mismatch")
        matches.append(row)
    require(len(matches) == 1, label + ": expected exactly one original accepted prefix event")
    return raw, rows


def actual_witness(local_status, witness, journal_hash, label):
    cut = local_status["actual_cut"]
    current = witness["current"]
    require(current == cut, label + ": witness current cut differs from the running sink cut")
    require(current["journal_sha256"] == journal_hash,
            label + ": witness does not name the captured journal bytes")
    require(current["authority"]["authority_version"] == local_status["authority_version"]
            and current["authority"]["active"] == local_status["active"],
            label + ": witness authority fields differ from runtime state")


def check(raw):
    original = raw["original"]
    candidate = raw["candidate"]
    between = raw["kill_between"]
    lost = raw["lost_reply"]
    require(original["old_token_after_actual_reap"]["status"] == 201, "original replay no longer admits old token")
    require(original["recovered_status"]["active"] is True, "original active bit did not replay")
    require(original["reaped_process"]["exit"] == -9, "original sink was not killed and reaped")
    original_raw, _ = prefix_bytes(original, "original")
    actual_witness(original["recovered_status"], original["witness"],
                   hashlib.sha256(original_raw).hexdigest(), "original")
    require(candidate["cold_admission_sealed"] is True, "cold candidate admission not sealed")
    require(candidate["reaped_process"]["exit"] == -9, "candidate predecessor was not killed and reaped")
    require(candidate["old_token_denial"]["status"] == 409 and candidate["denial_did_not_append"],
            "sealed old-token request was not refused without append")
    require(candidate["activate_only"]["status"] == 409 and candidate["activate_only_did_not_append"],
            "activate-only replay path unexpectedly opened admission")
    require(candidate["unknown_route_refused"]["status"] == 404, "unknown route was not refused")
    require(candidate["unknown_profile_field_refused"]["status"] == 400, "unknown profile field was not refused")
    require(candidate["malformed_submit_refused"]["status"] == 400 and candidate["decode_refusals_did_not_append"],
            "runtime input decoding did not reject malformed input cleanly")
    require(candidate["cpu_scratch_progress"]["iterations"] == 1_000_000
            and candidate["cpu_scratch_progress"]["progress"] != 0,
            "independent bounded CPU progress did not complete")
    require(candidate["cpu_progress_while_route_dead"]["iterations"] == 500_000
            and candidate["cpu_progress_while_route_dead"]["progress"] != 0
            and "transport_error" in candidate["dead_route_attempt"]["effect"],
            "independent progress did not continue while sink was down")
    require(candidate["mediated_effect_while_sealed"]["effect"]["status"] == 409,
            "sealed mediated effect unexpectedly committed")
    require(candidate["replaced_status"]["authority_version"] == 2 and candidate["replaced_status"]["active"] is False,
            "native replacement did not advance version and deactivate")
    require(candidate["activation_after_replace"]["status"] == 200, "native activation after replacement failed")
    require(candidate["fresh_current_effect"]["status"] == 201, "fresh current token did not continue")
    require(candidate["stale_old_token"]["status"] == 409, "old token survived replacement")
    require(candidate["old_physical_worker_given_new_token"]["effect"]["status"] == 201,
            "flat bearer physical-source limit was not demonstrated")
    candidate_raw, _ = prefix_bytes(candidate, "candidate")
    actual_witness(candidate["final_status"], candidate["witness"],
                   hashlib.sha256(candidate_raw).hexdigest(), "candidate")
    require(between["reaped_between_process"]["exit"] == -9, "between-transition process was not killed and reaped")
    require(between["second_cold_status"]["cold_admission_open"] is False,
            "replay after replacement reopened admission")
    require(between["second_cold_old_token"]["status"] == 409, "old token resurrected between transitions")
    require(between["intermediate_activate"]["status"] == 409
            and between["intermediate_activate"]["body"]["outcome"] == "fresh-replacement-required",
            "activation after replayed replacement bypassed fresh replacement")
    before_activate = bytes.fromhex(between["before_intermediate_activate_journal"]["raw_hex"])
    after_activate = bytes.fromhex(between["after_intermediate_activate_journal"]["raw_hex"])
    require(before_activate == after_activate, "intermediate activation refusal appended journal bytes")
    require(between["fresh_replacement_required"]["status"] == 200
            and between["after_second_replacement"]["authority_version"] == 3,
            "recovery did not require a fresh native replacement")
    require(between["second_activation"]["status"] == 200 and between["second_fresh_effect"]["status"] == 201,
            "post-recovery native continuation failed")
    between_raw, _ = prefix_bytes(between, "intermediate recovery")
    actual_witness(between["final_status"], between["witness"],
                   hashlib.sha256(between_raw).hexdigest(), "intermediate recovery")
    prior = raw["prior_code_control"]
    require(prior["reaped_process_after_replace"]["exit"] == -9,
            "prior-code control did not actually reap between transitions")
    require(prior["activate_without_fresh_replacement"]["status"] == 200
            and prior["activate_without_fresh_replacement"]["body"]["outcome"] == "accepted"
            and prior["final_status"]["active"] is True,
            "previous wrapper source did not reproduce the activation hole")
    prior_raw, _ = prefix_bytes(prior, "prior-code control")
    actual_witness(prior["final_status"], prior["final_witness"],
                   hashlib.sha256(prior_raw).hexdigest(), "prior-code control")
    require(lost["replace_reply"]["status"] == 503
            and lost["replace_reply"]["body"]["outcome"] == "cut-publication-unknown"
            and lost["replace_reply"]["body"]["local_control_committed"] is True,
            "replacement reply loss was mistaken for denial")
    local_cut = lost["local_readback"]["actual_cut"]
    remote_cut = lost["witness_readback"]["current"]
    require(local_cut == remote_cut and local_cut["authority"]["authority_version"] == 2
            and local_cut["authority"]["holder"] == "reply-lost-holder",
            "lost-reply exact local/remote readback did not agree")
    require(lost["activation_after_exact_readback"]["status"] == 200,
            "activation after matching readback failed")
    lost_raw, _ = prefix_bytes(lost, "lost reply")
    actual_witness(lost["final_status"], lost["final_witness"],
                   hashlib.sha256(lost_raw).hexdigest(), "lost reply")
    return {"original_replay_admits_old_token": True, "candidate_cold_seals": True,
            "accepted_prefix_retained_from_journal_bytes": True, "kill_between_replacement_and_activation": True,
            "prior_activation_hole_reproduced": True,
            "lost_reply_readback_matches": True, "bounded_worker_progress": True,
            "flat_bearer_source_limit_demonstrated": True, "runtime_inputs_refused": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("--mutant", choices=("unsealed", "resurrected", "activation-hole",
                                              "lost-reply-as-denial", "preloss-bytes"))
    args = parser.parse_args()
    data = json.loads(args.raw.read_text())
    if args.mutant == "unsealed":
        data["candidate"]["cold_admission_sealed"] = False
    elif args.mutant == "resurrected":
        data["kill_between"]["second_cold_status"]["cold_admission_open"] = True
    elif args.mutant == "activation-hole":
        data["kill_between"]["intermediate_activate"] = {
            "status": 200, "body": {"outcome": "accepted", "authority_version": 2}}
    elif args.mutant == "lost-reply-as-denial":
        data["lost_reply"]["replace_reply"]["body"]["local_control_committed"] = False
    elif args.mutant == "preloss-bytes":
        hex_bytes = data["candidate"]["preserved_prefix"]["journal_bytes_hex"]
        data["candidate"]["preserved_prefix"]["journal_bytes_hex"] = ("00" if hex_bytes[:2] != "00" else "ff") + hex_bytes[2:]
    print(json.dumps(check(data), sort_keys=True))


if __name__ == "__main__":
    main()
