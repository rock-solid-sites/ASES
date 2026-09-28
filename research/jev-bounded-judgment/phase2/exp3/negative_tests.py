#!/usr/bin/env python3
"""Non-vacuity tests for Experiment 3's controls.

A control that never rejects anything is not a control. Each case below tampers
with exactly one thing and asserts the named check fires. Runs offline; makes
no API call and does not touch the frozen packet, which is restored and
re-verified at the end.

Run:  python3 exp3/negative_tests.py
"""
import copy
import importlib.util as il
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE2 = os.path.dirname(HERE)
PK = os.path.join(HERE, "frozen", "packet.json")
AUDIT = os.path.join(PHASE2, "exp3", "phase_a_audit.py")

sys.path.insert(0, os.path.join(PHASE2, "harness"))
bp_spec = il.spec_from_file_location(
    "bp", os.path.join(HERE, "build_packet.py"))


def load():
    return json.load(open(PK, encoding="utf-8"))


def run_audit():
    p = subprocess.run([sys.executable, AUDIT], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def run_build():
    p = subprocess.run([sys.executable, os.path.join(HERE, "build_packet.py")],
                       capture_output=True, text=True, cwd=HERE)
    return p.returncode, p.stdout + p.stderr


def main():
    good = load()
    backup = copy.deepcopy(good)
    results = []

    def check(name, expect_substr, fn):
        fn()
        rc, out = run_audit()
        rc2, out2 = run_build()
        blob = out + out2
        fired = expect_substr in blob
        rejected = rc != 0 or rc2 != 0
        results.append({
            "tamper": name,
            "expected_signal": expect_substr,
            "signal_present": fired,
            "rejected": rejected,
            "pass": fired and rejected,
        })
        # restore
        json.dump(backup, open(PK, "w", encoding="utf-8"),
                  indent=1, sort_keys=True)

    def t_leak():
        pk = load()
        pk["plan"]["arm_b_explicit_unknown"]["instructions"] += \
            "\nThe answer is `no`."
        json.dump(pk, open(PK, "w", encoding="utf-8"), indent=1, sort_keys=True)

    def t_reword():
        # Reorder arm A's lines relative to arm B: matchedness must break.
        pk = load()
        pk["plan"]["arm_a_forced"]["instructions"] = (
            "Choose using only the material above.\n"
            "Answer with exactly one of: `yes`, `no`.")
        json.dump(pk, open(PK, "w", encoding="utf-8"), indent=1, sort_keys=True)

    def t_alts():
        # Drop an answer alternative from the forced arm.
        pk = load()
        pk["plan"]["arm_a_forced"]["options"] = ["yes"]
        json.dump(pk, open(PK, "w", encoding="utf-8"), indent=1, sort_keys=True)

    def t_threshold():
        # Post-hoc threshold edit: the pre-registration must be tamper-evident.
        pk = load()
        pk["preregistered_rules"]["explicit_unknown"]["rule"] = \
            "p(insufficient_evidence) >= 0.30"
        json.dump(pk, open(PK, "w", encoding="utf-8"), indent=1, sort_keys=True)

    def t_state():
        # Point a case at a different module's state.
        pk = load()
        for r in pk["rows"]:
            if r["module"] != "shlex":
                r["module"] = "shlex"
                break
        json.dump(pk, open(PK, "w", encoding="utf-8"), indent=1, sort_keys=True)

    check("instruction leaks a case answer", "A5", t_leak)
    check("arm wording reordered (matchedness)", "A4", t_reword)
    check("answer alternative removed", "A3", t_alts)
    check("state repointed to another module", "A2", t_state)
    check("pre-registered threshold edited post hoc", "A8", t_threshold)

    # ---- builder-side controls (F-checks) ---------------------------------
    pool_path = os.path.join(HERE, "frozen", "pool.json")
    pool_backup = json.load(open(pool_path, encoding="utf-8"))

    def restore_pool():
        json.dump(pool_backup, open(pool_path, "w", encoding="utf-8"),
                  indent=1, sort_keys=True)

    def do_f2():
        # Overwrite EVERY direct_call candidate for one module with an Exp 1
        # edge. A partial tamper is not a test: round_robin sorts candidates, so
        # editing one entry may simply not get selected, and the control would
        # look vacuous when it was never exercised.
        pool = json.load(open(pool_path, encoding="utf-8"))
        frozen = json.load(open(os.path.join(PHASE2, "frozen", "cases.json"),
                                encoding="utf-8"))
        edge = next((c["params"]["caller"], c["params"]["callee"])
                    for c in frozen if c["ctype"] == "direct_call")
        n = 0
        for c in pool["direct_call"]:
            if c["module"] == "shlex":
                c["params"] = {"caller": edge[0], "callee": edge[1]}
                c["question"] = (f"In this module, does `{edge[0]}` directly "
                                 f"call `{edge[1]}`?")
                c["polarity"] = "yes"
                n += 1
        json.dump(pool, open(pool_path, "w", encoding="utf-8"), indent=1,
                  sort_keys=True)
        rc, out = run_build()
        results.append({"tamper": f"pool reuses an Exp 1 call edge (n={n})",
                        "expected_signal": "F2", "signal_present": "F2" in out,
                        "rejected": rc != 0,
                        "pass": "F2" in out and rc != 0})
        restore_pool()

    def do_f4():
        # Flip EVERY direct_call polarity hint, so whichever candidates are
        # selected all disagree with the independent recomputation.
        pool = json.load(open(pool_path, encoding="utf-8"))
        n = 0
        for c in pool["direct_call"]:
            c["polarity"] = "no" if c["polarity"] == "yes" else "yes"
            n += 1
        json.dump(pool, open(pool_path, "w", encoding="utf-8"), indent=1,
                  sort_keys=True)
        rc, out = run_build()
        results.append({"tamper": f"pool polarity hints flipped (n={n})",
                        "expected_signal": "F4",
                        "signal_present": "F4" in out, "rejected": rc != 0,
                        "pass": "F4" in out and rc != 0})
        restore_pool()

    do_f2()
    do_f4()

    # ---- restore and re-verify -------------------------------------------
    json.dump(backup, open(PK, "w", encoding="utf-8"), indent=1, sort_keys=True)
    restore_pool()
    rc, out = run_audit()
    rc2, out2 = run_build()
    clean = rc == 0 and rc2 == 0

    report = {
        "purpose": "prove each Experiment 3 control actually rejects its tamper "
                   "class, so none is vacuous",
        "cases": results,
        "n_cases": len(results),
        "n_pass": sum(1 for r in results if r["pass"]),
        "restored_and_clean": clean,
    }
    with open(os.path.join(HERE, "negative_tests.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
        fh.write("\n")
    for r in results:
        print(f"  {'PASS' if r['pass'] else 'FAIL'}  {r['tamper']:44s} "
              f"-> {r['expected_signal']}")
    print(f"  {report['n_pass']}/{report['n_cases']} controls non-vacuous; "
          f"restored packet re-audits clean: {clean}")
    return 0 if all(r["pass"] for r in results) and clean else 1


if __name__ == "__main__":
    raise SystemExit(main())
