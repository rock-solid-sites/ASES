#!/usr/bin/env python3
"""Independent raw custody evidence checker; imports no probe implementation."""
import copy
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
RAW_DEFAULT = HERE / "evidence/attempt-08/raw.json"
BASE_DIGEST = "sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b"
PINNED = {
    "l1/l1.py": "000359c5f40a6d560940c356f3e4b08d8ce88e88e45cdf8ba7af9e8afe8d46f2",
    "l5/l5_integrated.py": "7216dbb401afa01c01ef5f72a5c45555d5525678799aa30164a7eafce4076fd8",
    "l5/move-cuts/worker.py": "69486c004728c55ba74fa6d8b11205513abf70fc99580b0c193e97c63213b8db",
    "l5/test_management_conformance.py": "b8db19dacd218e73c1a888a6a5ca7a4ee7567f840e485055e92998db993b57f1",
    "worker_variant.py": "636363669b8e782503972f6c2d18156b4a1cb4a26eae9a1ef1baad82542bc7ab",
}
CONTEXT = {
    "fixture/.dockerignore", "fixture/Dockerfile", "fixture/driver.py",
    "fixture/owner_supervisor.py", "fixture/worker_agent.py",
    "fixture/src/docs/research/phase-i-f1-recovery-repair/l5/worker_variant.py",
    "fixture/src/docs/research/phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l1/l1.py",
    "fixture/src/docs/research/phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l5/l5_integrated.py",
    "fixture/src/docs/research/phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l5/move-cuts/worker.py",
    "fixture/src/docs/research/phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l5/test_management_conformance.py",
}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _status(status, uid):
    need(status.get("Uid", "").split() == [str(uid)] * 4, f"UID real/effective/saved/fs mismatch: {uid}")
    need(status.get("Gid", "").split() == [str(uid)] * 4, f"GID real/effective/saved/fs mismatch: {uid}")
    need(status.get("Groups") in ("", None), f"supplementary groups present: {uid}")
    need(status.get("CapEff") == "0000000000000000", f"effective caps present: {uid}")
    need(status.get("CapPrm") == "0000000000000000", f"permitted caps present: {uid}")
    need(status.get("NoNewPrivs") == "1", f"NoNewPrivs missing: {uid}")


