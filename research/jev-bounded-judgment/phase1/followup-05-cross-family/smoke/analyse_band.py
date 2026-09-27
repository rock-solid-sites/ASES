#!/usr/bin/env python3
"""Deterministic band analysis for followup-05, from scored.ndjson only.

Reads the frozen scorer's output. Computes exactly the quantities the
pre-registered bands in RECON.md section 6 are defined over:

  - accuracy on the ANSWERABLE cases (n=50) for the arm and for jev
  - paired McNemar cells vs jev: b = arm right & jev wrong,
                                c = jev right & arm wrong
  - typed-error count over the arm's own 64 cells (replaces the lucky 1/64, N6)
  - unusable cells and why

Then assigns the band. No judgement, no smoothing, no pooling across arms.
"""
import argparse
import collections
import json
import os


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def band(errors, n, c):
    """Pre-registered bands. Verbatim from RECON.md section 6."""
    acc = 1.0 - errors / n
    if acc <= 0.90 or c >= 3:
        return "Jev's niche SUPPORTED", acc
    if acc >= 0.96 and c <= 1:
        return "Jev's tier UNSUPPORTED", acc
    return "INCONCLUSIVE", acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scored", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--role", required=True,
                    help="cross_family | transport_control")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cells = load(args.scored)
    arm = [c for c in cells if c["mechanism"] == "general_model"]
    jev = {c["case_id"]: c for c in cells if c["mechanism"] == "jev"}
    assert len(arm) == 64, f"expected 64 arm cells, got {len(arm)}"
    assert len(jev) == 64, f"expected 64 jev cells, got {len(jev)}"

    answerable = [c for c in arm if c["answerable"]]
    n = len(answerable)
    unusable = [c for c in arm if not c["usable"]]
    correct = sum(1 for c in answerable if c["correct"])
    errors = n - correct

    b = c = ties = 0
    for cell in answerable:
        j = jev[cell["case_id"]]
        if j["correct"] is None or cell["correct"] is None:
            continue
        if cell["correct"] and not j["correct"]:
            b += 1
        elif j["correct"] and not cell["correct"]:
            c += 1
        else:
            ties += 1

    verdict, acc = band(errors, n, c)

    err_by_type = collections.Counter(
        (cell.get("typed_error") or cell.get("unusable_reason") or "?")
        for cell in unusable)
    per_area = {}
    for cell in answerable:
        a = cell["area"]
        d = per_area.setdefault(a, {"n": 0, "correct": 0})
        d["n"] += 1
        d["correct"] += 1 if cell["correct"] else 0
    for a, d in per_area.items():
        d["errors"] = d["n"] - d["correct"]
        d["accuracy"] = round(d["correct"] / d["n"], 4) if d["n"] else None

    walls = []
    result = {
        "label": args.label,
        "role": args.role,
        "arm_model_id": arm[0].get("model_id"),
        "route": arm[0].get("endpoint"),
        "n_cells": len(arm),
        "n_answerable": n,
        "n_correct": correct,
        "n_errors": errors,
        "accuracy_answerable": round(acc, 4),
        "mcnemar_vs_jev": {"b_arm_right_jev_wrong": b,
                           "c_jev_right_arm_wrong": c, "ties": ties},
        "n_unusable": len(unusable),
        "unusable_by_reason": dict(err_by_type),
        "per_area": per_area,
        "band_verdict": verdict,
        "band_basis": "RECON.md section 6 pre-registered bands, verbatim",
    }
    if walls:
        result["chunk_wall_s"] = walls
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1)
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
