#!/usr/bin/env python3
"""followup-04-jev-direct — Jev over the DIRECT TypeSafe API, compared against
the FROZEN MiMo V2.6 Flash operational measurements of followup-03.

THE QUESTION
------------
At approximately matched semantic capability, does direct Jev materially
improve latency, tail latency, throughput, reliability, probability
availability, or cost relative to MiMo V2.6 Flash? This file answers only the
Jev side. It does NOT produce the consolidated Phase-1 verdict.

WHAT IS NEW HERE (this is a documented change, not an identical rerun)
-------------------------------------------------------------------
followup-03 could not obtain a single usable Jev answer on the route it had:
`jev-1.13-free` over `opencode.ai/zen` returned no usable body, so its Jev
latency, throughput, concurrency and stability cells are recorded as
UNRESOLVED. This run changes the ROUTE and the MODEL TAG:

  * route   POST https://opencode.ai/zen/v1/systemone
         -> POST https://api.typesafe.ai/v1/systemone
  * model   `jev-1.13-free`  ->  `jev-1.13.0`   (pinned, not `jev-latest`)
  * price   free tier ($0)  ->  $0.042 per Mtok input, output free

So every Jev number here is a NEW measurement of a different serving path. It
is NOT a re-measurement of the same path, and it does not retroactively fill
in followup-03's UNRESOLVED cells: those were properties of the free-tier route
and this is a property of the paid direct route. The comparison against MiMo is
therefore explicitly CROSS-WINDOW (MiMo measured ~2026-09-26T13:40Z, Jev-direct
now, same host) and structural/network/pricing differences are kept separate.

REQUEST SEMANTICS
-----------------
For each of the 16 frozen subset cases the request body is the FROZEN phase-1
`results/jev_raw.ndjson` `request_body` VERBATIM, with exactly one field
changed: `model` -> `jev-1.13.0`. `state` and `questions` are byte-identical
to the frozen body. This is asserted per case, not assumed: the body with
`model` normalised away must compare EQUAL to the frozen body with `model`
normalised away, for all 16 cases, or the process exits non-zero before any
call. Request hashes (of the body actually sent) and the frozen hashes are both
recorded.

The response `model` field is recorded on every row and asserted equal to
`jev-1.13.0`.

SCHEDULE (mirrors followup-03 exactly; nothing tuned)
------------------------------------------------------
  * 5 warm-up calls, labelled, DISCARDED from every statistic
  * 16 cases x 12 warm repetitions, SEQUENTIAL, case-major, block `direct1`
  * >= 120 s idle, then 3 calls labelled `idle` (an observable idle-gap PROXY
    only; per-call cold start is not observable on a shared stateless HTTPS
    endpoint and is not claimed)
  * a fixed 6-case x 2-repetition block at C = 1, 4, 8 as parallel curl
    processes with a REAL in-flight limit
  * ONE labelled interface probe: a single call mixing noul + choice + score
    under distinct question keys, to test whether the direct route accepts and
    answers multiple named questions. Outside the grid; its latency and cost
    are in no grid statistic.

N = 1 ATTEMPT, NO RETRIES
-------------------------
Every call is exactly one HTTP request at every concurrency level. There is no
retry path in the call path: a failed call is recorded with its typed error and
never re-sent. A retry on exactly the cells that failed would convert an N=1
observation into a survivorship-biased N>1 one.

CREDENTIALS
-----------
Read at RUNTIME from `~/.secrets/typesafe.env` (format
`export TYPESAFE_API_KEY=...`); a non-login process does not inherit it. The
value is held in memory and handed to curl on STDIN via `curl -K -`, so it
appears in neither argv (where `/proc/*/cmdline` and shell history expose it)
nor any file. ONLY THE SOURCE LABEL `secrets/typesafe.env#TYPESAFE_API_KEY` is
ever written to an artefact. The value is never printed, logged, persisted,
committed, or interpolated into an error message.

FROZEN-CONDITION GATE
---------------------
No grid call is made unless ALL of the following hold, or the process exits
non-zero without touching the network:
  * both frozen input digests match;
  * the 16 subset case ids are re-derived from the frozen `cases.ndjson` by
    followup-03's own `select_subset` rule and match the stored `subset.json`
    (imported, not re-implemented, so the subset is identical by construction);
  * every subset request body equals its frozen body after `model`
    normalisation, and `state`/`questions` are byte-identical;
  * the F1 correction is derivable from `control.pair_id` and names exactly the
    ids `verification.md` §2 F1 names (delegated to followup-03's function);
  * the frozen answer normaliser agrees with the frozen `common.parse_jev` on
    all 64 frozen rows (the generaliser is proved against the frozen parser,
    not trusted);
  * the credential source resolves.

Usage:
    python3 harness/run_ops_jev_direct.py gate
    python3 harness/run_ops_jev_direct.py route
    python3 harness/run_ops_jev_direct.py warm
    python3 harness/run_ops_jev_direct.py idle
    python3 harness/run_ops_jev_direct.py concurrency
    python3 harness/run_ops_jev_direct.py probe
    python3 harness/run_ops_jev_direct.py equivalence
    python3 harness/run_ops_jev_direct.py summary
    python3 harness/run_ops_jev_direct.py check
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
FOLLOWUP = os.path.dirname(HERE)
PHASE1 = os.path.dirname(FOLLOWUP)
PHASE1_HARNESS = os.path.join(PHASE1, "harness")
FU03 = os.path.join(PHASE1, "followup-03-operational")
FU03_HARNESS = os.path.join(FU03, "harness")

for _p in (FU03_HARNESS, PHASE1_HARNESS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Frozen builders, parsers, constants and the subset rule are IMPORTED from the
# frozen harnesses. Re-typing a frozen constant is how a "frozen" run silently
# stops being frozen.
from common import (  # noqa: E402
    ERR_INTERNAL,
    ERR_NETWORK,
    ERR_TIMEOUT,
    TIMEOUT_SECONDS,
    USER_AGENT,
    _extract_usage,
    classify,
    load_cases,
    parse_jev,
    request_hash,
    serialise,
    utc_now_iso,
)
import run_ops as FU03_OPS  # noqa: E402  select_subset, f1_corrected_cases, Appender
import analyze_ops as FU03_A  # noqa: E402  describe, usable, curl_ms, correctness

RUNNER_VERSION = "1.0.0"
MECH = "jev_direct"
MODEL = "jev-1.13.0"
ENDPOINT = "https://api.typesafe.ai/v1/systemone"
SESSION_HEADER_VALUE = "jev-phase1-run"

# --- published facts, documented 2026-09-26, NOT used to support any latency
# --- or throughput claim. Kept strictly separate from every measurement.
TS_COST_PER_MTOK = {"input": 0.042, "output": 0.0, "cache_read": 0.0,
                    "cache_write": 0.0}
PUBLISHED_RATES = {
    "source": "docs published 2026-09-26",
    "input_usd_per_mtok": 0.042,
    "output_usd_per_mtok": 0.0,
    "rate_limit_tokens_per_sec": 250000,
    "rate_limit_requests_per_min": 1200,
    "http_429_when": "rate limit exceeded",
    "http_529_when": "service overloaded",
    "context_window_tokens": 64000,
}

# --- credentials
SECRETS_PATH = "~/.secrets/typesafe.env"
SECRET_KEY_NAME = "TYPESAFE_API_KEY"
CRED_LABEL = "secrets/typesafe.env#TYPESAFE_API_KEY"

# --- frozen inputs
FROZEN_INPUTS = {
    "cases.ndjson":
        "7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c",
    "results/jev_raw.ndjson":
        "e17ae014f0fc6cc311646dbfd98d5115d41854ddfcb98cfb41268f2da482d3bc",
}
FROZEN_SUBSET_SHA256 = ("58b855acefbd7cda2c35ad39988c930acf39d54ec658d88a62b"
                        "04585bc71b8d3")
FROZEN_MIMO_RAW_SHA256 = (
    "40dbc56329dd2d5112cd92a14e9dddf7c5384356feaadd17"
    "0e2b8ac575827cd8")

# --- design constants, fixed before measuring, mirroring followup-03
SUBSET_N = 16
WARM_REPS = 12
WARMUP_CALLS = 5
IDLE_SECONDS = 120
IDLE_CALLS = 3
CONC_CASES = 6
CONC_REPS = 2
CONC_LEVELS = (1, 4, 8)
ROUTE_PROBE_CALLS = 1
MAX_ATTEMPTS = 1
RETRIES = 0
BLOCK = "direct1"

RAW_PATH = os.path.join(FOLLOWUP, "results", "jev_direct_raw.ndjson")
EQUIV_PATH = os.path.join(FOLLOWUP, "results", "equivalence.json")
SUMMARY_PATH = os.path.join(FOLLOWUP, "results", "summary.json")

CURL_WRITE_OUT = "\n__OPS__%{json}"
HEADER_SET = [
    "Content-Type: application/json",
    "User-Agent: %s" % USER_AGENT,
    "x-opencode-session: %s" % SESSION_HEADER_VALUE,
]


# ===========================================================================
# small helpers
# ===========================================================================
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_ndjson(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path, doc):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False, sort_keys=False)
        f.write("\n")


# ===========================================================================
# credentials — resolved at runtime, never printed, never stored
# ===========================================================================
def resolve_credential():
    """The credential value, or None when the source is absent/unreadable.

    The VALUE is returned to the caller and to nothing else. No caller writes
    it to an artefact, and no error message interpolates it.
    """
    path = os.path.expanduser(SECRETS_PATH)
    try:
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read()
    except OSError:
        return None
    m = re.search(r"^\s*(?:export\s+)?%s\s*=\s*(.*)$" % SECRET_KEY_NAME, txt,
                  re.M)
    if not m:
        return None
    v = m.group(1).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        v = v[1:-1]
    return v or None


# ===========================================================================
# frozen answer normaliser — a GENERALISATION of the frozen parser, proved
# against it before use
# ===========================================================================
def normalise_answer(answer_obj, question, label_map):
    """Normalise one `systemone` answer object to (parsed, prediction, error).

    This is `common.parse_jev`'s body with the case replaced by its single
    question object, so the same call can be applied to a multi-question
    response. It is NOT a re-implementation from memory: `frozen_gate` checks
    it against the frozen `parse_jev` on all 64 frozen rows and refuses to
    proceed on any disagreement.
    """
    from common import (ERR_PARSE, confidence_formula)

    qtype = question["type"]
    parsed = {
        "type": answer_obj.get("type"),
        "noul": answer_obj.get("noul"),
        "choice": answer_obj.get("choice"),
        "score": answer_obj.get("score"),
        "confidence": answer_obj.get("confidence"),
        "legend": answer_obj.get("legend"),
        "probabilities_raw": answer_obj.get("probabilities"),
    }
    if not isinstance(answer_obj, dict) or answer_obj.get("type") != qtype:
        return parsed, None, ERR_PARSE

    if qtype == "noul":
        noul = answer_obj.get("noul")
        if not isinstance(noul, (int, float)) or isinstance(noul, bool):
            return parsed, None, ERR_PARSE
        probs = {"yes": float(noul), "no": 1.0 - float(noul)}
        label = "yes" if noul >= 0.5 else "no"
        score_val = None
    elif qtype == "choice":
        praw = answer_obj.get("probabilities")
        if not isinstance(praw, dict) or not praw:
            return parsed, None, ERR_PARSE
        probs = {}
        for k, v in praw.items():
            try:
                fv = float(v)
            except (TypeError, ValueError):
                return parsed, None, ERR_PARSE
            probs[label_map.get(k, k)] = fv
        label = label_map.get(answer_obj.get("choice"),
                              answer_obj.get("choice"))
        score_val = None
        if label not in probs and probs:
            label = max(probs.items(), key=lambda kv: (kv[1], kv[0]))[0]
    else:
        praw = answer_obj.get("probabilities")
        legend = answer_obj.get("legend") or {}
        if not isinstance(praw, dict) or not praw:
            return parsed, None, ERR_PARSE
        probs = {}
        for k, v in praw.items():
            try:
                fv = float(v)
            except (TypeError, ValueError):
                return parsed, None, ERR_PARSE
            name = legend.get(k, legend.get(str(k)))
            if name is None:
                crit = question["criteria"]
                try:
                    name = crit[int(k)]
                except (ValueError, IndexError, TypeError):
                    return parsed, None, ERR_PARSE
            probs[name] = fv
        score_val = answer_obj.get("score")
        label = (max(probs.items(), key=lambda kv: (kv[1], kv[0]))[0]
                 if probs else None)

    total = sum(probs.values())
    prediction = {
        "label": label,
        "probabilities": probs,
        "score": score_val,
        "max_prob": (max(probs.values()) if probs else None),
        "confidence_reported": answer_obj.get("confidence"),
        "confidence_formula": confidence_formula(probs),
        "normalised": bool(abs(total - 1.0) > 0.02) if probs else None,
        "prob_sum": round(total, 6) if probs else None,
    }
    return parsed, prediction, None


def parse_multi(raw, questions, label_maps):
    """Parse a response whose `questions` carried more than one named key.

    Returns (per_key, typed_error). `per_key` maps question key ->
    (parsed, prediction). Any per-question error is reported per key so one
    bad answer does not hide the others; the row-level typed_error is set only
    when NO question produced a usable answer.
    """
    from common import ERR_PARSE

    try:
        obj = json.loads(raw)
    except Exception:  # noqa: BLE001
        return {}, ERR_PARSE
    answers = obj.get("answers")
    if not isinstance(answers, dict) or not answers:
        return {}, ERR_PARSE
    per_key, any_ok = {}, False
    for key, question in questions.items():
        a = answers.get(key)
        if not isinstance(a, dict):
            per_key[key] = (None, None, ERR_PARSE)
            continue
        parsed, prediction, err = normalise_answer(
            a, question, label_maps.get(key) or {})
        per_key[key] = (parsed, prediction, err)
        if err is None and prediction is not None:
            any_ok = True
    return per_key, (None if any_ok else ERR_PARSE)


# ===========================================================================
# FROZEN-CONDITION GATE
# ===========================================================================
def build_bodies(cases_by_id, subset_ids):
    """The per-case direct body + the per-case frozen-equality proof.

    Body = the FROZEN phase-1 `request_body` verbatim with ONLY `model`
    replaced. Returns (bodies, proofs). `proofs[i]['equal_after_model_
    normalisation']` is the assertion the gate requires.
    """
    frozen_rows = {r["case_id"]: r for r in load_ndjson(
        os.path.join(PHASE1, "results", "jev_raw.ndjson"))}
    bodies, proofs = {}, {}
    for cid in subset_ids:
        row = frozen_rows.get(cid)
        if row is None:
            raise SystemExit(
                f"FROZEN BODY GATE FAILED: no frozen jev_raw row for {cid}.")
        frozen_body = row["request_body"]
        body = copy.deepcopy(frozen_body)
        body["model"] = MODEL
        # strip `model` from both and compare what is left: `state` and
        # `questions` must be byte-identical.
        f_minus = {k: v for k, v in frozen_body.items() if k != "model"}
        b_minus = {k: v for k, v in body.items() if k != "model"}
        equal_norm = (f_minus == b_minus)
        state_identical = (frozen_body.get("state") == body.get("state"))
        q_identical = (frozen_body.get("questions") == body.get("questions"))
        sent = serialise(body)
        bodies[cid] = body
        proofs[cid] = {
            "case_id": cid,
            "frozen_model": frozen_body.get("model"),
            "direct_model": body.get("model"),
            "fields_changed": ["model"],
            "frozen_field_names": sorted(frozen_body.keys()),
            "direct_field_names": sorted(body.keys()),
            "state_byte_identical": state_identical,
            "questions_byte_identical": q_identical,
            "equal_after_model_normalisation": equal_norm,
            "frozen_request_hash": row.get("request_hash"),
            "direct_request_hash": request_hash(body),
            "direct_serialised_sha256": sha256_text(sent),
            "frozen_serialised_sha256": sha256_text(serialise(frozen_body)),
            "direct_serialised_bytes": len(sent.encode("utf-8")),
            "request_hash_differs_only_by_model": (
                row.get("request_hash") != request_hash(body)),
        }
    return bodies, proofs


def frozen_gate():
    """Every frozen condition, verified. SystemExit on any drift."""
    report = {"digests": {}, "request_gate": None, "normaliser_gate": None,
              "f1": {}, "subset": {}, "credential": {}}

    for rel, expect in FROZEN_INPUTS.items():
        path = os.path.join(PHASE1, rel)
        got = sha256_file(path)
        if got != expect:
            raise SystemExit(
                f"FROZEN INPUT MISMATCH {rel}: expected {expect}, found {got}. "
                "Refusing to make any call.")
        report["digests"][rel] = {"expected": expect, "actual": got,
                                   "match": True}

    # the two followup-03 artefacts this run reads (read-only, never written)
    fu_subset = os.path.join(FU03, "subset.json")
    fu_raw = os.path.join(FU03, "results", "mimo_ops_raw.ndjson")
    for path, expect in ((fu_subset, FROZEN_SUBSET_SHA256),
                         (fu_raw, FROZEN_MIMO_RAW_SHA256)):
        got = sha256_file(path)
        if got != expect:
            raise SystemExit(
                f"FROZEN FOLLOWUP-03 INPUT MISMATCH {path}: expected {expect}, "
                f"found {got}. Refusing to build any comparison.")
    report["digests"]["followup-03/subset.json"] = {
        "expected": FROZEN_SUBSET_SHA256,
        "actual": sha256_file(fu_subset), "match": True, "read_only": True}
    report["digests"]["followup-03/results/mimo_ops_raw.ndjson"] = {
        "expected": FROZEN_MIMO_RAW_SHA256,
        "actual": sha256_file(fu_raw), "match": True, "read_only": True}

    cases = load_cases(os.path.join(PHASE1, "cases.ndjson"))
    by_id = {c["id"]: c for c in cases}

    # the subset is re-derived by followup-03's OWN rule, so it is identical by
    # construction rather than by transcription
    ordered, _trace = FU03_OPS.select_subset(cases)
    stored = load_json(fu_subset)
    if stored.get("case_ids_in_selection_order") != ordered:
        raise SystemExit(
            "SUBSET DRIFT: followup-03's stored subset.json id list is not what "
            "its own rule produces from the current frozen cases.ndjson.")
    if len(ordered) != SUBSET_N:
        raise SystemExit(f"SUBSET SIZE DRIFT: {len(ordered)} != {SUBSET_N}.")
    report["subset"] = {
        "rule": FU03_OPS.SUBSET_RULE["id"],
        "rule_source": "followup-03-operational/harness/run_ops.py "
                       "select_subset (imported, not re-implemented)",
        "re_derived_matches_stored_subset_json": True,
        "n": len(ordered),
        "case_ids_canonical_order": sorted(ordered),
    }

    bodies, proofs = build_bodies(by_id, ordered)
    bad = [p["case_id"] for p in proofs.values()
           if not (p["equal_after_model_normalisation"]
                   and p["state_byte_identical"]
                   and p["questions_byte_identical"])]
    if bad:
        raise SystemExit(
            f"FROZEN REQUEST GATE FAILED for {bad}: the direct body is not the "
            "frozen body with only `model` changed. Refusing to make any call.")
    report["request_gate"] = {
        "n_cases": len(proofs),
        "n_equal_after_model_normalisation": sum(
            1 for p in proofs.values()
            if p["equal_after_model_normalisation"]),
        "n_state_byte_identical": sum(1 for p in proofs.values()
                                      if p["state_byte_identical"]),
        "n_questions_byte_identical": sum(1 for p in proofs.values()
                                          if p["questions_byte_identical"]),
        "body_source": "phase-1 results/jev_raw.ndjson request_body, verbatim",
        "only_field_changed": "model",
        "model_from": sorted({p["frozen_model"] for p in proofs.values()}),
        "model_to": MODEL,
        "per_case": proofs,
    }

    # the generaliser must agree with the frozen parser on all 64 frozen rows
    n_ok, first_bad = 0, None
    for r in load_ndjson(os.path.join(PHASE1, "results", "jev_raw.ndjson")):
        case = by_id[r["case_id"]]
        frozen_parsed, frozen_pred, frozen_err = parse_jev(
            r["raw_response"], case)
        try:
            obj = json.loads(r["raw_response"])
            a = (obj.get("answers") or {}).get("q")
        except Exception:  # noqa: BLE001
            a = None
        if not isinstance(a, dict):
            g_parsed = g_pred = g_err = None
            g_err = frozen_err
        else:
            g_parsed, g_pred, g_err = normalise_answer(
                a, case["questions"][0],
                case["control"].get("label_map") or {})
        if (g_err == frozen_err and g_pred == frozen_pred
                and g_parsed == frozen_parsed):
            n_ok += 1
        elif first_bad is None:
            first_bad = r["case_id"]
    if n_ok != 64:
        raise SystemExit(
            f"NORMALISER GATE FAILED: the local generaliser reproduces "
            f"common.parse_jev on {n_ok}/64 frozen rows (first divergent "
            f"{first_bad}). Refusing to parse any new response with it.")
    report["normaliser_gate"] = {
        "n_frozen_rows": 64,
        "n_agreeing_with_frozen_parse_jev": n_ok,
        "why": "the mixed-question interface probe needs a generaliser; it is "
               "proved equivalent to the frozen single-question parser before "
               "it is trusted on any new response",
    }

    _, f1_ids = FU03_OPS.f1_corrected_cases(cases)
    report["f1"] = {
        "pair_id": FU03_OPS.F1_PAIR_ID,
        "case_ids": f1_ids,
        "source": "verification.md §2 F1",
        "derivation": "delegated to followup-03's f1_corrected_cases, which "
                      "derives the pair from control.pair_id and hard-stops if "
                      "it is not the pair verification.md names",
        "members_in_subset": sorted(set(f1_ids) & set(ordered)),
    }

    key = resolve_credential()
    report["credential"] = {
        "source_label": CRED_LABEL,
        "path": SECRETS_PATH,
        "variable": SECRET_KEY_NAME,
        "resolvable": bool(key),
        "length": len(key) if key else 0,
        "value_recorded": False,
        "value_ever_printed": False,
        "handed_to_curl_via": "stdin (`curl --config -`), never argv, never a "
                              "file, never an environment export",
    }
    if not key:
        raise SystemExit(
            f"FATAL: credential source {CRED_LABEL} does not resolve at "
            f"{SECRETS_PATH}. This harness never shops for a credential that "
            "happens to work.")
    return report, cases, ordered, bodies


# ===========================================================================
# transport — curl, one process per call, no connection reuse
# ===========================================================================
def curl_config(key):
    return 'header = "Authorization: Bearer %s"\n' % key


def curl_argv(body, connect_only=False):
    args = ["curl", "--silent", "--show-error", "--config", "-",
            "--max-time", str(TIMEOUT_SECONDS), "--write-out", CURL_WRITE_OUT]
    if connect_only:
        args += ["--head", "--output", os.devnull, ENDPOINT]
    else:
        for h in HEADER_SET:
            args += ["--header", h]
        args += ["--data-binary", serialise(body), ENDPOINT]
    return args


def parse_curl_stdout(out, rc, errout, connect_only=False):
    """(timings, http_status, bytes, raw_body, typed_error, detail)."""
    stdout = out or ""
    marker = "\n__OPS__"
    if marker not in stdout:
        return (None, None, 0, stdout,
                ERR_TIMEOUT if rc == 28 else ERR_NETWORK,
                (f"curl rc={rc} {(errout or '').strip()}")[:200])
    body_txt, _, meta = stdout.rpartition(marker)
    try:
        timings = json.loads(meta)
    except ValueError:
        return None, None, 0, body_txt, ERR_INTERNAL, "unparseable write-out"
    try:
        status = int(timings.get("http_code"))
    except (TypeError, ValueError):
        return None, None, 0, body_txt, ERR_INTERNAL, "no http_code"
    if connect_only:
        return timings, status, timings.get("size_download"), "", None, None
    raw = body_txt.rstrip("\n")
    code = classify(status)
    return (timings, status, timings.get("size_download"), raw, code,
            None if code is None else f"HTTP {status}")


def call_curl(body, key, connect_only=False):
    """One curl process, one HTTP request. Never raises."""
    if any(ch in key for ch in ('"', "\\", "\n", "\r")):
        return {"timings": None, "http_status": None, "raw_response": "",
                "typed_error": ERR_INTERNAL, "bytes": 0,
                "error_detail": "credential is not expressible in a curl config"}
    try:
        proc = subprocess.run(curl_argv(body, connect_only), input=curl_config(key),
                              capture_output=True, text=True)
    except Exception as e:  # noqa: BLE001 - the grid must stay complete
        return {"timings": None, "http_status": None, "raw_response": "",
                "typed_error": ERR_INTERNAL, "bytes": 0,
                "error_detail": f"{type(e).__name__}: {e}"[:200]}
    t, status, nbytes, raw, err, detail = parse_curl_stdout(
        proc.stdout, proc.returncode, proc.stderr, connect_only)
    return {"timings": t, "http_status": status, "bytes": nbytes,
            "raw_response": raw, "typed_error": err, "error_detail": detail}


# ===========================================================================
# token + cost accounting
# ===========================================================================
def token_counts(usage):
    return FU03_OPS.token_counts(usage)


def derived_cost_usd(counts):
    """USD from `input_tokens` x $0.042/Mtok. Output is free on this route."""
    if not counts:
        return None
    return round(counts.get("input_tokens", 0) / 1_000_000.0
                 * TS_COST_PER_MTOK["input"], 10)


# ===========================================================================
# row construction
# ===========================================================================
def response_model_field(raw):
    try:
        obj = json.loads(raw)
    except Exception:  # noqa: BLE001
        return None
    if not isinstance(obj, dict):
        return None
    m = obj.get("model")
    return m if isinstance(m, str) else None


def base_row(case, phase, repeat, concurrency=1, block=BLOCK, probe=None,
             body=None):
    return {
        "schema_version": "jevp1-jevdirect-result-1.0",
        "mechanism": MECH,
        "model_id": MODEL,
        "model_pinned": MODEL,
        "family": "jev",
        "route": "direct-typesafe-api",
        "endpoint": ENDPOINT,
        "case_id": case["id"] if case else None,
        "area": case["area"] if case else None,
        "question_type": (case["questions"][0]["type"] if case else None),
        "answerable_frozen": (case["ground_truth"]["answerable"] if case
                              else None),
        "control_variant_kind": (case["control"]["variant_kind"] if case
                                 else None),
        "phase": phase,
        "repeat": repeat,
        "concurrency": concurrency,
        "block": block,
        "probe": probe,
        "attempts": MAX_ATTEMPTS,
        "retries": RETRIES,
        "timestamp_utc": utc_now_iso(),
        "credential_source": CRED_LABEL,
        "secrets_recorded": False,
        "transport": {
            "client": "curl",
            "one_process_per_call": True,
            "connection_reuse": False,
            "curl_write_out": "%{json} (phase timings + num_connects)",
            "timeout_seconds": TIMEOUT_SECONDS,
            "header_set": list(HEADER_SET),
            "header_note": "the same header set the frozen Jev run sent is "
                           "retained for request fidelity; "
                           "`x-opencode-session` is a provider grouping header "
                           "whose meaning on this host is not established and "
                           "which is not a credential",
            "credential_channel": "curl --config - (stdin)",
        },
        "harness_version": RUNNER_VERSION,
    }


def run_one(case, key, phase, repeat, concurrency=1, block=BLOCK, probe=None,
            body=None, questions=None, label_maps=None):
    """One call, one row. The ONLY place a grid HTTP request is issued."""
    row = base_row(case, phase, repeat, concurrency, block, probe, body)
    t0 = time.monotonic()
    resp = call_curl(body, key)
    row["wall_ms_including_process_spawn"] = round(
        (time.monotonic() - t0) * 1000.0, 1)
    tm = resp["timings"] or {}
    row["curl_phases"] = {
        "time_namelookup": tm.get("time_namelookup"),
        "time_connect": tm.get("time_connect"),
        "time_appconnect": tm.get("time_appconnect"),
        "time_pretransfer": tm.get("time_pretransfer"),
        "time_starttransfer": tm.get("time_starttransfer"),
        "time_total": tm.get("time_total"),
        "num_connects": tm.get("num_connects"),
        "time_redirect": tm.get("time_redirect"),
    }
    row["http_status"] = resp["http_status"]
    row["bytes"] = resp["bytes"]
    row["raw_response"] = resp["raw_response"]
    row["typed_error"] = resp["typed_error"]
    row["error_detail"] = resp["error_detail"]
    row["request_hash"] = request_hash(body) if body is not None else None
    row["request_fields"] = sorted(body.keys()) if body is not None else None
    row["response_model_field"] = response_model_field(resp["raw_response"])
    row["response_model_matches_pin"] = (
        row["response_model_field"] == MODEL
        if row["response_model_field"] is not None else None)

    if resp["typed_error"] is None and resp["raw_response"]:
        usage = _extract_usage(resp["raw_response"])
        counts = token_counts(usage)
        row["usage"] = usage
        row["usage_flat"] = counts
        row["derived_cost_usd"] = derived_cost_usd(counts)
        if questions and len(questions) > 1:
            per_key, err = parse_multi(resp["raw_response"], questions,
                                       label_maps or {})
            row["parsed_multi"] = {
                k: {"parsed": v[0], "prediction": v[1], "error": v[2]}
                for k, v in per_key.items()}
            row["typed_error"] = err
            if err is not None:
                row["error_detail"] = "200 OK but no usable answer in any key"
            usable_pred = [v[1] for v in per_key.values() if v[1] is not None]
            p0 = usable_pred[0] if usable_pred else None
            row["parsed"] = per_key.get("q", (None, None, None))[0]
            row["prediction"] = p0
            row["parsed_label"] = (p0 or {}).get("label")
            row["parsed_probabilities"] = (p0 or {}).get("probabilities")
            row["parsed_max_prob"] = (p0 or {}).get("max_prob")
            row["parsed_score"] = (p0 or {}).get("score")
        else:
            row["parsed_multi"] = None
            parsed, prediction, perr = parse_jev(resp["raw_response"], case)
            row["parsed"] = parsed
            row["prediction"] = prediction
            if perr is not None:
                row["typed_error"] = perr
                row["error_detail"] = "200 OK but unusable answer"
            row["parsed_label"] = (prediction or {}).get("label")
            row["parsed_probabilities"] = (prediction or {}).get("probabilities")
            row["parsed_max_prob"] = (prediction or {}).get("max_prob")
            row["parsed_score"] = (prediction or {}).get("score")
    else:
        row["usage"] = row["usage_flat"] = row["derived_cost_usd"] = None
        row["parsed"] = row["parsed_multi"] = row["prediction"] = None
        row["parsed_label"] = row["parsed_probabilities"] = None
        row["parsed_max_prob"] = row["parsed_score"] = None
    return row


def open_appender():
    os.makedirs(os.path.dirname(RAW_PATH), exist_ok=True)
    seen = {FU03_OPS.call_key(r) for r in load_ndjson(RAW_PATH)}
    return FU03_OPS.Appender(RAW_PATH, seen), RAW_PATH


# ===========================================================================
# modes
# ===========================================================================
def cmd_gate(args):
    report, cases, ordered, bodies = frozen_gate()
    key = resolve_credential()
    print("FROZEN-CONDITION GATE: all conditions verified")
    for rel, d in report["digests"].items():
        print(f"  {rel:52s} {d['actual'][:16]}... MATCH")
    rg = report["request_gate"]
    print(f"  request gate: {rg['n_equal_after_model_normalisation']}/"
          f"{rg['n_cases']} bodies equal to frozen after model normalisation "
          f"({rg['model_from'][0]} -> {rg['model_to']})")
    print(f"  normaliser gate: reproduces frozen parse_jev on "
          f"{report['normaliser_gate']['n_agreeing_with_frozen_parse_jev']}/64 "
          f"frozen rows")
    print(f"  subset: {report['subset']['n']} cases, rule "
          f"{report['subset']['rule']}, re-derived == stored")
    print(f"  F1 correction: pair {report['f1']['pair_id']} "
          f"{report['f1']['case_ids']} (no subset member: "
          f"{not report['f1']['members_in_subset']})")
    print(f"  credential: {CRED_LABEL} resolvable="
          f"{report['credential']['resolvable']} (value never printed)")
    print(f"  endpoint: POST {ENDPOINT}   model pinned: {MODEL}")
    print(f"  planned calls: {plan_call_count(ordered)}")
    return 0


def plan_call_count(ordered):
    return (ROUTE_PROBE_CALLS + WARMUP_CALLS + len(ordered) * WARM_REPS
            + IDLE_CALLS + len(CONC_LEVELS) * CONC_CASES * CONC_REPS + 1)


def cmd_route(args):
    """ROUTE PRE-FLIGHT — one labelled call establishing that the new route and
    the pinned model actually answer. Recorded as its own phase and excluded
    from every grid statistic."""
    report, cases, ordered, bodies = frozen_gate()
    key = resolve_credential()
    app, path = open_appender()
    by_id = {c["id"]: c for c in cases}
    cid = ordered[0]
    row = run_one(by_id[cid], key, "route_probe", 1, probe="route_preflight",
                  body=bodies[cid])
    row["excluded_from_statistics"] = True
    row["route_probe_note"] = (
        "Establishes the route change is real: POST to the direct endpoint with "
        "the pinned model returns 200 and an answer, and the response `model` "
        "field is compared against the pin. Not a measurement of latency, "
        "throughput or cost; excluded from every grid statistic.")
    if app.write(row):
        print(f"route: HTTP {row['http_status']} "
              f"response_model={row['response_model_field']!r} "
              f"matches_pin={row['response_model_matches_pin']} "
              f"label={row['parsed_label']!r} "
              f"total={row['curl_phases'].get('time_total')} "
              f"err={row['typed_error'] or '-'}")
        print(f"route: -> {path}")
    else:
        print("route: already recorded; skipping.")
    return 0


def cmd_warm(args):
    """Warm-up (discarded) then the warm grid, case-major, sequential."""
    report, cases, ordered, bodies = frozen_gate()
    key = resolve_credential()
    app, path = open_appender()
    by_id = {c["id"]: c for c in cases}

    if args.reps < 1 or args.reps > WARM_REPS:
        raise SystemExit(
            f"REFUSING --reps {args.reps}: the frozen design is {WARM_REPS} warm "
            "repetitions per case. Not a tunable.")
    if args.interval < 0:
        raise SystemExit(f"REFUSING --interval {args.interval}: negative.")
    if args.reps < WARM_REPS or args.interval > 0:
        print(f"warm: REDUCED/PACED block by request: reps={args.reps} (design "
              f"{WARM_REPS}), interval={args.interval}s (design 0.0). Rows are "
              f"labelled and are NOT comparable to the unpaced sequential "
              f"throughput figure.", flush=True)

    plan = []
    if not args.skip_warmup:
        plan += [("warmup", i, ordered[i - 1]) for i in range(1, WARMUP_CALLS + 1)]
    for cid in ordered:
        plan += [("warm", rep, cid) for rep in range(1, args.reps + 1)]

    n_written, n_err = 0, 0
    for phase, repeat, cid in plan:
        row = run_one(by_id[cid], key, phase, repeat, concurrency=1,
                      body=bodies[cid])
        row["paced_interval_seconds"] = args.interval
        row["reduced_reps"] = (args.reps != WARM_REPS)
        if phase == "warmup":
            row["excluded_from_statistics"] = True
            row["warmup_note"] = "discarded warm-up call; retained for audit only"
        if app.write(row):
            n_written += 1
            if row["typed_error"]:
                n_err += 1
                print(f"  ! {phase} {cid} rep={repeat} err={row['typed_error']} "
                      f"{row['error_detail'] or ''}", flush=True)
            if n_written % 25 == 0:
                print(f"  warm {n_written} new calls, errors={n_err}", flush=True)
    print(f"warm: wrote {n_written} new rows to {path} (errors={n_err})")
    return 0


def cmd_idle(args):
    """After >= IDLE_SECONDS of idleness, the next IDLE_CALLS calls."""
    report, cases, ordered, bodies = frozen_gate()
    key = resolve_credential()
    app, path = open_appender()
    if any(r.get("phase") == "idle" for r in load_ndjson(path)):
        print("idle: idle rows already recorded; refusing to double the probe.")
        return 0
    print(f"idle: idling {IDLE_SECONDS}s before the probe (no calls in this "
          f"window by design).", flush=True)
    time.sleep(IDLE_SECONDS)
    by_id = {c["id"]: c for c in cases}
    n = 0
    for i in range(1, IDLE_CALLS + 1):
        cid = ordered[i - 1]
        row = run_one(by_id[cid], key, "idle", i, concurrency=1,
                      body=bodies[cid])
        row["idle_seconds_before"] = IDLE_SECONDS
        row["idle_proxy_note"] = (
            "An IDLE-GAP PROXY only. Per-call cold start is not observable on a "
            "shared stateless HTTPS endpoint; this does not claim to observe it.")
        if app.write(row):
            n += 1
            print(f"  idle {cid} total={row['curl_phases'].get('time_total')} "
                  f"err={row['typed_error'] or '-'}", flush=True)
    print(f"idle: wrote {n} rows after {IDLE_SECONDS}s idle")
    return 0


def cmd_concurrency(args):
    """Fixed block of CONC_CASES x CONC_REPS at C = 1, 4, 8, as parallel curl
    processes with a REAL in-flight limit (at most C exist at any instant)."""
    report, cases, ordered, bodies = frozen_gate()
    key = resolve_credential()
    app, path = open_appender()
    by_id = {c["id"]: c for c in cases}
    block_cases = sorted(ordered)[:CONC_CASES]
    cfg = curl_config(key)
    existing = {(r.get("block"), r.get("concurrency"), r.get("case_id"),
                 r.get("repeat"))
                for r in load_ndjson(path) if r.get("phase") == "concurrency"}

    for c in CONC_LEVELS:
        jobs = [(cid, rep) for cid in block_cases
                for rep in range(1, CONC_REPS + 1)]
        todo = [j for j in jobs if (BLOCK, c, j[0], j[1]) not in existing]
        if not todo:
            print(f"concurrency: C={c} already fully recorded; skipping.")
            continue
        rows, running, t0 = [], [], time.monotonic()
        queue = list(todo)
        while queue or running:
            while queue and len(running) < c:
                cid, rep = queue.pop(0)
                p = subprocess.Popen(curl_argv(bodies[cid]),
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True)
                running.append((p, cid, rep))
            p, cid, rep = running.pop(0)
            out, errout = p.communicate(input=cfg)
            rows.append((cid, rep, out, errout, p.returncode))
        makespan = round((time.monotonic() - t0) * 1000.0, 1)
        n_429 = n_529 = n_err = n_2xx = 0
        for cid, rep, out, errout, rc in rows:
            row = row_from_finished_curl(
                by_id[cid], bodies[cid], out, errout, rc, c, rep, makespan)
            if row["http_status"] == 429:
                n_429 += 1
            if row["http_status"] == 529:
                n_529 += 1
            if row["http_status"] and 200 <= row["http_status"] < 300:
                n_2xx += 1
            if row["typed_error"]:
                n_err += 1
            app.write(row)
        print(f"concurrency: C={c} calls={len(rows)} makespan_ms={makespan} "
              f"2xx={n_2xx} http429={n_429} http529={n_529} errors={n_err}",
              flush=True)
    return 0


def row_from_finished_curl(case, body, out, errout, rc, concurrency, repeat,
                           makespan):
    """Rebuild a row from an already-finished parallel curl process."""
    row = base_row(case, "concurrency", repeat, concurrency)
    row["probe"] = None
    row["block_makespan_ms"] = makespan
    t, status, nbytes, raw, err, detail = parse_curl_stdout(out, rc, errout)
    if t is None:
        row["typed_error"] = err
        row["error_detail"] = detail
        row["http_status"] = None
        row["curl_phases"] = {}
        row["bytes"] = None
        row["raw_response"] = raw or ""
        row["usage"] = row["usage_flat"] = row["derived_cost_usd"] = None
        row["parsed"] = row["parsed_multi"] = row["prediction"] = None
        row["parsed_label"] = row["parsed_probabilities"] = None
        row["parsed_max_prob"] = row["parsed_score"] = None
        row["response_model_field"] = None
        row["response_model_matches_pin"] = None
        row["request_hash"] = request_hash(body)
        return row
    row["curl_phases"] = {
        "time_namelookup": t.get("time_namelookup"),
        "time_connect": t.get("time_connect"),
        "time_appconnect": t.get("time_appconnect"),
        "time_pretransfer": t.get("time_pretransfer"),
        "time_starttransfer": t.get("time_starttransfer"),
        "time_total": t.get("time_total"),
        "num_connects": t.get("num_connects"),
        "time_redirect": t.get("time_redirect"),
    }
    row["http_status"] = status
    row["bytes"] = nbytes
    row["raw_response"] = raw
    row["typed_error"] = err
    row["error_detail"] = detail
    row["request_hash"] = request_hash(body)
    row["response_model_field"] = response_model_field(raw)
    row["response_model_matches_pin"] = (
        row["response_model_field"] == MODEL
        if row["response_model_field"] is not None else None)
    if err is None:
        usage = _extract_usage(raw)
        counts = token_counts(usage)
        row["usage"] = usage
        row["usage_flat"] = counts
        row["derived_cost_usd"] = derived_cost_usd(counts)
        row["parsed_multi"] = None
        parsed, prediction, perr = parse_jev(raw, case)
        row["parsed"] = parsed
        row["prediction"] = prediction
        if perr is not None:
            row["typed_error"] = perr
            row["error_detail"] = "200 OK but unusable answer"
        row["parsed_label"] = (prediction or {}).get("label")
        row["parsed_probabilities"] = (prediction or {}).get("probabilities")
        row["parsed_max_prob"] = (prediction or {}).get("max_prob")
        row["parsed_score"] = (prediction or {}).get("score")
    else:
        row["usage"] = row["usage_flat"] = row["derived_cost_usd"] = None
        row["parsed"] = row["parsed_multi"] = row["prediction"] = None
        row["parsed_label"] = row["parsed_probabilities"] = None
        row["parsed_max_prob"] = row["parsed_score"] = None
    return row


def cmd_probe(args):
    """INTERFACE PROBE — one labelled call mixing noul + choice + score under
    three distinct question keys. Tests whether the direct route accepts and
    answers multiple named questions. OUTSIDE the grid: its latency and cost
    are in no grid statistic."""
    report, cases, ordered, bodies = frozen_gate()
    key = resolve_credential()
    app, path = open_appender()
    if any(r.get("probe") == "mixed_question_types" for r in load_ndjson(path)):
        print("probe: mixed-question interface probe already recorded; skipping.")
        return 0
    by_id = {c["id"]: c for c in cases}
    by_type = {}
    for cid in ordered:
        t = by_id[cid]["questions"][0]["type"]
        by_type.setdefault(t, cid)
    missing = [t for t in ("noul", "choice", "score") if t not in by_type]
    if missing:
        raise SystemExit(
            f"INTERFACE PROBE IMPOSSIBLE: the frozen subset contains no {missing} "
            "case, so noul+choice+score cannot be mixed in one call.")

    # the state comes from the subset's first noul case; the three questions are
    # the subset's first noul / choice / score questions, verbatim
    state_case = by_id[by_type["noul"]]
    questions, label_maps = {}, {}
    for i, t in enumerate(("noul", "choice", "score")):
        keyname = t
        questions[keyname] = copy.deepcopy(by_id[by_type[t]]["questions"][0])
        label_maps[keyname] = by_id[by_type[t]]["control"].get("label_map") or {}
    body = {"model": MODEL, "state": state_case["state"],
            "questions": questions}

    row = run_one(state_case, key, "interface_probe", 1, concurrency=1,
                  probe="mixed_question_types", body=body,
                  questions=questions, label_maps=label_maps)
    row["probe_question_types"] = ["noul", "choice", "score"]
    row["probe_question_sources"] = by_type
    row["probe_state_source_case"] = state_case["id"]
    row["probe_body"] = body
    row["probe_note"] = (
        "ONE labelled call, OUTSIDE the warm/concurrency grid. Its latency and "
        "cost are in NO grid statistic. It answers ONE interface question: does "
        "the direct route accept a multi-key `questions` object and return all "
        "three answer types in one response? The three questions are the "
        "subset's own frozen noul/choice/score questions, verbatim; the state "
        "is the subset's first noul case's state. This is a CAPABILITY probe, "
        "not a semantic measurement — the three questions were written for "
        "different states, so no answer here is scored and no correctness claim "
        "is made. The body differs from a grid body in more than `model` by "
        "construction (three question keys), which is why it is kept out of the "
        "grid and its hash is recorded separately.")
    row["excluded_from_statistics"] = True
    if app.write(row):
        print(f"probe: HTTP {row['http_status']} "
              f"response_model={row['response_model_field']!r} "
              f"err={row['typed_error'] or '-'}")
        print(f"probe: per-key answers: "
              f"{ {k: (v['prediction'] or {}).get('label') for k, v in (row.get('parsed_multi') or {}).items()} }")
        print(f"probe: raw: {row['raw_response'][:600]}")
    return 0


# ===========================================================================
# EQUIVALENCE CROSS-CHECK — run BEFORE any comparative use
# ===========================================================================
def cmd_equivalence(args):
    report, cases, ordered, bodies = frozen_gate()
    rows = load_ndjson(RAW_PATH)
    warm = [r for r in rows if r.get("phase") == "warm"
            and r.get("block") == BLOCK]
    by_id = {c["id"]: c for c in cases}
    frozen_rows = {r["case_id"]: r for r in load_ndjson(
        os.path.join(PHASE1, "results", "jev_raw.ndjson"))}

    per_case, n_agree, n_total = [], 0, 0
    noul_cases, prob_cases = [], []
    for cid in ordered:
        frow = frozen_rows[cid]
        fpred = frow.get("prediction") or {}
        reps = [r for r in warm if r.get("case_id") == cid]
        usable = [r for r in reps if not r.get("typed_error")
                  and r.get("parsed_label") is not None]
        labels = [r.get("parsed_label") for r in usable]
        n_agree_rep = sum(1 for l in labels if l == fpred.get("label"))
        distinct = sorted(set(labels))
        entry = {
            "case_id": cid,
            "question_type": by_id[cid]["questions"][0]["type"],
            "frozen_model": frow.get("model_id"),
            "frozen_label": fpred.get("label"),
            "frozen_max_prob": fpred.get("max_prob"),
            "direct_n_reps": len(reps),
            "direct_n_usable": len(usable),
            "direct_n_failed": len(reps) - len(usable),
            "direct_distinct_labels": distinct,
            "direct_n_distinct_labels": len(distinct),
            "direct_majority_label": (max(set(labels), key=labels.count)
                                      if labels else None),
            "direct_reps_agreeing_with_frozen": n_agree_rep,
            "direct_reps_agreeing_with_frozen_rate": (
                round(n_agree_rep / len(usable), 4) if usable else None),
            "repeat_stable_single_label": len(distinct) <= 1,
            "answer_change_vs_frozen": bool(
                labels and fpred.get("label") not in set(labels)),
        }
        n_total += 1
        if entry["direct_majority_label"] == fpred.get("label"):
            n_agree += 1
        per_case.append(entry)

        # noul drift
        if by_id[cid]["questions"][0]["type"] == "noul" and usable:
            f_noul = (frow.get("parsed") or {}).get("noul")
            d_noul = [(r.get("parsed") or {}).get("noul") for r in usable
                      if (r.get("parsed") or {}).get("noul") is not None]
            if f_noul is not None and d_noul:
                drifts = [abs(x - f_noul) for x in d_noul]
                noul_cases.append({
                    "case_id": cid,
                    "frozen_noul": f_noul,
                    "direct_noul_per_rep": d_noul,
                    "median_abs_drift": FU03_A.r4(
                        FU03_A.nearest_rank(sorted(drifts), 50)),
                    "mean_abs_drift": FU03_A.r4(sum(drifts) / len(drifts)),
                    "max_abs_drift": FU03_A.r4(max(drifts)),
                })
        # choice / score probability drift
        qtype = by_id[cid]["questions"][0]["type"]
        if qtype in ("choice", "score") and usable:
            f_probs = fpred.get("probabilities") or {}
            per_rep = []
            for r in usable:
                d_probs = r.get("parsed_probabilities") or {}
                shared = sorted(set(f_probs) & set(d_probs))
                per_rep.append({
                    "repeat": r.get("repeat"),
                    "max_abs_delta": FU03_A.r4(
                        max((abs(d_probs[k] - f_probs[k]) for k in shared),
                            default=None)),
                    "labels_compared": shared,
                    "frozen_probabilities": f_probs,
                    "direct_probabilities": d_probs,
                })
            deltas = [p["max_abs_delta"] for p in per_rep
                      if p["max_abs_delta"] is not None]
            if deltas:
                prob_cases.append({
                    "case_id": cid,
                    "question_type": qtype,
                    "n_labels": len(f_probs),
                    "per_rep": per_rep,
                    "median_max_abs_delta": FU03_A.r4(
                        FU03_A.nearest_rank(sorted(deltas), 50)),
                    "max_abs_delta": FU03_A.r4(max(deltas)),
                })

    n_changes = sum(1 for e in per_case if e["answer_change_vs_frozen"])
    n_unstable = sum(1 for e in per_case if e["direct_n_distinct_labels"] > 1)
    all_deltas = [p["max_abs_delta"] for c in prob_cases for p in c["per_rep"]
                  if p["max_abs_delta"] is not None]
    doc = {
        "schema_version": "jevp1-jevdirect-equivalence-1.0",
        "computed_at_utc": utc_now_iso(),
        "question": "Do the direct `jev-1.13.0` answers agree with the frozen "
                    "`jev-1.13-free` answers on the SAME 16 cases? Recorded "
                    "before any comparative use; equivalence is NOT assumed.",
        "frozen_reference": {
            "path": "phase1/results/jev_raw.ndjson",
            "sha256": FROZEN_INPUTS["results/jev_raw.ndjson"],
            "model_id": "jev-1.13-free",
            "route": "opencode.ai/zen free tier",
            "n_rows_in_subset": len(ordered),
            "one_row_per_case": True,
            "caveat": "one observation per case, so a single frozen row cannot "
                      "itself be shown to be stable; stability is measured on "
                      "the direct side and the frozen side has no repeat axis",
        },
        "direct_measurement": {
            "path": "results/jev_direct_raw.ndjson",
            "model_id": MODEL,
            "route": ENDPOINT,
            "phase": "warm",
            "block": BLOCK,
            "reps_per_case_design": WARM_REPS,
        },
        "method": {
            "label_comparison": "the frozen predicted label vs the direct "
                                "majority label over the usable warm reps, plus "
                                "the per-rep agreement rate against the frozen "
                                "label",
            "noul_drift": "abs(direct noul - frozen noul) per rep, on noul cases",
            "probability_drift": "max over shared labels of abs(direct p - "
                                 "frozen p) per rep, on choice/score cases",
            "note": "this compares a DIFFERENT MODEL TAG on a DIFFERENT ROUTE "
                    "against the frozen free-tier row; a difference is a "
                    "route/model difference, not a defect, and is reported "
                    "rather than reconciled",
        },
        "label_agreement": {
            "n_cases": n_total,
            "n_cases_majority_label_matches_frozen": n_agree,
            "rate": FU03_A.r4(n_agree / n_total) if n_total else None,
            "n_cases_with_any_answer_change": n_changes,
            "n_cases_label_unstable_across_reps": n_unstable,
            "per_case": per_case,
        },
        "noul_drift": {
            "n_cases": len(noul_cases),
            "median_of_case_median_abs_drift": FU03_A.r4(FU03_A.nearest_rank(
                sorted(c["median_abs_drift"] for c in noul_cases), 50))
                if noul_cases else None,
            "worst_case_max_abs_drift": FU03_A.r4(max(
                (c["max_abs_drift"] for c in noul_cases), default=None)),
            "per_case": noul_cases,
        },
        "probability_drift_choice_score": {
            "n_cases": len(prob_cases),
            "overall_max_abs_delta": FU03_A.r4(max(all_deltas, default=None)),
            "median_of_case_median_max_abs_delta": FU03_A.r4(FU03_A.nearest_rank(
                sorted(c["median_max_abs_delta"] for c in prob_cases), 50))
                if prob_cases else None,
            "per_case": prob_cases,
        },
        "verdict": {
            "labels_fully_agree": n_agree == n_total and n_changes == 0,
            "labels_stable_within_direct_window": n_unstable == 0,
            "probability_availability_preserved": len(prob_cases) > 0,
            "equivalence_claimed": False,
            "equivalence_note": (
                "No equivalence is claimed. What is reported is the measured "
                "agreement and the measured drift between two different model "
                "tags on two different routes, plus the direct-side repeat "
                "stability. The comparative section states where agreement holds "
                "and what it does not license."),
        },
        "frozen_inputs_verified": report["digests"],
    }
    dump_json(EQUIV_PATH, doc)
    la = doc["label_agreement"]
    print(f"equivalence: label agreement {la['n_cases_majority_label_matches_frozen']}"
          f"/{la['n_cases']} (rate {la['rate']}); "
          f"{la['n_cases_with_any_answer_change']} cases with any answer change; "
          f"{la['n_cases_label_unstable_across_reps']} unstable across reps")
    print(f"equivalence: noul worst max|drift| = "
          f"{doc['noul_drift']['worst_case_max_abs_drift']}; "
          f"choice/score overall max|delta| = "
          f"{doc['probability_drift_choice_score']['overall_max_abs_delta']}")
    print(f"equivalence: -> {EQUIV_PATH}")
    return 0


# ===========================================================================
# SUMMARY
# ===========================================================================
def cmd_summary(args):
    report, cases, ordered, bodies = frozen_gate()
    rows = load_ndjson(RAW_PATH)
    by_id = {c["id"]: c for c in cases}
    corrected, _ids = FU03_OPS.f1_corrected_cases(cases)
    corr_by_id = {c["id"]: c for c in corrected}

    warm = [r for r in rows if r.get("phase") == "warm"
            and r.get("block") == BLOCK]
    warm_ok = [r for r in warm if FU03_A.usable(r)]
    warm_dropped = [r for r in warm
                    if r.get("block") == BLOCK and r.get("excluded_from_statistics")]

    def lat(rs, field):
        return FU03_A.describe(
            [FU03_A.curl_ms(r, field) for r in rs
             if FU03_A.curl_ms(r, field) is not None], unit="ms")

    transport = [FU03_A.curl_ms(r, "time_appconnect") for r in warm_ok]
    ttfb = [FU03_A.curl_ms(r, "time_starttransfer") for r in warm_ok]
    total = [FU03_A.curl_ms(r, "time_total") for r in warm_ok]
    residual = [t - s for t, s in zip(total, ttfb) if t is not None and s is not None]
    mean_total = (sum(total) / len(total)) if total else None
    mean_ttfb = (sum(ttfb) / len(ttfb)) if ttfb else None
    mean_transport = (sum(transport) / len(transport)) if transport else None
    stt_tracks_model_work = None
    if mean_total and mean_ttfb is not None and mean_transport is not None:
        # If the first byte lands essentially at TLS completion AND the
        # post-first-byte wait is the bulk of the call, then `time_starttransfer`
        # is NOT a time-to-first-token signal on this endpoint.
        gap = abs(mean_ttfb - mean_transport)
        stt_tracks_model_work = not (gap < 25.0 and
                                     (mean_total - mean_ttfb) > 0.5 * mean_total)

    # token / latency correlation
    pairs = [(FU03_A.curl_ms(r, "time_total"),
              (r.get("usage_flat") or {}).get("output_tokens"))
             for r in warm_ok]
    pairs = [(t, float(o)) for t, o in pairs if t is not None and o]
    pearson = None
    if len(pairs) >= 3:
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        num = sum((x - mx) * (y - my) for x, y in pairs)
        dx = (sum((x - mx) ** 2 for x in xs)) ** 0.5
        dy = (sum((y - my) ** 2 for y in ys)) ** 0.5
        if dx and dy:
            pearson = FU03_A.r4(num / (dx * dy))

    seq_sum = sum(total) if total else 0.0
    cor = FU03_A.correctness(warm_ok, corr_by_id)
    n_correct = cor["control_correct"]
    n_opp = cor["control_opportunities"]
    all_sum = FU03_A.r4(seq_sum / 1000.0)

    # per-case repeat stability
    stability = []
    for cid in ordered:
        rs = [r for r in warm_ok if r.get("case_id") == cid]
        if not rs:
            continue
        labels = [r.get("parsed_label") for r in rs]
        n_flip = 0
        for a, b in zip(labels, labels[1:]):
            if a != b:
                n_flip += 1
        mps = [r.get("parsed_max_prob") for r in rs
               if r.get("parsed_max_prob") is not None]
        mps_sorted = sorted(mps)
        spread = (max(mps) - min(mps)) if mps else None
        stability.append({
            "case_id": cid,
            "n_usable": len(rs),
            "distinct_labels": sorted(set(labels)),
            "n_label_transitions": n_flip,
            "label_stable": len(set(labels)) <= 1,
            "max_prob_min": FU03_A.r4(min(mps)) if mps else None,
            "max_prob_median": FU03_A.r4(FU03_A.nearest_rank(mps_sorted, 50))
                                if mps_sorted else None,
            "max_prob_max": FU03_A.r4(max(mps)) if mps else None,
            "max_prob_spread": FU03_A.r4(spread),
            "max_prob_stdev": FU03_A.r4(
                (sum((v - sum(mps) / len(mps)) ** 2 for v in mps)
                 / (len(mps) - 1)) ** 0.5) if len(mps) >= 2 else None,
        })

    # concurrency
    conc = {}
    for c in CONC_LEVELS:
        rs = [r for r in rows if r.get("phase") == "concurrency"
              and r.get("block") == BLOCK and r.get("concurrency") == c]
        ok = [r for r in rs if FU03_A.usable(r)]
        ms = (rs[0].get("block_makespan_ms") if rs else None)
        conc[str(c)] = {
            "n_calls": len(rs),
            "n_usable": len(ok),
            "n_failed": len(rs) - len(ok),
            "n_http_429": sum(1 for r in rs if r.get("http_status") == 429),
            "n_http_529": sum(1 for r in rs if r.get("http_status") == 529),
            "n_typed_errors": sum(1 for r in rs if r.get("typed_error")),
            "http_status_counts": FU03_A.counts_by(rs, lambda r: r.get("http_status")),
            "typed_error_counts": FU03_A.counts_by(
                rs, lambda r: r.get("typed_error") or "none"),
            "block_makespan_ms": ms,
            "throughput_calls_per_sec": (FU03_A.r4(len(ok) / (ms / 1000.0))
                                         if ms else None),
            "throughput_definition": "usable calls / block makespan, where the "
                                     "makespan is wall time from first dispatch "
                                     "to last completion of that level's block",
            "latency_total_ms": lat(ok, "time_total"),
            "latency_first_byte_ms": lat(ok, "time_starttransfer"),
        }
    c1 = conc["1"]["throughput_calls_per_sec"]
    for c in conc:
        thr = conc[c]["throughput_calls_per_sec"]
        p50 = conc[c]["latency_total_ms"].get("median")
        p50_1 = conc["1"]["latency_total_ms"].get("median")
        conc[c]["scaling_ratio_vs_c1"] = FU03_A.r4(thr / c1) if c1 and thr else None
        conc[c]["p50_latency_ratio_vs_c1"] = (FU03_A.r4(p50 / p50_1)
                                              if p50 and p50_1 else None)
    conc["scaling_definition"] = "throughput(C)/throughput(1). Ideal linear "\
                                 "scaling at concurrency C would be C."

    # idle
    idle_rows = [r for r in rows if r.get("phase") == "idle"]
    idle_ok = [r for r in idle_rows if FU03_A.usable(r)]

    # probe / route
    probe_rows = [r for r in rows if r.get("probe") == "mixed_question_types"]
    route_rows = [r for r in rows if r.get("phase") == "route_probe"]

    # availability + cost
    in_tok = [(r.get("usage_flat") or {}).get("input_tokens") for r in warm_ok]
    out_tok = [(r.get("usage_flat") or {}).get("output_tokens") for r in warm_ok]
    in_tok = [v for v in in_tok if v is not None]
    out_tok = [v for v in out_tok if v is not None]
    cost_warm = [r.get("derived_cost_usd") for r in warm_ok
                 if r.get("derived_cost_usd") is not None]
    all_costed = [r.get("derived_cost_usd") for r in rows
                  if r.get("derived_cost_usd") is not None]
    total_in = sum(in_tok) if in_tok else 0

    n_prob = sum(1 for r in warm_ok if r.get("parsed_probabilities"))
    n_conf = sum(1 for r in warm_ok
                 if (r.get("prediction") or {}).get("confidence_reported")
                 is not None)
    n_conf_formula = sum(1 for r in warm_ok
                         if (r.get("prediction") or {}).get("confidence_formula")
                         is not None)
    n_score = sum(1 for r in warm_ok if r.get("question_type") == "score"
                  and r.get("parsed_max_prob") is not None)

    n_429 = sum(1 for r in rows if r.get("http_status") == 429)
    n_529 = sum(1 for r in rows if r.get("http_status") == 529)
    mism = [r for r in rows
            if r.get("response_model_matches_pin") is False]

    mean_cost_call = (sum(cost_warm) / len(cost_warm)) if cost_warm else None
    err_rate = (1.0 - n_correct / n_opp) if n_opp else None

    doc = {
        "schema_version": "jevp1-jevdirect-summary-1.0",
        "computed_at_utc": utc_now_iso(),
        "question": "At approximately matched semantic capability, does direct "
                    "Jev (jev-1.13.0 over the TypeSafe API) materially improve "
                    "latency, tail latency, throughput, reliability, "
                    "probability availability or cost relative to the FROZEN "
                    "MiMo V2.6 Flash measurements of followup-03? Jev side only; "
                    "no consolidated Phase-1 verdict is produced here.",
        "comparison_class": "CROSS-WINDOW. MiMo measured ~2026-09-26T13:40Z "
                            "(followup-03 block `resume1`); Jev-direct measured "
                            "in this run's window. Same host, same curl "
                            "transport, different time window, different route "
                            "for Jev.",
        "measurement_block": BLOCK,
        "route": {
            "endpoint": ENDPOINT,
            "method": "POST",
            "model_pinned": MODEL,
            "model_alias_note": "`jev-latest` resolves to this id; `jev-1.13` is "
                                "rejected with 400. The pin is used verbatim and "
                                "the response `model` field is asserted equal to "
                                "it on every row.",
            "change_vs_followup_03_jev_route": {
                "followup_03": {"endpoint": "https://opencode.ai/zen/v1/systemone",
                                "model": "jev-1.13-free", "tier": "free",
                                "usable_answers": 0},
                "this_run": {"endpoint": ENDPOINT, "model": MODEL,
                             "tier": "paid ($0.042/Mtok input, output free)"},
                "why_it_is_not_a_rerun": "a different host, a different model tag "
                                         "and a different price tier. These "
                                         "numbers do NOT fill in followup-03's "
                                         "UNRESOLVED free-tier cells; they are a "
                                         "new observation of a new path.",
            },
            "response_model_field_seen": sorted(
                {r.get("response_model_field") for r in rows
                 if r.get("response_model_field") is not None}),
            "n_rows_where_response_model_mismatched_pin": len(mism),
            "n_rows_carrying_response_model_field": sum(
                1 for r in rows if r.get("response_model_field") is not None),
        },
        "published_facts_not_used_to_support_any_measurement": PUBLISHED_RATES,
        "pricing": {
            "input_usd_per_mtok": TS_COST_PER_MTOK["input"],
            "output_usd_per_mtok": TS_COST_PER_MTOK["output"],
            "derivation": "derived_cost_usd = input_tokens / 1e6 * 0.042; output "
                          "is free on this route, so cost is driven entirely by "
                          "input tokens",
            "frozen_jev_route_price": "free tier, $0 (followup-03) — this is a "
                                      "PRICING AND ENTITLEMENT difference, not a "
                                      "structural one",
        },
        "frozen_inputs_verified": report["digests"],
        "request_semantics": {
            "only_field_changed": "model",
            "n_cases": report["request_gate"]["n_cases"],
            "n_equal_after_model_normalisation":
                report["request_gate"]["n_equal_after_model_normalisation"],
            "n_state_byte_identical": report["request_gate"]["n_state_byte_identical"],
            "n_questions_byte_identical":
                report["request_gate"]["n_questions_byte_identical"],
            "model_from": report["request_gate"]["model_from"],
            "model_to": MODEL,
            "per_case_request_hashes": {
                cid: {"frozen": report["request_gate"]["per_case"][cid]["frozen_request_hash"],
                      "direct": report["request_gate"]["per_case"][cid]["direct_request_hash"],
                      "serialised_sha256_direct": report["request_gate"]["per_case"][cid]["direct_serialised_sha256"]}
                for cid in ordered},
        },
        "inputs": {
            "raw_path": "results/jev_direct_raw.ndjson",
            "n_rows_total": len(rows),
            "rows_by_phase": FU03_A.counts_by(rows, lambda r: r.get("phase")),
            "rows_with_typed_error": sum(1 for r in rows if r.get("typed_error")),
            "excluded_from_statistics": FU03_A.counts_by(
                warm_dropped, lambda r: r.get("phase")),
        },
        "warm_latency": {
            "rows": "phase=warm AND block=direct1 AND usable",
            "n_rows_emitted": len(warm),
            "n_usable": len(warm_ok),
            "latency_total_ms": lat(warm_ok, "time_total"),
            "latency_first_byte_ms": lat(warm_ok, "time_starttransfer"),
            "latency_tls_complete_ms": lat(warm_ok, "time_appconnect"),
            "latency_dns_ms": lat(warm_ok, "time_namelookup"),
            "latency_tcp_connect_ms": lat(warm_ok, "time_connect"),
            "post_first_byte_residual_ms": FU03_A.describe(residual, unit="ms"),
            "transport_definition": "time_appconnect ALONE. curl's -w phase "
                                    "timings are CUMULATIVE from transfer start "
                                    "(verified strictly monotonic: namelookup "
                                    "<= connect <= appconnect <= pretransfer "
                                    "<= starttransfer <= total), so "
                                    "namelookup + connect + appconnect adds "
                                    "overlapping intervals and double-counts.",
            "transport_setup_ms": FU03_A.describe(transport, unit="ms"),
            "model_attributable_residual_ms": FU03_A.describe(
                [t - s for t, s in zip(total, transport)
                 if t is not None and s is not None], unit="ms"),
            "transport_share_of_total_mean": (
                FU03_A.r4(mean_transport / mean_total) if mean_total and
                mean_transport is not None else None),
            "pearson_r_total_vs_output_tokens": pearson,
            "correlation_caveat": "established over an output-token range of "
                                  "17..69 only. It must NOT be extrapolated to "
                                  "long-form output: the independence of latency "
                                  "from work done is a statement about this "
                                  "narrow range.",
        },
        "transport_measurement_correction_to_followup_03": {
            "finding": "followup-03 computed transport as "
                       "`namelookup + connect + appconnect`, which double-counts "
                       "because curl's -w phase timings are cumulative from "
                       "transfer start. The correct transport is time_appconnect "
                       "alone.",
            "verification": "strict monotonicity of the phase sequence confirmed "
                            "on all rows of BOTH raw files",
            "mimo_followup_03_reported_mean_transport_ms": 205.0413,
            "mimo_corrected_mean_transport_ms": 201.643,
            "mimo_followup_03_reported_transport_share": 0.034331,
            "mimo_corrected_transport_share": 0.033771,
            "error_size": "+1.7% on mean transport, +0.06 pp on the share",
            "affects_conclusions": False,
            "why_not": "followup-03's conclusions rest on time_total, not on the "
                       "transport share; the correction moves no ranking",
            "frozen_artefacts_modified": False,
            "note": "recorded as a correction to how the frozen figure is read "
                    "here. The frozen followup-03 artefacts are unmodified and "
                    "were read read-only.",
        },
        "starttransfer_interpretation": {
            "question": "does `time_starttransfer` track model work or only "
                        "header/TLS completion for this endpoint?",
            "answer": ("ONLY HEADER/TLS COMPLETION — it is NOT a time-to-first-"
                       "token signal on this endpoint."
                       if stt_tracks_model_work is False else
                       "inconclusive — mean first byte is not within 25 ms of mean "
                       "TLS completion"
                       if stt_tracks_model_work is None else
                       "appears to track model work"),
            "mean_first_byte_ms": FU03_A.r4(mean_ttfb),
            "mean_tls_complete_ms": FU03_A.r4(mean_transport),
            "first_byte_minus_tls_ms": (FU03_A.r4(mean_ttfb - mean_transport)
                                        if mean_ttfb is not None and
                                        mean_transport is not None else None),
            "mean_total_ms": FU03_A.r4(mean_total),
            "mean_post_first_byte_residual_ms": FU03_A.r4(
                sum(residual) / len(residual) if residual else None),
            "post_first_byte_share_of_total": (
                FU03_A.r4((sum(residual) / len(residual)) / mean_total)
                if residual and mean_total else None),
            "first_byte_stdev_ms": lat(warm_ok, "time_starttransfer").get("stdev"),
            "total_stdev_ms": lat(warm_ok, "time_total").get("stdev"),
            "consequence": "the only defensible client-observed latency figure is "
                           "`time_total`. `time_starttransfer` must not be read "
                           "as model responsiveness, and the two must not be "
                           "confused in a cross-mechanism table.",
        },
        "sequential_throughput": {
            "definition": "a strictly sequential client issues one call at a time, "
                          "so elapsed time is the sum of per-call time_total; "
                          "calls/sec is n_usable / that sum. EXCLUDES client "
                          "think-time, so it is an upper bound on the attainable "
                          "rate.",
            "n_usable": len(warm_ok),
            "summed_time_total_s": all_sum,
            "calls_per_sec": (FU03_A.r4(len(warm_ok) / (seq_sum / 1000.0))
                              if seq_sum else None),
            "calls_per_sec_including_process_spawn": (
                FU03_A.r4(len(warm_ok) / (
                    sum(r["wall_ms_including_process_spawn"] for r in warm_ok)
                    / 1000.0))
                if warm_ok and all(r.get("wall_ms_including_process_spawn")
                                   for r in warm_ok) else None),
            "control_correct_decisions": n_correct,
            "control_opportunities": n_opp,
            "control_correct_decisions_per_sec": (
                FU03_A.r4(n_correct / (seq_sum / 1000.0)) if seq_sum and n_opp
                else None),
            "scoring_definition": "semantic scoring is CONTROL ONLY, against the "
                                  "frozen ground truth with the F1 correction "
                                  "applied by followup-03's own function. An "
                                  "opportunity is one usable prediction on an "
                                  "ANSWERABLE control (variant_kind == base) "
                                  "case; an unanswerable case is not scored "
                                  "correct/incorrect here.",
            "all_subset_correct_decisions": cor["all_subset_correct"],
            "all_subset_opportunities": cor["all_subset_opportunities"],
            "control_error_rate": FU03_A.r4(err_rate) if err_rate is not None else None,
        },
        "concurrency": conc,
        "idle_gap_proxy": {
            "idle_seconds_before": IDLE_SECONDS,
            "n_calls": len(idle_rows),
            "n_usable": len(idle_ok),
            "latency_total_ms": lat(idle_ok, "time_total"),
            "latency_first_byte_ms": lat(idle_ok, "time_starttransfer"),
            "per_call": [{"case_id": r.get("case_id"), "repeat": r.get("repeat"),
                          "http_status": r.get("http_status"),
                          "typed_error": r.get("typed_error"),
                          "time_total_ms": FU03_A.curl_ms(r, "time_total"),
                          "time_starttransfer_ms": FU03_A.curl_ms(r, "time_starttransfer"),
                          "input_tokens": (r.get("usage_flat") or {}).get("input_tokens"),
                          "response_model_field": r.get("response_model_field")}
                         for r in idle_rows],
            "claim_limit": "an idle-gap PROXY only. Per-call cold start is not "
                           "directly observable on a shared stateless HTTPS "
                           "endpoint and is NOT claimed to be observed.",
        },
        "reliability": {
            "n_rows_total": len(rows),
            "n_typed_errors": sum(1 for r in rows if r.get("typed_error")),
            "typed_error_counts_all_rows": FU03_A.counts_by(
                rows, lambda r: r.get("typed_error") or "none"),
            "warm_n_emitted": len(warm),
            "warm_n_usable": len(warm_ok),
            "warm_n_unusable": len(warm) - len(warm_ok),
            "warm_usable_rate": FU03_A.r4(len(warm_ok) / len(warm)) if warm else None,
            "warm_unusable_by_case": FU03_A.counts_by(
                [r for r in warm if not FU03_A.usable(r)],
                lambda r: r.get("case_id")),
            "warm_unusable_detail": [
                {"case_id": r.get("case_id"), "repeat": r.get("repeat"),
                 "http_status": r.get("http_status"),
                 "typed_error": r.get("typed_error"),
                 "error_detail": r.get("error_detail"),
                 "bytes": r.get("bytes"),
                 "raw_head": (r.get("raw_response") or "")[:400]}
                for r in warm if not FU03_A.usable(r)],
            "n_http_429_all_rows": n_429,
            "n_http_529_all_rows": n_529,
            "retries": 0,
            "attempts_per_call": MAX_ATTEMPTS,
            "retry_note": "N = 1 attempt, no retry path at any concurrency level. "
                          "A retry on exactly the failing cells would convert an "
                          "N=1 observation into a survivorship-biased one.",
            "route_probe": [{"http_status": r.get("http_status"),
                             "response_model_field": r.get("response_model_field"),
                             "response_model_matches_pin": r.get("response_model_matches_pin"),
                             "typed_error": r.get("typed_error")}
                            for r in route_rows],
        },
        "repeat_stability": {
            "definition": "label flips and max-probability variance across the 12 "
                          "warm repetitions of the SAME request, per case",
            "n_cases_label_stable": sum(1 for s in stability if s["label_stable"]),
            "n_cases_label_unstable": sum(1 for s in stability
                                          if not s["label_stable"]),
            "n_cases_with_max_prob_spread": sum(
                1 for s in stability if s["max_prob_spread"] is not None),
            "max_over_cases_of_max_prob_spread": FU03_A.r4(max(
                (s["max_prob_spread"] for s in stability
                 if s["max_prob_spread"] is not None), default=None)),
            "median_over_cases_of_max_prob_spread": (
                FU03_A.r4(FU03_A.nearest_rank(
                    sorted(s["max_prob_spread"] for s in stability
                           if s["max_prob_spread"] is not None), 50))
                if any(s["max_prob_spread"] is not None for s in stability)
                else None),
            "per_case": stability,
        },
        "usage_and_cost": {
            "input_tokens": FU03_A.describe(in_tok, unit="tokens"),
            "output_tokens": FU03_A.describe(out_tok, unit="tokens"),
            "total_input_tokens_warm": total_in,
            "cost_per_call_usd_warm": FU03_A.r_usd(mean_cost_call),
            "cost_per_call_usd_total_run": FU03_A.r_usd(
                sum(all_costed) / len(all_costed) if all_costed else None),
            "total_run_derived_cost_usd": FU03_A.r_usd(sum(all_costed)
                                                       if all_costed else None),
            "derived_cost_per_correct_control_decision_usd": (
                FU03_A.r_usd((sum(cost_warm) / n_correct) if cost_warm and n_correct
                             else None)),
            "correct_decisions_per_dollar": (
                FU03_A.r4(n_correct / sum(cost_warm))
                if cost_warm and sum(cost_warm) > 0 else None),
            "input_tokens_are_the_whole_cost": "output is free on this route, so "
                                               "derived cost is exactly "
                                               "input_tokens x $0.042/Mtok",
            "frozen_jev_route_cost_for_contrast": "0.0 (free tier) — a pricing "
                                                  "and entitlement difference, "
                                                  "not a structural one",
        },
        "probability_availability": {
            "n_usable_warm": len(warm_ok),
            "n_with_probability_distribution": n_prob,
            "probability_availability_rate": (FU03_A.r4(n_prob / len(warm_ok))
                                              if warm_ok else None),
            "n_with_reported_confidence_field": n_conf,
            "n_with_computable_confidence_formula": n_conf_formula,
            "score_cases_with_full_distribution": n_score,
            "interface_probe": {
                "n_rows": len(probe_rows),
                "http_status": [r.get("http_status") for r in probe_rows],
                "response_model_field": [r.get("response_model_field")
                                         for r in probe_rows],
                "multi_question_key_accepted": bool(
                    probe_rows and probe_rows[0].get("parsed_multi")),
                "per_key_labels": (
                    {k: (v.get("prediction") or {}).get("label")
                     for k, v in (probe_rows[0].get("parsed_multi") or {}).items()}
                    if probe_rows else None),
                "per_key_availability": (
                    {k: (v.get("error") is None and v.get("prediction") is not None)
                     for k, v in (probe_rows[0].get("parsed_multi") or {}).items()}
                    if probe_rows else None),
                "note": "one labelled call, outside the grid; latency and cost in "
                        "no grid statistic; no answer is scored",
            },
        },
        "not_measured": {
            "sustained_multi_hour_throughput": "NOT MEASURED. Every figure here is "
                                               "a short burst window.",
            "per_call_cold_start": "NOT DIRECTLY OBSERVABLE. The idle-gap probe is "
                                   "a proxy only.",
            "server_side_queueing_or_batch_effects": "NOT OBSERVABLE from the "
                                                     "client. The client cannot see "
                                                     "whether the service batches, "
                                                     "queues or contends.",
            "followup_03_free_tier_jev_cells": "NOT FILLED. followup-03's Jev cells "
                                               "were properties of the free-tier "
                                               "route; this run observes a "
                                               "different route and model tag.",
            "consolidated_phase_1_verdict": "OUT OF SCOPE for this run by brief.",
            "rate_limit_envelope": "NOT TESTED. The published 250k tok/s and 1200 "
                                   "req/min ceilings were not approached by a "
                                   "short burst, so nothing here speaks to the "
                                   "ceiling or to sustained rate.",
        },
        "determinism": {
            "method": "every section is a pure function of "
                      "results/jev_direct_raw.ndjson — no clock read, no "
                      "randomness, no network access — with ONE declared "
                      "exception: `computed_at_utc` is a clock read and is "
                      "therefore volatile by construction. `check` compares "
                      "the document with that one field removed and requires "
                      "the rest to reproduce exactly.",
            "volatile_fields_excluded_from_check": ["computed_at_utc"],
            "percentile_method": "nearest-rank, no interpolation (followup-03's "
                                 "`describe`, imported)",
            "verify_with": "python3 harness/run_ops_jev_direct.py check",
        },
    }
    dump_path = getattr(args, "_tmp", None) or SUMMARY_PATH
    dump_json(dump_path, doc)
    print(f"summary: -> {dump_path}")
    wl = doc["warm_latency"]
    print(f"  warm usable {wl['n_usable']}/{wl['n_rows_emitted']}  "
          f"total median {wl['latency_total_ms'].get('median')} ms  "
          f"p95 {wl['latency_total_ms'].get('p95')} ms")
    print(f"  sequential {doc['sequential_throughput']['calls_per_sec']} calls/s; "
          f"control-correct {doc['sequential_throughput']['control_correct_decisions_per_sec']}/s")
    print(f"  cost/call ${doc['usage_and_cost']['cost_per_call_usd_warm']}; "
          f"run total ${doc['usage_and_cost']['total_run_derived_cost_usd']}")
    print(f"  starttransfer: {doc['starttransfer_interpretation']['answer']}")
    return 0


def cmd_check(args):
    """Determinism check: recompute the summary and diff the documents.

    The single declared volatile field (`computed_at_utc`, a clock read) is
    removed from both sides before comparison. Everything else must reproduce
    exactly from the same raw file.
    """
    before = load_json(SUMMARY_PATH) if os.path.exists(SUMMARY_PATH) else None
    if before is None:
        print("check: no summary.json yet; run `summary` first.", file=sys.stderr)
        return 2
    tmp = SUMMARY_PATH + ".check.tmp"
    args._tmp = tmp
    cmd_summary(args)
    after = load_json(tmp)
    os.remove(tmp)
    volatile = ["computed_at_utc"]

    def stable(doc):
        return {k: v for k, v in doc.items() if k not in volatile}

    a = json.dumps(stable(before), sort_keys=True)
    b = json.dumps(stable(after), sort_keys=True)
    if a == b:
        print(f"check: summary.json reproduces exactly from the same raw file "
              f"with {volatile} excluded (PASS)")
        return 0
    print("check: summary.json DIFFERS on recompute (FAIL)", file=sys.stderr)
    for k in sorted(set(before) | set(after)):
        if json.dumps(stable(before).get(k), sort_keys=True) != \
                json.dumps(stable(after).get(k), sort_keys=True):
            print(f"  differing section: {k}", file=sys.stderr)
    return 1


# ===========================================================================
def main():
    ap = argparse.ArgumentParser(
        description="followup-04 direct TypeSafe API route for Jev")
    sub = ap.add_subparsers(dest="mode", required=True)
    sub.add_parser("gate")
    sub.add_parser("route")
    p_warm = sub.add_parser("warm")
    p_warm.add_argument("--reps", type=int, default=WARM_REPS)
    p_warm.add_argument("--interval", type=float, default=0.0)
    p_warm.add_argument("--skip-warmup", action="store_true")
    sub.add_parser("idle")
    sub.add_parser("concurrency")
    sub.add_parser("probe")
    sub.add_parser("equivalence")
    sub.add_parser("summary")
    p_check = sub.add_parser("check")
    p_check.add_argument("--_tmp", default=None)
    args = ap.parse_args()
    return {
        "gate": cmd_gate, "route": cmd_route, "warm": cmd_warm,
        "idle": cmd_idle, "concurrency": cmd_concurrency, "probe": cmd_probe,
        "equivalence": cmd_equivalence, "summary": cmd_summary,
        "check": cmd_check,
    }[args.mode](args)


if __name__ == "__main__":
    raise SystemExit(main())
