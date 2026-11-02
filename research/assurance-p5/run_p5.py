#!/usr/bin/env python3
"""P5 compare conventional restart checks vs qualified SIGKILL boundary checks.

All journals live under a disposable temporary directory. No provider calls.
Outcome classification separates injected behavior failures from instrument errors.
"""
import argparse
import hashlib
import json
import os
import select
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path

PLAN = Path(__file__).resolve().parent.parent / "testing-assurance-pilot/P5-PREREGISTERED-PLAN-2026-11-02.md"
MODES = ("correct", "duplicate", "early_ack")
POINTS = {"before": "PREPARED", "after_sync": "DURABLE", "after_ack": "ACK"}
TARGET = {"reserved": 1, "charged": 40, "entries": 1, "ids": 1}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(exe, args, timeout=5):
    start = time.monotonic_ns()
    p = subprocess.run([exe, *map(str, args)], text=True, capture_output=True, timeout=timeout, check=False)
    duration = (time.monotonic_ns() - start) / 1e6
    if p.returncode:
        raise RuntimeError(f"{exe} return {p.returncode}: {p.stderr[-500:]}")
    return p.stdout.strip().splitlines(), round(duration, 3)

def apply(exe, journal, mode, ident="A", units=1, charge=40, capacity=2, cap=80, consent=True):
    return run(exe, ["apply", journal, mode, "none", ident, units, charge, capacity, cap, str(consent).lower()])

def inspect(exe, journal):
    output, ms = run(exe, ["inspect", journal])
    if len(output) != 1 or not output[0].startswith("STATE|"):
        raise RuntimeError("unexpected inspect output " + str(output))
    fields = output[0].split("|")
    if len(fields) != 5:
        raise RuntimeError("invalid journal inspection frame")
    return {name: int(value) for name, value in zip(("reserved","charged","entries","ids"),fields[1:])}, ms

def event(rec, name, expected, actual, observed_ms=None):
    passed = actual == expected
    rec.append({"check": name, "expected": expected, "observed": actual,
                "pass": passed, "elapsed_ms": observed_ms})
    return passed

def run_a(exe, mode, directory):
    started = time.monotonic()
    directory.mkdir(parents=True, exist_ok=True)
    records = []
    journal = directory / "normal.log"
    journal.write_text("")
    reply, ms = apply(exe, journal, mode)
    event(records,"normal_ack", ["ACK"], reply, ms)
    state, ms = inspect(exe, journal)
    event(records,"restart_recover_committed",TARGET,state,ms)
    reply, ms = apply(exe, journal, mode)
    event(records,"idempotent_retry",["DUPLICATE"],reply,ms)
    state, ms = inspect(exe, journal)
    event(records,"retry_does_not_duplicate_charge",TARGET,state,ms)
    for label, kw in [
        ("unapproved",{"ident":"B","charge":40,"consent":False}),
        ("capacity_exceeded",{"ident":"B","units":3,"charge":0}),
        ("spend_cap_exceeded",{"ident":"B","units":1,"charge":50,"cap":80})
    ]:
        isolated = directory / f"{label}.log"
        isolated.write_text("")
        resp, dur = apply(exe, isolated, mode, **kw)
        event(records,label+"_deny",["DENY"],resp,dur)
        state, dur = inspect(exe, isolated)
        event(records,label+"_unchanged",{"reserved":0,"charged":0,"entries":0,"ids":0},state,dur)
    return {
        "status": "PASS" if all(x["pass"] for x in records) else "BEHAVIOR_FAIL",
        "checks": records,
        "wall_ms": round((time.monotonic() - started)*1000,3),
    }

def read_protocol_line(proc, deadline):
    # Byte-wise reads avoid TextIOWrapper read-ahead hiding queued markers.
    value = bytearray()
    while True:
        left = deadline - time.monotonic()
        if left <= 0:
            raise RuntimeError("marker timeout")
        readers, _, _ = select.select([proc.stdout.fileno()], [], [], min(left, 0.3))
        if not readers:
            if proc.poll() is not None:
                raise RuntimeError("child exited before requested milestone")
            continue
        chunk = os.read(proc.stdout.fileno(), 1)
        if not chunk:
            raise RuntimeError("child EOF before milestone")
        if chunk == b"\n":
            return value.decode("ascii")
        value.extend(chunk)
        if len(value) > 128:
            raise RuntimeError("invalid oversized protocol marker")

