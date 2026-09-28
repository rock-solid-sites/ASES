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



# --------------------------------------------------------------- question plan
# The runner used to be hardcoded to a single `noul` question, which cannot
# express an explicit-unknown arm or a shared-state multi-question request.
# This is the smallest correction that supports both: the question is data.
# With no --question-plan the built-in single-noul plan is used, so the existing
# Phase 2 command line behaves exactly as before.
DEFAULT_PLAN = {
    "noul_forced": {
        "type": "noul",
        "instructions": None,          # None -> take case["question"]
        "options": None,
    }
}


def load_plan(path):
    if not path:
        return DEFAULT_PLAN
    with open(path, encoding="utf-8") as fh:
        plan = json.load(fh)
    for arm, spec in plan.items():
        if spec.get("type") not in ("noul", "choice"):
            raise ValueError(f"arm {arm!r}: unsupported type {spec.get('type')!r}")
    return plan


def build_question(arm, spec, case, qid="q"):
    """Materialise one question for a case under one arm."""
    if spec["type"] == "noul":
        return qid, {"type": "noul",
                     "instructions": spec.get("instructions")
                     or case["question"]}
    options = spec.get("options") or []
    criteria = {o: spec.get("option_text", {}).get(o) for o in options} \
        if spec.get("option_text") else {o: None for o in options}
    # The case's own question MUST be carried into the instruction. An earlier
    # version used spec["instructions"] alone, which asked the model to pick a
    # label over the state with no question present; it returned a near-constant
    # answer on every case. The question is prefixed identically in every arm, so
    # the arms still differ only by the option set and its defining block.
    instructions = f"{case['question']}\n\n{spec['instructions']}"
    return qid, {"type": "choice",
                 "instructions": instructions,
                 "criteria": criteria}


