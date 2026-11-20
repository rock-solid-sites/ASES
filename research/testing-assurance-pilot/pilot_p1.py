#!/usr/bin/env python3
"""EDASES P1: qualify controls against real compiled source mutants.

Pre-registered plan: research/testing-assurance-pilot/P1-PREREGISTERED-PLAN-2026-11-01.md
No production resources, provider APIs, account data, or real archive mutation.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUST = ROOT / "language-eval/rust"
HASKELL = ROOT / "language-eval/haskell/Main.hs"
PLAN = ROOT / "testing-assurance-pilot/P1-PREREGISTERED-PLAN-2026-11-01.md"
FIXTURES = ROOT / "language-eval/cases.json"

# These five literal expectations are frozen contract examples, NOT produced
# by the implementation's logic or the Python calculation oracle.
FROZEN = {
    "free-covered": (True, "admitted", 0),
    "free-spill-denied": (False, "paid-opt-in-required", 0),
    "free-spill-authorized": (True, "admitted", 10),
    "postpaid-unapproved": (False, "paid-opt-in-required", 0),
    "postpaid-authorized": (True, "admitted", 40),
}
NEGATIVE = ("free-spill-denied", "postpaid-unapproved")
POSITIVE = ("free-covered", "free-spill-authorized", "postpaid-authorized")
MUTATIONS = {
    "rust": {
        "bypass-paid-guard": (
            "if charge > 0 && !c.paid_opt_in {",
            "if charge > 0 && !c.paid_opt_in && false {",
        ),
        "reject-valid": (
            '    result(c, "admitted", charge)\n}',
            '    result(c, "unverified", 0)\n}',
        ),
    },
    "haskell": {
        "bypass-paid-guard": (
            '| charge > 0 && not (paidOptIn c) = deny "paid-opt-in-required"',
            '| charge > 0 && not (paidOptIn c) && False = deny "paid-opt-in-required"',
        ),
        "reject-valid": (
            '| otherwise = outcome "admitted" charge',
            '| otherwise = outcome "unverified" 0',
        ),
    },
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def run_process(command, *, input_text=None, timeout=120, env=None):
    before = time.monotonic()
    p = subprocess.run(
        list(map(str, command)), text=True, input=input_text,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
        timeout=timeout, check=False
    )
    return p, round((time.monotonic() - before) * 1000, 3)


def observe(exe, corpus):
    p, millis = run_process([exe], input_text=json.dumps(corpus), timeout=20)
    if p.returncode != 0:
        raise AssertionError(f"binary exited {p.returncode}: {p.stderr[:400]}")
    decoded = json.loads(p.stdout)
    if len(decoded) != len(FROZEN):
        raise AssertionError("not all frozen control results returned")
    actual = {}
    for row in decoded:
        if row["id"] not in FROZEN or row["id"] in actual:
            raise AssertionError("unexpected/duplicate control response")
        actual[row["id"]] = {
            "accepted": row["accepted"],
            "reason": row["reason"],
            "charge_cents": row["charge_cents"],
        }
    return actual, millis


def correct(row, case):
    return tuple(row[k] for k in ("accepted", "reason", "charge_cents")) == FROZEN[case]


def archive_check(root, manifest):
    problems = []
    for x in manifest:
        file = root / x["path"]
        if not file.is_file():
            problems.append({"path": x["path"], "reason": "MISSING"})
            continue
        data = file.read_bytes()
        if len(data) != x["size"] or digest(data) != x["sha256"]:
            problems.append({"path": x["path"], "reason": "CORRUPT"})
    return {"integrity": "COMPLETE" if not problems else "FAIL", "problems": problems}


def archive_fault_injection(tmp):
    root = tmp / "fake-archive"
    root.mkdir()
    a = root / "test-output.txt"
    b = root / "assumptions.txt"
    a.write_text("PASS: synthetic test only\n")
    b.write_text("Synthetic assumption; not a real production test\n")
    manifest = [{"path": f.name, "size": f.stat().st_size, "sha256": digest(f.read_bytes())}
                for f in (a, b)]
    good = archive_check(root, manifest)
    a.unlink()
    missing = archive_check(root, manifest)
    a.write_text("PASS: synthetic test only\n")
    b.write_text("Tampered assumption; not a real production test\n")
    corrupt = archive_check(root, manifest)
    ok = (good["integrity"] == "COMPLETE"
          and any(x["reason"] == "MISSING" for x in missing["problems"])
          and any(x["reason"] == "CORRUPT" for x in corrupt["problems"]))
    return {"qualified": ok, "intact": good, "deleted_fixture": missing,
            "altered_fixture": corrupt, "scope": "synthetic private test blobs only"}


def build_mutant(language, operator, source, tmp, original_rust_target):
    old, new = MUTATIONS[language][operator]
    if source.count(old) != 1:
        raise AssertionError(f"{language}/{operator}: expected one mutation anchor; got {source.count(old)}")
    mutated = source.replace(old, new, 1)
    src_dir = tmp / f"{language}-{operator}"
    src_dir.mkdir()
    if language == "rust":
        (src_dir / "src").mkdir()
        shutil.copy2(RUST / "Cargo.toml", src_dir / "Cargo.toml")
        (src_dir / "src/main.rs").write_text(mutated)
        cmd = ["cargo", "build", "--offline", "--release",
               "--manifest-path", src_dir / "Cargo.toml",
               "--target-dir", original_rust_target]
        executable = tmp / f"mutant-{language}-{operator}"
    else:
        (src_dir / "Main.hs").write_text(mutated)
        output = src_dir / "build"
        output.mkdir()
        executable = tmp / f"mutant-{language}-{operator}"
        cmd = ["ghc", "-O2", "-package", "aeson",
               "-outputdir", output, "-o", executable, src_dir / "Main.hs"]
    p, elapsed = run_process(cmd, timeout=180)
    if p.returncode != 0:
        raise RuntimeError(
            f"{language}/{operator} compile ERROR: {p.returncode}: {p.stderr[-1500:]}"
        )
    if language == "rust":
        shutil.copy2(Path(original_rust_target) / "release/ases-admit-rs", executable)
    return {
        "executable": str(executable),
        "source_sha256": digest(mutated.encode()),
        "build_elapsed_ms": elapsed,
        "operator": operator,
        "exact_source_replacement": {"from": old, "to": new},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rust", required=True)
    ap.add_argument("--haskell", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    started = time.monotonic()
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    originals = {"rust": (RUST / "src/main.rs").read_text(),
                 "haskell": HASKELL.read_text()}
    fixtures = {c["id"]: c for c in json.loads(FIXTURES.read_text())}
    if not PLAN.is_file():
        raise AssertionError("frozen plan absent")
    if set(FROZEN) - set(fixtures):
        raise AssertionError("frozen cases absent")
    corpus = [fixtures[k] for k in FROZEN]
    report = {
        "schema_version": 1,
        "pilot": "EDASES-P1",
        "status": "RUNNING",
        "frozen_plan_sha256": digest(PLAN.read_bytes()),
        "source_sha256": {k: digest(v.encode()) for k, v in originals.items()},
        "fixed_control_expectations": {
            case: {"accepted": val[0], "reason": val[1], "charge_cents": val[2]}
            for case, val in FROZEN.items()
        },
        "baseline": {},
        "mutants": [],
    }
    try:
        with tempfile.TemporaryDirectory(prefix="ases-assurance-pilot-") as dirpath:
            tmp = Path(dirpath)
            report["archive_fault_injection"] = archive_fault_injection(tmp)
            # Copy baseline binaries before Cargo changes the shared target path.
            baseline = {}
            for lang, orig in (("rust", args.rust), ("haskell", args.haskell)):
                exe = tmp / f"baseline-{lang}"
                shutil.copy2(orig, exe)
                baseline[lang] = exe
                result, ms = observe(str(exe), corpus)
                complete = all(correct(result[c], c) for c in FROZEN)
                report["baseline"][lang] = {
                    "valid": complete,
                    "observed": result,
                    "elapsed_ms": ms,
                }
                if not complete:
                    raise AssertionError(f"{lang}: baseline does not satisfy the frozen controls")

            for lang in ("rust", "haskell"):
                for operator in ("bypass-paid-guard", "reject-valid"):
                    built = build_mutant(lang, operator, originals[lang], tmp,
                                         str(RUST / "target"))
                    result, ms = observe(built["executable"], corpus)
                    # Intentionally faulty binaries MUST fail for expected cases.
                    if operator == "bypass-paid-guard":
                        violated = [k for k in NEGATIVE if not correct(result[k], k)
                                    and result[k]["accepted"]]
                        neighbors_ok = all(correct(result[k], k) for k in POSITIVE)
                        detected = len(violated) == len(NEGATIVE) and neighbors_ok
                    else:
                        violated = [k for k in POSITIVE if not correct(result[k], k)
                                    and not result[k]["accepted"]]
                        neighbors_ok = all(correct(result[k], k) for k in NEGATIVE)
                        detected = len(violated) == len(POSITIVE) and neighbors_ok
                    report["mutants"].append({
                        "language": lang,
                        "operator": operator,
                        "intended_failure_cases": list(NEGATIVE if operator == "bypass-paid-guard" else POSITIVE),
                        "observed_violation_cases": violated,
                        "neighbor_pass": neighbors_ok,
                        "detected": detected,
                        "observed": result,
                        "build_elapsed_ms": built["build_elapsed_ms"],
                        "execute_elapsed_ms": ms,
                        "source_sha256": built["source_sha256"],
                        "exact_source_replacement": built["exact_source_replacement"],
                    })

        report["qualification"] = (
            "QUALIFIED_FOR_SELECTED_CONTROLS"
            if (all(x["detected"] for x in report["mutants"])
                and report["archive_fault_injection"]["qualified"])
            else "UNQUALIFIED"
        )
        report["status"] = "PASS" if report["qualification"] == "QUALIFIED_FOR_SELECTED_CONTROLS" else "FAIL"
    except Exception as ex:
        report["status"] = "ERROR"
        report["execution_error"] = f"{type(ex).__name__}: {str(ex)[:1500]}"
    finally:
        report["total_pilot_elapsed_ms"] = round((time.monotonic() - started) * 1000, 3)
        report["method_limitations"] = [
            "Controls are attributable to the synthetic one-shot ASES admission contract only.",
            "Mutants do not establish complete specification or test-suite quality.",
            "Oracle and source may share incorrect product assumptions.",
            "Archive fault-injection tests the checker, not live CI export.",
            "External provider settlement, distributed concurrency, and independent review not tested.",
        ]
        destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps({
            "pilot": report["pilot"],
            "status": report["status"],
            "qualification": report.get("qualification", "UNRESOLVED"),
            "baseline_passed": {k: v["valid"] for k, v in report["baseline"].items()},
            "mutations_detected": sum(x["detected"] for x in report["mutants"]),
            "mutations_attempted": len(report["mutants"]),
            "archive_fault_checks_qualified": report.get("archive_fault_injection", {}).get("qualified"),
            "elapsed_ms": report["total_pilot_elapsed_ms"],
            "report_bytes": destination.stat().st_size,
        }, sort_keys=True))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
