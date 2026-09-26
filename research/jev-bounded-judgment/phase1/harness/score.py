#!/usr/bin/env python3
"""Jev Phase 1 scorer — turns raw mechanism responses into scored records,
machine-readable metrics, a run manifest, and the summary tables.

Stdlib only. Deterministic: the same raw files always produce byte-identical
`results/scored.ndjson` and `results/metrics.json`. The only wall-clock value
anywhere is `manifest.scoring.generated_utc`, which is injectable with
`--generated-utc` so a verifier can pin it and diff the whole tree.

    python3 harness/score.py                # score + metrics + manifest + tables
    python3 harness/score.py --no-tables    # scoring artefacts only
    python3 harness/score.py --self-check   # score twice, assert identical

DESIGN RULES (from schema.md 3.4)
--------------------------------
Scoring inputs are `prediction.label`, `prediction.probabilities`,
`prediction.confidence_reported`, the case's `ground_truth`,
`routing.signals`, `split`, `area` and `control`. Nothing else. In particular
`latency_ms`, `timestamp_utc`, `attempt`, `retries`, `usage` and `http_status`
are carried into `scored.ndjson` for cost/reliability reporting and are NEVER
read by a threshold, a ranking, or a verdict.

TWO PROPOSITIONS THIS FILE DOES *NOT* ACCEPT AT FACE VALUE
---------------------------------------------------------
1. `routing.legal_roles` / `illegal_roles` / `expected_role` are RECOMPUTED from
   `routing.signals` by `routing_policy.compute_legality` and compared with the
   stored block. The stored answer is checked, never trusted.
2. `prediction.confidence_formula` is RECOMPUTED from the stored probability
   vector and compared with the stored value. A silent harness bug in that
   derivation would otherwise propagate into every coverage number.

READ THIS BEFORE QUOTING ANY NUMBER
-----------------------------------
Jev returns **no `confidence` field and no `probabilities` field** for `noul`
questions. 50 of the 64 cases are `noul` (all of areas A, B and C). So for
those 50 cells the confidence used by every threshold sweep is LOCALLY DERIVED
from the single `noul` = P(yes) number via `(n*max(p)-1)/(n-1)`, not supplied
by the API. `metrics.json -> m4b_confidence_convention_sensitivity` reports what
happens under each convention, and the tables carry the convention in every
coverage cell. A headline "Jev covers 59% at 0 errors" is a statement about a
derived quantity.

HONESTY NOTES CARRIED FROM THE BASELINE RUNNERS
-----------------------------------------------
* The `rule` and `lexical` cue lexicons were hand-authored by the same agent
  that authored the corpus, with the corpus vocabulary in view. They are
  hand-built baselines, not discovered ones. Their accuracy is an UPPER BOUND
  on a generic cue engine, and the hand-built `rule` numbers are an UPPER BOUND
  on what a rule engine could do here.
* `rule` on area D is not a cue engine at all: it evaluates
  `routing_policy.compute_legality`, the same policy that DEFINES the expected
  role. Its 12/12 is a tautology, not a discovery.
* `general_model` is decoded to a hard one-hot label, so its derived confidence
  is identically 1.0 on every cell. Its threshold coverage is therefore 100% by
  construction and its selective-prediction numbers are an artefact of the
  encoding, not a measurement. The tables say so at the point of use.
* `rule` confidences outside area D come from ASSUMED constants
  (`RULE_HARD_CONF` 0.75, `RULE_SOFT_CONF` 0.55) injected into `_sigmoid_probs`.
  Those are modelling assumptions, not measurements.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE1 = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from common import MECHANISMS, RESULT_SCHEMA_VERSION, load_cases  # noqa: E402
from routing_policy import compute_legality  # noqa: E402

SCORER_VERSION = "1.0.0"
SCORED_SCHEMA_VERSION = "jevp1-scored-1.0"

# Escalation thresholds and error budgets are fixed by README.md, not tuned.
THRESHOLDS = (0.70, 0.80, 0.90, 0.95)
BUDGETS = (0.01, 0.05, 0.10)
AREAS = ("A", "B", "C", "D")
SPLITS = ("train", "dev", "test")
VARIANT_KINDS = ("irrelevant_change", "distractor", "noise", "opaque_labels",
                 "option_reorder", "missing_evidence")
JEV = "jev"

RAW_FILES = {
    "jev": "jev_raw.ndjson",
    "baselines": "baselines_raw.ndjson",
}
SUPERSEDED_FILES = ("baselines_raw_prefix_max_tokens16.ndjson",)

# What the confidence on a cell actually is. Carried into every table that uses
# a threshold, so no reader can mistake a derived value for a reported one.
CONFIDENCE_NOTE = {
    "prior": "derived from the measured TRAIN-split label distribution",
    "rule": "ASSUMED constant injected by the rule engine (0.75/0.55/0.90), "
            "not a measurement; area D re-derives it from the routing policy",
    "lexical": "derived from an arbitrary-scale token-overlap softmax; the "
               "scale is not calibrated, only monotone in overlap",
    "jev": "MIXED: API-reported for choice/score (14 cells), locally derived "
           "from noul for noul (50 cells) — see the caveat block above",
    "general_model": "IDENTICALLY 1.0 by construction (hard one-hot decode); "
                     "threshold coverage is an encoding artefact, not a "
                     "measurement",
}


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def r4(x):
    return None if x is None else round(float(x), 4)


def frac(n, d):
    return None if not d else round(n / d, 4)


def pct(x, dp=1):
    return "n/a" if x is None else f"{100.0 * x:.{dp}f}%"


def pp(x, dp=1):
    return "n/a" if x is None else f"{100.0 * x:+.{dp}f}pp"


def load_ndjson(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise SystemExit(
                    f"FATAL {path}:{lineno} is not valid JSON: {e}") from e
    return rows


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git(*args):
    try:
        return subprocess.run(["git", *args], cwd=PHASE1, check=True,
                              capture_output=True, text=True).stdout.strip()
    except Exception:  # noqa: BLE001 - provenance is best-effort, never fatal
        return None


# ---------------------------------------------------------------------------
# per-cell scoring
# ---------------------------------------------------------------------------
def confidence_of(prediction):
    """(confidence, source) for a cell, preferring the API's own field.

    `reported` -> the API supplied `confidence`.
    `derived`  -> recomputed locally as (n*max(p)-1)/(n-1) over the cell's own
                  probability vector. For `noul` this is the ONLY option: the
                  API supplies no confidence and no probabilities.
    `none`     -> a one-category vector or no prediction; no threshold applies.
    """
    if not prediction:
        return None, "none"
    rep = prediction.get("confidence_reported")
    if rep is not None:
        return float(rep), "reported"
    der = prediction.get("confidence_formula")
    if der is not None:
        return float(der), "derived"
    return None, "none"


def brier(probabilities, truth):
    """Multi-category Brier score: sum over categories of (p - onehot)^2.

    NOT divided by the number of categories, so a 6-way routing answer is
    penalised on the same 0..2 scale as a 2-way noul answer. Lower is better;
    0.0 means a perfect one-hot on the truth.
    """
    if not probabilities or truth is None:
        return None
    keys = set(probabilities) | {truth}
    return round(sum((float(probabilities.get(k, 0.0))
                      - (1.0 if k == truth else 0.0)) ** 2
                     for k in keys), 6)


def build_cell(case, row):
    """One scored (case, mechanism) cell. This is the scored.ndjson payload."""
    gt = case["ground_truth"]
    pred = row.get("prediction")
    usable = bool(pred and pred.get("label") is not None)
    answerable = bool(gt["answerable"]) and gt.get("answer") is not None
    conf, conf_src = confidence_of(pred)
    probs = pred.get("probabilities") if pred else None

    cell = {
        "schema_version": SCORED_SCHEMA_VERSION,
        "case_id": case["id"],
        "mechanism": row["mechanism"],
        "area": case["area"],
        "split": case["split"],
        "difficulty": case["difficulty"],
        "question_type": case["questions"][0]["type"],
        "pair_id": case["control"]["pair_id"],
        "variant_kind": case["control"]["variant_kind"],
        "base_case_id": case["control"].get("base_case_id"),

        "usable": usable,
        "unusable_reason": None if usable else (row.get("typed_error")
                                                or "no_prediction"),
        "answerable": answerable,
        # An unanswerable case is not "wrong" — it is a case where answering at
        # all is the failure mode. Kept separate from `correct` on purpose.
        "unanswerable": not answerable,
        "unanswerable_but_answered": bool((not answerable) and usable),
        "abstain_expected": bool(gt["abstain_expected"]),
        "abstained": bool(row.get("abstained")),

        "gt_answer": gt.get("answer"),
        "pred_label": pred.get("label") if pred else None,
        "correct": (bool(pred["label"] == gt["answer"])
                    if (usable and answerable) else None),
        "probabilities": probs,
        "max_prob": pred.get("max_prob") if pred else None,
        "prob_sum": pred.get("prob_sum") if pred else None,
        "score_value": pred.get("score") if pred else None,
        "brier": brier(probs, gt.get("answer")),

        "confidence": r4(conf) if conf is not None else None,
        "confidence_source": conf_src,
        "confidence_reported": (pred.get("confidence_reported")
                                if pred else None),
        "confidence_formula": (pred.get("confidence_formula")
                               if pred else None),
        "confidence_check_ok": None,

        # Recorded, never scored on.
        "typed_error": row.get("typed_error"),
        "error_detail": row.get("error_detail"),
        "http_status": row.get("http_status"),
        "endpoint": row.get("endpoint"),
        "model_id": row.get("model_id"),
        "request_hash": row.get("request_hash"),
        "latency_ms": row.get("latency_ms"),
        "usage": row.get("usage"),
        "attempt": row.get("attempt"),
        "retries": row.get("retries"),
        "timestamp_utc": row.get("timestamp_utc"),
    }

    # Proposition 2: recompute the stored derived confidence. A mismatch means
    # the runner's derivation drifted, so it is surfaced per cell.
    if usable and probs and len(probs) >= 2:
        n = len(probs)
        expect = max(0.0, min(1.0, (n * max(probs.values()) - 1.0) / (n - 1.0)))
        stored = pred.get("confidence_formula")
        cell["confidence_check_ok"] = (stored is not None
                                       and abs(stored - expect) <= 1e-9)

    if case.get("routing"):
        cell["routing"] = score_routing(case, cell)
    return cell


def score_routing(case, cell):
    """Recompute legality from signals, then judge the prediction against it.

    Proposition 1. The stored block is compared, not trusted; `recompute_ok`
    is the comparison result.
    """
    stored = case["routing"]
    recomputed = compute_legality(stored["signals"])
    recompute_ok = all(
        recomputed[k] == stored.get(k) for k in
        ("policy_rule_id", "legal_roles", "illegal_roles", "expected_role"))

    lm = case["control"].get("label_map") or {}
    order = [lm.get(k, k) for k in case["questions"][0]["criteria"].keys()]
    pred = cell["pred_label"]
    usable = cell["usable"]
    expected = stored.get("expected_role")
    return {
        "expected_role": expected,
        "legal_roles": list(stored["legal_roles"]),
        "illegal_roles": list(stored["illegal_roles"]),
        "pred_role": pred,
        "is_legal": (pred in stored["legal_roles"]) if usable else None,
        "is_illegal": (pred in stored["illegal_roles"]) if usable else None,
        "is_expected": (pred == expected) if usable else None,
        "option_order": order,
        "n_options": len(order),
        "pred_position": (order.index(pred)
                          if usable and pred in order else None),
        "expected_position": (order.index(expected)
                              if expected in order else None),
        "recompute_ok": recompute_ok,
        "recomputed": {k: recomputed[k] for k in
                       ("legal_roles", "illegal_roles", "expected_role")},
    }


# ---------------------------------------------------------------------------
# metrics
# ---------------------------------------------------------------------------
def by_mech(cells):
    out = collections.defaultdict(list)
    for c in cells:
        out[c["mechanism"]].append(c)
    for m in out:
        out[m].sort(key=lambda c: c["case_id"])
    return out


def _acc(scope):
    """accuracy triple over a list of cells.

    acc_answerable : correct / usable, ANSWERABLE cases only. Answers the
                     question "given that it produced a label, was it right?"
    acc_mixed      : over ALL cells, counting "answered an unanswerable case"
                     as an error. Answers "is this mechanism safe to run?"
    false_conf     : answered / all unanswerable cells. The abstention metric.
    """
    ans = [c for c in scope if not c["unanswerable"]]
    unans = [c for c in scope if c["unanswerable"]]
    ans_usable = [c for c in ans if c["usable"]]
    correct = sum(1 for c in ans_usable if c["correct"])
    mixed_correct = correct + sum(1 for c in unans
                                  if not c["unanswerable_but_answered"])
    return {
        "n_cells": len(scope),
        "n_answerable": len(ans),
        "n_unanswerable": len(unans),
        "n_usable": sum(1 for c in scope if c["usable"]),
        "n_unusable": sum(1 for c in scope if not c["usable"]),
        "acc_answerable": frac(correct, len(ans_usable)),
        "acc_mixed": frac(mixed_correct, len(scope)),
        "n_correct_answerable": correct,
        "n_answered_unanswerable": sum(1 for c in unans
                                       if c["unanswerable_but_answered"]),
        "false_confidence_rate": frac(sum(1 for c in unans
                                          if c["unanswerable_but_answered"]),
                                      len(unans)),
        # A deliberate abstention is the cell setting `abstained`, which is
        # distinct from emitting no label because the transport failed.
        "n_abstained_flag": sum(1 for c in scope if c["abstained"]),
        "n_unanswerable_no_label": sum(1 for c in unans
                                       if not c["unanswerable_but_answered"]),
    }


def m1_accuracy(MB):
    overall = {m: _acc(MB[m]) for m in MECHANISMS}
    by_area = {m: {a: _acc([c for c in MB[m] if c["area"] == a])
                   for a in AREAS} for m in MECHANISMS}
    by_split = {m: {s: _acc([c for c in MB[m] if c["split"] == s])
                    for s in SPLITS} for m in MECHANISMS}
    by_difficulty = {
        m: {d: _acc([c for c in MB[m] if c["difficulty"] == d])
            for d in sorted({c["difficulty"] for c in MB[JEV]})}
        for m in MECHANISMS}
    return {"definitions": {
        "acc_answerable": "correct / usable, over answerable cases only",
        "acc_mixed": "over all cells; answering an unanswerable case is an error",
        "false_confidence_rate": "answered / all unanswerable cases",
    }, "overall": overall, "by_area": by_area, "by_split": by_split,
        "by_difficulty": by_difficulty}


def m2_brier(MB):
    def mean(scope):
        v = [c["brier"] for c in scope
             if c["brier"] is not None and c["usable"] and not c["unanswerable"]]
        return frac(round(sum(v) / len(v), 6), 1) if v else None

    out = {}
    for m in MECHANISMS:
        cells = MB[m]
        out[m] = {
            "all_answerable": mean(cells),
            "by_question_type": {t: mean([c for c in cells
                                          if c["question_type"] == t])
                                 for t in sorted({c["question_type"]
                                                  for c in cells})},
            "by_split": {s: mean([c for c in cells if c["split"] == s])
                         for s in SPLITS},
            "n_scored": sum(1 for c in cells
                            if c["brier"] is not None and not c["unanswerable"]),
        }
    out["_definition"] = (
        "sum over categories of (p - onehot)^2, un-normalised by category count; "
        "answerable cases with a usable prediction only. A general model decoded "
        "to a hard label therefore scores 0.0 by construction whenever it is "
        "right — that is an encoding floor, not perfect calibration. An ECE / "
        "reliability diagram is deliberately NOT reported: these vectors are "
        "P(label) under the model's own answer, not frequency forecasts, so "
        "binning them against realised frequencies would not be meaningful.")
    return out


def _paired_gain(MB, mech, prev, sel):
    """McNemar-style paired delta on the cases where both mechanisms answered.

    `b` = cases the challenger got right and the incumbent got wrong.
    `c` = the reverse. `delta` is the accuracy difference in proportion points.
    No p-value is claimed (schema.md 5: n=64, cheapest-test-first bar).
    """
    cur = {c["case_id"]: c for c in MB[mech]}
    prv = {c["case_id"]: c for c in MB[prev]}
    pair = [cid for cid in sorted(cur)
            if cid in prv
            and cur[cid]["usable"] and prv[cid]["usable"]
            and not cur[cid]["unanswerable"]
            and sel(cur[cid])]
    if not pair:
        return None
    n = len(pair)
    correct = sum(1 for x in pair if cur[x]["correct"])
    prev_correct = sum(1 for x in pair if prv[x]["correct"])
    return {
        "mechanism": mech, "vs": prev, "n_paired": n,
        "acc": frac(correct, n), "acc_prev": frac(prev_correct, n),
        "delta": r4((correct - prev_correct) / n),
        "discordant_b": sum(1 for x in pair
                            if cur[x]["correct"] and not prv[x]["correct"]),
        "discordant_c": sum(1 for x in pair
                            if not cur[x]["correct"] and prv[x]["correct"]),
    }


def m3_incremental_gain(MB):
    scopes = {
        "ALL": lambda c: True,
        **{f"area {a}": (lambda a: lambda c: c["area"] == a)(a) for a in AREAS},
        **{f"split {s}": (lambda s: lambda c: c["split"] == s)(s)
           for s in SPLITS},
    }
    out = {}
    for name, sel in scopes.items():
        rows = []
        for i, m in enumerate(MECHANISMS):
            if i == 0:
                rows.append({"mechanism": m, "role": "floor"})
                continue
            g = _paired_gain(MB, m, MECHANISMS[i - 1], sel)
            if g:
                g["role"] = "gain over cheapest preceding mechanism"
                rows.append(g)
        out[name] = rows
    out["_definition"] = (
        "MECHANISMS is ordered by cost (schema.md 3.1) and that order is "
        "normative, so 'cheapest preceding mechanism' is well defined. Pairing "
        "is restricted to cases where BOTH mechanisms produced a usable label on "
        "an ANSWERABLE case; unanswerable cases are excluded here and handled by "
        "m1.false_confidence_rate and m4 instead. discordant_b/c are the McNemar "
        "cells; no significance test is claimed.")
    return out


def m3b_jev_vs_all(MB):
    """Every jev-vs-X paired delta, because 'incremental gain' depends entirely
    on which incumbent you name. Reported so the headline is not cherry-picked.
    """
    out = {}
    for m in MECHANISMS:
        if m == JEV:
            continue
        g = _paired_gain(MB, JEV, m, lambda c: True)
        if g:
            out[JEV + "_vs_" + m] = g
    out["_read_this"] = (
        "jev vs prior/rule/lexical is the cheap-baseline question (area A of the "
        "brief). jev vs general_model is the honest comparator: both are free-tier, "
        "and if the free chat model matches Jev then Jev's gain is over a "
        "mechanism the user could have run anyway.")
    return out


def _coverage(cells, thresholds=THRESHOLDS, source=None):
    """Coverage/error curve.

    An "act" is a cell whose confidence reaches the threshold. A cell whose
    mechanism produced no label, or no confidence at all, is EXCLUDED from the
    pool and counted in `excluded` — it can never be acted on. An "error" among
    the acted cells is either a wrong label on an answerable case, or any label
    at all on an unanswerable case (the abstention failure).
    """
    n = len(cells)
    pool = [c for c in cells
            if c["usable"] and c["confidence"] is not None
            and (source is None or c["confidence_source"] == source)]
    out = []
    for t in thresholds:
        acted = [c for c in pool if c["confidence"] >= t]
        errs = [c for c in acted
                if (c["unanswerable"] and c["unanswerable_but_answered"])
                or (not c["unanswerable"] and not c["correct"])]
        out.append({
            "threshold": t,
            "pool": len(pool),
            "excluded": n - len(pool),
            "acted": len(acted),
            "coverage": frac(len(acted), n),
            "n_errors": len(errs),
            "error_rate_of_acted": frac(len(errs), len(acted)),
            "n_errors_false_confidence": sum(1 for c in errs
                                             if c["unanswerable"]),
            "n_errors_wrong_label": sum(1 for c in errs
                                        if not c["unanswerable"]),
        })
    return out


def m4_coverage_error(MB):
    return {m: {"confidence_note": CONFIDENCE_NOTE[m],
                "curve": _coverage(MB[m])} for m in MECHANISMS}


def m5_error_budgets(MB):
    """Largest coverage reachable at each error budget.

    A budget of B% over n cells allows floor(B*n) errors. `discrete` records
    whether B*n was not an integer, because at n=64 a "1% budget" is 0.64
    errors and the floor is 0 — a 1% budget on 64 cells means ZERO errors.
    """
    out = {}
    for m in MECHANISMS:
        cells = MB[m]
        n = len(cells)
        curve = _coverage(cells)
        rows = []
        for b in BUDGETS:
            exact = b * n
            allowed = int(exact)
            feasible = [c for c in curve if c["n_errors"] <= allowed]
            best = (max(feasible, key=lambda c: (c["acted"], c["threshold"]))
                    if feasible else None)
            rows.append({
                "budget": b,
                "max_errors_exact": round(exact, 2),
                "max_errors_floor": allowed,
                "discrete": exact != allowed,
                "achievable": best is not None,
                "threshold": best["threshold"] if best else None,
                "coverage": best["coverage"] if best else None,
                "acted": best["acted"] if best else None,
                "n_errors": best["n_errors"] if best else None,
                "min_errors_any_threshold": min(c["n_errors"] for c in curve),
            })
        out[m] = {"confidence_note": CONFIDENCE_NOTE[m], "budgets": rows}
    return out


def m4b_confidence_convention_sensitivity(MB):
    """The single most important sensitivity in this run.

    Jev reports no confidence for noul. The headline coverage curve therefore
    uses a LOCALLY DERIVED confidence for 50 of 64 cells. This recomputes the
    whole curve under each convention so the reader can see exactly how much of
    the escalation story depends on the derived value.
    """
    out = {}
    for source in ("reported", "derived"):
        out[source] = {
            "curve": _coverage(MB[JEV], source=source),
            "n_pool": sum(1 for c in MB[JEV] if c["confidence_source"] == source),
        }
    out["source_counts"] = dict(sorted(collections.Counter(
        c["confidence_source"] for c in MB[JEV]).items()))
    out["source_by_question_type"] = {
        t: dict(sorted(collections.Counter(
            c["confidence_source"] for c in MB[JEV]
            if c["question_type"] == t).items()))
        for t in sorted({c["question_type"] for c in MB[JEV]})}
    out["_reading"] = (
        "A high coverage at 0 errors under 'derived' is evidence that the "
        "DERIVED quantity separates answerable from unanswerable cases — not "
        "evidence that Jev can support escalation, because Jev emitted a "
        "confident label on every unanswerable case it was given.")
    return out


def m6_contrastive_and_controls(MB, cases):
    """Contrastive pairs (the deciding fact is the only difference) and every
    control variant, per mechanism.

    `confidence_verdict` replaces the earlier scratch script's `inverted`
    counter, which was a dead branch: it accumulated the conjunction
    `a_correct and not b_correct and b_correct and not a_correct`, which is
    unsatisfiable, so it reported 0 for every mechanism without measuring
    anything. The measurable quantity is whether the confidence signal ranks
    the member the mechanism got wrong above the member it got right.
    """
    families = collections.defaultdict(list)
    for cid, c in cases.items():
        families[c["control"]["pair_id"]].append(cid)

    pairs = {}
    for m in MECHANISMS:
        idx = {c["case_id"]: c for c in MB[m]}
        rows = []
        for fam in sorted(families):
            members = sorted(families[fam])
            bases = [x for x in members
                     if cases[x]["control"]["variant_kind"] == "base"]
            if len(bases) != 2:
                continue
            a, b = idx.get(bases[0]), idx.get(bases[1])
            if not (a and b and a["usable"] and b["usable"]):
                continue
            n_correct = sum(1 for x in (a, b) if x["correct"])
            # Does the confidence signal rank the two members the way the truth
            # does? Four-valued, because a tie is NOT an inversion:
            #   correct_order  the member it got right carries the higher conf
            #   inverted       the member it got WRONG carries the higher conf
            #   tied           identical confidence -> no ranking expressed
            #   unmeasurable   confidence missing on one side, or both/neither
            #                  correct so there is no ranking to check
            if a["confidence"] is None or b["confidence"] is None:
                verdict = "unmeasurable"
            elif a["correct"] is None or b["correct"] is None \
                    or a["correct"] == b["correct"]:
                verdict = "unmeasurable"
            elif a["confidence"] == b["confidence"]:
                verdict = "tied"
            else:
                right_is_higher = ((a["confidence"] > b["confidence"])
                                   if a["correct"]
                                   else (b["confidence"] > a["confidence"]))
                verdict = "correct_order" if right_is_higher else "inverted"
            rows.append({
                "pair_id": fam,
                "cases": [a["case_id"], b["case_id"]],
                "gt": [a["gt_answer"], b["gt_answer"]],
                "pred": [a["pred_label"], b["pred_label"]],
                "confidence": [a["confidence"], b["confidence"]],
                "distinguished": a["pred_label"] != b["pred_label"],
                "n_correct": n_correct,
                "both_correct": n_correct == 2,
                "confidence_verdict": verdict,
            })
        n = len(rows)
        verdicts = collections.Counter(r["confidence_verdict"] for r in rows)
        pairs[m] = {
            "n_pairs": n,
            "n_distinguished": sum(1 for r in rows if r["distinguished"]),
            "n_both_correct": sum(1 for r in rows if r["both_correct"]),
            "n_one_correct": sum(1 for r in rows if r["n_correct"] == 1),
            "n_neither_correct": sum(1 for r in rows if r["n_correct"] == 0),
            "confidence_verdicts": {k: verdicts[k]
                                    for k in ("correct_order", "inverted",
                                              "tied", "unmeasurable")
                                    if verdicts[k]},
            "pairs": rows,
        }

    controls = {}
    for m in MECHANISMS:
        idx = {c["case_id"]: c for c in MB[m]}
        by_kind = {}
        for kind in VARIANT_KINDS:
            rows = []
            for cid, c in sorted(cases.items()):
                if c["control"]["variant_kind"] != kind:
                    continue
                base_id = c["control"].get("base_case_id")
                v, b = idx.get(cid), idx.get(base_id or "")
                if not (v and b):
                    continue
                rows.append({
                    "case_id": cid, "base_case_id": base_id,
                    "gt_base": b["gt_answer"], "gt_variant": v["gt_answer"],
                    "pred_base": b["pred_label"], "pred_variant": v["pred_label"],
                    "confidence_base": b["confidence"],
                    "confidence_variant": v["confidence"],
                    "delta_confidence": (round(v["confidence"] - b["confidence"], 4)
                                         if v["confidence"] is not None
                                         and b["confidence"] is not None
                                         else None),
                    "label_stable": v["pred_label"] == b["pred_label"],
                    "correct": v["correct"],
                    "answered_unanswerable": v["unanswerable_but_answered"],
                })
            if not rows:
                continue
            deltas = [r["delta_confidence"] for r in rows
                      if r["delta_confidence"] is not None]
            by_kind[kind] = {
                "n": len(rows),
                "n_label_stable": sum(1 for r in rows if r["label_stable"]),
                "n_correct": sum(1 for r in rows if r["correct"]),
                "n_answered_unanswerable": sum(1 for r in rows
                                               if r["answered_unanswerable"]),
                "mean_delta_confidence": (round(sum(deltas) / len(deltas), 4)
                                          if deltas else None),
                "min_delta_confidence": min(deltas) if deltas else None,
                "max_delta_confidence": max(deltas) if deltas else None,
                "variants": rows,
            }
        controls[m] = by_kind
    return {"pairs": pairs, "controls": controls}


def m7_order_consistency(MB, cases):
    """Option reorder + opaque-label rename, and option-position bias.

    Area D is the only place with a `choice` label space, so position bias is
    measured there. The predicted-position histogram is compared with the
    expected-position histogram; a mechanism that always picks, say, the first
    option would show one bucket at 0 and 11/12 at the mode.
    """
    perturb = {}
    for m in MECHANISMS:
        idx = {c["case_id"]: c for c in MB[m]}
        rows = []
        for cid, c in sorted(cases.items()):
            if c["control"]["variant_kind"] not in ("option_reorder",
                                                    "opaque_labels"):
                continue
            v, b = idx.get(cid), idx.get(c["control"]["base_case_id"] or "")
            if not (v and b and v.get("routing") and b.get("routing")):
                continue
            rows.append({
                "case_id": cid, "base_case_id": b["case_id"],
                "kind": c["control"]["variant_kind"],
                "pred_base": b["pred_label"], "pred_variant": v["pred_label"],
                "label_stable": v["pred_label"] == b["pred_label"],
                "both_correct": bool(v["correct"] and b["correct"]),
                "position_base": b["routing"]["pred_position"],
                "position_variant": v["routing"]["pred_position"],
                "n_options": v["routing"]["n_options"],
            })
        if rows:
            perturb[m] = {
                "n": len(rows),
                "n_label_stable": sum(1 for r in rows if r["label_stable"]),
                "n_both_correct": sum(1 for r in rows if r["both_correct"]),
                "rows": rows,
            }

    position = {}
    for m in MECHANISMS:
        hist = collections.Counter()
        exp = collections.Counter()
        n = match = 0
        for c in MB[m]:
            g = c.get("routing")
            if not g or not c["usable"] or g["pred_position"] is None:
                continue
            hist[g["pred_position"]] += 1
            exp[g["expected_position"]] += 1
            n += 1
            match += g["pred_position"] == g["expected_position"]
        if n:
            position[m] = {
                "n_answered": n, "n_options": 6,
                "uniform_share": frac(1, 6),
                "predicted_position_histogram": {str(k): hist[k]
                                                 for k in sorted(hist)},
                "expected_position_histogram": {str(k): exp[k]
                                                for k in sorted(exp)},
                "n_pred_matches_expected_position": match,
                "chi2_vs_expected_histogram": chi2(hist, exp, n),
            }
    return {"perturbation": perturb, "position_bias": position,
            "_note": ("n_options is 6 for every area-D case, so uniform is "
                      "1/6 = 0.1667. A mechanism that always answered the same "
                      "position would score far above uniform on the chi2. "
                      "`rule` and `general_model` matching the expected position "
                      "12/12 is a strong result for them; for `rule` it is also "
                      "partly tautological (see the honesty note).")}


def chi2(observed, expected_counts, n):
    """Chi-square of an observed position histogram against the expected one.

    Degrees of freedom = (number of occupied buckets - 1). No p-value is
    reported: at n=12 the cheapest-test-first bar forbids a significance claim,
    and this is reported as a descriptive distance only.
    """
    if not observed or not expected_counts:
        return None
    exp_total = sum(expected_counts.values()) or 1
    stat = 0.0
    for k in set(observed) | set(expected_counts):
        e = expected_counts.get(k, 0) * n / exp_total
        if e <= 0:
            continue
        stat += (observed.get(k, 0) - e) ** 2 / e
    return {"chi2": round(stat, 4),
            "df": max(1, len(set(observed) | set(expected_counts)) - 1),
            "p_value": None}


def m8_routing(MB):
    out = {}
    for m in MECHANISMS:
        cells = [c for c in MB[m] if c.get("routing")]
        usable = [c for c in cells if c["usable"]]
        out[m] = {
            "n_cases": len(cells),
            "n_usable": len(usable),
            "n_legal": sum(1 for c in usable if c["routing"]["is_legal"]),
            "n_illegal": sum(1 for c in usable if c["routing"]["is_illegal"]),
            "n_expected": sum(1 for c in usable if c["routing"]["is_expected"]),
            "n_recompute_mismatch": sum(1 for c in cells
                                        if not c["routing"]["recompute_ok"]),
            "per_case": [{"case_id": c["case_id"],
                          "expected_role": c["routing"]["expected_role"],
                          "legal_roles": c["routing"]["legal_roles"],
                          "pred_role": c["routing"]["pred_role"],
                          "is_legal": c["routing"]["is_legal"],
                          "is_illegal": c["routing"]["is_illegal"],
                          "correct": c["correct"],
                          "confidence": c["confidence"],
                          "confidence_source": c["confidence_source"]}
                         for c in sorted(cells,
                                         key=lambda x: x["case_id"])],
        }
    out["_definition"] = (
        "Legality is recomputed from routing.signals by routing_policy."
        "compute_legality and compared with the stored block; "
        "n_recompute_mismatch must be 0. A role is legal only when its own "
        "precondition signal is set, so the illegal candidates are structurally "
        "impossible — that is what makes area D adversarial rather than "
        "descriptive. TAUTOLOGY WARNING: `rule` evaluates that same policy, so "
        "its 12/12 is a definition, not a discovery.")
    return out


def m9_confidence_formula(MB):
    """Empirical test of the documented derivation
    `confidence = (n*max(p) - 1) / (n - 1)`, against the competing hypothesis
    `confidence = max(p)`.

    Only cells that actually carry an API-reported confidence can test it. For
    Jev that is 14/64 (the 12 `choice` and 2 `score` cases); the 50 `noul` cells
    report nothing and are therefore NOT part of this test.
    """
    out = {}
    for m in MECHANISMS:
        testable = [c for c in MB[m]
                    if c["usable"] and c["probabilities"]
                    and len(c["probabilities"]) >= 2
                    and c["confidence_reported"] is not None]
        if not testable:
            out[m] = {"testable": 0, "n_cells": len(MB[m]),
                      "verdict": "NOT TESTABLE — this mechanism reports no "
                                 "confidence field"}
            continue
        err_a, err_b, exact_a, exact_b, sizes = [], [], 0, 0, collections.Counter()
        for c in testable:
            pr = {k: float(v) for k, v in c["probabilities"].items()}
            n = len(pr)
            mx = max(pr.values())
            pred_a = max(0.0, min(1.0, (n * mx - 1.0) / (n - 1.0)))
            rep = float(c["confidence_reported"])
            err_a.append(abs(rep - pred_a))
            err_b.append(abs(rep - mx))
            exact_a += round(rep, 2) == round(pred_a, 2)
            exact_b += round(rep, 2) == round(mx, 2)
            sizes[n] += 1
        sa, sb = sum(err_a), sum(err_b)
        out[m] = {
            "testable": len(testable), "n_cells": len(MB[m]),
            "label_space_sizes": {str(k): v for k, v in sorted(sizes.items())},
            "hypothesis_A_formula": {
                "expression": "(n*max(p) - 1) / (n - 1)",
                "mean_abs_error": r4(sum(err_a) / len(err_a)),
                "median_abs_error": r4(sorted(err_a)[len(err_a) // 2]),
                "max_abs_error": r4(max(err_a)),
                "n_within_0.005": sum(1 for e in err_a if e <= 0.005),
                "n_within_0.01": sum(1 for e in err_a if e <= 0.01),
                "n_exact_at_2dp": exact_a,
            },
            "hypothesis_B_max_prob": {
                "expression": "max(p)",
                "mean_abs_error": r4(sum(err_b) / len(err_b)),
                "median_abs_error": r4(sorted(err_b)[len(err_b) // 2]),
                "max_abs_error": r4(max(err_b)),
                "n_within_0.005": sum(1 for e in err_b if e <= 0.005),
                "n_within_0.01": sum(1 for e in err_b if e <= 0.01),
                "n_exact_at_2dp": exact_b,
            },
            "sum_abs_error_A": r4(sa), "sum_abs_error_B": r4(sb),
            "A_strictly_better_than_B": sa < sb,
        }

    jev = [c for c in MB[JEV] if c["usable"]]
    out["jev_by_question_type"] = {
        t: {"n_cells": sum(1 for c in jev if c["question_type"] == t),
            "n_with_reported_confidence": sum(
                1 for c in jev if c["question_type"] == t
                and c["confidence_reported"] is not None)}
        for t in sorted({c["question_type"] for c in jev})}

    out["stored_formula_recheck"] = {
        m: {"n_checked": sum(1 for c in MB[m] if c["confidence_check_ok"] is not None),
            "n_mismatch": sum(1 for c in MB[m]
                              if c["confidence_check_ok"] is False)}
        for m in MECHANISMS}
    out["_definition"] = (
        "Residual = |reported confidence - hypothesis|. Probabilities are "
        "published rounded, so a residual of one or two units in the last place "
        "is the rounding floor, not a refutation. Hypothesis A is supported "
        "where A's mean absolute residual is materially below B's. A CHEAP TEST "
        "IS NOT AVAILABLE for noul: the API publishes no confidence there, so "
        "the derivation can only be tested on 14 of Jev's 64 cells.")
    return out


def m10_cost_reliability(MB):
    """Recorded for cost/reliability analysis ONLY. Never a scoring input
    (schema.md 3.4). Nothing downstream reads this."""
    out = {}
    for m in MECHANISMS:
        cells = MB[m]
        lat = sorted(c["latency_ms"] for c in cells
                     if c["latency_ms"] is not None)
        in_tok = out_tok = 0
        for c in cells:
            u = c.get("usage") or {}
            in_tok += (u.get("input_tokens") or u.get("prompt_tokens") or 0)
            out_tok += (u.get("output_tokens")
                        or u.get("completion_tokens") or 0)
        errs = collections.Counter(str(c["typed_error"]) for c in cells)
        out[m] = {
            "n_cells": len(cells),
            "latency_ms_min": lat[0] if lat else None,
            "latency_ms_median": lat[len(lat) // 2] if lat else None,
            "latency_ms_max": lat[-1] if lat else None,
            "total_input_tokens": in_tok,
            "total_output_tokens": out_tok,
            "total_retries": sum(c["retries"] or 0 for c in cells),
            "max_attempt": max((c["attempt"] or 0) for c in cells),
            "typed_errors": dict(sorted(errs.items())),
            "endpoints": sorted({c["endpoint"] for c in cells
                                 if c["endpoint"]}),
            "model_ids": sorted({c["model_id"] for c in cells
                                 if c["model_id"]}),
        }
    out["_not_a_scoring_input"] = True
    return out


def compute_all(cells, cases):
    MB = by_mech(cells)
    metrics = {
        "_scorer_version": SCORER_VERSION,
        "_grid": {"n_cases": len(cases), "n_mechanisms": len(MECHANISMS),
                  "n_cells": len(cells), "complete": True},
        "m1_accuracy": m1_accuracy(MB),
        "m2_brier": m2_brier(MB),
        "m3_incremental_gain": m3_incremental_gain(MB),
        "m3b_jev_vs_all": m3b_jev_vs_all(MB),
        "m4_coverage_error": m4_coverage_error(MB),
        "m4b_confidence_convention_sensitivity":
            m4b_confidence_convention_sensitivity(MB),
        "m5_error_budgets": m5_error_budgets(MB),
        "m6_contrastive_and_controls": m6_contrastive_and_controls(MB, cases),
        "m7_order_consistency": m7_order_consistency(MB, cases),
        "m8_routing": m8_routing(MB),
        "m9_confidence_formula": m9_confidence_formula(MB),
        "m10_cost_reliability": m10_cost_reliability(MB),
    }
    return metrics


# ---------------------------------------------------------------------------
# tables
# ---------------------------------------------------------------------------
def md_table(headers, rows, aligns=None):
    aligns = aligns or ["---"] * len(headers)
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(aligns) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def write_tables(metrics, out_dir, cases):
    os.makedirs(out_dir, exist_ok=True)
    written = []
    m1, m2, m3 = metrics["m1_accuracy"], metrics["m2_brier"], metrics["m3_incremental_gain"]
    m3b, m4, m4b = (metrics["m3b_jev_vs_all"], metrics["m4_coverage_error"],
                    metrics["m4b_confidence_convention_sensitivity"])
    m5, m6, m7 = (metrics["m5_error_budgets"],
                  metrics["m6_contrastive_and_controls"],
                  metrics["m7_order_consistency"])
    m8, m9, m10 = (metrics["m8_routing"], metrics["m9_confidence_formula"],
                   metrics["m10_cost_reliability"])

    def w(name, text):
        path = os.path.join(out_dir, name)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.rstrip() + "\n")
        written.append(name)

    # ---- T1 accuracy ------------------------------------------------------
    hdr = (["mechanism", "cells", "answerable", "unanswerable", "usable",
            "acc answerable-only", "acc mixed", "answered unanswerable",
            "false-confidence rate", "abstained flag"])
    rows = [[m, m1["overall"][m]["n_cells"], m1["overall"][m]["n_answerable"],
             m1["overall"][m]["n_unanswerable"], m1["overall"][m]["n_usable"],
             pct(m1["overall"][m]["acc_answerable"]),
             pct(m1["overall"][m]["acc_mixed"]),
             f'{m1["overall"][m]["n_answered_unanswerable"]}'
             f'/{m1["overall"][m]["n_unanswerable"]}',
             pct(m1["overall"][m]["false_confidence_rate"]),
             m1["overall"][m]["n_abstained_flag"]]
            for m in MECHANISMS]
    w("T1-accuracy-overall.md",
      "# T1 — Accuracy per mechanism (whole grid)\n\n"
      f"Generated by `harness/score.py` {SCORER_VERSION} from "
      f"`results/scored.ndjson`. {metrics['_grid']['n_cases']} cases x "
      f"{metrics['_grid']['n_mechanisms']} mechanisms = "
      f"{metrics['_grid']['n_cells']} cells.\n\n"
      "- **acc answerable-only** = correct / usable on the 50 answerable cases. "
      "Answers *given that it produced a label, was it right?*\n"
      "- **acc mixed** = over all 64 cells, counting any label on an "
      "unanswerable case as an error. Answers *is this safe to run?*\n"
      "- **false-confidence rate** = answered / all 14 unanswerable cases. This "
      "is the abstention metric, and it is the column that decides whether the "
      "high answerable-only accuracy means anything.\n"
      "- **abstained flag** = cells where the mechanism itself recorded a "
      "deliberate abstention. Zero everywhere; see `T7` §T7c.\n\n"
      + md_table(hdr, rows) + "\n")

    # ---- T2 per-area ------------------------------------------------------
    area_rows = []
    for m in MECHANISMS:
        for a in AREAS:
            d = m1["by_area"][m][a]
            area_rows.append([m, a, d["n_cells"], d["n_answerable"],
                              d["n_unanswerable"],
                              pct(d["acc_answerable"]) if d["n_answerable"]
                              else "n/a (all unanswerable)",
                              pct(d["acc_mixed"]),
                              f'{d["n_answered_unanswerable"]}'
                              f'/{d["n_unanswerable"]}'])
    w("T2-accuracy-by-area.md",
      "# T2 — Accuracy per area\n\n"
      "Area A cheap-baseline comparison · B abstention/escalation · "
      "C contrastive/causal perturbations · D workflow routing.\n\n"
      "**Area B is 13/13 unanswerable** — every area-B case has "
      "`answerable=false` and `abstain_expected=true`, so `acc answerable-only` "
      "is undefined there and the mixed column plus the false-confidence column "
      "are the whole of the area-B result.\n\n"
      + md_table(["mechanism", "area", "cells", "answerable", "unanswerable",
                  "acc answerable-only", "acc mixed", "answered unanswerable"],
                 area_rows) + "\n\n"
      + md_table(["mechanism", "split", "cells", "acc answerable-only",
                  "acc mixed"],
                 [[m, s, m1["by_split"][m][s]["n_cells"],
                   pct(m1["by_split"][m][s]["acc_answerable"]),
                   pct(m1["by_split"][m][s]["acc_mixed"])]
                  for m in MECHANISMS for s in SPLITS]) + "\n")

    # ---- T3 incremental gain --------------------------------------------
    ig = []
    for scope in ["ALL"] + [f"area {a}" for a in AREAS] + [f"split {s}"
                                                           for s in SPLITS]:
        for r in m3[scope]:
            if r.get("role") == "floor":
                ig.append([scope, r["mechanism"], "—", "—", "—", "—", "—",
                           "floor (cheapest mechanism)"])
                continue
            ig.append([scope, r["mechanism"], r["vs"], r["n_paired"],
                       pct(r["acc"]), pct(r["acc_prev"]), pp(r["delta"]),
                       f'b={r["discordant_b"]} c={r["discordant_c"]}'])
    jv = [[k.replace("_vs_", " vs "), v["vs"], v["n_paired"], pct(v["acc"]),
           pct(v["acc_prev"]), pp(v["delta"]),
           f'b={v["discordant_b"]} c={v["discordant_c"]}']
          for k, v in m3b.items() if not k.startswith("_")]
    w("T3-incremental-gain.md",
      "# T3 — Incremental gain over the cheapest preceding mechanism\n\n"
      "Mechanism cost order is normative (`schema.md` 3.1): prior -> rule -> "
      "lexical -> jev -> general_model. So **Jev's cheapest preceding mechanism "
      "is `lexical`** and that is the headline row.\n\n"
      "Pairing: cases where BOTH mechanisms produced a usable label on an "
      "ANSWERABLE case. Unanswerable cases are excluded here and handled by the "
      "false-confidence column of T1/T2. `b` = challenger right / incumbent "
      "wrong, `c` = the reverse (McNemar cells). **No significance test is "
      "claimed** — at n<=50 the cheapest-test-first bar forbids it.\n\n"
      "## T3a — chain\n\n"
      + md_table(["scope", "mechanism", "vs", "n paired", "acc", "prev acc",
                  "delta", "McNemar"], ig) + "\n\n"
      "## T3b — Jev against every other mechanism, whole grid\n\n"
      + md_table(["comparison", "incumbent", "n paired", "jev acc",
                  "incumbent acc", "delta", "McNemar"], jv) + "\n\n"
      "> T3b is the honest comparator set. `jev vs lexical` is the "
      "cheap-baseline question the brief asks; `jev vs general_model` is the "
      "one that decides the brief's actual question, because both mechanisms "
      "are free-tier and the general model was available to the user anyway. "
      "A negative delta there means Jev adds nothing over a free chat model on "
      "this corpus.\n\n" + m3["_definition"] + "\n\n" + m3b["_read_this"] + "\n")

    # ---- T4 Brier ---------------------------------------------------------
    brow = [[m, pct(m2[m]["all_answerable"]), m2[m]["n_scored"]]
            + [pct(m2[m]["by_question_type"].get(t))
               for t in ("noul", "choice", "score")]
            + [pct(m2[m]["by_split"].get(s)) for s in SPLITS]
            for m in MECHANISMS]
    w("T4-brier.md",
      "# T4 — Brier score per mechanism\n\n"
      "Lower is better; 0.0 is a perfect one-hot on the truth. Answerable cases "
      "with a usable prediction only.\n\n"
      + md_table(["mechanism", "Brier (all answerable)", "n scored", "noul",
                  "choice", "score", "train", "dev", "test"], brow) + "\n\n"
      "> " + m2["_definition"] + "\n\n"
      "> `general_model` is decoded to a hard one-hot, so its Brier is 0.0 "
      "whenever it is right and 1.0 (2-way) / 1.8 (6-way routing) whenever it "
      "is not. It is an **encoding floor, not a calibration result**, and it is "
      "not comparable to a mechanism that emits a graded distribution.\n")

    # ---- T5 coverage / error --------------------------------------------
    crows = []
    for m in MECHANISMS:
        for c in m4[m]["curve"]:
            crows.append([m, f'{c["threshold"]:.2f}', c["pool"], c["excluded"],
                          c["acted"], pct(c["coverage"]), c["n_errors"],
                          pct(c["error_rate_of_acted"]),
                          c["n_errors_false_confidence"],
                          c["n_errors_wrong_label"]])
    w("T5-coverage-error.md",
      "# T5 — Coverage vs error at the four fixed thresholds\n\n"
      "Thresholds 0.70 / 0.80 / 0.90 / 0.95 are fixed by `README.md`, not tuned "
      "on this data. An **act** = a cell whose confidence reaches the threshold. "
      "An **error** among the acted cells = a wrong label on an answerable case, "
      "or any label at all on an unanswerable case.\n\n"
      "`pool` = cells with a usable label AND a confidence; `excluded` = cells "
      "that can never be acted on (no label, or no confidence at all).\n\n"
      "## T5a — what each mechanism's confidence actually is\n\n"
      + md_table(["mechanism", "what the confidence is"],
                 [[m, m4[m]["confidence_note"]] for m in MECHANISMS]) + "\n\n"
      "## T5b — the curve\n\n"
      + md_table(["mechanism", "threshold", "pool", "excluded", "acted",
                  "coverage", "errors", "error rate of acted",
                  "of which false-confidence", "of which wrong label"],
                 crows) + "\n\n"
      "## T5c — Jev coverage under each confidence convention\n\n"
      "This is the sensitivity that governs the whole escalation story. Jev "
      "publishes **no confidence field for `noul` questions**, and 50 of the 64 "
      "cases are `noul`.\n\n"
      + md_table(["convention", "pool", "thr 0.70", "thr 0.80", "thr 0.90",
                  "thr 0.95"],
                 [[src,
                   m4b[src]["n_pool"]]
                  + [f'{pct(c["coverage"])} / {c["n_errors"]} err'
                     for c in m4b[src]["curve"]]
                  for src in ("reported", "derived")]) + "\n\n"
      + md_table(["question type", "cells", "with API-reported confidence"],
                 [[t, d["n_cells"], d["n_with_reported_confidence"]]
                  for t, d in m9["jev_by_question_type"].items()]) + "\n\n"
      "> " + m4b["_reading"] + "\n\n"
      "> The mixed headcount of `general_model` is 63 not 64: one cell "
      "(`b-i03`) is a `empty_content` transport failure and has no label. "
      "Its coverage is flat across all four thresholds because its hard one-hot "
      "decode always yields a derived confidence of exactly 1.0.\n")

    # ---- T6 error budgets ------------------------------------------------
    brows = [[m, f'{b["budget"]:.0%}', b["max_errors_exact"],
              b["max_errors_floor"], "yes" if b["discrete"] else "no",
              "yes" if b["achievable"] else "**no**",
              f'{b["threshold"]:.2f}' if b["achievable"] else "—",
              pct(b["coverage"]) if b["achievable"] else "—",
              b["n_errors"] if b["achievable"] else
              f'min {b["min_errors_any_threshold"]}']
             for m in MECHANISMS for b in m5[m]["budgets"]]
    w("T6-error-budgets.md",
      "# T6 — Coverage reachable under 1% / 5% / 10% error budgets\n\n"
      "A budget of B% over 64 cells allows `floor(B*n)` errors. **At n=64 a 1% "
      "budget is 0.64 errors, so the floor is 0 — a 1% budget means ZERO "
      "errors.** That discreteness is not a detail; it is the whole reason the "
      "1% row is so stark.\n\n"
      + md_table(["mechanism", "budget", "max errors (exact)", "max errors (floor)",
                  "discrete", "achievable at a tested threshold", "threshold",
                  "coverage", "errors"], brows) + "\n\n"
      "> Only the four thresholds of T5 are searched. A mechanism could in "
      "principle sit between them, so *not achievable here* means *not achievable "
      "at 0.70/0.80/0.90/0.95* and is not a proof that no threshold works.\n\n"
      "> `general_model` is not achievable at any budget because its confidence "
      "carries no information: a hard one-hot decode gives 1.0 on every cell, "
      "so every threshold selects the same 63 cells and the same 13 errors. Read "
      "this as *the general model emitted no usable confidence*, not as *the "
      "general model is inaccurate* — on answerable cases it was the most "
      "accurate mechanism in the grid (T1).\n")

    # ---- T7 contrastive + controls ---------------------------------------
    prows = []
    for m in MECHANISMS:
        p = m6["pairs"][m]
        v = p["confidence_verdicts"]
        prows.append([m, p["n_pairs"],
                      f'{p["n_distinguished"]}/{p["n_pairs"]}',
                      pct(frac(p["n_distinguished"], p["n_pairs"])),
                      f'{p["n_both_correct"]}/{p["n_pairs"]}',
                      p["n_one_correct"], p["n_neither_correct"],
                      v.get("correct_order", 0), v.get("inverted", 0),
                      v.get("tied", 0), v.get("unmeasurable", 0)])
    crows = []
    for m in MECHANISMS:
        for kind, d in m6["controls"][m].items():
            crows.append([m, kind, d["n"],
                          f'{d["n_label_stable"]}/{d["n"]}',
                          pct(frac(d["n_label_stable"], d["n"])),
                          d["n_correct"], d["n_answered_unanswerable"],
                          d["mean_delta_confidence"],
                          d["min_delta_confidence"],
                          d["max_delta_confidence"]])
    # Controls that are supposed to be inert, and are not.
    INERT = ("irrelevant_change", "distractor", "noise", "opaque_labels",
             "option_reorder")
    findings = []
    for m in MECHANISMS:
        for kind, d in m6["controls"][m].items():
            for v in d["variants"]:
                dc = v["delta_confidence"]
                if kind in INERT and v["label_stable"] and dc is not None \
                        and abs(dc) >= 0.05:
                    findings.append(
                        [m, kind, v["case_id"], v["base_case_id"],
                         v["pred_base"], v["pred_variant"], dc,
                         "supposed to be inert: label held, confidence moved"])
                if kind == "missing_evidence":
                    if not v["answered_unanswerable"]:
                        verdict = "ABSTAINED (no label emitted)"
                    elif dc is None:
                        verdict = "answered, confidence unavailable"
                    elif dc > 0:
                        verdict = "evidence removed, confidence ROSE, still answered"
                    elif dc < 0:
                        verdict = "evidence removed, confidence fell, still answered"
                    else:
                        verdict = "evidence removed, confidence flat, still answered"
                    findings.append(
                        [m, kind, v["case_id"], v["base_case_id"],
                         v["pred_base"], v["pred_variant"], dc, verdict])

    n_abstained = sum(1 for m in MECHANISMS
                      for d in m6["controls"][m].get("missing_evidence", {})
                      .get("variants", [])
                      if not d["answered_unanswerable"])

    # The grid-wide abstention picture, over every unanswerable cell rather than
    # just the missing_evidence controls. A cell that emitted no label because
    # the transport failed is counted separately: that is a missing answer, not
    # a judgement that the question could not be answered.
    un_cells = sum(m1["overall"][m]["n_unanswerable"] for m in MECHANISMS)
    answered = sum(m1["overall"][m]["n_answered_unanswerable"]
                   for m in MECHANISMS)
    no_label = sum(m1["overall"][m]["n_unanswerable_no_label"]
                   for m in MECHANISMS)
    flag_set = sum(m1["overall"][m]["n_abstained_flag"] for m in MECHANISMS)
    total_cells = sum(m1["overall"][m]["n_cells"] for m in MECHANISMS)

    w("T7-contrastive-and-controls.md",
      "# T7 — Contrastive pairs and adversarial controls\n\n"
      "## T7a — contrastive pairs (six families, each differing only in the "
      "deciding fact)\n\n"
      "`distinguished` = the two members of the pair got different labels. "
      "`both correct` = the mechanism got both. The confidence verdict asks "
      "whether the confidence signal ranked the members the way the truth does, "
      "and only on pairs where the mechanism got exactly one right: "
      "**correct order** = the right member carries the higher confidence; "
      "**inverted** = the wrong member does; **tied** = identical confidence, "
      "so no ranking is expressed at all; **n/a** = confidence missing, or both "
      "/ neither correct so there is no ranking to check.\n\n"
      + md_table(["mechanism", "pairs", "distinguished", "rate", "both correct",
                  "one correct", "neither", "conf correct order",
                  "conf inverted", "conf tied", "conf n/a"], prows) + "\n\n"
      "## T7b — per-control behaviour, each control against its own base\n\n"
      "`label stable` = the control did not change the label. "
      "`mean/min/max d(conf)` = the shift in the confidence the mechanism "
      "reports, control minus base. A control that is *supposed* to be inert "
      "(`irrelevant_change`) but moves the confidence is a finding; "
      "`missing_evidence` is *supposed* to move it, and a control where it does "
      "not is also a finding.\n\n"
      + md_table(["mechanism", "control", "n", "label stable", "rate",
                  "correct", "answered unanswerable", "mean d(conf)",
                  "min d(conf)", "max d(conf)"], crows) + "\n\n"
      "## T7c — controls that did not behave\n\n"
      "Selected from the data, not written by hand. Two filters: a control that "
      "is *supposed* to be inert but moved the confidence by 0.05 or more while "
      "holding the label; and **every** `missing_evidence` cell, in either "
      "direction.\n\n"
      f"Grid-wide abstention picture: the corpus contains {un_cells} "
      f"unanswerable cells (14 unanswerable cases x 5 mechanisms). "
      f"**{answered} of them received a label**, and **{flag_set} of "
      f"{total_cells} cells set the `abstained` flag**. The {no_label} cell(s) "
      "that emitted no label did so because the transport failed, not because "
      "the mechanism judged the question unanswerable: that is a missing "
      "answer, not an abstention. No mechanism in this grid recognised that a "
      "deciding fact had been removed. Where the confidence rose after the "
      "evidence was removed, the confidence is not tracking evidential support "
      "at all.\n\n"
      + (md_table(["mechanism", "control", "variant", "base", "pred base",
                   "pred variant", "d(conf)", "what happened"], findings)
         if findings else "None: no control moved its confidence by 0.05 or "
                          "more while holding the label.") + "\n")

    # ---- T8 order consistency --------------------------------------------
    orows = []
    for m in MECHANISMS:
        p = m7["perturbation"].get(m)
        if p:
            orows.append([m, p["n"], f'{p["n_label_stable"]}/{p["n"]}',
                          pct(frac(p["n_label_stable"], p["n"])),
                          f'{p["n_both_correct"]}/{p["n"]}'])
    prows = []
    for m in MECHANISMS:
        d = m7["position_bias"].get(m)
        if d:
            prows.append([m, d["n_answered"], d["n_options"],
                          pct(d["uniform_share"]),
                          d["predicted_position_histogram"],
                          d["expected_position_histogram"],
                          f'{d["n_pred_matches_expected_position"]}'
                          f'/{d["n_answered"]}',
                          d["chi2_vs_expected_histogram"]["chi2"],
                          d["chi2_vs_expected_histogram"]["df"]])
    w("T8-option-order-consistency.md",
      "# T8 — Option-order and opaque-label robustness, plus position bias\n\n"
      "## T8a — does renaming or reordering the options change the answer?\n\n"
      "`opaque_labels` renames the option keys to content-free tokens (the label "
      "*text* is unchanged); `option_reorder` presents the same options in a "
      "different order.\n\n"
      + md_table(["mechanism", "controls", "label stable", "rate",
                  "base and variant both correct"], orows) + "\n\n"
      "## T8b — option-position bias (area D, 6 options, uniform = 16.7%)\n\n"
      "A mechanism that always picked the same slot would put every cell in one "
      "histogram bucket. `chi2` is the descriptive distance from the "
      "expected-position histogram; **no p-value is reported** (n=12).\n\n"
      + md_table(["mechanism", "answered", "options", "uniform share",
                  "predicted position histogram",
                  "expected position histogram", "pred == expected position",
                  "chi2", "df"], prows) + "\n\n"
      "> " + m7["_note"] + "\n")

    # ---- T9 routing -------------------------------------------------------
    rrows = [[m, m8[m]["n_cases"], m8[m]["n_usable"],
              f'{m8[m]["n_legal"]}/{m8[m]["n_usable"]}',
              pct(frac(m8[m]["n_legal"], m8[m]["n_usable"])),
              m8[m]["n_illegal"],
              f'{m8[m]["n_expected"]}/{m8[m]["n_usable"]}',
              m8[m]["n_recompute_mismatch"]]
             for m in MECHANISMS]
    w("T9-routing-legality.md",
      "# T9 — Routing legality (area D)\n\n"
      "Legality is deterministic and computed from `routing.signals` **before "
      "any model sees a case**. `n_recompute_mismatch` is the scorer "
      "independently recomputing the stored block and comparing — it must be 0 "
      "for every mechanism.\n\n"
      + md_table(["mechanism", "cases", "usable", "legal", "legal rate",
                  "illegal picks", "picked expected role", "recompute mismatch"],
                 rrows) + "\n\n"
      "## T9a — Jev, case by case\n\n"
      + md_table(["case", "expected role", "legal roles", "predicted role",
                  "legal?", "correct?", "confidence", "source"],
                 [[c["case_id"], c["expected_role"], ", ".join(c["legal_roles"]),
                   str(c["pred_role"]), c["is_legal"], c["correct"],
                   c["confidence"], c["confidence_source"]]
                  for c in m8["jev"]["per_case"]]) + "\n\n"
      "> " + m8["_definition"] + "\n")

    # ---- T10 confidence formula ------------------------------------------
    frows = []
    for m in MECHANISMS:
        d = m9[m]
        if not d.get("testable"):
            frows.append([m, f'{d["testable"]}/{d["n_cells"]}', "—", "—", "—",
                          "—", "—", d["verdict"]])
            continue
        a, b = d["hypothesis_A_formula"], d["hypothesis_B_max_prob"]
        frows.append([m, f'{d["testable"]}/{d["n_cells"]}',
                      d["label_space_sizes"],
                      f'{a["mean_abs_error"]} / max {a["max_abs_error"]}',
                      f'{a["n_within_0.01"]}/{d["testable"]}',
                      f'{a["n_exact_at_2dp"]}/{d["testable"]}',
                      f'{b["mean_abs_error"]} / max {b["max_abs_error"]}',
                      "A better" if d["A_strictly_better_than_B"] else "tie"])
    w("T10-confidence-formula.md",
      "# T10 — Empirical test of the documented confidence derivation\n\n"
      "Claim under test (`README.md`): `confidence = (n*max(p) - 1) / (n - 1)`. "
      "Competing hypothesis: `confidence = max(p)`. The published confidence is "
      "demonstrably **not** `max(p)` (preflight P3a: 0.13 vs 0.27), so the "
      "distinction is load-bearing for every threshold sweep.\n\n"
      + md_table(["mechanism", "testable cells", "label-space sizes",
                  "A: mean / max abs error", "A within 0.01",
                  "A exact at 2dp", "B: mean / max abs error", "verdict"],
                 frows) + "\n\n"
      "## T10a — stored derived confidence rechecked against a fresh "
      "recomputation\n\n"
      + md_table(["mechanism", "rows checked", "mismatches"],
                 [[m, m9["stored_formula_recheck"][m]["n_checked"],
                   m9["stored_formula_recheck"][m]["n_mismatch"]]
                  for m in MECHANISMS]) + "\n\n"
      + md_table(["question type", "cells", "with API-reported confidence"],
                 [[t, d["n_cells"], d["n_with_reported_confidence"]]
                  for t, d in m9["jev_by_question_type"].items()]) + "\n\n"
      "> " + m9["_definition"] + "\n")

    # ---- T11 cost (flagged non-scoring) ----------------------------------
    crows = [[m, m10[m]["n_cells"], m10[m]["latency_ms_min"],
              m10[m]["latency_ms_median"], m10[m]["latency_ms_max"],
              m10[m]["total_input_tokens"], m10[m]["total_output_tokens"],
              m10[m]["total_retries"],
              ", ".join(f"{k}={v}" for k, v in m10[m]["typed_errors"].items()),
              ", ".join(m10[m]["endpoints"]) or "none (offline)"]
             for m in MECHANISMS]
    w("T11-cost-reliability.md",
      "# T11 — Cost and reliability\n\n"
      "> **This table is not a scoring input.** Latency, tokens, retries, "
      "timestamps and HTTP status are recorded for cost and reliability "
      "analysis only (`schema.md` 3.4). No threshold, ranking or verdict in "
      "any other table depends on a number in this one.\n\n"
      + md_table(["mechanism", "cells", "latency min ms", "median", "max",
                  "input tokens", "output tokens", "retries", "typed errors",
                  "endpoint"], crows) + "\n")

    # ---- INDEX -----------------------------------------------------------
    w("INDEX.md",
      "# Tables index — Jev Phase 1\n\n"
      f"Every table is generated by `harness/score.py` {SCORER_VERSION} from "
      "`results/scored.ndjson` and `results/metrics.json`. Regenerate with "
      "`python3 harness/score.py`; never edit a table by hand.\n\n"
      + md_table(["table", "what it answers", "issue brief item"],
                 [["`T1-accuracy-overall.md`",
                   "Is it right, and does it stay quiet when it should not?", "A, B"],
                  ["`T2-accuracy-by-area.md`",
                   "Where does each mechanism work, area by area?", "A, B, C, D"],
                  ["`T3-incremental-gain.md`",
                   "Does the next mechanism beat the cheaper one?", "A"],
                  ["`T4-brier.md`",
                   "How sharp are the distributions?", "B"],
                  ["`T5-coverage-error.md`",
                   "Coverage vs error at 0.70/0.80/0.90/0.95, and how much of "
                   "it rests on a derived confidence", "B"],
                  ["`T6-error-budgets.md`",
                   "Coverage reachable at 1/5/10% error", "B"],
                  ["`T7-contrastive-and-controls.md`",
                   "Does the deciding fact drive the answer, and are the "
                   "controls inert?", "C"],
                  ["`T8-option-order-consistency.md`",
                   "Order/rename robustness and option-position bias",
                   "adversarial controls"],
                  ["`T9-routing-legality.md`",
                   "Does it pick a legal role, and does the recomputation agree?",
                   "D"],
                  ["`T10-confidence-formula.md`",
                   "Is confidence (n*max(p)-1)/(n-1)?", "interface fact"],
                  ["`T11-cost-reliability.md`",
                   "What did it cost, and what failed? (NOT a scoring input)",
                   "reliability"]])
      + "\n\n## Standing caveats\n\n"
      "- n=64 synthetic cases. No significance test is claimed anywhere.\n"
      "- The `rule` and `lexical` cue lexicons were hand-authored with the "
      "corpus vocabulary in view: they are hand-built baselines, and their "
      "accuracy is an upper bound on a generic cue engine.\n"
      "- `rule` on area D evaluates the same policy that defines the expected "
      "role, so its 12/12 is tautological.\n"
      "- Jev reports no confidence for `noul` questions, which is 50 of 64 "
      "cases; escalation coverage therefore rests on a locally derived value.\n"
      "- `general_model` is hard-decoded, so its confidence is identically 1.0 "
      "and its threshold coverage is an encoding artefact.\n")

    return written


# ---------------------------------------------------------------------------
# manifest
# ---------------------------------------------------------------------------
def build_manifest(phase1, cells, metrics, generated_utc, files_written):
    results_dir = os.path.join(phase1, "results")
    raw = {}
    for key, name in RAW_FILES.items():
        path = os.path.join(results_dir, name)
        raw[name] = {"sha256": sha256_file(path),
                     "bytes": os.path.getsize(path),
                     "n_lines": sum(1 for _ in open(path, encoding="utf-8"))}
    superseded = {}
    for name in SUPERSEDED_FILES:
        path = os.path.join(results_dir, name)
        if not os.path.exists(path):
            continue
        meta = None
        for r in load_ndjson(path):
            if "_meta" in r:
                meta = r["_meta"]
        superseded[name] = {"sha256": sha256_file(path),
                            "bytes": os.path.getsize(path),
                            "reason": "preserved pre-fix run; see the _meta row",
                            "meta": meta}

    err_counts = {m: dict(sorted(collections.Counter(
        str(c["typed_error"]) for c in cells
        if c["mechanism"] == m).items())) for m in MECHANISMS}
    retry_counts = {m: sum(c["retries"] or 0 for c in cells
                           if c["mechanism"] == m) for m in MECHANISMS}
    attempt_counts = {m: max((c["attempt"] or 0) for c in cells
                             if c["mechanism"] == m) for m in MECHANISMS}
    endpoints = sorted({c["endpoint"] for c in cells if c["endpoint"]})

    def endpoints_for(mech):
        return sorted({c["endpoint"] for c in cells
                       if c["mechanism"] == mech and c["endpoint"]})

    def model_ids_for(mech):
        return sorted({c["model_id"] for c in cells
                       if c["mechanism"] == mech and c["model_id"]})

    stamps = sorted(c["timestamp_utc"] for c in cells if c["timestamp_utc"])

    return {
        "schema_version": "jevp1-manifest-1.0",
        "crosslink_issue": 565,
        "git": {"branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                "commit": git("rev-parse", "HEAD"),
                "remote": git("config", "--get", "remote.origin.url")},
        "scoring": {
            "scorer": "harness/score.py",
            "scorer_version": SCORER_VERSION,
            "generated_utc": generated_utc,
            "deterministic": True,
            "determinism_note": (
                "results/scored.ndjson and results/metrics.json are pure "
                "functions of the raw files. The ONLY wall-clock value in any "
                "emitted artefact is scoring.generated_utc here; pin it with "
                "--generated-utc to diff the whole tree."),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "stdlib_only": True,
            "third_party_imports": [],
        },
        "models": {
            "jev": {"model_id": (model_ids_for("jev") or [None])[0],
                    "endpoints_observed": endpoints_for("jev"),
                    "provider": "TypeSafe AI System One via OpenCode Zen",
                    "tier": "Free / Unlimited",
                    "n_cells": sum(1 for c in cells
                                   if c["mechanism"] == "jev")},
            "general_model": {
                "model_id": (model_ids_for("general_model") or [None])[0],
                "catalog_id": "opencode-go/space-bunny-free",
                "endpoints_observed": endpoints_for("general_model"),
                "endpoint_rejected": "https://opencode.ai/zen/go/v1/"
                                     "chat/completions",
                "endpoint_note": "the Go route returns HTTP 403 with this "
                                 "credential (preflight P4a); the same model ID "
                                 "is reachable on the Zen route (P4b). Route "
                                 "change, NOT a model substitution.",
                "temperature": 0, "max_tokens": 256,
                "tier": "Free (0/0 cost fields at dispatch)"},
            "offline_mechanisms": ["prior", "rule", "lexical"],
            "model_ids_per_mechanism": {m: model_ids_for(m)
                                        for m in MECHANISMS},
        },
        "endpoints": endpoints,
        "inputs": {
            "cases.ndjson": {"sha256": sha256_file(
                os.path.join(phase1, "cases.ndjson"))},
            "raw_results": raw,
            "superseded_raw_results": superseded,
        },
        "raw_run_window_utc": {"first_cell": stamps[0] if stamps else None,
                              "last_cell": stamps[-1] if stamps else None},
        "grid": {"n_cases": metrics["_grid"]["n_cases"],
                 "n_mechanisms": metrics["_grid"]["n_mechanisms"],
                 "n_cells": metrics["_grid"]["n_cells"],
                 "cells_complete": metrics["_grid"]["complete"]},
        "error_counts": err_counts,
        "retry_counts": retry_counts,
        "max_attempt_per_mechanism": attempt_counts,
        "outputs": sorted(files_written),
        "secrets": {
            "api_key_env": "OPENCODE_GO_API_KEY",
            "required_for_scoring": False,
            "recorded_anywhere": False,
            "note": "scoring is offline and never reads the key. No "
                    "credential, and no length-bearing substring of one, is "
                    "recorded in any artefact. `secrets_recorded` is false on "
                    "every raw and scored row.",
        },
    }


def secret_scan(paths):
    """Boolean-only check that no credential leaked into an emitted artefact.

    Reads the key from the environment to search for it, and records only
    whether it was found. The value is never printed, logged, or written.
    """
    key = os.environ.get("OPENCODE_GO_API_KEY")
    if not key:
        return {"performed": False, "reason": "key absent from environment"}
    hits = []
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                if key in f.read():
                    hits.append(os.path.basename(p))
    return {"performed": True, "files_scanned": len(paths),
            "hits": len(hits), "hit_files": hits}


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--phase1-dir", default=PHASE1)
    ap.add_argument("--tables-dir", default=None)
    ap.add_argument("--no-tables", action="store_true")
    ap.add_argument("--generated-utc", default=None,
                    help="pin the manifest timestamp for byte-diffing")
    ap.add_argument("--self-check", action="store_true",
                    help="score twice and assert the output is identical")
    args = ap.parse_args()

    phase1 = os.path.abspath(args.phase1_dir)
    results_dir = os.path.join(phase1, "results")
    tables_dir = args.tables_dir or os.path.join(phase1, "tables")

    cases = load_cases(os.path.join(phase1, "cases.ndjson"))
    by_id = {c["id"]: c for c in cases}
    if len(by_id) != len(cases):
        raise SystemExit("FATAL duplicate case ids in cases.ndjson")

    raw_rows = []
    for name in RAW_FILES.values():
        raw_rows += load_ndjson(os.path.join(results_dir, name))

    cells = collections.Counter((r["case_id"], r["mechanism"]) for r in raw_rows)
    expected = {(c["id"], m) for c in cases for m in MECHANISMS}
    missing = expected - set(cells)
    extra = set(cells) - expected
    dupes = [k for k, v in cells.items() if v > 1]
    if missing or extra or dupes:
        raise SystemExit(
            f"FATAL grid incomplete: {len(missing)} missing, {len(extra)} "
            f"unknown, {len(dupes)} duplicated cells. Refusing to score a "
            f"partial grid — fix or re-run the mechanism first.")
    unknown = sorted({r["case_id"] for r in raw_rows} - set(by_id))
    if unknown:
        raise SystemExit(f"FATAL raw rows reference unknown cases: {unknown}")

    scored = [build_cell(by_id[r["case_id"]], r) for r in raw_rows]
    scored.sort(key=lambda c: (MECHANISMS.index(c["mechanism"]), c["case_id"]))

    mism = [c for c in scored if c.get("routing")
            and not c["routing"]["recompute_ok"]]
    if mism:
        raise SystemExit(
            f"FATAL stored routing block disagrees with a fresh recomputation "
            f"from signals on {len(mism)} cells: "
            f"{[c['case_id'] for c in mism][:5]}")
    conf_bad = [c for c in scored if c["confidence_check_ok"] is False]
    if conf_bad:
        raise SystemExit(
            f"FATAL stored confidence_formula disagrees with a fresh "
            f"recomputation on {len(conf_bad)} cells: "
            f"{[c['case_id'] for c in conf_bad][:5]}")

    metrics = compute_all(scored, {c["id"]: c for c in cases})

    scored_text = "".join(
        json.dumps(c, ensure_ascii=False, sort_keys=True,
                   separators=(",", ":")) + "\n" for c in scored)
    metrics_text = json.dumps(metrics, ensure_ascii=False, sort_keys=True,
                              indent=2) + "\n"

    def emit():
        """Write the artefacts and return [(repo-relative path, absolute path)]."""
        written = [("results/scored.ndjson",
                    os.path.join(results_dir, "scored.ndjson")),
                   ("results/metrics.json",
                    os.path.join(results_dir, "metrics.json"))]
        with open(written[0][1], "w", encoding="utf-8", newline="\n") as f:
            f.write(scored_text)
        with open(written[1][1], "w", encoding="utf-8", newline="\n") as f:
            f.write(metrics_text)
        if not args.no_tables:
            for name in write_tables(metrics, tables_dir,
                                     {c["id"]: c for c in cases}):
                written.append((os.path.join("tables", name),
                                os.path.join(tables_dir, name)))
        return written

    written = emit()

    if args.self_check:
        again = [build_cell(by_id[r["case_id"]], r) for r in raw_rows]
        again.sort(key=lambda c: (MECHANISMS.index(c["mechanism"]),
                                  c["case_id"]))
        text2 = "".join(json.dumps(c, ensure_ascii=False, sort_keys=True,
                                   separators=(",", ":")) + "\n"
                        for c in again)
        if text2 != scored_text:
            raise SystemExit("FATAL self-check failed: scoring is not "
                             "deterministic")
        print("self-check: scoring is deterministic (byte-identical)")

    generated_utc = args.generated_utc or datetime.now(
        timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = build_manifest(phase1, scored, metrics, generated_utc,
                              [rel for rel, _ in written])
    manifest["scoring"]["self_check_passed"] = bool(args.self_check)
    manifest["outputs_sha256"] = {rel: sha256_file(abs_)
                                  for rel, abs_ in sorted(written)}
    manifest["secrets"]["scan"] = secret_scan([abs_ for _, abs_ in written])
    manifest["outputs"] = sorted([rel for rel, _ in written]
                                 + ["results/manifest.json"])
    with open(os.path.join(results_dir, "manifest.json"), "w",
              encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(manifest, ensure_ascii=False, sort_keys=True,
                           indent=2) + "\n")

    scan = manifest["secrets"]["scan"]
    routing_bad = sum(metrics["m8_routing"][m]["n_recompute_mismatch"]
                      for m in MECHANISMS)
    conf_bad = sum(metrics["m9_confidence_formula"]["stored_formula_recheck"][m]
                   ["n_mismatch"] for m in MECHANISMS)
    print(f"score.py {SCORER_VERSION}")
    print(f"  grid                       : {metrics['_grid']['n_cases']} cases x "
          f"{metrics['_grid']['n_mechanisms']} mechanisms = "
          f"{metrics['_grid']['n_cells']} cells, complete")
    print(f"  routing recompute mismatches: {routing_bad}")
    print(f"  confidence recheck mismatch : {conf_bad}")
    print(f"  scored.ndjson sha256        : {sha256_text(scored_text)}")
    print(f"  metrics.json sha256         : {sha256_text(metrics_text)}")
    print(f"  secret scan                 : {scan.get('hits', 'n/a')} hits over "
          f"{scan.get('files_scanned', 0)} emitted files (boolean only)")
    print(f"  outputs                     : {len(manifest['outputs'])} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
