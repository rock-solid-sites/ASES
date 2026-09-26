#!/usr/bin/env python3
"""Deterministic baseline mechanisms + the cheap general-model baseline.

Four mechanisms, in cost order (the order is normative -- it defines
"cheapest preceding mechanism" for the incremental-gain metric):

  0 prior         measured label majority fitted on the TRAIN split only
  1 rule          deterministic rules
  2 lexical       token-overlap / keyword scoring
  3 jev           (see harness/run_jev.py)
  4 general_model cheap chat model over a fixed template

HONESTY NOTE, stated up front because it conditions how every number from
these baselines may be read:

  The `rule` cue lexicons and the `lexical` cue lexicons below were authored by
  the same agent that authored the corpus, with the case vocabulary in view.
  They are therefore NOT independent of the corpus. They are hand-built
  baselines, not discovered ones, and their accuracy is an upper bound on what
  a generic cue engine would achieve on this corpus. This is disclosed in the
  tables and must be restated wherever these numbers are cited.

  `rule` on area D is different: it evaluates `harness/routing_policy.py`,
  the deterministic legality policy, recomputed from `routing.signals` rather
  than read from the stored answer. That is a genuine deterministic mechanism,
  not a hand-tuned cue list, and it is the strongest cheap baseline the routing
  area admits.

Usage:
    python3 harness/run_baselines.py [--cases P] [--out P] [--limit N]
                                     [--skip-general] [--general-url URL]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from common import (  # noqa: E402
    ERR_EMPTY,
    ERR_NOT_ATTEMPTED,
    ERR_PARSE,
    NdjsonWriter,
    confidence_formula,
    load_cases,
    make_result,
    post_json,
)
from routing_policy import ROLE_LABEL, compute_legality  # noqa: E402

GO_CHAT_URL = "https://opencode.ai/zen/go/v1/chat/completions"
ZEN_CHAT_URL = "https://opencode.ai/zen/v1/chat/completions"
GENERAL_MODEL = "space-bunny-free"
API_KEY_ENV = "OPENCODE_GO_API_KEY"
SESSION_ID = "jev-phase1-baselines-20260926"

# Assumed confidences for the deterministic mechanisms. These are MODELLING
# ASSUMPTIONS, not measurements; they exist so the coverage/error analysis can
# be run uniformly across mechanisms that have no native confidence output.
RULE_HARD_CONF = 0.75
RULE_SOFT_CONF = 0.55
ROUTING_POLICY_CONF = 0.90

STOPWORDS = frozenset("""
a an the is are was were be been being of to in on at by for with from as and or
but if then than that this these those it its there here did do does done have
has had having any all each every some no not non nor so such which who whom
what when where why how into out up down over under again further once more most
other own same too very can will just should now
""".split())

# Hand-authored cue lexicons. See HONESTY NOTE above.
NEGATIVE_CUES = frozenset("""
fail failed failing failure failures error errors errored wrong exceed
exceeded exceeds exceeding blocked blocking missing absent none invalid
unknown unrecorded truncated empty rejected aborted paused suspended
unresolved declined withheld incompatible unsatisfiable conflict conflicting
cannot lacking absent_without retire retired stopped halted
""".split())
POSITIVE_CUES = frozenset("""
pass passes passed passing succeed succeeds succeeded success success_ok
green clean cleanly healthy resolved complete completed closed signed
approved approved_by reconciled matched consistent valid accurate
""".split())
UNANSWERABLE_CUES = frozenset("""
absent unrecorded unknown truncated empty conflicting disagree disagrees
not_recorded missing unavailable neither regardless cannot_determine
""".split())
# Strong, high-precision phrases: presence is treated as decisive.
NEGATIVE_PHRASES = (
    "failed", "failure", "exit code 1", "exit code 2", "build failed",
    "were not", "was not", "not started", "never resumed", "never executed",
    "cannot be", "do not exist", "is empty", "were failed", "still running",
    "was rolled back", "remains incomplete", "exceeds the", "above the",
    "is not present", "are not present", "has not", "have not", "does not",
    "is not complete", "not yet",
)
POSITIVE_PHRASES = (
    "all 18", "all 42", "all required", "all three", "all five",
    "marked pass", "exit code 0", "0 errors", "0 warnings", "0 missing",
    "0 duplicate", "applied cleanly", "declared resolved", "100%",
    "passed all", "is the pin", "matching the pin", "was resolved",
    "was remediated", "never exceeded",
)


def tokens(text):
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if t]


def content_tokens(text):
    return [t for t in tokens(text) if t not in STOPWORDS and len(t) > 2]


# ---------------------------------------------------------------------------
# Mechanism 0: prior (measured on TRAIN only)
# ---------------------------------------------------------------------------
def fit_prior(cases):
    """Label distribution per question type, fitted on the train split only."""
    prior = {}
    for qtype in ("noul", "choice", "score"):
        labels = [c["ground_truth"]["answer"] for c in cases
                  if c["split"] == "train"
                  and c["questions"][0]["type"] == qtype
                  and c["ground_truth"]["answerable"]]
        prior[qtype] = dict(Counter(labels))
    return prior


def run_prior(case, prior):
    qtype = case["questions"][0]["type"]
    if qtype == "noul":
        labels = ("no", "yes")
    elif qtype == "choice":
        lm = case["control"].get("label_map") or {}
        labels = tuple(lm.get(k, k) for k in case["questions"][0]["criteria"])
    else:
        labels = tuple(case["questions"][0]["criteria"])
    counts = prior.get(qtype) or {}
    support = sum(counts.values())
    if support == 0:
        # No train evidence for this label space. Emit uniform and say so.
        probs = {l: 1.0 / len(labels) for l in labels}
        label = sorted(labels)[0]
    else:
        probs = {l: counts.get(l, 0) / support for l in labels}
        label = max(sorted(probs), key=lambda l: (probs[l], l))
    return {
        "label": label,
        "probabilities": probs,
        "score": None,
        "max_prob": max(probs.values()),
        "confidence_reported": None,
        "confidence_formula": confidence_formula(probs),
        "normalised": False,
        "prob_sum": round(sum(probs.values()), 6),
        "train_support": support,
        "train_distribution": counts,
    }


# ---------------------------------------------------------------------------
# Mechanism 1: rule
# ---------------------------------------------------------------------------
def run_rule(case):
    if case["area"] == "D" and case.get("routing"):
        # Deterministic legality policy, recomputed from the signals rather
        # than read from the stored answer.
        leg = compute_legality(case["routing"]["signals"])
        labels = sorted(set(leg["legal_roles"]) | set(leg["illegal_roles"]))
        exp = leg["expected_role"]
        probs = {l: (ROUTING_POLICY_CONF if l == exp
                     else round((1.0 - ROUTING_POLICY_CONF) /
                                max(1, len(labels) - 1), 6))
                 for l in labels}
        return {
            "label": exp,
            "probabilities": probs,
            "score": None,
            "max_prob": ROUTING_POLICY_CONF,
            "confidence_reported": None,
            "confidence_formula": confidence_formula(probs),
            "normalised": abs(sum(probs.values()) - 1.0) > 0.02,
            "prob_sum": round(sum(probs.values()), 6),
            "rule_branch": "foreman-routing-1.0",
        }

    qtype = case["questions"][0]["type"]
    state_low = case["state"].lower()

    if qtype == "choice":
        # Non-routing choice: a rule engine counts exact role-name mentions and
        # otherwise declines to discriminate. Unreachable in this corpus (all
        # choice cases are area D) but kept so the mechanism is total.
        labels, _ = _choice_space(case)
        hits = {l: state_low.count(l) for l in labels}
        mx = max(hits.values()) if hits else 0
        if mx == 0:
            label, conf, branch = sorted(labels)[0], 0.5, "choice_no_mention"
        else:
            winners = [l for l in sorted(labels) if hits[l] == mx]
            label = winners[0]
            conf = RULE_SOFT_CONF if len(winners) == 1 else RULE_HARD_CONF * 0.5
            branch = f"choice_mentions {mx} tied={len(winners) == 1}"
        probs = _sigmoid_probs(label, labels, conf)
        return _pack(label, probs, None, branch)

    if qtype == "score":
        # A rule engine matches a criterion only when ALL of its cue phrases are
        # present. First match in criteria order wins; no match falls back to
        # the first criterion with low confidence.
        crit = list(case["questions"][0]["criteria"])
        fired, branch = None, "score_no_rule"
        for c in crit:
            cues = SCORE_RULES.get(c, ())
            if cues and all(p in state_low for p in cues):
                fired = c
                branch = f"score_rule[{c}]"
                break
        if fired is None:
            fired, conf = crit[0], 0.5
        else:
            conf = RULE_SOFT_CONF
        probs = _sigmoid_probs(fired, crit, conf)
        return _pack(fired, probs, None, branch)

    labels, lex = ("no", "yes"), None
    inst_low = case["questions"][0]["instructions"].lower()
    npos = sum(1 for p in POSITIVE_PHRASES if p in state_low)
    nneg = sum(1 for p in NEGATIVE_PHRASES if p in state_low)
    unans = any(c in state_low for c in UNANSWERABLE_CUES) and \
        "conflict" in state_low
    if npos == 0 and nneg == 0:
        probs = {"yes": 0.5, "no": 0.5}
        conf = 0.5
        branch = "no_cue"
    else:
        total = npos + nneg
        p_yes = npos / total
        conf = RULE_HARD_CONF if abs(p_yes - 0.5) >= 0.5 else RULE_SOFT_CONF
        probs = {"yes": p_yes, "no": 1.0 - p_yes}
        branch = f"phrases pos={npos} neg={nneg}"
    label = "yes" if probs["yes"] >= 0.5 else "no"
    out = _pack(label, probs, None, branch)
    out["confidence_assumed"] = conf
    if unans:
        # A rule engine that recognises "conflicting and unexplained" must
        # still answer something; record that it is guessing.
        out["unanswerability_cue"] = True
    return out


def _sigmoid_probs(chosen, labels, conf):
    """Distribution with `conf` on the chosen label and the rest spread evenly."""
    others = [l for l in labels if l != chosen]
    if not others:
        return {chosen: 1.0}
    share = (1.0 - conf) / len(others)
    return {chosen: round(conf, 6), **{l: round(share, 6) for l in others}}


# Criterion -> cue phrases that must ALL be present for the rule to fire.
# Hand-authored with the corpus vocabulary in view. See HONESTY NOTE.
SCORE_RULES = {
    "none": ("zero", "no consumer has reported an error"),
    "low": ("decommissioned",),
    "medium": (),
    "high": (),
    "weak": ("one said it is weak",),
    "moderate": (),
    "strong": (),
}


def _choice_space(case):
    lm = case["control"].get("label_map") or {}
    labels = tuple(lm.get(k, k) for k in case["questions"][0]["criteria"])
    lex = {}
    for l in labels:
        lex[l] = _lex_of(f"{l} {ROLE_LABEL.get(l, '')}")
    return labels, lex


def _score_space(case):
    labels = tuple(case["questions"][0]["criteria"])
    lex = {l: _lex_of(l) for l in labels}
    return labels, lex


def _lex_of(text):
    return set(content_tokens(text))


# ---------------------------------------------------------------------------
# Mechanism 2: lexical
# ---------------------------------------------------------------------------
def run_lexical(case):
    qtype = case["questions"][0]["type"]
    state = set(content_tokens(case["state"]))
    inst = set(content_tokens(case["questions"][0]["instructions"]))

    if qtype == "choice":
        labels, lex = _choice_space(case)
    elif qtype == "score":
        labels, lex = _score_space(case)
    else:
        labels = ("no", "yes")
        lex = None

    if lex is None:
        npos = len(state & POSITIVE_CUES) + 0.5 * len(inst & POSITIVE_CUES)
        nneg = len(state & NEGATIVE_CUES) + 0.5 * len(inst & NEGATIVE_CUES)
        p_yes = (npos + 1.0) / (npos + nneg + 2.0)     # Laplace a=1
        probs = {"yes": p_yes, "no": 1.0 - p_yes}
        label = "yes" if p_yes >= 0.5 else "no"
        return _pack(label, probs, None,
                     f"cue_hits pos={npos:.1f} neg={nneg:.1f}")

    scores = {}
    for l in labels:
        s = len(state & lex[l]) + 0.5 * len(inst & lex[l])
        # The question's own words must not count as evidence about the state.
        s -= 0.25 * len(inst & lex[l])
        scores[l] = s
    return _soft_label(scores, branch=f"overlap({qtype})")


def _soft_label(scores, branch):
    mx = max(scores.values()) if scores else 0.0
    expo = {k: math.exp(2.0 * (v - mx)) for k, v in scores.items()}
    z = sum(expo.values()) or 1.0
    probs = {k: round(v / z, 6) for k, v in expo.items()}
    label = max(sorted(probs), key=lambda k: (probs[k], k))
    return _pack(label, probs, None, branch)


def _pack(label, probs, score, branch):
    return {
        "label": label,
        "probabilities": probs,
        "score": score,
        "max_prob": max(probs.values()) if probs else None,
        "confidence_reported": None,
        "confidence_formula": confidence_formula(probs),
        "normalised": abs(sum(probs.values()) - 1.0) > 0.02,
        "prob_sum": round(sum(probs.values()), 6),
        "rule_branch": branch,
    }


# ---------------------------------------------------------------------------
# Mechanism 4: general_model
# ---------------------------------------------------------------------------
GEN_SYS = ("You are a deterministic classifier. Reply with the single required "
           "token and nothing else. Never explain. Never add punctuation.")


def build_general_request(case, model_id):
    q = case["questions"][0]
    qtype = q["type"]
    if qtype == "noul":
        user = (f"State:\n{case['state']}\n\n"
                f"Question: {q['instructions']}\n\n"
                f"Reply with exactly one word: YES or NO.")
    elif qtype == "choice":
        opts = "\n".join(f"{k}: {v}" for k, v in q["criteria"].items())
        user = (f"State:\n{case['state']}\n\n"
                f"Question: {q['instructions']}\n\n"
                f"Options:\n{opts}\n\n"
                f"Reply with exactly one option key and nothing else.")
    else:
        opts = ", ".join(q["criteria"])
        user = (f"State:\n{case['state']}\n\n"
                f"Question: {q['instructions']}\n\n"
                f"Allowed labels: {opts}\n\n"
                f"Reply with exactly one label and nothing else.")
    return {
        "model": model_id,
        "messages": [
            {"role": "system", "content": GEN_SYS},
            {"role": "user", "content": user},
        ],
        "temperature": 0,
        "max_tokens": 16,
    }


def parse_general(raw, case):
    q = case["questions"][0]
    qtype = q["type"]
    try:
        obj = json.loads(raw)
        content = obj["choices"][0]["message"]["content"]
    except Exception:  # noqa: BLE001
        return None, ERR_PARSE
    if content is None or not str(content).strip():
        return None, ERR_EMPTY
    text = str(content).strip()
    up = text.upper()

    if qtype == "noul":
        if re.search(r"\bYES\b", up):
            label = "yes"
        elif re.search(r"\bNO\b", up):
            label = "no"
        else:
            return None, ERR_PARSE
        probs = {"yes": 1.0, "no": 0.0} if label == "yes" \
            else {"yes": 0.0, "no": 1.0}
        score = None
    elif qtype == "choice":
        keys = list(case["questions"][0]["criteria"].keys())
        found = None
        for k in keys:
            if re.search(rf"\b{re.escape(k)}\b", text, re.IGNORECASE):
                found = k
                break
        if found is None:
            # Fall back to the first label whose descriptive text appears.
            for k, v in case["questions"][0]["criteria"].items():
                for word in content_tokens(v)[:3]:
                    if word and word in text.lower():
                        found = k
                        break
                if found:
                    break
        if found is None:
            return None, ERR_PARSE
        lm = case["control"].get("label_map") or {}
        label = lm.get(found, found)
        probs = {lm.get(k, k): (1.0 if k == found else 0.0) for k in keys}
        score = None
    else:
        crit = case["questions"][0]["criteria"]
        found = None
        for c in crit:
            if re.search(rf"\b{re.escape(c)}\b", text, re.IGNORECASE):
                found = c
                break
        if found is None:
            return None, ERR_PARSE
        label = found
        probs = {c: (1.0 if c == found else 0.0) for c in crit}
        score = None

    return {
        "raw_content": text,
        "label": label,
        "probabilities": probs,
        "score": score,
        "max_prob": max(probs.values()),
        "confidence_reported": None,
        "confidence_formula": confidence_formula(probs),
        "normalised": abs(sum(probs.values()) - 1.0) > 0.02,
        "prob_sum": round(sum(probs.values()), 6),
    }, None


def run_all(cases, writer, api_key=None, general_url=ZEN_CHAT_URL,
            general_model=GENERAL_MODEL, limit=None, skip_general=False):
    prior = fit_prior(cases)
    subset = cases[:limit] if limit else cases
    print(f"  prior fitted on train: {prior}")
    offline = (("prior", lambda c: run_prior(c, prior)),
               ("rule", run_rule),
               ("lexical", run_lexical))
    for i, case in enumerate(subset, 1):
        for name, fn in offline:
            try:
                pred = fn(case)
                row = make_result(
                    case=case, mechanism=name, body=None, endpoint=None,
                    model_id=name, http_status=None,
                    raw=json.dumps({"offline": True, "branch":
                                    pred.get("rule_branch"),
                                    "train_distribution":
                                    pred.get("train_distribution")},
                                   sort_keys=True),
                    parsed={"offline": True,
                            "rule_branch": pred.get("rule_branch")},
                    prediction=pred, typed_error=None, error_detail=None,
                    usage=None, latency_ms=0.0, attempts=0, retries=0)
            except Exception as e:  # noqa: BLE001
                row = make_result(
                    case=case, mechanism=name, body=None, endpoint=None,
                    model_id=name, http_status=None, raw="", parsed=None,
                    prediction=None, typed_error="internal_error",
                    error_detail=f"{type(e).__name__}: {e}"[:200],
                    usage=None, latency_ms=0.0, attempts=0, retries=0)
            writer.write(row)

        if not skip_general:
            try:
                body = build_general_request(case, general_model)
                if not api_key:
                    row = make_result(
                        case=case, mechanism="general_model", body=body,
                        endpoint=general_url, model_id=general_model,
                        http_status=None, raw="", parsed=None,
                        prediction=None, typed_error=ERR_NOT_ATTEMPTED,
                        error_detail=f"{API_KEY_ENV} not set",
                        usage=None, latency_ms=None, attempts=0, retries=0)
                else:
                    resp = post_json(general_url, body, api_key,
                                     session_id=SESSION_ID)
                    if resp["typed_error"] is None:
                        pred, perr = parse_general(resp["raw_response"], case)
                        if perr:
                            resp["typed_error"] = perr
                            resp["error_detail"] = (
                                "200 OK but reply did not match a candidate")
                            parsed = None
                        else:
                            parsed = {"raw_content": pred["raw_content"],
                                      "hard_label": True}
                            pred = {k: v for k, v in pred.items()
                                    if k != "raw_content"}
                    else:
                        parsed, pred = None, None
                    row = make_result(
                        case=case, mechanism="general_model", body=body,
                        endpoint=general_url, model_id=general_model,
                        http_status=resp["http_status"],
                        raw=resp["raw_response"], parsed=parsed,
                        prediction=pred, typed_error=resp["typed_error"],
                        error_detail=resp["error_detail"],
                        usage=resp["usage"], latency_ms=resp["latency_ms"],
                        attempts=resp["attempts"], retries=resp["retries"])
            except Exception as e:  # noqa: BLE001
                row = make_result(
                    case=case, mechanism="general_model", body=None,
                    endpoint=general_url, model_id=general_model,
                    http_status=None, raw="", parsed=None, prediction=None,
                    typed_error="internal_error",
                    error_detail=f"{type(e).__name__}: {e}"[:200],
                    usage=None, latency_ms=None, attempts=0, retries=0)
            writer.write(row)

        if i % 10 == 0 or i == len(subset):
            print(f"  baselines {i}/{len(subset)}", flush=True)
    return writer.n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default=os.path.join(ROOT, "cases.ndjson"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results",
                                                   "baselines_raw.ndjson"))
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--skip-general", action="store_true")
    ap.add_argument("--general-url", default=ZEN_CHAT_URL,
                    help="chat/completions route for the general-model "
                         "baseline. Defaults to the Zen route; see the "
                         "preflight record for why the Go route 403s.")
    ap.add_argument("--general-model", default=GENERAL_MODEL)
    args = ap.parse_args()

    key = os.environ.get(API_KEY_ENV)
    cases = load_cases(args.cases)
    print(f"run_baselines: {len(cases)} cases -> {args.out}")
    print(f"  general-model route={args.general_url} model={args.general_model}"
          f" key_env={API_KEY_ENV}({'set' if key else 'MISSING'})")
    with NdjsonWriter(args.out) as w:
        n = run_all(cases, w, api_key=key, general_url=args.general_url,
                    general_model=args.general_model, limit=args.limit,
                    skip_general=args.skip_general)
    print(f"run_baselines: wrote {n} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
