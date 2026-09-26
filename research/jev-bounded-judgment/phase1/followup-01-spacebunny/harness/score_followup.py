#!/usr/bin/env python3
"""followup-01-spacebunny scorer — deterministic scoring of the new baseline.

Compares the ONE new `spacebunny` run against the FROZEN Jev results and the
FROZEN `general_model` results, under two ground-truth views:

  raw_gt            the committed corpus labels as-is (50 answerable / 14
                    unanswerable).
  f1_corrected_gt   `verification.md` §2 F1 applied: c-p4a and c-p4b are
                    reclassified UNANSWERABLE, because their ground truth is
                    not derivable from the model-visible text. Answerable
                    becomes 48, unanswerable 16. The correction is applied
                    IDENTICALLY to all three mechanisms, so it is a change of
                    the yardstick, not a change of any subject's score.

The frozen scorer is reused rather than re-implemented: `build_cell`, `_acc`,
`load_ndjson`, `sha256_file`, `frac`, `r4`, `pct`, `pp` and `_paired_gain` are
imported from `../../harness/score.py`, and `load_cases` from
`../../harness/common.py`.

DENOMINATORS ARE STATED, NEVER IMPLIED
--------------------------------------
`acc_answerable` divides by the number of **usable** cells in the answerable
set. A cell is usable when the mechanism emitted a label. Transport failures
(no label) are therefore EXCLUDED from the semantic denominator and reported
separately, exactly as the brief requires. Every accuracy block carries
`n_answerable`, `n_usable_in_answerable`, `n_transport_failures_in_answerable`
and `n_correct` so the division is checkable by hand. Two bounded sensitivity
variants are also reported: counting every transport failure as an error, and
counting every one as correct.

BAND EVALUATION
---------------
The decision bands from `findings.md` §6 are applied verbatim to the
F1-corrected semantic accuracy. They were pre-registered for a CROSS-FAMILY
model; this run uses a SAME-FAMILY model, which is disclosed in the output and
in `comparison.md`, and it does not change the arithmetic.

Usage:
    python3 harness/score_followup.py
    python3 harness/score_followup.py --self-check     # score twice, diff
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FOLLOWUP = os.path.dirname(HERE)
PHASE1 = os.path.dirname(FOLLOWUP)
PHASE1_HARNESS = os.path.join(PHASE1, "harness")
sys.path.insert(0, PHASE1_HARNESS)

from common import load_cases, utc_now_iso  # noqa: E402
from score import (  # noqa: E402
    _acc,
    _paired_gain,
    build_cell,
    frac,
    git,
    load_ndjson,
    pct,
    pp,
    r4,
    sha256_file,
)

SCORER_VERSION = "1.0.0"
COMPARISON_SCHEMA_VERSION = "jevp1-followup-comparison-1.0"

AREAS = ("A", "B", "C", "D")
SPLITS = ("train", "dev", "test")
QTYPE_ORDER = ("noul", "choice", "score")

JEV = "jev"
FROZEN_GENERAL = "general_model"
NEW = "spacebunny"
MECHS = (JEV, FROZEN_GENERAL, NEW)

# verification.md §2 F1: cp4's ground truth is not derivable from the
# model-visible text; both members are reclassified unanswerable.
F1_PAIR_ID = "cp4"

# The three frozen digests, re-verified here so a score can never be produced
# from drifted inputs.
FROZEN_INPUTS = {
    "cases.ndjson":
        "7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c",
    "results/jev_raw.ndjson":
        "e17ae014f0fc6cc311646dbfd98d5115d41854ddfcb98cfb41268f2da482d3bc",
    "results/baselines_raw.ndjson":
        "42f37690ec7ebbca75293ab0a690dc8efd8d5ef8a6a663db632bb05d682bf7ba",
}

# findings.md §6, transcribed verbatim. No threshold is invented or moved.
BAND_SUPPORT_MAX_ACC = 0.90
BAND_SUPPORT_MIN_C = 3
BAND_REFUTE_MIN_ACC = 0.96
BAND_REFUTE_MAX_C = 1
BAND_UNINFORMATIVE_LO = 0.92
BAND_UNINFORMATIVE_HI = 0.94
BAND_SOURCE = "findings.md §6 (pre-registered before this run)"


def verify_frozen_inputs():
    got = {}
    for rel, expect in FROZEN_INPUTS.items():
        path = os.path.join(PHASE1, rel)
        digest = sha256_file(path)
        got[rel] = {"expected": expect, "actual": digest, "match": digest == expect}
        if digest != expect:
            raise SystemExit(
                f"FROZEN INPUT MISMATCH {rel}: expected {expect}, found {digest}. "
                "Refusing to score.")
    return got


def load_mechanism_rows():
    """mechanism -> {case_id: raw row}, from frozen + new files."""
    out = {JEV: {}, FROZEN_GENERAL: {}, NEW: {}}
    src = {
        JEV: os.path.join(PHASE1, "results", "jev_raw.ndjson"),
        FROZEN_GENERAL: os.path.join(PHASE1, "results", "baselines_raw.ndjson"),
        NEW: os.path.join(FOLLOWUP, "results", "spacebunny_raw.ndjson"),
    }
    for mech, path in src.items():
        for row in load_ndjson(path):
            if row["mechanism"] == mech:
                if row["case_id"] in out[mech]:
                    raise SystemExit(
                        f"DUPLICATE {mech} row for {row['case_id']} in {path}")
                out[mech][row["case_id"]] = row
        if len(out[mech]) != 64:
            raise SystemExit(
                f"{mech}: expected 64 rows, found {len(out[mech])} in {path}")
    return out, src


def f1_corrected_cases(cases):
    """Cases with the F1 correction applied (cp4 both members unanswerable).

    The pair is DERIVED from `control.pair_id`, not hardcoded, and then checked
    against the ids verification.md F1 names. A mismatch is a hard stop: the
    correction must be exactly the documented one.
    """
    members = [c for c in cases if c["control"]["pair_id"] == F1_PAIR_ID]
    ids = sorted(c["id"] for c in members)
    if ids != ["c-p4a", "c-p4b"]:
        raise SystemExit(
            f"F1 CORRECTION FAIL: pair {F1_PAIR_ID} is {ids}, expected "
            "['c-p4a', 'c-p4b'] as named in verification.md §2 F1")
    for c in members:
        if not c["ground_truth"]["answerable"]:
            raise SystemExit(
                f"F1 CORRECTION FAIL: {c['id']} is already unanswerable in the "
                "committed corpus; the correction would be a no-op")
    corrected = []
    for c in cases:
        if c["id"] in ids:
            d = copy.deepcopy(c)
            d["ground_truth"]["answerable"] = False
            d["ground_truth"]["answer"] = None
            d["ground_truth"]["abstain_expected"] = True
            d["_f1_corrected"] = True
            corrected.append(d)
        else:
            d = copy.deepcopy(c)
            d["_f1_corrected"] = False
            corrected.append(d)
    return corrected, ids


# ---------------------------------------------------------------------------
# accuracy, with denominators stated
# ---------------------------------------------------------------------------
def acc_block(cells, label):
    """Accuracy over the ANSWERABLE cells of `cells`, denominators stated.

    The point estimate divides by usable cells only. `transport_*` carries the
    two bounded sensitivity variants.
    """
    ans = [c for c in cells if not c["unanswerable"]]
    usable = [c for c in ans if c["usable"]]
    n_correct = sum(1 for c in usable if c["correct"])
    n_transport = len(ans) - len(usable)
    unans = [c for c in cells if c["unanswerable"]]
    return {
        "scope": label,
        "n_answerable": len(ans),
        "n_usable_in_answerable": len(usable),
        "n_transport_failures_in_answerable": n_transport,
        "n_correct": n_correct,
        "n_semantic_errors": len(usable) - n_correct,
        "acc_answerable": frac(n_correct, len(usable)),
        "acc_pct": pct(frac(n_correct, len(usable))),
        "denominator": "usable answerable cells (transport failures excluded "
                       "and reported separately)",
        "transport_sensitivity": {
            "if_transport_counted_as_error": frac(n_correct, len(ans)),
            "if_transport_counted_as_error_pct": pct(frac(n_correct, len(ans))),
            "if_transport_counted_as_correct": frac(n_correct + n_transport, len(ans)),
            "if_transport_counted_as_correct_pct": pct(
                frac(n_correct + n_transport, len(ans))),
        },
        # Unanswerable behaviour is reported but never folded into the semantic
        # accuracy above: answering an unanswerable case is a separate failure
        # mode (abstention), not a wrong label.
        "n_unanswerable": len(unans),
        "n_answered_unanswerable": sum(1 for c in unans
                                       if c["unanswerable_but_answered"]),
        "false_confidence_rate": frac(sum(1 for c in unans
                                          if c["unanswerable_but_answered"]),
                                      len(unans)),
    }


def accuracy_by_scope(cells_by_mech, view):
    out = {}
    for mech in MECHS:
        cells = cells_by_mech[mech]
        block = {"overall": acc_block(cells, "ALL")}
        block["by_area"] = {
            a: acc_block([c for c in cells if c["area"] == a], f"area {a}")
            for a in AREAS if any(c["area"] == a for c in cells)}
        block["by_split"] = {
            s: acc_block([c for c in cells if c["split"] == s], f"split {s}")
            for s in SPLITS if any(c["split"] == s for c in cells)}
        block["by_question_type"] = {
            t: acc_block([c for c in cells if c["question_type"] == t], f"qtype {t}")
            for t in QTYPE_ORDER if any(c["question_type"] == t for c in cells)}
        out[mech] = block
    return {view: out}


# ---------------------------------------------------------------------------
# paired comparison vs frozen Jev
# ---------------------------------------------------------------------------
def paired_vs_jev(cells_by_mech, view, label):
    """b / c / ties on cells where BOTH emitted a usable label.

    Pairing is restricted to ANSWERABLE cells (in the view's ground truth) on
    which both mechanisms produced a label. Transport failures therefore never
    enter a paired cell; a case where either side produced no label is excluded
    and counted in `n_excluded_*` so the pairing is auditable.
    """
    jev = {c["case_id"]: c for c in cells_by_mech[JEV]}
    new = {c["case_id"]: c for c in cells_by_mech[NEW]}
    pair, excl_unusable, excl_unanswerable = [], 0, 0
    for cid in sorted(jev):
        a, b = jev[cid], new[cid]
        if a["unanswerable"] or b["unanswerable"]:
            excl_unanswerable += 1
            continue
        if not (a["usable"] and b["usable"]):
            excl_unusable += 1
            continue
        pair.append(cid)
    b_n = sum(1 for cid in pair if new[cid]["correct"] and not jev[cid]["correct"])
    c_n = sum(1 for cid in pair if jev[cid]["correct"] and not new[cid]["correct"])
    both_right = sum(1 for cid in pair if new[cid]["correct"] and jev[cid]["correct"])
    both_wrong = sum(1 for cid in pair
                     if not new[cid]["correct"] and not jev[cid]["correct"])
    acc_new = frac(sum(1 for cid in pair if new[cid]["correct"]), len(pair))
    acc_jev = frac(sum(1 for cid in pair if jev[cid]["correct"]), len(pair))
    return {
        "view": view,
        "label": label,
        "n_paired": len(pair),
        "n_excluded_but_unusable": excl_unusable,
        "n_excluded_unanswerable": excl_unanswerable,
        "acc_spacebunny": acc_new,
        "acc_spacebunny_pct": pct(acc_new),
        "acc_jev": acc_jev,
        "acc_jev_pct": pct(acc_jev),
        "delta_spacebunny_minus_jev": r4((acc_new or 0) - (acc_jev or 0)),
        "delta_pp": pp((acc_new or 0) - (acc_jev or 0)),
        "discordant_b_spacebunny_right_jev_wrong": b_n,
        "discordant_c_jev_right_spacebunny_wrong": c_n,
        "ties_total": both_right + both_wrong,
        "ties_both_right": both_right,
        "ties_both_wrong": both_wrong,
        "discordant_case_ids": {
            "b": [cid for cid in pair
                  if new[cid]["correct"] and not jev[cid]["correct"]],
            "c": [cid for cid in pair
                  if jev[cid]["correct"] and not new[cid]["correct"]],
        },
    }


def acc_cross_check(cells, view, mech):
    """Verify the stated denominators against the frozen `_acc`.

    `acc_block` here and `_acc` in the frozen scorer divide by different
    expressions of the same set. If they ever disagree, one of them is wrong
    and every number built on it is wrong. A disagreement is a hard stop.
    """
    mine = acc_block(cells, "cross-check")
    theirs = _acc(cells)
    # In `_acc`, every unanswerable cell that emitted a label is counted by
    # `n_answered_unanswerable`, so the usable-in-answerable count follows by
    # subtraction. This is the quantity the brief requires to be stated.
    theirs_usable_in_ans = (theirs["n_usable"]
                            - theirs["n_answered_unanswerable"])
    problems = []
    for label, a, b in (
            ("n_answerable", mine["n_answerable"], theirs["n_answerable"]),
            ("n_usable_in_answerable", mine["n_usable_in_answerable"],
             theirs_usable_in_ans),
            ("n_correct", mine["n_correct"], theirs["n_correct_answerable"]),
            ("acc_answerable", mine["acc_answerable"],
             theirs["acc_answerable"]),
            ("n_answered_unanswerable", mine["n_answered_unanswerable"],
             theirs["n_answered_unanswerable"]),
    ):
        if a != b:
            problems.append(f"{label}: mine {a} vs frozen _acc {b}")
    if problems:
        raise SystemExit(
            f"ACCURACY CROSS-CHECK FAIL ({view}/{mech}): " + "; ".join(problems))
    return {"agrees_with_frozen__acc": True,
            "n_answerable": mine["n_answerable"],
            "n_usable_in_answerable": mine["n_usable_in_answerable"],
            "n_correct": mine["n_correct"],
            "acc_answerable": mine["acc_answerable"]}


def paired_cross_check(cells_by_mech, view):
    """Cross-check b/c against the frozen `_paired_gain`, which computes them
    independently and knows nothing about this file. Any disagreement is a
    hard stop, so a silent drift in the pairing rule cannot survive."""
    expected = _paired_gain(cells_by_mech, NEW, JEV, lambda c: True)
    mine = paired_vs_jev(cells_by_mech, view, "cross-check")
    if expected is None:
        return {"available": False, "note": "frozen _paired_gain returned None"}
    ok = (expected["discordant_b"] == mine["discordant_b_spacebunny_right_jev_wrong"]
          and expected["discordant_c"] == mine["discordant_c_jev_right_spacebunny_wrong"]
          and expected["n_paired"] == mine["n_paired"])
    if not ok:
        raise SystemExit(
            f"PAIRED CROSS-CHECK FAIL ({view}): frozen _paired_gain "
            f"b/c/n = {expected['discordant_b']}/{expected['discordant_c']}"
            f"/{expected['n_paired']}, this file = "
            f"{mine['discordant_b_spacebunny_right_jev_wrong']}/"
            f"{mine['discordant_c_jev_right_spacebunny_wrong']}/"
            f"{mine['n_paired']}")
    return {"available": True, "agrees_with_frozen_paired_gain": True,
            "n_paired": expected["n_paired"],
            "discordant_b": expected["discordant_b"],
            "discordant_c": expected["discordant_c"]}


# ---------------------------------------------------------------------------
# decision bands (verbatim from findings.md §6)
# ---------------------------------------------------------------------------
def replicate_stability(rows, cases):
    """Label agreement between the new run and the frozen run of the SAME
    mechanism (same model, prompt, route, temperature; N=1 each).

    Not a hypothesis test. It is the cheapest available measurement of how
    reproducible one general-model cell is, and it bounds how much any single
    N=1 accuracy figure in this directory can be trusted.
    """
    new = rows[NEW]
    old = rows[FROZEN_GENERAL]
    by_id = {c["id"]: c for c in cases}
    agree, disagree, unusable, both_unusable = [], [], [], []
    for cid in sorted(new):
        a = (new[cid]["prediction"] or {}).get("label")
        b = (old[cid]["prediction"] or {}).get("label")
        answerable = bool(by_id[cid]["ground_truth"]["answerable"])
        if a is None and b is None:
            both_unusable.append(cid)
        elif a is None or b is None:
            unusable.append({"case_id": cid, "new": a, "frozen": b,
                             "new_typed_error": new[cid]["typed_error"],
                             "frozen_typed_error": old[cid]["typed_error"],
                             "answerable": answerable})
        elif a == b:
            agree.append(cid)
        else:
            disagree.append({"case_id": cid, "new": a, "frozen": b,
                             "gt_answer": by_id[cid]["ground_truth"]["answer"],
                             "answerable": answerable,
                             "new_correct": a == by_id[cid]["ground_truth"]["answer"],
                             "frozen_correct": b == by_id[cid]["ground_truth"]["answer"]})
    return {
        "what": "label agreement between this N=1 run and the frozen N=1 run "
                "of the same mechanism (space-bunny-free, same GEN_SYS, same "
                "route, temperature 0, one attempt per cell)",
        "n_cells": len(new),
        "n_label_agree": len(agree),
        "n_label_disagree": len(disagree),
        "n_unusable_in_exactly_one_run": len(unusable),
        "n_unusable_in_both_runs": len(both_unusable),
        "disagreements": disagree,
        "unusable_in_exactly_one_run": unusable,
        "note": "a flip at temperature 0 on a free-tier unpinned endpoint is "
                "expected (findings.md §4 L3) and is recorded, not smoothed. "
                "Each disagreement listed here is a cell whose label is not "
                "reproducible across two N=1 samples of the same mechanism.",
    }


def evaluate_bands(acc, c_value, c_source):
    """Apply the pre-registered bands. Support is evaluated before refute."""
    fired = []
    if acc <= BAND_SUPPORT_MAX_ACC:
        fired.append(f"acc {acc} <= {BAND_SUPPORT_MAX_ACC} (support arm 1)")
    if c_value is not None and c_value >= BAND_SUPPORT_MIN_C:
        fired.append(f"c {c_value} >= {BAND_SUPPORT_MIN_C} (support arm 2)")

    verdict = None
    if fired:
        verdict = "supports a Jev niche"
    else:
        ref = []
        if acc >= BAND_REFUTE_MIN_ACC:
            ref.append(f"acc {acc} >= {BAND_REFUTE_MIN_ACC} (refute arm 1)")
        if c_value is not None and c_value <= BAND_REFUTE_MAX_C:
            ref.append(f"c {c_value} <= {BAND_REFUTE_MAX_C} (refute arm 2)")
        if ref:
            verdict = "REFUTES a Jev niche"
            fired = ref
        elif BAND_UNINFORMATIVE_LO <= acc <= BAND_UNINFORMATIVE_HI:
            verdict = "uninformative (declared inconclusive band)"
            fired = [f"acc {acc} in [{BAND_UNINFORMATIVE_LO}, {BAND_UNINFORMATIVE_HI}]"]
        else:
            verdict = "OUTSIDE the defined bands"
            fired = [f"acc {acc} is in no band: not <= {BAND_SUPPORT_MAX_ACC}, "
                     f"not >= {BAND_REFUTE_MIN_ACC}, not in "
                     f"[{BAND_UNINFORMATIVE_LO}, {BAND_UNINFORMATIVE_HI}]"]
    return {
        "verdict": verdict,
        "conditions_fired": fired,
        "acc_used": acc,
        "c_used": c_value,
        "c_source": c_source,
        "evaluation_order": "support evaluated before refute, as pre-registered",
        "bands_verbatim": {
            "supports": f"acc <= {BAND_SUPPORT_MAX_ACC} OR c >= {BAND_SUPPORT_MIN_C}",
            "refutes": f"acc >= {BAND_REFUTE_MIN_ACC} AND c <= {BAND_REFUTE_MAX_C}",
            "uninformative": f"{BAND_UNINFORMATIVE_LO} <= acc <= {BAND_UNINFORMATIVE_HI}",
            "otherwise": "OUTSIDE the defined bands; no new threshold is invented",
        },
    }


# ---------------------------------------------------------------------------
# outputs
# ---------------------------------------------------------------------------
def write_paired_ndjson(path, views, cases, f1_ids):
    """One row per case: both verdicts, transport flags, raw + corrected.

    The raw_* and corrected_* columns come from the two SEPARATE cell sets
    (built from the committed ground truth and from the F1-corrected ground
    truth). They are not derived from each other: for c-p4a/c-p4b the two
    differ, and reusing one set for both silently reports raw correctness
    under a corrected label.
    """
    raw_cells = views["raw_gt"]["cells"]
    corr_cells = views["f1_corrected_gt"]["cells"]
    by_id = {c["id"]: c for c in cases}
    jev = {c["case_id"]: c for c in raw_cells[JEV]}
    new = {c["case_id"]: c for c in raw_cells[NEW]}
    jev_c = {c["case_id"]: c for c in corr_cells[JEV]}
    new_c = {c["case_id"]: c for c in corr_cells[NEW]}
    n = 0
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for cid in sorted(by_id):
            case = by_id[cid]
            j, s = jev[cid], new[cid]
            jc, sc = jev_c[cid], new_c[cid]
            row = {
                "schema_version": COMPARISON_SCHEMA_VERSION,
                "case_id": cid,
                "area": case["area"],
                "split": case["split"],
                "question_type": case["questions"][0]["type"],
                "pair_id": case["control"]["pair_id"],
                "variant_kind": case["control"]["variant_kind"],
                # ---- raw (committed) ground truth
                "raw_gt_answerable": not j["unanswerable"],
                "raw_gt_answer": j["gt_answer"],
                "raw_jev_label": j["pred_label"],
                "raw_jev_correct": j["correct"],
                "raw_jev_usable": j["usable"],
                "raw_spacebunny_label": s["pred_label"],
                "raw_spacebunny_correct": s["correct"],
                "raw_spacebunny_usable": s["usable"],
                "raw_f1_corrected": cid in f1_ids,
                "raw_paired_outcome": paired_outcome(j, s),
                # ---- F1-corrected ground truth (independent cell set)
                "corrected_gt_answerable": not sc["unanswerable"],
                "corrected_gt_answer": sc["gt_answer"],
                "corrected_jev_correct": jc["correct"],
                "corrected_jev_usable": jc["usable"],
                "corrected_spacebunny_correct": sc["correct"],
                "corrected_spacebunny_usable": sc["usable"],
                "corrected_paired_outcome": paired_outcome(jc, sc),
                # ---- transport, separated from judgement
                "jev_transport_failure": (not j["usable"]),
                "jev_typed_error": j["typed_error"],
                "spacebunny_transport_failure": (not s["usable"]),
                "spacebunny_typed_error": s["typed_error"],
                "spacebunny_http_status": s["http_status"],
                "spacebunny_latency_ms": s["latency_ms"],
                "spacebunny_usage": s["usage"],
            }
            f.write(json.dumps(row, ensure_ascii=False,
                               separators=(",", ":")) + "\n")
            n += 1
    return n


def paired_outcome(j, s):
    if j["unanswerable"] or s["unanswerable"]:
        return "excluded_unanswerable"
    if not (j["usable"] and s["usable"]):
        return "excluded_transport_failure"
    if s["correct"] and not j["correct"]:
        return "b_spacebunny_only"
    if j["correct"] and not s["correct"]:
        return "c_jev_only"
    return "tie_both_right" if s["correct"] else "tie_both_wrong"


def transport_summary(cells_by_mech, cases):
    out = {}
    by_id = {c["id"]: c for c in cases}
    for mech in MECHS:
        cells = cells_by_mech[mech]
        fails = [c for c in cells if not c["usable"]]
        out[mech] = {
            "n_cells": len(cells),
            "n_usable": sum(1 for c in cells if c["usable"]),
            "n_transport_failures": len(fails),
            "typed_error_counts": {str(c["typed_error"]): sum(
                1 for c in cells if str(c["typed_error"]) == str(
                    c["typed_error"]) and not c["usable"])
                for c in fails} or {},
            "failed_case_ids": sorted(c["case_id"] for c in fails),
            "failed_cases_answerable": sorted(
                c["case_id"] for c in fails if not c["unanswerable"]),
            "failed_cases_unanswerable": sorted(
                c["case_id"] for c in fails if c["unanswerable"]),
        }
    # A transport failure on an UNANSWERABLE case cannot move a semantic
    # answerable accuracy at all, under any counting convention. Stated
    # explicitly because it makes the sensitivity analysis degenerate.
    out["_note"] = (
        "A transport failure on an unanswerable case is excluded from every "
        "semantic answerable denominator, so counting it as an error and "
        "counting it as correct give the SAME accuracy. The sensitivity "
        "analysis is only informative when a failure lands on an answerable "
        "case.")
    return out


def build(seed):
    cases = seed["cases"]
    rows = seed["rows"]
    f1_cases, f1_ids = f1_corrected_cases(cases)

    views = {}
    for view, cset in (("raw_gt", cases), ("f1_corrected_gt", f1_cases)):
        cells = {m: [build_cell(c, rows[m][c["id"]]) for c in cset]
                 for m in MECHS}
        views[view] = {"cells": cells, "cases": cset}

    comparison = {
        "schema_version": COMPARISON_SCHEMA_VERSION,
        "scorer_version": SCORER_VERSION,
        "question": "followup-01: does a second, same-family "
                    "space-bunny-free run match the frozen Jev results, and "
                    "where does the pre-registered band land?",
        "definitions": {
            "acc_answerable": "correct / usable, over answerable cells only. "
                              "Transport failures (no label emitted) are "
                              "excluded from the denominator and reported "
                              "separately, per the brief.",
            "b": "cells where spacebunny is right and jev is wrong",
            "c": "cells where jev is right and spacebunny is wrong",
            "ties": "both right or both wrong, on paired cells",
            "pairing": "answerable cells (in the view's ground truth) where "
                       "BOTH mechanisms emitted a usable label",
            "f1_correction": "verification.md §2 F1: c-p4a and c-p4b "
                             "reclassified unanswerable, applied identically "
                             "to all three mechanisms",
            "no_significance_test": "n=64 (n=50 answerable raw, n=48 "
                                    "corrected). No p-value is claimed "
                                    "(schema.md §5).",
        },
        "inputs": {
            "frozen_sha256": seed["frozen"],
            "new_run_sha256": seed["new_sha"],
            "new_run_rows": seed["new_rows"],
        },
        "f1_correction": {
            "pair_id": F1_PAIR_ID,
            "case_ids": f1_ids,
            "source": "verification.md §2 F1",
            "committed_answerable": sum(
                1 for c in cases if c["ground_truth"]["answerable"]),
            "committed_unanswerable": sum(
                1 for c in cases if not c["ground_truth"]["answerable"]),
            "corrected_answerable": sum(
                1 for c in f1_cases if c["ground_truth"]["answerable"]),
            "corrected_unanswerable": sum(
                1 for c in f1_cases if not c["ground_truth"]["answerable"]),
        },
        "transport": transport_summary(
            {m: views["raw_gt"]["cells"][m] for m in MECHS}, cases),
    }

    for view in ("raw_gt", "f1_corrected_gt"):
        comparison.update(accuracy_by_scope(views[view]["cells"], view))
        comparison.setdefault("paired_vs_jev", {})[view] = paired_vs_jev(
            views[view]["cells"], view,
            "spacebunny vs frozen jev")
        comparison.setdefault("paired_cross_check", {})[view] = \
            paired_cross_check(views[view]["cells"], view)
        comparison.setdefault("accuracy_cross_check", {})[view] = {
            m: acc_cross_check(views[view]["cells"][m], view, m)
            for m in MECHS}

    # frozen general_model, the same-family comparator this run replicates
    comparison["frozen_general_model_reference"] = {
        "note": "the frozen general_model run this experiment replicates; "
                "reported under both views for context, not as a subject of "
                "the paired test",
        "acc_raw_gt": comparison["raw_gt"][FROZEN_GENERAL]["overall"],
        "acc_f1_corrected_gt": comparison["f1_corrected_gt"][FROZEN_GENERAL][
            "overall"],
    }

    # ---- free rider: run-to-run stability of the SAME mechanism
    # `spacebunny` and the frozen `general_model` are the same model, the same
    # prompt, the same route and the same decoding, sampled once each. Their
    # disagreement is therefore a direct, same-conditions measurement of how
    # reproducible a single N=1 general-model cell is. It is not part of the
    # paired test against Jev; it is reported because it bounds that test.
    comparison["replicate_stability_vs_frozen_general_model"] = \
        replicate_stability(rows, cases)

    # ---- the figures the band is applied to, named once
    acc_corr_block = comparison["f1_corrected_gt"][NEW]["overall"]
    acc = acc_corr_block["acc_answerable"]
    c_corr = comparison["paired_vs_jev"]["f1_corrected_gt"][
        "discordant_c_jev_right_spacebunny_wrong"]
    c_raw = comparison["paired_vs_jev"]["raw_gt"][
        "discordant_c_jev_right_spacebunny_wrong"]
    b_corr = comparison["paired_vs_jev"]["f1_corrected_gt"][
        "discordant_b_spacebunny_right_jev_wrong"]
    b_raw = comparison["paired_vs_jev"]["raw_gt"][
        "discordant_b_spacebunny_right_jev_wrong"]

    # ---- band evaluation, on the F1-corrected semantic accuracy
    comparison["band_evaluation"] = {
        "bands_source": BAND_SOURCE,
        "primary": evaluate_bands(
            acc, c_corr,
            "paired c on the F1-corrected answerable set (consistent with the "
            "corrected accuracy the band is applied to)"),
        "variant_raw_gt_c": evaluate_bands(
            comparison["raw_gt"][NEW]["overall"]["acc_answerable"], c_raw,
            "paired c on the raw (committed) answerable set"),
        "transport_failure_sensitivity": {
            "note": "bounded sensitivity only: the same bands applied if the "
                    "transport failures were counted as errors, and as "
                    "correct. The point estimate excludes them.",
            "counted_as_error": evaluate_bands(
                acc_corr_block["transport_sensitivity"][
                    "if_transport_counted_as_error"], c_corr,
                "c unchanged: transport failures never enter a paired cell"),
            "counted_as_correct": evaluate_bands(
                acc_corr_block["transport_sensitivity"][
                    "if_transport_counted_as_correct"], c_corr,
                "c unchanged: transport failures never enter a paired cell"),
        },
    }
    # ---- how many further answerable errors would move the band verdict.
    # The bands are applied verbatim at each k; no threshold is invented. Each
    # additional error is modelled on a cell Jev also got right, so c rises
    # with k, which is the conservative direction for the refute verdict.
    corr_n = comparison["f1_corrected_gt"][NEW]["overall"]["n_answerable"]
    comparison["band_flip_margin"] = {
        "note": "the pre-registered bands re-applied verbatim at k additional "
                "answerable errors, each taken on a cell Jev also got right so "
                "that c rises with k. This measures how much of the verdict "
                "rests on single cells; it introduces no new threshold.",
        "denominator_n_answerable_corrected": corr_n,
        "observed_k": acc_corr_block["n_semantic_errors"],
        "verdict_by_k": {
            str(k): evaluate_bands(frac(corr_n - k, corr_n), c_corr + k,
                                   f"modelled: k={k} extra answerable errors, "
                                   f"c = {c_corr} + {k}")
            for k in range(0, 7)},
    }
    margin = comparison["band_flip_margin"]
    base_verdict = comparison["band_evaluation"]["primary"]["verdict"]
    margin["first_k_that_changes_the_verdict"] = next(
        (int(k) for k in sorted(margin["verdict_by_k"], key=int)
         if margin["verdict_by_k"][k]["verdict"] != base_verdict), None)

    comparison["band_evaluation"]["_design_caveat"] = (
        "These bands were pre-registered in findings.md §6 for a CROSS-FAMILY "
        "model (question Q1: is Jev's non-advantage a property of cheap "
        "general models, or of one family reading one family's prose?). This "
        "run uses space-bunny-free, which findings.md §4 L1 identifies as the "
        "SAME family as the corpus author, the harness author, the GEN_SYS "
        "author, and the verifier. The band arithmetic below is applied "
        "verbatim as instructed, but the verdict is NOT the answer to Q1 and "
        "must not be reported as one. The self-preference confound can only "
        "inflate this baseline, never deflate it.")

    comparison["_read_before_quoting"] = [
        "n=64. No significance test is claimed anywhere (schema.md §5).",
        "One run, one attempt per cell, zero retries, free-tier unpinned "
        "model (findings.md §4 L3).",
        "spacebunny is a REPLICATE of the frozen general_model mechanism under "
        "the same route, prompt and decoding, not an independent model.",
    ]

    return comparison, views, f1_ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", default=os.path.join(FOLLOWUP, "results"))
    ap.add_argument("--generated-utc", default=None,
                    help="pin the manifest timestamp for byte-reproducibility")
    ap.add_argument("--commit", default=None,
                    help="pin the commit recorded in the manifest")
    ap.add_argument("--self-check", action="store_true",
                    help="score twice and assert byte-identical outputs")
    args = ap.parse_args()

    os.makedirs(args.results_dir, exist_ok=True)
    # Captured once, so the two passes of --self-check share it and the
    # determinism comparison is about the scoring, not about the clock.
    generated_utc = args.generated_utc or utc_now_iso()
    print("score_followup: verifying frozen inputs")
    frozen = verify_frozen_inputs()
    for rel, d in frozen.items():
        print(f"  {rel}: {d['actual']} {'OK' if d['match'] else 'MISMATCH'}")

    cases = load_cases(os.path.join(PHASE1, "cases.ndjson"))
    rows, src = load_mechanism_rows()
    new_path = os.path.join(args.results_dir, "spacebunny_raw.ndjson")
    seed = {"cases": cases, "rows": rows, "frozen": frozen,
            "new_sha": sha256_file(new_path),
            "new_rows": len(load_ndjson(new_path))}

    print("score_followup: building cells and metrics")
    comparison, views, f1_ids = build(seed)

    cj = os.path.join(args.results_dir, "comparison.json")
    paired_path = os.path.join(args.results_dir, "paired.ndjson")
    mf = os.path.join(args.results_dir, "manifest.json")

    with open(cj, "w", encoding="utf-8", newline="\n") as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    n = write_paired_ndjson(paired_path, views,
                            views["raw_gt"]["cases"], f1_ids)

    new_rows = load_ndjson(new_path)
    commit = args.commit or git("rev-parse", "HEAD") or "unknown"
    manifest = {
        "schema_version": COMPARISON_SCHEMA_VERSION,
        "crosslink_issue": 565,
        "followup": "followup-01-spacebunny",
        "generated_utc": generated_utc,
        "commit": commit,
        "scorer": {"version": SCORER_VERSION,
                   "path": "followup-01-spacebunny/harness/score_followup.py",
                   "stdlib_only": True,
                   "reuses": ["common.py", "score.py"],
                   "python": "%d.%d" % sys.version_info[:2]},
        "runner": {"version": "1.0.0",
                   "path": "followup-01-spacebunny/harness/run_spacebunny.py"},
        "frozen_inputs": frozen,
        "model": {
            "catalog_id": "opencode-go/space-bunny-free",
            "model_id": "space-bunny-free",
            "mechanism_label": NEW,
            "provider": "OpenCode Go model, served on the OpenCode Zen route",
            "endpoint": "https://opencode.ai/zen/v1/chat/completions",
            "route_note": "the disclosed Zen route, identical to the frozen "
                          "general_model route. A route change, not a model "
                          "substitution (see phase1 manifest.models."
                          "general_model.endpoint_note).",
            "cost": {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0},
            "context": 1048576,
            "catalog_refreshed": "2026-09-26",
            "family": "SAME family as the corpus author, harness author, "
                      "GEN_SYS author and verifier (findings.md §4 L1). This "
                      "run is a same-family REPLICATE of general_model, not "
                      "the cross-family test Q1 calls for.",
        },
        "conditions": {
            "gen_sys": "imported from frozen harness/run_baselines.py",
            "max_tokens": 256,
            "temperature": 0,
            "attempts_per_cell": 1,
            "retries": 0,
            "n_cases": 64,
            "frozen_condition_check": "all 64 rebuilt requests hash-equal and "
                                      "body-equal to the frozen general_model "
                                      "rows; enforced as a pre-call gate",
            "session_header": "jev-phase1-followup-01-spacebunny-20260926",
            "transport_note": "the x-opencode-session provenance header is the "
                              "only transport-level difference from the frozen "
                              "run; it is not part of the hashed body",
        },
        "raw_run_window_utc": [min(r["timestamp_utc"] for r in new_rows),
                               max(r["timestamp_utc"] for r in new_rows)],
        "error_counts": {
            NEW: _error_counts(new_rows),
            JEV: _error_counts([rows[JEV][c["id"]] for c in cases]),
            FROZEN_GENERAL: _error_counts([rows[FROZEN_GENERAL][c["id"]]
                                           for c in cases]),
        },
        "outputs_sha256": {},
        "secrets": {"api_key_env": "OPENCODE_GO_API_KEY",
                    "value_recorded": False,
                    "secrets_recorded_field": False},
    }
    outputs = {}
    for name, path in (("spacebunny_raw.ndjson", new_path),
                       ("paired.ndjson", paired_path),
                       ("comparison.json", cj)):
        outputs[name] = sha256_file(path)
    manifest["outputs_sha256"] = outputs
    with open(mf, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")

    print(f"score_followup: wrote comparison.json, paired.ndjson ({n} rows), "
          f"manifest.json")

    if args.self_check:
        before = {k: sha256_file(os.path.join(args.results_dir, k))
                  for k in ("comparison.json", "paired.ndjson", "manifest.json")}
        print("score_followup: self-check, second pass")
        comparison2, views2, f1_ids2 = build(seed)
        cj2 = os.path.join(args.results_dir, "comparison.json")
        with open(cj2, "w", encoding="utf-8", newline="\n") as f:
            json.dump(comparison2, f, ensure_ascii=False, indent=2,
                      sort_keys=True)
            f.write("\n")
        write_paired_ndjson(paired_path, views2,
                            views2["raw_gt"]["cases"], f1_ids2)
        after = {k: sha256_file(os.path.join(args.results_dir, k))
                 for k in ("comparison.json", "paired.ndjson", "manifest.json")}
        same = before == after
        print("  pass 1:", json.dumps(before, indent=2))
        print("  pass 2:", json.dumps(after, indent=2))
        print(f"  DETERMINISM: {'IDENTICAL' if same else 'DIVERGED'}")
        if not same:
            return 1
    return 0


def _error_counts(rows):
    out = {}
    for r in rows:
        k = str(r.get("typed_error"))
        out[k] = out.get(k, 0) + 1
    return out


if __name__ == "__main__":
    raise SystemExit(main())
