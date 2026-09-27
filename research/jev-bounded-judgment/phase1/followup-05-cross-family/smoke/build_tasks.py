#!/usr/bin/env python3
"""Build a sanitised task file for an agent-routed general-model arm.

Deterministic. Reads the frozen corpus and emits ONLY the fields a model is
allowed to see, using the frozen request builder from harness/run_baselines.py
so the user-message text is byte-identical to the direct-HTTP arms.

Ground truth is never emitted. Stripped fields, and why each is a leak:

  ground_truth          the answer
  control.deciding_fact the answer, in prose
  difficulty_note       the answer, in prose
  control.pair_id/base_case_id  lets a worker pair cases and infer the flip
  routing               precomputed legality, i.e. the answer
  provenance/area/split/difficulty  not answers, but not needed either

Emitted per case: id, question type, instructions, criteria, and the exact
user message that build_general_request() would have sent.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # .../smoke
FOLLOWUP = os.path.dirname(HERE)                           # .../followup-05-*
PHASE1 = os.path.dirname(FOLLOWUP)                         # .../phase1
sys.path.insert(0, os.path.join(PHASE1, "harness"))

import run_baselines as rb  # noqa: E402  (frozen builder; must not be edited)


def sanitise(case, model_id):
    q = case["questions"][0]
    body = rb.build_general_request(case, model_id)
    user = body["messages"][1]["content"]
    return {
        "case_id": case["id"],
        "question_type": q["type"],
        "instructions": q["instructions"],
        "criteria": q.get("criteria"),
        "system_prompt_frozen": rb.GEN_SYS,
        "user_message": user,
    }


def pick(cases, n):
    """Deterministic spread across question types: noul first, then the
    minority types, so a smoke test exercises every parse branch."""
    by_type = {}
    for c in cases:
        by_type.setdefault(c["questions"][0]["type"], []).append(c)
    order = ["noul", "choice", "score"]
    picked, i = [], 0
    while len(picked) < n:
        added = False
        for t in order:
            if i < len(by_type.get(t, [])) and len(picked) < n:
                picked.append(by_type[t][i])
                added = True
        if not added:
            break
        i += 1
    return picked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default=os.path.join(PHASE1, "cases.ndjson"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--model-id", required=True,
                    help="catalog id recorded in the request body")
    ap.add_argument("--limit", type=int, default=4)
    ap.add_argument("--case-ids", default=None,
                    help="comma-separated explicit ids; overrides --limit")
    args = ap.parse_args()

    cases = [json.loads(l) for l in open(args.cases, encoding="utf-8")
             if l.strip()]
    corpus_sha = hashlib.sha256(
        open(args.cases, "rb").read()).hexdigest()

    if args.case_ids:
        want = [s.strip() for s in args.case_ids.split(",") if s.strip()]
        index = {c["id"]: c for c in cases}
        missing = [w for w in want if w not in index]
        if missing:
            print(f"ERROR: unknown case ids: {missing}", file=sys.stderr)
            return 2
        chosen = [index[w] for w in want]
    else:
        chosen = pick(cases, args.limit)

    tasks = [sanitise(c, args.model_id) for c in chosen]

    # Leak guard: fail loudly if any forbidden key survives serialisation.
    blob = json.dumps(tasks)
    for forbidden in ("ground_truth", "deciding_fact", "difficulty_note",
                      "rationale", "answerable"):
        if forbidden in blob:
            print(f"ERROR: leak guard tripped on {forbidden!r}",
                  file=sys.stderr)
            return 3

    payload = {
        "corpus_sha256": corpus_sha,
        "model_id": args.model_id,
        "n_cases": len(tasks),
        "cases": tasks,
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print(f"wrote {len(tasks)} sanitised cases -> {args.out}")
    print(f"corpus_sha256={corpus_sha}")
    print("leak_guard=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
