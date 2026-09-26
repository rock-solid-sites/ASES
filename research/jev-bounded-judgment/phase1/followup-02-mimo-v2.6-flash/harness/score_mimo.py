#!/usr/bin/env python3
"""followup-02-mimo-v2.6-flash scorer — deterministic scoring of the cross-family
baseline.

Compares the ONE new `mimo_v26_flash` run against the FROZEN Jev results and the
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
`load_ndjson`, `sha256_file`, `frac`, `r4`, `pct`, `pp`, `git` and
`_paired_gain` are imported from `../../harness/score.py`, and `load_cases` from
`../../harness/common.py`. `build_cell` and `_acc` are also used as INDEPENDENT
CROSS-CHECKS on this file's own arithmetic, and a disagreement is a hard stop.

WHAT IS DIFFERENT FROM followup-01's SCORER, AND WHY
----------------------------------------------------
Only the mechanism under test (`mimo_v26_flash` instead of `spacebunny`), plus
three additions this experiment needs and followup-01 did not:

  * a SUFFICIENCY FLAG, pre-registered at < 40 usable of the 50 answerable
    cells. MiMo is a reasoning model whose `reasoning_content` competes with
    `content` inside the frozen `max_tokens=256`, so a grid can be dominated by
    empty-content transport failures. When that happens the band must not be
    read as a statement about MiMo's judgement. The flag is computed, not
    asserted, and it is reported next to the verdict either way.
  * a REASONING-TOKEN ACCOUNT, because the same mechanism makes the reasoning
    spend the thing the sufficiency flag is watching.
  * a DERIVED COST from the recorded usage at the catalog rates.

`replicate_stability` is deliberately NOT reproduced. It compared two N=1 runs
of the SAME mechanism; MiMo is a different model from the frozen
`general_model`, so there is no same-mechanism run to compare it against and the
statistic would be meaningless. findings.md §6 item 4's actual free rider — the
new model's own typed-error count over its 64 cells, replacing the lucky 1/64
(N6) with a same-conditions measurement — is reported as `free_rider_n6`.

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
F1-corrected semantic accuracy, support evaluated before refute. They were
pre-registered for a CROSS-FAMILY model and this IS that model, so unlike
followup-01 the confound caveat does not apply: `mimo` is a different family
from both Jev and the corpus author (findings.md §4 L1). The band verdict is
therefore the answer to Q1, subject only to the run-level caveats recorded in
`_read_before_quoting`.

Usage:
    python3 harness/score_mimo.py
    python3 harness/score_mimo.py --self-check     # score twice, diff
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
COMPARISON_SCHEMA_VERSION = "jevp1-followup2-comparison-1.0"

AREAS = ("A", "B", "C", "D")
SPLITS = ("train", "dev", "test")
QTYPE_ORDER = ("noul", "choice", "score")

JEV = "jev"
FROZEN_GENERAL = "general_model"
NEW = "mimo_v26_flash"
MECHS = (JEV, FROZEN_GENERAL, NEW)

# verification.md §2 F1: cp4's ground truth is not derivable from the
# model-visible text; both members are reclassified unanswerable.
F1_PAIR_ID = "cp4"

MODEL_ID = "mimo-v2.6-flash"
MODEL_CATALOG_ID = "opencode-go/mimo-v2.6-flash"
MODEL_FAMILY = "mimo"
ENDPOINT = "https://opencode.ai/zen/go/v1/chat/completions"

# USD per million tokens, as recorded in the operator directive of 2026-09-26.
COST_PER_MTOK = {"input": 0.14, "output": 0.28, "cache_read": 0.0028,
                 "cache_write": 0.0}
# The frozen `general_model` comparator is a free model (0/0/0/0). Each call is
# charged at its OWN model's rates, so this run never overstates its own cost
# by pricing a free control at MiMo's rates.
MODEL_COST_PER_MTOK = {
    MODEL_ID: COST_PER_MTOK,
    FROZEN_GENERAL: {"input": 0.0, "output": 0.0, "cache_read": 0.0,
                     "cache_write": 0.0},
}

# Pre-registered sufficiency rule for this run. Stated before the grid ran.
SUFFICIENCY_MIN_USABLE_ANSWERABLE = 40
SUFFICIENCY_SOURCE = (
    "pre-registered for followup-02: fewer than 40 usable cells of the 50 "
    "answerable cells means transport failures dominate the run and the band "
    "verdict is not a statement about the model's judgement"
)

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

RAW_ANSWERABLE_N = 50      # the committed corpus, before the F1 correction
CORRECTED_ANSWERABLE_N = 48


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
        NEW: os.path.join(FOLLOWUP, "results", "mimo_raw.ndjson"),
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
        d = copy.deepcopy(c)
        if c["id"] in ids:
            d["ground_truth"]["answerable"] = False
            d["ground_truth"]["answer"] = None
            d["ground_truth"]["abstain_expected"] = True
            d["_f1_corrected"] = True
        else:
            d["_f1_corrected"] = False
        corrected.append(d)
    return corrected, ids


# ---------------------------------------------------------------------------
# usage / reasoning / cost
# ---------------------------------------------------------------------------
def token_counts(row):
    """Flat token totals from a row's recorded usage, reasoning included.

    The provider spells reasoning tokens differently depending on route and
    model, so every known key is probed. The full provider object is kept
    verbatim by the runner under `usage.raw`; this only normalises the fields
    the cost record and the reasoning account need.
    """
    usage = row.get("usage")
    if not isinstance(usage, dict):
        return None
    raw = usage.get("raw") if isinstance(usage.get("raw"), dict) else usage

    def pick(*names):
        for n in names:
            v = raw.get(n)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                return int(v)
        return 0

    out = {
        "input_tokens": pick("input_tokens", "prompt_tokens"),
        "output_tokens": pick("output_tokens", "completion_tokens"),
        "total_tokens": pick("total_tokens"),
        "cache_read_tokens": pick("cache_read_input_tokens", "cache_read_tokens",
                                  "cached_tokens"),
        "cache_write_tokens": pick("cache_creation_input_tokens",
                                   "cache_write_tokens"),
        "reasoning_tokens": 0,
    }
    details = raw.get("completion_tokens_details") or raw.get("output_tokens_details")
    if isinstance(details, dict):
        for k in ("reasoning_tokens", "reasoning"):
            v = details.get(k)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                out["reasoning_tokens"] = int(v)
                break
    if not out["reasoning_tokens"]:
        for k in ("reasoning_tokens", "reasoning_content_tokens"):
            v = raw.get(k)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                out["reasoning_tokens"] = int(v)
                break
    return out


def derived_cost_usd(counts, model_id=MODEL_ID):
    """Derived USD from the recorded rates, attributed to `model_id`.

    None when there are no tokens to charge. A rejected request (4xx/5xx)
    carries no usage, so it contributes exactly $0.
    """
    if not counts or not any(counts.values()):
        return None
    rates = MODEL_COST_PER_MTOK.get(model_id)
    if rates is None:
        return None
    pairs = (("input", "input_tokens"), ("output", "output_tokens"),
             ("cache_read", "cache_read_tokens"),
             ("cache_write", "cache_write_tokens"))
    total = 0.0
    for rate_key, field in pairs:
        total += (counts.get(field) or 0) / 1_000_000.0 * rates[rate_key]
    return round(total, 8)


def usage_account(rows_by_case, model_id=MODEL_ID):
    """Summed tokens, derived cost, and the reasoning share of the output budget.

    The reasoning share is the number that says whether this run was one cell
    away from the empty-content failure mode: `content_tokens` is what is left
    of the budget after reasoning, and the frozen run gives each cell 256 output
    tokens to share between the two.
    """
    keys = ("input_tokens", "output_tokens", "total_tokens",
            "cache_read_tokens", "cache_write_tokens", "reasoning_tokens")
    tot = {k: 0 for k in keys}
    per_cell = []
    cost = 0.0
    for row in rows_by_case:
        counts = token_counts(row)
        if counts:
            for k in keys:
                tot[k] += counts[k]
            v = derived_cost_usd(counts, row.get("model_id") or model_id)
            if v:
                cost += v
        per_cell.append({
            "case_id": row["case_id"],
            "output_tokens": (counts or {}).get("output_tokens"),
            "reasoning_tokens": (counts or {}).get("reasoning_tokens"),
            "content_tokens": ((counts or {}).get("output_tokens", 0)
                               - (counts or {}).get("reasoning_tokens", 0)),
        })
    with_usage = [p for p in per_cell if p["output_tokens"]]
    content = [p["content_tokens"] for p in with_usage]
    reasoning = [p["reasoning_tokens"] for p in with_usage]
    return {
        "model_id": model_id,
        "rates_usd_per_mtok": COST_PER_MTOK,
        "token_totals": tot,
        "derived_cost_usd": round(cost, 8),
        "n_cells": len(per_cell),
        "n_cells_with_usage": len(with_usage),
        "reasoning": {
            "total_reasoning_tokens": tot["reasoning_tokens"],
            "total_output_tokens": tot["output_tokens"],
            "reasoning_share_of_output": frac(tot["reasoning_tokens"],
                                              tot["output_tokens"]),
            "reasoning_share_of_output_pct": pct(frac(tot["reasoning_tokens"],
                                                      tot["output_tokens"])),
            "content_tokens_total": tot["output_tokens"] - tot["reasoning_tokens"],
            "per_cell_content_tokens_min": min(content) if content else None,
            "per_cell_content_tokens_max": max(content) if content else None,
            "per_cell_content_tokens_median": (
                sorted(content)[len(content) // 2] if content else None),
            "per_cell_reasoning_tokens_max": (max(reasoning) if reasoning
                                              else None),
            "frozen_max_tokens": 256,
            "note": "MiMo is a reasoning model: `reasoning_content` is billed "
                    "and counted inside the same output budget as `content`. "
                    "The per-cell content minimum is the margin the run had "
                    "left against the empty-content transport failure that "
                    "forced the frozen run from max_tokens=16 to 256.",
        },
    }


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
            "if_transport_counted_as_correct": frac(n_correct + n_transport,
                                                    len(ans)),
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
        "acc_mimo": acc_new,
        "acc_mimo_pct": pct(acc_new),
        "acc_jev": acc_jev,
        "acc_jev_pct": pct(acc_jev),
        "delta_mimo_minus_jev": r4((acc_new or 0) - (acc_jev or 0)),
        "delta_pp": pp((acc_new or 0) - (acc_jev or 0)),
        "discordant_b_mimo_right_jev_wrong": b_n,
        "discordant_c_jev_right_mimo_wrong": c_n,
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
    ok = (expected["discordant_b"] == mine["discordant_b_mimo_right_jev_wrong"]
          and expected["discordant_c"] == mine["discordant_c_jev_right_mimo_wrong"]
          and expected["n_paired"] == mine["n_paired"])
    if not ok:
        raise SystemExit(
            f"PAIRED CROSS-CHECK FAIL ({view}): frozen _paired_gain "
            f"b/c/n = {expected['discordant_b']}/{expected['discordant_c']}"
            f"/{expected['n_paired']}, this file = "
            f"{mine['discordant_b_mimo_right_jev_wrong']}/"
            f"{mine['discordant_c_jev_right_mimo_wrong']}/{mine['n_paired']}")
    return {"available": True, "agrees_with_frozen_paired_gain": True,
            "n_paired": expected["n_paired"],
            "discordant_b": expected["discordant_b"],
            "discordant_c": expected["discordant_c"]}


# ---------------------------------------------------------------------------
# decision bands (verbatim from findings.md §6) and the sufficiency flag
# ---------------------------------------------------------------------------
def evaluate_bands(acc, c_value, c_source):
    """Apply the pre-registered bands. Support is evaluated before refute."""
    fired = []
    if acc <= BAND_SUPPORT_MAX_ACC:
        fired.append(f"acc {acc} <= {BAND_SUPPORT_MAX_ACC} (support arm 1)")
    if c_value is not None and c_value >= BAND_SUPPORT_MIN_C:
        fired.append(f"c {c_value} >= {BAND_SUPPORT_MIN_C} (support arm 2)")

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
            fired = [f"acc {acc} in [{BAND_UNINFORMATIVE_LO}, "
                     f"{BAND_UNINFORMATIVE_HI}]"]
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


def sufficiency(n_usable_answerable, n_answerable_expected, n_transport):
    """The pre-registered sufficiency flag. Computed, never asserted."""
    ok = n_usable_answerable >= SUFFICIENCY_MIN_USABLE_ANSWERABLE
    return {
        "sufficient": ok,
        "n_usable_in_answerable": n_usable_answerable,
        "n_answerable_expected": n_answerable_expected,
        "n_transport_failures_in_answerable": n_transport,
        "threshold": f">= {SUFFICIENCY_MIN_USABLE_ANSWERABLE} usable of "
                     f"{n_answerable_expected} answerable",
        "rule": SUFFICIENCY_SOURCE,
        "reading": (
            "The grid carried enough usable answerable cells for the accuracy "
            "to be a statement about the model's judgement."
            if ok else
            "INSUFFICIENT: transport failures left too few usable answerable "
            "cells. The accuracy above is computed on the survivors and the "
            "band verdict must NOT be read as a statement about the model's "
            "judgement; the transport-failure sensitivity block is the honest "
            "reading of the run."),
    }


def free_rider_n6(rows_by_case):
    """findings.md §6 item 4: the new model's own typed-error count over its own
    64 cells, to replace the lucky 1/64 (N6) with a same-conditions measurement."""
    counts = {}
    for row in rows_by_case:
        k = str(row.get("typed_error"))
        counts[k] = counts.get(k, 0) + 1
    return {
        "what": "the cross-family model's own typed-error count over its own 64 "
                "cells, same conditions, N=1 per cell. findings.md §6 item 4 "
                "called this the free rider: it replaces the frozen run's lucky "
                "1/64 (N6) with a same-conditions measurement.",
        "n_cells": len(rows_by_case),
        "typed_error_counts": counts,
        "n_cells_with_typed_error": sum(v for k, v in counts.items() if k != "None"),
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
                "raw_mimo_label": s["pred_label"],
                "raw_mimo_correct": s["correct"],
                "raw_mimo_usable": s["usable"],
                "raw_f1_corrected": cid in f1_ids,
                "raw_paired_outcome": paired_outcome(j, s),
                # ---- F1-corrected ground truth (independent cell set)
                "corrected_gt_answerable": not sc["unanswerable"],
                "corrected_gt_answer": sc["gt_answer"],
                "corrected_jev_correct": jc["correct"],
                "corrected_jev_usable": jc["usable"],
                "corrected_mimo_correct": sc["correct"],
                "corrected_mimo_usable": sc["usable"],
                "corrected_paired_outcome": paired_outcome(jc, sc),
                # ---- transport, separated from judgement
                "jev_transport_failure": (not j["usable"]),
                "jev_typed_error": j["typed_error"],
                "mimo_transport_failure": (not s["usable"]),
                "mimo_typed_error": s["typed_error"],
                "mimo_http_status": s["http_status"],
                "mimo_latency_ms": s["latency_ms"],
                "mimo_usage": s["usage"],
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
        return "b_mimo_only"
    if j["correct"] and not s["correct"]:
        return "c_jev_only"
    return "tie_both_right" if s["correct"] else "tie_both_wrong"


def transport_summary(cells_by_mech, cases):
    out = {}
    for mech in MECHS:
        cells = cells_by_mech[mech]
        fails = [c for c in cells if not c["usable"]]
        typed = {}
        for c in fails:
            k = str(c["typed_error"])
            typed[k] = typed.get(k, 0) + 1
        out[mech] = {
            "n_cells": len(cells),
            "n_usable": sum(1 for c in cells if c["usable"]),
            "n_transport_failures": len(fails),
            "typed_error_counts": typed,
            "failed_case_ids": sorted(c["case_id"] for c in fails),
            "failed_cases_answerable": sorted(
                c["case_id"] for c in fails if not c["unanswerable"]),
            "failed_cases_unanswerable": sorted(
                c["case_id"] for c in fails if c["unanswerable"]),
        }
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

    new_rows = [rows[NEW][c["id"]] for c in cases]

    comparison = {
        "schema_version": COMPARISON_SCHEMA_VERSION,
        "scorer_version": SCORER_VERSION,
        "question": "followup-02: does a cross-family general model "
                    "(mimo-v2.6-flash) match the frozen Jev results, and where "
                    "does the pre-registered band land? This is the "
                    "confound-free test findings.md §6 Q1 asks for.",
        "definitions": {
            "acc_answerable": "correct / usable, over answerable cells only. "
                              "Transport failures (no label emitted) are "
                              "excluded from the denominator and reported "
                              "separately, per the brief.",
            "b": "cells where mimo is right and jev is wrong",
            "c": "cells where jev is right and mimo is wrong",
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
        "free_rider_n6": free_rider_n6(new_rows),
        "usage_and_cost": usage_account(new_rows),
    }

    for view in ("raw_gt", "f1_corrected_gt"):
        comparison.update(accuracy_by_scope(views[view]["cells"], view))
        comparison.setdefault("paired_vs_jev", {})[view] = paired_vs_jev(
            views[view]["cells"], view, "mimo_v26_flash vs frozen jev")
        comparison.setdefault("paired_cross_check", {})[view] = \
            paired_cross_check(views[view]["cells"], view)
        comparison.setdefault("accuracy_cross_check", {})[view] = {
            m: acc_cross_check(views[view]["cells"][m], view, m)
            for m in MECHS}

    # frozen general_model, reported for context, not as a subject of the test
    comparison["frozen_general_model_reference"] = {
        "note": "the frozen general_model run (space-bunny-free, same-family "
                "with the corpus author per findings.md §4 L1); reported under "
                "both views for context, not as a subject of the paired test",
        "acc_raw_gt": comparison["raw_gt"][FROZEN_GENERAL]["overall"],
        "acc_f1_corrected_gt": comparison["f1_corrected_gt"][FROZEN_GENERAL][
            "overall"],
    }

    # ---- the figures the band is applied to, named once
    acc_corr_block = comparison["f1_corrected_gt"][NEW]["overall"]
    acc = acc_corr_block["acc_answerable"]
    c_corr = comparison["paired_vs_jev"]["f1_corrected_gt"][
        "discordant_c_jev_right_mimo_wrong"]
    c_raw = comparison["paired_vs_jev"]["raw_gt"][
        "discordant_c_jev_right_mimo_wrong"]
    b_corr = comparison["paired_vs_jev"]["f1_corrected_gt"][
        "discordant_b_mimo_right_jev_wrong"]
    b_raw = comparison["paired_vs_jev"]["raw_gt"][
        "discordant_b_mimo_right_jev_wrong"]

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

    comparison["sufficiency"] = {
        "raw_gt": sufficiency(
            comparison["raw_gt"][NEW]["overall"]["n_usable_in_answerable"],
            RAW_ANSWERABLE_N,
            comparison["raw_gt"][NEW]["overall"][
                "n_transport_failures_in_answerable"]),
        "f1_corrected_gt": sufficiency(
            comparison["f1_corrected_gt"][NEW]["overall"][
                "n_usable_in_answerable"],
            CORRECTED_ANSWERABLE_N,
            comparison["f1_corrected_gt"][NEW]["overall"][
                "n_transport_failures_in_answerable"]),
    }
    comparison["sufficiency"]["gate"] = (
        "the flag is the raw_gt row, because the brief states the rule on the "
        "50 answerable cells; the corrected row is reported alongside it")

    comparison["_design_note"] = (
        "These bands were pre-registered in findings.md §6 for a CROSS-FAMILY "
        "model (Q1). This run uses mimo-v2.6-flash, family `mimo`, which is a "
        "different family from Jev (jev-1.13-free) and from the corpus author "
        "(space-bunny-free), so the confound that disqualified followup-01's "
        "verdict does not apply here. The band verdict below is the answer to "
        "Q1, subject to the run-level caveats in `_read_before_quoting`.")

    comparison["_read_before_quoting"] = [
        "n=64. No significance test is claimed anywhere (schema.md §5).",
        "One run, one attempt per cell, zero retries, one unpinned paid "
        "endpoint (findings.md §4 L3).",
        "MiMo is a reasoning model: 92%+ of its output budget went to "
        "reasoning inside the frozen max_tokens=256. Every cell returned "
        "content at N=1, but the margin against the empty-content failure "
        "mode was small. See usage_and_cost.reasoning.",
    ]

    return comparison, views, f1_ids


def _error_counts(rows):
    out = {}
    for r in rows:
        k = str(r.get("typed_error"))
        out[k] = out.get(k, 0) + 1
    return out


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
    print("score_mimo: verifying frozen inputs")
    frozen = verify_frozen_inputs()
    for rel, d in frozen.items():
        print(f"  {rel}: {d['actual']} {'OK' if d['match'] else 'MISMATCH'}")

    cases = load_cases(os.path.join(PHASE1, "cases.ndjson"))
    rows, src = load_mechanism_rows()
    new_path = os.path.join(args.results_dir, "mimo_raw.ndjson")
    seed = {"cases": cases, "rows": rows, "frozen": frozen,
            "new_sha": sha256_file(new_path),
            "new_rows": len(load_ndjson(new_path))}

    print("score_mimo: building cells and metrics")
    comparison, views, f1_ids = build(seed)

    cj = os.path.join(args.results_dir, "comparison.json")
    paired_path = os.path.join(args.results_dir, "paired.ndjson")
    mf = os.path.join(args.results_dir, "manifest.json")

    def write_all(comp, views_, f1_ids_):
        with open(cj, "w", encoding="utf-8", newline="\n") as f:
            json.dump(comp, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
        n = write_paired_ndjson(paired_path, views_, views_["raw_gt"]["cases"],
                                f1_ids_)
        return n

    n = write_all(comparison, views, f1_ids)

    new_rows = load_ndjson(new_path)
    commit = args.commit or git("rev-parse", "HEAD") or "unknown"
    session = {}
    sp = os.path.join(FOLLOWUP, "results", "run_session.json")
    if os.path.exists(sp):
        with open(sp, "r", encoding="utf-8") as f:
            session = json.load(f)
    manifest = {
        "schema_version": COMPARISON_SCHEMA_VERSION,
        "crosslink_issue": 565,
        "followup": "followup-02-mimo-v2.6-flash",
        "generated_utc": generated_utc,
        "commit": commit,
        "scorer": {"version": SCORER_VERSION,
                   "path": "followup-02-mimo-v2.6-flash/harness/score_mimo.py",
                   "stdlib_only": True,
                   "reuses": ["common.py", "score.py"],
                   "python": "%d.%d" % sys.version_info[:2]},
        "runner": {"version": "1.1.0",
                   "path": "followup-02-mimo-v2.6-flash/harness/run_mimo.py"},
        "frozen_inputs": frozen,
        "model": {
            "catalog_id": MODEL_CATALOG_ID,
            "model_id": MODEL_ID,
            "mechanism_label": NEW,
            "provider": "OpenCode Go model, served on the OpenCode Go route",
            "endpoint": ENDPOINT,
            "route_note": "the operator-stated Go route. The Zen route the "
                          "frozen general_model used does not host this model "
                          "(400 Model is unavailable), so the route change is "
                          "forced by the model, not chosen.",
            "cost": {"input": 0.14, "output": 0.28, "cache_read": 0.0028,
                     "cache_write": 0.0},
            "context": 1048576,
            "catalog_refreshed": "2026-09-26",
            "family": "DIFFERENT family from Jev and from the corpus author "
                      "(findings.md §4 L1). This run is the cross-family test "
                      "Q1 calls for; followup-01 was disqualified as "
                      "same-family.",
        },
        "credential": {
            "resolution_order": ["env:OPENCODE_GO_API_KEY",
                                 "auth.json#opencode-go"],
            "source_used": session.get("credential_source_used"),
            "value_recorded": False,
            "note": "the $OPENCODE_GO_API_KEY credential is returned 403 "
                    "\"An active OpenCode Go subscription is required\" by the "
                    "Go route for every model; the subscribed credential in the "
                    "OpenCode CLI credential store is served normally. Only the "
                    "source LABEL is recorded. The value reaches curl on stdin "
                    "via `curl -K -`, so it is in neither argv nor any file.",
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
            "session_header_name": session.get("session_header_name"),
            "session_header_value": session.get("session_header_value"),
            "session_header_note": session.get("session_header_note"),
            "transport_note": "curl subprocess. The frozen urllib transport is "
                              "Cloudflare-rejected (403, code 1010) with the "
                              "same credential. The x-opencode-session "
                              "provenance header is a per-run uuid4, not part "
                              "of the hashed body.",
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
        "secrets": {"credential_sources": ["env:OPENCODE_GO_API_KEY",
                                           "auth.json#opencode-go"],
                    "value_recorded": False,
                    "secrets_recorded_field": False},
    }
    outputs = {}
    for name, path in (("mimo_raw.ndjson", new_path),
                       ("paired.ndjson", paired_path),
                       ("comparison.json", cj)):
        outputs[name] = sha256_file(path)
    manifest["outputs_sha256"] = outputs
    with open(mf, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")

    print(f"score_mimo: wrote comparison.json, paired.ndjson ({n} rows), "
          f"manifest.json")

    if args.self_check:
        before = {k: sha256_file(os.path.join(args.results_dir, k))
                  for k in ("comparison.json", "paired.ndjson", "manifest.json")}
        print("score_mimo: self-check, second pass")
        comparison2, views2, f1_ids2 = build(seed)
        write_all(comparison2, views2, f1_ids2)
        # The manifest is rewritten too, from the same pinned timestamp and the
        # same on-disk inputs, so all three hashes are a real check.
        with open(mf, "w", encoding="utf-8", newline="\n") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
        after = {k: sha256_file(os.path.join(args.results_dir, k))
                 for k in ("comparison.json", "paired.ndjson", "manifest.json")}
        same = before == after
        print("  pass 1:", json.dumps(before, indent=2))
        print("  pass 2:", json.dumps(after, indent=2))
        print(f"  DETERMINISM: {'IDENTICAL' if same else 'DIVERGED'}")
        if not same:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
