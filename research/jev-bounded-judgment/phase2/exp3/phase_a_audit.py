#!/usr/bin/env python3
"""Phase A: validate the complete planned Experiment 3 batch with ZERO API spend.

Renders every request that Phase B would send and asserts, mechanically, that
each one carries:

  A1 the intended CASE QUESTION;
  A2 the intended EVIDENCE -- the state must be byte-identical to the corpus
     source for that module, and must match the packet's recorded sha256;
  A3 the intended ANSWER ALTERNATIVES for its arm:
       arm_a_forced            -> {yes, no}
       arm_b_explicit_unknown  -> {yes, no, insufficient_evidence}
  A4 the intended EXPERIMENTAL ARM, i.e. the instruction text is the one
     Experiment 1 used, byte for byte;
  A5 NO GROUND-TRUTH LEAK -- no case's ground-truth label appears anywhere in
     its own instruction in a way that could steer the answer. The ground truth
     is the token "yes" or "no", which also names an answer alternative, so the
     test is structural: the instruction must be identical across every case in
     an arm once the case-question line is removed. If one case carried extra
     text naming its own answer, that case's instruction would differ.
  A6 the arm pair for a case differs ONLY by the added option and its defining
     block -- the Experiment 1 matchedness property, re-asserted here;
  A7 counts match the packet's plan, so Phase B cannot silently send fewer
     requests than Phase A validated;
  A8 the PRE-REGISTERED RULES in the packet are identical to the ones declared
     in the frozen DESIGN.md. Without this the thresholds were merely recorded,
     not tamper-evident: nothing would stop a post-hoc edit of 0.05 or 0.86 in
     the packet, which is precisely the failure this experiment exists to rule
     out.

Makes no network call. Writes `frozen/phase_a_audit.json`.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE2 = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PHASE2, "harness"))

import extract  # noqa: E402
import importlib.util as il  # noqa: E402

_spec = il.spec_from_file_location(
    "rj", os.path.join(PHASE2, "harness", "run_jev.py"))
rj = il.module_from_spec(_spec)
_spec.loader.exec_module(rj)

PACKET = os.path.join(HERE, "frozen", "packet.json")
EXP1_PACKET = os.path.join(PHASE2, "exp1", "frozen", "packet.json")
OUT = os.path.join(HERE, "frozen", "phase_a_audit.json")

EXPECTED_OPTIONS = {
    "arm_a_forced": ["yes", "no"],
    "arm_b_explicit_unknown": ["yes", "no", "insufficient_evidence"],
}


def main():
    packet = json.load(open(PACKET, encoding="utf-8"))
    plan = packet["plan"]
    exp1_plan = json.load(open(EXP1_PACKET, encoding="utf-8"))["plan"]
    rows = packet["rows"]

    problems, checks = [], {}

    # ---- A4 arm instruction text is Experiment 1's, byte for byte ---------
    for arm in sorted(plan):
        if arm not in exp1_plan:
            problems.append(f"A4: arm {arm} absent from Experiment 1")
            continue
        if plan[arm]["instructions"] != exp1_plan[arm]["instructions"]:
            problems.append(f"A4: arm {arm} instruction text differs from "
                            f"Experiment 1")
        if plan[arm].get("options") != exp1_plan[arm].get("options"):
            problems.append(f"A4: arm {arm} option set differs from Experiment 1")

    # ---- A2 state is the corpus source, byte-identical --------------------
    src_cache, rendered = {}, {}
    for r in rows:
        m = r["module"]
        if m not in src_cache:
            src_cache[m] = extract.load_module(
                os.path.join(PHASE2, "corpus", m + ".py"), m)
        facts = src_cache[m]
        state, prov = rj.represent.build_state({"module": m}, "raw")
        digest = hashlib.sha256(state.encode("utf-8")).hexdigest()
        if digest != r["state_sha256"]:
            problems.append(f"A2: {r['case_id']} state sha256 drifted from the "
                            f"frozen packet")
        if state != facts.source:
            problems.append(f"A2: {r['case_id']} state is not the verbatim "
                            f"corpus source")
        if prov["state_bytes"] != r["state_bytes"]:
            problems.append(f"A2: {r['case_id']} state byte count disagrees")

    # ---- A1/A3/A5/A6 render every planned request -------------------------
    per_arm_suffix = {}
    n_rendered = 0
    for r in rows:
        for arm in sorted(plan):
            qid, q = rj.build_question(arm, plan[arm], r)
            inst = q.get("instructions", "")
            n_rendered += 1

            if r["question"] not in inst:
                problems.append(f"A1: {r['case_id']}/{arm} instruction lacks the "
                                f"case question")

            opts = list((q.get("criteria") or {}).keys())
            if opts != EXPECTED_OPTIONS[arm]:
                problems.append(f"A3: {r['case_id']}/{arm} alternatives {opts} "
                                f"!= {EXPECTED_OPTIONS[arm]}")

            # A5: strip the leading case-question line; the remainder must be
            # byte-identical across every case in this arm.
            suffix = inst.split("\n\n", 1)[1] if "\n\n" in inst else inst
            per_arm_suffix.setdefault(arm, set()).add(suffix)

            if arm == "arm_b_explicit_unknown" and \
                    r["unanswerable"] is False and \
                    "insufficient_evidence" in opts and \
                    opts != EXPECTED_OPTIONS[arm]:
                problems.append(f"A3: {r['case_id']} wrong alternatives")

            rendered.setdefault(r["case_id"], {})[arm] = {
                "question_id": qid, "type": q.get("type"),
                "alternatives": opts, "instruction_bytes": len(inst),
                "suffix_sha256": hashlib.sha256(
                    suffix.encode("utf-8")).hexdigest()}

    for arm, sufs in sorted(per_arm_suffix.items()):
        checks[f"A5_instruction_suffixes_identical_{arm}"] = len(sufs) == 1
        if len(sufs) != 1:
            problems.append(f"A5: arm {arm} instruction suffix differs across "
                            f"cases ({len(sufs)} distinct) -- a case may carry "
                            f"extra text naming its own answer")

    # ---- A6 arms differ only by option set + defining block ---------------
    # Structural test, no hardcoded wording. Arm B must equal arm A plus
    # exactly two things: the added option in the alternatives line, and a block
    # of extra lines defining that option. Normalising the added option out of
    # the alternatives line must leave arm A's lines as an IN-ORDER SUBSEQUENCE
    # of arm B's -- in-order so wording cannot have been reordered, subsequence
    # so only insertions are permitted. A raw substring test is wrong: the
    # alternatives line legitimately differs, so A's full text is never a
    # substring of B's.
    a_suf = (list(per_arm_suffix.get("arm_a_forced") or [None])[0])
    b_suf = (list(per_arm_suffix.get("arm_b_explicit_unknown") or [None])[0])
    a6_ok = False
    if a_suf and b_suf:
        norm = b_suf.replace(", `insufficient_evidence`", "")
        a_lines, b_lines = a_suf.split("\n"), norm.split("\n")
        it = iter(b_lines)
        a6_ok = all(any(x == y for y in it) for x in a_lines)
        if a6_ok:
            extra = len(b_lines) - len(a_lines)
            checks["A6_added_block_lines"] = extra
            if extra < 1:
                a6_ok = False
                problems.append("A6: arm B adds no defining block for the new "
                                "option")
        else:
            problems.append(
                "A6: arm A's lines are not an in-order subsequence of arm B's "
                "once the added option is normalised out, so the arms differ by "
                "more than the option and its definition")
    checks["A6_arms_differ_only_by_option_and_block"] = a6_ok

    # ---- A7 counts --------------------------------------------------------
    expected = len(rows) * len(plan)
    checks["A7_rendered_matches_plan"] = (n_rendered == expected)
    if n_rendered != expected:
        problems.append(f"A7: rendered {n_rendered} requests, packet plans "
                        f"{expected}")

    # ---- A8 pre-registration is tamper-evident ----------------------------
    # The packet records the rules; DESIGN.md declares them. Bind them together
    # so a post-hoc threshold edit has to edit a frozen, hashed file too.
    design = open(os.path.join(HERE, "DESIGN.md"), encoding="utf-8").read()
    pre = packet.get("preregistered_rules", {})
    # Match the THRESHOLD EXPRESSION, not surrounding prose. The invariant is
    # that 0.05 and 0.86 are unchanged; the sentence around them is wording and
    # must not be load-bearing, or an innocuous rephrase would read as tampering.
    want = {
        "explicit_unknown": "p(insufficient_evidence) >= 0.05",
        "external_gate": "p(ground_truth_option) >= 0.86",
    }
    a8_ok = True
    for key, expr in want.items():
        if key not in pre:
            a8_ok = False
            problems.append(f"A8: packet has no pre-registered rule for {key}")
            continue
        got = pre[key].get("rule", "")
        if expr not in got:
            a8_ok = False
            problems.append(
                f"A8: packet's {key} rule is {got!r}, which does not contain the "
                f"pre-registered expression {expr!r}")
        if expr not in design:
            a8_ok = False
            problems.append(
                f"A8: DESIGN.md no longer declares {expr!r} for {key}; the "
                f"pre-registration was edited")
    checks["A8_preregistration_matches_design"] = a8_ok
    checks["A8_declared_explicit_unknown_threshold"] = want["explicit_unknown"]
    checks["A8_declared_external_gate_threshold"] = want["external_gate"]

    audit = {
        "phase": "A",
        "api_spend": 0,
        "cases": len(rows),
        "arms": sorted(plan),
        "requests_rendered": n_rendered,
        "requests_planned": expected,
        "answerable": sum(1 for r in rows if not r["unanswerable"]),
        "unanswerable": sum(1 for r in rows if r["unanswerable"]),
        "checks": checks,
        "problems": sorted(set(problems)),
        "per_case_rendered": rendered,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(audit, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(f"phase A audit -> {OUT}")
    print(f"  cases={len(rows)} arms={len(plan)} "
          f"rendered={n_rendered} planned={expected} api_spend=0")
    for k, v in sorted(checks.items()):
        print(f"  {'OK  ' if v else 'FAIL'} {k}")
    if problems:
        print("  REJECTED:")
        for p in sorted(set(problems)):
            print("   -", p)
        return 1
    print("  Phase A PASS: every rendered request carries the intended question,")
    print("  evidence, answer alternatives and arm. Cleared for Phase B.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
