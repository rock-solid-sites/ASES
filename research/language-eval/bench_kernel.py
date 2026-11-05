#!/usr/bin/env python3
"""Shared decision-only experiment: timed native loop, wire parsing once.

Input/output serialization is deliberately outside each language's measured
core_ns interval. Correctness compares an independent Python oracle checksum.
Benchmarks remain tiny-research evidence, not production kernel selection.
"""
import argparse
import json
import math
import statistics
import subprocess
import time
from pathlib import Path

from compare import make_generated, oracle

ROOT = Path(__file__).resolve().parent
MAX_I64 = (1 << 63) - 1
REASON_CODE = {
    "admitted": 0, "invalid-input": 1, "inactive": 2,
    "unverified": 3, "stale-evidence": 4, "unknown-price": 5,
    "capacity-exceeded": 6, "arithmetic-overflow": 7,
    "paid-opt-in-required": 8, "wallet-floor-exceeded": 9,
    "spend-cap-exceeded": 10,
}


def expected_checksum(cases, passes):
    accepted = 0
    charges = 0
    reasons = 0
    for step in range(passes):
        delta = step % 17
        for case in cases:
            current = dict(case)
            if current["usage"] <= MAX_I64 - 16:
                current["usage"] += delta
            decision = oracle(current)
            accepted += int(decision["accepted"])
            charges += decision["charge_cents"]
            reasons += REASON_CODE[decision["reason"]]
    return {
        "accepted_count": accepted,
        "charge_sum": charges,
        "reason_sum": reasons,
        "evaluations": len(cases) * passes,
    }


def sample(executable, payload, passes, expected, iterations):
    collected = []
    for index in range(iterations + 2):
        start = time.perf_counter_ns()
        result = subprocess.run(
            [executable, "--bench-core", str(passes)],
            input=payload,
            text=True,
            capture_output=True,
            timeout=50,
            check=False,
        )
        wall_ms = (time.perf_counter_ns() - start) / 1e6
        if result.returncode:
            raise AssertionError(
                f"{executable} failed with {result.returncode}: {result.stderr[:1000]}"
            )
        reply = json.loads(result.stdout)
        for field, value in expected.items():
            if reply.get(field) != value:
                raise AssertionError(
                    f"{executable} {field}: got {reply.get(field)}, expected {value}"
                )
        if not isinstance(reply.get("core_ns"), int) or reply["core_ns"] <= 0:
            raise AssertionError(f"{executable}: missing native monotonic core timing")
        if index >= 2:
            collected.append({
                "core_ms": round(reply["core_ns"] / 1e6, 4),
                "process_ms": round(wall_ms, 4),
            })
    core = sorted(x["core_ms"] for x in collected)
    process = sorted(x["process_ms"] for x in collected)
    return {
        "core_median_ms": round(statistics.median(core), 4),
        "core_p95_ms": core[math.ceil(.95 * len(core)) - 1],
        "process_median_ms": round(statistics.median(process), 4),
        "samples": collected,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rust", required=True)
    parser.add_argument("--haskell", required=True)
    parser.add_argument("--passes", type=int, default=240)
    parser.add_argument("--iterations", type=int, default=7)
    args = parser.parse_args()
    if not (1 <= args.passes <= 10000 and 3 <= args.iterations <= 40):
        parser.error("invalid measurement settings")
    cases = json.loads((ROOT / "cases.json").read_text()) + make_generated()
    payload = json.dumps(cases, separators=(",", ":"))
    expected = expected_checksum(cases, args.passes)
    measurements = {
        "rust": sample(args.rust, payload, args.passes, expected, args.iterations),
        "haskell": sample(args.haskell, payload, args.passes, expected, args.iterations),
    }
    print(json.dumps({
        "result": "PASS",
        "kind": "admission-decision-loop-no-per-case-json",
        "scope": "native monotonic timing after one JSON parse and before summary encoding",
        "cases": len(cases),
        "passes": args.passes,
        "warmups": 2,
        "iterations": args.iterations,
        "expected_checksum": expected,
        "measurements": measurements,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
