#!/usr/bin/env python3
"""Bounded Jev free-tier availability probe series (issue #565, followup-03).

WHY THIS EXISTS
---------------
The first followup-03 block issued 197 sequential Jev calls between 06:34:53Z
and 06:36:35Z. Every one failed: 125 HTTP 403 `server_error` ("Upstream
response was not valid JSON") followed by 72 HTTP 429. The question this
script answers is narrow and operational only:

    Is the Jev free tier accepting calls at all, right now?

It is deliberately NOT a measurement phase. It emits no row that any latency,
throughput, token or cost statistic may consume, and it is written to a
SEPARATE file (`results/jev_ratelimit_probes.ndjson`) from the measurement
NDJSON for exactly that reason.

DISCIPLINE (all of it is the point)
-----------------------------------
* ONE attempt per probe. No retry, ever, not even on a transport error. A
  retried probe would be indistinguishable from load and would destroy the
  very signal being measured.
* Probes are spaced >= MIN_GAP_SECONDS apart (default 60). Hammering a
  rate-limited endpoint is not a workaround, it is a confound.
* At most MAX_PROBES probes (default 10), then the series stops and reports
  what it saw.
* The series STOPS EARLY on the first probe that returns a usable answer.
  Probing a recovered endpoint past that point would consume the very
  headroom the paced measurement block needs.
* The probe reuses the harness's own `run_one`, so the request shape, the
  headers, the timeout and the curl instrumentation are byte-identical to a
  grid call. If the probe fails, the grid call would have failed too; the
  probe is therefore a valid availability witness.
* Cases are drawn in the frozen canonical subset order, cycling, and the case
  id is recorded per probe.
* The credential is resolved at runtime and passed to curl on stdin. No
  credential value is printed, logged, or written here; only the source
  LABEL is recorded.

FIELDS PER PROBE ROW
--------------------
timestamp_utc, seconds_since_previous_attempt, probe_index, case_id,
http_status, typed_error, error_detail, error_code, message,
curl_time_total_seconds, curl_time_starttransfer_seconds, bytes,
usable_answer (200 + parseable label/score), raw_response_excerpt.

Usage
-----
    python3 harness/jev_ratelimit_probe.py                    # 10 probes, 60s
    python3 harness/jev_ratelimit_probe.py --max-probes 4 --min-gap 90
    python3 harness/jev_ratelimit_probe.py --once             # a single probe

Run it DETACHED with a foreground heartbeat monitor. Do not run it in a
silent foreground pipeline: the inter-probe gap is minutes of sleeping by
design, and a foreground command with no stream output for minutes is
indistinguishable from a hang.
"""

import argparse
import calendar
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import run_ops as R  # noqa: E402  (path set above; stdlib + curl only)

PROBE_PATH = os.path.join(R.RESULTS, "jev_ratelimit_probes.ndjson")
SCHEMA = "jevp1-ops-ratelimit-probe-1.0"
MIN_GAP_SECONDS = 60
MAX_PROBES = 10
# An error body is recorded verbatim up to this many characters. Error bodies
# from this endpoint carry no credential, but the cap keeps the file small and
# makes it obvious that only the failure surface is being captured.
EXCERPT_CHARS = 400


def epoch_from_iso(value):
    """Seconds since the epoch for a `...Z` timestamp this script wrote.

    Returns None on anything unexpected: an unparseable prior timestamp must
    degrade to "no gap information", never to a guessed gap.
    """
    if not value:
        return None
    try:
        return float(calendar.timegm(time.strptime(value, "%Y-%m-%dT%H:%M:%SZ")))
    except (TypeError, ValueError):
        return None


