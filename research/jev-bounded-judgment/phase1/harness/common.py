#!/usr/bin/env python3
"""Shared harness layer: HTTP with retries, request hashing, answer parsing.

Stdlib only. Two properties matter for the rest of the harness:

1. `post_json` never raises. Every outcome -- success, non-retryable 4xx,
   exhausted 5xx, timeout, DNS/TLS failure -- comes back as a dict, so the
   runner can always emit a result row and the case x mechanism grid stays
   complete.
2. `request_hash` hashes the bytes as actually serialised, NOT a key-sorted
   canonical form. That matters: the `option_reorder` control differs from its
   base only in JSON key order, and a sort_keys hash would collide them.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

HARNESS_VERSION = "1.0.0"
RESULT_SCHEMA_VERSION = "jevp1-result-1.0"

# Cloudflare rejects urllib's default User-Agent with "error code: 1010"
# (measured, preflight P5). An explicit UA is mandatory for reproducibility.
USER_AGENT = "curl/8.5.0"

MAX_ATTEMPTS = 3
BACKOFF_SECONDS = (1.0, 2.0, 4.0)      # fixed, no jitter: keeps runs comparable
TIMEOUT_SECONDS = 90

# Typed error codes, mirrored in schema.md 3.2.
ERR_4XX = "http_4xx"
ERR_5XX = "http_5xx"
ERR_429 = "http_429"
ERR_TIMEOUT = "network_timeout"
ERR_NETWORK = "network_error"
ERR_PARSE = "parse_error"
ERR_EMPTY = "empty_content"
ERR_NOT_ATTEMPTED = "not_attempted"
ERR_INTERNAL = "internal_error"

MECHANISMS = ("prior", "rule", "lexical", "jev", "general_model")


def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def serialise(body):
    """Exact wire bytes for a request body. Insertion order preserved."""
    return json.dumps(body, ensure_ascii=False, separators=(",", ":"))


def request_hash(body):
    return "sha256:" + hashlib.sha256(
        serialise(body).encode("utf-8")).hexdigest()


def classify(status, exc=None):
    if status is None:
        return ERR_NETWORK
    if status == 429:
        return ERR_429
    if 400 <= status < 500:
        return ERR_4XX
    if status >= 500:
        return ERR_5XX
    return None


def post_json(url, body, api_key, session_id=None, max_attempts=MAX_ATTEMPTS,
              timeout=TIMEOUT_SECONDS):
    """POST with bounded retries. Returns a dict; never raises."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }
    if session_id:
        headers["x-opencode-session"] = session_id
    payload = serialise(body).encode("utf-8")
    attempts, retries = 0, 0
    last = {"http_status": None, "raw_response": "", "typed_error": ERR_NETWORK,
            "error_detail": None, "usage": None}

    while attempts < max_attempts:
        attempts += 1
        req = urllib.request.Request(url, data=payload, method="POST",
                                     headers=headers)
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read().decode("utf-8", "replace")
                last = {
                    "http_status": r.status,
                    "raw_response": raw,
                    "typed_error": classify(r.status),
                    "error_detail": None,
                    "usage": _extract_usage(raw),
                    "latency_ms": round((time.monotonic() - t0) * 1000.0, 1),
                }
            break
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            code = classify(e.code)
            last = {
                "http_status": e.code,
                "raw_response": raw,
                "typed_error": code,
                "error_detail": f"HTTP {e.code}",
                "usage": _extract_usage(raw),
                "latency_ms": round((time.monotonic() - t0) * 1000.0, 1),
            }
            # 4xx other than 429 is a contract error: retrying cannot help.
            if code in (ERR_4XX,):
                break
        except TimeoutError:
            last = {"http_status": None, "raw_response": "",
                    "typed_error": ERR_TIMEOUT,
                    "error_detail": "socket timeout",
                    "usage": None,
                    "latency_ms": round((time.monotonic() - t0) * 1000.0, 1)}
        except urllib.error.URLError as e:
            reason = getattr(e, "reason", e)
            is_timeout = isinstance(reason, TimeoutError)
            last = {"http_status": None, "raw_response": "",
                    "typed_error": ERR_TIMEOUT if is_timeout else ERR_NETWORK,
                    "error_detail": f"URLError: {type(reason).__name__}",
                    "usage": None,
                    "latency_ms": round((time.monotonic() - t0) * 1000.0, 1)}
        except Exception as e:  # noqa: BLE001 - harness must never die here
            last = {"http_status": None, "raw_response": "",
                    "typed_error": ERR_INTERNAL,
                    "error_detail": f"{type(e).__name__}: {e}"[:200],
                    "usage": None,
                    "latency_ms": round((time.monotonic() - t0) * 1000.0, 1)}

        if attempts < max_attempts and last["typed_error"] in (ERR_429,
                                                              ERR_5XX,
                                                              ERR_TIMEOUT,
                                                              ERR_NETWORK):
            retries += 1
            time.sleep(BACKOFF_SECONDS[min(attempts - 1,
                                            len(BACKOFF_SECONDS) - 1)])
        else:
            break

    last["attempts"] = attempts
    last["retries"] = retries
    return last