def injected(exe, mode, point, journal):
    journal.write_text("")
    args = ["apply", str(journal), mode, point, "A", "1", "40", "2", "80", "true"]
    start = time.monotonic_ns()
    proc = subprocess.Popen([exe, *args], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    seen = []
    try:
        deadline = time.monotonic()+4
        while True:
            message = read_protocol_line(proc, deadline)
            seen.append(message)
            if message == POINTS[point]:
                break
            if message not in {"ACK"}:
                raise RuntimeError("unexpected pre-milestone marker: "+message)
        if proc.poll() is not None:
            raise RuntimeError("child exited before SIGKILL")
        os.kill(proc.pid, signal.SIGKILL)
        out, err = proc.communicate(timeout=3)
        returncode = proc.returncode
        if returncode != -signal.SIGKILL:
            raise RuntimeError(f"SIGKILL was not verified; exit={returncode}")
        state, recover_ms = inspect(exe, journal)
        expected_before = {"reserved":0,"charged":0,"entries":0,"ids":0}
        expected = expected_before if point=="before" else TARGET
        passing = state == expected
        retry_reply=None
        retry_state=None
        if point in ("before", "after_sync", "after_ack"):
            response, _ = apply(exe, journal, mode)
            retry_reply = response
            retry_state, _ = inspect(exe, journal)
            intended_reply = ["ACK"] if point=="before" else ["DUPLICATE"]
            passing = passing and response == intended_reply and retry_state == TARGET
        return {
            "point":point,"observed_markers":seen, "verified_signal":returncode,
            "recovered_state":state,"expected_recovered_state":expected,
            "retry_reply":retry_reply,"retry_state":retry_state,
            "journal_sha256":sha(journal),"journal_bytes":journal.stat().st_size,
            "passed":passing,
            "elapsed_ms":round((time.monotonic_ns()-start)/1e6,3),
            "recovery_inspect_ms":recover_ms,
        }
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.communicate(timeout=2)

def run_b(exe, mode, directory, repetitions):
    begin = time.monotonic()
    ordinary = run_a(exe, mode, directory / "regression")
    trials = []
    for point in POINTS:
        for rep in range(repetitions):
            j=directory / f"{point}-{rep}.log"
            trials.append({"repetition":rep, **injected(exe,mode,point,j)})
    return {
        "status": "PASS" if ordinary["status"]=="PASS"
            and all(x["passed"] for x in trials) else "BEHAVIOR_FAIL",
        "conventional_component":ordinary,
        "kill_trials":trials,
        "kill_checks_passed":sum(x["passed"] for x in trials),
        "kill_checks_failed":sum(not x["passed"] for x in trials),
        "wall_ms":round((time.monotonic()-begin)*1000,3),
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--rust",required=True)
    p.add_argument("--haskell",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--repetitions",type=int,default=5)
    args=p.parse_args()
    if not (5 <= args.repetitions <= 10):
        p.error("5..10 repetitions only")
    begin=time.monotonic()
    report={"schema_version":1,"study":"EDASES-P5","status":"ERROR",
            "source_plan_sha256":hashlib.sha256(PLAN.read_bytes()).hexdigest(),
            "methods":{
                "A":"conventional normal commit, process restart, retry, authorization and caps",
                "B":"same conventional checks plus marker-qualified SIGKILL, recovery and retry"
            },
            "implementations":{},"repetitions":args.repetitions,
            "instrument":"SIGKILL exact child at verified marker; separate recovery process",
            "not_tested":["power loss","disk cache loss","multi-process concurrency","distributed lock","production payments"],
            "complete_external_archive":"NOT_VERIFIED"}
    try:
        with tempfile.TemporaryDirectory(prefix="ases-p5-") as tmp:
            for language, exe in (("rust",args.rust),("haskell",args.haskell)):
                report["implementations"][language]={}
                for mode in MODES:
                    root=Path(tmp)/language/mode
                    a=run_a(exe,mode,root/"A")
                    b=run_b(exe,mode,root/"B",args.repetitions)
                    report["implementations"][language][mode]={"A":a,"B":b}
        for language in report["implementations"]:
            for mode, obj in report["implementations"][language].items():
                expectA="BEHAVIOR_FAIL" if mode=="duplicate" else "PASS"
                expectB="PASS" if mode=="correct" else "BEHAVIOR_FAIL"
                if obj["A"]["status"] != expectA or obj["B"]["status"] != expectB:
                    raise AssertionError(f"method sensitivity mismatch {language}/{mode}")
                if mode == "early_ack":
                    ack=[x for x in obj["B"]["kill_trials"] if x["point"]=="after_ack"]
                    if len(ack)!=args.repetitions or any(x["passed"] for x in ack):
                        raise AssertionError("early-ACK defect not reproduced at ack crash")
                if mode=="correct" and obj["B"]["kill_checks_failed"]:
                    raise AssertionError("correct variant violated crash durability invariant")
                if mode=="duplicate" and obj["B"]["kill_checks_failed"] < args.repetitions:
                    raise AssertionError("duplicate fault missing after durable checkpoint")
        report["status"]="PASS"
    except RuntimeError as error:
        report["status"]="INSTRUMENT_ERROR"
        report["error"]=str(error)[:900]
    except Exception as error:
        report["status"]="FAIL"
        report["error"]=f"{type(error).__name__}: {str(error)[:900]}"
    finally:
        report["wall_seconds"]=round(time.monotonic()-begin,4)
        out=Path(args.out)
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
        subset={}
        for lang, modes in report["implementations"].items():
            subset[lang]={}
            for mode,v in modes.items():
                subset[lang][mode]={
                    "A":v["A"]["status"],"B":v["B"]["status"],
                    "A_wall_ms":v["A"]["wall_ms"],"B_wall_ms":v["B"]["wall_ms"],
                    "B_kill_pass":v["B"]["kill_checks_passed"],"B_kill_fail":v["B"]["kill_checks_failed"],
                    "B_failures_by_point":{k:sum(x["point"]==k and not x["passed"]
                                               for x in v["B"]["kill_trials"]) for k in POINTS}
                }
        print("ASES_P5_SUMMARY="+json.dumps({
            "status":report["status"],"plan_sha256":report["source_plan_sha256"],
            "wall_seconds":report["wall_seconds"],"result_bytes":out.stat().st_size,
            "comparison":subset,"error":report.get("error"),
        },sort_keys=True))
    if report["status"]!="PASS":
        raise SystemExit(1)

if __name__=="__main__":
    main()
