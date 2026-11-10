#!/usr/bin/env python3
"""Prove the independent checker rejects internally rehashed evidence tampering."""
import copy
import json
from pathlib import Path
import sys

import check


def rehash_journal(case):
    events = case["capture"]["journal"]["events"]
    raw = b"".join((json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n").encode()
                   for event in events)
    snap = case["capture"]["journal"]
    snap["raw_hex"] = raw.hex()
    snap["size"] = len(raw)
    snap["sha256"] = check.sha(raw)


def must_reject(label, raw):
    try:
        check.validate(raw)
    except (KeyError, TypeError, ValueError, IndexError):
        return label
    raise AssertionError("checker accepted mutation: " + label)


def main(path):
    original = json.loads(Path(path).read_text())
    check.validate(copy.deepcopy(original))
    rejected = []

    duplicate = copy.deepcopy(original)
    case = duplicate["cases"]["candidate-same-process"]
    events = case["capture"]["journal"]["events"]
    injected = copy.deepcopy(next(event for event in events if event.get("event") == "effect_accepted"))
    injected["seq"] = max(event["seq"] for event in events) + 1
    events.append(injected)
    rehash_journal(case)
    rejected.append(must_reject("rehashed duplicate request row", duplicate))

    sequence = copy.deepcopy(original)
    retry = sequence["cases"]["candidate-same-process"]["retry"]
    retry["response"]["event_seq"] += 20
    rejected.append(must_reject("false original event sequence", sequence))

    receipt = copy.deepcopy(original)
    retry = receipt["cases"]["candidate-same-process"]["retry"]
    retry["response"]["verified_journal_sha256"] = "0" * 64
    rejected.append(must_reject("mismatched verified journal receipt", receipt))

    print(json.dumps({"verdict": "PASS", "controls": rejected}, sort_keys=True, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: check_mutations.py evidence/final/raw.json")
    main(sys.argv[1])
