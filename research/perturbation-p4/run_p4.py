#!/usr/bin/env python3
"""EDASES-P4: stateful concurrency and bounded environmental perturbation.

CI-only research; no external provider, billing, network calls or production data.
The CPU treatment is restricted to one permitted Linux CPU for <=1.5 seconds.
"""
import argparse
import hashlib
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLAN = HERE.parent / "testing-assurance-pilot/P4-PREREGISTERED-PLAN-2026-11-02.md"

def request(id_, charge=60, authorized=True):
    return {"id": id_, "units": 1, "charge_cents": charge,
            "paid_opt_in": authorized}

TESTS = {
    "capacity-race": {
        "input": {"capacity": 1, "spend_cap_cents": 100,
                  "requests": [request("A"), request("B")]},
        "expected": {"accepted_count": 1, "reserved": 1,
                     "charged_cents": 60, "unique_commit_count": 1}
    },
    "spend-race": {
        "input": {"capacity": 2, "spend_cap_cents": 100,
                  "requests": [request("A"), request("B")]},
        "expected": {"accepted_count": 1, "reserved": 1,
                     "charged_cents": 60, "unique_commit_count": 1}
    },
    "authorization": {
        "input": {"capacity": 2, "spend_cap_cents": 100,
                  "requests": [request("A", 40, False), request("B", 40, True)]},
        "expected": {"accepted_count": 1, "reserved": 1,
                     "charged_cents": 40, "unique_commit_count": 1}
    },
    "duplicate-id": {
        "input": {"capacity": 2, "spend_cap_cents": 100,
                  "requests": [request("A", 40), request("A", 40)]},
        "expected": {"accepted_count": 1, "reserved": 1,
                     "charged_cents": 40, "unique_commit_count": 1}
    }
}

def invoke(binary, case, mode, delay, core=None):
    cmd = [binary, "--mode", mode, "--delay-us", str(delay)]
    if core is not None:
        cmd = ["taskset", "-c", str(core)] + cmd
    t0 = time.perf_counter_ns()
    process = subprocess.run(
        cmd, input=json.dumps(case["input"], separators=(",", ":")),
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False, timeout=12,
    )
    wall_ms = (time.perf_counter_ns() - t0) / 1e6
    if process.returncode:
        raise RuntimeError(f"{binary} {mode} exit {process.returncode}: {process.stderr[-800:]}")
    try:
        got = json.loads(process.stdout)
    except Exception as e:
        raise RuntimeError(f"{binary} invalid JSON stdout: {process.stdout[-400:]}") from e
    if got["workers_reached_barrier"] != len(case["input"]["requests"]):
        raise AssertionError("release barrier not measured with all workers ready")
    if len(got["per_request_accepted"]) != len(case["input"]["requests"]):
        raise AssertionError("incorrect worker result count")
    if got["accepted_count"] + got["rejected_count"] != len(case["input"]["requests"]):
        raise AssertionError("worker outcomes not conserved")
    if got["accepted_count"] != sum(got["per_request_accepted"]):
        raise AssertionError("accepted count inconsistent")
    if got["measured_delay_us_min"] < 0 or got["elapsed_us"] < 0:
        raise AssertionError("invalid monotonic timings")
    return {
        "observed": got, "wall_ms": round(wall_ms, 3),
        "within_expected": all(got[key] == value
                               for key, value in case["expected"].items())
    }

def run_regular(binaries, repeats):
    records = []
    for language, exe in binaries.items():
        for name, case in TESTS.items():
            for mode, delay in (("safe", 0), ("safe", 3000), ("stale", 0)):
                for repetition in range(repeats):
                    r = invoke(exe, case, mode, delay)
                    if mode == "safe" and not r["within_expected"]:
                        raise AssertionError(f"{language}/{name}/{mode}: invariant violated: {r}")
                    if delay and r["observed"]["measured_delay_us_min"] < 2500:
                        raise AssertionError(f"{language}/{name}: scheduled pause not measured")
                    if mode == "stale":
                        expected_fault = name in ("capacity-race", "spend-race", "duplicate-id")
                        if r["within_expected"] == expected_fault:
                            raise AssertionError(
                                f"{language}/{name}: fault instrument not discriminating: {r}"
                            )
                    records.append({
                        "language": language, "case": name, "mode": mode,
                        "delay_requested_us": delay, "repetition": repetition,
                        **r
                    })
    return records

