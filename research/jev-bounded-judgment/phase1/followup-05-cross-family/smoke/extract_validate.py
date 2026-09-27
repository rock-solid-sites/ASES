#!/usr/bin/env python3
"""Extract and deterministically validate an agent-routed arm's answers.

Reads the raw `opencode run --format json` event stream, pulls the final text
block, parses it as NDJSON, and validates it against the task file.

Validation is strict and mechanical. An arm that fails any check is reported
as failed rather than partially scored -- the Phase-1 rule that a mechanism
either produced a cell or it did not, with no silent repair.

Every surviving `content` string is then pushed through the FROZEN
`parse_general()` from harness/run_baselines.py. That proves the answer text
is acceptable to the existing scorer without modifying it, which is what lets
the frozen `harness/score.py` consume these arms unchanged.

Exit codes: 0 all checks passed · 2 validation failed · 3 parse rejected.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE1 = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(PHASE1, "harness"))

import run_baselines as rb  # noqa: E402


def final_text(path):
    texts = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            if ev.get("type") == "text":
                part = ev.get("part") or {}
                if part.get("type") == "text" and part.get("text"):
                    texts.append(part["text"])
    if not texts:
        return None
    return texts[-1]


def parse_ndjson(text):
    """Tolerant of a stray code fence; strict about the object shape."""
    body = text.strip()
    body = re.sub(r"^```[a-zA-Z]*\s*", "", body)
    body = re.sub(r"\s*```$", "", body)
    rows, bad = [], []
    for ln in body.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            obj = json.loads(ln)
        except Exception:
            bad.append(ln)
            continue
        if isinstance(obj, dict) and "case_id" in obj and "content" in obj:
            rows.append(obj)
        else:
            bad.append(ln)
    return rows, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", required=True)
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--out", required=True, help="validated NDJSON out")
    ap.add_argument("--label", required=True)
    args = ap.parse_args()

    tasks = json.load(open(args.tasks, encoding="utf-8"))
    want = [c["case_id"] for c in tasks["cases"]]
    report = {"label": args.label, "model_id": tasks["model_id"],
              "n_expected": len(want), "checks": {}, "failures": []}

    text = final_text(args.events)
    if text is None:
        report["checks"]["text_block_found"] = False
        report["failures"].append("no text block in event stream")
        print(json.dumps(report, indent=1))
        return 2
    report["checks"]["text_block_found"] = True

    rows, bad = parse_ndjson(text)
    report["n_parsed"] = len(rows)
    report["n_unparsable_lines"] = len(bad)

    got = [r["case_id"] for r in rows]
    report["checks"]["count_matches"] = (len(rows) == len(want))
    report["checks"]["no_duplicates"] = (len(set(got)) == len(got))
    report["checks"]["all_case_ids_present"] = (set(got) == set(want))
    report["missing_case_ids"] = sorted(set(want) - set(got))
    report["unexpected_case_ids"] = sorted(set(got) - set(want))
    if bad:
        report["unparsable_sample"] = bad[:3]

    hard = ("count_matches", "no_duplicates", "all_case_ids_present")
    if not all(report["checks"][c] for c in hard):
        report["checks"]["frozen_parser_accepts"] = False
        print(json.dumps(report, indent=1))
        return 2

    # Push every answer through the frozen scorer parser.
    by_id = {c["case_id"]: c for c in tasks["cases"]}
    corpus = {json.loads(l)["id"]: json.loads(l)
              for l in open(os.path.join(PHASE1, "cases.ndjson"),
                            encoding="utf-8") if l.strip()}
    out_rows, rejected = [], []
    for r in rows:
        case = corpus[r["case_id"]]
        envelope = json.dumps({"choices": [{"message":
                          {"content": r["content"]}}]})
        parsed, err = rb.parse_general(envelope, case)
        if err or parsed is None:
            rejected.append({"case_id": r["case_id"], "error": err,
                             "content": r["content"][:80]})
            continue
        out_rows.append({"case_id": r["case_id"], "content": r["content"],
                         "label": parsed["label"]})
    report["n_accepted_by_frozen_parser"] = len(out_rows)
    report["n_rejected_by_frozen_parser"] = len(rejected)
    report["rejected"] = rejected
    report["checks"]["frozen_parser_accepts"] = (not rejected)

    with open(args.out, "w", encoding="utf-8") as fh:
        for row in out_rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(json.dumps(report, indent=1))
    return 0 if not rejected else 3


if __name__ == "__main__":
    raise SystemExit(main())
