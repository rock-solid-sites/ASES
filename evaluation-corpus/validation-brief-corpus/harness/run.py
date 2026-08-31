#!/usr/bin/env python3
"""
run.py — Thin runner for validation-brief-corpus (issue #530).

This runner is intentionally thin: it ingests corpus.jsonl and emits
results.jsonl with per-brief pass/fail per criterion. It does NOT implement
the EDASES methodology — the methodology lives in the system under test (SUT).

Two modes:
  1. --corpus + --out : ingest corpus, emit stub results (not_run) for each brief.
     A real SUT replaces the TODO block with actual calls.
  2. --compare A B --out delta.md : compare two results.jsonl and emit a markdown delta table.

Usage:
  python harness/run.py --corpus ../corpus.jsonl --out /tmp/results.jsonl
  python harness/run.py --compare /tmp/run-a.jsonl /tmp/run-b.jsonl --out /tmp/delta.md
"""

import argparse
import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

def emit_stub_results(corpus_path: Path, out_path: Path):
    records = []
    for line in corpus_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        bid = rec["id"]
        kind = rec["kind"]
        # Stub: mark every brief as not_run; a real SUT would replace this block
        # with actual execution and per-criterion grading (see scoring.md).
        if kind == "well-formed":
            criteria = ["AC1", "AC2", "AC3", "AC4"]
            max_points = 8
        else:
            criteria = ["detection", "recovery"]
            max_points = 4
        result = {
            "id": bid,
            "kind": kind,
            "status": "not_run",
            "criteria": {c: "not_run" for c in criteria},
            "points": None,
            "max_points": max_points,
            "note": "TODO: SUT integration — replace stub with actual execution and grading per scoring.md"
        }
        records.append(result)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    print(f"Wrote {len(records)} stub results to {out_path}")
    print("NOTE: These are stubs (not_run). Integrate your SUT at the TODO in run.py to emit real points.")

def compare_results(a_path: Path, b_path: Path, out_path: Path, manifest_path: Path = None):
    def load(p: Path):
        d = {}
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            d[r["id"]] = r
        return d

    a = load(a_path)
    b = load(b_path)

    # Try to load manifest for class grouping
    classes = {}
    if manifest_path and manifest_path.exists():
        m = json.loads(manifest_path.read_text(encoding="utf-8"))
        for e in m["briefs"]:
            classes[e["id"]] = e.get("class") or e.get("kind")

    # Per-class aggregates
    per_class = defaultdict(lambda: {"a_points": 0, "a_max": 0, "b_points": 0, "b_max": 0, "count": 0})
    total_a = total_b = total_max = 0

    all_ids = sorted(set(a) | set(b))
    for bid in all_ids:
        ra = a.get(bid, {})
        rb = b.get(bid, {})
        # Use 0 if not_run / missing
        pa = ra.get("points") if isinstance(ra.get("points"), int) else 0
        pb = rb.get("points") if isinstance(rb.get("points"), int) else 0
        mx = ra.get("max_points") or rb.get("max_points") or 0
        cls = classes.get(bid, "unknown")
        per_class[cls]["a_points"] += pa
        per_class[cls]["b_points"] += pb
        per_class[cls]["a_max"] += mx
        per_class[cls]["b_max"] += mx
        per_class[cls]["count"] += 1
        total_a += pa
        total_b += pb
        total_max += mx

    # Emit markdown
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        f.write("# Delta — Validation Brief Corpus Comparison\n\n")
        f.write(f"Run A: `{a_path}` ({len(a)} briefs)\n")
        f.write(f"Run B: `{b_path}` ({len(b)} briefs)\n\n")
        f.write("| Class | A | B | Δ | Δ% | n |\n")
        f.write("|-------|---|---|---|----|---|\n")
        for cls in sorted(per_class):
            d = per_class[cls]
            delta = d["b_points"] - d["a_points"]
            pct = (delta / d["a_max"] * 100) if d["a_max"] else 0
            f.write(f"| {cls} | {d['a_points']}/{d['a_max']} | {d['b_points']}/{d['b_max']} | {delta:+d} | {pct:+.1f}% | {d['count']} |\n")
        total_delta = total_b - total_a
        total_pct = (total_delta / total_max * 100) if total_max else 0
        f.write(f"| **total** | **{total_a}/{total_max}** | **{total_b}/{total_max}** | **{total_delta:+d}** | **{total_pct:+.1f}%** | **{len(all_ids)}** |\n")
        f.write("\n")
        f.write("> Interpretation: per-class Δ shows where enforcement diverged. See harness/scoring.md for thresholds.\n")

    print(f"Wrote delta to {out_path}")
    print(out_path.read_text(encoding="utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, help="Path to corpus.jsonl")
    ap.add_argument("--out", type=Path, required=True, help="Output path (results.jsonl or delta.md)")
    ap.add_argument("--compare", nargs=2, type=Path, metavar=("A", "B"), help="Compare two results.jsonl files")
    ap.add_argument("--manifest", type=Path, default=None, help="Path to manifest.json (for class grouping in --compare)")
    args = ap.parse_args()

    if args.compare:
        a, b = args.compare
        manifest = args.manifest
        if not manifest:
            # Try to infer manifest location from corpus default
            # harness/run.py is at evaluation-corpus/validation-brief-corpus/harness/run.py
            # manifest is at ../manifest.json
            default_manifest = Path(__file__).parent.parent / "manifest.json"
            if default_manifest.exists():
                manifest = default_manifest
        compare_results(a, b, args.out, manifest)
    elif args.corpus:
        if not args.corpus.exists():
            # Try resolving relative to corpus root
            print(f"Corpus not found: {args.corpus}", file=sys.stderr)
            sys.exit(1)
        emit_stub_results(args.corpus, args.out)
    else:
        ap.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
