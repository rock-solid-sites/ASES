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
            "cost_usd_total": round(cost, 8) if cost is not None else None,
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
    args = ap.parse_args()

    rows = []
    for p in args.raw:
        rows += load_ndjson(p)

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

    # split paired comparisons by classification -- the decisive cut
    cls_pairs = []
    for cls in ("lookup", "judgment"):
        a = [r for r in by_cond.get("raw", []) if r["classification"] == cls]
        b = [r for r in by_cond.get("struct", []) if r["classification"] == cls]
        p = paired(a, b, "raw", "struct")
        if p["n_shared_admissible"]:
            p["classification"] = cls
            cls_pairs.append(p)
    metrics["paired_by_classification"] = cls_pairs

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
    print("\nby classification (raw vs struct):")
    for p in metrics["paired_by_classification"]:
        print(f"  [{p['classification']:8s}] n={p['n_shared_admissible']:3d} "
              f"raw_acc={p['acc_a']} struct_acc={p['acc_b']} "
              f"only_raw={p['only_raw_correct']} only_struct={p['only_struct_correct']}")
    print(f"\nmetrics -> {mp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
