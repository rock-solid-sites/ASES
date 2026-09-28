#!/usr/bin/env python3
"""Freeze manifest and verification for Phase 2.

Rule being enforced:

  Before measured execution, freeze and hash EVERY executable component that
  can affect the result -- corpus, representation/evidence generation, request
  construction, scoring, schema validation, and derived analysis. Verify the
  hashes immediately BEFORE and immediately AFTER the measured run. Do not
  modify a frozen component without declaring and recording a new freeze.

This module exists because the first Phase 2 freeze was incomplete: it recorded
six harness files but the manifest was never updated after `score.py` and
`run_jev.py` changed, so the recorded digests stopped describing the code that
produced the results (errata E2 in findings/findings.md). A freeze that is not
verified is not a freeze.

Usage
  python3 harness/freeze.py declare            # write frozen/FREEZE.json
  python3 harness/freeze.py verify             # check, exit 1 on any mismatch
  python3 harness/freeze.py verify --stage pre # labelled check for the run log
  python3 harness/freeze.py show               # human-readable table

Every component is assigned a `role`, because "hash everything" is only useful
if the manifest says what each thing is *for* and therefore what a change to it
would invalidate.
"""
import argparse
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE2 = os.path.dirname(HERE)

MANIFEST = os.path.join(PHASE2, "frozen", "FREEZE.json")

# role -> (description, [paths relative to phase2])
COMPONENTS = {
    "corpus": (
        "the real code every case is derived from; changing it invalidates "
        "every ground truth and every representation",
        ["corpus/shlex.py", "corpus/json_encoder.py", "corpus/textwrap.py",
         "corpus/dataclasses.py", "corpus/configparser.py",
         "corpus/_distractor_uuid.py", "corpus/PROVENANCE.json"],
    ),
    "frozen_input": (
        "the enumerated case set and its admissibility matrix; changing either "
        "changes what is being measured",
        ["frozen/cases.json", "frozen/admissibility.json"],
    ),
    "representation": (
        "evidence generation: source->structure extraction and the per-"
        "condition model-visible state",
        ["harness/extract.py", "harness/represent.py"],
    ),
    "request": (
        "request construction and transport: endpoint, model, headers, payload "
        "shape, credential resolution",
        ["harness/run_jev.py"],
    ),
    "schema_validation": (
        "schema validation and the admissibility gate",
        ["harness/validate_cases.py", "harness/record_schema.py"],
    ),
    "scoring": (
        "turning raw records into reported statistics",
        ["harness/score.py"],
    ),
    "derived_analysis": (
        "analyses computed from the scored output; these do not touch the API",
        ["harness/crosscheck_stats.py"],
    ),
    "experiment_design": (
        "the experiment designs and the frozen packets they define; changing a "
        "question, an option set or a case selection changes the experiment",
        ["exp1/DESIGN.md", "exp1/build_packet.py", "exp1/frozen/packet.json",
         "exp2/DESIGN.md", "exp2/build_packet.py", "exp2/frozen/packet.json",
         "exp3/DESIGN.md", "exp3/build_packet.py", "exp3/phase_a_audit.py",
         "exp3/frozen/pool.json", "exp3/frozen/packet.json",
         "exp3/frozen/phase_a_audit.json", "exp3/negative_tests.py"],
    ),
    "freeze_control": (
        "the freeze machinery itself; a change here can silently weaken every "
        "other guarantee",
        ["harness/freeze.py"],
    ),
}

ALL_ROLES = tuple(COMPONENTS)


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build(version=1):
    comps = []
    for role in ALL_ROLES:
        desc, paths = COMPONENTS[role]
        for rel in paths:
            full = os.path.join(PHASE2, rel)
            entry = {"role": role, "path": rel, "present": os.path.exists(full)}
            if entry["present"]:
                entry["sha256"] = sha256_file(full)
                entry["bytes"] = os.path.getsize(full)
            comps.append(entry)
    return {
        "freeze_version": version,
        "declared_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "policy": ("every component that can affect a reported number is hashed "
                   "here and verified immediately before and immediately after "
                   "the measured run; modifying one requires declaring a new "
                   "freeze"),
        "components": comps,
    }


def declare():
    prev = 0
    if os.path.exists(MANIFEST):
        try:
            prev = int(json.load(open(MANIFEST, encoding="utf-8"))
                       .get("freeze_version", 0))
        except Exception:
            prev = 0
    m = build(version=prev + 1)
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(m, fh, indent=1, sort_keys=True)
        fh.write("\n")
    n = len(m["components"])
    print(f"declared freeze v{m['freeze_version']}: {n} components -> {MANIFEST}")
    for role in ALL_ROLES:
        paths = [c["path"] for c in m["components"] if c["role"] == role]
        print(f"  {role:20s} {len(paths)} file(s)")
    return 0


def verify(stage=None, manifest=MANIFEST):
    if not os.path.exists(manifest):
        print(f"FAIL: no freeze manifest at {manifest}")
        return 1
    m = json.load(open(manifest, encoding="utf-8"))
    label = f" [{stage}]" if stage else ""
    bad, missing, roles_seen = [], [], set()
    for c in m["components"]:
        roles_seen.add(c["role"])
        full = os.path.join(PHASE2, c["path"])
        if not os.path.exists(full):
            if c.get("present"):
                bad.append(f"  MISSING  {c['path']} (was present at freeze)")
                missing.append(c["path"])
            continue
        now = sha256_file(full)
        if now != c.get("sha256"):
            bad.append(f"  CHANGED  {c['path']}\n"
                       f"           frozen  {c.get('sha256')}\n"
                       f"           current {now}")
    undeclared = sorted(set(ALL_ROLES) - roles_seen)
    print(f"freeze v{m['freeze_version']} verify{label}: "
          f"{len(m['components'])} components, {len(bad)} mismatch(es)")
    for b in bad:
        print(b)
    if undeclared:
        print("  ERROR: manifest does not cover required role(s): "
              + ", ".join(undeclared))
        return 1
    if bad:
        print("  A frozen component changed. Declaring a NEW FREEZE is required "
              "before any further measured execution.")
        return 1
    print("  OK: every frozen component matches.")
    return 0


def show():
    m = json.load(open(MANIFEST, encoding="utf-8"))
    print(f"freeze v{m['freeze_version']} declared {m['declared_utc']}")
    print(f"{'role':20s} {'path':34s} {'sha256':18s} bytes")
    print("-" * 92)
    for c in m["components"]:
        print(f"{c['role']:20s} {c['path']:34s} "
              f"{(c.get('sha256') or '-')[:16]:18s} {c.get('bytes', '-')}")
    print(f"\ntotal components: {len(m['components'])}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["declare", "verify", "show"])
    ap.add_argument("--stage", default=None,
                    help="label the verification, e.g. pre or post")
    ap.add_argument("--manifest", default=MANIFEST)
    a = ap.parse_args()
    if a.action == "declare":
        raise SystemExit(declare())
    if a.action == "verify":
        raise SystemExit(verify(a.stage, a.manifest))
    show()
    raise SystemExit(0)
