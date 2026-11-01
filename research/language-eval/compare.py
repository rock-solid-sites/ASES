#!/usr/bin/env python3
"""Language-neutral black-box oracle and Rust/Haskell differential tests.

Python is a TEST HARNESS ONLY, not an approved production implementation.
No external packages or provider credentials are used.
"""
import argparse
import json
import random
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAX_I64 = (1 << 63) - 1


def oracle(c):
    def reject(reason):
        return dict(id=c["id"], accepted=False, reason=reason, charge_cents=0)
    numeric = ("capacity", "reserved", "requested", "usage", "included", "rate",
               "wallet", "wallet_floor", "liability", "spend_cap")
    if any(c[key] < 0 for key in numeric) or c["requested"] == 0:
        return reject("invalid-input")
    if c["mode"] not in ("free", "subscription", "prepaid", "postpaid"):
        return reject("invalid-input")
    for key, reason in (("active", "inactive"), ("verified", "unverified"),
                        ("evidence_current", "stale-evidence"),
                        ("price_known", "unknown-price")):
        if not c[key]:
            return reject(reason)
    if c["reserved"] > c["capacity"] or c["requested"] > c["capacity"] - c["reserved"]:
        return reject("capacity-exceeded")
    units = max(0, c["usage"] - c["included"]) if c["mode"] in ("free", "subscription") else c["usage"]
    charge = units * c["rate"]
    if charge > MAX_I64:
        return reject("arithmetic-overflow")
    if charge and not c["paid_opt_in"]:
        return reject("paid-opt-in-required")
    if c["mode"] == "prepaid":
        if c["wallet"] < c["wallet_floor"] or charge > c["wallet"] - c["wallet_floor"]:
            return reject("wallet-floor-exceeded")
    elif c["liability"] > c["spend_cap"] or charge > c["spend_cap"] - c["liability"]:
        return reject("spend-cap-exceeded")
    return dict(id=c["id"], accepted=True, reason="admitted", charge_cents=charge)


def execute(binary, cases):
    started = time.perf_counter_ns()
    p = subprocess.run([str(binary)], input=json.dumps(cases), text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=40, check=False)
    seconds = (time.perf_counter_ns() - started) / 1_000_000_000
    if p.returncode:
        raise AssertionError(f"{binary} exited {p.returncode}: {p.stderr[:1500]}")
    result = json.loads(p.stdout)
    if not isinstance(result, list) or len(result) != len(cases):
        raise AssertionError(f"{binary}: invalid output length")
    return result, seconds


def assert_equal(actual, expected, label):
    if actual == expected:
        return
    for index, (have, want) in enumerate(zip(actual, expected)):
        if have != want:
            raise AssertionError(f"{label} mismatch at row {index}: {have!r} != {want!r}")
    raise AssertionError(f"{label} length mismatch")


def make_generated():
    randomizer = random.Random(20261101)
    base = json.loads((ROOT / "cases.json").read_text())[0]
    cases = []
    for i in range(1000):
        c = dict(base)
        c["id"] = f"generated-{i:04d}"
        c["mode"] = randomizer.choice(["free", "prepaid", "postpaid", "subscription"])
        c["capacity"] = randomizer.randint(1, 64)
        c["reserved"] = randomizer.randint(0, 70)
        c["requested"] = randomizer.randint(0, 35)
        c["usage"] = randomizer.randint(0, 150)
        c["included"] = randomizer.randint(0, 100)
        c["rate"] = randomizer.randint(0, 20)
        c["wallet"] = randomizer.randint(0, 1200)
        c["wallet_floor"] = randomizer.randint(0, 250)
        c["liability"] = randomizer.randint(0, 800)
        c["spend_cap"] = randomizer.randint(0, 1200)
        c["paid_opt_in"] = randomizer.choice([True, False])
        c["active"] = randomizer.random() > 0.05
        c["verified"] = randomizer.random() > 0.06
        c["evidence_current"] = randomizer.random() > 0.08
        c["price_known"] = randomizer.random() > 0.05
        cases.append(c)
    overflow = dict(base, id="overflow-generated", mode="postpaid",
                    usage=MAX_I64, rate=2, paid_opt_in=True)
    cases.append(overflow)
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rust", required=True)
    parser.add_argument("--haskell", required=True)
    args = parser.parse_args()
    samples = json.loads((ROOT / "cases.json").read_text())
    golden = json.loads((ROOT / "expected.json").read_text())
    assert_equal([oracle(c) for c in samples], golden, "handwritten-golden-vs-oracle")
    generated = make_generated()
    batch = samples + generated
    expected = golden + [oracle(c) for c in generated]
    timings = {}
    for label, binary in (("rust", args.rust), ("haskell", args.haskell)):
        output, seconds = execute(binary, batch)
        assert_equal(output, expected, label + "-oracle")
        repeated, repeat_seconds = execute(binary, batch)
        assert_equal(repeated, output, label + "-determinism")
        if any(row["accepted"] and row["charge_cents"] > 0 and not c["paid_opt_in"]
               for c, row in zip(batch, output)):
            raise AssertionError(label + " unauthorized paid charge")
        timings[label] = {"first_seconds": round(seconds, 6),
                          "repeat_seconds": round(repeat_seconds, 6)}
    print(json.dumps({"result": "PASS", "golden_cases": len(samples),
                      "generated_cases": len(generated),
                      "checked_per_language": len(batch) * 2,
                      "seed": 20261101, "timing": timings}, sort_keys=True))


if __name__ == "__main__":
    main()
