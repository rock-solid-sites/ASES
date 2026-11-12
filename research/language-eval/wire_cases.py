#!/usr/bin/env python3
"""Strict wire-format conformance checks for both experimental implementations.

Invalid transport envelopes must exit nonzero; valid but inadmissible cases must
return a structured denial instead. Test harness only, not production code.
"""
import argparse
import json
import subprocess
from pathlib import Path
from compare import oracle, assert_equal

ROOT = Path(__file__).resolve().parent
BASE = json.loads((ROOT / "cases.json").read_text())[0]
MAX = (1 << 63) - 1
MIN = -(1 << 63)


def record(**changes):
    return {**BASE, **changes}


def cases():
    # The case names and their expected transport outcomes are specification,
    # not assertions about the present behavior of either implementation.
    valid = [
        ("baseline", [record()], True),
        ("upper-bound-64bit", [record(id="max", wallet=MAX, spend_cap=MAX)], True),
        ("lower-bound-64bit-domain-denial", [record(id="min", wallet=MIN)], True),
        ("arithmetic-overflow-domain-denial",
         [record(id="overflow", mode="postpaid", usage=MAX, rate=2, paid_opt_in=True)], True),
        ("zero-request-domain-denial", [record(id="zero", requested=0)], True),
        ("empty-array", [], True),
    ]
    invalid = [
        ("invalid-json", "{", False),
        ("wrong-top-level-object", json.dumps(record()), False),
        ("missing-required-field", json.dumps([{
            k: v for k, v in BASE.items() if k != "price_known"
        }]), False),
        ("unknown-extra-field", json.dumps([{**BASE, "untrusted_extra": "ignored?"}]), False),
        ("integer-too-large", json.dumps([record(wallet=MAX + 1)]), False),
        ("integer-too-small", json.dumps([record(wallet=MIN - 1)]), False),
        ("non-integer-capacity", json.dumps([record(capacity="16")]), False),
        ("boolean-string", json.dumps([record(active="true")]), False),
        ("null-instead-of-value", json.dumps([record(wallet=None)]), False),
        ("fractional-integer", json.dumps([record(capacity=1.5)]), False),
    ]
    return [(name, json.dumps(payload), expected) for name, payload, expected in valid] + invalid


def run(exe, entries):
    count = 0
    for name, payload, is_valid in entries:
        p = subprocess.run([exe], input=payload, text=True,
                           capture_output=True, timeout=20, check=False)
        if not is_valid:
            if p.returncode == 0:
                raise AssertionError(f"{exe}: {name}: accepted forbidden wire envelope")
            count += 1
            continue
        if p.returncode:
            raise AssertionError(f"{exe}: {name}: rejected valid envelope: {p.stderr[:350]}")
        cases = json.loads(payload)
        expected = [oracle(c) for c in cases]
        assert_equal(json.loads(p.stdout), expected, f"{exe}/{name}")
        count += 1
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rust", required=True)
    parser.add_argument("--haskell", required=True)
    args = parser.parse_args()
    entries = cases()
    counts = {"rust": run(args.rust, entries), "haskell": run(args.haskell, entries)}
    print(json.dumps({"result": "PASS", "wire_cases_per_language": len(entries),
                      "checks": counts}, sort_keys=True))


if __name__ == "__main__":
    main()
