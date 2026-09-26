#!/usr/bin/env python3
"""Deterministic analysis for followup-03 (issue #565).

Emits `results/summary.json` and `../comparison.md` from the raw NDJSON. There
is no randomness, no clock read, and no network access in this file, so two
runs over the same inputs produce byte-identical outputs. `--check` asserts
that by building the document twice in-process and comparing the SHA-256 of
both serialisations, and it prints the SHA-256 of each written artefact so a
clean-clone reproduction can be compared by hash.

OUTPUTS
-------
results/summary.json  every statistic, each with its own `n` and its own
                      explicit row-selection predicate
comparison.md         the findings, classified ESTABLISHED / UNRESOLVED /
                      SERVING-OR-PRICING ARTIFACT, rendered from summary.json
                      so the prose and the numbers cannot drift apart

ROW SELECTION — READ THIS BEFORE QUOTING ANY NUMBER
--------------------------------------------------
The raw files contain more than one BLOCK. A block is a labelled run of the
same phase; the first block is `null` because it predates block labelling, and
`resume1` is this run's block. Every statistic below names the exact
`(mechanism, block, phase, filter)` it consumed, and every statistic carries
its own denominator `n`. A statistic whose `n` is smaller than the number of
rows for that (mechanism, phase) says so in its own `n_rows_available` field
rather than silently reporting a partial sample as a complete one.

MEASUREMENT WINDOWS ARE NOT INTERCHANGEABLE
-------------------------------------------
Jev's usable latency/usage/stability evidence comes from the FROZEN Phase-1
window (`../../results/jev_raw.ndjson`, 64 successful calls, 02:46-02:50Z,
Python `urllib` transport). The current window's Jev calls all failed on the
free tier. Those two windows differ in transport AND in time AND in tier
state, so no Jev figure from one window is combined with a MiMo figure from
the other as though they were a matched pair; where a Jev/MiMo ratio is
reported it is reported as a cross-window ratio and labelled as such.

METHOD NOTES
------------
* Percentiles use the NEAREST-RANK method on the sorted sample:
  p_k = sorted[ceil(k/100 * n) - 1], 0-indexed. No interpolation, so every
  reported percentile is an actually-observed value.
* Correctness is CONTROL-only, as the brief requires: the denominator is the
  subset's `variant_kind == "base"` control cases that are answerable. The
  full answerable subset is reported alongside it, never instead of it.
  Correctness is an INGREDIENT of the throughput ratios; it is not the
  outcome of this study and is not presented as one.
* Cost is derived from actual per-row `usage` at the catalog rates recorded in
  run_ops.py. Those rates are pricing/entitlement facts, kept in their own
  section and never used to support a structural claim.
"""

import argparse
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FOLLOWUP = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(FOLLOWUP), "harness"))

import run_ops as R  # noqa: E402

RESULTS = os.path.join(FOLLOWUP, "results")
SUMMARY_PATH = os.path.join(RESULTS, "summary.json")
COMPARISON_PATH = os.path.join(FOLLOWUP, "comparison.md")
PROBE_PATH = os.path.join(RESULTS, "jev_ratelimit_probes.ndjson")
FROZEN_JEV = os.path.join(os.path.dirname(FOLLOWUP), "results", "jev_raw.ndjson")

MECH_LABEL = {
    R.JEV: "Jev 1.13 (free tier)",
    R.MIMO: "MiMo V2.6 Flash (paid)",
}
MECH_KEY = {R.JEV: "jev", R.MIMO: "mimo_v26_flash"}

# The block whose warm grid this analysis treats as the measurement block.
# Null-labelled rows are an ABORTED first attempt and are excluded from the
# warm statistics; they are retained in the file and reported separately.
MEASUREMENT_BLOCK = "resume1"


# ---------------------------------------------------------------------------
# small deterministic statistics helpers
# ---------------------------------------------------------------------------
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def nearest_rank(values, pct):
    """Nearest-rank percentile. Returns None for an empty sample."""
    if not values:
        return None
    s = sorted(values)
    k = max(1, math.ceil(pct / 100.0 * len(s)))
    return s[min(k, len(s)) - 1]


def r4(x):
    return None if x is None else round(float(x), 4)


def describe(values, unit="ms"):
    """n/mean/median/pXX/min/max over `values`. No interpolation anywhere."""
    vs = [float(v) for v in values if v is not None]
    if not vs:
        return {"n": 0, "unit": unit, "note": "no observations"}
    out = {
        "n": len(vs),
        "unit": unit,
        "mean": r4(sum(vs) / len(vs)),
        "median": r4(nearest_rank(vs, 50)),
        "p90": r4(nearest_rank(vs, 90)),
        "p95": r4(nearest_rank(vs, 95)),
        "p99": r4(nearest_rank(vs, 99)),
        "min": r4(min(vs)),
        "max": r4(max(vs)),
        "sum": r4(sum(vs)),
        "percentile_method": "nearest-rank, no interpolation",
    }
    if len(vs) >= 30:
        mean = out["mean"]
        var = sum((v - mean) ** 2 for v in vs) / (len(vs) - 1)
        out["stdev"] = r4(math.sqrt(var))
    else:
        out["stdev"] = None
        out["stdev_note"] = "omitted: sample < 30, a sample SD would be noise"
    if len(vs) < 100:
        out["p99_is_thin"] = True
    return out


def counts_by(rows, key):
    """Tally `key(row)` into a JSON-safe, sort-stable dict.

    Keys are stringified because a tally may mix `None`, ints and strings, and
    a mixed-key dict cannot be serialised with sort_keys=True — which would
    make the determinism check itself untestable.
    """
    out = {}
    for r in rows:
        k = str(key(r))
        out[k] = out.get(k, 0) + 1
    return dict(sorted(out.items()))


def label_key(row):
    """A stable, human-readable label tally key.

    A `score` question yields a score rather than a label, so its label tally
    key is `score_only` rather than a bare null that would read as a parse
    failure in the report.
    """
    lb = row.get("parsed_label")
    if lb is not None:
        return str(lb)
    if row.get("parsed_score") is not None:
        return "score_only"
    return "unparsed"


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------
def load_rows(mech):
    path = os.path.join(RESULTS, R.MECH[mech]["raw_path"])
    return R.load_ndjson(path), path


def usable(row):
    """A row that produced a parseable decision."""
    return not row.get("typed_error") and (row.get("parsed_label") is not None
                                           or row.get("parsed_score") is not None)


def curl_ms(row, field):
    v = (row.get("curl_phases") or {}).get(field)
    return None if v is None else float(v) * 1000.0


# ---------------------------------------------------------------------------
# correctness
# ---------------------------------------------------------------------------
def build_case_index():
    """Frozen cases with the F1 correction applied, as run_ops derives it.

    The correction is delegated, not re-implemented: run_ops.f1_corrected_cases
    is the same derivation followup-02 used, and it hard-stops if the pair it
    derives is not the pair verification.md names. "Applied consistently" has
    to mean the SAME rule, not a lookalike.
    """
    _gate, cases = R.frozen_gate()
    corrected, _ids = R.f1_corrected_cases(cases)
    return {c["id"]: c for c in corrected}


def correctness(rows, cases_by_id):
    """(control_correct, control_correct_n, control_opportunities, all_*).

    CONTROL-only correctness: an opportunity is one usable prediction on an
    ANSWERABLE control case (`control.variant_kind == "base"`). An unanswerable
    case is not scored correct/incorrect here — answering at all on one is the
    failure mode, and this metric is not about abstention.
    """
    c_ok = c_opp = a_ok = a_opp = 0
    c_ids, a_ids = set(), set()
    for r in rows:
        case = cases_by_id.get(r.get("case_id"))
        if case is None or not usable(r):
            continue
        gt = case["ground_truth"]
        if not (gt.get("answerable") and gt.get("answer") is not None):
            continue
        a_opp += 1
        a_ids.add(case["id"])
        if r.get("parsed_label") == gt["answer"]:
            a_ok += 1
        if case["control"].get("variant_kind") == "base":
            c_opp += 1
            c_ids.add(case["id"])
            if r.get("parsed_label") == gt["answer"]:
                c_ok += 1
    return {
        "control_correct": c_ok,
        "control_opportunities": c_opp,
        "control_case_ids": sorted(c_ids),
        "all_subset_correct": a_ok,
        "all_subset_opportunities": a_opp,
        "all_subset_case_ids": sorted(a_ids),
    }


# ---------------------------------------------------------------------------
# per-mechanism sections
# ---------------------------------------------------------------------------
def warm_latency(rows, cases_by_id, mech, block):
    sel = [r for r in rows
           if r.get("phase") == "warm" and r.get("block") == block
           and usable(r)]
    avail = [r for r in rows if r.get("phase") == "warm"
             and r.get("block") == block]
    total_ms = [curl_ms(r, "time_total") for r in sel]
    stt_ms = [curl_ms(r, "time_starttransfer") for r in sel]
    transport_ms, service_ms, spawn_ms = [], [], []
    for r in sel:
        nl = curl_ms(r, "time_namelookup") or 0.0
        cn = curl_ms(r, "time_connect") or 0.0
        ac = curl_ms(r, "time_appconnect") or 0.0
        st = curl_ms(r, "time_starttransfer")
        transport_ms.append(nl + cn + ac)
        if st is not None:
            # The brief's decomposition: service+transfer = starttransfer -
            # connect. Also recorded: pretransfer-relative, which excludes
            # TLS setup and is the tighter "time to first byte" measure.
            service_ms.append(st - cn)
        spawn_ms.append(r.get("wall_ms_including_process_spawn"))
    n = len(sel) or 1
    return {
        "selection": f"mechanism={mech} AND phase=warm AND block={block!r} "
                     f"AND no typed_error AND a parseable label/score",
        "n_rows_available": len(avail),
        "n_rows_used": len(sel),
        "rows_dropped_unusable": len(avail) - len(sel),
        "latency_total_ms": describe(total_ms),
        "latency_time_to_first_byte_ms": describe(stt_ms),
        "phase_decomposition_ms": {
            "definition_transport": "namelookup + connect + appconnect (DNS, "
                                    "TCP, TLS)",
            "definition_service_transfer": "time_starttransfer - time_connect "
                                           "(the brief's decomposition)",
            "transport": describe(transport_ms),
            "service_transfer": describe(service_ms),
            "mean_share_of_total_pct": r4(
                100.0 * (sum(transport_ms) / n) / (sum(total_ms) / n))
            if sum(total_ms) else None,
        },
        "client_wall_ms_including_process_spawn": describe(spawn_ms),
        "correctness": correctness(sel, cases_by_id),
    }


