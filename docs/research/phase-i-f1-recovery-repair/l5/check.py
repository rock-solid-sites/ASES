#!/usr/bin/env python3
"""Independent byte/meaning/lifecycle checks for the L5 guard comparison."""
import argparse
import copy
import hashlib
import json
from pathlib import Path


def need(value, why):
    if not value:
        raise ValueError(why)


def state(frame):
    view = frame["snapshot"]
    files = view["files"]
    for name in ("CURRENT", view["selected"]):
        raw = bytes.fromhex(files[name]["raw_hex"])
        need(hashlib.sha256(raw).hexdigest() == files[name]["sha256"], "snapshot byte digest")
    need(bytes.fromhex(files["CURRENT"]["raw_hex"]).decode().strip() == view["selected"], "selector identity")
    decoded = json.loads(bytes.fromhex(files[view["selected"]]["raw_hex"]))
    need(decoded == view["state"], "selected record meaning")
    meta = decoded["work_units"]["C"]["accepted_contents"][0]
    raw = bytes.fromhex(files[meta["object"]]["raw_hex"])
    need(len(raw) == meta["size"] and hashlib.sha256(raw).hexdigest() == meta["sha256"], "accepted content integrity")
    return decoded


def reply(frame):
    return frame["result"]["reply"]["result"]


def one(case):
    mode, schedule = case["mode"], case["schedule"]
    final = state(case["cold"])
    parent = final["work_units"]["C"]["parent"]
    if mode == "original" or schedule == "bypass":
        need(reply(case["move"]) == "COMMITTED" and reply(case["rival_operation"]) == "COMMITTED" and parent == "P", "original/bypass counterexample not reproduced")
        return dict(observation="WRONG_MOVE_ACK_REPRODUCED", scope="unguarded writer allowed", parent=parent)
    if schedule == "kill-after-record" and mode == "generation":
        need(reply(case["successor_operation"]) == "DENY" and parent == "P", "uncertain generation reservation was reset")
        need(case["guard_files"], "missing persistent generation claim")
        return dict(observation="FAIL_CLOSED_BUT_PROGRESS_BLOCKED", parent=parent)
    need(parent == "Q", "acknowledged move not retained")
    for name in ("C", "D"):
        need(final["work_units"][name]["latent_ceiling"] == ["read"], "descendant authority widened")
    if schedule == "overlap":
        need(reply(case["move"]) == "COMMITTED", "owner move failed")
        if mode == "exclusive":
            need(case["rival_ready"]["event"] == "REFUSED" and case["rival_ready"]["reason"] == "writer-busy", "exclusive contender admitted")
        else:
            need(reply(case["rival_operation"]) == "DENY", "reserved generation contender admitted")
    elif schedule == "serial":
        need(reply(case["move"]) == reply(case["activate"]) == "COMMITTED" and final["work_units"]["C"]["active"], "valid move/activation neighbor failed")
    else:
        need(reply(case["successor_operation"]) == "COMMITTED", "post-reap successor failed")
    return dict(observation="SUPPORTED_WITHIN_COOPERATIVE_SCOPE", parent=parent)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("capture", type=Path)
    args = parser.parse_args()
    data = json.loads((args.capture / "raw.json").read_text())
    need(data["execution"] == "PASS", "incomplete experiment")
    for process in data["processes"]:
        need(process["start_ns"] < process["exit_ns"], "process lifetime")
        need(not process["stderr"], "child error")
        for frame in process["frames"]:
            need(json.loads(bytes.fromhex(frame["raw_hex"])) == frame["frame"], "raw process frame identity")
    results = {name: one(case) for name, case in data["cases"].items()}
    for name, case in data["cases"].items():
        if "kill-" in name:
            owner = next(p for p in data["processes"] if p["pid"] == case["gate"]["pid"])
            need(owner["exit"] == -9 and not owner["stdout_tail"], "owner not killed/reaped without ACK")
            need(owner["exit_ns"] < next(p for p in data["processes"] if p["pid"] == case["successor_ready"]["pid"])["start_ns"], "successor started before reap")
    invalid = copy.deepcopy(data["cases"]["exclusive-overlap"])
    selected = invalid["cold"]["snapshot"]
    selected["state"]["work_units"]["C"]["parent"] = "P"
    raw = json.dumps(selected["state"], sort_keys=True).encode()
    selected["files"][selected["selected"]].update(raw_hex=raw.hex(), sha256=hashlib.sha256(raw).hexdigest())
    try:
        one(invalid)
    except ValueError as error:
        control = dict(outcome="REJECTED", reason=str(error))
    else:
        raise ValueError("well-formed wrong-parent evidence escaped")
    print(json.dumps(dict(cases=results, invalid_control=control,
                         conclusion="Exclusive writer is the smaller tested cooperative candidate; generation fence blocks prepublication crash recovery; neither resists unguarded writers; direct atomic CURRENT CAS not implemented."), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
