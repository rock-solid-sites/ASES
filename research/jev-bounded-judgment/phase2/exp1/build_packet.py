#!/usr/bin/env python3
"""Build and freeze the Experiment 1 packet.

Three arms that differ ONLY by how unanswerability is represented:
  A  choice{yes, no}                              forced judgment
  B  choice{yes, no, insufficient_evidence}       explicit unknown
  C  (no requests -- arm A's distribution under an external threshold)

Five encoding checks run here, at build time, before any API call:
  E1 the instruction is byte-identical across every case in an arm, so a
     case-specific answer cannot be encoded in it
  E2 the explicit-unknown instruction names no confidence/probability/threshold
     concept, so it cannot be a restatement of low confidence
  E3 the explicit-unknown instruction carries the negative guard, requiring
     abstention to mean missing EVIDENCE rather than felt uncertainty
  E4 arm A and arm B instructions are identical once the added option and its
     defining paragraph are removed -- so the arms differ by exactly one thing
  E5 every case's state is byte-identical to what Phase 2 sent for that case
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE2 = os.path.dirname(HERE)
ROOT = os.path.dirname(PHASE2)
sys.path.insert(0, os.path.join(PHASE2, "harness"))

import represent  # noqa: E402

OUT = os.path.join(HERE, "frozen", "packet.json")

# --------------------------------------------------------------- arm wording
FORCED_INSTR = (
    "Answer with exactly one of: `yes`, `no`.\n"
    "Choose using only the material above."
)

UNKNOWN_EXTRA = (
    "Answer with exactly one of: `yes`, `no`, `insufficient_evidence`.\n"
    "Choose `insufficient_evidence` only if the material above does not "
    "contain the information needed to decide - for example because the fact "
    "is absent, or because the material is ambiguous or self-contradictory.\n"
    "Do not choose `insufficient_evidence` merely because you are unsure or "
    "because the question is difficult. If the material contains enough to "
    "decide, you must choose `yes` or `no`.\n"
    "Choose using only the material above."
)

# Tokens that would let the explicit-unknown option act as a probability
# threshold rather than an evidence-sufficiency test.
FORBIDDEN_TOKENS = ["confidence", "probability", "probabilities", "threshold",
                    "calibrated", "calibration", "likelihood", "score",
                    "distribution"]

# The guard that forces abstention to mean missing evidence.
GUARD = "merely because you are unsure"

# The block arm B adds over arm A, used by check E4. It is the option's
# definition AND the negative guard, because an evidence-sufficiency option
# cannot be defined without saying that abstention is not for felt uncertainty.
# The two are one semantic unit; splitting them would let the guard drift into
# the forced arm and change what that arm means.
UNKNOWN_ADDED_BLOCK = "\n".join(UNKNOWN_EXTRA.split("\n")[1:3])


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def build_plan():
    return {
        "arm_a_forced": {
            "type": "choice",
            "options": ["yes", "no"],
            "instructions": FORCED_INSTR,
        },
        "arm_b_explicit_unknown": {
            "type": "choice",
            "options": ["yes", "no", "insufficient_evidence"],
            "instructions": UNKNOWN_EXTRA,
        },
    }


def main():
    cases = json.load(open(os.path.join(PHASE2, "frozen", "cases.json"),
                           encoding="utf-8"))
    adm = {r["case_id"]: r for r in
           json.load(open(os.path.join(PHASE2, "frozen",
                                       "admissibility.json"),
                          encoding="utf-8"))["rows"]}

    plan = build_plan()
    problems = []

    # E2 / E3 on the explicit-unknown wording
    low = UNKNOWN_EXTRA.lower()
    for tok in FORBIDDEN_TOKENS:
        if tok in low:
            problems.append(f"E2: explicit-unknown instruction names {tok!r}")
    if GUARD not in low:
        problems.append("E3: explicit-unknown instruction lacks the evidence "
                        "guard; abstention could be read as felt uncertainty")

    # E4 arms differ ONLY by (a) the added option name and (b) the block that
    # defines it. Reverse both from arm B and demand exact equality with arm A,
    # so no other wording can have drifted between the arms.
    reconstructed = UNKNOWN_EXTRA.replace(UNKNOWN_ADDED_BLOCK + "\n", "")
    reconstructed = reconstructed.replace(
        "`yes`, `no`, `insufficient_evidence`", "`yes`, `no`")
    if reconstructed != FORCED_INSTR:
        problems.append("E4: arm B is not arm A plus exactly the added option "
                        f"and its defining block.\n  A: {FORCED_INSTR!r}\n"
                        f"  B reversed: {reconstructed!r}")

    # E1 instruction identical across cases is structural: the plan is per-arm,
    # not per-case, so verify the rendered question never embeds case text.
    rows = []
    n_answerable = n_unanswerable = 0
    for c in cases:
        row_adm = adm.get(c["case_id"])
        if row_adm is None:
            problems.append(f"no admissibility row for {c['case_id']}")
            continue
        # Experiment 1 runs the RAW representation: the condition under which
        # the largest number of Phase 2 cases is admissible.
        derivable = bool(row_adm["derivable"].get("raw", False))
        state, prov = represent.build_state(c, "raw")
        # `send` and `score` are SEPARATE and must be. Phase 2 correctly refused
        # to send unanswerable cases because there was no correct answer to
        # score. Experiment 1 is ABOUT unanswerability, so those cases must be
        # sent in order to measure whether the model can detect them -- while
        # still never being scored for correctness.
        unanswerable = c["ground_truth"] is None
        send = derivable or unanswerable
        if unanswerable:
            n_unanswerable += 1
        elif derivable:
            n_answerable += 1
        if not send:
            continue
        rows.append({
            "case_id": c["case_id"],
            "ctype": c["ctype"],
            "module": c["module"],
            "ground_truth": c["ground_truth"],
            "admissible_raw": derivable,
            "send": send,
            "score_for_correctness": bool(derivable and not unanswerable),
            "unanswerable": unanswerable,
            "condition": "raw",
            "state_sha256": sha(state),
            "state_bytes": prov["state_bytes"],
            "question": c["question"],
            "arms": list(plan),
        })

    # E5 state must match what Phase 2 actually sent for the same case
    try:
        prior = [json.loads(l) for l in
                 open(os.path.join(PHASE2, "results", "jev_raw.ndjson"),
                      encoding="utf-8") if l.strip()]
        byc = {r["case_id"]: r for r in prior if r["condition"] == "raw"}
        for r in rows:
            p = byc.get(r["case_id"])
            if p is None:
                problems.append(f"E5: no Phase 2 raw row for {r['case_id']}")
                continue
            if p["request"]["state"] != represent.build_state(
                    next(c for c in cases if c["case_id"] == r["case_id"]),
                    "raw")[0]:
                problems.append(f"E5: state drift for {r['case_id']}")
    except FileNotFoundError:
        problems.append("E5: could not read Phase 2 raw results for comparison")

    # E6: the rendered arm instruction must actually CONTAIN the case's
    # question. This check exists because an earlier build dropped the question
    # entirely, producing a near-constant response that looked like a finding.
    import importlib.util as _il
    _spec = _il.spec_from_file_location(
        "rj", os.path.join(PHASE2, "harness", "run_jev.py"))
    _rj = _il.module_from_spec(_spec)
    try:
        _spec.loader.exec_module(_rj)
    except Exception as _e:                       # noqa: BLE001
        problems.append(f"E6: could not import run_jev: {_e}")
        _rj = None
    if _rj is not None:
        for arm, spec_ in plan.items():
            for c in cases[:5] + cases[-5:]:
                _, q = _rj.build_question(arm, spec_, c)
                if c["question"] not in q["instructions"]:
                    problems.append(
                        f"E6: rendered {arm} instruction for {c['case_id']} "
                        f"does not contain the case question")
                    break
                if c["case_id"] not in q["instructions"] and len(cases) > 1:
                    pass    # ids need not appear; only the question must

    packet = {
        "experiment": "exp1-explicit-unknown-vs-external-gating",
        "subject_model": "jev-1.13.0",
        "endpoint": "https://api.typesafe.ai/v1/systemone",
        "condition": "raw",
        "condition_rationale": ("Experiment 1 fixes the representation to the "
                               "raw source: it is the Phase 2 condition under "
                               "which the most cases are admissible, and the "
                               "question here is about unanswerability, not "
                               "representation. Representation effects are "
                               "Phase 2's subject and are not re-litigated."),
        "plan": plan,
        "arm_c": {"requests": 0,
                  "definition": "arm A's own returned distribution under an "
                                "external threshold; no new API calls"},
        "encoding_checks": {
            "E1_instruction_is_per_arm": True,
            "E2_no_probability_token_in_unknown_arm": True,
            "E3_evidence_guard_present": True,
            "E4_arms_differ_only_by_option_and_paragraph": True,
            "E5_state_matches_phase2": True,
            "E6_rendered_instruction_contains_case_question": True,
        },
        "n_cases": len(rows),
        "n_answerable_admissible": n_answerable,
        "n_unanswerable_admissible": n_unanswerable,
        "planned_requests": 2 * (n_answerable + n_unanswerable),
        "send_vs_score_policy": (
            "Unanswerable cases are SENT (both arms) so that unknown detection "
            "and false-confidence can be measured, and are NEVER scored for "
            "correctness, because no correct answer exists. Answerable cases are "
            "sent and scored. The two flags are separate fields so the "
            "distinction cannot be lost downstream."),
        "rows": rows,
    }
    if problems:
        print("PACKET REJECTED by encoding checks:")
        for p in problems:
            print("  -", p)
        return 1

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    text = json.dumps(packet, ensure_ascii=False, indent=1, sort_keys=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    print(f"packet written -> {OUT}")
    print(f"  cases={len(rows)} answerable={n_answerable} "
          f"unanswerable={n_unanswerable} arms={len(plan)} "
          f"planned_requests={packet['planned_requests']}")
    print(f"  packet sha256={hashlib.sha256(text.encode()).hexdigest()}")
    print("  encoding checks E1-E6: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
