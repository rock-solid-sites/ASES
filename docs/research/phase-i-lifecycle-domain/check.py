#!/usr/bin/env python3
"""Independent finite-history checks, without importing the domain guard."""
import copy
import hashlib
import json
from pathlib import Path
import sys


def need(condition, why):
    if not condition:
        raise ValueError(why)


def reply(case):
    return case["response"]["reply"]


def valid_blob(item):
    raw = bytes.fromhex(item["raw_hex"])
    need(hashlib.sha256(raw).hexdigest() == item["sha256"] and len(raw) == item["size"], "invalid raw byte capture")
    return raw


def l5_material(snapshot):
    tree = snapshot["l5"]
    selector = valid_blob(tree["protected/CURRENT"]).decode().strip()
    state = json.loads(valid_blob(tree["protected/" + selector]))
    references = [meta for unit in state["work_units"].values() for meta in unit.get("accepted_contents", [])]
    files = {p: valid_blob(b) for p, b in tree.items() if p.startswith("protected/objects/")}
    return references, files


def check(raw):
    need(raw["execution"] == "PASS", "probe incomplete")
    cases = raw["cases"]
    need(len(cases) == 12, "unexpected history set")
    local, guarded = cases["local-removal-survivor"], cases["joint-refuses-survivor"]
    refs, files = l5_material(local["after"])
    need(reply(local)["result"] == "COMMITTED" and not local["after"]["l6"]["live"] and refs and files,
         "native local removal did not leave the asserted foreign survivor")
    need(reply(guarded)["result"] == "DENY" and guarded["after"]["l6"]["live"]
         and guarded["before"]["l6"]["dependencies"] == guarded["after"]["l6"]["dependencies"],
         "joint guard failed to retain occupied unit")
    observations = guarded["response"]["joint_observations"]
    need(observations and observations[-1]["l6_in_transaction"]
         and observations[-1]["accepted_references"] and observations[-1]["object_material"],
         "foreign inventory did not run under native transaction")

    empty = cases["empty-neighbor"]
    need(reply(empty)["result"] == "COMMITTED" and reply(empty)["joint_empty_observed"] is True
         and reply(empty)["native_global_destruction"] is False, "empty neighbor did not remove locally")
    need(not empty["after"]["l6"]["live"] and not empty["after"]["l6"]["objects_directory_exists"],
         "local empty removal not committed")
    need(empty["later_create"]["reply"]["result"] == "DENY", "creation after completed removal succeeded")
    need(reply(cases["creator-first"])["result"] == "DENY"
         and cases["creator-first"]["after"]["l6"]["live"], "creator-first dependent was stranded")

    removal = cases["remover-first"]
    need(removal["gate"]["in_transaction"] is True, "scan gate detached from transaction")
    need(removal["overlap"]["reply"]["result"] == "DENY"
         and "locked" in removal["overlap"]["reply"].get("error", "").lower(), "creator not serialized by native lock")
    need(reply(removal)["result"] == "COMMITTED" and removal["later_create"]["reply"]["result"] == "DENY",
         "later creator resurrected removed domain")

    orphan = cases["put-kill-orphan"]
    need(orphan["process"]["exit"] == -9 and orphan["gate"]["phase"] == "file-fsynced-row-uncommitted",
         "orphan test did not kill after file fsync")
    need(reply(orphan)["result"] == "DENY" and orphan["after"]["l6"]["unknown_files"] == ["x"]
         and orphan["after"]["l6"]["live"], "unregistered durable orphan not retained")
    cleanup = cases["dispose-kill-cleanup"]
    need(cleanup["process"]["exit"] == -9 and cleanup["gate"]["phase"] == "disposition-committed-before-unlink-reply",
         "disposition test did not kill after commit")
    need(reply(cleanup["before_cleanup"])["result"] == "DENY"
         and cleanup["before_cleanup"]["after"]["l6"]["files"], "uncleaned disposed bytes did not block")
    need(cleanup["cleanup"]["reply"]["result"] == "COMMITTED"
         and reply(cleanup["after_cleanup"])["result"] == "COMMITTED", "separate cleanup did not permit empty neighbor")

    missing = cases["missing-l5-reference"]
    need(reply(missing)["result"] == "DENY" and reply(missing)["reason"] == "joint-inventory-unresolved"
         and missing["after"]["l6"]["live"], "missing reference was treated as disposition")
    unknown = cases["unknown-l5-material"]
    refs, files = l5_material(unknown["after"])
    need(not refs and files and reply(unknown)["result"] == "DENY", "unknown foreign bytes were omitted")
    directory = cases["unknown-l5-directory"]
    need(reply(directory)["result"] == "DENY"
         and any(item.get("kind") == "directory" for item in directory["response"]["joint_observations"][-1]["object_material"]),
         "durable empty directory omitted from material")
    shared = cases["empty-shared-child"]
    refs, files = l5_material(shared["before"])
    need(not refs and not files and reply(shared)["result"] == "DENY"
         and "foreign-l5-child:D" in reply(shared)["inventory"]
         and shared["after"]["l6"]["live"], "empty native descendant was omitted from shared removal")

    ordered = cases["effect-vs-removal"]
    need(ordered["gate"]["stage"] == "guarded"
         and reply(ordered["removal_while_guarded"])["reason"] == "joint-domain-busy", "removal not ordered with in-flight effect")
    journal = valid_blob(ordered["journal"])
    effects = [row for row in map(json.loads, journal.splitlines()) if row["event"] == "effect_accepted"]
    need(ordered["effect"]["status"] == 201 and len(effects) == 1, "ordered authorized effect did not commit")
    need(ordered["witness"]["body"]["current"]["journal_sha256"] == hashlib.sha256(journal).hexdigest(),
         "ordered effect did not publish exact local bytes")
    need(ordered["local_remove"]["reply"]["result"] == "COMMITTED"
         and ordered["later_effect_denied"] == "l6-unit-not-live-sealed", "post-removal effect was not refused at lifecycle check")
    return dict(verdict="PASS", histories=len(cases), conclusion="local-removal-under-fixed-joint-inventory-guard",
                native_shared_identity=False, native_l5_disposition="missing-interface",
                native_global_destruction=False)


def controls(raw):
    bad = []
    changed = copy.deepcopy(raw)
    changed["cases"]["joint-refuses-survivor"]["response"]["reply"]["result"] = "COMMITTED"
    bad.append(changed)
    changed = copy.deepcopy(raw)
    changed["cases"]["put-kill-orphan"]["after"]["l6"]["unknown_files"] = []
    bad.append(changed)
    changed = copy.deepcopy(raw)
    changed["cases"]["effect-vs-removal"]["later_effect_denied"] = "request-identity-mismatch"
    bad.append(changed)
    for value in bad:
        try:
            check(value)
        except ValueError:
            continue
        raise ValueError("altered-evidence control escaped checker")
    return len(bad)


if __name__ == "__main__":
    raw = json.loads(Path(sys.argv[1]).read_text())
    result = check(raw)
    result["altered_controls_rejected"] = controls(raw)
    print(json.dumps(result, sort_keys=True, indent=2))