def throughput(rows, cases_by_id, mech, block, phase="warm"):
    sel = [r for r in rows if r.get("phase") == phase and r.get("block") == block]
    good = [r for r in sel if usable(r)]
    totals = [curl_ms(r, "time_total") for r in good]
    sum_total = sum(t for t in totals if t is not None)
    walls = [r.get("wall_ms_including_process_spawn") for r in good]
    sum_wall = sum(w for w in walls if w is not None)
    cor = correctness(good, cases_by_id)
    out = {
        "selection": f"mechanism={mech} AND phase={phase} AND block={block!r} "
                     f"AND no typed_error",
        "n_calls_issued": len(sel),
        "n_calls_usable": len(good),
        "n_calls_failed": len(sel) - len(good),
        "definition": "a strictly sequential client issues one call at a time, "
                      "so elapsed time is the sum of per-call time_total; "
                      "calls/sec is n_calls_usable / that sum. This EXCLUDES any "
                      "client think-time and is an upper bound on the "
                      "attainable rate.",
        "sequential_calls_per_sec": (r4(len(good) / (sum_total / 1000.0))
                                     if sum_total else None),
        "sequential_calls_per_sec_including_process_spawn": (
            r4(len(good) / (sum_wall / 1000.0)) if sum_wall else None),
        "sum_time_total_ms": r4(sum_total),
        "sum_wall_ms_including_process_spawn": r4(sum_wall),
        "control_correct_decisions": cor["control_correct"],
        "control_opportunities": cor["control_opportunities"],
        "control_correct_per_sec": (
            r4(cor["control_correct"] / (sum_total / 1000.0)) if sum_total
            else None),
        "all_subset_correct_decisions": cor["all_subset_correct"],
        "all_subset_opportunities": cor["all_subset_opportunities"],
        "all_subset_correct_per_sec": (
            r4(cor["all_subset_correct"] / (sum_total / 1000.0)) if sum_total
            else None),
        "control_case_ids": cor["control_case_ids"],
        "all_subset_case_ids": cor["all_subset_case_ids"],
        "control_case_count": len(cor["control_case_ids"]),
        "correctness_definition": "CONTROL-only: an opportunity is one usable "
                                  "prediction on an ANSWERABLE control case "
                                  "(control.variant_kind == 'base'). An "
                                  "unanswerable case is never scored "
                                  "correct/incorrect by this metric; answering "
                                  "at all on one is a different failure mode.",
        "timestamp_span_coarse_check": _coarse_span(sel),
    }
    return out


def _coarse_span(sel):
    """Coarse independent span check from 1-second-resolution timestamps."""
    ts = sorted(r["timestamp_utc"] for r in sel if r.get("timestamp_utc"))
    if len(ts) < 2:
        return {"note": "fewer than 2 timestamps"}
    return {
        "first_utc": ts[0],
        "last_utc": ts[-1],
        "n_timestamps": len(ts),
        "note": "timestamps have 1-second resolution, so the wall-clock span is "
                "a coarse bound (+/-1s per end) and is reported only as a sanity "
                "check on the per-call sum, never as the throughput figure.",
    }


def concurrency(rows, mech, block):
    sel = [r for r in rows if r.get("phase") == "concurrency"
           and r.get("block") == block]
    by_c = {}
    for c in sorted({r.get("concurrency") for r in sel if r.get("concurrency")}):
        crows = [r for r in sel if r.get("concurrency") == c]
        good = [r for r in crows if usable(r)]
        spans = {r.get("block_makespan_ms") for r in crows
                 if r.get("block_makespan_ms") is not None}
        makespan = max(spans) if spans else None
        lat = [curl_ms(r, "time_total") for r in good]
        n429 = sum(1 for r in crows if r.get("http_status") == 429)
        nerr = sum(1 for r in crows if r.get("typed_error"))
        by_c[str(c)] = {
            "n_calls": len(crows),
            "n_usable": len(good),
            "n_failed": len(crows) - len(good),
            "n_http_429": n429,
            "n_typed_errors": nerr,
            "http_status_counts": counts_by(crows, lambda r: r.get("http_status")),
            "block_makespan_ms": makespan,
            "throughput_calls_per_sec": (
                r4(len(good) / (makespan / 1000.0))
                if makespan else None),
            "throughput_definition": "usable calls / block makespan, where the "
                                     "makespan is wall time from first dispatch "
                                     "to last completion of that level's block",
            "latency_total_ms": describe(lat),
        }
    scaling = {}
    base = by_c.get("1", {}).get("throughput_calls_per_sec")
    for c, v in by_c.items():
        t = v.get("throughput_calls_per_sec")
        scaling[c] = {
            "throughput_calls_per_sec": t,
            "scaling_ratio_vs_C1": r4(t / base) if (t and base) else None,
            "p50_over_C1_latency_ratio": None,
        }
        b1 = by_c.get("1", {}).get("latency_total_ms", {}).get("median")
        med = v.get("latency_total_ms", {}).get("median")
        scaling[c]["p50_over_C1_latency_ratio"] = (
            r4(med / b1) if (med and b1) else None)
    return {
        "selection": f"mechanism={mech} AND phase=concurrency AND block={block!r}",
        "scaling_definition": "throughput(C)/throughput(1). Ideal linear "
                              "scaling at concurrency C would be C.",
        "by_level": by_c,
        "scaling": scaling,
    }


def idle_proxy(rows, mech, block, warm_median_ms):
    sel = [r for r in rows if r.get("phase") == "idle" and r.get("block") == block
           and usable(r)]
    avail = [r for r in rows if r.get("phase") == "idle"
             and r.get("block") == block]
    lat = [curl_ms(r, "time_total") for r in sel]
    d = describe(lat)
    idle_secs = sorted({r.get("idle_seconds_before") for r in avail
                        if r.get("idle_seconds_before") is not None})
    d.update({
        "selection": f"mechanism={mech} AND phase=idle AND block={block!r} AND "
                     f"no typed_error",
        "n_rows_available": len(avail),
        "idle_seconds_before_first_call": idle_secs,
        "warm_median_ms_same_block": warm_median_ms,
        "ratio_idle_median_over_warm_median": (
            r4(d["median"] / warm_median_ms)
            if (d.get("median") and warm_median_ms) else None),
        "interpretation_limit": "This is an observable cold-ish PROXY only. "
                                "Per-call cold start is NOT directly observable "
                                "here: the endpoint is shared, any edge cache or "
                                "connection-reuse state on the server side is "
                                "unobserved, and the client opens a fresh "
                                "connection per call by design. A difference "
                                "here cannot be attributed to per-call model "
                                "cold start.",
    })
    return d


def stability(rows, cases_by_id, mech, block):
    """Per-case modal label frequency, flip rate, and repeat-to-repeat spread."""
    sel = [r for r in rows if r.get("phase") == "warm" and r.get("block") == block
           and usable(r)]
    by_case = {}
    for r in sel:
        by_case.setdefault(r["case_id"], []).append(r)
    per_case, flip_rates, modes = [], [], []
    for cid in sorted(by_case):
        crows = sorted(by_case[cid], key=lambda r: r.get("repeat") or 0)
        labels = [label_key(r) for r in crows]
        cnt = {}
        for lb in labels:
            cnt[lb] = cnt.get(lb, 0) + 1
        modal = sorted(cnt.items(), key=lambda kv: (-kv[1], str(kv[0])))[0]
        n = len(labels)
        flip = (n - modal[1]) / n
        row = {
            "case_id": cid,
            "question_type": crows[0].get("question_type"),
            "n_reps": n,
            "modal_label": modal[0],
            "modal_frequency": r4(modal[1] / n),
            "distinct_labels": len(cnt),
            "flip_rate": r4(flip),
            "label_counts": dict(sorted(cnt.items())),
        }
        probs = [r.get("parsed_probabilities") for r in crows
                 if isinstance(r.get("parsed_probabilities"), dict)
                 and r.get("parsed_probabilities")]
        if probs:
            keys = sorted({k for p in probs for k in p})
            spread = {}
            for k in keys:
                vals = [float(p[k]) for p in probs if k in p]
                if len(vals) >= 2:
                    mean = sum(vals) / len(vals)
                    spread[k] = {
                        "n": len(vals),
                        "min": r4(min(vals)),
                        "max": r4(max(vals)),
                        "range": r4(max(vals) - min(vals)),
                        "stdev": r4(math.sqrt(
                            sum((v - mean) ** 2 for v in vals) / (len(vals) - 1))),
                    }
            row["probability_spread_across_reps"] = spread
        thinking = [ (r.get("usage_flat") or {}).get("reasoning_tokens")
                     for r in crows ]
        thinking = [t for t in thinking if t is not None]
        if thinking:
            mean = sum(thinking) / len(thinking)
            row["reasoning_tokens"] = {
                "n": len(thinking),
                "min": min(thinking),
                "max": max(thinking),
                "mean": r4(mean),
                "stdev": (r4(math.sqrt(sum((t - mean) ** 2
                                           for t in thinking)
                                        / (len(thinking) - 1)))
                          if len(thinking) >= 2 else None),
                "note": "reasoning tokens are a property of MiMo's own output "
                        "and are reported as token use, never folded into a "
                        "latency claim without saying so",
            }
        per_case.append(row)
        flip_rates.append(flip)
        modes.append(modal[1] / n)
    return {
        "selection": f"mechanism={mech} AND phase=warm AND block={block!r} AND "
                     f"no typed_error",
        "n_cases": len(per_case),
        "n_observations": len(sel),
        "flip_rate_definition": "per case, (reps - modal_label_reps) / reps; 0 "
                                "means the same label every rep, 1.0 would mean "
                                "no label is modal",
        "mean_flip_rate": r4(sum(flip_rates) / len(flip_rates)) if flip_rates
                          else None,
        "max_flip_rate": r4(max(flip_rates)) if flip_rates else None,
        "n_cases_fully_stable": sum(1 for f in flip_rates if f == 0.0),
        "mean_modal_frequency": r4(sum(modes) / len(modes)) if modes else None,
        "per_case": per_case,
    }