def parse_choice(raw_text, options):
    """Parse a `choice` answer. Keeps probability, provider confidence, the
    selected option and a DERIVED confidence as separate fields; they are never
    merged. Per INSTRUMENT-VALIDATION.md the provider's `confidence` is a
    function of the probability vector, so it is recorded, not trusted."""
    try:
        obj = json.loads(raw_text)
    except Exception:                                        # noqa: BLE001
        return None, ERR_PARSE, None
    ans = obj.get("answers") or {}
    if not ans:
        return None, ERR_EMPTY, None
    first = list(ans.values())[0]
    sel = first.get("choice")
    probs = first.get("probabilities") or {}
    if sel is None:
        return None, ERR_PARSE, None
    try:
        probs = {k: float(v) for k, v in probs.items()}
    except Exception:                                        # noqa: BLE001
        probs = {}
    for k, v in probs.items():
        if v < 0.0 or v > 1.0:
            return None, ERR_PARSE, None
    total = sum(probs.values())
    if not probs or total <= 0:
        return None, ERR_PARSE, None
    p_sel = probs.get(sel)
    if p_sel is None:
        return None, ERR_PARSE, None
    n = len(probs)
    derived = (n * max(probs.values()) - 1) / (n - 1) if n > 1 else p_sel
    return {
        "primitive": "choice",
        "selected": sel,
        "probabilities": probs,
        "p_selected": p_sel,
        "max_prob": max(probs.values()),
        "prob_sum": round(total, 6),
        "provider_confidence": first.get("confidence"),
        "derived_confidence": round(derived, 6),
        "confidence_is_derived": True,
        "n_options": n,
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
    ap.add_argument("--question-plan", default=None,
                    help="JSON file mapping arm_id -> question spec; enables "
                         "explicit-unknown and multi-question arms")
    ap.add_argument("--arms", default=None,
                    help="comma-separated arm ids to run; default all in the plan")
    ap.add_argument("--packet", default=None,
                    help="restrict to case_ids listed in this JSON packet")
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

    pk_cache = {}
    if args.packet:
        pk = json.load(open(args.packet, encoding="utf-8"))
        pk_cache = pk if isinstance(pk, dict) else {}

    plan = load_plan(args.question_plan)
    if (not args.question_plan and args.packet
            and isinstance(pk_cache.get("plan"), dict)):
        # An experiment packet is the single source of truth for its own arms,
        # so a packet without an external --question-plan supplies its own.
        plan = pk_cache["plan"]

    arms = ([a.strip() for a in args.arms.split(",") if a.strip()]
            if args.arms else list(plan))
    for a in arms:
        if a not in plan:
            raise SystemExit(f"FATAL: arm {a!r} not in question plan")
    packet_send = {}
    packet_score = {}
    if isinstance(pk_cache.get("rows"), list):
        # An experiment packet is the SINGLE SOURCE OF TRUTH for its own cases,
        # send decision and score decision.
        #
        # Two defects are fixed together here, and they are coupled:
        #  1. this used to INTERSECT the packet's ids against `args.cases`, the
        #     Phase 2 frozen case file. A fresh-case experiment packet (Exp 3)
        #     has ids that by design appear in no earlier case file, so the
        #     intersection came out empty and the run reported `cases=0` and
        #     sent nothing -- silently, with exit status 0.
        #  2. the per-case loop skips any case with no Phase 2 admissibility
        #     row, so a fresh case was dropped a second time even had it
        #     survived (1).
        packet_send = {r["case_id"]: bool(r.get("send", True))
                       for r in pk_cache["rows"]}
        packet_score = {r["case_id"]: bool(r.get("score_for_correctness", True))
                        for r in pk_cache["rows"]}
        # Merge the packet row OVER the Phase 2 base case where one exists. A
        # packet that reuses Phase 2 case ids (Experiment 1) then keeps every
        # field the base provides -- notably `classification`, which the record
        # builder indexes -- while a packet of genuinely fresh cases (Experiment
        # 3) is taken wholly from the packet.
        base = {c["case_id"]: c for c in cases}
        cases = []
        for r in pk_cache["rows"]:
            if not r.get("send", True):
                continue
            merged = dict(base.get(r["case_id"], {}))
            merged.update(r)
            cases.append(merged)
        for c in cases:
            adm.setdefault(c["case_id"], {
                "case_id": c["case_id"],
                "derivable": {cond: True for cond in conditions},
                "provenance": "experiment packet supplies its own case; the "
                              "Phase 2 admissibility gate does not apply",
            })
        print(f"packet supplies {len(cases)} case(s) directly "
              f"({len(cases) - sum(1 for c in cases if c['case_id'] in base)} "
              f"fresh, not in the Phase 2 case file); the Phase 2 admissibility "
              f"gate is bypassed for this experiment")
    elif args.packet:
        keep = set(pk["case_ids"]) if isinstance(pk, dict) else set(pk)
        cases = [c for c in cases if c["case_id"] in keep]
    print(f"question plan: {len(plan)} arm(s); running {arms}; "
          f"conditions={conditions}; cases={len(cases)}")

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
          for arm in arms:
            row = adm.get(case["case_id"])
            if row is None:
                continue
            # Keyed by case_id, NOT by condition. An earlier version tested
            # `cond in packet_send`, which never matched because the dict is
            # keyed by case, so every case silently fell back to the Phase 2
            # admissibility gate -- which excludes exactly the unanswerable
            # cases Experiment 1 exists to measure.
            if case["case_id"] in packet_send:
                derivable = packet_send[case["case_id"]]
            else:
                derivable = row["derivable"].get(cond, False)
            state, prov = represent.build_state(case, cond)
            rec = {
                "schema_version": "jevp2-result-1.0",
                "case_id": case["case_id"],
                "ctype": case["ctype"],
                "module": case["module"],
                "condition": cond,
                "mechanism": f"jev_direct:{arm}",
                "model_id": MODEL,
                "endpoint": ENDPOINT,
                "credential_source": CRED_LABEL,
                "admissible": bool(derivable),
                "score_for_correctness": bool(
                    packet_score.get(case["case_id"], derivable)),
                "admissibility_basis": ("required-evidence predicate satisfied"
                                        if derivable else
                                        "required-evidence predicate NOT "
                                        "satisfied -> unanswerable for this "
                                        "condition, not a model error"),
                # A fresh-case packet need not carry `classification`; it is
                # Phase 2 metadata about the ctype, not a fact about the case.
                # Read it defensively so a packet-provided case does not crash
                # the record builder.
                "classification": (case.get("classification") or {}).get(cond),
                "ground_truth": case["ground_truth"],
                "representation": prov,
                "arm": arm,
                "request": {"model": MODEL,
                            "state": state,
                            "questions": {build_question(
                                arm, plan[arm], case)[0]:
                                build_question(arm, plan[arm], case)[1]}},
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
                spec = plan[rec["arm"]]
                if spec["type"] == "choice":
                    parsed, err, usage = parse_choice(
                        raw, spec.get("options") or [])
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