def parse_existing(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                continue
    return rows


def error_surface(raw):
    """Pull the error code/message out of an error body, if it is JSON."""
    code = message = None
    if not raw:
        return code, message
    try:
        doc = json.loads(raw)
    except ValueError:
        return code, (raw[:EXCERPT_CHARS] or None)
    err = doc.get("error") if isinstance(doc, dict) else None
    if isinstance(err, dict):
        code = err.get("code")
        message = err.get("message")
    if code is None and message is None and isinstance(doc, dict):
        code = doc.get("code")
        message = doc.get("message")
    return code, message


def one_probe(mech, case, index, prev_ts):
    """Exactly one call. Returns the row. Never retries."""
    key = R.resolve_credential(R.MECH[mech]["credential_source"])
    if not key:
        raise SystemExit("FATAL: credential did not resolve at probe time.")
    started = time.time()
    row = R.run_one(mech, case, key, "probe_ratelimit", index, concurrency=1,
                    block="ratelimit_probe")
    tm = (row.get("curl_phases") or {})
    code, message = error_surface(row.get("raw_response"))
    usable = (row.get("http_status") == 200
              and not row.get("typed_error")
              and (row.get("parsed_label") is not None
                   or row.get("parsed_score") is not None))
    return {
        "schema_version": SCHEMA,
        "what_this_is": "One bounded availability probe against the Jev free "
                        "tier. Not a measurement phase: no statistic may "
                        "consume this row.",
        "probe_index": index,
        "timestamp_utc": R.utc_now_iso(),
        "seconds_since_previous_attempt": (None if prev_ts is None
                                           else round(started - prev_ts, 1)),
        "mechanism": mech,
        "model_id": row.get("model_id"),
        "model_catalog_id": row.get("model_catalog_id"),
        "endpoint": row.get("endpoint"),
        "case_id": case["id"],
        "question_type": case.get("question_type"),
        "attempts": 1,
        "retries": 0,
        "http_status": row.get("http_status"),
        "typed_error": row.get("typed_error"),
        "error_detail": row.get("error_detail"),
        "error_code": code,
        "error_message": message,
        "usable_answer": usable,
        "curl_time_starttransfer_seconds": tm.get("time_starttransfer"),
        "curl_time_total_seconds": tm.get("time_total"),
        "bytes": row.get("bytes"),
        "raw_response_excerpt": (row.get("raw_response") or "")[:EXCERPT_CHARS],
        "credential_source": R.MECH[mech]["credential_source"],
        "secrets_recorded": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mechanism", default=R.JEV, choices=list(R.MECHANISMS))
    ap.add_argument("--max-probes", type=int, default=MAX_PROBES)
    ap.add_argument("--min-gap", type=float, default=MIN_GAP_SECONDS)
    ap.add_argument("--once", action="store_true",
                    help="exactly one probe, then exit (ignores --min-gap)")
    args = ap.parse_args()

    _, _, cases, ordered, _sel = R.load_frozen_subset()
    by_id = {c["id"]: c for c in cases}
    os.makedirs(R.RESULTS, exist_ok=True)

    prior = parse_existing(PROBE_PATH)
    prev_ts = None
    if prior:
        prev_ts = epoch_from_iso(prior[-1].get("timestamp_utc"))
    already = len(prior)

    budget = 1 if args.once else args.max_probes
    if budget < 1:
        raise SystemExit("--max-probes must be >= 1")
    if not args.once and args.min_gap < MIN_GAP_SECONDS:
        raise SystemExit(
            f"REFUSING: --min-gap {args.min_gap}s is below the {MIN_GAP_SECONDS}s "
            "floor. A tighter gap would hammer a rate-limited endpoint and "
            "confound the signal this series exists to measure.")

    print(f"ratelimit probe: {args.mechanism} up_to={budget} "
          f"min_gap={args.min_gap}s prior_probes_on_file={already} "
          f"file={PROBE_PATH}", flush=True)

    n_ok = 0
    with open(PROBE_PATH, "a", encoding="utf-8") as out:
        for i in range(1, budget + 1):
            if not args.once and prev_ts is not None:
                wait = args.min_gap - (time.time() - prev_ts)
                while wait > 0:
                    step = min(20.0, wait)
                    print(f"  waiting {wait:.0f}s before probe {i} "
                          f"(gap floor {args.min_gap:.0f}s honoured)", flush=True)
                    time.sleep(step)
                    wait = args.min_gap - (time.time() - prev_ts)
            cid = ordered[(already + i - 1) % len(ordered)]
            row = one_probe(args.mechanism, by_id[cid], already + i, prev_ts)
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            prev_ts = time.time()
            print(f"probe {row['probe_index']} {row['timestamp_utc']} "
                  f"gap={row['seconds_since_previous_attempt']} "
                  f"case={cid} http={row['http_status']} "
                  f"err={row['typed_error']} code={row['error_code']} "
                  f"usable={row['usable_answer']}", flush=True)
            if row["usable_answer"]:
                n_ok += 1
                print("SERIES STOPPING EARLY: a probe returned a usable answer. "
                      "Probing further would consume the headroom the paced "
                      "measurement block needs.", flush=True)
                break

    print(f"ratelimit probe: series complete, {n_ok} usable answer(s); "
          f"{len(parse_existing(PROBE_PATH))} probe row(s) on file", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
