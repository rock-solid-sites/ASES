#!/usr/bin/env python3
"""Phase 2 deterministic scorer. Reads raw result rows; writes scored rows,
metrics, and the comparison tables.

Reports results SPLIT BY CLASSIFICATION (lookup vs judgment). This is the single
most important property of the analysis: structure can turn a judgment into a
lookup, and a lookup is not a judgment. A gain concentrated in `lookup` cases is
evidence that structure removed the need to judge, NOT that structure improved
judging, and the split makes that visible instead of hiding it in an aggregate.

Unanswerable cells are never counted as errors. They are reported separately as
behaviour observations only.
"""
import argparse
import json
import os
import statistics
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE2 = os.path.dirname(HERE)

# jev-1.13.0 tariff as recorded in followup-04 (TypeSafe docs fetched
# 2026-09-26): USD per 1M input tokens, output free. Recorded, not assumed;
# a tariff change would change the cost column and nothing else.
COST_PER_MTOK_INPUT = 0.042
COST_TARIFF_SOURCE = ("followup-04-jev-direct/README.md, TypeSafe docs "
                      "models.md fetched 2026-09-26")

# Analysis failure threshold for the cost/token consistency check. Pricing is a
# fixed linear function of input tokens, so the cost ratio between two
# conditions MUST equal the input-token ratio between the same two conditions
# over the same cell set. Any disagreement beyond this tolerance means the two
# numbers were computed over different denominators or different cell sets, and
# is an analysis failure rather than a rounding artefact.
COST_TOKEN_RTOL = 1e-6
# Absolute tolerance for the per-condition identity cost == tokens * rate.
# Cost is stored rounded to 10 decimal places, so 5e-11 is the rounding bound;
# 1e-9 leaves headroom while remaining ~7 orders of magnitude tighter than the
# ~9% divergence a real denominator mismatch produces.
COST_IDENTITY_ATOL = 1e-9


class AnalysisFailure(RuntimeError):
    """Raised when reported statistics are mutually inconsistent."""