def run_cpu(binaries):
    if sys.platform != "linux" or not hasattr(os, "sched_getaffinity"):
        return {"classification": "NOT_TESTED", "reason": "Linux CPU affinity not available"}
    permitted = sorted(os.sched_getaffinity(0))
    if not permitted:
        return {"classification": "NOT_TESTED", "reason": "no permitted CPUs"}
    core = permitted[0]
    case = TESTS["spend-race"]
    baseline = {}
    for language, exe in binaries.items():
        baseline[language] = [invoke(exe, case, "safe", 3000, core=core)
                              for _ in range(5)]
        if not all(x["within_expected"] for x in baseline[language]):
            raise AssertionError("affinity baseline violates business invariants")
    spinner = r'''
import os, sys, time, json
start = time.monotonic()
before = time.process_time()
print("READY", flush=True)
x = 1
while time.monotonic() - start < 1.2:
    x = (x * 1664525 + 1013904223) % 4294967296
print(json.dumps({"wall_ms":(time.monotonic()-start)*1000,
                  "cpu_ms":(time.process_time()-before)*1000,
                  "cpu_affinity":sorted(os.sched_getaffinity(0))}))
'''
    proc = subprocess.Popen(
        ["taskset", "-c", str(core), sys.executable, "-u", "-c", spinner],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        ready = proc.stdout.readline().strip()
        if ready != "READY":
            stderr = proc.stderr.read()
            return {"classification": "NOT_TESTED", "reason": "spinner setup failed: " + stderr[-250:]}
        stressed = {}
        for language, exe in binaries.items():
            stressed[language] = [invoke(exe, case, "safe", 3000, core=core)
                                  for _ in range(5)]
            if not all(x["within_expected"] for x in stressed[language]):
                raise AssertionError("CPU-stressed run violates invariant")
        stdout, stderr = proc.communicate(timeout=3)
        if proc.returncode:
            raise RuntimeError("bounded spinner failed: " + stderr[-300:])
        load = json.loads(stdout.strip().splitlines()[-1])
        comparisons = {}
        for lang in binaries:
            b = statistics.median(x["wall_ms"] for x in baseline[lang])
            s = statistics.median(x["wall_ms"] for x in stressed[lang])
            comparisons[lang] = {
                "affinity_baseline_median_ms": round(b, 3),
                "affinity_stressed_median_ms": round(s, 3),
                "slowdown_ratio": round(s / b, 4) if b else None,
                "baseline": baseline[lang],
                "stressed": stressed[lang]
            }
        pressure = load["cpu_ms"] >= 150 and load["cpu_affinity"] == [core]
        slowed = any(v["slowdown_ratio"] is not None and
                     v["slowdown_ratio"] > 1.15 for v in comparisons.values())
        return {
            "classification": "EFFECT_MEASURED" if pressure and slowed
                else "PERTURBATION_INEFFECTIVE",
            "selected_core": core, "allowed_cpu_count": len(permitted),
            "spinner": load, "spinner_pressure_observed": pressure,
            "application_slowdown_observed": slowed,
            "measurements": comparisons,
            "resource_limit": "single assigned CPU, 1.2-second load process"
        }
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.communicate(timeout=3)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rust", required=True)
    parser.add_argument("--haskell", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--cpu", action="store_true")
    args = parser.parse_args()
    if args.repetitions < 5 or args.repetitions > 20:
        parser.error("at least five, at most 20 repetitions")
    binaries = {"rust": args.rust, "haskell": args.haskell}
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    result = {
        "experiment": "EDASES-P4",
        "status": "ERROR", "plan_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
        "native_binaries": binaries,
        "hypotheses_frozen_before_execution": True,
        "frozen_inputs": TESTS, "repetitions": args.repetitions,
        "tests": [], "cpu": {"classification": "NOT_TESTED"},
        "limitations": [
            "In-memory process only: not journal durability or crash recovery",
            "Intentionally stale snapshot is a negative control, not production code",
            "No verification of real provider settlements or distributed atomic commits",
            "CPU stress at most one permitted runner CPU for 1.2 seconds",
            "CPU slowdown is an observation, not guaranteed under a shared runner",
            "Full CI artifact transfer outside provider must be verified separately"
        ]
    }
    try:
        result["tests"] = run_regular(binaries, args.repetitions)
        if args.cpu:
            result["cpu"] = run_cpu(binaries)
        result["status"] = "PASS"
    except Exception as exc:
        result["status"] = "ERROR" if isinstance(exc, RuntimeError) else "FAIL"
        result["error"] = f"{type(exc).__name__}: {str(exc)[:800]}"
    finally:
        result["duration_seconds"] = round(time.monotonic() - started, 4)
        destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print("ASES_P4_SUMMARY=" + json.dumps({
            "status": result["status"],
            "plan_sha256": result["plan_sha256"],
            "trials": len(result["tests"]),
            "safe_trials": sum(x["mode"] == "safe" for x in result["tests"]),
            "fault_trials": sum(x["mode"] == "stale" for x in result["tests"]),
            "cpu_classification": result["cpu"].get("classification"),
            "duration_seconds": result["duration_seconds"],
            "evidence_bytes": destination.stat().st_size,
            "error": result.get("error")
        }, sort_keys=True))
        # Compress the CI trace evidence to a distinct run summary; full raw
        # trial data is in the uploaded artifact and must be externally archived.
        condensed = {
            "status": result["status"],
            "plan_sha256": result["plan_sha256"],
            "trial_observations": [{
                "language": row["language"], "case": row["case"],
                "mode": row["mode"], "delay_requested_us": row["delay_requested_us"],
                "repetition": row["repetition"],
                "observed": row["observed"], "within_expected": row["within_expected"],
                "wall_ms": row["wall_ms"]
            } for row in result["tests"]],
            "cpu": result["cpu"],
            "error": result.get("error"),
            "duration_seconds": result["duration_seconds"]
        }
        print("ASES_P4_TRACE_JSON=" + json.dumps(condensed, separators=(",", ":"), sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