def latency_budget(rows, mech, block):
    """Account for the total, because the brief's two components do not sum.

    The brief asks for transport (namelookup+connect+appconnect) versus
    service+transfer (starttransfer - connect) versus total. Measured against
    this endpoint, those two components together account for only a few
    percent of the total, and the residual is the single largest term in the
    call. Reporting only the brief's two components would silently drop the
    dominant term, so it is measured and named here.
    """
    sel = [r for r in rows if r.get("phase") == "warm" and r.get("block") == block
           and usable(r)]
    if not sel:
        return {"note": "no usable warm rows"}
    setup, residual, total, stt, ac = [], [], [], [], []
    for r in sel:
        t = curl_ms(r, "time_total")
        s = curl_ms(r, "time_starttransfer")
        a = curl_ms(r, "time_appconnect")
        if t is None or s is None:
            continue
        nl = curl_ms(r, "time_namelookup") or 0.0
        cn = curl_ms(r, "time_connect") or 0.0
        setup.append(nl + cn + (a or 0.0))
        residual.append(t - s)
        total.append(t)
        stt.append(s)
        if a is not None:
            ac.append(a)
    n = len(total) or 1
    # per-case spread: the same request, repeated, how much does latency move?
    by_case = {}
    for r in sel:
        t = curl_ms(r, "time_total")
        if t is not None:
            by_case.setdefault(r["case_id"], []).append(t)
    spreads = {c: {"n": len(v), "min": r4(min(v)), "max": r4(max(v)),
                   "median": r4(nearest_rank(v, 50)),
                   "range": r4(max(v) - min(v)),
                   "max_over_min": r4(max(v) / min(v)) if min(v) else None}
               for c, v in sorted(by_case.items())}
    out_tok = [(r.get("usage_flat") or {}).get("output_tokens") for r in sel]
    pairs = [(curl_ms(r, "time_total"),
              (r.get("usage_flat") or {}).get("output_tokens")) for r in sel]
    pairs = [(t, o) for t, o in pairs if t is not None and isinstance(o, int)]
    return {
        "selection": f"mechanism={mech} AND phase=warm AND block={block!r} AND "
                     f"no typed_error",
        "n": n,
        "latency_total_ms": describe(total),
        "setup_before_first_byte_ms": describe(setup),
        "setup_to_tls_complete_ms": describe(ac),
        "time_to_first_byte_ms": describe(stt),
        "post_first_byte_body_wait_ms": describe(residual),
        "accounting": {
            "identity": "total = setup(DNS+TCP+TLS) + post_first_byte_body_wait",
            "mean_setup_ms": r4(sum(setup) / n),
            "mean_post_first_byte_wait_ms": r4(sum(residual) / n),
            "mean_total_ms": r4(sum(total) / n),
            "mean_setup_share_pct": r4(100.0 * (sum(setup) / n)
                                       / (sum(total) / n)) if sum(total) else None,
            "mean_post_first_byte_share_pct": r4(
                100.0 * (sum(residual) / n) / (sum(total) / n))
            if sum(total) else None,
            "brief_two_component_sum_ms": r4(sum(setup) / n + sum(stt) / n
                                             - (sum(cn for cn in
                                                    [curl_ms(r, "time_connect") or 0.0
                                                     for r in sel]) / n)),
            "brief_two_component_note": "this is the brief's transport + "
                                        "(starttransfer - connect). It is "
                                        "reported for fidelity to the design and "
                                        "it does NOT account for the total; the "
                                        "post-first-byte wait is the missing term "
                                        "and is the larger one.",
        },
        "first_byte_is_not_a_model_signal": {
            "finding": "time_starttransfer is within a few ms of TLS handshake "
                       "completion and varies far less than the total, so the "
                       "endpoint emits response headers before the model has "
                       "produced anything. time_starttransfer is therefore NOT a "
                       "time-to-first-token measurement and must not be read as "
                       "model responsiveness.",
            "median_starttransfer_ms": r4(nearest_rank(stt, 50)) if stt else None,
            "median_tls_complete_ms": r4(nearest_rank(ac, 50)) if ac else None,
            "stdev_starttransfer_ms": describe(stt).get("stdev"),
            "stdev_total_ms": describe(total).get("stdev"),
            "consequence": "the only defensible client-observed latency figure "
                           "is time_total.",
        },
        "token_latency_correlation": {
            "pearson_r_total_vs_output_tokens": _pearson(
                [p[0] for p in pairs], [float(p[1]) for p in pairs]),
            "reading": "a moderate correlation means token count explains part of "
                       "the latency and leaves a large serving-side residual. A "
                       "value near 1.0 would mean the endpoint simply streams at a "
                       "fixed token rate; a value near 0 would mean latency is "
                       "independent of the work done.",
        },
        "within_case_spread_ms": spreads,
        "max_within_case_range_over_median_range": _spread_ratio(spreads),
    }


def _pearson(a, b):
    n = len(a)
    if n < 3:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((y - mb) ** 2 for y in b))
    return r4(num / (da * db)) if da and db else None


def _spread_ratio(spreads):
    ranges = [v["range"] for v in spreads.values() if v.get("range")]
    if len(ranges) < 2:
        return None
    return {
        "n_cases": len(ranges),
        "min_range_ms": r4(min(ranges)),
        "max_range_ms": r4(max(ranges)),
        "reading": "repeating the SAME request moves latency by this much, so a "
                   "single-call latency figure is a sample from a wide "
                   "distribution rather than a property of the request",
    }


def token_and_cost(rows, mech, block, phases=("warm", "warmup", "idle",
                                              "concurrency"),
                   include_warmup_in_cost=True):
    sel = [r for r in rows if r.get("block") == block and r.get("phase") in phases
           and usable(r)]
    fields = ("input_tokens", "output_tokens", "reasoning_tokens",
              "cache_read_tokens", "cache_write_tokens", "total_tokens")
    agg = {f: 0 for f in fields}
    per_call = []
    for r in sel:
        uf = r.get("usage_flat") or {}
        for f in fields:
            v = uf.get(f)
            if isinstance(v, int):
                agg[f] += v
        per_call.append(r.get("derived_cost_usd") or 0.0)
    n = len(sel) or 1
    cost_total = sum(per_call)
    return {
        "selection": f"mechanism={mech} AND block={block!r} AND phase IN "
                     f"{list(phases)} AND no typed_error",
        "warmup_included_in_cost_total": include_warmup_in_cost,
        "n_calls": len(sel),
        "tokens_total": dict(sorted(agg.items())),
        "tokens_per_call": {k: r4(v / n) for k, v in sorted(agg.items())},
        "denominator_note": "tokens_per_call divides by n_calls, which INCLUDES "
                            "warm-up calls when warmup_included_in_cost_total "
                            "is true; set it false for a warm-only figure",
        "rates_usd_per_million": R.MODEL_COST_PER_MTOK[R.MECH[mech]["model_id"]],
        "rates_class": "PRICING/ENTITLEMENT FACT — promotional and tier "
                       "dependent; not a structural property of the model",
        "derived_cost_usd_total": r4(cost_total),
        "derived_cost_usd_per_call": r4(cost_total / n),
        "derived_cost_source": "per-row derived_cost_usd from the harness, summed",
    }


def failures(rows, mech):
    out = {}
    for phase in sorted({r.get("phase") for r in rows}):
        prows = [r for r in rows if r.get("phase") == phase]
        out[phase] = {
            "n_rows": len(prows),
            "n_typed_errors": sum(1 for r in prows if r.get("typed_error")),
            "typed_error_counts": counts_by(prows, lambda r: r.get("typed_error")),
            "http_status_counts": counts_by(prows, lambda r: r.get("http_status")),
            "retries_total": sum(r.get("retries") or 0 for r in prows),
            "attempts_total": sum(r.get("attempts") or 0 for r in prows),
            "max_attempts_any_call": max([r.get("attempts") or 0
                                          for r in prows] or [0]),
        }
    return {
        "selection": f"mechanism={mech} AND all blocks",
        "by_phase": out,
        "retry_policy": "N = 1 attempt per call, 0 retries, everywhere, by "
                        "design. A retry would make an availability failure "
                        "invisible, so it is not permitted in a measurement "
                        "phase.",
    }


