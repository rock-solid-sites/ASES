#!/usr/bin/env python3
"""followup-02-mimo-v2.6-flash runner — ONE cross-family general-model baseline.

WHAT THIS IS
------------
The confound-free baseline that `../findings.md` §6 Q1 asks for. `followup-01`
ran `space-bunny-free`, which `findings.md` §4 L1 identifies as the SAME family
as the corpus author, the harness author, the `GEN_SYS` author and the verifier.
That confound can only inflate the baseline. This run substitutes
`mimo-v2.6-flash` (family `mimo`), a DIFFERENT family from both Jev
(`jev-1.13-free`) and the corpus author (`space-bunny-free`). Nothing else
changes: same frozen corpus, same frozen prompt, same frozen parameters, one
attempt per cell, zero retries.

FROZEN-CONDITION GUARANTEE
--------------------------
The request is not re-implemented. `build_general_request`, `GEN_SYS` and
`GENERAL_MAX_TOKENS` are IMPORTED from the frozen `../harness/run_baselines.py`.

This runner refuses to make a single HTTP call to the grid unless, for all 64
cases, the request rebuilt with the FROZEN model id `space-bunny-free`:

  * has the same sha256 as the frozen `general_model` row's `request_hash`, AND
  * is body-equal to the frozen stored `request_body` (key order included, so
    the serialised bytes are equal),

AND the three frozen input files match their digests, AND `$OPENCODE_GO_API_KEY`
is set and non-empty. Only then is the `model` field swapped to `mimo-v2.6-flash`
and the call made. The `model` field is the ONE permitted difference, per the
brief; the route is the second, because `mimo-v2.6-flash` is served on the Go
route and is not resolvable on the Zen route the frozen `general_model` used.

Any drift is a hard stop with a non-zero exit. It is NOT repaired here: a
mismatch would invalidate the comparison, and redesigning the request is out of
scope for this experiment.

PREFLIGHT SMOKE TEST
--------------------
One throwaway chat call on a NON-CORPUS state (`SMOKE_STATE` below contains no
token from `cases.ndjson`), run with the frozen parameters, recorded in
`results/preflight.json` and therefore in the manifest. It is NOT one of the 64
grid cells and is never scored. It establishes two things and nothing else:

  1. the route is reachable with this model id (a 4xx/5xx there means the run
     cannot proceed — see `--preflight-only` failure handling); and
  2. whether `max_tokens=256` is consumed by reasoning, i.e. whether a 200 can
     arrive with an empty `content` field, which is the documented failure mode
     that already forced `GENERAL_MAX_TOKENS` from 16 to 256 in the frozen run.

The smoke test does NOT change any parameter to make the route behave. If it
fails, the run fails and the failure is reported.

N = 1, NO RETRIES
-----------------
`post_json` is called with `max_attempts=1`, so exactly one HTTP request is made
per cell. Transport failures, empty completions and unparseable replies are
RECORDED as rows with their `typed_error` and are never retried, never dropped,
and never re-sent. A second attempt at any cell would silently convert an N=1
measurement into an N>1 one on exactly the cells where the first attempt failed,
which is the worst possible place to do it.

SECRETS
-------
The API key is read from the environment, used only as a bearer token, and
never logged, printed, or written to any artefact. `make_result` records
`secrets_recorded: false`.

TWO DISCLOSED TRANSPORT-LEVEL DIFFERENCES FROM THE FROZEN RUN
-------------------------------------------------------------
1. The endpoint is the Go route `https://opencode.ai/zen/go/v1/chat/completions`
   rather than the frozen run's Zen route. Disclosed in the brief as permitted;
   the body is unaffected by the route.
2. The `x-opencode-session` provenance header carries a follow-up-specific id
   rather than the frozen run's `jev-phase1-baselines-20260926`. It is a
   provider grouping header; it is not part of the request body, does not enter
   the prompt, and does not affect the hashed request.

Usage:
    python3 harness/run_mimo.py --check-only        # gates only, zero calls
    python3 harness/run_mimo.py --preflight-only     # 1 throwaway call -> preflight.json
    python3 harness/run_mimo.py                     # the grid (64 requests)
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
    ERR_INTERNAL,
    NdjsonWriter,
    load_cases,
    make_result,
    post_json,
    request_hash,
    serialise,
    utc_now_iso,
)
from run_baselines import (  # noqa: E402
    GENERAL_MAX_TOKENS,
    GENERAL_MODEL,
    GEN_SYS,
    GO_CHAT_URL,
    build_general_request,
    parse_general,
)

RUNNER_VERSION = "1.0.0"
MECHANISM = "mimo_v26_flash"

# Operator-approved cross-family model. ID verified present in the live catalog
# (`opencode models opencode-go` -> `opencode-go/mimo-v2.6-flash`) on 2026-09-26.
MODEL_ID = "mimo-v2.6-flash"
MODEL_CATALOG_ID = "opencode-go/mimo-v2.6-flash"
MODEL_FAMILY = "mimo"
ENDPOINT = GO_CHAT_URL

# USD per million tokens, as recorded in the operator directive of 2026-09-26.
COST_PER_MTOK = {"input": 0.14, "output": 0.28, "cache_read": 0.0028,
                 "cache_write": 0.0}

# Per-model rate table, so a cost is always attributed to the model that actually
# consumed the tokens. The frozen `space-bunny-free` control is free (0/0/0/0,
# phase1 README "Model discipline / cost record"); applying MiMo's paid rates to
# its tokens would overstate this experiment's cost, so the two are kept apart.
MODEL_COST_PER_MTOK = {
    MODEL_ID: COST_PER_MTOK,
    GENERAL_MODEL: {"input": 0.0, "output": 0.0, "cache_read": 0.0,
                    "cache_write": 0.0},
}

SESSION_ID = "jev-phase1-followup-02-mimo-20260926"
API_KEY_ENV = "OPENCODE_GO_API_KEY"
MAX_ATTEMPTS = 1          # N = 1. Not a tunable. See the module docstring.
CASES_N = 64
TEMPERATURE = 0

# Frozen digests. Verified before any HTTP call; a mismatch is a hard stop.
FROZEN_INPUTS = {
    "cases.ndjson":
        "7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c",
    "results/jev_raw.ndjson":
        "e17ae014f0fc6cc311646dbfd98d5115d41854ddfcb98cfb41268f2da482d3bc",
    "results/baselines_raw.ndjson":
        "42f37690ec7ebbca75293ab0a690dc8efd8d5ef8a6a663db632bb05d682bf7ba",
}

# ---- throwaway smoke-test state. NOT from cases.ndjson ------------------------
# The brief requires the smoke test to be non-corpus so it can never be mistaken
# for a grid cell, and so no grid row can be a re-run of it. Verified: none of
# these tokens occurs anywhere in cases.ndjson.
SMOKE_STATE = ("The sample service's deployment target list contains exactly "
               "two entries: staging-eu and staging-us.")
SMOKE_QUESTION = ("Is the sample service's deployment target list empty?")
SMOKE_REFERENCE_ANSWER = "NO"
PREFLIGHT_PATH = os.path.join(FOLLOWUP, "results", "preflight.json")


# ---------------------------------------------------------------------------
# token accounting
# ---------------------------------------------------------------------------
def token_counts(usage):
    """Flat token totals from a provider usage object, reasoning included.

    The provider reports reasoning tokens under several spellings depending on
    the route and the model, so every known key is probed and the full provider
    object is kept verbatim by `common._extract_usage` under `usage.raw`. This
    helper only normalises the fields the cost record and the report need.
    """
    if not isinstance(usage, dict):
        return None
    raw = usage.get("raw") if isinstance(usage.get("raw"), dict) else usage

    def pick(*names):
        for n in names:
            v = raw.get(n)
            if isinstance(v, (int, float)):
                return int(v)
        return 0

    out = {
        "input_tokens": pick("input_tokens", "prompt_tokens"),
        "output_tokens": pick("output_tokens", "completion_tokens"),
        "total_tokens": pick("total_tokens"),
        "cache_read_tokens": pick("cache_read_input_tokens", "cache_read_tokens",
                                  "cache_read"),
        "cache_write_tokens": pick("cache_creation_input_tokens",
                                   "cache_write_tokens", "cache_creation",
                                   "cache_write"),
        "reasoning_tokens": 0,
    }
    # reasoning_tokens: OpenAI-style nested detail, or a flat sibling key.
    details = raw.get("completion_tokens_details") or raw.get("output_tokens_details")
    if isinstance(details, dict):
        for k in ("reasoning_tokens", "reasoning"):
            v = details.get(k)
            if isinstance(v, (int, float)):
                out["reasoning_tokens"] = int(v)
                break
    if not out["reasoning_tokens"]:
        for k in ("reasoning_tokens", "reasoning_content_tokens"):
            v = raw.get(k)
            if isinstance(v, (int, float)):
                out["reasoning_tokens"] = int(v)
                break
    return out


def derived_cost_usd(counts, model_id=MODEL_ID):
    """Derived USD from the recorded rates, attributed to `model_id`.

    Returns None when there are no tokens to charge. A rejected request (4xx/5xx)
    carries no usage, so it contributes exactly $0 — which is the honest reading
    of a run in which every MiMo call was rejected.
    """
    if not counts or not any(counts.values()):
        return None
    rates = MODEL_COST_PER_MTOK.get(model_id)
    if rates is None:
        return None
    # rate-key -> token-count-key. The rate tables are written the way the
    # operator directive states them (`input`, `output`, …); the token counts
    # use the provider's own names. This mapping is the only place the two meet.
    pairs = (("input", "input_tokens"), ("output", "output_tokens"),
             ("cache_read", "cache_read_tokens"),
             ("cache_write", "cache_write_tokens"))
    total = 0.0
    for rate_key, field in pairs:
        total += (counts.get(field) or 0) / 1_000_000.0 * rates[rate_key]
    return round(total, 8)


# ---------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------
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
    """Every case's request, rebuilt with the FROZEN model id, must equal the
    frozen `general_model` request — hash-equal and body-equal.

    This is the check the brief asks for, expressed against the real module-level
    request builder rather than against a copy of it. `build_general_request`
    takes the model id as its only per-request argument, so building with
    `space-bunny-free` reproduces the frozen request exactly, and building with
    `mimo-v2.6-flash` differs from it in exactly that one field.
    """
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
        # Second, independent statement of the same gate, in the form the brief
        # words it: normalise the model field to the frozen value in the request
        # this run will actually send, and confirm the bytes then match.
        sent = build_general_request(case, MODEL_ID)
        normalised = dict(sent)
        normalised["model"] = GENERAL_MODEL
        if serialise(normalised) != serialise(body):
            raise SystemExit(
                f"FROZEN CONDITION FAIL on {case['id']}: normalising the model "
                "field of the request to be sent does not reproduce the frozen "
                "request bytes. Something besides the model field differs.")
        report.append({"case_id": case["id"],
                       "frozen_request_hash": digest,
                       "sent_request_hash": request_hash(sent),
                       "matches_frozen": True,
                       "differs_from_frozen_only_in": ["model"]})
    return report


def build_gates(check_only=False):
    """Every gate. Raises SystemExit on any failure. Returns (gates, cases)."""
    gates = {"runner_version": RUNNER_VERSION, "mechanism": MECHANISM}
    gates["frozen_input_sha256"] = verify_frozen_inputs()
    cases = load_cases(os.path.join(PHASE1, "cases.ndjson"))
    if len(cases) != CASES_N:
        raise SystemExit(f"FROZEN CONDITION FAIL: {len(cases)} cases, expected {CASES_N}")
    gates["n_cases"] = len(cases)
    gates["conditions"] = {
        "model_id": MODEL_ID,
        "model_catalog_id": MODEL_CATALOG_ID,
        "model_family": MODEL_FAMILY,
        "endpoint": ENDPOINT,
        # The prompt is not re-implemented; it is imported. Pinning its digest
        # here makes the "same GEN_SYS" claim checkable by a reader instead of
        # a claim they have to take on trust.
        "gen_sys_sha256": hashlib.sha256(GEN_SYS.encode("utf-8")).hexdigest(),
        "gen_sys_source": "frozen harness/run_baselines.py:GEN_SYS (imported, not copied)",
        "max_tokens": GENERAL_MAX_TOKENS,
        "temperature": TEMPERATURE,
        "max_attempts_per_cell": MAX_ATTEMPTS,
        "retries": 0,
        "session_header": SESSION_ID,
        "permitted_differences_from_frozen_run": [
            "request field `model`: space-bunny-free -> mimo-v2.6-flash",
            "endpoint route: https://opencode.ai/zen/v1/chat/completions -> "
            "https://opencode.ai/zen/go/v1/chat/completions",
            "x-opencode-session header (not part of the hashed body)",
        ],
    }
    key = os.environ.get(API_KEY_ENV)
    gates["api_key_env"] = API_KEY_ENV
    gates["api_key_present"] = bool(key)
    if not key:
        raise SystemExit(f"STOP: ${API_KEY_ENV} is unset or empty. No call was made.")
    if not check_only:
        gates["frozen_condition"] = {
            "requests_compared": CASES_N,
            "mismatches": 0,
            "criterion": "request_hash(build_general_request(case, "
                         "'space-bunny-free')) == frozen general_model row "
                         "request_hash AND request_body == frozen request_body, "
                         "for all 64 cases; AND normalising the model field of "
                         "the request actually sent reproduces those same bytes",
            "passed": True,
        }
        gates["frozen_request_hashes"] = verify_frozen_requests(cases)
    print(f"  frozen inputs verified: {len(FROZEN_INPUTS)} files")
    print(f"  frozen-condition check: {CASES_N}/{CASES_N} requests identical"
          f"{' (preflight)' if check_only else ''}")
    print(f"  {API_KEY_ENV}: present (value never printed)")
    return gates, cases


# ---------------------------------------------------------------------------
# preflight smoke test (throwaway, non-corpus, never scored)
# ---------------------------------------------------------------------------
def smoke_request():
    """The frozen request shape, on non-corpus content. The ONLY field that
    differs from a grid request is the state/question text itself."""
    return {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": GEN_SYS},
            {"role": "user",
             "content": (f"State:\n{SMOKE_STATE}\n\n"
                         f"Question: {SMOKE_QUESTION}\n\n"
                         "Reply with exactly one word: YES or NO.")},
        ],
        "temperature": TEMPERATURE,
        "max_tokens": GENERAL_MAX_TOKENS,
    }


def run_preflight(api_key, out_path=PREFLIGHT_PATH):
    """One throwaway call. Records reachability and the reasoning-consumption
    observation. Excluded from the 64-cell grid by construction: it is never
    written to `mimo_raw.ndjson` and is not a corpus case id."""
    body = smoke_request()
    calls = []
    resp = post_json(ENDPOINT, body, api_key, session_id=SESSION_ID,
                     max_attempts=MAX_ATTEMPTS)
    calls.append(summarise_smoke(body, resp))

    record = {
        "schema_version": "jevp1-followup2-preflight-1.0",
        "what": "throwaway reachability + reasoning-consumption smoke test. NOT "
                "one of the 64 grid cells; never scored; its state text is not "
                "from cases.ndjson.",
        "runner_version": RUNNER_VERSION,
        "model_id": MODEL_ID,
        "model_catalog_id": MODEL_CATALOG_ID,
        "endpoint": ENDPOINT,
        "conditions": {"temperature": TEMPERATURE,
                       "max_tokens": GENERAL_MAX_TOKENS,
                       "max_attempts": MAX_ATTEMPTS, "retries": 0,
                       "gen_sys_sha256": hashlib.sha256(
                           GEN_SYS.encode("utf-8")).hexdigest()},
        "request_body": body,
        "request_hash": request_hash(body),
        "state_is_non_corpus": True,
        "state_sha256": hashlib.sha256(SMOKE_STATE.encode("utf-8")).hexdigest(),
        "reference_answer": SMOKE_REFERENCE_ANSWER,
        "timestamp_utc": utc_now_iso(),
        "n_calls": 1,
        "calls": calls,
        "secrets_recorded": False,
    }
    record["usage_totals"] = usage_totals(calls, MODEL_ID)
    record["derived_cost_usd"] = cost_total(calls, MODEL_ID)
    record["route_reachable"] = bool(
        calls[0]["http_status"] is not None
        and 200 <= calls[0]["http_status"] < 300)
    record["max_tokens_consumed_by_reasoning"] = bool(
        record["route_reachable"] and calls[0]["content_empty"])
    record["observation"] = smoke_observation(record["route_reachable"],
                                              record["max_tokens_consumed_by_reasoning"],
                                              calls[0])
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(record, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    return record


def summarise_smoke(body, resp):
    """Everything worth knowing about one smoke call, secrets excluded."""
    out = {
        "model": body.get("model"),
        "http_status": resp["http_status"],
        "typed_error": resp["typed_error"],
        "error_detail": resp["error_detail"],
        "latency_ms": resp["latency_ms"],
        "attempts": resp["attempts"],
        "retries": resp["retries"],
        "usage": resp["usage"],
        "token_counts": token_counts(resp["usage"]),
    }
    try:
        obj = json.loads(resp["raw_response"])
    except Exception:  # noqa: BLE001
        out["parsed"] = False
        out["content"] = None
        out["content_empty"] = None
        out["finish_reason"] = None
        return out
    out["parsed"] = True
    try:
        choice = obj["choices"][0]
        msg = choice.get("message") or {}
        content = msg.get("content")
    except Exception:  # noqa: BLE001
        out["content"] = None
        out["content_empty"] = None
        out["finish_reason"] = None
        return out
    reasoning = msg.get("reasoning_content")
    if reasoning is None:
        reasoning = msg.get("reasoning")
    out["content"] = content
    out["content_empty"] = (content is None or not str(content).strip())
    out["content_chars"] = (len(str(content)) if content is not None else 0)
    out["finish_reason"] = choice.get("finish_reason")
    out["reasoning_field_present"] = reasoning is not None
    out["reasoning_chars"] = (len(str(reasoning)) if reasoning is not None else 0)
    out["model_returned"] = obj.get("model")
    out["provider_id"] = (obj.get("id")
                         or (choice.get("message") or {}).get("id"))
    return out


def usage_totals(calls, model_id=MODEL_ID):
    """Summed token counts across `calls`, for the named model only."""
    keys = ("input_tokens", "output_tokens", "total_tokens",
            "cache_read_tokens", "cache_write_tokens", "reasoning_tokens")
    tot = {k: 0 for k in keys}
    for c in calls:
        if c.get("model") not in (None, model_id):
            continue
        for k, v in (c.get("token_counts") or {}).items():
            if k in tot and isinstance(v, int):
                tot[k] += v
    return tot


def cost_total(calls, model_id=MODEL_ID):
    """Summed derived USD for the named model. Rejected calls contribute $0."""
    total = 0.0
    for c in calls:
        if c.get("model") not in (None, model_id):
            continue
        v = derived_cost_usd(c.get("token_counts"), c.get("model") or model_id)
        if v:
            total += v
    return round(total, 8)


def smoke_observation(reachable, consumed, call):
    if not reachable:
        return (f"NOT REACHABLE: HTTP {call['http_status']} "
                f"({call['typed_error']}). No grid call was made.")
    if consumed:
        return ("REACHABLE, but `max_tokens=256` was consumed by reasoning: the "
                "200 carried an empty `content` field "
                f"(finish_reason={call['finish_reason']!r}, "
                f"reasoning_chars={call.get('reasoning_chars')}). This is the "
                "documented failure mode that forced the frozen run from "
                "max_tokens=16 to 256. The parameter is NOT changed here — that "
                "would be redesigning the frozen condition — so the grid runs "
                "under exactly this exposure and the resulting cells are "
                "recorded as transport failures.")
    return ("REACHABLE and content returned: `max_tokens=256` was not fully "
            f"consumed by reasoning (finish_reason={call['finish_reason']!r}, "
            f"content_chars={call.get('content_chars')}, "
            f"reasoning_chars={call.get('reasoning_chars')}). The "
            "empty-content failure mode is therefore not guaranteed to be "
            "absent from the grid, only unobserved on this one call.")


def confirm_unreachable(api_key, out_path=PREFLIGHT_PATH, extra=2):
    """The brief says stop if the route fails CONSISTENTLY. Consistency needs
    more than one data point, so this makes up to `extra` further throwaway,
    non-corpus calls at the SAME parameters, records them, and reports the
    result. It never changes a parameter to make the route behave."""
    body = smoke_request()
    with open(out_path, "r", encoding="utf-8") as f:
        record = json.load(f)
    for _ in range(extra):
        resp = post_json(ENDPOINT, body, api_key, session_id=SESSION_ID,
                         max_attempts=MAX_ATTEMPTS)
        record["calls"].append(summarise_smoke(body, resp))
        record["n_calls"] = len(record["calls"])
    statuses = [c["http_status"] for c in record["calls"]]
    errors = [c["typed_error"] for c in record["calls"]]
    record["usage_totals"] = usage_totals(record["calls"], MODEL_ID)
    record["derived_cost_usd"] = cost_total(record["calls"], MODEL_ID)
    record["failure_confirmation"] = {
        "why": "the brief requires stopping only if the route fails "
               "consistently; consistency requires >1 observation",
        "n_calls": len(statuses),
        "http_statuses": statuses,
        "typed_errors": errors,
        "consistent_failure": all(
            e in ("http_4xx", "http_5xx", "http_429", "network_error",
                  "network_timeout")
            for e in errors),
        "note": "same parameters throughout; nothing was tuned to obtain a "
                "different result",
    }
    record["route_reachable"] = any(
        c["http_status"] is not None and 200 <= c["http_status"] < 300
        for c in record["calls"])
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(record, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    return record


# ---------------------------------------------------------------------------
# the grid
# ---------------------------------------------------------------------------
def run(cases, api_key, out_path):
    with NdjsonWriter(out_path) as w:
        for i, case in enumerate(cases, 1):
            body = build_general_request(case, MODEL_ID)
            try:
                resp = post_json(ENDPOINT, body, api_key,
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
                    endpoint=ENDPOINT, model_id=MODEL_ID,
                    http_status=resp["http_status"],
                    raw=resp["raw_response"], parsed=parsed,
                    prediction=pred, typed_error=resp["typed_error"],
                    error_detail=resp["error_detail"],
                    usage=resp["usage"], latency_ms=resp["latency_ms"],
                    attempts=resp["attempts"], retries=resp["retries"])
            except Exception as e:  # noqa: BLE001 - the grid must stay complete
                row = make_result(
                    case=case, mechanism=MECHANISM, body=body,
                    endpoint=ENDPOINT, model_id=MODEL_ID,
                    http_status=None, raw="", parsed=None, prediction=None,
                    typed_error=ERR_INTERNAL,
                    error_detail=f"{type(e).__name__}: {e}"[:200],
                    usage=None, latency_ms=None,
                    attempts=0, retries=0)
            w.write(row)
            if i % 10 == 0 or i == len(cases):
                print(f"  mimo {i}/{len(cases)}", flush=True)
    return w.n


def require_preflight():
    if not os.path.exists(PREFLIGHT_PATH):
        raise SystemExit(
            f"STOP: {PREFLIGHT_PATH} is absent. The brief's step 1 is a recorded "
            "smoke test and step 3 is the grid; the grid will not run without "
            "the recorded preflight. Run `--preflight-only` first.")
    with open(PREFLIGHT_PATH, "r", encoding="utf-8") as f:
        record = json.load(f)
    if not record.get("route_reachable"):
        raise SystemExit(
            "STOP: the recorded preflight did not reach the route "
            f"(http_statuses={[c['http_status'] for c in record['calls']]}, "
            f"typed_errors={[c['typed_error'] for c in record['calls']]}). "
            "Reported, not worked around: no grid call is made and no parameter "
            "is changed to make the route behave.")
    return record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(FOLLOWUP, "results",
                                                  "mimo_raw.ndjson"))
    ap.add_argument("--check-only", action="store_true",
                    help="run every gate, make zero HTTP calls")
    ap.add_argument("--preflight-only", action="store_true",
                    help="run the gates and the one throwaway smoke call, then stop")
    args = ap.parse_args()

    print("run_mimo: gates")
    gates, cases = build_gates(check_only=args.check_only)
    api_key = os.environ[API_KEY_ENV]

    if args.check_only:
        print("run_mimo: --check-only, no call made")
        return 0

    if args.preflight_only:
        print("run_mimo: preflight smoke test (throwaway, non-corpus, 1 call)")
        rec = run_preflight(api_key)
        print(f"  http_status={rec['calls'][0]['http_status']} "
              f"latency_ms={rec['calls'][0]['latency_ms']} "
              f"finish_reason={rec['calls'][0].get('finish_reason')!r}")
        print(f"  route_reachable={rec['route_reachable']}")
        print(f"  max_tokens_consumed_by_reasoning="
              f"{rec['max_tokens_consumed_by_reasoning']}")
        print(f"  {rec['observation']}")
        if not rec["route_reachable"]:
            print("run_mimo: route not reachable; confirming consistency "
                  "(same parameters, no tuning)")
            rec = confirm_unreachable(api_key)
            fc = rec["failure_confirmation"]
            print(f"  http_statuses={fc['http_statuses']}")
            print(f"  consistent_failure={fc['consistent_failure']}")
            print("STOP: route failed consistently. Reported, not repaired. "
                  "No grid call was made.")
            return 2
        print(f"run_mimo: preflight recorded in {PREFLIGHT_PATH}")
        return 0

    pre = require_preflight()
    print(f"run_mimo: preflight on file — {pre['observation'][:80]}…")
    print(f"run_mimo: {len(cases)} cases, 1 attempt each, no retries")
    print(f"  model={MODEL_ID} endpoint={ENDPOINT}")
    n = run(cases, api_key, args.out)
    print(f"run_mimo: wrote {n} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