def _extract_usage(raw):
    """Pull usage tokens out of a response body without failing on odd bodies."""
    try:
        obj = json.loads(raw)
    except Exception:  # noqa: BLE001
        return None
    u = obj.get("usage")
    if not isinstance(u, dict):
        return None
    return {
        "input_tokens": u.get("input_tokens", u.get("prompt_tokens")),
        "output_tokens": u.get("output_tokens", u.get("completion_tokens")),
        "total_tokens": u.get("total_tokens"),
        "raw": u,
    }


# ---------------------------------------------------------------------------
# Jev answer parsing
# ---------------------------------------------------------------------------
def confidence_formula(probabilities):
    """Recompute (n*max(p)-1)/(n-1), clamped. None for n < 2."""
    if not probabilities or len(probabilities) < 2:
        return None
    n = len(probabilities)
    mx = max(probabilities.values())
    v = (n * mx - 1.0) / (n - 1.0)
    return max(0.0, min(1.0, v))


def label_map_for(case):
    return case["control"].get("label_map") or {}


def parse_jev(raw, case):
    """Parse a systemone body into `parsed` + `prediction`.

    Returns (parsed, prediction, typed_error). `prediction` is None on failure.
    Label-space normalisation:
      * noul   -> noul is P(yes); expand to {yes, no}
      * choice -> map option keys back through control.label_map
      * score  -> map stringified indices through the response legend
    """
    q = case["questions"][0]
    qtype = q["type"]
    try:
        obj = json.loads(raw)
    except Exception:  # noqa: BLE001
        return None, None, ERR_PARSE
    answers = obj.get("answers")
    if not isinstance(answers, dict) or "q" not in answers:
        return None, None, ERR_PARSE
    a = answers["q"]
    if not isinstance(a, dict) or a.get("type") != qtype:
        return (None, None, ERR_PARSE)

    parsed = {
        "type": a.get("type"),
        "noul": a.get("noul"),
        "choice": a.get("choice"),
        "score": a.get("score"),
        "confidence": a.get("confidence"),
        "legend": a.get("legend"),
        "probabilities_raw": a.get("probabilities"),
    }

    if qtype == "noul":
        noul = a.get("noul")
        if not isinstance(noul, (int, float)):
            return parsed, None, ERR_PARSE
        probs = {"yes": float(noul), "no": 1.0 - float(noul)}
        label = "yes" if noul >= 0.5 else "no"
        score_val = None
    elif qtype == "choice":
        praw = a.get("probabilities")
        if not isinstance(praw, dict) or not praw:
            return parsed, None, ERR_PARSE
        lm = label_map_for(case)
        probs = {}
        for k, v in praw.items():
            try:
                fv = float(v)
            except (TypeError, ValueError):
                return parsed, None, ERR_PARSE
            probs[lm.get(k, k)] = fv
        label = lm.get(a.get("choice"), a.get("choice"))
        score_val = None
        if label not in probs and probs:
            label = max(probs.items(), key=lambda kv: (kv[1], kv[0]))[0]
    else:  # score
        praw = a.get("probabilities")
        legend = a.get("legend") or {}
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
                crit = q["criteria"]
                try:
                    name = crit[int(k)]
                except (ValueError, IndexError, TypeError):
                    return parsed, None, ERR_PARSE
            probs[name] = fv
        score_val = a.get("score")
        label = (max(probs.items(), key=lambda kv: (kv[1], kv[0]))[0]
                 if probs else None)

    total = sum(probs.values())
    prediction = {
        "label": label,
        "probabilities": probs,
        "score": score_val,
        "max_prob": (max(probs.values()) if probs else None),
        "confidence_reported": a.get("confidence"),
        "confidence_formula": confidence_formula(probs),
        "normalised": bool(abs(total - 1.0) > 0.02) if probs else None,
        "prob_sum": round(total, 6) if probs else None,
    }
    return parsed, prediction, None


def make_result(case, mechanism, body, endpoint, model_id, http_status,
                raw, parsed, prediction, typed_error, error_detail, usage,
                latency_ms, attempts, retries):
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "case_id": case["id"],
        "mechanism": mechanism,
        "request_hash": request_hash(body) if body is not None else None,
        "request_body": body,
        "endpoint": endpoint,
        "model_id": model_id,
        "http_status": http_status,
        "raw_response": raw,
        "parsed": parsed,
        "prediction": prediction,
        "abstained": False,
        "latency_ms": latency_ms,
        "usage": usage,
        "typed_error": typed_error,
        "error_detail": error_detail,
        "attempt": attempts,
        "retries": retries,
        "timestamp_utc": utc_now_iso(),
        "harness_version": HARNESS_VERSION,
        "secrets_recorded": False,
    }


class NdjsonWriter:
    """Append-only NDJSON writer that flushes every row."""

    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._f = open(path, "w", encoding="utf-8", newline="\n")
        self.n = 0

    def write(self, row):
        self._f.write(json.dumps(row, ensure_ascii=False,
                                 separators=(",", ":")) + "\n")
        self._f.flush()
        self.n += 1

    def close(self):
        self._f.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def load_cases(path):
    cases = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    cases.sort(key=lambda c: c["id"])
    return cases