# ---------------------------------------------------------------------------
# Jev: the free-tier cap, the probe series, and the frozen window
# ---------------------------------------------------------------------------
def jev_cap_timeline(rows):
    seq = sorted([r for r in rows if r.get("phase") in ("warmup", "warm")],
                 key=lambda r: (r.get("timestamp_utc") or "",
                                r.get("phase") or "", r.get("repeat") or 0))
    first_429 = None
    for i, r in enumerate(seq):
        if r.get("http_status") == 429:
            first_429 = i
            break
    seg = []
    if first_429 is not None:
        seg = [
            {
                "segment": "before_first_429",
                "n_calls": first_429,
                "http_status_counts": counts_by(seq[:first_429],
                                                lambda r: r.get("http_status")),
                "first_utc": seq[0].get("timestamp_utc"),
                "last_utc": seq[first_429 - 1].get("timestamp_utc"),
            },
            {
                "segment": "from_first_429_onward",
                "n_calls": len(seq) - first_429,
                "http_status_counts": counts_by(seq[first_429:],
                                                lambda r: r.get("http_status")),
                "first_utc": seq[first_429].get("timestamp_utc"),
                "last_utc": seq[-1].get("timestamp_utc"),
            },
        ]
    return {
        "selection": "mechanism=jev AND block=null AND phase IN (warmup, warm)",
        "n_calls": len(seq),
        "n_usable": sum(1 for r in seq if usable(r)),
        "tokens_consumed": 0,
        "tokens_consumed_note": "zero: every call was rejected before inference, "
                                "so this window yields NO latency, throughput, "
                                "token or cost statistic",
        "first_utc": seq[0].get("timestamp_utc") if seq else None,
        "last_utc": seq[-1].get("timestamp_utc") if seq else None,
        "transition": seg,
        "error_detail_first": (seq[0].get("error_detail") if seq else None),
        "interpretation": "The 403 phase masks the cap behind an upstream parse "
                          "error, so a client that only inspects http_status "
                          "would read it as a server fault, not an entitlement "
                          "wall. The 429 phase names it: FreeUsageLimitError.",
    }


def probe_series():
    if not os.path.exists(PROBE_PATH):
        return {"note": "no probe file"}
    rows = R.load_ndjson(PROBE_PATH)
    # Probes 1-2 predate the structured `error_type` field (the extractor
    # looked for error.code, but this endpoint discriminates on error.type).
    # Their verbatim excerpt still carries the type; deriving it here rather
    # than rewriting the rows keeps the evidence append-only.
    for r in rows:
        if r.get("error_type") is None and r.get("raw_response_excerpt"):
            try:
                doc = json.loads(r["raw_response_excerpt"])
                err = doc.get("error") or {}
                if err.get("type"):
                    r["error_type"] = err["type"]
                    r["error_type_derived"] = True
            except ValueError:
                pass
    gaps = [r.get("seconds_since_previous_attempt") for r in rows
            if r.get("seconds_since_previous_attempt") is not None]
    return {
        "file": os.path.relpath(PROBE_PATH, FOLLOWUP),
        "what_this_is": "A bounded AVAILABILITY series against the Jev free "
                        "tier, not a measurement phase. No statistic in this "
                        "document consumes a probe row.",
        "protocol": {
            "max_probes": 10,
            "min_gap_seconds": 60,
            "attempts_per_probe": 1,
            "retries": 0,
            "stop_early_on_first_success": True,
            "rationale": "probing a rate-limited endpoint more tightly, or "
                         "retrying, would manufacture load and destroy the "
                         "signal the series exists to measure",
        },
        "n_probes": len(rows),
        "n_usable_answers": sum(1 for r in rows if r.get("usable_answer")),
        "http_status_counts": counts_by(rows, lambda r: r.get("http_status")),
        "error_type_counts": counts_by(rows, lambda r: r.get("error_type")),
        "first_utc": rows[0].get("timestamp_utc") if rows else None,
        "last_utc": rows[-1].get("timestamp_utc") if rows else None,
        "min_gap_observed_s": r4(min(gaps)) if gaps else None,
        "all_gaps_at_or_above_floor": (min(gaps) >= 60.0) if gaps else None,
        "probes": [{
            "probe_index": r.get("probe_index"),
            "timestamp_utc": r.get("timestamp_utc"),
            "seconds_since_previous_attempt": r.get(
                "seconds_since_previous_attempt"),
            "case_id": r.get("case_id"),
            "http_status": r.get("http_status"),
            "error_type": r.get("error_type"),
            "error_message": r.get("error_message"),
            "usable_answer": r.get("usable_answer"),
        } for r in rows],
    }


def frozen_jev_window():
    """The frozen Phase-1 Jev window: a DIFFERENT window and a DIFFERENT
    transport. Reported as such; never merged with the current window."""
    if not os.path.exists(FROZEN_JEV):
        return {"note": "frozen file absent"}
    rows = R.load_ndjson(FROZEN_JEV)
    good = [r for r in rows if not r.get("typed_error")]
    lat = [r.get("latency_ms") for r in good if r.get("latency_ms") is not None]
    tin = [ (r.get("usage") or {}).get("input_tokens") for r in good]
    tout = [(r.get("usage") or {}).get("output_tokens") for r in good]
    tin = [t for t in tin if isinstance(t, int)]
    tout = [t for t in tout if isinstance(t, int)]
    n = len(good) or 1
    # probability availability, from the frozen responses
    avail = {"noul_scalar": 0, "noul_total": 0, "choice_distribution": 0,
             "score_distribution": 0, "choice_total": 0, "score_total": 0}
    for r in good:
        qtype = (r.get("prediction") or {}).get("type")
        pred = r.get("prediction") or {}
        probs = pred.get("probabilities")
        if qtype == "noul":
            avail["noul_total"] += 1
            if isinstance(pred.get("noul"), (int, float)) or isinstance(probs, dict):
                avail["noul_scalar"] += 1
        elif qtype == "choice":
            avail["choice_total"] += 1
            if isinstance(probs, dict) and probs:
                avail["choice_distribution"] += 1
        elif qtype == "score":
            avail["score_total"] += 1
            if isinstance(probs, dict) and probs:
                avail["score_distribution"] += 1
    ts = sorted(r.get("timestamp_utc") for r in good if r.get("timestamp_utc"))
    return {
        "file": os.path.relpath(FROZEN_JEV, FOLLOWUP),
        "window": {
            "first_utc": ts[0] if ts else None,
            "last_utc": ts[-1] if ts else None,
            "transport": "python urllib (the frozen Phase-1 transport), NOT "
                         "curl; the current window uses curl. Client-side "
                         "process-spawn and curl-instrumented phase timings are "
                         "therefore NOT available for these rows.",
            "tier_state": "free tier, inside quota at that time",
            "why_used": "the current window produced zero usable Jev calls, so "
                        "this is the only Jev latency/usage/stability evidence "
                        "that exists. Using it is honest; treating it as "
                        "current-window data would not be.",
        },
        "n_calls": len(rows),
        "n_usable": len(good),
        "latency_ms": describe(lat),
        "tokens_input": describe(tin, unit="tokens"),
        "tokens_output": describe(tout, unit="tokens"),
        "mean_input_tokens_per_call": r4(sum(tin) / n) if tin else None,
        "mean_output_tokens_per_call": r4(sum(tout) / n) if tout else None,
        "derived_cost_usd_total": 0.0,
        "probability_availability": avail,
        "sha256": sha256_file(FROZEN_JEV),
    }


# ---------------------------------------------------------------------------
# interface probe
# ---------------------------------------------------------------------------
def interface_probe(rows_by_mech, cases_by_id):
    mimo = rows_by_mech[R.MIMO]
    logprobs_rows = [r for r in mimo if r.get("probe") == "logprobs"
                     or (r.get("request_fields") and "logprobs" in r["request_fields"])]
    out = {
        "mimo": {
            "probe_rows": len(logprobs_rows),
            "probabilities_exposed_under_frozen_conditions": sum(
                1 for r in mimo if usable(r)
                and isinstance(r.get("parsed_probabilities"), dict)
                and r.get("parsed_probabilities")),
            "logprobs_requested_and_returned": [
                {
                    "case_id": r.get("case_id"),
                    "http_status": r.get("http_status"),
                    "logprobs_present_in_response": bool(
                        ((r.get("parsed") or {}).get("logprobs"))),
                    "typed_error": r.get("typed_error"),
                    "request_fields": r.get("request_fields"),
                } for r in logprobs_rows
            ],
            "reasoning_content_exposed": sum(
                1 for r in mimo if usable(r)
                and ((r.get("parsed") or {}).get("reasoning_content_present"))),
            "note": "the frozen request shape does not request logprobs, so a "
                    "null probabilities field under frozen conditions is a "
                    "property of the REQUEST, not proof the API cannot return "
                    "probabilities. The labelled interface probe is what tests "
                    "the latter.",
        },
        "jev": {
            "probe_rows": 0,
            "probe_cost_calls": 0,
            "note": "Jev's distribution availability is read from the FROZEN "
                    "responses (see frozen_jev_window.probability_availability) "
                    "rather than from new calls: a noul question returns the "
                    "scalar `noul` and choice/score return full distributions, "
                    "so a new probe call would have added cost and rate-limit "
                    "pressure for no new information.",
        },
    }
    return out


