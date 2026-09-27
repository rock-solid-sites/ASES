#!/usr/bin/env python3
"""Stage one agent-routed arm as a COMPLETE grid and score it with the frozen
harness/score.py, unmodified.

Why staging is necessary: score.py aggregates strictly over the five names in
common.MECHANISMS and hard-refuses a partial grid
(`FATAL grid incomplete: ... Refusing to score a partial grid`). An agent-routed
arm is a *substitute* for the `general_model` mechanism, not a sixth mechanism.
So each arm gets its own staging directory containing:

  cases.ndjson              byte-identical copy of the frozen corpus
  results/jev_raw.ndjson    the frozen Jev arm, copied unchanged
  results/baselines_raw.ndjson
        prior / rule / lexical   copied unchanged from the frozen run
        general_model            THIS ARM, replacing the space-bunny rows
  results/                  score.py writes scored.ndjson + metrics.json here

Nothing in harness/ is touched. The arm's answers are converted to raw rows by
calling the frozen parse_general(), so the prediction payloads are produced by
exactly the same code that produced the frozen ones.

Honest omissions, recorded rather than faked:
  latency_ms = null   per-case latency is not individually observable when 8
                      cases share one invocation, and the agent route's wall
                      clock is not comparable to the direct-HTTP arms anyway
                      (RECON.md section 4). Not estimated.
  usage        = null same reason; token accounting is per-invocation.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FOLLOWUP = os.path.dirname(HERE)
PHASE1 = os.path.dirname(FOLLOWUP)
sys.path.insert(0, os.path.join(PHASE1, "harness"))

import run_baselines as rb  # noqa: E402
import common as cm  # noqa: E402  (request_hash / serialise live here)
import score as sc  # noqa: E402  (imported to reuse its loader/constants only)

EXPECTED_SHA = "7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c"
ROUTE = "opencode-agent-route (opencode run --format json); NOT a direct HTTP call"


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_ndjson(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--model-id", required=True)
    ap.add_argument("--answers", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--runlog", default=None)
    args = ap.parse_args()

    frozen_cases = os.path.join(PHASE1, "cases.ndjson")
    sha = sha256_file(frozen_cases)
    if sha != EXPECTED_SHA:
        print(f"FATAL corpus sha mismatch: {sha}", file=sys.stderr)
        return 4

    cases = {c["id"]: c for c in load_ndjson(frozen_cases)}
    answers = load_ndjson(args.answers)
    got = {a["case_id"] for a in answers}
    missing = sorted(set(cases) - got)
    if missing:
        print(f"FATAL arm {args.tag} is missing {len(missing)} case(s): "
              f"{missing[:8]}{'...' if len(missing) > 8 else ''}", file=sys.stderr)
        print("score.py would refuse a partial grid; not staging.", file=sys.stderr)
        return 5

    os.makedirs(os.path.join(args.outdir, "results"), exist_ok=True)
    os.makedirs(os.path.join(args.outdir, "tables"), exist_ok=True)
    shutil.copyfile(frozen_cases, os.path.join(args.outdir, "cases.ndjson"))
    shutil.copyfile(os.path.join(PHASE1, "results", "jev_raw.ndjson"),
                    os.path.join(args.outdir, "results", "jev_raw.ndjson"))

    base = load_ndjson(os.path.join(PHASE1, "results", "baselines_raw.ndjson"))
    kept = [r for r in base if r["mechanism"] != "general_model"]
    dropped = [r for r in base if r["mechanism"] == "general_model"]
    if len(dropped) != len(cases):
        print(f"FATAL expected {len(cases)} general_model rows to replace, "
              f"found {len(dropped)}", file=sys.stderr)
        return 4

    runlog = {}
    if args.runlog and os.path.exists(args.runlog):
        runlog = json.load(open(args.runlog, encoding="utf-8"))
    walls = [a.get("wall_s") for a in runlog.get("attempts", [])
             if a.get("stage") == "ok" and a.get("wall_s")]

    new_rows = []
    for cid in sorted(cases):
        a = next(x for x in answers if x["case_id"] == cid)
        case = cases[cid]
        envelope = json.dumps({"choices": [{"message":
                          {"content": a["content"]}}]})
        parsed, err = rb.parse_general(envelope, case)
        body = rb.build_general_request(case, args.model_id)
        new_rows.append({
            "schema_version": "jevp1-result-1.0",
            "case_id": cid,
            "mechanism": "general_model",
            "request_hash": cm.request_hash(body),
            "request_body": body,
            "endpoint": ROUTE,
            "model_id": args.model_id,
            "http_status": 200,
            "raw_response": json.dumps({"choices": [{"message": {
                "content": a["content"]}}]}),
            "parsed": parsed,
            "prediction": parsed,
            "abstained": False,
            "latency_ms": None,
            "usage": None,
            "typed_error": err,
            "error_detail": None if parsed else "frozen parser rejected",
            "attempt": 1,
            "retries": 0,
            "timestamp_utc": runlog.get("finished_utc"),
            "harness_version": "1.0.0-followup05",
            "secrets_recorded": False,
        })

    out = os.path.join(args.outdir, "results", "baselines_raw.ndjson")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        for r in kept + new_rows:
            fh.write(json.dumps(r, ensure_ascii=False,
                                separators=(",", ":")) + "\n")

    print(f"staged arm={args.tag} model={args.model_id}")
    print(f"  cases={len(cases)} kept_offline={len(kept)} "
          f"general_model={len(new_rows)} (replaced {len(dropped)})")
    print(f"  corpus_sha256={sha}")
    print(f"  baselines_raw sha256={sha256_file(out)}")
    if walls:
        print(f"  ok-chunk wall_s: n={len(walls)} "
              f"min={min(walls)} max={max(walls)}")
    print(f"  latency_ms=null by design (not comparable to direct-HTTP arms)")
    print(f"  staging_dir={args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
