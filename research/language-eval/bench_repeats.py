#!/usr/bin/env python3
"""Repeatable end-to-end reference workload. Timings are NOT pure kernel time.

Measures JSON serialization/deserialization, process startup and admission.
Fixed seeded input, same host, repeated samples; keeps source and compiler provenance
in CI. These early measurements do not establish language selection.
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


def series(binary, payload, expected, iterations):
    results = []
    baseline = None
    for i in range(iterations + 2):
        begin = time.perf_counter_ns()
        p = subprocess.run([binary], input=payload, text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45)
        duration = (time.perf_counter_ns() - begin) / 1e6
        if p.returncode:
            raise AssertionError(f"{binary}: exit {p.returncode}: {p.stderr[:400]}")
        # Every run is required to return identical output; check the whole
        # semantic oracle on first run of each executable.
        if baseline is None:
            baseline = p.stdout
            actual = json.loads(p.stdout)
            if actual != expected:
                mismatch = next((i for i,(a,b) in enumerate(zip(actual,expected)) if a != b), None)
                raise AssertionError(f"{binary}: incorrect result, first mismatch {mismatch}")
        elif p.stdout != baseline:
            raise AssertionError(f"{binary}: nondeterministic output")
        if i >= 2:
            results.append(duration)
    sorted_results = sorted(results)
    return {"median_ms": round(statistics.median(results),3),
            "p95_ms": round(sorted_results[math.ceil(0.95*len(results))-1],3),
            "samples_ms": [round(x,3) for x in results]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--rust", required=True)
    p.add_argument("--haskell", required=True)
    p.add_argument("--factor", type=int, default=12)
    p.add_argument("--iterations", type=int, default=9)
    args = p.parse_args()
    if not (1 <= args.factor <= 100 and 3 <= args.iterations <= 100):
        raise SystemExit("invalid benchmark repetition settings")
    source = json.loads((ROOT/"cases.json").read_text()) + make_generated()
    expanded = source * args.factor
    payload = json.dumps(expanded, separators=(",",":"))
    expected = [oracle(x) for x in expanded]
    measurements = {
        "rust": series(args.rust, payload, expected, args.iterations),
        "haskell": series(args.haskell, payload, expected, args.iterations)
    }
    print(json.dumps({"result":"PASS", "cases_per_invocation":len(expanded),
                      "iterations":args.iterations, "warmup_iterations":2,
                      "input_bytes":len(payload.encode("utf-8")),
                      "measurements": measurements}, sort_keys=True))


if __name__ == "__main__":
    main()
