#!/usr/bin/env python3
"""Independent Phase I concrete-evidence projection pilot.

No import from source-specific check.py. Selected observable invariants are
mapped from raw process/SQLite evidence. Not a full refinement proof.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path


class BadEvidence(Exception):
    pass


def require(cond, description):
    if not cond:
        raise BadEvidence(description)


def raw_bytes(observation, field="raw_hex", digest="sha256"):
    try:
        blob = bytes.fromhex(observation[field])
        require(hashlib.sha256(blob).hexdigest() == observation[digest], "raw hash disagrees")
        return blob
    except (ValueError, KeyError, TypeError) as error:
        raise BadEvidence("missing or malformed raw evidence") from error


def f1(c):
    """Independently tie actual SQLite reader bytes to consumer-visible semantics."""
    r = c["independent_reader"]["observation"]
    q = c["recovered_query"]["response"]["consumer_query"]
    view = json.loads(raw_bytes({"raw_hex": r["view_utf8_hex"], "sha256": r["view_sha256"]}))
    require(view == r["view"] and view == c["recovered_query"]["response"]["state"],
            "view bytes not represented by recovered state")
    obs = json.loads(raw_bytes({"raw_hex": r["observation_utf8_hex"], "sha256": r["observation_sha256"]}))
    require("observations" not in c["recovered"]["config"], "recovery supplied original opaque evidence")
    require(view["content"] == q["accepted_content"], "recovered state/query disagree")
    require("accepted_content" in obs and "required" in obs, "missing opaque accepted binding")
    paired = (obs["accepted_content"] == view["content"] and
              q["status"] == "available" and q["required"] == obs["required"])
    if c["stage"] == "prepared":
        require(paired and q["accepted_content"] != c["accept"]["request"]["value"],
                "precommit recovery was not old accepted pair")
    elif c["name"] == "split-gap":
        require(not paired and q["status"] == "incompatible_required_observations"
                and q["required"] is None and view["content"] == c["accept"]["request"]["value"],
                "split-commit counterexample not observed")
    else:
        require(paired and q["accepted_content"] == c["accept"]["request"]["value"]
                and obs["required"] == c["declared_original_observations"],
                "accepted protected evidence pair was not durable")
    return "COUNTEREXAMPLE" if c["name"] == "split-gap" else "CONSISTENT"


def l5(c):
    """Project durable selector and raw selected record, not checker assertions."""
    a = c["after_process"]
    selected = a["selected"]
    require(selected in a["files"], "selected record absent")
    require(raw_bytes(a["files"]["CURRENT"]).decode().strip() == selected,
            "actual selector bytes differ")
    state = json.loads(raw_bytes(a["files"][selected]))
    require(state == a["state"], "selected raw state not used")
    require(c["cold_ready"]["frame"]["snapshot"]["state"] == state,
            "cold reloading did not see selected state")
    cunit, dunit = state["work_units"]["C"], state["work_units"]["D"]
    write_allowed = c["write"]["frame"]["result"]["reply"]["allowed"]
    new = cunit["parent"] == "Q"
    safe = (not new or (cunit.get("latent_ceiling") == ["read"]
                        and dunit.get("latent_ceiling") == ["read"]))
    safe = safe and not (new and write_allowed)
    if c["kind"] == "split-mutant":
        require(not safe and new and write_allowed, "expected split-selection hazard missing")
    else:
        require(safe, "new selector omitted descendant authority or allowed forbidden write")
    return "COUNTEREXAMPLE" if c["kind"] == "split-mutant" else "CONSISTENT"


def l6(c):
    """Project actual lock, creator result and physical leftovers from raw state."""
    final = c["final_before_exit"]
    for name, info in final["files"].items():
        blob = raw_bytes(info)
        require(info["size"] == len(blob), "physical file length mismatch")
        require(any(d["name"] == name and d["sha256"] == info["sha256"]
                    for d in final["dependencies"]), "file has no matching durable dependency")
    if c["kind"] == "creator-first":
        require(c["creator_ack"]["frame"]["reply"]["result"] == "COMMITTED",
                "prior creator did not commit")
        require(final["live"] and final["dependencies"] and
                c["removal"]["frame"]["reply"]["result"] == "DENY",
                "creator-first removal was not denied")
        return "CONSISTENT"
    gate = c["gate"]["frame"]
    attempt = c["creator_attempt"]["frame"]["reply"]
    removal = c["removal"]["frame"]["reply"]
    if c["kind"] == "guarded":
        require(gate["in_transaction"] is True and
                attempt["result"] == "DENY" and attempt["sqlite_errorcode"] == 5,
                "guarded creator not excluded by actual SQLite contention")
        require(removal["result"] == "COMMITTED" and not final["live"]
                and not final["files"] and not final["dependencies"],
                "guarded removal left a dependent object")
        return "CONSISTENT"
    require(gate["in_transaction"] is False and attempt["result"] == "COMMITTED",
            "detached creator did not interleave")
    require(removal["result"] == "COMMITTED" and not final["live"]
            and bool(final["files"]) and bool(final["dependencies"]),
            "expected detached removal inconsistency absent")
    return "COUNTEREXAMPLE"


CASES = {
    "f1": (f1, {"atomic-A", "atomic-B", "atomic-before", "split-ack", "split-gap"},
           {"split-gap"}),
    "l5": (l5, {"before_record", "after_record", "after_selector", "uninterrupted",
                "write-positive", "split-mutant"}, {"split-mutant"}),
    "l6": (l6, {"creator-first", "guarded", "detached"}, {"detached"}),
}


def audit(kind, data):
    checker, names, bad = CASES[kind]
    require(set(data["cases"]) == names, "case coverage set changed")
    observations = {}
    for name, case in sorted(data["cases"].items()):
        require(case["name" if kind == "f1" else "kind"] == name, "case label/provenance mismatch")
        verdict = checker(case)
        require((verdict == "COUNTEREXAMPLE") == (name in bad), "wrong semantic classification")
        observations[name] = verdict
    negatives = {}
    if kind == "f1":
        require(data["cases"]["atomic-A"]["independent_reader"]["observation"]["view"] ==
                data["cases"]["atomic-B"]["independent_reader"]["observation"]["view"],
                "two positive worlds have differing core content views")
        require(data["cases"]["atomic-A"]["independent_reader"]["observation"]["observation_sha256"] !=
                data["cases"]["atomic-B"]["independent_reader"]["observation"]["observation_sha256"],
                "two positive worlds did not preserve distinct opaque observations")
        witness_name = "atomic-A"
    elif kind == "l5":
        witness_name = "after_selector"
    else:
        witness_name = "guarded"
    for variant in ("raw_integrity", "semantic_violation"):
        witness = copy.deepcopy(data["cases"][witness_name])
        if kind == "f1":
            if variant == "raw_integrity":
                witness["independent_reader"]["observation"]["view_sha256"] = "0" * 64
            else:
                witness["recovered_query"]["response"]["consumer_query"]["required"] = {"forged": True}
        elif kind == "l5":
            if variant == "raw_integrity":
                witness["after_process"]["state"]["work_units"]["C"]["parent"] = "forged"
            else:
                witness["write"]["frame"]["result"]["reply"]["allowed"] = True
        else:
            if variant == "raw_integrity":
                witness = copy.deepcopy(data["cases"]["creator-first"])
                witness["final_before_exit"]["files"]["z"]["sha256"] = "0" * 64
            else:
                witness["creator_attempt"]["frame"]["reply"]["sqlite_errorcode"] = 0
        try:
            checker(witness)
        except BadEvidence:
            negatives[variant] = "REJECTED"
        else:
            raise BadEvidence("tampered valid neighbor escaped projection: " + variant)
    return {"case": kind, "assessments": observations,
            "negative_controls": negatives,
            "oracle_qualification": "independent raw-evidence projection only; not complete implementation refinement"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case", required=True, choices=tuple(CASES))
    p.add_argument("--raw", required=True, type=Path)
    args = p.parse_args()
    print(json.dumps(audit(args.case, json.loads(args.raw.read_text())), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