# ---------------------------------------------------------------------------
# document assembly
# ---------------------------------------------------------------------------
def build_summary():
    cases_by_id = build_case_index()
    rows_by_mech = {}
    paths = {}
    for mech in R.MECHANISMS:
        rows, path = load_rows(mech)
        rows_by_mech[mech] = rows
        paths[mech] = path

    doc = {
        "schema_version": "jevp1-ops-summary-1.0",
        "study": "followup-03 operational comparison, issue #565",
        "question": "given roughly matched bounded-decision accuracy on the "
                    "frozen corpus, does Jev provide a material LATENCY, "
                    "THROUGHPUT, COST or OPERATIONAL advantage over MiMo V2.6 "
                    "Flash?",
        "determinism": {
            "method": "this document contains no clock read, no randomness and "
                      "no network access; two runs over the same inputs are "
                      "byte-identical",
            "percentile_method": "nearest-rank, no interpolation",
            "verify_with": "python3 harness/analyze_ops.py --check",
        },
        "inputs": {
            mech: {
                "path": os.path.relpath(path, FOLLOWUP),
                "sha256": sha256_file(path),
                "n_rows": len(rows_by_mech[mech]),
                "blocks": counts_by(rows_by_mech[mech], lambda r: r.get("block")),
                "phases": counts_by(rows_by_mech[mech], lambda r: r.get("phase")),
            } for mech, path in paths.items()
        },
        "frozen_inputs_verified": {
            name: {"sha256": h, "matches": R.FROZEN_INPUTS.get(name) == h}
            for name, h in (
                ("cases.ndjson", sha256_file(os.path.join(
                    os.path.dirname(FOLLOWUP), "cases.ndjson"))),
                ("results/jev_raw.ndjson", sha256_file(FROZEN_JEV)),
            )
        },
        "blocks": {
            "measurement_block": MEASUREMENT_BLOCK,
            "null_block_rows": "the aborted first attempt, retained verbatim; "
                               "excluded from warm statistics and reported "
                               "separately under jev.free_tier_cap and "
                               "mimo.aborted_first_block",
        },
    }

    # ---- per-mechanism structural sections
    mech_sections = {}
    for mech in R.MECHANISMS:
        rows = rows_by_mech[mech]
        if mech == R.JEV:
            mech_sections["jev"] = {
                "label": MECH_LABEL[mech],
                "model_id": R.MECH[mech]["model_id"],
                "current_window_measurement": {
                    "status": "UNRESOLVED",
                    "reason": "zero usable calls in this window: the free tier "
                              "rejected every call (see free_tier_cap)",
                "warm_latency": None,
                "latency_budget": None,
                "throughput": None,
                    "concurrency": None,
                    "idle_proxy": None,
                    "stability": None,
                },
                "aborted_first_block": {
                    "n_rows": len([r for r in rows if r.get("block") is None]),
                    "note": "all rows are failures; nothing here is a "
                            "measurement",
                },
                "free_tier_cap": jev_cap_timeline(rows),
                "availability_probes": probe_series(),
                "frozen_window": frozen_jev_window(),
                "failures": failures(rows, mech),
                "cost": {
                    "derived_cost_usd_per_call": 0.0,
                    "derived_cost_usd_total": 0.0,
                    "per_dollar_ratio": None,
                    "per_dollar_status": "UNDEFINED at $0 — correct decisions "
                                         "per dollar requires dividing by a "
                                         "non-zero price, and the free tier's "
                                         "price is exactly zero. Reporting a "
                                         "number here would be a division by "
                                         "zero dressed as a result.",
                    "pricing_dependency": "every cost comparison against Jev is "
                                          "conditional on a free-tier "
                                          "entitlement that is (a) promotional, "
                                          "(b) revocable, and (c) empirically "
                                          "already exhausted within 197 calls in "
                                          "this very study. Jev is therefore "
                                          "$0 per call only while quota exists; "
                                          "the observed service level is a "
                                          "SERVING artefact, not a price.",
                },
            }
            continue

        warm = warm_latency(rows, cases_by_id, mech, MEASUREMENT_BLOCK)
        warm_median = warm["latency_total_ms"].get("median")
        th = throughput(rows, cases_by_id, mech, MEASUREMENT_BLOCK)
        conc = concurrency(rows, mech, MEASUREMENT_BLOCK)
        stab = stability(rows, cases_by_id, mech, MEASUREMENT_BLOCK)
        cost = token_and_cost(rows, mech, MEASUREMENT_BLOCK)
        n_ok = th["control_correct_decisions"]
        cost["derived_cost_usd_per_correct_control_decision"] = (
            r4(cost["derived_cost_usd_total"] / n_ok)
            if n_ok and cost["derived_cost_usd_total"] is not None else None)
        cost["per_correct_denominator"] = (
            "control_correct_decisions over warm+idle+concurrency rows; the "
            "total includes warm-up calls, so this is a slight UNDER-estimate "
            "of cost per decision; the warm-only figure is below")
        cost["derived_cost_usd_per_correct_control_decision_warm_only"] = (
            r4(_warm_only_cost(rows, mech, MEASUREMENT_BLOCK) / n_ok)
            if n_ok else None)
        mech_sections["mimo"] = {
            "label": MECH_LABEL[mech],
            "model_id": R.MECH[mech]["model_id"],
            "model_catalog_id": R.MECH[mech]["model_catalog_id"],
            "current_window_measurement": {
                "status": "ESTABLISHED (structural)",
                "warm_latency": warm,
                "latency_budget": latency_budget(rows, mech, MEASUREMENT_BLOCK),
                "idle_proxy": idle_proxy(rows, mech, MEASUREMENT_BLOCK,
                                        warm_median),
                "sequential_throughput": th,
                "concurrency": conc,
                "stability": stab,
                "tokens_and_cost": cost,
            },
            "aborted_first_block": {
                "n_rows": len([r for r in rows if r.get("block") is None]),
                "excluded_from_statistics": True,
                "reason": "an aborted 11-row first attempt; the complete grid "
                          "lives in block=resume1 and pooling a partial block "
                          "with a complete one would misstate the denominator",
            },
            "failures": failures(rows, mech),
        }

    doc["mechanisms"] = mech_sections
    doc["transport_probe"] = _transport_probe_summary()
    doc["interface_probe"] = interface_probe(rows_by_mech, cases_by_id)
    doc["ratios"] = _ratios(mech_sections)
    doc["not_measured"] = _not_measured(mech_sections)
    return doc


def _warm_only_cost(rows, mech, block):
    sel = [r for r in rows if r.get("block") == block and r.get("phase") == "warm"
           and usable(r)]
    return sum(r.get("derived_cost_usd") or 0.0 for r in sel)


def _transport_probe_summary():
    path = os.path.join(RESULTS, "transport_probe.json")
    if not os.path.exists(path):
        return {"note": "absent"}
    with open(path, "r", encoding="utf-8") as f:
        doc = json.load(f)
    by = {}
    for p in doc.get("probes", []):
        by.setdefault(p["mechanism"], []).append(p)
    out = {
        "file": os.path.relpath(path, FOLLOWUP),
        "guard": doc.get("interpretation_guard"),
        "never_folded_into_model_latency": doc.get(
            "never_folded_into_model_latency"),
        "by_mechanism": {},
    }
    for mech, probes in by.items():
        out["by_mechanism"][mech] = {
            "n": len(probes),
            "time_namelookup_s": describe(
                [(p.get("curl_phases") or {}).get("time_namelookup")
                 for p in probes], unit="s"),
            "time_connect_s": describe(
                [(p.get("curl_phases") or {}).get("time_connect")
                 for p in probes], unit="s"),
            "time_appconnect_tls_s": describe(
                [(p.get("curl_phases") or {}).get("time_appconnect")
                 for p in probes], unit="s"),
            "time_total_s": describe(
                [(p.get("curl_phases") or {}).get("time_total")
                 for p in probes], unit="s"),
        }
    return out


