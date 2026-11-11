#!/usr/bin/env python3
"""Derive native UID-route conclusions from captured bytes and process facts."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess


def need(condition, reason):
    if not condition: raise ValueError(reason)


def sha(raw): return hashlib.sha256(raw).hexdigest()


def identity(status, uid, check_bound=True):
    need(status["Uid"].split() == [str(uid)] * 4, "UID real/effective/saved/fs mismatch")
    need(status["Gid"].split() == [str(uid)] * 4, "GID real/effective/saved/fs mismatch")
    need(status["Groups"] == "" and status["NoNewPrivs"] == "1", "groups/NNP mismatch")
    need(status["CapEff"] == status["CapPrm"] == "0000000000000000", "child retains capabilities")
    if check_bound:
        need(status["CapBnd"] == "00000000000000c3", "unexpected capability bounding set")


def blob(value):
    raw = bytes.fromhex(value["raw_hex"])
    need(sha(raw) == value["sha256"] and len(raw) == value["size"], "captured byte digest/size mismatch")
    return raw


def owner_view(frame): return frame["frame"]["reply"]["snapshot"]


def check(raw):
    need(raw["status"] == "PASS" and raw["controller_exit"] == 0, "native fixture did not finish")
    for key, uid in (("controller_status", 2000), ("worker_status", 2001),
                     ("denied_worker_status", 2001), ("attack_status", 2001)):
        identity(raw[key], uid)
    outer = raw["outer"]
    need(outer["base_id"] == "sha256:b5ba49a53a9c5ad0d0fc3c2c925773589e0d8912cd8077eca91af0bb4ab5e335",
         "different #27 base image")
    need(outer["base_inspection"]["stdout"].strip() == outer["base_id"], "base image changed")
    commit = outer["source_commit"]
    need(re.fullmatch("[a-f0-9]{40}", commit), "invalid source commit")
    repo = Path(__file__).resolve().parents[3]
    for path, expected in outer["context_sources"].items():
        need(path.startswith("docs/research/") and ".." not in Path(path).parts
             and Path(path).suffix == ".py", "unexpected runtime source path")
        source = subprocess.run(["git", "show", commit + ":" + path], cwd=repo,
                                check=True, capture_output=True).stdout
        need(sha(source) == expected, "runtime source differs from captured commit: " + path)
    argv = outer["run"]["argv"]
    need(argv[:2] == ["docker", "--host=unix:///var/run/docker.sock"], "wrong Docker daemon selection")
    for flag in ("--rm", "--network=none", "--cpus=1", "--memory=512m", "--pids-limit=32",
                 "--cap-drop=ALL", "--cap-add=CHOWN", "--cap-add=DAC_OVERRIDE",
                 "--cap-add=SETUID", "--cap-add=SETGID", "--security-opt=no-new-privileges"):
        need(flag in argv, "missing bounded container option: " + flag)
    need(not any(a in ("--privileged", "--mount", "--volume", "-v", "--publish", "-p")
                 or a.startswith(("--mount=", "--volume=", "--publish=")) for a in argv),
         "unexpected mount, publication or privilege")
    need(outer["run"]["exit"] == 0, "native container did not complete")
    audit = raw["fd_audit"]
    need(audit["uid"] == audit["euid"] == 2001, "FD audit from wrong role")
    entries = audit["descriptors"]
    need({e["fd"] for e in entries} >= {0, 1, 2}, "FD evidence incomplete")
    for entry in entries:
        if "errno" in entry:
            need(entry["fd"] == 3 and entry["errno"] == 9, "unexpected unobserved FD")
        else:
            need(entry["access_mode"] in (0, 1, 2) and entry["kind"] != "regular",
                 "worker inherited a regular-file FD")
    need(audit["writable_store_fds"] == [] and audit["direct_invalid_fd_write"]["errno"] == 9
         and audit["direct_path_write"]["errno"] == 13, "direct FD/path controls changed")
    neighbor = raw["authorized_neighbor"]
    decision = neighbor["driver_decision"]
    need(decision["status"] == 201 and decision["body"]["owner_effect"]["status"] == "published",
         "authorized native D use not published")
    before = owner_view(raw["after_neighbor"])
    after_management = owner_view(raw["after_worker_management_attempt"])
    need(before["generation"] == after_management["generation"]
         and before["inventory"]["files"] == after_management["inventory"]["files"],
         "worker management attempt changed native authority/material")
    need(raw["worker_management_attempt"]["driver_decision"]["result"] == "DENY",
         "worker selected a management operation")
    journal = blob(raw["after_neighbor"]["f4"]["journal"])
    events = [json.loads(line) for line in journal.splitlines()]
    effects = [e for e in events if e["event"] == "effect_accepted"]
    need(len(effects) == 1, "expected exactly one actual native effect")
    event = effects[0]
    request_id = neighbor["input"]["request"]["payload"]
    need(event["request_id"] == request_id, "worker request identity lost at actual effect")
    envelope = json.loads(event["payload"])
    native = before["state"]["native_owner"]
    registration = next(r for r in native["registrations"] if r["id"] == native["selected"])
    observed = raw["controller_ready"]["f1_accept"]["response"]["response"]
    pair = {k: observed["consumer_query"][k] for k in ("accepted_content", "required")}
    need(observed["outcome"] == "commit" and observed["state"]["content"] == pair["accepted_content"]
         and registration["pair"] == pair == envelope["pair"], "native source/registration world mismatch")
    meta = registration["metadata"]
    material = before["inventory"]["files"][Path(meta["object"]).name]
    need(blob(material) == pair["accepted_content"].encode() and meta["identity"] == registration["id"],
         "registered bytes/identity do not match native source")
    certificate = event["admission"]
    need(certificate["profile"] == "native-f3-owner-v1" and certificate["native_registration"] is True
         and certificate["domain_id"] == native["domain_id"], "effect does not use native issuer")
    retained = native["effects"][request_id]
    need(retained["status"] == "published" and retained["seq"] == event["seq"]
         and retained["payload_sha256"] == sha(event["payload"].encode())
         and retained["receipt"]["journal_sha256"] == sha(journal), "owner outcome not bound to actual journal")
    for key in ("sink_process", "witness_process"):
        st = raw["after_neighbor"]["f4"][key]["listen_socket_stat"]
        need(st["uid"] == 2000 and st["mode"] == "0o600", "socket not private to owner UID")
    need(raw["post_attenuation_write"]["driver_decision"]["status"] == 409
         and raw["post_attenuation_write"]["driver_decision"]["body"]["reason"] == "native-current-path-denied",
         "attenuated D request did not reach current native denial")
    need(blob(raw["after_denial"]["f4"]["journal"]) == journal, "denied D use appended bytes")
    state = owner_view(raw["after_denial"])["state"]
    rights = {"read", "write"}; unit = "D"; seen = set()
    while unit is not None:
        need(unit not in seen, "current containment cycle")
        seen.add(unit); current = state["work_units"][unit]
        rights &= set(current["grants"])
        if "latent_ceiling" in current: rights &= set(current["latent_ceiling"])
        unit = current["parent"]
    need(rights == {"read"} and state["work_units"]["C"]["parent"] == "Q",
         "attenuation not derived from actual full path")
    actions = {a["name"]: a for a in raw["attack"]["actions"]}
    for key in ("protected-current-append", "management-lock-unlink", "sink-unix-connect", "witness-unix-connect"):
        need(actions[key]["result"] == "denied" and actions[key]["errno"] == 13, "worker access allowed: " + key)
    cli = actions["owner-cli-direct"]
    need(cli["returncode"] != 0 and "PermissionError" in cli["stderr"]
         and "protected/CURRENT" in cli["stderr"] and "ModuleNotFoundError" not in cli["stderr"],
         "direct owner CLI was not tested at protected store access")
    need(actions["setuid-controller"]["errno"] == 1, "worker became owner")
    need(len(raw["attack"]["owner_proc_fds"]) == 16
         and all(a["errno"] == 13 for a in raw["attack"]["owner_proc_fds"]), "owner FD access succeeded")
    descendant = json.loads(raw["attack"]["fork_exec_descendant"]["stdout"])
    # Actual descendant UID/GID/caps/NNP are captured. Its bounding set is not;
    # do not turn the parent's observed value into a fabricated child reading.
    identity(descendant, 2001, check_bound=False)
    need(descendant["setuid"]["errno"] == 1 and descendant["write"]["errno"] == 13,
         "descendant acquired store authority")
    return dict(status="PASS", actual_effects=1, checked_worker_roles=3)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("--controls", action="store_true")
    args = parser.parse_args()
    raw = json.loads(args.raw.read_text())
    result = check(raw)
    if args.controls:
        controls = []
        for name, mutate in (
            ("effective-worker-root", lambda v: v["worker_status"].update(Uid="2001 0 2001 2001")),
            ("raw-regular-fd-hidden-by-summary", lambda v: v["fd_audit"]["descriptors"].append(
                dict(fd=9, kind="regular", access_mode=1, target="protected/objects/objecta"))),
            ("attenuation-denial-changed-to-success", lambda v: v["post_attenuation_write"]["driver_decision"].update(status=201)),
        ):
            altered = copy.deepcopy(raw); mutate(altered)
            try: check(altered)
            except ValueError: controls.append(dict(name=name, rejected=True))
            else: raise ValueError("checker accepted altered evidence: " + name)
        result["controls"] = controls
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__": main()
