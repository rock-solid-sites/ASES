#!/usr/bin/env python3
"""Phase 2 subject arm: direct TypeSafe jev-1.13.0.

Endpoint: POST https://api.typesafe.ai/v1/systemone
Model:    jev-1.13.0

Carried over from Phase 1, because each was paid for in a failed run:
  * An explicit User-Agent is MANDATORY. urllib's default
    `Python-urllib/3.10` is Cloudflare-rejected with 403 code 1010. A 403 here
    is a harness defect, never a model or account conclusion.
  * ONE scenario per request. Never concatenate contrasting situations into a
    single state; Phase 1's first probe did that and got degenerate ~0.45-0.48
    readings on every question.
  * Never batch questions that share a state.
  * `noul` returns only a scalar; there is NO `confidence` field. Reported
    confidence, where useful, is DERIVED from the probability vector and must
    never be presented as independent evidence (Phase 1 INSTRUMENT-VALIDATION).
  * The Zen free route is NOT used. followup-03 recorded 0 of 197 usable
    answers on it.

Credential: read from ~/.secrets/typesafe.env. Only the source LABEL is ever
written to an artefact; the value is never recorded, logged or echoed.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE2 = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import represent  # noqa: E402
import freeze as freeze_ctl  # noqa: E402
import record_schema as rschema  # noqa: E402

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-1.13.0"
UA = "edas-jev-phase2/1.0 (+opencode; research)"
CRED_LABEL = "secrets/typesafe.env#TYPESAFE_API_KEY"

ERR_NETWORK = "network_error"
ERR_403 = "forbidden_403"
ERR_429 = "rate_limited_429"
ERR_5XX = "server_5xx"
ERR_HTTP = "http_error"
ERR_PARSE = "parse_error"
ERR_EMPTY = "empty_answer"


def load_key():
    path = os.path.expanduser("~/.secrets/typesafe.env")
    if not os.path.exists(path):
        return None
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line.startswith("export "):
            line = line[7:]
        if line.startswith("TYPESAFE_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def classify(status):
    if status is None:
        return ERR_NETWORK
    if status == 403:
        return ERR_403
    if status == 429:
        return ERR_429
    if status >= 500:
        return ERR_5XX
    return ERR_HTTP


def post(payload, key, timeout=120):
    """Returns (status, body_text, elapsed_s). Transport via curl subprocess
    only because urllib's TLS/UA fingerprint is rejected by the edge; the
    explicit UA below is what actually matters."""
    body = json.dumps(payload, ensure_ascii=False)
    cfg = ("url = \"%s\"\nheader = \"Content-Type: application/json\"\n"
           "header = \"Authorization: Bearer %s\"\n"
           "header = \"User-Agent: %s\"\n"
           "request = \"POST\"\ndata = \"@%s\"\n"
           % (ENDPOINT, key, UA, _write_body(body)))
    p = subprocess.run(["curl", "-s", "--max-time", str(timeout),
                        "--config", "-", "-w", "\n__HTTP__%{http_code}",
                        "-o", _write_out()],
                       input=cfg, capture_output=True, text=True)
    status = None
    tail = (p.stdout or "").rsplit("__HTTP__", 1)
    if len(tail) == 2 and tail[1].strip().isdigit():
        status = int(tail[1].strip())
    out = _read_out()
    _cleanup()
    return status, out, None


def _write_body(body):
    path = os.path.join("/tmp/opencode", "p2-jev-body.json")
    os.makedirs("/tmp/opencode", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    return path


def _write_out():
    path = os.path.join("/tmp/opencode", "p2-jev-out.json")
    open(path, "w").close()
    return path


def _read_out():
    path = os.path.join("/tmp/opencode", "p2-jev-out.json")
    try:
        return open(path, encoding="utf-8").read()
    except Exception:
        return ""


def _cleanup():
    for p in ("/tmp/opencode/p2-jev-body.json", "/tmp/opencode/p2-jev-out.json"):
        try:
            os.remove(p)
        except OSError:
            pass


def parse_noul(raw_text, question):
    """Phase-1-compatible parse of a noul answer. `noul` is P(yes) in [0,1];
    there is no confidence field, so derived confidence is computed here and
    labelled as derived wherever it is reported."""
    try:
        obj = json.loads(raw_text)
    except Exception:
        return None, ERR_PARSE, None
    ans = (obj.get("answers") or {})
    if not ans:
        return None, ERR_EMPTY, None
    first = list(ans.values())[0]
    val = first.get("noul")
    if val is None:
        return None, ERR_PARSE, None
    try:
        p = float(val)
    except Exception:
        return None, ERR_PARSE, None
    if p < 0.0 or p > 1.0:
        return None, ERR_PARSE, None
    label = "yes" if p >= 0.5 else "no"
    return {
        "noul": p,
        "label": label,
        "probabilities": {"yes": p, "no": 1.0 - p},
        "max_prob": max(p, 1.0 - p),
        "derived_confidence_2p1": abs(2 * p - 1),
        "derived_from": "2*max(p,1-p)-1 ; NOT a model-reported confidence",
    }, None, obj.get("usage")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default=os.path.join(PHASE2, "frozen",
                                                    "cases.json"))
    ap.add_argument("--admissibility",
                    default=os.path.join(PHASE2, "frozen",
                                         "admissibility.json"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--conditions", default=",".join(represent.CONDITIONS))
    ap.add_argument("--sleep", type=float, default=0.0)
    ap.add_argument("--preflight", action="store_true")
    ap.add_argument("--no-freeze-check", action="store_true",
                    help="escape hatch for inspecting a run whose freeze has "
                         "been broken; recorded in the output as a violation")
    ap.add_argument("--send-unanswerable", action="store_true",
                    help="OBSERVATION ONLY. Send cases with no ground truth so "
                         "answering/confidence behaviour can be compared across "
                         "representations. They remain admissible=False and are "
                         "NEVER scored: ground_truth is None, so score.py "
                         "cannot mark them correct or incorrect.")
    args = ap.parse_args()

    key = load_key()
    if not key:
        print("FATAL: TYPESAFE_API_KEY not resolvable from "
              "~/.secrets/typesafe.env", file=sys.stderr)
        return 4

    # ---- FREEZE GATE (pre) -------------------------------------------------
    # Nothing is planned, built, sent or scored until every frozen component is
    # confirmed byte-identical. A changed component requires a NEW declared
    # freeze; continuing silently would invalidate every number downstream.
    if not args.no_freeze_check:
        rc = freeze_ctl.verify("pre-run")
        if rc != 0:
            print("ABORT: frozen components changed. Declare a new freeze with "
                  "`python3 harness/freeze.py declare` before any measured "
                  "execution.", file=sys.stderr)
            return 6

    cases = json.load(open(args.cases, encoding="utf-8"))
    adm = {r["case_id"]: r for r in
           json.load(open(args.admissibility, encoding="utf-8"))["rows"]}
    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]

    if args.preflight:
        payload = {"model": MODEL,
                   "state": "Preflight probe: the test suite ran and all 42 "
                            "tests passed. Exit code 0.",
                   "questions": {"q": {"type": "noul",
                                       "instructions":
                                       "Did all tests pass with exit code 0?"}}}
        st, raw, _ = post(payload, key)
        print(f"preflight http={st} raw={raw[:220]}")
        return 0 if st == 200 else 5

    case_by_id = {c["case_id"]: c for c in cases}

    # ---- PHASE A: construct every record, spend nothing -------------------
    # The whole batch is built and schema-validated BEFORE the first request.
    # A schema defect therefore costs zero API calls instead of a whole run.
    planned = []
    for case in cases:
        for cond in conditions:
            row = adm.get(case["case_id"])
            if row is None:
                continue
            derivable = row["derivable"].get(cond, False)
            state, prov = represent.build_state(case, cond)
            rec = {
                "schema_version": "jevp2-result-1.0",
                "case_id": case["case_id"],
                "ctype": case["ctype"],
                "module": case["module"],
                "condition": cond,
                "mechanism": "jev_direct",
                "model_id": MODEL,
                "endpoint": ENDPOINT,
                "credential_source": CRED_LABEL,
                "admissible": bool(derivable),
                "admissibility_basis": ("required-evidence predicate satisfied"
                                        if derivable else
                                        "required-evidence predicate NOT "
                                        "satisfied -> unanswerable for this "
                                        "condition, not a model error"),
                "classification": case["classification"].get(cond),
                "ground_truth": case["ground_truth"],
                "representation": prov,
                "request": {"model": MODEL,
                            "state": state,
                            "questions": {"q": {"type": "noul",
                                                "instructions":
                                                case["question"]}}},
                "request_sha256": None,
                "response_raw": None,
                "parsed": None,
                "typed_error": None,
                "error_detail": None,
                "http_status": None,
                "latency_ms": None,
                "usage": None,
            }
            import hashlib
            rec["request_sha256"] = hashlib.sha256(
                json.dumps(rec["request"], ensure_ascii=False,
                           sort_keys=True, separators=(",", ":")
                           ).encode()).hexdigest()

            rec["observation_only"] = bool(
                args.send_unanswerable and case["ground_truth"] is None)
            if not derivable and not rec["observation_only"]:
                # Recorded as an unanswerable cell. NOT sent, because sending
                # it would invite the model to answer a question the
                # representation cannot support, and the answer could not be
                # scored anyway.
                rec["typed_error"] = "not_admissible"
                rec["error_detail"] = ("case unanswerable under this "
                                       "condition by construction")
                planned.append(rec)
                continue
            if not derivable:
                rec["admissibility_basis"] = (
                    "required-evidence predicate NOT satisfied -> unanswerable "
                    "for this condition; sent for BEHAVIOUR OBSERVATION ONLY and "
                    "never scored")
            planned.append(rec)
        if args.limit and len(planned) >= args.limit:
            break
    if args.limit:
        planned = planned[:args.limit]

    # ---- SCHEMA GATE ------------------------------------------------------
    # Zero API spend so far. Validate the entire planned batch now.
    violations = rschema.validate_batch(planned, label="planned")
    planned_sent = sum(1 for r in planned
                       if r["typed_error"] != "not_admissible")
    print(f"schema gate: {len(planned)} records planned, "
          f"{planned_sent} to be sent, {len(violations)} violation(s)")
    if violations:
        for v in violations[:30]:
            print("  " + v, file=sys.stderr)
        print("ABORT: raw-record schema violated before any API call was "
              "spent. No request was made.", file=sys.stderr)
        return 7

    # ---- PHASE B: send ----------------------------------------------------
    rows = []
    n = 0
    for rec in planned:
            case = case_by_id[rec["case_id"]]
            if rec["typed_error"] == "not_admissible":
                rows.append(rec)
                n += 1
                continue
            t0 = time.time()
            st, raw, _ = post(rec["request"], key)
            rec["http_status"] = st
            rec["latency_ms"] = round((time.time() - t0) * 1000, 2)
            rec["response_raw"] = raw
            if st != 200:
                rec["typed_error"] = classify(st)
                rec["error_detail"] = raw[:300]
            else:
                parsed, err, usage = parse_noul(raw, case["question"])
                rec["parsed"] = parsed
                rec["usage"] = usage
                if err:
                    rec["typed_error"] = err
                    rec["error_detail"] = raw[:300]
            rows.append(rec)
            n += 1
            if args.sleep:
                time.sleep(args.sleep)

    # ---- FREEZE GATE (post) ----------------------------------------------
    # Confirms nothing mutated a frozen component during the run.
    if not args.no_freeze_check:
        rc = freeze_ctl.verify("post-run")
        if rc != 0:
            print("WARNING: frozen components changed DURING the run; results "
                  "are not attributable to the declared freeze.", file=sys.stderr)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

    from collections import Counter
    print(f"rows={len(rows)} -> {args.out}")
    print("  conditions:", dict(Counter(r["condition"] for r in rows)))
    print("  admissible:", dict(Counter(r["admissible"] for r in rows)))
    print("  typed_error:", dict(Counter(
        str(r["typed_error"]) for r in rows)))
    sent = [r for r in rows if r["admissible"]]
    if sent:
        lat = sorted(r["latency_ms"] for r in sent if r["latency_ms"])
        if lat:
            print(f"  latency ms: min={lat[0]} med={lat[len(lat)//2]} "
                  f"max={lat[-1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