def load_ndjson(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def pct(xs, q):
    if not xs:
        return None
    xs = sorted(xs)
    if len(xs) == 1:
        return xs[0]
    k = (len(xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def case_group(case):
    """Intrinsic group for a case, independent of which condition is shown.

    The per-condition `classification` is deliberately condition-relative -- a
    direct_call case genuinely IS a lookup under struct and a judgment under raw
    -- so pairing on it would silently drop every converted case, which is
    exactly the comparison that matters. Grouping is therefore done on the
    case's intrinsic shape:

      lookup_under_struct  the case is a field lookup once structure is shown
                          (structure may have converted a judgment to a lookup)
      judgment_under_both  requires composition under BOTH representations
      raw_only             not answerable from structure at all
    """
    cl = case.get("classification", {})
    s, r = cl.get("struct"), cl.get("raw")
    if s == "lookup":
        return "lookup_under_struct"
    if r == "unanswerable" or s == "unanswerable":
        return "raw_only"
    return "judgment_under_both"




def matched_set(rows, conditions):
    """Case ids admissible AND answered in EVERY listed condition.

    This is the only legitimate basis for comparing aggregate cost or token
    totals across conditions, because it guarantees an identical cell set.
    """
    sets = []
    for cond in conditions:
        sets.append({r["case_id"] for r in rows
                     if r["condition"] == cond and r["admissible"]
                     and r["parsed"]})
    if not sets:
        return set()
    inter = set.intersection(*sets)
    return inter


def efficiency_over_matched_set(rows, conditions):
    """Per-case and total efficiency over an explicitly identical cell set."""
    ids = matched_set(rows, conditions)
    out = {"conditions": list(conditions), "n_matched_cases": len(ids),
           "case_ids_sha_note": "explicitly identical cell set across conditions"}
    per = {}
    for cond in conditions:
        sel = [r for r in rows if r["case_id"] in ids and r["condition"] == cond]
        tok = sum((r.get("usage") or {}).get("input_tokens", 0) for r in sel)
        sb = sum(r["representation"]["state_bytes"] for r in sel)
        cost = tok / 1_000_000.0 * COST_PER_MTOK_INPUT
        per[cond] = {
            "n_cells": len(sel),
            "input_tokens_total": tok,
            "input_tokens_per_case": round(tok / len(sel), 4) if sel else None,
            "state_bytes_total": sb,
            "state_bytes_per_case": round(sb / len(sel), 2) if sel else None,
            "cost_usd_total": round(cost, 10),
            "cost_usd_per_case": round(cost / len(sel), 12) if sel else None,
        }
    out["per_condition"] = per
    if len(conditions) == 2:
        a, b = conditions
        ta = per[a]["input_tokens_per_case"]
        tb = per[b]["input_tokens_per_case"]
        ca = per[a]["cost_usd_per_case"]
        cb = per[b]["cost_usd_per_case"]
        out["token_ratio_a_over_b"] = round(ta / tb, 6) if ta and tb else None
        out["cost_ratio_a_over_b"] = round(ca / cb, 6) if ca and cb else None
    return out


def assert_cost_token_consistency(rows, conditions, label="", reported=None):
    """Verify a REPORTED cost ratio against a freshly computed token ratio.

    The first version of this check was VACUOUS: it derived cost from the same
    token sum it then compared against, so the two ratios were identical by
    construction and could never disagree. A negative test caught that. This
    version is non-vacuous because the two sides are computed from different
    places:

      * the reported side comes from the document / metrics under test
      * the fresh side is recomputed from the raw records

    Two failure modes are checked:

    1. PER-CONDITION. A reported cost total must equal its own reported input
       token total times the tariff. Disagreement means the cost figure was
       computed over a different cell set from the token figure.
    2. CROSS-CONDITION. A reported cost ratio must equal the token ratio over
       the MATCHED cell set. Disagreement means the ratio compared unequal
       denominators, which is exactly the retracted 1.63x claim (errata E1).

    Disagreement raises AnalysisFailure.
    """
    rep = efficiency_over_matched_set(rows, conditions)
    a, b = (conditions + [None, None])[:2] if len(conditions) < 2 else conditions[:2]
    tr = rep.get("token_ratio_a_over_b")

    out = {"label": label, "conditions": list(conditions),
           "n_matched_cases": rep["n_matched_cases"],
           "fresh_token_ratio_matched": tr,
           "checks": []}

    # 1. per-condition: reported cost == reported tokens * rate
    if reported:
        for cond in conditions:
            rc = (reported.get("by_condition", {}).get(cond) or {})
            ct, ctok = rc.get("cost_usd_total"), rc.get("input_tokens_total")
            if ct is not None and ctok is not None:
                expect = ctok / 1_000_000.0 * COST_PER_MTOK_INPUT
                ok = abs(ct - expect) <= COST_IDENTITY_ATOL
                out["checks"].append({
                    "check": "reported_cost_equals_reported_tokens_times_rate",
                    "condition": cond, "reported_cost": ct,
                    "reported_tokens": ctok, "expected_cost": expect,
                    "ok": ok})
                if not ok:
                    raise AnalysisFailure(
                        f"{label}: reported cost {ct} for {cond} does not equal "
                        f"its own reported token total {ctok} x "
                        f"{COST_PER_MTOK_INPUT}/Mtok = {expect}. The cost and "
                        f"token figures were computed over different cell sets. "
                        f"Investigate before reporting.")
        # 2. cross-condition: reported cost ratio == fresh matched token ratio
        rr = reported.get("efficiency_matched_set", {}).get(
            "|".join(conditions[:2]) if len(conditions) == 2 else "", {})
        rcr = rr.get("cost_ratio_a_over_b")
        if rcr is not None and tr is not None:
            ok = abs(rcr - tr) <= COST_TOKEN_RTOL * max(abs(tr), 1.0)
            out["checks"].append({
                "check": "reported_cost_ratio_equals_matched_token_ratio",
                "reported_cost_ratio": rcr, "fresh_matched_token_ratio": tr,
                "ok": ok})
            if not ok:
                raise AnalysisFailure(
                    f"{label}: reported cost ratio {rcr} disagrees with the "
                    f"input-token ratio {tr} recomputed over the matched cell "
                    f"set (n={rep['n_matched_cases']}). Pricing is a fixed "
                    f"linear function of input tokens, so these MUST agree. "
                    f"Disagreement means the reported ratio compared unequal "
                    f"denominators. Investigate before reporting.")
    out["consistent"] = all(c["ok"] for c in out["checks"]) if out["checks"] \
        else None
    return rep, out


def naive_total_ratio(rows, a, b):
    """The WRONG way, computed only so the report can show it being rejected."""
    def tot(cond):
        sel = [r for r in rows if r["condition"] == cond and r["admissible"]]
        tok = sum((r.get("usage") or {}).get("input_tokens", 0) for r in sel)
        return len(sel), tok, tok / 1_000_000.0 * COST_PER_MTOK_INPUT
    na, ta, ca = tot(a)
    nb, tb, cb = tot(b)
    return {"a": a, "b": b, "n_a": na, "n_b": nb,
            "cost_ratio_of_totals": round(ca / cb, 6) if cb else None,
            "token_ratio_of_totals": round(ta / tb, 6) if tb else None,
            "n_equal": na == nb,
            "why_rejected": ("unequal scored-question counts"
                             if na != nb else "n/a (equal n)")}


def summarise(rows, keyfn):
    groups = defaultdict(list)
    for r in rows:
        groups[keyfn(r)].append(r)
    out = {}
    for k, rs in sorted(groups.items(), key=lambda kv: str(kv[0])):
        scored = [r for r in rs if r["admissible"]]
        unusable = [r for r in rs if not r["admissible"]]
        errs = [r for r in rs if r["typed_error"] and r["typed_error"] != "not_admissible"]
        correct = [r for r in scored if r["parsed"] and
                   r["parsed"]["label"] == r["ground_truth"]]
        n = len(scored)
        lat = [r["latency_ms"] for r in scored if r["latency_ms"] is not None]
        in_tok = [(r.get("usage") or {}).get("input_tokens")
                  for r in scored if (r.get("usage") or {}).get("input_tokens")]
        in_tok = [t for t in in_tok if t]
        state_b = [r["representation"]["state_bytes"] for r in scored]
        nouls = [r["parsed"]["noul"] for r in scored if r["parsed"]]
        cost = (sum(in_tok) / 1_000_000.0 * COST_PER_MTOK_INPUT) if in_tok else None
        out[str(k)] = {
            "n_cells": len(rs),
            "n_admissible": n,
            "n_unanswerable": len(unusable),
            "n_transport_or_parse_error": len(errs),
            "n_correct": len(correct),
            "accuracy": round(len(correct) / n, 4) if n else None,
            "state_bytes_mean": round(statistics.mean(state_b), 1) if state_b else None,
            "state_bytes_total": sum(state_b),
            "input_tokens_mean": round(statistics.mean(in_tok), 1) if in_tok else None,
            "input_tokens_total": sum(in_tok),
            "cost_usd_total": round(cost, 10) if cost is not None else None,
            "cost_usd_per_case": (round(cost / n, 12)
                                  if cost is not None and n else None),
            "n_scored_questions": n,
            "latency_ms_median": round(statistics.median(lat), 2) if lat else None,
            "latency_ms_p95": round(pct(lat, 0.95), 2) if lat else None,
            "latency_ms_max": round(max(lat), 2) if lat else None,
            "noul_mean": round(statistics.mean(nouls), 4) if nouls else None,
            "noul_min": round(min(nouls), 4) if nouls else None,
            "noul_max": round(max(nouls), 4) if nouls else None,
            "noul_at_0_or_1": sum(1 for v in nouls if v <= 0.0 or v >= 1.0),
            "noul_near_half": sum(1 for v in nouls if 0.4 <= v <= 0.6),
        }
    return out


def paired(a_rows, b_rows, label_a, label_b):
    """McNemar-style paired comparison between two conditions on shared cases."""
    a = {r["case_id"]: r for r in a_rows if r["admissible"] and r["parsed"]}
    b = {r["case_id"]: r for r in b_rows if r["admissible"] and r["parsed"]}
    shared = sorted(set(a) & set(b))
    only_a = only_b = both = neither = 0
    for cid in shared:
        ca = a[cid]["parsed"]["label"] == a[cid]["ground_truth"]
        cb = b[cid]["parsed"]["label"] == b[cid]["ground_truth"]
        if ca and not cb:
            only_a += 1
        elif cb and not ca:
            only_b += 1
        elif ca and cb:
            both += 1
        else:
            neither += 1
    return {
        "comparison": f"{label_a} vs {label_b}",
        "n_shared_admissible": len(shared),
        f"only_{label_a}_correct": only_a,
        f"only_{label_b}_correct": only_b,
        "both_correct": both,
        "neither_correct": neither,
        "acc_a": round((only_a + both) / len(shared), 4) if shared else None,
        "acc_b": round((only_b + both) / len(shared), 4) if shared else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", nargs="+", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--label", default="jev_direct")
    ap.add_argument("--exp1", default=None,
                    help="raw NDJSON for Experiment 1; adds the exp1 summary")
    ap.add_argument("--reported-metrics", default=None,
                    help="a metrics.json to verify the reported cost figures "
                         "against; enables the non-vacuous consistency check")
    args = ap.parse_args()

    rows = []
    for p in args.raw:
        rows += load_ndjson(p)
    # Intrinsic per-case classification comes from the FROZEN case set, not
    # from the result rows: run_jev.py stores the condition-relative value
    # (a string), which is the thing that must not be used for grouping.
    cases_path = os.path.join(PHASE2, "frozen", "cases.json")
    cls_by_id = {c["case_id"]: c["classification"]
                 for c in json.load(open(cases_path, encoding="utf-8"))}
    for r in rows:
        r["intrinsic_classification"] = cls_by_id.get(r["case_id"], {})
        r["case_group"] = case_group(
            {"classification": r["intrinsic_classification"]})

    os.makedirs(args.outdir, exist_ok=True)
    tables = os.path.join(PHASE2, "tables")
    os.makedirs(tables, exist_ok=True)

    metrics = {
        "label": args.label,
        "n_rows": len(rows),
        "cost_tariff": {"usd_per_1M_input": COST_PER_MTOK_INPUT,
                        "output": "free", "source": COST_TARIFF_SOURCE},
        "by_condition": summarise(rows, lambda r: r["condition"]),
        "by_condition_and_class": summarise(
            rows, lambda r: f'{r["condition"]}|{r["classification"]}'),
        "by_condition_and_ctype": summarise(
            rows, lambda r: f'{r["condition"]}|{r["ctype"]}'),
        "by_module": summarise(
            rows, lambda r: f'{r["condition"]}|{r["module"]}'),
        "typed_errors": dict(Counter(
            str(r["typed_error"]) for r in rows if r["typed_error"])),
        "unanswerable_by_condition": dict(Counter(
            r["condition"] for r in rows if not r["admissible"])),
    }

    by_cond = defaultdict(list)
    for r in rows:
        by_cond[r["condition"]].append(r)
    pairs = [
        paired(by_cond.get("raw", []), by_cond.get("struct", []),
               "raw", "struct"),
        paired(by_cond.get("raw_ic", []), by_cond.get("struct_ic", []),
               "raw_ic", "struct_ic"),
        paired(by_cond.get("raw", []), by_cond.get("raw_ic", []),
               "raw", "raw_ic"),
        paired(by_cond.get("struct", []), by_cond.get("struct_ic", []),
               "struct", "struct_ic"),
    ]
    metrics["paired"] = [p for p in pairs if p["n_shared_admissible"]]

    # split paired comparisons by the case's INTRINSIC group. This is the
    # decisive cut: it keeps the judgment->lookup converted cases visible
    # instead of dropping them, which a condition-relative split would do.
    cls_pairs = []
    groups = sorted({r.get("case_group") for r in rows if r.get("case_group")})
    for grp in groups:
        a = [r for r in by_cond.get("raw", []) if r.get("case_group") == grp]
        b = [r for r in by_cond.get("struct", []) if r.get("case_group") == grp]
        p = paired(a, b, "raw", "struct")
        if p["n_shared_admissible"]:
            p["case_group"] = grp
            cls_pairs.append(p)
    metrics["paired_by_case_group"] = cls_pairs

    # ---- MATCHED-DENOMINATOR EFFICIENCY ---------------------------------
    # Aggregate cost/token totals are only comparable over an IDENTICAL cell
    # set. Every reported efficiency figure below is per-case over a matched
    # set, and the naive unequal-n ratio is recorded solely to show it rejected.
    reported = None
    if args.reported_metrics and os.path.exists(args.reported_metrics):
        reported = json.load(open(args.reported_metrics, encoding="utf-8"))
        print(f"verifying REPORTED aggregates from {args.reported_metrics}")
    matched = {}
    consistency = {}
    for a, b in (("raw", "struct"), ("raw_ic", "struct_ic"),
                 ("raw", "raw_ic"), ("struct", "struct_ic")):
        key = f"{a}|{b}"
        rep, cons = assert_cost_token_consistency(rows, [a, b], label=key,
                                                  reported=reported)
        matched[key] = rep
        if cons and cons.get("checks"):
            consistency[key] = cons
    metrics["efficiency_matched_set"] = matched
    metrics["cost_token_consistency"] = consistency
    metrics["rejected_unequal_n_ratios"] = {
        k: naive_total_ratio(rows, *k.split("|"))
        for k in ("raw|struct", "raw_ic|struct_ic")}
    metrics["efficiency_policy"] = (
        "All comparative efficiency statistics are per-case over an explicitly "
        "identical cell set. Aggregate totals across conditions with different "
        "scored-question counts are NOT comparable and are recorded under "
        "rejected_unequal_n_ratios only to document their rejection. Because "
        "pricing is a fixed linear function of input tokens, the cost ratio and "
        "the input-token ratio must agree over the matched set; disagreement "
        "raises AnalysisFailure.")

    mp = os.path.join(args.outdir, "metrics.json")
    json.dump(metrics, open(mp, "w", encoding="utf-8"), indent=1)

    with open(os.path.join(args.outdir, "scored.ndjson"), "w",
              encoding="utf-8", newline="\n") as fh:
        for r in rows:
            scored = dict(r)
            if r["admissible"] and r["parsed"]:
                scored["correct"] = (r["parsed"]["label"] == r["ground_truth"])
            else:
                scored["correct"] = None
            fh.write(json.dumps(scored, ensure_ascii=False, sort_keys=True)
                     + "\n")

    bc = metrics["by_condition"]
    print(f"rows={len(rows)}  conditions={sorted(bc)}")
    hdr = (f"{'condition':12s} {'n_adm':>5s} {'acc':>7s} {'state_B':>9s} "
           f"{'in_tok':>8s} {'med_ms':>8s} {'p95_ms':>8s} {'cost$':>10s}")
    print(hdr)
    print("-" * len(hdr))
    for c in sorted(bc):
        m = bc[c]
        print(f"{c:12s} {m['n_admissible']:5d} "
              f"{(m['accuracy'] if m['accuracy'] is not None else float('nan')):7.4f} "
              f"{m['state_bytes_mean']:9.0f} {m['input_tokens_mean'] or 0:8.0f} "
              f"{m['latency_ms_median'] or 0:8.1f} {m['latency_ms_p95'] or 0:8.1f} "
              f"{m['cost_usd_total'] or 0:10.6f}")
    print("\npaired raw vs struct, by intrinsic case group:")
    for p in metrics["paired_by_case_group"]:
        print(f"  [{p['case_group']:20s}] n={p['n_shared_admissible']:3d} "
              f"raw_acc={p['acc_a']} struct_acc={p['acc_b']} "
              f"only_raw={p['only_raw_correct']} only_struct={p['only_struct_correct']} "
              f"both={p['both_correct']} neither={p['neither_correct']}")
    print("\npaired (all groups):")
    for p in metrics["paired"]:
        print(f"  {p['comparison']:22s} n={p['n_shared_admissible']:3d} "
              f"a={p['acc_a']} b={p['acc_b']}")
    print("\nefficiency over MATCHED cell sets (per case):")
    for k, rep in metrics["efficiency_matched_set"].items():
        cons = metrics["cost_token_consistency"].get(k, {})
        print(f"  {k:22s} n={rep['n_matched_cases']:3d} "
              f"fresh_matched_token_ratio={cons.get('fresh_token_ratio_matched')} "
              f"checks={len(cons.get('checks') or [])} "
              f"consistent={cons.get('consistent')}")
    rej = metrics["rejected_unequal_n_ratios"]
    print("\nrejected unequal-n aggregate ratios (recorded, not used):")
    for k, v in rej.items():
        print(f"  {k:22s} n {v['n_a']} vs {v['n_b']}  "
              f"cost_ratio={v['cost_ratio_of_totals']}  "
              f"token_ratio={v['token_ratio_of_totals']}  "
              f"rejected: {v['why_rejected']}")
    if args.exp1:
        e1rows = load_ndjson(args.exp1)
        summ = summarise_exp1(e1rows, label="exp1")
        head = exp1_headline(summ)
        summ["headline"] = head
        json.dump(summ, open(os.path.join(args.outdir, "exp1_summary.json"),
                             "w", encoding="utf-8"), indent=1)
        mm = summ["SEPARATE MEASURES"]
        print("\n=== EXPERIMENT 1 ===")
        print(f"  matched cases {summ['n_matched_cases']} "
              f"(answerable {summ['n_matched_answerable']}, "
              f"unanswerable {summ['n_matched_unanswerable']})")
        for arm in ("arm_a_forced", "arm_b_explicit_unknown"):
            ca = mm["correctness_on_answerable"][arm]
            print(f"  {arm:26s} answerable acc {ca['accuracy']} "
                  f"({ca['n_correct']}/{ca['n']})")
        for arm in ("arm_a_forced", "arm_b_explicit_unknown"):
            ud = mm["unknown_detection_on_unanswerable"][arm]
            fu = mm["false_unknown_on_answerable"][arm]
            print(f"  {arm:26s} unknown-detection {ud['rate']}  "
                  f"false-unknown {fu['rate']}")
        print("  arm C best unanswerable abstention: "
              f"{head['best_external_threshold_unanswerable_abstention']} "
              f"at tau={head['best_external_threshold']}")
        print(f"  VERDICT: {head['verdict']}")

    print(f"\nmetrics -> {mp}")
    return 0




# ===========================================================================
# Experiment 1 — explicit unknown vs external probability gating
# ===========================================================================
# Probability, provider confidence, measured calibration, correctness and
# abstention are kept in SEPARATE tables and never combined into a composite.
# Arm C has no requests: it is arm A's own distribution under a threshold, so it
# is free by construction and any A-vs-C difference is attributable to the
# threshold alone.
THRESHOLDS = [round(0.50 + 0.05 * i, 2) for i in range(10)]


def _exp1_cells(rows):
    out = {}
    for r in rows:
        if r.get("typed_error") or not r.get("parsed"):
            continue
        out.setdefault(r["arm"], {})[r["case_id"]] = r
    return out


def summarise_exp1(rows, label="exp1"):
    arms = _exp1_cells(rows)
    a, b = arms.get("arm_a_forced", {}), arms.get("arm_b_explicit_unknown", {})

    # matched cell sets: only cases answered in BOTH arms
    matched = sorted(set(a) & set(b))
    matched_ans = [c for c in matched if a[c]["ground_truth"] is not None]
    matched_unans = [c for c in matched if a[c]["ground_truth"] is None]

    def sel(row):
        return row["parsed"]["selected"]

    def correct(row):
        gt = row["ground_truth"]
        return gt is not None and sel(row) == gt

    out = {
        "label": label,
        "n_matched_cases": len(matched),
        "n_matched_answerable": len(matched_ans),
        "n_matched_unanswerable": len(matched_unans),
        "matched_denominator_policy": (
            "only cases answered in BOTH arms enter any cross-arm comparison; "
            "answerable and unanswerable are reported on their own matched sets "
            "and never pooled"),
        "SEPARATE MEASURES": {},
    }
    m = out["SEPARATE MEASURES"]

    # 1. correctness on answerable (arm A, arm B)
    m["correctness_on_answerable"] = {
        "arm_a_forced": {
            "n": len(matched_ans),
            "n_correct": sum(1 for c in matched_ans if correct(a[c])),
            "accuracy": round(sum(1 for c in matched_ans if correct(a[c]))
                              / len(matched_ans), 4) if matched_ans else None},
        "arm_b_explicit_unknown": {
            "n": len(matched_ans),
            "n_correct": sum(1 for c in matched_ans if correct(b[c])),
            "accuracy": round(sum(1 for c in matched_ans if correct(b[c]))
                              / len(matched_ans), 4) if matched_ans else None,
            "note": "selecting insufficient_evidence on an answerable case is "
                    "WRONG, not partial credit"},
    }

    # 2. explicit-unknown detection on unanswerable
    def insuf(row):
        return sel(row) == "insufficient_evidence"
    m["unknown_detection_on_unanswerable"] = {
        "arm_a_forced": {"n": len(matched_unans),
                         "n_detected": 0, "rate": 0.0,
                         "note": "cannot express abstention; 0 BY CONSTRUCTION"},
        "arm_b_explicit_unknown": {
            "n": len(matched_unans),
            "n_detected": sum(1 for c in matched_unans if insuf(b[c])),
            "rate": round(sum(1 for c in matched_unans if insuf(b[c]))
                          / len(matched_unans), 4) if matched_unans else None},
    }

    # 3. false-unknown rate on answerable
    m["false_unknown_on_answerable"] = {
        "arm_a_forced": {"n": len(matched_ans),
                         "n_false_unknown": 0, "rate": 0.0,
                         "note": "cannot express abstention; 0 BY CONSTRUCTION"},
        "arm_b_explicit_unknown": {
            "n": len(matched_ans),
            "n_false_unknown": sum(1 for c in matched_ans if insuf(b[c])),
            "rate": round(sum(1 for c in matched_ans if insuf(b[c]))
                          / len(matched_ans), 4) if matched_ans else None},
    }

    # 4. false-confidence: emitting a positive label on an unanswerable case
    def confident(row):
        return sel(row) in ("yes", "no")
    m["false_confidence_on_unanswerable"] = {
        arm: {"n": len(matched_unans),
              "n_false_confident": sum(1 for c in matched_unans
                                       if confident(arms[arm][c])),
              "rate": round(sum(1 for c in matched_unans
                                if confident(arms[arm][c]))
                            / len(matched_unans), 4) if matched_unans else None}
        for arm in arms if set(arms[arm]) & set(matched_unans)}

    # 5a. arm C: external threshold over arm A's own distribution
    sweep_c = []
    for t in THRESHOLDS:
        acted_ans = acted_ok = abst_ans = 0
        for c in matched_ans:
            p = a[c]["parsed"]["probabilities"].get(a[c]["ground_truth"], 0.0)
            if p >= t:
                acted_ans += 1
                acted_ok += 1 if sel(a[c]) == a[c]["ground_truth"] else 0
            else:
                abst_ans += 1
        # on unanswerable, abstention requires a LOW probability on either label
        abst_un = sum(1 for c in matched_unans
                      if max(a[c]["parsed"]["probabilities"].get("yes", 0),
                             a[c]["parsed"]["probabilities"].get("no", 0)) < t)
        sweep_c.append({
            "threshold": t,
            "coverage_answerable": round(acted_ans / len(matched_ans), 4)
            if matched_ans else None,
            "accuracy_when_acting": round(acted_ok / acted_ans, 4)
            if acted_ans else None,
            "error_rate_when_acting": round(1 - acted_ok / acted_ans, 4)
            if acted_ans else None,
            "abstain_answerable": abst_ans,
            "abstain_unanswerable": abst_un,
            "unanswerable_abstention_rate": round(abst_un / len(matched_unans), 4)
            if matched_unans else None,
        })
    m["arm_C_external_threshold_sweep"] = {
        "definition": "act iff p(ground-truth option) >= threshold; arm A's own "
                      "requests, no new API calls",
        "sweep": sweep_c}

    # 5b. arm B: the like-for-like operating curve over p(insufficient_evidence)
    sweep_b = []
    for t in THRESHOLDS:
        abst_ans = sum(1 for c in matched_ans
                       if b[c]["parsed"]["probabilities"].get(
                           "insufficient_evidence", 0.0) >= t)
        det_un = sum(1 for c in matched_unans
                     if b[c]["parsed"]["probabilities"].get(
                         "insufficient_evidence", 0.0) >= t)
        acted_ans = len(matched_ans) - abst_ans
        ok_ans = sum(1 for c in matched_ans
                     if b[c]["parsed"]["probabilities"].get(
                         "insufficient_evidence", 0.0) < t
                     and sel(b[c]) == b[c]["ground_truth"])
        sweep_b.append({
            "threshold": t,
            "abstain_answerable": abst_ans,
            "false_unknown_rate": round(abst_ans / len(matched_ans), 4)
            if matched_ans else None,
            "coverage_answerable": round(acted_ans / len(matched_ans), 4)
            if matched_ans else None,
            "accuracy_when_acting": round(ok_ans / acted_ans, 4)
            if acted_ans else None,
            "unknown_detection_rate": round(det_un / len(matched_unans), 4)
            if matched_unans else None,
        })
    m["arm_B_explicit_unknown_sweep"] = {
        "definition": "abstain iff p(insufficient_evidence) >= threshold; the "
                      "like-for-like operating curve against arm C",
        "sweep": sweep_b}

    # 6. probability and provider confidence, reported raw and separate
    for arm, cells_ in arms.items():
        ps = [r["parsed"]["probabilities"] for r in cells_.values()]
        flat = [v for p in ps for v in p.values()]
        conf_diff = [abs((r["parsed"]["provider_confidence"] or 0)
                        - r["parsed"]["derived_confidence"])
                     for r in cells_.values()
                     if r["parsed"].get("provider_confidence") is not None]
        m.setdefault("probability_and_confidence", {})[arm] = {
            "prob_min": round(min(flat), 4) if flat else None,
            "prob_max": round(max(flat), 4) if flat else None,
            "prob_mean": round(sum(flat) / len(flat), 4) if flat else None,
            "n_one_hot_rows": sum(
                1 for p in ps
                if all(v >= 0.999 for v in p.values())) if ps else 0,
            "n_rows": len(ps),
            "provider_confidence_vs_derived_max_abs_diff":
                round(max(conf_diff), 4) if conf_diff else None,
            "note": "provider confidence is a DERIVED function of the "
                    "probability vector (Phase 1 INSTRUMENT-VALIDATION) and is "
                    "not independent evidence",
        }

    # 7. measured calibration, descriptive only, clearly not the provider's claim
    cal = {}
    for arm, cells_ in arms.items():
        buckets = {}
        for c in matched_ans:
            row = cells_[c]
            p = row["parsed"]["probabilities"].get(row["ground_truth"], 0.0)
            hit = sel(row) == row["ground_truth"]
            b_ = min(int(p * 5), 4)
            d = buckets.setdefault(b_, {"n": 0, "hit": 0})
            d["n"] += 1
            d["hit"] += 1 if hit else 0
        cal[arm] = {str(k): {"n": v["n"], "mean_p": None,
                             "observed_rate": round(v["hit"] / v["n"], 4)}
                    for k, v in sorted(buckets.items())}
    m["measured_calibration_descriptive"] = {
        "buckets": cal,
        "claim": "NONE. n is far too small for a reliability claim; this is a "
                 "descriptive binning computed by us, not the provider's, and it "
                 "is not evidence that Jev is calibrated.",
    }
    return out


def exp1_headline(s):
    """The question, answered in one line, with the number that answers it."""
    m = s["SEPARATE MEASURES"]
    best_c = max((r for r in m["arm_C_external_threshold_sweep"]["sweep"]
                  if r["unanswerable_abstention_rate"] is not None),
                 key=lambda r: r["unanswerable_abstention_rate"], default=None)
    det_b = m["unknown_detection_on_unanswerable"]["arm_b_explicit_unknown"]
    return {
        "explicit_unknown_detection_rate": det_b["rate"],
        "false_unknown_rate":
            m["false_unknown_on_answerable"]["arm_b_explicit_unknown"]["rate"],
        "accuracy_answerable_arm_A":
            m["correctness_on_answerable"]["arm_a_forced"]["accuracy"],
        "accuracy_answerable_arm_B":
            m["correctness_on_answerable"]["arm_b_explicit_unknown"]["accuracy"],
        "best_external_threshold_unanswerable_abstention":
            (best_c or {}).get("unanswerable_abstention_rate"),
        "best_external_threshold": (best_c or {}).get("threshold"),
        "verdict": ("explicit unknown detects missing evidence at "
                    f"{det_b['rate']}, while an external probability threshold "
                    f"reaches at most "
                    f"{(best_c or {}).get('unanswerable_abstention_rate')}"),
    }


if __name__ == "__main__":
    raise SystemExit(main())