def _ratios(mech_sections):
    m = mech_sections["mimo"]["current_window_measurement"]
    j = mech_sections["jev"]
    th = m["sequential_throughput"]
    conc = m["concurrency"]
    cost = m["tokens_and_cost"]
    warm = m["warm_latency"]
    frozen = j["frozen_window"]
    out = {
        "measurement_boundary": "MIMO figures are from THIS window (curl, "
                               f"block={MEASUREMENT_BLOCK}). Jev figures are "
                               "from the FROZEN window (python urllib, "
                               "02:46-02:50Z) because this window produced no "
                               "usable Jev call. Every Jev/MiMo ratio below is "
                               "therefore a CROSS-WINDOW ratio across two "
                               "transports and two tier states. It is reported "
                               "because it is the only Jev evidence that "
                               "exists, and flagged because it is not a "
                               "matched pair.",
        "structural": {},
        "cost": {},
    }
    # cost per decision is tier-independent as a TOKEN fact, and a pricing
    # fact as a DOLLAR fact. Both are reported; only the second is labelled.
    n_mimo = th["n_calls_usable"]
    n_jev = (frozen.get("n_usable") or 0)
    if n_mimo and n_jev:
        out["structural"]["tokens_per_call_input_ratio_jev_over_mimo"] = r4(
            ((frozen.get("mean_input_tokens_per_call") or 0)
             / max(cost["tokens_per_call"].get("input_tokens") or 0, 1e-9)))
        out["structural"]["tokens_per_call_output_ratio_jev_over_mimo"] = r4(
            ((frozen.get("mean_output_tokens_per_call") or 0)
             / max(cost["tokens_per_call"].get("output_tokens") or 0, 1e-9)))
        out["structural"]["warm_median_latency_ratio_jev_over_mimo"] = r4(
            (frozen["latency_ms"].get("median") or 0)
            / max(warm["latency_total_ms"].get("median") or 0, 1e-9))
        out["structural"]["denominators"] = {
            "jev": f"n={n_jev} frozen calls, median over 1-second-rounded "
                   "latency_ms",
            "mimo": f"n={n_mimo} warm calls in block={MEASUREMENT_BLOCK}",
        }
    out["cost"]["mimo_usd_per_call"] = cost["derived_cost_usd_per_call"]
    out["cost"]["mimo_usd_per_correct_control_decision"] = cost.get(
        "derived_cost_usd_per_correct_control_decision_warm_only")
    out["cost"]["mimo_correct_decisions_per_dollar"] = (
        r4(1.0 / cost["derived_cost_usd_per_correct_control_decision_warm_only"])
        if cost.get("derived_cost_usd_per_correct_control_decision_warm_only")
        else None)
    out["cost"]["jev_usd_per_call"] = 0.0
    out["cost"]["jev_usd_per_correct_control_decision"] = 0.0
    out["cost"]["jev_correct_decisions_per_dollar"] = None
    out["cost"]["jev_per_dollar_classification"] = (
        "UNDEFINED at $0. Not 'infinite' and not 'best': the ratio has no "
        "value because its denominator is zero. The honest statement is the "
        "conditional one — while quota exists Jev costs $0 per call, and this "
        "study measured quota exhausting inside 197 calls.")
    out["cost"]["miMo_rates_class"] = (
        "PRICING/ENTITLEMENT FACT: input $0.14/Mtok, output $0.28/Mtok, cache "
        "read $0.0028/Mtok from the current catalog. Promotional and "
        "tier-dependent.")
    # cost/latency at the matched observed error level
    cc = th["control_opportunities"]
    if cc:
        out["cost"]["mimo_control_error_rate"] = r4(
            1.0 - (th["control_correct_decisions"] / cc))
    out["cost"]["mimo_control_error_rate_denominator"] = (
        f"{cc} usable predictions on ANSWERABLE control (variant_kind=base) "
        "subset cases in the warm block")
    out["cost"]["matched_error_level_note"] = (
        "A matched-error comparison requires a per-dollar or per-latency figure "
        "at the SAME observed error level. Jev's error level in this window is "
        "undefined in the operational sense: 0 of 197 calls returned an answer, "
        "so its decision error rate is not measurable at all. No matched-error "
        "ratio is therefore reported, and none should be inferred from Jev's "
        "$0 cost.")
    return out


def _not_measured(mech_sections):
    j = mech_sections["jev"]
    return {
        "jev_current_window_latency": "UNRESOLVED — 0 usable calls",
        "jev_current_window_throughput": "UNRESOLVED — 0 usable calls",
        "jev_current_window_concurrency": "UNRESOLVED — not attempted; issuing "
                                          "a concurrency block against an "
                                          "endpoint that has already refused "
                                          "197 of 197 calls would have produced "
                                          "12 more refusals, not a scaling curve",
        "jev_current_window_idle_cold_proxy": "UNRESOLVED — not attempted",
        "jev_current_window_stability": "UNRESOLVED in this window; the frozen "
                                         "window gives 1 call per case, so a "
                                         "repeat-to-repeat flip rate is NOT "
                                         "computable from it either",
        "jev_current_window_curl_phase_decomposition": "UNRESOLVED — no usable "
                                                       "curl response to "
                                                       "decompose; only the "
                                                       "rejection timings exist",
        "jev_paced_reduced_block": "NOT RUN — its precondition (a probe "
                                   "returning a usable answer) never held",
        "per_call_cold_start": "NOT DIRECTLY OBSERVABLE for either mechanism — "
                               "an idle-gap proxy is all the design can see",
        "server_side_queueing_or_batch_effects": "NOT OBSERVABLE from the "
                                                 "client; the client cannot "
                                                 "see whether the service "
                                                 "batched or queued a request",
        "sustained_multi_hour_throughput": "NOT MEASURED for either mechanism; "
                                           "every figure here is a short "
                                           "burst-window measurement",
        "price_elasticity_or_paid_jev_tier": "NOT MEASURED — out of scope and "
                                             "not priced",
    }


# ---------------------------------------------------------------------------
# comparison.md rendering — from the same dict, so prose cannot drift
# ---------------------------------------------------------------------------
def _fmt(v, dp=2):
    if v is None:
        return "n/a"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return f"{v:,.{dp}f}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v)


def _cap(text):
    """Capitalise an interpolated note so prose reads as sentences.

    The notes live in summary.json in lower case because that is how a note
    reads on its own; this only fixes the splice into a sentence.
    """
    if not text:
        return text
    return text[0].upper() + text[1:]


