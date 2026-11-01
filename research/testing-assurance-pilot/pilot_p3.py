#!/usr/bin/env python3
"""EDASES P3 — compare three test suites on unlike safety-rule source mutants.

Research-only. Builds temporary source copies. No production/provider contact.
Pre-registration: P3-PREREGISTERED-PLAN-2026-11-01.md.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
from collections import Counter
from pathlib import Path

from pilot_p1 import FROZEN
from compare import make_generated, oracle

BASE = Path(__file__).resolve().parent.parent
LANG = BASE / "language-eval"
PLAN = BASE / "testing-assurance-pilot/P3-PREREGISTERED-PLAN-2026-11-01.md"
MAX_DIFF_PREVIEW = 8

MUTANTS = {
    "rust": {
        "capacity": (
            'if c.reserved > c.capacity || c.requested > c.capacity - c.reserved {',
            'if false { // P3 mutant: capacity guard disabled'
        ),
        "wallet-floor": (
            'if c.wallet < c.wallet_floor || charge > c.wallet - c.wallet_floor {',
            'if false { // P3 mutant: wallet-floor guard disabled'
        ),
        "spend-cap": (
            '} else if c.liability > c.spend_cap || charge > c.spend_cap - c.liability {',
            '} else if false { // P3 mutant: spend-cap guard disabled'
        ),
    },
    "haskell": {
        "capacity": (
            '| reserved c > capacity c || requested c > capacity c - reserved c = deny "capacity-exceeded"',
            '| False = deny "capacity-exceeded" -- P3 mutant'
        ),
        "wallet-floor": (
            '| fundingMode c == "prepaid" && (wallet c < walletFloor c',
            '| fundingMode c == "prepaid" && False && (wallet c < walletFloor c'
        ),
        "spend-cap": (
            '| fundingMode c /= "prepaid" && (liability c > spendCap c',
            '| fundingMode c /= "prepaid" && False && (liability c > spendCap c'
        ),
    }
}

NEW_EXPECTED = {
    "capacity-exact-p3": (True, "admitted", 0),
    "capacity-over-p3": (False, "capacity-exceeded", 0),
    "wallet-exact-p3": (True, "admitted", 40),
    "wallet-over-p3": (False, "wallet-floor-exceeded", 0),
    "spend-exact-p3": (True, "admitted", 40),
    "spend-over-p3": (False, "spend-cap-exceeded", 0)
}
WITNESSES = {
    "capacity": ("capacity-exact-p3", "capacity-over-p3"),
    "wallet-floor": ("wallet-exact-p3", "wallet-over-p3"),
    "spend-cap": ("spend-exact-p3", "spend-over-p3")
}


def hashtext(text):
    return hashlib.sha256(text.encode()).hexdigest()


def actual_dict(expected, item_id):
    accepted, reason, charge = expected
    return {"id": item_id, "accepted": accepted, "reason": reason,
            "charge_cents": charge}


def fixtures():
    original = json.loads((LANG / "cases.json").read_text())
    golden = json.loads((LANG / "expected.json").read_text())
    if len(original) != len(golden):
        raise AssertionError("handwritten corpus/golden lengths differ")
    for index, (c, want) in enumerate(zip(original, golden)):
        if oracle(c) != want:
            raise AssertionError(f"existing oracle/golden conflict at {index}")
    base = dict(original[0])
    p1cases = [{**next(c for c in original if c["id"] == key)}
               for key in FROZEN]
    p1want = [actual_dict(FROZEN[c["id"]], c["id"]) for c in p1cases]
    generated = make_generated()
    legacy_cases = original + generated
    legacy_want = golden + [oracle(c) for c in generated]

    new = []
    new.append(dict(base, id="capacity-exact-p3",
                    capacity=16, reserved=4, requested=12))
    new.append(dict(base, id="capacity-over-p3",
                    capacity=16, reserved=4, requested=13))
    for id_, wallet in (("wallet-exact-p3", 50), ("wallet-over-p3", 49)):
        new.append(dict(base, id=id_, mode="prepaid", usage=20, rate=2,
                        paid_opt_in=True, wallet=wallet, wallet_floor=10))
    for id_, liability in (("spend-exact-p3", 60), ("spend-over-p3", 61)):
        new.append(dict(base, id=id_, mode="postpaid", usage=20, rate=2,
                        paid_opt_in=True, spend_cap=100, liability=liability))
    if [c["id"] for c in new] != list(NEW_EXPECTED):
        raise AssertionError("unexpected boundary control order")
    new_want = [actual_dict(NEW_EXPECTED[c["id"]], c["id"]) for c in new]
    return {
        "p1-five": (p1cases, p1want),
        "legacy-full": (legacy_cases, legacy_want),
        "p3-new-boundaries": (new, new_want)
    }


def execute(exe, cases):
    start = time.monotonic_ns()
    proc = subprocess.run([str(exe)], input=json.dumps(cases),
                          text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=35, check=False)
    elapsed = round((time.monotonic_ns() - start) / 1_000_000, 3)
    if proc.returncode:
        raise RuntimeError(
            f"executable returned {proc.returncode}: {proc.stderr[:600]}"
        )
    got = json.loads(proc.stdout)
    if not isinstance(got, list) or len(got) != len(cases):
        raise RuntimeError("invalid result type or result count")
    return got, elapsed


def compare_results(got, expected):
    mismatches = []
    for row, correct in zip(got, expected):
        if row != correct:
            mismatches.append({
                "id": correct["id"],
                "expected": correct,
                "observed": row
            })
    return {
        "checked": len(expected),
        "mismatch_count": len(mismatches),
        "first_mismatches": mismatches[:MAX_DIFF_PREVIEW],
        "mismatch_reason_histogram": dict(sorted(Counter(
            m["expected"]["reason"] for m in mismatches).items()))
    }


def mutate_and_compile(lang, kind, raw, temp_dir, rust_target):
    before, after = MUTANTS[lang][kind]
    if raw.count(before) != 1:
        raise RuntimeError(f"{lang}/{kind}: anchor count {raw.count(before)}")
    changed = raw.replace(before, after, 1)
    target = temp_dir / (lang + "-" + kind)
    target.mkdir()
    binary = target / "candidate"
    if lang == "rust":
        (target / "src").mkdir()
        shutil.copy2(LANG / "rust/Cargo.toml", target / "Cargo.toml")
        (target / "src/main.rs").write_text(changed)
        cmd = ["cargo", "build", "--offline", "--release", "--manifest-path",
               str(target / "Cargo.toml"), "--target-dir", str(rust_target)]
    else:
        (target / "Main.hs").write_text(changed)
        (target / "build").mkdir()
        cmd = ["ghc", "-O2", "-package", "aeson", "-outputdir",
               str(target / "build"), "-o", str(binary),
               str(target / "Main.hs")]
    started = time.monotonic_ns()
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=180, check=False)
    duration = round((time.monotonic_ns() - started) / 1_000_000, 3)
    if proc.returncode:
        raise RuntimeError(
            f"{lang}/{kind}: COMPILER ERROR: {proc.stderr[-1300:]}"
        )
    if lang == "rust":
        shutil.copy2(rust_target / "release/ases-admit-rs", binary)
    return binary, {
        "operator": kind,
        "source_sha256": hashtext(changed),
        "exact_replacement": {"from": before, "to": after},
        "build_elapsed_ms": duration
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rust", required=True)
    parser.add_argument("--haskell", required=True)
    parser.add_argument("--out", required=True)
    arguments = parser.parse_args()
    out = Path(arguments.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic_ns()
    report = {
        "schema_version": 1,
        "pilot": "EDASES-P3",
        "plan_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
        "status": "ERROR",
        "baseline": {},
        "mutants": [],
        "suite_definitions": {},
        "limitations": [
            "Hand-selected mutations are not a general mutation-score estimate",
            "Existing generated suite shares logic with a Python reference oracle",
            "Neither system is a real concurrent funding or reservation engine",
            "Compilers and test execution are not production infrastructure",
            "Complete external archive is NOT_VERIFIED until independently stored"
        ]
    }
    try:
        suites = fixtures()
        report["suite_definitions"] = {k: {"cases": len(v[0])}
                                       for k, v in suites.items()}
        originals = {
            "rust": (LANG / "rust/src/main.rs").read_text(),
            "haskell": (LANG / "haskell/Main.hs").read_text()
        }
        report["source_sha256"] = {k: hashtext(v)
                                   for k, v in originals.items()}
        with tempfile.TemporaryDirectory(prefix="ases-p3-") as t:
            temp = Path(t)
            baseline = {}
            for lang, executable in (("rust", arguments.rust),
                                      ("haskell", arguments.haskell)):
                copied = temp / ("original-" + lang)
                shutil.copy2(executable, copied)
                baseline[lang] = copied
                checks = {}
                for suite, (cases, expected) in suites.items():
                    got, elapsed = execute(copied, cases)
                    check = compare_results(got, expected)
                    check["execute_elapsed_ms"] = elapsed
                    checks[suite] = check
                    if check["mismatch_count"]:
                        raise RuntimeError(
                            f"{lang} baseline violated {suite} on {check['first_mismatches']}"
                        )
                report["baseline"][lang] = checks
            rust_target = LANG / "rust/target"
            for lang in ("rust", "haskell"):
                for kind in MUTANTS[lang]:
                    binary, provenance = mutate_and_compile(
                        lang, kind, originals[lang], temp, rust_target)
                    checks = {}
                    new_actual = None
                    for suite, (cases, expected) in suites.items():
                        got, elapsed = execute(binary, cases)
                        check = compare_results(got, expected)
                        check["execute_elapsed_ms"] = elapsed
                        checks[suite] = check
                        if suite == "p3-new-boundaries":
                            new_actual = {item["id"]: item for item in got}
                    positive, negative = WITNESSES[kind]
                    if not (new_actual[positive] ==
                            actual_dict(NEW_EXPECTED[positive], positive)):
                        raise RuntimeError(
                            f"{lang}/{kind}: positive boundary is not preserved"
                        )
                    neg_expected = actual_dict(NEW_EXPECTED[negative], negative)
                    if new_actual[negative] == neg_expected:
                        raise RuntimeError(
                            f"{lang}/{kind}: matching negative boundary did not expose mutant"
                        )
                    report["mutants"].append({
                        "language": lang, "kind": kind,
                        "build": provenance,
                        "suite_results": checks,
                        "positive_boundary": positive,
                        "negative_boundary": negative,
                        "actual_positive": new_actual[positive],
                        "actual_negative": new_actual[negative],
                        "boundary_detected": True
                    })
        report["status"] = "PASS"
        report["summary"] = {
            "mutants_compiled": len(report["mutants"]),
            "new_boundary_detected": sum(x["boundary_detected"]
                                         for x in report["mutants"]),
            "caught_by_original_five": sum(
                x["suite_results"]["p1-five"]["mismatch_count"] > 0
                for x in report["mutants"]),
            "caught_by_existing_full": sum(
                x["suite_results"]["legacy-full"]["mismatch_count"] > 0
                for x in report["mutants"]),
            "caught_by_new_boundaries": sum(
                x["suite_results"]["p3-new-boundaries"]["mismatch_count"] > 0
                for x in report["mutants"])
        }
    except Exception as error:
        report["status"] = "ERROR"
        report["error"] = str(error)[:1500]
    finally:
        report["total_pilot_elapsed_ms"] = round(
            (time.monotonic_ns() - started) / 1_000_000, 3)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print("ASES_P3_RESULT=" + json.dumps({
            "status": report["status"],
            "summary": report.get("summary"),
            "error": report.get("error"),
            "total_pilot_elapsed_ms": report["total_pilot_elapsed_ms"],
            "result_bytes": out.stat().st_size,
            "plan_sha256": report["plan_sha256"]
        }, sort_keys=True))
        print("ASES_P3_FULL_JSON=" + json.dumps(report, separators=(",", ":"),
                                               sort_keys=True))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
