#!/usr/bin/env python3
"""followup-01-spacebunny runner — ONE new baseline over the FROZEN corpus.

WHAT THIS IS
------------
A single add-one-baseline run: mechanism label `spacebunny`, model
`space-bunny-free`, over the unchanged 64-case corpus, to be compared with the
frozen Jev results. Nothing else changes. No new cases, no prompt tuning, no
temperature change, no re-authoring of anything.

FROZEN-CONDITION GUARANTEE
--------------------------
The request is not re-implemented here. `build_general_request`, `GEN_SYS` and
`GENERAL_MAX_TOKENS` are IMPORTED from the frozen
`../harness/run_baselines.py`, so the request body is byte-identical to the
frozen `general_model` requests by construction, not by review. On top of that
this runner refuses to make a single HTTP call unless, for all 64 cases:

  * the sha256 of cases.ndjson, results/jev_raw.ndjson and
    results/baselines_raw.ndjson equal the frozen digests below, AND
  * `request_hash(build_general_request(case, MODEL))` equals the frozen
    `general_model` row's stored `request_hash` for that case, AND
  * the built request body equals the frozen stored `request_body` (key order
    included, so the serialised bytes are equal), AND
  * `$OPENCODE_GO_API_KEY` is set and non-empty.

Any failure is a hard stop with a non-zero exit. It is NOT repaired here: a
mismatch would invalidate the comparison, and redesigning the request is out of
scope for this experiment.

N = 1, NO RETRIES
-----------------
`post_json` is called with `max_attempts=1`, so exactly one HTTP request is made
per cell. Transport failures, empty completions and unparseable replies are
RECORDED as rows with their `typed_error` and are never retried, never dropped,
and never re-sent. The run is a single sample; a second attempt at any cell
would silently convert an N=1 measurement into an N>1 one on exactly the cells
where the first attempt failed, which is the worst possible place to do it.

SECRETS
-------
The API key is read from the environment, used only as a bearer token, and
never logged, printed, or written to any artefact. `make_result` records
`secrets_recorded: false`.

ONE DISCLOSED TRANSPORT-LEVEL DIFFERENCE FROM THE FROZEN RUN
-------------------------------------------------------------
The `x-opencode-session` provenance header carries a follow-up-specific id
rather than the frozen run's `jev-phase1-baselines-20260926`. It is a provider
grouping header; it is not part of the request body, does not enter the prompt,
and does not affect the hashed request. It is changed so the two runs stay
separable in provider telemetry. It is recorded in the manifest.

Usage:
    python3 harness/run_spacebunny.py                 # the run (64 requests)
    python3 harness/run_spacebunny.py --check-only    # gates only, zero calls
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FOLLOWUP = os.path.dirname(HERE)
PHASE1 = os.path.dirname(FOLLOWUP)
PHASE1_HARNESS = os.path.join(PHASE1, "harness")
sys.path.insert(0, PHASE1_HARNESS)

from common import (  # noqa: E402
    NdjsonWriter,
    load_cases,
    make_result,
    post_json,
    request_hash,
)
from run_baselines import (  # noqa: E402
    GENERAL_MAX_TOKENS,
    GENERAL_MODEL,
    GEN_SYS,
    ZEN_CHAT_URL,
    build_general_request,
    parse_general,
)

RUNNER_VERSION = "1.0.0"
MECHANISM = "spacebunny"
SESSION_ID = "jev-phase1-followup-01-spacebunny-20260926"
API_KEY_ENV = "OPENCODE_GO_API_KEY"
MAX_ATTEMPTS = 1          # N = 1. Not a tunable. See the module docstring.
CASES_N = 64

# Frozen digests. Verified before any HTTP call; a mismatch is a hard stop.
FROZEN_INPUTS = {
    "cases.ndjson":
        "7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c",
    "results/jev_raw.ndjson":
        "e17ae014f0fc6cc311646dbfd98d5115d41854ddfcb98cfb41268f2da482d3bc",
    "results/baselines_raw.ndjson":
        "42f37690ec7ebbca75293ab0a690dc8efd8d5ef8a6a663db632bb05d682bf7ba",
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_frozen_inputs():
    """sha256 gate on every frozen input. Returns {relpath: digest}."""
    got = {}
    for rel, expect in FROZEN_INPUTS.items():
        path = os.path.join(PHASE1, rel)
        digest = sha256_file(path)
        got[rel] = digest
        if digest != expect:
            raise SystemExit(
                f"FROZEN INPUT MISMATCH {rel}\n  expected {expect}\n  found    {digest}\n"
                "STOP: the corpus or a frozen result file has changed. The "
                "comparison would be void; this run is not redone against a "
                "different input.")
    return got


def verify_frozen_requests(cases):
    """Every case's rebuilt request must equal the frozen general_model request."""
    frozen = {}
    with open(os.path.join(PHASE1, "results", "baselines_raw.ndjson"),
              "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row["mechanism"] == "general_model":
                frozen[row["case_id"]] = row
    if len(frozen) != CASES_N:
        raise SystemExit(
            f"FROZEN CONDITION FAIL: expected {CASES_N} frozen general_model "
            f"rows, found {len(frozen)}")

    report = []
    for case in cases:
        body = build_general_request(case, GENERAL_MODEL)
        digest = request_hash(body)
        ref = frozen[case["id"]]
        if digest != ref["request_hash"] or body != ref["request_body"]:
            raise SystemExit(
                f"FROZEN CONDITION FAIL on {case['id']}\n"
                f"  rebuilt  {digest}\n  frozen   {ref['request_hash']}\n"
                f"  bodies equal: {body == ref['request_body']}\n"
                "STOP: the rebuilt request is not the frozen request. "
                "Redesigning it is out of scope for this experiment; the run "
                "is abandoned rather than adjusted.")
        report.append({"case_id": case["id"], "request_hash": digest,
                       "matches_frozen": True})
    return report


def preflight(check_only=False):
    """All gates. Raises SystemExit on any failure. Returns the gate record."""
    gates = {"runner_version": RUNNER_VERSION, "mechanism": MECHANISM}
    gates["frozen_input_sha256"] = verify_frozen_inputs()
    cases = load_cases(os.path.join(PHASE1, "cases.ndjson"))
    if len(cases) != CASES_N:
        raise SystemExit(f"FROZEN CONDITION FAIL: {len(cases)} cases, expected {CASES_N}")
    gates["n_cases"] = len(cases)
    gates["frozen_condition"] = {
        "requests_compared": CASES_N,
        "mismatches": 0,
        "criterion": "request_hash(build_general_request(case, 'space-bunny-free')) "
                     "== frozen general_model row request_hash AND "
                     "request_body == frozen request_body, for all 64 cases",
        "passed": True,
    }
    gates["conditions"] = {
        "model_id": GENERAL_MODEL,
        "endpoint": ZEN_CHAT_URL,
        # The prompt is not re-implemented; it is imported. Pinning its digest
        # here makes the "same GEN_SYS" claim checkable by a reader instead of
        # a claim they have to take on trust.
        "gen_sys_sha256": hashlib.sha256(GEN_SYS.encode("utf-8")).hexdigest(),
        "gen_sys_source": "frozen harness/run_baselines.py:GEN_SYS (imported, not copied)",
        "max_tokens": GENERAL_MAX_TOKENS,
        "temperature": 0,
        "max_attempts_per_cell": MAX_ATTEMPTS,
        "retries": 0,
        "session_header": SESSION_ID,
    }
    key = os.environ.get(API_KEY_ENV)
    gates["api_key_env"] = API_KEY_ENV
    gates["api_key_present"] = bool(key)
    if not key:
        raise SystemExit(f"STOP: ${API_KEY_ENV} is unset or empty. No call was made.")
    if not check_only:
        gates["frozen_request_hashes"] = verify_frozen_requests(cases)
    print(f"  frozen inputs verified: {len(FROZEN_INPUTS)} files")
    print(f"  frozen-condition check: {CASES_N}/{CASES_N} requests identical"
          f"{' (preflight)' if check_only else ''}")
    print(f"  {API_KEY_ENV}: present (value never printed)")
    return gates, cases


def run(cases, api_key, out_path):
    written = {"n": 0}
    with NdjsonWriter(out_path) as w:
        for i, case in enumerate(cases, 1):
            body = build_general_request(case, GENERAL_MODEL)
            try:
                resp = post_json(ZEN_CHAT_URL, body, api_key,
                                 session_id=SESSION_ID,
                                 max_attempts=MAX_ATTEMPTS)
                if resp["typed_error"] is None:
                    pred, perr = parse_general(resp["raw_response"], case)
                    if perr:
                        resp["typed_error"] = perr
                        resp["error_detail"] = (
                            "200 OK but reply did not match a candidate label")
                        parsed = None
                    else:
                        parsed = {"raw_content": pred["raw_content"],
                                  "hard_label": True}
                        pred = {k: v for k, v in pred.items()
                                if k != "raw_content"}
                else:
                    parsed, pred = None, None
                row = make_result(
                    case=case, mechanism=MECHANISM, body=body,
                    endpoint=ZEN_CHAT_URL, model_id=GENERAL_MODEL,
                    http_status=resp["http_status"],
                    raw=resp["raw_response"], parsed=parsed,
                    prediction=pred, typed_error=resp["typed_error"],
                    error_detail=resp["error_detail"],
                    usage=resp["usage"], latency_ms=resp["latency_ms"],
                    attempts=resp["attempts"], retries=resp["retries"])
            except Exception as e:  # noqa: BLE001 - the grid must stay complete
                row = make_result(
                    case=case, mechanism=MECHANISM, body=body,
                    endpoint=ZEN_CHAT_URL, model_id=GENERAL_MODEL,
                    http_status=None, raw="", parsed=None, prediction=None,
                    typed_error="internal_error",
                    error_detail=f"{type(e).__name__}: {e}"[:200],
                    usage=None, latency_ms=None,
                    attempts=0, retries=0)
            w.write(row)
            written["n"] = w.n
            if i % 10 == 0 or i == len(cases):
                print(f"  spacebunny {i}/{len(cases)}", flush=True)
    return written["n"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(
        FOLLOWUP, "results", "spacebunny_raw.ndjson"))
    ap.add_argument("--check-only", action="store_true",
                    help="run every gate, make zero HTTP calls")
    args = ap.parse_args()

    print("run_spacebunny: gates")
    gates, cases = preflight(check_only=args.check_only)
    if args.check_only:
        print("run_spacebunny: --check-only, no call made")
        return 0
    print(f"run_spacebunny: {len(cases)} cases, 1 attempt each, no retries")
    print(f"  model={GENERAL_MODEL} endpoint={ZEN_CHAT_URL}")
    n = run(cases, os.environ[API_KEY_ENV], args.out)
    print(f"run_spacebunny: wrote {n} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