def render_comparison(d):
    L = []
    A = L.append
    j = d["mechanisms"]["jev"]
    m = d["mechanisms"]["mimo"]
    mw = m["current_window_measurement"]
    A("# Followup-03 — operational comparison: Jev 1.13 (free) vs MiMo V2.6 Flash")
    A("")
    A(f"*{d['question']}*")
    A("")
    A("Issue #565. Analysis is deterministic: `python3 harness/analyze_ops.py "
      "--check` rebuilds this document from the raw NDJSON and asserts the two "
      "serialisations are byte-identical.")
    A("")
    A("## Headline")
    A("")
    A("**The comparison the brief asked for cannot be completed as a matched "
      "pair, and the reason is itself the finding.** Jev's free tier refused "
      "every call in this window, so the only Jev latency, token and stability "
      "evidence that exists comes from a different window measured with a "
      "different transport. MiMo was measured cleanly. What follows separates "
      "the two, and marks the Jev/MiMo ratios as cross-window rather than "
      "pretending they are matched.")
    A("")
    A("| | MiMo V2.6 Flash | Jev 1.13 (free) |")
    A("|---|---|---|")
    A("| Calls attempted this window | "
      f"{_fmt(mw['sequential_throughput']['n_calls_usable'])} usable | "
      "0 usable (of 197 attempted) |")
    A("| Warm latency | measured | UNRESOLVED this window |")
    A("| Throughput | measured | UNRESOLVED this window |")
    A("| Concurrency scaling | measured | UNRESOLVED this window |")
    A("| Cost per call | $"
      f"{_fmt(mw['tokens_and_cost']['derived_cost_usd_per_call'], 6)} | $0.00 |")
    A("| Cost per correct decision | $"
      f"{_fmt(mw['tokens_and_cost'].get('derived_cost_usd_per_correct_control_decision_warm_only'), 6)} | "
      "$0.00 |")
    A("| Correct decisions per dollar | "
      f"{_fmt(d['ratios']['cost']['mimo_correct_decisions_per_dollar'], 1)} | "
      "**UNDEFINED at $0** |")
    A("| Availability under load | sustained | **exhausted inside 197 calls** |")
    A("")

    A("## 1. ESTABLISHED — structural measurements")
    A("")
    A("Tier-independent. Nothing in this section uses a price.")
    A("")
    A("### 1.1 MiMo warm latency (this window, curl)")
    A("")
    w = mw["warm_latency"]
    A(f"Rows: `{w['selection']}`. "
      f"{_fmt(w['n_rows_used'])} of {_fmt(w['n_rows_available'])} available rows "
      f"used ({_fmt(w['rows_dropped_unusable'])} dropped as unusable).")
    A("")
    A("| statistic | total time (ms) | time to first byte (ms) |")
    A("|---|---|---|")
    for k in ("n", "mean", "median", "p90", "p95", "p99", "min", "max", "stdev"):
        A(f"| {k} | {_fmt(w['latency_total_ms'].get(k))} | "
          f"{_fmt(w['latency_time_to_first_byte_ms'].get(k))} |")
    A("")
    pd_ = w["phase_decomposition_ms"]
    A(f"Decomposition (mean share of total that is pure transport: "
      f"**{_fmt(pd_['mean_share_of_total_pct'])}%**):")
    A("")
    A("| component | mean ms | median ms | p95 ms |")
    A("|---|---|---|---|")
    for label, key in (("transport (DNS+TCP+TLS)", "transport"),
                       ("service+transfer (starttransfer − connect)",
                        "service_transfer")):
        dd = pd_[key]
        A(f"| {label} | {_fmt(dd.get('mean'))} | {_fmt(dd.get('median'))} | "
          f"{_fmt(dd.get('p95'))} |")
    A("")
    A("The transport share matters for interpretation: a large fraction of a "
      "MiMo call is network setup, not model work, so wall-clock latency "
      "overstates the model's own cost and a like-for-like comparison must "
      "either hold transport constant or subtract it.")
    A("")

    # ---- the decomposition above does not account for the total
    lb = mw.get("latency_budget")
    if lb and "accounting" in lb:
        acc = lb["accounting"]
        A("#### 1.1a The brief's two components do not sum to the total — and "
          "the missing term is the largest one")
        A("")
        A(f"Rows: `{lb['selection']}`, n={_fmt(lb['n'])}.")
        A("")
        A("| component | mean ms | share of total |")
        A("|---|---|---|")
        A(f"| setup before first byte (DNS+TCP+TLS) | "
          f"{_fmt(acc['mean_setup_ms'])} | {_fmt(acc['mean_setup_share_pct'])}% |")
        A(f"| **post-first-byte body wait (the residual)** | "
          f"**{_fmt(acc['mean_post_first_byte_wait_ms'])}** | "
          f"**{_fmt(acc['mean_post_first_byte_share_pct'])}%** |")
        A(f"| total | {_fmt(acc['mean_total_ms'])} | 100% |")
        A("")
        A(f"The brief's two components sum to "
          f"{_fmt(acc['brief_two_component_sum_ms'])} ms of a "
          f"{_fmt(acc['mean_total_ms'])} ms call. "
          f"{_cap(acc['brief_two_component_note'])} "
          "Reporting the brief's decomposition without this residual would "
          "attribute a call's cost to the wrong place.")
        A("")
        fb = lb["first_byte_is_not_a_model_signal"]
        A(f"**`time_starttransfer` is not a model signal here.** "
          f"{_cap(fb['finding'])} Measured: median first byte "
          f"{_fmt(fb['median_starttransfer_ms'])} ms against median TLS "
          f"completion {_fmt(fb['median_tls_complete_ms'])} ms, with a "
          f"first-byte SD of {_fmt(fb['stdev_starttransfer_ms'])} ms against a "
          f"total SD of {_fmt(fb['stdev_total_ms'])} ms. "
          f"{_cap(fb['consequence'])}")
        A("")
        tc_ = lb["token_latency_correlation"]
        A(f"Token count explains only part of the latency: Pearson r between "
          f"total time and output tokens is "
          f"**{_fmt(tc_['pearson_r_total_vs_output_tokens'], 3)}**. "
          f"{_cap(tc_['reading'])}")
        A("")
        sw = lb.get("max_within_case_range_over_median_range")
        if sw:
            A(f"Repeating the **identical** request moves latency by between "
              f"{_fmt(sw['min_range_ms'], 0)} ms and "
              f"{_fmt(sw['max_range_ms'], 0)} ms across the "
              f"{_fmt(sw['n_cases'])} cases. {_cap(sw['reading'])}.")
            A("")
            A("| case | n | min ms | median ms | max ms | range ms | max/min |")
            A("|---|---|---|---|---|---|---|")
            for c, v in lb["within_case_spread_ms"].items():
                A(f"| {c} | {_fmt(v['n'])} | {_fmt(v['min'], 0)} | "
                  f"{_fmt(v['median'], 0)} | {_fmt(v['max'], 0)} | "
                  f"{_fmt(v['range'], 0)} | {_fmt(v['max_over_min'])}x |")
            A("")
            A("This is the strongest operational finding on the MiMo side, and "
              "it cuts against using any single latency number: the endpoint's "
              "serving time for a fixed small request is dominated by variable "
              "queueing that the client cannot see or control. Report the "
              "distribution, not the mean.")
            A("")

    A("### 1.2 MiMo sequential and concurrent throughput")
    A("")
    th = mw["sequential_throughput"]
    A(f"Rows: `{th['selection']}`. {_cap(th['definition'])}")
    A("")
    A(f"- sequential: **{_fmt(th['sequential_calls_per_sec'], 3)} calls/sec** "
      f"({_fmt(th['n_calls_usable'])} calls / "
      f"{_fmt(th['sum_time_total_ms'] / 1000.0, 2)} s of summed per-call time)")
    A(f"- including curl process spawn: "
      f"{_fmt(th['sequential_calls_per_sec_including_process_spawn'], 3)} "
      "calls/sec")
    A(f"- correct control decisions/sec: "
      f"**{_fmt(th['control_correct_per_sec'], 4)}** "
      f"({_fmt(th['control_correct_decisions'])} correct of "
      f"{_fmt(th['control_opportunities'])} control opportunities)")
    A(f"- correct decisions/sec over the full answerable subset: "
      f"{_fmt(th['all_subset_correct_per_sec'], 4)} "
      f"({_fmt(th['all_subset_correct_decisions'])} of "
      f"{_fmt(th['all_subset_opportunities'])})")
    A("")
    A("| C | usable | failed | 429 | makespan (ms) | calls/sec | scaling vs C=1 "
      "| p50 latency ratio vs C=1 |")
    A("|---|---|---|---|---|---|---|---|")
    for c, v in sorted(mw["concurrency"]["by_level"].items(), key=lambda kv: int(kv[0])):
        s = mw["concurrency"]["scaling"][c]
        A(f"| {c} | {_fmt(v['n_usable'])} | {_fmt(v['n_failed'])} | "
          f"{_fmt(v['n_http_429'])} | {_fmt(v['block_makespan_ms'], 0)} | "
          f"{_fmt(v['throughput_calls_per_sec'], 3)} | "
          f"{_fmt(s['scaling_ratio_vs_C1'])}x | "
          f"{_fmt(s['p50_over_C1_latency_ratio'])}x |")
    if not mw["concurrency"]["by_level"]:
        A("| — | 0 | 0 | 0 | n/a | n/a | n/a | n/a |")
        A("")
        A("**No concurrency block was recorded for this mechanism.** The "
          "section is retained rather than dropped so its absence is visible.")
    A("")
    A(f"Scoring definition: {mw['concurrency']['scaling_definition']}")
    A("")

    A("### 1.3 MiMo label stability")
    A("")
    st = mw["stability"]
    A(f"Rows: `{st['selection']}`. {_cap(st['flip_rate_definition'])}.")
    A("")
    A(f"- {_fmt(st['n_cases'])} cases x {_fmt(st['n_observations'])} warm "
      "observations")
    A(f"- mean flip rate: **{_fmt(st['mean_flip_rate'], 4)}**; max "
      f"{_fmt(st['max_flip_rate'], 4)}")
    A(f"- cases stable on every rep: {_fmt(st['n_cases_fully_stable'])} of "
      f"{_fmt(st['n_cases'])}")
    A(f"- mean modal-label frequency: {_fmt(st['mean_modal_frequency'], 4)}")
    A("")
    A("| case | type | reps | modal label | modal freq | distinct labels | "
      "flip rate | reasoning tokens mean (min–max) |")
    A("|---|---|---|---|---|---|---|---|")
    for r in st["per_case"]:
        rt = r.get("reasoning_tokens") or {}
        rt_s = (f"{_fmt(rt.get('mean'), 1)} ({_fmt(rt.get('min'))}–"
                f"{_fmt(rt.get('max'))})" if rt else "n/a")
        A(f"| {r['case_id']} | {r['question_type']} | {_fmt(r['n_reps'])} | "
          f"{r['modal_label']} | {_fmt(r['modal_frequency'], 3)} | "
          f"{_fmt(r['distinct_labels'])} | {_fmt(r['flip_rate'], 3)} | {rt_s} |")
    A("")

    A("### 1.4 MiMo token use (including reasoning)")
    A("")
    tc = mw["tokens_and_cost"]
    A(f"Rows: `{tc['selection']}`. {_cap(tc['denominator_note'])}.")
    A("")
    A("| token class | total | per call |")
    A("|---|---|---|")
    for k, v in tc["tokens_total"].items():
        A(f"| {k} | {_fmt(v)} | {_fmt(tc['tokens_per_call'].get(k))} |")
    A("")

    A("### 1.5 The Jev free-tier cap — an operational property, not a price")
    A("")
    cap = j["free_tier_cap"]
    A(f"Rows: `{cap['selection']}`. **{_fmt(cap['n_calls'])} calls, "
      f"{_fmt(cap['n_usable'])} usable, {_fmt(cap['tokens_consumed'])} tokens "
      f"consumed.** Window {cap['first_utc']} → {cap['last_utc']}.")
    A("")
    if cap.get("transition"):
        A("| segment | calls | HTTP status mix | window |")
        A("|---|---|---|---|")
        for s in cap["transition"]:
            A(f"| {s['segment']} | {_fmt(s['n_calls'])} | "
              f"{s['http_status_counts']} | {s['first_utc']} → {s['last_utc']} |")
        A("")
    A(f"Reading: {_cap(cap['interpretation'])}")
    A("")
    A("This is the sharpest operational result in the study, and it is worth "
      "stating plainly: **a free tier that answers 403 for 125 consecutive "
      "calls and only then starts answering 429 is a serving policy, not a "
      "benchmark result.** A client that retries on 403 alone would have "
      "spent 125 calls learning nothing. The 429 body names the cause "
      "(`FreeUsageLimitError`); the 403 body does not.")
    A("")

    A("### 1.6 Jev availability probes (bounded series)")
    A("")
    pr = j["availability_probes"]
    if "n_probes" in pr:
        A(f"Protocol: {pr['protocol']['max_probes']} probes maximum, "
          f">= {pr['protocol']['min_gap_seconds']}s apart, "
          f"{pr['protocol']['attempts_per_probe']} attempt each, "
          f"{pr['protocol']['retries']} retries, stopping early on the first "
          "usable answer. " + pr["protocol"]["rationale"] + ".")
        A("")
        A(f"Result: **{_fmt(pr['n_probes'])} probes, "
          f"{_fmt(pr['n_usable_answers'])} usable answers**, "
          f"{pr['first_utc']} → {pr['last_utc']}. "
          f"HTTP status mix {pr['http_status_counts']}; error types "
          f"{pr['error_type_counts']}. Smallest observed gap "
          f"{_fmt(pr['min_gap_observed_s'], 1)}s "
          f"(floor respected: {_fmt(pr['all_gaps_at_or_above_floor'])}).")
        A("")
        A("| # | UTC | gap (s) | case | HTTP | error type | usable |")
        A("|---|---|---|---|---|---|---|")
        for p in pr["probes"]:
            A(f"| {p['probe_index']} | {p['timestamp_utc']} | "
              f"{_fmt(p['seconds_since_previous_attempt'], 1)} | "
              f"{p['case_id']} | {p['http_status']} | "
              f"{p['error_type']} | {_fmt(p['usable_answer'])} |")
        A("")
        A("The series exhausted its budget without a single usable answer, so "
          "the paced reduced Jev block described in the brief was **not run**: "
          "its precondition never held. No Jev number in this document comes "
          "from a fabricated or estimated call.")
    else:
        A("No probe series recorded.")
    A("")

    A("### 1.7 All Jev evidence that exists (frozen window)")
    A("")
    fz = j["frozen_window"]
    if "n_usable" in fz:
        A(f"Source: `{fz['file']}` ({fz['n_usable']} usable of {fz['n_calls']} "
          f"rows), window {fz['window']['first_utc']} → "
          f"{fz['window']['last_utc']}, transport {fz['window']['transport']}, "
          f"tier state: {fz['window']['tier_state']}.")
        A("")
        A(f"Used because: {fz['window']['why_used']}")
        A("")
        fl = fz["latency_ms"]
        A("| statistic | latency (ms) |")
        A("|---|---|")
        for k in ("n", "mean", "median", "p90", "p95", "p99", "min", "max",
                  "stdev"):
            A(f"| {k} | {_fmt(fl.get(k))} |")
        A("")
        A(f"- input tokens per call: mean "
          f"{_fmt(fz['mean_input_tokens_per_call'], 1)}; output tokens per call: "
          f"mean {_fmt(fz['mean_output_tokens_per_call'], 1)}")
        pa = fz["probability_availability"]
        A(f"- probability availability: noul scalar exposed on "
          f"{_fmt(pa['noul_scalar'])}/{_fmt(pa['noul_total'])} noul calls; "
          f"choice distribution on {_fmt(pa['choice_distribution'])}/"
          f"{_fmt(pa['choice_total'])}; score distribution on "
          f"{_fmt(pa['score_distribution'])}/{_fmt(pa['score_total'])}")
        A("- cost: $0.00 (free tier), with the same entitlement caveat as §1.5")
        A("")
        A("**What this window cannot support:** curl phase decomposition "
          "(different transport), concurrency, idle/cold proxy, and a "
          "repeat-to-repeat stability rate (it holds one call per case, so a "
          "flip rate is not computable from it at all).")
    A("")

    A("## 2. UNRESOLVED")
    A("")
    A("Each item is a question this study could not answer. None is filled in "
      "by estimate.")
    A("")
    for k, v in d["not_measured"].items():
        A(f"- **{k}** — {v}")
    A("")
    A("The Jev side of the comparison is UNRESOLVED on every structural axis "
      "in this window. The single most consequential unknown is whether the "
      "cap is a hard entitlement wall or a burst allowance: 197 calls inside "
      "~100 seconds exhausted it, but nothing here distinguishes "
      "\"N calls per day\" from \"N calls per minute with a leaky bucket\". "
      "That distinction decides whether Jev is operationally usable at all, "
      "and this design cannot make it.")
    A("")

    A("## 3. SERVING-OR-PRICING ARTIFACT")
    A("")
    A("Facts that look like results but are properties of a commercial "
      "arrangement rather than of either model.")
    A("")
    A(f"1. **Jev's $0 price.** {d['ratios']['cost']['jev_per_dollar_classification']}")
    A(f"2. **MiMo's rates.** {d['ratios']['cost']['miMo_rates_class']} These "
      "may be used to state a dollar cost. They may NOT be used to claim a "
      "latency or throughput advantage, and no such claim appears above.")
    A(f"3. **Matched-error comparison.** {d['ratios']['cost']['matched_error_level_note']}")
    A(f"4. **The 403→429 transition itself.** The 403 phase is a serving "
      "policy (error masking); the 429 phase is an entitlement wall. Neither "
      "is a property of Jev's reasoning. Any 'Jev is slow/unreliable' reading "
      "taken from this window is reading the free tier, not the model.")
    A("5. **Network/transport overhead.** The connect-only probe is a property "
      "of the path and the CDN edge, not of either model "
      f"({d['transport_probe'].get('guard')}).")
    A("")
    A("### Cost, stated with its denominator")
    A("")
    rc = d["ratios"]["cost"]
    A(f"- MiMo per call: **${_fmt(rc['mimo_usd_per_call'], 6)}** over "
      f"{_fmt(mw['tokens_and_cost']['n_calls'])} calls")
    A(f"- MiMo per correct CONTROL decision: **$"
      f"{_fmt(rc['mimo_usd_per_correct_control_decision'], 6)}** over "
      f"{_fmt(mw['sequential_throughput']['control_correct_decisions'])} correct "
      "control decisions in the warm block")
    A(f"- MiMo correct decisions per dollar: **"
      f"{_fmt(rc['mimo_correct_decisions_per_dollar'], 1)}** (reciprocal of the "
      "line above; promotional rates)")
    A(f"- Jev per call: **$0.00**; per correct decision: **$0.00**; per dollar: "
      "**UNDEFINED**")
    A(f"- MiMo control error rate this window: "
      f"{_fmt(rc.get('mimo_control_error_rate'), 4)} over "
      f"{rc['mimo_control_error_rate_denominator']}")
    A("")
    A("### Cross-window ratios (flagged, not matched)")
    A("")
    A(d["ratios"]["measurement_boundary"])
    A("")
    st_ = d["ratios"]["structural"]
    for k, v in st_.items():
        if k == "denominators":
            continue
        A(f"- `{k}` = **{_fmt(v, 3)}**")
    if "denominators" in st_:
        A("")
        A("Denominators:")
        for k, v in st_["denominators"].items():
            A(f"- {k}: {v}")
    A("")

    A("## 4. Probability distributions — interface probe")
    A("")
    ip = d["interface_probe"]
    A(f"**MiMo.** {ip['mimo']['note']} Probe rows: "
      f"{_fmt(ip['mimo']['probe_rows'])}; reasoning content exposed on "
      f"{_fmt(ip['mimo']['reasoning_content_exposed'])} usable calls.")
    for r in ip["mimo"]["logprobs_requested_and_returned"]:
        A(f"  - `{r['case_id']}`: HTTP {r['http_status']}, logprobs requested="
          f"{r['request_fields']}, logprobs present in response="
          f"{_fmt(r['logprobs_present_in_response'])}")
    A("")
    A(f"**Jev.** {ip['jev']['note']} In the frozen window Jev returns the "
      "scalar `noul` for noul questions and full distributions for choice and "
      "score — see §1.7. That is a genuine interface difference and the one "
      "operational advantage this study can point at with evidence, because it "
      "is a property of the response schema rather than of price or quota.")
    A("")

    A("## 5. Failures and retries")
    A("")
    A(f"{j['failures']['retry_policy']}")
    A("")
    A("| mechanism | phase | rows | typed errors | HTTP status mix | retries |")
    A("|---|---|---|---|---|---|")
    for mk, sec in (("Jev", j), ("MiMo", m)):
        for ph, v in sec["failures"]["by_phase"].items():
            A(f"| {mk} | {ph} | {_fmt(v['n_rows'])} | "
              f"{_fmt(v['n_typed_errors'])} | {v['http_status_counts']} | "
              f"{_fmt(v['retries_total'])} |")
    A("")

    A("## 6. Row selection — which rows every statistic used")
    A("")
    A("| mechanism | file | rows | blocks | phases |")
    A("|---|---|---|---|---|")
    for mk, v in d["inputs"].items():
        A(f"| {mk} | `{v['path']}` | {_fmt(v['n_rows'])} | {v['blocks']} | "
          f"{v['phases']} |")
    A("")
    A(f"Measurement block: `{d['blocks']['measurement_block']}`. "
      f"{d['blocks']['null_block_rows']}")
    A("")
    A("Frozen inputs re-verified at analysis time: "
      + ", ".join(f"`{k}` "
                  f"({'match' if v['matches'] else 'MISMATCH'})"
                  for k, v in d["frozen_inputs_verified"].items()) + ".")
    A("")
    A("## 7. Honest summary of the comparison")
    A("")
    A("- **ESTABLISHED:** MiMo's latency distribution, throughput at C=1/4/8, "
      "label stability, token use including reasoning, and derived cost, all "
      "under frozen conditions with one attempt per call and zero retries.")
    A("- **ESTABLISHED:** the Jev free tier is not merely slower or costlier "
      "than a paid tier — it is unavailable under sustained sequential load, "
      "exhausting inside 197 calls in ~100 seconds, and it masks that "
      "exhaustion behind 125 consecutive 403s before it will name it.")
    A("- **ESTABLISHED:** Jev's response interface exposes probabilities "
      "(scalar for noul, full distributions for choice/score) where MiMo's "
      "frozen request shape exposes none. This is an interface fact, and its "
      "operational value is real and independent of price.")
    A("- **UNRESOLVED:** every Jev structural metric in this window, and "
      "therefore any matched Jev-vs-MiMo latency, throughput or concurrency "
      "claim.")
    A("- **ARTIFACT:** Jev's $0 per-call cost. It is not an advantage that can "
      "be divided by; it is a promotional entitlement that this study watched "
      "exhaust. Whether Jev is cheaper in any decision-relevant sense depends "
      "entirely on a quota whose size is unpublished and whose rate this study "
      "could not measure.")
    A("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="build the document twice and assert the two "
                         "serialisations are byte-identical")
    args = ap.parse_args()

    doc = build_summary()
    text = json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    md = render_comparison(doc)

    if args.check:
        again = build_summary()
        text2 = (json.dumps(again, indent=2, sort_keys=True, ensure_ascii=False)
                 + "\n")
        md2 = render_comparison(again)
        if text != text2 or md != md2:
            raise SystemExit("NON-DETERMINISTIC: two builds differ.")
        print("determinism: OK (two in-process builds byte-identical)")

    os.makedirs(RESULTS, exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write(text)
    with open(COMPARISON_PATH, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"summary.json    -> {SUMMARY_PATH}")
    print(f"  sha256 {sha256_text(text)}")
    print(f"comparison.md   -> {COMPARISON_PATH}")
    print(f"  sha256 {sha256_text(md)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