def check(raw, check_host_sources=True):
    need(raw.get("execution") == "PASS", "container execution did not pass")
    cases = raw["cases"]
    required_cases = {"allowed-native-path", "moved-attenuated-native-path",
                      "direct-and-descendant-attacks", "guarded-contender",
                      "kill-before-selector", "kill-after-selector",
                      "unguarded-same-uid-bypass", "writable-fd-mutant"}
    need(set(cases) == required_cases, "native case set differs from packet")

    outer = raw["outer"]
    need(outer.get("pinned_base_ref") == "python@" + BASE_DIGEST, "base image digest is not pinned")
    need(outer.get("built_image_id", "").startswith("sha256:"), "built image ID missing")
    need(outer.get("docker_server", "").startswith("28.4.0|vfs|"), "unexpected managed daemon")
    need(set(outer["build_context_file_hashes"]) == CONTEXT, "build context includes unexpected sources")
    for relative, expected in outer["build_context_file_hashes"].items():
        path = HERE / relative
        need(path.is_file() and sha(path.read_bytes()) == expected, "fixture source hash mismatch: " + relative)
    run_argv = outer["run_argv"]
    need(run_argv[:2] == ["docker", "--host=unix:///var/run/docker.sock"], "run did not explicitly select managed socket")
    for required in ("--rm", "--network=none", "--cpus=1", "--memory=512m", "--pids-limit=32",
                     "--cap-drop=ALL", "--cap-add=CHOWN", "--cap-add=DAC_OVERRIDE",
                     "--cap-add=SETUID", "--cap-add=SETGID", "--security-opt=no-new-privileges"):
        need(required in run_argv, "container missing run restriction: " + required)
    need(not any(item in ("--privileged", "-p", "--publish", "--mount", "-v", "--volume")
                 or item.startswith(("--mount=", "--publish=", "-p")) for item in run_argv),
         "container unexpectedly privileged, mounted, or published")
    need(outer.get("run_exit") == 0 and "--rm" in run_argv, "container did not complete with --rm")
    task_id = outer.get("container_label", "")
    need(task_id and outer.get("container_name") == "ases-" + task_id,
         "container name and task label are not unique and aligned")

    runtime = raw["runtime"]
    need(runtime.get("driver_uid") == 0 and runtime.get("cap_exact"), "driver caps or uid mismatch")
    need(runtime.get("cap_expected_hex") == "00000000000000c3", "driver capability set differs")
    need(runtime["driver_status"].get("Uid", "").split() == ["0"] * 4
         and runtime["driver_status"].get("Gid", "").split() == ["0"] * 4
         and runtime["driver_status"].get("NoNewPrivs") == "1",
         "trusted driver identity or NoNewPrivs mismatch")
    need(runtime["driver_status"].get("CapEff") == "00000000000000c3"
         and runtime["driver_status"].get("CapPrm") == "00000000000000c3"
         and runtime["driver_status"].get("CapBnd") == "00000000000000c3",
         "driver capability set is not exactly CHOWN,DAC_OVERRIDE,SETUID,SETGID")
    for path, meta in runtime["layout"].items():
        need(meta["uid"] == 0 and meta["gid"] == 0, "trusted image path not root-owned: " + path)
        expected_mode = "0o755" if meta["is_dir"] else "0o644"
        need(meta["mode"] == expected_mode,
             "trusted image mode is not 0755/0644: " + path)
    for key, digest in PINNED.items():
        candidate = next((value for path, value in runtime["native_source_hashes"].items()
                          if path.endswith(key)), None)
        need(candidate == digest, "native #11 source pin mismatch: " + key)
    need(runtime.get("native_l5_commit") == "51b34aface9340b7e6821b8c40dc62ca38da15e2",
         "native L5 source commit pin mismatch")

    for name in ("allowed-native-path", "moved-attenuated-native-path"):
        case = cases[name]
        _status(case["owner_process"]["manager_uid_status"], 2000)
        _status(case["worker_status"], 2001)
        need(case["store_identity"]["uid"] == 2000 and case["store_identity"]["gid"] == 2000
             and case["store_identity"]["mode"] == "0o700", "store custody identity/mode mismatch")
        need(case["protected_identity"]["uid"] == 2000
             and case["protected_identity"]["mode"] == "0o700", "protected directory custody mismatch")
        need(case["case_parent_identity"]["uid"] == 0
             and case["case_parent_identity"]["mode"] == "0o711", "store parent is worker-writable")
        lock = case["setup"]["lock"]
        after_lock = case["store_lock_after"]
        need(lock["uid"] == 2000 and lock["mode"] == "0o600"
             and (lock["device"], lock["inode"]) == (after_lock["device"], after_lock["inode"]),
             "stable writer lock identity changed")
        audit = case["worker_fds"]
        need(audit.get("event") == "worker-fd-audit" and audit.get("uid") == 2001
             and audit.get("euid") == 2001, "worker self-audit identity mismatch")
        entries = audit.get("descriptors", [])
        fd_numbers = [entry.get("fd") for entry in entries]
        need(len(fd_numbers) == len(set(fd_numbers)) and set(fd_numbers) == {0, 1, 2, 3},
             "worker FD audit omitted or duplicated descriptors")
        writable_store_fds = []
        for entry in entries:
            if "errno" in entry:
                need(entry["fd"] == 3 and entry.get("errno_name") == "EBADF",
                     "worker FD audit has an unexpected unobserved descriptor")
                continue
            need(entry.get("access_mode") in (0, 1, 2), "worker FD access mode missing")
            is_writable = entry.get("kind") == "regular" and entry["access_mode"] != 0
            is_store_path = "/run/custody/cases/" in entry.get("target", "")
            if is_writable and is_store_path:
                writable_store_fds.append(entry)
        need(not writable_store_fds, "worker inherited a writable regular store FD")
        need(audit.get("writable_store_fds") == writable_store_fds,
             "worker summary contradicts descriptor-derived result")
        need(audit["direct_invalid_fd_write"].get("errno_name") == "EBADF"
             and audit["direct_path_write"].get("errno_name") == "EACCES",
             "direct no-FD/path controls did not refuse")
        need(case["direct_ebadf_and_path_control"]["unchanged"], "worker direct attempts changed the store")
        need(case["management_route"]["driver_decision"].get("result") == "DENY"
             and case["management_route_unchanged"], "worker-selected management route was admitted")
        need(case["write_route"]["input"]["request"].get("op") == "write",
             "worker role did not issue D-write")
        object_records = case["final"].get("accepted_objects", [])
        need(len(object_records) == 1, "accepted object bytes missing from raw snapshot")
        obj = object_records[0]
        object_bytes = bytes.fromhex(obj["raw_hex"])
        need(object_bytes == bytes.fromhex(case["expected_object_hex"])
             and sha(object_bytes) == obj["metadata"]["sha256"]
             and sha(object_bytes) == obj["sha256"], "accepted object bytes/hash mismatch")
    allowed = cases["allowed-native-path"]
    expected_effect = b"allowed-payload"
    need(allowed["write_route"]["driver_decision"] == {"allowed": True, "result": "COMMITTED"},
         "native allowed D-write did not commit")
    need(bytes.fromhex(allowed["final"]["effect_raw_hex"]) == expected_effect,
         "native allowed D-write bytes differ")
    moved = cases["moved-attenuated-native-path"]
    need(moved["setup"]["move"]["result"]["reply"]["result"] == "COMMITTED",
         "native move did not commit")
    need(moved["setup"]["activation"]["result"]["reply"]["result"] == "COMMITTED",
         "native activation did not commit")
    need(moved["write_route"]["driver_decision"].get("result") == "DENY"
         and moved["final"]["effect_raw_hex"] is None,
         "moved attenuated native path allowed D-write")

    attacks = cases["direct-and-descendant-attacks"]
    _status(attacks["worker_status"], 2001)
    names = {item["name"]: item for item in attacks["attack"]["actions"]}
    for name in ("direct-protected-write", "chmod-current", "unlink-management-lock",
                 "rename-store-root", "modify-original-manager-source", "setuid-store-owner"):
        need(names[name]["result"] == "denied", "direct attack succeeded: " + name)
    need(names["setuid-store-owner"]["errno_name"] == "EPERM", "setuid refusal was not EPERM")
    direct = attacks["attack"]["direct_original_manager"]
    need(direct["exit"] != 0 and "PermissionError" in direct["stderr"],
         "UID-2001 launched original manager without store denial")
    need(all(item["errno_name"] == "EACCES" for item in attacks["attack"]["owner_proc_fd_attempts"]),
         "UID-2001 acquired manager /proc FD access")
    descendant = json.loads(attacks["attack"]["fork_exec_descendant"]["stdout"])
    _status({"Uid": descendant.get("Uid"), "Gid": descendant.get("Gid"),
             "Groups": descendant.get("Groups"),
             "CapEff": descendant.get("CapEff"), "CapPrm": descendant.get("CapPrm"),
             "NoNewPrivs": descendant.get("NoNewPrivs")}, 2001)
    need(descendant["setuid"].get("name") == "EPERM" and descendant["write"].get("name") == "EACCES",
         "fork/exec descendant regained store authority")
    need(attacks["store_snapshot_unchanged"]
         and attacks["current_before"] == attacks["current_after"],
         "direct attacks changed selected record/effect/object bytes")
    need(attacks["root_inode_before"] == attacks["root_inode_after"], "worker replaced store root inode")
    need(attacks["lock_before"] == attacks["lock_after"], "worker replaced stable lock inode")

    contender = cases["guarded-contender"]
    need(contender["contender_frame"].get("event") == "REFUSED"
         and contender["contender_frame"].get("reason") == "writer-busy"
         and contender["current_unchanged"], "guarded contender was admitted or changed state")
    for name, selector in (("kill-before-selector", "record-000001.json"),
                           ("kill-after-selector", "record-000002.json")):
        case = cases[name]
        need(case["owner_pid"] != case["owner_process"]["supervisor_pid"],
             "kill evidence names supervisor instead of native manager")
        need(case["owner_exit"] == -9 and case["owner_reaped"]
             and case["owner_process"]["manager_reaped"], "native manager was not SIGKILLed and reaped")
        need(case["gate"]["event"] == "GATE" and case["selected_expected_before_successor"]
             and case["at_gate"]["selector"] == selector,
             name + " gate did not capture expected selector position")
        need(case["successor_ready"]["event"] == "READY"
             and case["successor_operation"]["result"]["reply"]["result"] == "COMMITTED",
             name + " successor made no native progress")

    bypass = cases["unguarded-same-uid-bypass"]
    need(bypass["unguarded_move"]["result"]["reply"]["result"] == "COMMITTED",
         "outside-boundary unguarded owner bypass was not demonstrated")
    need(bypass["lock_held_inode"] == bypass["lock_after"],
         "outside-boundary bypass altered lock inode")
    mutant = cases["writable-fd-mutant"]
    need(mutant["mutant_write"]["uid"] == 2001 and mutant["mutant_write"]["access_mode"] == 1
         and mutant["mutant_write"]["write_bytes"] > 0,
         "deliberate pass_fds mutant did not write through its inherited writable descriptor")
    need(bytes.fromhex(mutant["record_bytes_after_mutant_hex"]).endswith(b"\nfd-mutant-write"),
         "separate descriptor-mutant fixture did not retain the written bytes")

    if check_host_sources:
        host_sources = {
            "l1/l1.py": HERE.parent / "phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l1/l1.py",
            "l5/l5_integrated.py": HERE.parent / "phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l5/l5_integrated.py",
            "l5/move-cuts/worker.py": HERE.parent / "phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l5/move-cuts/worker.py",
            "l5/test_management_conformance.py": HERE.parent / "phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l5/test_management_conformance.py",
            "worker_variant.py": HERE.parent / "phase-i-f1-recovery-repair/l5/worker_variant.py"}
        for suffix, path in host_sources.items():
            need(path.is_file() and sha(path.read_bytes()) == PINNED[suffix],
                 "checkout source does not match pinned native source: " + suffix)
    return {"result": "PASS", "native_cases": len(cases),
            "source_hashes": len(PINNED), "context_files": len(CONTEXT)}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=RAW_DEFAULT)
    args = parser.parse_args()
    print(json.dumps(check(json.loads(args.raw.read_text())), sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except BaseException as error:
        print(type(error).__name__ + ": " + str(error), file=sys.stderr)
        raise
