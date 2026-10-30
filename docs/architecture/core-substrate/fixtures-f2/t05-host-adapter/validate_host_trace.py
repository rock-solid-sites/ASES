#!/usr/bin/env python3
"""Independent F2 evaluator for captured T05 selected host subprofile evidence."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

SENTINEL = b"authority-loss-sentinel-v1"
EXPECTED_REPLY = b"OK " + SENTINEL


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def evaluate_candidate(candidate, role):
    errors = []

    def require(condition, code, detail):
        if not condition:
            errors.append({"check": code, "detail": detail})

    baseline = candidate.get("baseline", {})
    post = candidate.get("post_loss", {})
    holder = candidate.get("holder_pid")
    mediator = candidate.get("mediator_pid")
    worker = candidate.get("worker_pid")
    kill_ns = candidate.get("holder_kill_requested_ns")
    reap_ns = candidate.get("holder_wait_reaped_ns")
    trigger_ns = post.get("signal_ns")

    require(baseline.get("reply", "").encode() == EXPECTED_REPLY,
            "baseline_sentinel", "baseline reply must equal expected sentinel bytes")
    require(is_int(baseline.get("pid")) and baseline.get("pid") == worker,
            "baseline_worker_pid", "baseline reply PID must be the worker PID")
    require(all(is_int(pid) and pid > 0 for pid in (holder, mediator, worker)),
            "positive_pids", "holder, mediator, and worker PIDs must be positive integers")
    require(worker != holder, "worker_holder_distinct", "worker and holder PIDs must differ")
    if role == "safe":
        require(mediator == holder, "safe_h_equals_m", "safe selected profile requires H=M")
    else:
        require(mediator != holder, "control_h_not_equals_m", "fault control requires H!=M")

    require(candidate.get("holder_returncode") == -9,
            "holder_sigkill", "holder return code must record actual -9 termination")
    require(is_int(kill_ns) and is_int(reap_ns) and reap_ns > kill_ns,
            "independent_reap", "independent reap timestamp must follow kill request")
    require(is_int(trigger_ns) and is_int(reap_ns) and trigger_ns > reap_ns,
            "reap_before_trigger", "post-loss trigger must occur after independent reap")
    require(post.get("event") == "post_loss" and post.get("pid") == worker,
            "post_loss_worker", "post-loss event must identify the surviving worker")

    iterations = post.get("cpu_iterations")
    cpu_start = post.get("cpu_start_ns")
    cpu_end = post.get("cpu_end_ns")
    require(is_int(iterations) and iterations > 0,
            "positive_cpu_iterations", "CPU loop count must be a positive integer")
    require(is_int(cpu_start) and is_int(reap_ns) and cpu_start > reap_ns,
            "cpu_start_after_reap", "CPU loop start must follow reap")
    require(is_int(cpu_end) and is_int(reap_ns) and cpu_end > reap_ns,
            "cpu_end_after_reap", "CPU loop end must follow reap")
    require(is_int(cpu_start) and is_int(cpu_end) and cpu_end >= cpu_start,
            "cpu_interval_order", "CPU interval end must not precede start")
    require(candidate.get("worker_returncode") == 0,
            "worker_success", "surviving worker must exit successfully after second request")

    routes = {
        "direct_target": post.get("paths", {}).get("direct_target"),
        "symlink_alias": post.get("paths", {}).get("symlink_alias"),
        "noop_O_WRONLY": post.get("direct_write_open"),
    }
    for name, observation in routes.items():
        require(isinstance(observation, dict)
                and observation.get("result") == "denied"
                and observation.get("errno") == 13,
                "route_denied_" + name,
                name + " must independently report denied with errno 13")

    reply = post.get("second_reply", "")
    reply_bytes = reply.encode() if isinstance(reply, str) else b""
    contains_sentinel = SENTINEL in reply_bytes
    reported_bytes = post.get("second_has_protected_bytes")
    if role == "safe":
        require(not contains_sentinel and reported_bytes is False,
                "safe_post_loss_no_sentinel",
                "safe same-socket post-loss reply must contain no sentinel/protected bytes")
        require(reply == "IOERROR:32", "safe_same_socket_epipe",
                "safe same-socket reply must record EPIPE (IOERROR:32)")
    else:
        require(contains_sentinel and reported_bytes is True,
                "control_stale_grant_delivered",
                "H!=M stale-grant control must return sentinel bytes after H reaping")
        require(reply_bytes == EXPECTED_REPLY,
                "control_exact_sentinel", "control reply must equal exact sentinel bytes")

    return {"role": role, "passed": not errors, "errors": errors,
            "observed": {"holder_pid": holder, "mediator_pid": mediator,
                         "worker_pid": worker, "holder_returncode": candidate.get("holder_returncode"),
                         "kill_requested_ns": kill_ns, "reaped_ns": reap_ns,
                         "post_loss_trigger_ns": trigger_ns,
                         "cpu_iterations": iterations, "cpu_start_ns": cpu_start,
                         "cpu_end_ns": cpu_end, "post_loss_reply": reply,
                         "route_observations": routes}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--mutation-output", type=Path)
    args = parser.parse_args()
    raw_bytes = args.input.read_bytes()
    run = json.loads(raw_bytes)
    sentinel_hash = hashlib.sha256(SENTINEL).hexdigest()
    hash_ok = run.get("sentinel_sha256") == sentinel_hash
    safe = evaluate_candidate(run.get("safe_candidate", {}), "safe")
    control = evaluate_candidate(run.get("stale_grant_fault_control", {}), "control")

    mutated = copy.deepcopy(run)
    mutated["safe_candidate"]["post_loss"]["second_reply"] = EXPECTED_REPLY.decode()
    mutated["safe_candidate"]["post_loss"]["second_has_protected_bytes"] = True
    mutation_bytes = (json.dumps(mutated, indent=2, sort_keys=True) + "\n").encode()
    if args.mutation_output:
        args.mutation_output.write_bytes(mutation_bytes)
    mutation = evaluate_candidate(json.loads(mutation_bytes)["safe_candidate"], "safe")
    mutation_rejected = (not mutation["passed"]
                         and any(e["check"] == "safe_post_loss_no_sentinel"
                                 for e in mutation["errors"]))

    result = {
        "evaluator": "F2 independent raw-field T05 selected-subprofile adapter",
        "input": str(args.input),
        "input_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "sentinel_sha256_matches_raw_field": hash_ok,
        "safe_selected_profile": safe,
        "unsafe_H_not_M_control": control,
        "fault_sensitivity": {"mutated_trace_sha256": hashlib.sha256(mutation_bytes).hexdigest(),
                              "mutation_rejected": mutation_rejected,
                              "mutation_errors": mutation["errors"]},
        "overall_pass": hash_ok and safe["passed"] and control["passed"] and mutation_rejected,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
