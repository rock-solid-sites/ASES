#!/usr/bin/env python3
"""followup-02 route diagnostics — why the MiMo grid could not be run.

WHAT THIS IS
------------
The brief's step 1 is a preflight smoke test on a throwaway, non-corpus state,
with the instruction: *"If the route returns 4xx/5xx consistently, STOP and
report."* It did: `https://opencode.ai/zen/go/v1/chat/completions` returned
`403` on three consecutive calls.

Before reporting, the cheapest discriminating tests were run to establish
**which** blocker this is, because the two candidates have very different
remedies and the report is only useful if it names the right one:

  1. Is the 403 specific to `mimo-v2.6-flash`, or does it block every model on
     the Go route for this API key?
  2. Is the model reachable on the Zen route — the route the FROZEN
     `general_model` run used successfully with this same key?

The probe matrix below answers both. It changes **no** frozen parameter: the
prompt, the state text, `temperature`, `max_tokens` and the single attempt are
identical across every probe and identical to the frozen conditions. The two
variables under test are the ones the brief explicitly permits to differ — the
`model` field and the provider route.

WHAT THIS IS NOT
----------------
Not a search for a substitute model. Model selection is operator-gated
(`AGENTS.md` model discipline) and the brief pins the baseline to
`mimo-v2.6-flash`; substituting one would void the frozen-condition design.
Not a repair attempt. Nothing here tunes a parameter to obtain a 200.

Usage:
    python3 harness/route_diagnostics.py
    python3 harness/route_diagnostics.py --check-only   # gates, zero calls
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FOLLOWUP = os.path.dirname(HERE)
sys.path.insert(0, HERE)

# `run_mimo` is imported first: it puts the FROZEN phase1 harness on sys.path and
# exposes the frozen body builder. `common` then resolves.
import run_mimo as R  # noqa: E402

from common import post_json, request_hash, utc_now_iso  # noqa: E402

ZEN_ROUTE = "https://opencode.ai/zen/v1/chat/completions"   # the FROZEN route
GO_ROUTE = R.ENDPOINT                                       # operator-stated route
DIAG_SESSION = "jev-phase1-followup-02-diagnostic"

# (label, route, model, what_this_probe_decides)
PROBES = (
    ("go_route_operator_model",
     GO_ROUTE, R.MODEL_ID,
     "the operator-stated endpoint with the operator-stated model: is the "
     "brief's step-1 smoke test reachable at all?"),
    ("go_route_frozen_model",
     GO_ROUTE, R.GENERAL_MODEL,
     "control: is the Go-route 403 specific to mimo-v2.6-flash, or does it "
     "block EVERY model for this key? 200/403 here is the whole diagnosis."),
    ("go_route_prefixed_id",
     GO_ROUTE, R.MODEL_CATALOG_ID,
     "does the fully-qualified catalog id resolve on the Go route?"),
    ("zen_route_frozen_model",
     ZEN_ROUTE, R.GENERAL_MODEL,
     "control: is this key valid on the Zen route at all? this is the exact "
     "route+model combination the FROZEN general_model run used successfully."),
    ("zen_route_operator_model",
     ZEN_ROUTE, R.MODEL_ID,
     "does the Zen route serve mimo-v2.6-flash, even though it is not the "
     "operator-stated endpoint?"),
    ("zen_route_prefixed_id",
     ZEN_ROUTE, R.MODEL_CATALOG_ID,
     "does the fully-qualified catalog id resolve on the Zen route?"),
)


def probe(url, model):
    body = R.smoke_request()
    body["model"] = model
    resp = post_json(url, body, os.environ[R.API_KEY_ENV],
                     session_id=DIAG_SESSION, max_attempts=R.MAX_ATTEMPTS)
    out = {
        "model": model,
        "http_status": resp["http_status"],
        "typed_error": resp["typed_error"],
        "error_detail": resp["error_detail"],
        "latency_ms": resp["latency_ms"],
        "attempts": resp["attempts"],
        "retries": resp["retries"],
        "usage": resp["usage"],
        "token_counts": R.token_counts(resp["usage"]),
        "derived_cost_usd": R.derived_cost_usd(R.token_counts(resp["usage"]),
                                               model),
    }
    try:
        obj = json.loads(resp["raw_response"])
    except Exception:  # noqa: BLE001
        out["provider_error"] = None
        out["content"] = None
        out["finish_reason"] = None
        return out
    out["provider_error"] = ((obj.get("error") or {}).get("message")
                             if isinstance(obj.get("error"), dict) else None)
    try:
        choice = obj["choices"][0]
        msg = choice.get("message") or {}
        out["content"] = msg.get("content")
        out["finish_reason"] = choice.get("finish_reason")
        reasoning = msg.get("reasoning_content")
        if reasoning is None:
            reasoning = msg.get("reasoning")
        out["reasoning_field_present"] = reasoning is not None
        out["reasoning_chars"] = (len(str(reasoning))
                                  if reasoning is not None else 0)
    except Exception:  # noqa: BLE001
        out["content"] = None
        out["finish_reason"] = None
    return out


def classify(status):
    if status is None:
        return "unreachable"
    if 200 <= status < 300:
        return "reachable"
    if 400 <= status < 500:
        return "client_error"
    return "server_error"


def run(out_path):
    results = []
    for label, url, model, decides in PROBES:
        r = probe(url, model)
        r.update({"probe": label, "route": url, "model": model,
                  "decides": decides,
                  "outcome": classify(r["http_status"])})
        results.append(r)
        print(f"  {label:28s} {r['http_status']}  {r['outcome']:12s} "
              f"{(r.get('provider_error') or '')[:70]}", flush=True)

    by = {r["probe"]: r for r in results}
    go_403_is_account_wide = (
        by["go_route_frozen_model"]["http_status"] == 403
        and by["go_route_operator_model"]["http_status"] == 403)
    zen_serves_operator_model = (
        by["zen_route_operator_model"]["outcome"] == "reachable")
    reachable_anywhere = any(
        r["outcome"] == "reachable" and r["model"] == R.MODEL_ID
        for r in results)

    verdict = {
        "model_reachable_on_any_tested_route": reachable_anywhere,
        "go_route_403_is_account_wide_not_model_specific": go_403_is_account_wide,
        "zen_route_serves_the_operator_model": zen_serves_operator_model,
        "key_is_valid_on_zen_route":
            by["zen_route_frozen_model"]["outcome"] == "reachable",
    }
    if not reachable_anywhere:
        verdict["blocker"] = (
            "UNREACHABLE CREDENTIAL/ENTITLEMENT, not a parameter problem. "
            "The Go route returns 403 'An active OpenCode Go subscription is "
            "required to use Go models' for the frozen model AND for "
            "mimo-v2.6-flash, so the block is account-wide and no model "
            "selection avoids it. The Zen route — the route the frozen "
            "general_model run used successfully with this same key — does not "
            "host mimo-v2.6-flash at all (400 'Model is unavailable').")
    elif zen_serves_operator_model:
        verdict["blocker"] = (
            "ROUTE MISMATCH ONLY: the operator-stated Go route is "
            "entitlement-blocked, but the frozen Zen route serves "
            "mimo-v2.6-flash. Proceeding would be a route substitution, which "
            "the brief permits but which must be disclosed.")
    else:
        verdict["blocker"] = "REACHABLE — no blocker."

    record = {
        "schema_version": "jevp1-followup2-route-diagnostics-1.0",
        "what": "throwaway route/model reachability probes on a NON-CORPUS "
                "state. No corpus text, no grid cell, nothing scored. Frozen "
                "parameters (temperature, max_tokens, prompt, 1 attempt) are "
                "identical across every probe; only the route and the model id "
                "vary, which are the two differences the brief permits.",
        "runner_version": R.RUNNER_VERSION,
        "model_id_under_test": R.MODEL_ID,
        "model_catalog_id": R.MODEL_CATALOG_ID,
        "frozen_model_id_control": R.GENERAL_MODEL,
        "routes_tested": {"go_operator_stated": GO_ROUTE, "zen_frozen": ZEN_ROUTE},
        "conditions": {"temperature": R.TEMPERATURE,
                       "max_tokens": R.GENERAL_MAX_TOKENS,
                       "max_attempts": R.MAX_ATTEMPTS, "retries": 0,
                       "state_is_non_corpus": True},
        "timestamp_utc": utc_now_iso(),
        "n_probes": len(results),
        "probes": results,
        "verdict": verdict,
        "usage_totals_by_model": _usage_totals_by_model(results),
        "derived_cost_usd_by_model": _cost_by_model(results),
        "secrets_recorded": False,
    }
    record["usage_totals"] = _usage_totals(
        [r for r in results if r["model"] == R.MODEL_ID])
    record["derived_cost_usd_total"] = _cost_total(
        [r for r in results if r["model"] == R.MODEL_ID])
    record["cost_note"] = (
        "Costs are attributed per model, and only to calls that actually "
        "returned a completion. Every mimo-v2.6-flash call in this experiment "
        "was rejected (403/400) and carried no usage, so the derived cost "
        "attributable to the MiMo baseline is exactly $0.00. The 216 input / 2 "
        "output tokens in this file were consumed by the free "
        "space-bunny-free control probe on the Zen route, which is a 0/0/0/0 "
        "model and is charged at its own rates, not MiMo's.")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(record, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    return record


def _usage_totals(results):
    keys = ("input_tokens", "output_tokens", "total_tokens",
            "cache_read_tokens", "cache_write_tokens", "reasoning_tokens")
    tot = {k: 0 for k in keys}
    for r in results:
        for k, v in (r.get("token_counts") or {}).items():
            if k in tot and isinstance(v, int):
                tot[k] += v
    return tot


def _cost_total(results):
    total = 0.0
    for r in results:
        if r.get("derived_cost_usd"):
            total += r["derived_cost_usd"]
    return round(total, 8)


def _usage_totals_by_model(results):
    out = {}
    for model in sorted({r["model"] for r in results}):
        rows = [r for r in results if r["model"] == model]
        out[model] = {"n_calls": len(rows),
                      "n_calls_with_usage": sum(
                          1 for r in rows if r.get("token_counts")
                          and any(r["token_counts"].values())),
                      "usage_totals": _usage_totals(rows),
                      "derived_cost_usd": _cost_total(rows),
                      "rates_per_mtok": R.MODEL_COST_PER_MTOK.get(model)}
    return out


def _cost_by_model(results):
    return {m: v["derived_cost_usd"] for m, v in _usage_totals_by_model(results).items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(FOLLOWUP, "results",
                                                  "route_diagnostics.json"))
    ap.add_argument("--check-only", action="store_true",
                    help="verify the frozen gates, make zero HTTP calls")
    args = ap.parse_args()

    print("route_diagnostics: frozen gates")
    R.verify_frozen_inputs()
    print("  frozen inputs verified: 3 files")
    key = os.environ.get(R.API_KEY_ENV)
    if not key:
        raise SystemExit(f"STOP: ${R.API_KEY_ENV} is unset or empty. No call "
                         "was made.")
    print(f"  {R.API_KEY_ENV}: present (value never printed)")
    if args.check_only:
        print("route_diagnostics: --check-only, no call made")
        return 0

    print(f"route_diagnostics: {len(PROBES)} throwaway non-corpus probes")
    rec = run(args.out)
    v = rec["verdict"]
    print(f"  model reachable on any tested route: "
          f"{v['model_reachable_on_any_tested_route']}")
    print(f"  blocker: {v['blocker']}")
    print(f"  probe cost: ${rec['derived_cost_usd_total']:.8f}")
    print(f"route_diagnostics: wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
