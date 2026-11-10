#!/usr/bin/env python3
"""Run the bounded own-kernel F4 continuation comparison."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PIN = "9226cd4b8cd155a1d1b8e6b0495c0e1b99b941b9"
PRE_FIX = "b85fd935"
PATHS = ("research/phase-i-t18-sink-order-20261103/published-cut/cut_sink.py",
         "research/phase-i-t18-sink-order-20261103/managed-revocation/managed_sink.py",
         "research/phase-i-t18-sink-order-20261103/run.py")
PATH = PATHS[0]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def child(worker):
    return subprocess.Popen([sys.executable, str(worker)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, bufsize=1)


def worker_call(proc, value):
    proc.stdin.write(canonical(value) + "\n")
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())


def export_source(destination):
    archive = subprocess.check_output(["git", "archive", PIN, *PATHS], cwd=REPO)
    tar_path = destination / "pinned.tar"
    tar_path.write_bytes(archive)
    with tarfile.open(tar_path) as stream:
        stream.extractall(destination / "pinned", filter="data")
    tar_path.unlink()
    return destination / "pinned" / PATH


def make_f4(native, source, root, identity):
    pub = native.F4(source, root, identity)
    # Keep the managed initial prefix and append an actually accepted effect.
    payload = "pre-loss accepted bytes\u0000x\n"
    env = {"causal_id": identity + ":x", "unit": "C", "descendant": "D", "sink_position": "p",
           "content": payload, "content_sha256": sha(payload.encode()), "accepted_observations": {"accepted": True}}
    accepted = pub.submit(env, version=1)
    if accepted["status"] != 201:
        raise RuntimeError("pre-loss effect was not accepted")
    return pub, env, payload


def kill_and_recover(native, pub, cold_script=None, pinned=None):
    dead = pub.sink.close()
    pub.killed_sink_meta = dead
    if cold_script is None:
        pub.start(True)
    else:
        pub.sink = native.Child([sys.executable, cold_script, "--cold-sink", "recover", pub.journal,
                                 pub.wp, "published-cut", pub.identity, pinned])
        pub.port = pub.sink.ready.get("port")
    return pub


def verify_payload(pub, payload):
    raw = pub.journal.read_bytes()
    records = [json.loads(line) for line in raw.splitlines()]
    embedded = []
    for record in records:
        if record.get("event") != "effect_accepted":
            continue
        try:
            embedded.append(json.loads(record["payload"]))
        except (TypeError, json.JSONDecodeError):
            embedded.append({"content": record.get("payload")})
    preloss = [(record, item) for record, item in zip(
        [r for r in records if r.get("event") == "effect_accepted"], embedded)
        if record.get("request_id", "").endswith(":x")]
    return {"journal_bytes_hex": raw.hex(), "journal_sha256": sha(raw),
            "expected_preloss_payload": payload,
            "preloss_bytes_exactly_once": len(preloss) == 1 and preloss[0][1].get("content") == payload,
            "effect_request_ids": [record.get("request_id") for record in records if record.get("event") == "effect_accepted"],
            "journal_lines": records}


def run(out):
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        raise FileExistsError("output directory must be new and empty: " + str(out))
    native = module("native_helpers", HERE.parent / "phase-i-sol-integration/native.py")
    pinned = export_source(out)
    cold_script = str(HERE / "cold_sink.py")
    results = {"metadata": {"receipt_commit": PIN, "receipt_source_path": PATH,
                            "receipt_source_sha256": sha(pinned.read_bytes()),
                            "cold_sink_sha256": sha((HERE / "cold_sink.py").read_bytes()),
                            "worker_sha256": sha((HERE / "worker.py").read_bytes()),
                            "native_helpers_sha256": sha((HERE.parent / "phase-i-sol-integration/native.py").read_bytes()),
                            "python": sys.version, "platform": sys.platform,
                            "bounded_iterations_max": 2_000_000}}
    root = out / "state" / "original-replay"
    pub, env, payload = make_f4(native, pinned, root, "cold-original")
    old_version = pub.sink.ready.get("authority_version", 1)
    kill_and_recover(native, pub)
    old_reply = pub.submit(env | {"causal_id": "cold-original:y"}, version=1)
    results["original"] = {"old_token_after_actual_reap": old_reply,
                            "recovered_status": native.http(pub.port, "/status")["body"],
                            "witness": native.http(pub.wp, "/status")["body"],
                            "preserved_prefix": verify_payload(pub, payload),
                            "reaped_process": pub.killed_sink_meta,
                            "processes": pub.sink.meta}
    pub.close()

    root = out / "state" / "cold-sealed"
    pub, env, payload = make_f4(native, pinned, root, "cold-candidate")
    cpu = child(HERE / "worker.py")
    dead_port = pub.port
    pub.killed_sink_meta = pub.sink.close()
    dead_progress = worker_call(cpu, {"op": "progress", "iterations": 500_000})
    dead_route_attempt = worker_call(cpu, {"op": "progress", "iterations": 100_000, "port": dead_port,
                                           "version": 1, "request_id": "candidate:route-dead",
                                           "payload": "route unavailable"})
    pub.sink = native.Child([sys.executable, cold_script, "--cold-sink", "recover", pub.journal,
                             pub.wp, "published-cut", pub.identity, pinned])
    pub.port = pub.sink.ready.get("port")
    cold_status = native.http(pub.port, "/status")["body"]
    before_deny = native.blob(pub.journal)
    denied = pub.submit(env | {"causal_id": "candidate:sealed-old"}, version=1)
    after_deny = native.blob(pub.journal)
    activate_only = pub.call("/activate", {"authority_version": 1})
    after_activate = native.blob(pub.journal)
    unknown_route = pub.call("/future-profile", {})
    unknown_profile_field = pub.call("/activate", {"authority_version": 1, "profile": "flat-managed-v1"})
    malformed_submit = pub.call("/submit", {"authority_version": "1", "request_id": "bad", "payload": "bad"})
    after_decode = native.blob(pub.journal)

    # A physically independent worker advances in a bounded CPU-only task while
    # the effect route is sealed, then attempts its mediated effect.
    scratch = worker_call(cpu, {"op": "progress", "iterations": 1_000_000})
    mediated = worker_call(cpu, {"op": "progress", "iterations": 250_000, "port": pub.port,
                                 "version": 1, "request_id": "candidate:worker-sealed", "payload": "worker effect"})
    pub.call("/replace", {"holder": "new-holder"})
    replaced_status = native.http(pub.port, "/status")["body"]
    activated = pub.call("/activate", {"authority_version": 2})
    fresh = pub.submit(env | {"causal_id": "candidate:fresh"}, version=2)
    stale = pub.submit(env | {"causal_id": "candidate:stale"}, version=1)
    # Deliberate limit test: same old process receives the new flat bearer token.
    physical_old_given_new = worker_call(cpu, {"op": "progress", "iterations": 100_000, "port": pub.port,
                                               "version": 2, "request_id": "candidate:old-physical-new-token",
                                               "payload": "old physical worker with new token"})
    worker_call(cpu, {"op": "stop"})
    cpu.wait(timeout=3)
    results["candidate"] = {"cold_status": cold_status, "cold_admission_sealed": cold_status.get("cold_admission_open") is False,
        "old_token_denial": denied, "denial_did_not_append": before_deny == after_deny,
        "activate_only": activate_only, "activate_only_did_not_append": after_deny == after_activate,
        "unknown_route_refused": unknown_route, "unknown_profile_field_refused": unknown_profile_field,
        "malformed_submit_refused": malformed_submit, "decode_refusals_did_not_append": after_decode == after_activate,
        "cpu_progress_while_route_dead": dead_progress, "dead_route_attempt": dead_route_attempt,
        "cpu_scratch_progress": scratch, "mediated_effect_while_sealed": mediated,
        "replaced_status": replaced_status, "activation_after_replace": activated,
        "fresh_current_effect": fresh, "stale_old_token": stale,
        "old_physical_worker_given_new_token": physical_old_given_new,
        "preserved_prefix": verify_payload(pub, payload),
        "final_status": native.http(pub.port, "/status")["body"],
        "journal": native.blob(pub.journal), "witness": native.http(pub.wp, "/status")["body"],
        "calls": pub.calls, "sink_processes": [pub.sink.meta]}
    results["candidate"]["reaped_process"] = pub.killed_sink_meta
    pub.close()

    # Kill after native replacement publication, before native activation.
    root = out / "state" / "kill-between"
    pub, env, payload = make_f4(native, pinned, root, "cold-between")
    kill_and_recover(native, pub, cold_script, pinned)
    replacement = pub.call("/replace", {"holder": "replacement-before-kill"})
    replacement_cut = native.http(pub.port, "/status")["body"]
    pub.sink.close()
    first_reaped = pub.sink.meta
    pub.sink = native.Child([sys.executable, cold_script, "--cold-sink", "recover", pub.journal,
                             pub.wp, "published-cut", pub.identity, pinned])
    pub.port = pub.sink.ready.get("port")
    second_cold = native.http(pub.port, "/status")["body"]
    second_old_denial = pub.submit(env | {"causal_id": "between:old"}, version=1)
    before_intermediate_activate = native.blob(pub.journal)
    intermediate_activate = pub.call("/activate", {"authority_version": 2})
    after_intermediate_activate = native.blob(pub.journal)
    second_replace = pub.call("/replace", {"holder": "replacement-after-kill"})
    second_replace_status = native.http(pub.port, "/status")["body"]
    second_activation = pub.call("/activate", {"authority_version": 3})
    second_fresh = pub.submit(env | {"causal_id": "between:fresh-after-second-replace"}, version=3)
    results["kill_between"] = {"first_replacement": replacement, "first_replacement_status": replacement_cut,
        "reaped_between_process": first_reaped,
        "second_cold_status": second_cold, "second_cold_old_token": second_old_denial,
        "intermediate_activate": intermediate_activate,
        "intermediate_activate_did_not_append": before_intermediate_activate == after_intermediate_activate,
        "before_intermediate_activate_journal": before_intermediate_activate,
        "after_intermediate_activate_journal": after_intermediate_activate,
        "fresh_replacement_required": second_replace, "after_second_replacement": second_replace_status,
        "second_activation": second_activation, "second_fresh_effect": second_fresh,
        "preserved_prefix": verify_payload(pub, payload), "final_status": native.http(pub.port, "/status")["body"],
        "witness": native.http(pub.wp, "/status")["body"]}
    pub.close()

    # Preserve and run the immediately previous cold wrapper as a direct
    # comparator: it sealed on boot but let native activation through after a
    # replacement had been replayed with active=false.
    controls = out / "controls"
    controls.mkdir()
    prior_source = controls / "prior_cold_sink.py"
    prior_source.write_bytes(subprocess.check_output(
        ["git", "show", PRE_FIX + ":docs/research/phase-i-cold-activation/cold_sink.py"], cwd=REPO))
    control_root = out / "state" / "prior-code-activate-hole"
    pub, env, payload = make_f4(native, pinned, control_root, "cold-prior-control")
    kill_and_recover(native, pub, str(prior_source), pinned)
    first_replace = pub.call("/replace", {"holder": "control-holder-one"})
    pub.sink.close()
    after_replace_process = pub.sink.meta
    pub.sink = native.Child([sys.executable, str(prior_source), "--cold-sink", "recover", pub.journal,
                             pub.wp, "published-cut", pub.identity, pinned])
    pub.port = pub.sink.ready.get("port")
    prior_activate = pub.call("/activate", {"authority_version": 2})
    results["prior_code_control"] = {"source_commit": PRE_FIX,
        "source_sha256": sha(prior_source.read_bytes()), "first_replacement": first_replace,
        "reaped_process_after_replace": after_replace_process,
        "cold_status": native.http(pub.port, "/status")["body"],
        "activate_without_fresh_replacement": prior_activate,
        "final_status": native.http(pub.port, "/status")["body"],
        "final_witness": native.http(pub.wp, "/status")["body"],
        "preserved_prefix": verify_payload(pub, payload)}
    pub.close()

    # The receipt witness can commit replacement then drop only its reply.
    root = out / "state" / "lost-replacement-reply"
    pub, env, payload = make_f4(native, pinned, root, "cold-lost-reply")
    kill_and_recover(native, pub, cold_script, pinned)
    fault = pub.wcall("/fault", reject_publish=False, drop_publish_reply_once=True)
    reply_lost = pub.call("/replace", {"holder": "reply-lost-holder"})
    local_readback = native.http(pub.port, "/status")["body"]
    witness_readback = native.http(pub.wp, "/status")["body"]
    activate_after_readback = pub.call("/activate", {"authority_version": local_readback["authority_version"]})
    results["lost_reply"] = {"fault": fault, "replace_reply": reply_lost, "local_readback": local_readback,
        "witness_readback": witness_readback, "activation_after_exact_readback": activate_after_readback,
        "final_status": native.http(pub.port, "/status")["body"],
        "final_witness": native.http(pub.wp, "/status")["body"],
        "preserved_prefix": verify_payload(pub, payload), "calls": pub.calls}
    pub.close()

    raw_path = out / "raw.json"
    raw_path.write_text(json.dumps(results, sort_keys=True, indent=2) + "\n")
    return raw_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=HERE / "evidence" / "run-02")
    args = parser.parse_args()
    print(run(args.out))
