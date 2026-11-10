#!/usr/bin/env python3
"""Raw-evidence assertions; deliberately does not import candidate code."""
import argparse
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def check(raw):
    original = raw["original"]
    candidate = raw["candidate"]
    between = raw["kill_between"]
    lost = raw["lost_reply"]
    require(original["old_token_after_actual_reap"]["status"] == 201, "original replay no longer admits old token")
    require(original["recovered_status"]["active"] is True, "original active bit did not replay")
    require(original["reaped_process"]["exit"] == -9, "original sink was not killed and reaped")
    require(original["preserved_prefix"]["preloss_bytes_exactly_once"], "original pre-loss accepted bytes changed")
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
    require(candidate["preserved_prefix"]["preloss_bytes_exactly_once"], "candidate lost or duplicated pre-loss bytes")
    require(between["reaped_between_process"]["exit"] == -9, "between-transition process was not killed and reaped")
    require(between["second_cold_status"]["cold_admission_open"] is False,
            "replay after replacement reopened admission")
    require(between["second_cold_old_token"]["status"] == 409, "old token resurrected between transitions")
    require(between["fresh_replacement_required"]["status"] == 200
            and between["after_second_replacement"]["authority_version"] == 3,
            "recovery did not require a fresh native replacement")
    require(between["second_activation"]["status"] == 200 and between["second_fresh_effect"]["status"] == 201,
            "post-recovery native continuation failed")
    require(between["preserved_prefix"]["preloss_bytes_exactly_once"], "intermediate kill changed accepted prefix")
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
    require(lost["preserved_prefix"]["preloss_bytes_exactly_once"], "lost reply path changed accepted prefix")
    return {"original_replay_admits_old_token": True, "candidate_cold_seals": True,
            "accepted_prefix_retained": True, "kill_between_replacement_and_activation": True,
            "lost_reply_readback_matches": True, "bounded_worker_progress": True,
            "flat_bearer_source_limit_demonstrated": True, "runtime_inputs_refused": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("--mutant", choices=("unsealed", "resurrected", "lost-reply-as-denial"))
    args = parser.parse_args()
    data = json.loads(args.raw.read_text())
    if args.mutant == "unsealed":
        data["candidate"]["cold_admission_sealed"] = False
    elif args.mutant == "resurrected":
        data["kill_between"]["second_cold_status"]["cold_admission_open"] = True
    elif args.mutant == "lost-reply-as-denial":
        data["lost_reply"]["replace_reply"]["body"]["local_control_committed"] = False
    print(json.dumps(check(data), sort_keys=True))


if __name__ == "__main__":
    main()
