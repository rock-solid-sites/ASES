#!/usr/bin/env python3
"""Deterministic Jev client.

Runs every case in `cases.ndjson` against
`POST https://opencode.ai/zen/v1/systemone` and writes one NDJSON row per case
to `results/jev_raw.ndjson`.

Guarantees:
  * The request body is built from `state` and `questions` ONLY. Routing
    signals, ground truth, and control metadata are never sent, so area D
    legality cannot leak to the model.
  * One row per case, always. A failure becomes a `typed_error` on the row, so
    the case x mechanism grid is never silently short.
  * The raw response body is stored verbatim. Nothing is reduced to pass/fail.
  * `cases.ndjson` is opened read-only and never rewritten.
  * Case order is by ascending case id, so the run is reproducible.

Usage:
    OPENCODE_GO_API_KEY=... python3 harness/run_jev.py [--out PATH] [--limit N]
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from common import (  # noqa: E402
    ERR_INTERNAL,
    NdjsonWriter,
    load_cases,
    make_result,
    parse_jev,
    post_json,
)

JEV_URL = "https://opencode.ai/zen/v1/systemone"
JEV_MODEL = "jev-1.13-free"
API_KEY_ENV = "OPENCODE_GO_API_KEY"


def build_request(case, model_id=JEV_MODEL):
    """Build the systemone body. Reads ONLY state + questions.

    The per-type criteria containers are the ones measured in preflight:
    `choice` takes a dict of option_key -> option_label, `score` takes a list of
    ordered labels, `noul` takes no criteria at all.
    """
    q = case["questions"][0]
    qq = {"type": q["type"], "instructions": q["instructions"]}
    if q["type"] == "choice":
        qq["criteria"] = dict(q["criteria"])          # preserve wire order
    elif q["type"] == "score":
        qq["criteria"] = list(q["criteria"])
    return {"model": model_id, "state": case["state"], "questions": {"q": qq}}


def run(cases, writer, url=JEV_URL, model_id=JEV_MODEL, api_key=None,
        limit=None, session_id="jev-phase1-run"):
    subset = cases[:limit] if limit else cases
    for i, case in enumerate(subset, 1):
        try:
            body = build_request(case, model_id)
            resp = post_json(url, body, api_key, session_id=session_id)
            if resp["typed_error"] is None:
                parsed, prediction, perr = parse_jev(resp["raw_response"], case)
                if perr is not None:
                    resp["typed_error"] = perr
                    resp["error_detail"] = "200 OK but unparseable answer"
            else:
                parsed, prediction = None, None
            row = make_result(
                case=case, mechanism="jev", body=body, endpoint=url,
                model_id=model_id, http_status=resp["http_status"],
                raw=resp["raw_response"], parsed=parsed,
                prediction=prediction, typed_error=resp["typed_error"],
                error_detail=resp["error_detail"], usage=resp["usage"],
                latency_ms=resp["latency_ms"], attempts=resp["attempts"],
                retries=resp["retries"])
        except Exception as e:  # noqa: BLE001 - never lose a case
            row = make_result(
                case=case, mechanism="jev", body=None, endpoint=url,
                model_id=model_id, http_status=None, raw="", parsed=None,
                prediction=None, typed_error=ERR_INTERNAL,
                error_detail=f"{type(e).__name__}: {e}"[:200], usage=None,
                latency_ms=None, attempts=0, retries=0)
        writer.write(row)
        if i % 10 == 0 or i == len(subset):
            print(f"  jev {i}/{len(subset)} "
                  f"(err={row['typed_error'] or '-'})", flush=True)
    return writer.n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default=os.path.join(ROOT, "cases.ndjson"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results",
                                                   "jev_raw.ndjson"))
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--url", default=JEV_URL)
    ap.add_argument("--model", default=JEV_MODEL)
    args = ap.parse_args()

    key = os.environ.get(API_KEY_ENV)
    if not key:
        print(f"FATAL: {API_KEY_ENV} is not set. Refusing to run; the Jev "
              f"endpoint requires it. (Never pass the key on the command "
              f"line -- it would land in shell history.)", file=sys.stderr)
        return 2

    cases = load_cases(args.cases)
    print(f"run_jev: {len(cases)} cases -> {args.out}")
    print(f"  endpoint={args.url} model={args.model} "
          f"key_env={API_KEY_ENV}(set, value not recorded)")
    with NdjsonWriter(args.out) as w:
        n = run(cases, w, url=args.url, model_id=args.model, api_key=key,
                limit=args.limit)
    print(f"run_jev: wrote {n} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
