#!/usr/bin/env python3
"""followup-03-operational — operational measurement runner (Jev vs MiMo V2.6 Flash).

WHAT THIS IS
------------
The narrow operational question `../findings.md` leaves open: given roughly matched
bounded-decision accuracy on the frozen corpus, does Jev provide a MATERIAL
latency / throughput / cost / operational advantage over the cheap general model
(`mimo-v2.6-flash`)?

This runner MEASURES. It does not score, judge, or conclude. The deliverable is
one NDJSON line per call, with the transport phase timings that make latency
decomposable. `harness/analyze_ops.py` does the arithmetic.

It is NOT a benchmark extension. The frozen corpus is not re-used to re-derive any
semantic result, and no accuracy number here is an outcome — correctness appears
only as a normalisation term for an operational ratio, scored against the frozen
ground truth with the F1 correction applied by the same function followup-02 uses.

DESIGN, FIXED BEFORE MEASURING
------------------------------
1. SUBSET — `STRAT-OPS-v1` (see `select_subset`). 16 of 64 cases, chosen by a
   seeded-constraint + area-round-robin rule that is a pure function of the
   frozen `cases.ndjson`. `subset.json` is written BEFORE any HTTP call, and the
   measure modes RE-DERIVE the selection and refuse to run if the stored id list
   is not what the rule produces from the same inputs. No cherry-picking is
   possible after the fact: the rule does not read any measurement.
2. WARM GRID — R = 12 warm repetitions per case per mechanism, SEQUENTIAL, one
   attempt, no retries, case-major order. A warm-up of 5 calls per mechanism runs
   first and is labelled `warmup` and excluded from every statistic.
3. IDLE/COLD PROXY — after >= 120 s idle per mechanism, the next 3 calls are
   labelled `idle`. This is an OBSERVABLE PROXY ONLY. Per-call cold start is not
   directly observable on a shared stateless HTTPS endpoint, and this run does
   not claim to observe it.
4. CONCURRENCY — a fixed block of 6 cases x 2 reps = 12 calls per mechanism at
   C = 1, 4, 8, as parallel curl processes, fixed case-major order, no retries.
   Makespan, per-call latency, HTTP status, 429s and failures are all recorded.
   Rate limiting that makes the block unclean is REPORTED as an operational
   finding, never worked around by lowering C or adding retries.
5. TRANSPORT PROBE — connect-only (no inference) requests per endpoint quantify
   DNS/TCP/TLS overhead. Recorded in `results/transport_probe.json`, kept out of
   the model-latency statistics entirely.
6. INTERFACE PROBE — clearly labelled, OUTSIDE the grid: one MiMo call with
   `logprobs: true` to test probability availability, and Jev's distribution
   availability read from the FROZEN responses rather than from new calls.

TRANSPORT: CURL FOR BOTH MECHANISMS
-----------------------------------
`curl` is the transport for Jev as well as for MiMo, with the same `-w` phase
timings, one process per call and no connection reuse (`num_connects` is recorded
so the no-reuse claim is checkable rather than asserted). The frozen Jev
transport was Python `urllib`; that difference is a real change and is handled
explicitly, not waved through:

  * the request BODY is byte-identical to the frozen row (gate below), and the
    same headers the frozen `common.post_json` sent are sent (bearer, JSON
    content type, the frozen explicit `User-Agent`, and the frozen
    `x-opencode-session: jev-phase1-run`);
  * equivalence is then VALIDATED empirically, not assumed: the `verify` mode
    compares the curl-transported labels/distributions for every subset case
    against the frozen `results/jev_raw.ndjson` rows (>= 4 cases by construction)
    and records the agreement rate per case. `analyze_ops.py` reports it and the
    report states what it does and does not license.

MiMo's frozen transport in followup-02 was already curl, so for MiMo the curl
transport is not a change at all — it is the same transport as the run whose
accuracy was already measured.

CREDENTIALS
-----------
  Jev  — `$OPENCODE_GO_API_KEY`                     (label `env:OPENCODE_GO_API_KEY`)
  MiMo — `~/.local/share/opencode/auth.json` ->
          `opencode-go.key`                        (label `auth.json#opencode-go`)

The Go route is served to the CLI-store credential; the env credential is
unsubscribed for Go models (measured in followup-02, HTTP 403 "subscription is
required"). Both sources are checked for RESOLVABILITY before any call and a
missing source is a hard stop — the run never shops for a credential that
happens to work. A credential is read at runtime, held in memory, and handed to
curl through a config on STDIN (`curl -K -`), so it appears in neither argv (where
`/proc/*/cmdline` and shell history expose it) nor any file. ONLY THE SOURCE
LABEL is ever written to an artefact. Credential values are never printed, logged
or stored.

N = 1 ATTEMPT, NO RETRIES
-------------------------
Every call is exactly one HTTP request. There is no retry path in the call path
at any concurrency level: a failed call is recorded with its typed error and
never re-sent. A retry on exactly the cells that failed would convert an N=1
observation into a survivorship-biased N>1 one.

FROZEN-CONDITION GATE
---------------------
No grid call is made unless ALL of the following hold, or the process exits
non-zero without touching the network:

  * both frozen input digests match (cases.ndjson, results/jev_raw.ndjson);
  * for all 64 cases the Jev body rebuilt by the FROZEN `run_jev.build_request`
    is both `==` the frozen row's `request_body` and hashes to the frozen
    `request_hash`;
  * for all 64 cases the general body rebuilt by the FROZEN
    `run_baselines.build_general_request` with the FROZEN model id is likewise
    identical to the frozen `general_model` row — after which exactly ONE field,
    `model`, is swapped to `mimo-v2.6-flash`, per the brief;
  * the F1 correction is derivable from `control.pair_id` and names exactly the
    ids `verification.md` §2 F1 names (a hard stop otherwise);
  * `subset.json` exists and its id list is reproduced by `select_subset` from the
    same frozen inputs;
  * the mechanism's credential source resolves.

Request builders, the system prompt, `max_tokens`, `temperature` and the label
parsers are IMPORTED from the frozen harnesses, not re-implemented. Re-typing a
frozen constant is how a "frozen" run silently stops being frozen.

Usage:
    python3 harness/run_ops.py subset
    python3 harness/run_ops.py transport
    python3 harness/run_ops.py verify
    python3 harness/run_ops.py warm        --mechanism jev|mimo
    python3 harness/run_ops.py idle        --mechanism jev|mimo
    python3 harness/run_ops.py concurrency --mechanism jev|mimo
    python3 harness/run_ops.py probe       --mechanism mimo
"""
from __future__ import annotations

import argparse
import copy
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
sys.path.insert(0, PHASE1_HARNESS)

from common import (  # noqa: E402
    ERR_4XX,
    ERR_INTERNAL,
    ERR_NETWORK,
    ERR_TIMEOUT,
    ERR_429,
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
from run_baselines import (  # noqa: E402
    GENERAL_MAX_TOKENS,
    GENERAL_MODEL,
    GEN_SYS,
    GO_CHAT_URL,
    build_general_request,
    parse_general,
)
from run_jev import JEV_MODEL, JEV_URL, build_request  # noqa: E402

RUNNER_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# mechanisms
# ---------------------------------------------------------------------------
JEV = "jev"
MIMO = "mimo_v26_flash"
MECHANISMS = (JEV, MIMO)

# `mimo-v2.6-flash` (family mimo), ID verified in the live catalog
# (`opencode models opencode-go` -> `opencode-go/mimo-v2.6-flash`) on 2026-09-26.
MIMO_MODEL = "mimo-v2.6-flash"
MIMO_CATALOG_ID = "opencode-go/mimo-v2.6-flash"
MIMO_FAMILY = "mimo"

MECH = {
    JEV: {
        "mechanism": JEV,
        "model_id": JEV_MODEL,
        "model_catalog_id": JEV_MODEL,
        "family": "jev",
        "endpoint": JEV_URL,
        "transport": "curl",
        "frozen_transport": "python-urllib",
        "session_header_value": "jev-phase1-run",
        "credential_source": "env:OPENCODE_GO_API_KEY",
        "raw_path": "jev_ops_raw.ndjson",
    },
    MIMO: {
        "mechanism": MIMO,
        "model_id": MIMO_MODEL,
        "model_catalog_id": MIMO_CATALOG_ID,
        "family": MIMO_FAMILY,
        "endpoint": GO_CHAT_URL,
        "transport": "curl",
        "frozen_transport": "curl",
        "session_header_value": None,       # uuid4 per call, see session_id()
        "credential_source": "auth.json#opencode-go",
        "raw_path": "mimo_ops_raw.ndjson",
    },
}

# USD per million tokens, from the operator directive of 2026-09-26 / current
# catalog. These are PRICING AND ENTITLEMENT FACTS, tier-dependent and
# promotional, kept strictly separate from every structural measurement. No
# number in this file uses a price to support a latency or throughput claim.
COST_PER_MTOK = {"input": 0.14, "output": 0.28, "cache_read": 0.0028,
                 "cache_write": 0.0}
JEV_COST_PER_MTOK = {"input": 0.0, "output": 0.0, "cache_read": 0.0,
                     "cache_write": 0.0}
MODEL_COST_PER_MTOK = {
    MIMO_MODEL: COST_PER_MTOK,
    JEV_MODEL: JEV_COST_PER_MTOK,
}

# ---------------------------------------------------------------------------
# credentials
# ---------------------------------------------------------------------------
API_KEY_ENV = "OPENCODE_GO_API_KEY"
AUTH_JSON = "~/.local/share/opencode/auth.json"
AUTH_JSON_PROVIDER = "opencode-go"
LABEL_ENV = "env:OPENCODE_GO_API_KEY"
LABEL_AUTHJSON = "auth.json#opencode-go"
SESSION_HEADER = "x-opencode-session"

# ---------------------------------------------------------------------------
# design constants — fixed before measurement, recorded in subset.json
# ---------------------------------------------------------------------------
SUBSET_N = 16
WARM_REPS = 12
WARMUP_CALLS = 5
IDLE_SECONDS = 120
IDLE_CALLS = 3
CONC_CASES = 6
CONC_REPS = 2
CONC_LEVELS = (1, 4, 8)
TRANSPORT_PROBE_CALLS = 3
MAX_ATTEMPTS = 1                     # N = 1. Not a tunable. See module docstring.
RETRIES = 0

# verification.md §2 F1: cp4's ground truth is not derivable from the
# model-visible text; both members are reclassified unanswerable. Carried over
# unchanged so "the F1 correction applied consistently" means the SAME correction,
# derived by the SAME rule, not a lookalike.
F1_PAIR_ID = "cp4"
F1_MEMBER_IDS = ["c-p4a", "c-p4b"]

FROZEN_INPUTS = {
    "cases.ndjson":
        "7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c",
    "results/jev_raw.ndjson":
        "e17ae014f0fc6cc311646dbfd98d5115d41854ddfcb98cfb41268f2da482d3bc",
}

SUBSET_PATH = os.path.join(FOLLOWUP, "subset.json")
RESULTS = os.path.join(FOLLOWUP, "results")
TRANSPORT_PROBE_PATH = os.path.join(RESULTS, "transport_probe.json")

# canonical, fixed call order for every sequential phase: subset id order
PHASE_ORDER = ("warmup", "warm", "idle", "concurrency")

CURL_WRITE_OUT = (
    "\n__OPS__%{json}"
)


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def sha256_file(path):
    h = __import__("hashlib").sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_ndjson(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


class Appender:
    """Append-only NDJSON writer that tolerates re-entry (resumable phases).

    Phases are separately invocable so a long run can be checkpointed. A phase
    that is re-run must not double-count, so the caller passes the keys already
    present and the writer refuses to emit a duplicate call key.
    """

    def __init__(self, path, seen):
        self.path = path
        self.seen = seen
        self.n = 0

    def write(self, row):
        key = call_key(row)
        if key in self.seen:
            return False
        self.seen.add(key)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        self.n += 1
        return True


def call_key(row):
    return "|".join(str(row.get(k)) for k in
                    ("mechanism", "phase", "case_id", "repeat", "concurrency",
                     "block", "probe"))


def session_id(cli_value=None):
    """The `x-opencode-session` value for this run.

    Jev's is FIXED to the frozen `run_jev` default (`jev-phase1-run`) so the
    header set is byte-identical to the frozen run. MiMo's is a per-run uuid4:
    the Go route answers 400 `MissingSessionID` without it. It is a provider
    grouping header, not a credential — recorded because it is how a reader ties
    a provider-side request log to this run, which discloses nothing.
    """
    global _SESSION
    if _SESSION.get("id") is None:
        _SESSION["id"] = cli_value or str(uuid.uuid4())
    return _SESSION["id"]


_SESSION = {"id": None}


# ---------------------------------------------------------------------------
# credentials — read at runtime, never printed, never stored
# ---------------------------------------------------------------------------
def resolve_credential(label):
    """The credential named by `label`, or None when absent/unreadable.

    Returns the VALUE to the caller only. No caller of this function writes the
    value to an artefact, and the run prints only whether a source RESOLVED.
    """
    if label == LABEL_ENV:
        return os.environ.get(API_KEY_ENV) or None
    if label == LABEL_AUTHJSON:
        path = os.path.expanduser(AUTH_JSON)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return None
        node = data.get(AUTH_JSON_PROVIDER)
        if isinstance(node, dict):
            value = node.get("key")
            return value if isinstance(value, str) and value else None
        return None
    raise SystemExit(f"FATAL: unknown credential source label {label!r}")


# ---------------------------------------------------------------------------
# F1 correction — derived, then checked against the documented ids
# ---------------------------------------------------------------------------
def f1_corrected_cases(cases):
    """Cases with the verification.md §2 F1 correction applied.

    The pair is DERIVED from `control.pair_id`, not hardcoded, and then checked
    against the ids F1 names. A mismatch is a hard stop: the correction must be
    exactly the documented one or "applied consistently" is a lie.
    """
    members = [c for c in cases if c["control"]["pair_id"] == F1_PAIR_ID]
    ids = sorted(c["id"] for c in members)
    if ids != F1_MEMBER_IDS:
        raise SystemExit(
            f"F1 CORRECTION FAIL: pair {F1_PAIR_ID} is {ids}, expected "
            f"{F1_MEMBER_IDS} as named in verification.md §2 F1")
    for c in members:
        if not c["ground_truth"]["answerable"]:
            raise SystemExit(
                f"F1 CORRECTION FAIL: {c['id']} is already unanswerable in the "
                "committed corpus; the correction would be a no-op")
    out = []
    for c in cases:
        d = copy.deepcopy(c)
        if c["id"] in ids:
            d["ground_truth"]["answerable"] = False
            d["ground_truth"]["answer"] = None
            d["ground_truth"]["abstain_expected"] = True
            d["_f1_corrected"] = True
        else:
            d["_f1_corrected"] = False
        out.append(d)
    return out, ids


# ---------------------------------------------------------------------------
# FROZEN-CONDITION GATE
# ---------------------------------------------------------------------------
def frozen_gate():
    """Every frozen condition, verified. Raises SystemExit on any drift."""
    report = {"digests": {}, "jev_request_gate": None,
              "general_request_gate": None, "f1": {}, "credentials": {}}

    for rel, expect in FROZEN_INPUTS.items():
        path = os.path.join(PHASE1, rel)
        got = sha256_file(path)
        if got != expect:
            raise SystemExit(
                f"FROZEN INPUT MISMATCH {rel}: expected {expect}, found {got}. "
                "Refusing to make any call.")
        report["digests"][rel] = {"expected": expect, "actual": got, "match": True}

    cases = load_cases(os.path.join(PHASE1, "cases.ndjson"))
    by_id = {c["id"]: c for c in cases}
    jev = {r["case_id"]: r for r in load_ndjson(
        os.path.join(PHASE1, "results", "jev_raw.ndjson"))}
    gen = {}
    for r in load_ndjson(os.path.join(PHASE1, "results", "baselines_raw.ndjson")):
        if r.get("mechanism") == "general_model":
            gen[r["case_id"]] = r

    n_ok, bad = 0, []
    for cid, case in by_id.items():
        body = build_request(case, JEV_MODEL)
        row = jev.get(cid)
        if (row is not None and body == row["request_body"]
                and request_hash(body) == row["request_hash"]):
            n_ok += 1
        else:
            bad.append(cid)
    if bad or n_ok != len(by_id):
        raise SystemExit(
            f"FROZEN REQUEST GATE (jev) FAILED: {n_ok}/{len(by_id)} identical, "
            f"first divergent {bad[:5]}. Refusing to make any call.")
    report["jev_request_gate"] = {
        "n_cases": len(by_id), "n_identical": n_ok,
        "checks": ["request_body structural equality",
                   "request_hash == sha256(serialise(body))"],
        "builder": "frozen harness/run_jev.build_request (imported, not re-typed)",
    }

    n_ok, bad = 0, []
    for cid, case in by_id.items():
        body = build_general_request(case, GENERAL_MODEL)
        row = gen.get(cid)
        if (row is not None and body == row["request_body"]
                and request_hash(body) == row["request_hash"]):
            n_ok += 1
        else:
            bad.append(cid)
    if bad or n_ok != len(by_id):
        raise SystemExit(
            f"FROZEN REQUEST GATE (general_model) FAILED: {n_ok}/{len(by_id)} "
            f"identical, first divergent {bad[:5]}. Refusing to make any call.")
    report["general_request_gate"] = {
        "n_cases": len(by_id), "n_identical": n_ok,
        "checks": ["request_body structural equality",
                   "request_hash == sha256(serialise(body))"],
        "frozen_model_id": GENERAL_MODEL,
        "permitted_difference": "the `model` field, swapped to "
                                f"{MIMO_MODEL!r} (the brief's one change)",
        "inherited_conditions": {
            "system_prompt": GEN_SYS,
            "max_tokens": GENERAL_MAX_TOKENS,
            "temperature": 0,
            "attempts": 1,
        },
        "builder": "frozen harness/run_baselines.build_general_request "
                   "(imported, not re-typed)",
    }

    _, ids = f1_corrected_cases(cases)
    report["f1"] = {
        "pair_id": F1_PAIR_ID, "case_ids": ids,
        "source": "verification.md §2 F1",
        "derivation": "derived from control.pair_id, then checked against the "
                      "documented ids",
    }

    for label in (LABEL_ENV, LABEL_AUTHJSON):
        value = resolve_credential(label)
        report["credentials"][label] = {
            "resolvable": bool(value),
            "length": len(value) if value else 0,
            "value_recorded": False,
        }
    for mech, spec in MECH.items():
        if not report["credentials"][spec["credential_source"]]["resolvable"]:
            raise SystemExit(
                f"FATAL: credential source {spec['credential_source']!r} required "
                f"by mechanism {mech!r} is not resolvable. Refusing to run; this "
                "harness never shops for a credential that happens to work.")
    return report, cases


# ---------------------------------------------------------------------------
# SUBSET — rule STRAT-OPS-v1
# ---------------------------------------------------------------------------
# The rule is a pure function of `cases.ndjson`. It reads NO measurement, so the
# subset cannot be chosen after seeing a result. Written out longhand here
# because a subset rule that only exists as code is not auditable.
SUBSET_RULE = {
    "id": "STRAT-OPS-v1",
    "inputs": "frozen cases.ndjson only",
    "candidate_order": "ascending case id (byte order)",
    "real_contrastive_pair": "a control.pair_id with exactly 2 members",
    "area_default_stratum": {
        "A": {"answerable": True, "variant_kind": "base"},
        "B": {"answerable": False, "variant_kind": "base"},
        "C": {"answerable": True, "variant_kind": "base"},
        "D": {"answerable": True, "variant_kind": "base"},
    },
    "area_default_stratum_why":
        "Each area's MODAL (area, answerable, variant_kind) cell. B contains no "
        "answerable case at all (all 13 are unanswerable), so a single global "
        "'answerable base' stratum would have made area B unrepresentable and "
        "silently dropped the area with the most unanswerable cases.",
    "steps": [
        "S0 sort all 64 candidates by ascending case id",
        "S1 seed qtype=score: lowest id with question_type == 'score'",
        "S2 seed qtype=choice, control base: lowest id with question_type == "
        "'choice' AND variant_kind == 'base'",
        "S3 seed unanswerable in area A: lowest id, area A, not answerable",
        "S4 seed unanswerable control variant: lowest id, area B, not "
        "answerable, variant_kind != 'base'",
        "S5 seed unanswerable control base: lowest id, area B, not answerable, "
        "variant_kind == 'base'",
        "S6 seed answerable control variant: lowest id, area A, answerable, "
        "variant_kind != 'base'",
        "S7 seed contrastive pair: among REAL pairs (exactly 2 members) with both "
        "members answerable, sorted by pair_id ascending, take the first pair "
        "with NEITHER member already selected; add both members",
        "S8 fill: round-robin over areas A,B,C,D in that fixed order; in each "
        "round take each area's lowest-id untaken case from that area's default "
        "stratum; stop at SUBSET_N",
        "S9 verify every required constraint; any violation is a hard stop",
    ],
    "required_constraints": {
        "n_between": [12, 16],
        "areas_all_of": ["A", "B", "C", "D"],
        "qtypes_at_least": {"noul": 1, "choice": 1, "score": 1},
        "unanswerable_at_least": 3,
        "control_variant_at_least": 1,
        "both_members_of_one_contrastive_pair": 1,
    },
    "not_used_for_selection": [
        "any latency, token, cost or stability measurement",
        "any correctness or error rate",
        "any Jev or MiMo response",
    ],
}


def _lowest(cands, pred, taken):
    for c in sorted(cands, key=lambda r: r["id"]):
        if c["id"] in taken:
            continue
        if pred(c):
            return c
    return None


def select_subset(cases, n=SUBSET_N):
    """STRAT-OPS-v1. Returns (selected_list_in_selection_order, trace)."""
    cands = sorted(cases, key=lambda r: r["id"])
    taken, trace, ordered = set(), [], []

    def add(c, why):
        if c is None or c["id"] in taken:
            raise SystemExit(
                f"SUBSET RULE {SUBSET_RULE['id']}: seed {why} found no eligible "
                f"case. The frozen corpus changed shape; re-derive the rule "
                "rather than relaxing a constraint.")
        taken.add(c["id"])
        ordered.append(c["id"])
        trace.append({"step": why, "case_id": c["id"]})

    def qtype(t):
        return lambda c: c["questions"][0]["type"] == t

    add(_lowest(cands, qtype("score"), taken), "S1 qtype=score")
    add(_lowest(cands, lambda c: qtype("choice")(c)
                and c["control"]["variant_kind"] == "base", taken),
        "S2 qtype=choice control base")
    add(_lowest(cands, lambda c: c["area"] == "A"
                and not c["ground_truth"]["answerable"], taken),
        "S3 unanswerable in area A")
    add(_lowest(cands, lambda c: c["area"] == "B"
                and not c["ground_truth"]["answerable"]
                and c["control"]["variant_kind"] != "base", taken),
        "S4 unanswerable control variant")
    add(_lowest(cands, lambda c: c["area"] == "B"
                and not c["ground_truth"]["answerable"]
                and c["control"]["variant_kind"] == "base", taken),
        "S5 unanswerable control base")
    add(_lowest(cands, lambda c: c["area"] == "A"
                and c["ground_truth"]["answerable"]
                and c["control"]["variant_kind"] != "base", taken),
        "S6 answerable control variant")

    # S7 — first real pair, by pair_id, with both members answerable and
    # neither already selected.
    counts = {}
    for c in cands:
        counts[c["control"]["pair_id"]] = counts.get(c["control"]["pair_id"], 0) + 1
    pair_members = {}
    for c in cands:
        if counts[c["control"]["pair_id"]] == 2:
            pair_members.setdefault(c["control"]["pair_id"], []).append(c)
    chosen_pair = None
    for pid in sorted(pair_members):
        members = sorted(pair_members[pid], key=lambda r: r["id"])
        if (all(m["ground_truth"]["answerable"] for m in members)
                and not any(m["id"] in taken for m in members)):
            chosen_pair = pid
            add(members[0], f"S7 contrastive pair {pid} member 1")
            add(members[1], f"S7 contrastive pair {pid} member 2")
            break
    if chosen_pair is None:
        raise SystemExit(
            f"SUBSET RULE {SUBSET_RULE['id']}: no eligible contrastive pair. "
            "The required constraint cannot be satisfied.")

    # S8 — round-robin area fill from each area's default stratum.
    areas = ("A", "B", "C", "D")
    for area in areas:
        stratum = SUBSET_RULE["area_default_stratum"][area]
        def in_stratum(c, area=area, stratum=stratum):
            if c["area"] != area or c["id"] in taken:
                return False
            if c["ground_truth"]["answerable"] != stratum["answerable"]:
                return False
            return (c["control"]["variant_kind"] == "base") == (
                stratum["variant_kind"] == "base")
        if _lowest(cands, in_stratum, taken) is None:
            raise SystemExit(
                f"SUBSET RULE {SUBSET_RULE['id']}: area {area} default stratum "
                "is empty; the area quota cannot be filled.")
    round_no = 0
    while len(ordered) < n:
        round_no += 1
        progressed = False
        for area in areas:
            if len(ordered) >= n:
                break
            stratum = SUBSET_RULE["area_default_stratum"][area]
            def in_stratum(c, area=area, stratum=stratum):
                if c["area"] != area or c["id"] in taken:
                    return False
                if c["ground_truth"]["answerable"] != stratum["answerable"]:
                    return False
                return (c["control"]["variant_kind"] == "base") == (
                    stratum["variant_kind"] == "base")
            c = _lowest(cands, in_stratum, taken)
            if c is not None:
                add(c, f"S8 area round {round_no} fill ({area} default stratum)")
                progressed = True
        if not progressed:
            raise SystemExit(
                f"SUBSET RULE {SUBSET_RULE['id']}: round {round_no} could not "
                f"fill to n={n} (stopped at {len(ordered)}).")
    return ordered, {"trace": trace, "contrastive_pair": chosen_pair,
                     "rounds": round_no}


def verify_subset_constraints(sel_cases):
    """S9. Every required constraint, checked. Any violation raises."""
    n = len(sel_cases)
    req = SUBSET_RULE["required_constraints"]
    lo, hi = req["n_between"]
    problems = []
    if not (lo <= n <= hi):
        problems.append(f"n={n} outside [{lo},{hi}]")
    areas = sorted({c["area"] for c in sel_cases})
    if areas != req["areas_all_of"]:
        problems.append(f"areas {areas} != {req['areas_all_of']}")
    for t, k in req["qtypes_at_least"].items():
        got = sum(1 for c in sel_cases if c["questions"][0]["type"] == t)
        if got < k:
            problems.append(f"qtype {t}: {got} < {k}")
    nun = sum(1 for c in sel_cases if not c["ground_truth"]["answerable"])
    if nun < req["unanswerable_at_least"]:
        problems.append(f"unanswerable {nun} < {req['unanswerable_at_least']}")
    nvar = sum(1 for c in sel_cases if c["control"]["variant_kind"] != "base")
    if nvar < req["control_variant_at_least"]:
        problems.append(f"control variants {nvar} < {req['control_variant_at_least']}")
    counts = {}
    for c in sel_cases:
        counts[c["control"]["pair_id"]] = counts.get(c["control"]["pair_id"], 0) + 1
    full = sorted(p for p, k in counts.items() if k == 2)
    if not full:
        problems.append("no complete contrastive pair present")
    if problems:
        raise SystemExit("SUBSET CONSTRAINT FAIL: " + "; ".join(problems))
    return {
        "n": n, "areas": areas,
        "by_area": {a: sum(1 for c in sel_cases if c["area"] == a)
                    for a in req["areas_all_of"]},
        "by_question_type": {
            t: sum(1 for c in sel_cases if c["questions"][0]["type"] == t)
            for t in ("noul", "choice", "score")},
        "n_unanswerable": nun,
        "n_control_variants": nvar,
        "complete_contrastive_pairs": full,
        "all_constraints_satisfied": True,
    }


# ---------------------------------------------------------------------------
# transport — curl with phase timings, one process per call, no reuse
# ---------------------------------------------------------------------------
def call_curl(endpoint, body_obj, api_key, mech, timeout=TIMEOUT_SECONDS,
              extra_headers=None, connect_only=False, raw_body=None):
    """One curl process, one HTTP request. Never raises.

    Timing comes from curl's own `-w %{json}` (namelookup / connect /
    appconnect / pretransfer / starttransfer / total / num_connects), NOT from a
    wall clock around the subprocess, so process spawn cost is separable and the
    two mechanisms are measured by the same instrument.

    The bearer token is handed to curl on STDIN as a config line, so it is in
    neither argv (where /proc/*/cmdline and shell history expose it) nor any
    file. The request body carries no secret and goes as an argv value, which
    keeps the two channels from colliding.
    """
    if any(ch in api_key for ch in ('"', "\\", "\n", "\r")):
        return {"timings": None, "http_status": None, "raw_response": "",
                "typed_error": ERR_INTERNAL, "bytes": 0,
                "error_detail": "credential is not expressible in a curl config"}

    cfg = 'header = "Authorization: Bearer %s"\n' % api_key
    args = ["curl", "--silent", "--show-error", "--config", "-",
            "--max-time", str(timeout), "--write-out", CURL_WRITE_OUT]
    if connect_only:
        # DNS + TCP + TLS and nothing else. `--head` sends no request body and
        # carries no model input, so NO inference happens and no token is
        # spent; the handshake cost is the cumulative `time_appconnect`. This is
        # a transport measurement of the network path, and it is recorded
        # separately so it can never be folded into a model-latency statistic.
        args += ["--head", "--output", os.devnull, endpoint]
    else:
        args += ["--header", "Content-Type: application/json",
                 "--header", "User-Agent: %s" % USER_AGENT]
        if mech == JEV:
            args += ["--header", "%s: %s" % (SESSION_HEADER,
                                            MECH[JEV]["session_header_value"])]
        else:
            args += ["--header", "%s: %s" % (SESSION_HEADER, session_id())]
        for h in (extra_headers or []):
            args += ["--header", h]
        payload = raw_body if raw_body is not None else serialise(body_obj)
        args += ["--data-binary", payload, endpoint]

    out = {"timings": None, "http_status": None, "raw_response": "",
           "typed_error": ERR_NETWORK, "bytes": 0, "error_detail": None}
    try:
        proc = subprocess.run(args, input=cfg, capture_output=True, text=True)
    except Exception as e:  # noqa: BLE001 - the grid must stay complete
        out["typed_error"] = ERR_INTERNAL
        out["error_detail"] = f"{type(e).__name__}: {e}"[:200]
        return out

    stdout = proc.stdout or ""
    marker = "\n__OPS__"
    if marker not in stdout:
        timed_out = proc.returncode == 28
        out["typed_error"] = ERR_TIMEOUT if timed_out else ERR_NETWORK
        out["raw_response"] = stdout
        out["error_detail"] = (f"curl rc={proc.returncode} "
                               f"{(proc.stderr or '').strip()}")[:200]
        return out
    body_txt, _, meta = stdout.rpartition(marker)
    try:
        timings = json.loads(meta)
    except ValueError:
        out["typed_error"] = ERR_INTERNAL
        out["error_detail"] = f"unparseable curl write-out {meta[:120]!r}"
        return out
    out["timings"] = timings
    try:
        status = int(timings.get("http_code"))
    except (TypeError, ValueError):
        out["typed_error"] = ERR_INTERNAL
        out["error_detail"] = "curl write-out carried no http_code"
        return out
    out["http_status"] = status
    out["bytes"] = timings.get("size_download")
    if connect_only:
        # A HEAD answering 405/404/200 is a REACHABLE endpoint, not a failure.
        out["typed_error"] = None
        out["error_detail"] = None
        return out
    raw = body_txt.rstrip("\n")
    out["raw_response"] = raw
    code = classify(status)
    out["typed_error"] = code
    out["error_detail"] = None if code is None else f"HTTP {status}"
    return out


# ---------------------------------------------------------------------------
# token accounting
# ---------------------------------------------------------------------------
def token_counts(usage):
    if not isinstance(usage, dict):
        return None
    raw = usage.get("raw") if isinstance(usage.get("raw"), dict) else usage

    def pick(*names):
        for nm in names:
            v = raw.get(nm)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                return int(v)
        return 0

    out = {
        "input_tokens": pick("input_tokens", "prompt_tokens"),
        "output_tokens": pick("output_tokens", "completion_tokens"),
        "total_tokens": pick("total_tokens"),
        "cache_read_tokens": pick("cache_read_input_tokens", "cache_read_tokens",
                                  "cached_tokens"),
        "cache_write_tokens": pick("cache_creation_input_tokens",
                                   "cache_write_tokens"),
        "reasoning_tokens": 0,
    }
    details = (raw.get("completion_tokens_details")
               or raw.get("output_tokens_details"))
    if isinstance(details, dict):
        for k in ("reasoning_tokens", "reasoning"):
            v = details.get(k)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                out["reasoning_tokens"] = int(v)
                break
    if not out["reasoning_tokens"]:
        for k in ("reasoning_tokens", "reasoning_content_tokens"):
            v = raw.get(k)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                out["reasoning_tokens"] = int(v)
                break
    return out


def derived_cost_usd(counts, model_id):
    """Derived USD attributed to the model that actually consumed the tokens."""
    if not counts or not any(counts.values()):
        return None
    rates = MODEL_COST_PER_MTOK.get(model_id)
    if rates is None:
        return None
    total = 0.0
    for rate_key, field in (("input", "input_tokens"), ("output", "output_tokens"),
                            ("cache_read", "cache_read_tokens"),
                            ("cache_write", "cache_write_tokens")):
        total += (counts.get(field) or 0) / 1_000_000.0 * rates[rate_key]
    return round(total, 10)


# ---------------------------------------------------------------------------
# call construction
# ---------------------------------------------------------------------------
def build_call_body(mech, case):
    """The request body for one call. Only `model` ever differs from frozen."""
    if mech == JEV:
        return build_request(case, JEV_MODEL)
    return build_general_request(case, MIMO_MODEL)


def parse_call(mech, raw, case):
    """(parsed, prediction, typed_error) using the FROZEN parsers."""
    if mech == JEV:
        parsed, prediction, err = parse_jev(raw, case)
        if err is not None:
            return parsed, prediction, err
        return parsed, prediction, None
    prediction, err = parse_general(raw, case)
    if err is not None:
        return None, prediction, err
    obj = None
    try:
        obj = json.loads(raw)
    except Exception:  # noqa: BLE001
        return None, prediction, err
    msg = ((obj or {}).get("choices") or [{}])[0].get("message") or {}
    parsed = {
        "type": case["questions"][0]["type"],
        "content": msg.get("content"),
        "reasoning_content_present": msg.get("reasoning_content") is not None,
        "finish_reason": ((obj or {}).get("choices") or [{}])[0].get("finish_reason"),
        "logprobs": ((obj or {}).get("choices") or [{}])[0].get("logprobs"),
    }
    return parsed, prediction, None


def base_row(mech, case, phase, repeat, concurrency, block, probe):
    return {
        "schema_version": "jevp1-ops-result-1.0",
        "mechanism": mech,
        "model_id": MECH[mech]["model_id"],
        "model_catalog_id": MECH[mech]["model_catalog_id"],
        "family": MECH[mech]["family"],
        "endpoint": MECH[mech]["endpoint"],
        "case_id": case["id"] if case else None,
        "area": case["area"] if case else None,
        "question_type": (case["questions"][0]["type"] if case else None),
        "answerable_frozen": (case["ground_truth"]["answerable"] if case else None),
        "control_variant_kind": (case["control"]["variant_kind"] if case else None),
        "phase": phase,
        "repeat": repeat,
        "concurrency": concurrency,
        "block": block,
        "probe": probe,
        "attempts": 1,
        "retries": RETRIES,
        "timestamp_utc": utc_now_iso(),
        "credential_source": MECH[mech]["credential_source"],
        "secrets_recorded": False,
        "transport": {
            "client": "curl",
            "frozen_transport": MECH[mech]["frozen_transport"],
            "transport_changed_from_frozen":
                MECH[mech]["transport"] != MECH[mech]["frozen_transport"],
            "one_process_per_call": True,
            "connection_reuse": False,
            "curl_write_out": "%%{json} (phase timings + num_connects)",
            "timeout_seconds": TIMEOUT_SECONDS,
            "user_agent_header": USER_AGENT,
            "session_header": SESSION_HEADER,
        },
        "harness_version": RUNNER_VERSION,
    }


def run_one(mech, case, api_key, phase, repeat, concurrency=1, block=None,
            probe=None, extra_headers=None, raw_body=None, body_obj=None):
    """One call, one row. The ONLY place a grid HTTP request is issued."""
    row = base_row(mech, case, phase, repeat, concurrency, block, probe)
    body = body_obj if body_obj is not None else (
        build_call_body(mech, case) if case is not None else None)
    t0 = time.monotonic()
    resp = call_curl(MECH[mech]["endpoint"], body, api_key, mech,
                     extra_headers=extra_headers, raw_body=raw_body)
    wall_ms = round((time.monotonic() - t0) * 1000.0, 1)
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
    row["wall_ms_including_process_spawn"] = wall_ms
    row["request_hash"] = request_hash(body) if body is not None else None
    row["request_fields"] = sorted(body.keys()) if body is not None else None

    if resp["typed_error"] is None and resp["raw_response"]:
        usage = _extract_usage(resp["raw_response"])
        counts = token_counts(usage)
        row["usage"] = usage
        row["usage_flat"] = counts
        row["derived_cost_usd"] = derived_cost_usd(counts, MECH[mech]["model_id"])
        parsed, prediction, perr = parse_call(mech, resp["raw_response"], case)
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
        row["usage"] = None
        row["usage_flat"] = None
        row["derived_cost_usd"] = None
        row["parsed"] = None
        row["prediction"] = None
        row["parsed_label"] = None
        row["parsed_probabilities"] = None
        row["parsed_max_prob"] = None
        row["parsed_score"] = None
    return row


# ---------------------------------------------------------------------------
# modes
# ---------------------------------------------------------------------------
def cmd_subset(args):
    gate, cases = frozen_gate()
    ordered, trace = select_subset(cases)
    by_id = {c["id"]: c for c in cases}
    sel = [by_id[i] for i in ordered]
    summary = verify_subset_constraints(sel)
    corrected, f1_ids = f1_corrected_cases(cases)
    corr_by_id = {c["id"]: c for c in corrected}
    f1_in_subset = [i for i in ordered if i in f1_ids]

    doc = {
        "schema_version": "jevp1-ops-subset-1.0",
        "frozen_at_utc": utc_now_iso(),
        "written_before_any_measurement": True,
        "statement": "The id list, the rule that produced it and the rationale "
                     "are fixed here BEFORE any HTTP call is made. No "
                     "measurement informed any part of this selection.",
        "gate_at_freeze": {
            "digests": gate["digests"],
            "jev_request_gate": gate["jev_request_gate"],
            "general_request_gate": gate["general_request_gate"],
            "f1": gate["f1"],
            "credentials": {k: {"resolvable": v["resolvable"]}
                            for k, v in gate["credentials"].items()},
        },
        "selection_rule": SUBSET_RULE,
        "selection_trace": trace["trace"],
        "contrastive_pair_selected": trace["contrastive_pair"],
        "area_fill_rounds": trace["rounds"],
        "n": len(ordered),
        "case_ids_in_selection_order": ordered,
        "case_ids_canonical_order": sorted(ordered),
        "case_ids_sorted_ascending": ordered,
        "cases": [
            {
                "id": c["id"],
                "area": c["area"],
                "split": c["split"],
                "difficulty": c["difficulty"],
                "question_type": c["questions"][0]["type"],
                "answerable_frozen": c["ground_truth"]["answerable"],
                "gt_answer": c["ground_truth"].get("answer"),
                "control_pair_id": c["control"]["pair_id"],
                "control_variant_kind": c["control"]["variant_kind"],
                "control_base_case_id": c["control"].get("base_case_id"),
                "answerable_after_f1": corr_by_id[c["id"]]["ground_truth"]["answerable"],
                "gt_answer_after_f1": corr_by_id[c["id"]]["ground_truth"].get("answer"),
            }
            for c in sel
        ],
        "coverage": summary,
        "f1_correction_on_this_subset": {
            "pair_id": F1_PAIR_ID,
            "member_ids": f1_ids,
            "members_in_subset": f1_in_subset,
            "effect_on_subset": "none — verified no-op, because the rule "
                                "selected no cp4 member",
            "applied_consistently": "the same derivation and the same hard-stop "
                                    "check as followup-02 / verification.md §2 F1; "
                                    "it happens to change no ground truth in "
                                    "this subset, which is recorded rather than "
                                    "left implicit",
        },
        "design_constants": {
            "warm_reps_per_case": WARM_REPS,
            "warmup_calls_discarded": WARMUP_CALLS,
            "idle_seconds_before_probe": IDLE_SECONDS,
            "idle_calls": IDLE_CALLS,
            "concurrency_block_cases": CONC_CASES,
            "concurrency_block_reps": CONC_REPS,
            "concurrency_levels": list(CONC_LEVELS),
            "attempts_per_call": MAX_ATTEMPTS,
            "retries": RETRIES,
            "sequential_order": "case-major (all reps of case 1, then case 2, "
                                "...) in ascending case id",
            "concurrency_order": "case-major over the first 6 canonical case "
                                 "ids, reps 1..2, dispatched in that order",
        },
        "planned_calls": {
            JEV: WARMUP_CALLS + len(ordered) * WARM_REPS + IDLE_CALLS
                 + len(CONC_LEVELS) * CONC_CASES * CONC_REPS,
            MIMO: WARMUP_CALLS + len(ordered) * WARM_REPS + IDLE_CALLS
                  + len(CONC_LEVELS) * CONC_CASES * CONC_REPS + 1,
            "note": "Jev's interface probe costs 0 calls: distribution "
                    "availability is read from the FROZEN responses, not from "
                    "new ones. MiMo's interface probe costs 1 labelled call.",
        },
        "rationale": [
            "Operational latency is a property of the (case, mechanism) pair, "
            "not of the case's difficulty as a question. A spread of areas and "
            "question types is needed so the latency distribution is not an "
            "artefact of one prompt shape, not so that accuracy is measured.",
            "The unanswerable cases are kept because they are the majority "
            "shape of the corpus (50 of 64 are noul, 14 unanswerable) and "
            "excluding them would bias the token-use and latency distribution "
            "toward longer prompts.",
            "One `score` case is the minimum the interface probe needs: it is "
            "the only question type where Jev returns a full distribution with "
            "a legend, and a single case is enough to establish availability. "
            "A larger score sample would buy accuracy precision, which is not "
            "this run's question.",
            "Both members of one contrastive pair are kept so a stability "
            "comparison can be read pair-wise (same prompt, different deciding "
            "fact) rather than only case-wise.",
            "The area fill is round-robin from each area's MODAL stratum so no "
            "area's latency profile is carried entirely by its rarest case "
            "shape. B has no answerable case, so its default stratum is the "
            "unanswerable one.",
        ],
    }
    with open(SUBSET_PATH, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"subset: {len(ordered)} cases -> {SUBSET_PATH}")
    print(f"  ids: {', '.join(ordered)}")
    print(f"  coverage: {json.dumps(summary['by_area'])} "
          f"qtypes={summary['by_question_type']} "
          f"unanswerable={summary['n_unanswerable']} "
          f"variants={summary['n_control_variants']} "
          f"pairs={summary['complete_contrastive_pairs']}")
    print(f"  planned calls: jev={doc['planned_calls'][JEV]} "
          f"mimo={doc['planned_calls'][MIMO]}")
    return 0


def load_frozen_subset():
    """subset.json, re-derived and re-checked against the frozen inputs."""
    if not os.path.exists(SUBSET_PATH):
        raise SystemExit(
            f"FATAL: {SUBSET_PATH} does not exist. Run "
            "`python3 harness/run_ops.py subset` FIRST: the id list must be "
            "frozen before any measurement.")
    with open(SUBSET_PATH, "r", encoding="utf-8") as f:
        doc = json.load(f)
    gate, cases = frozen_gate()
    ordered, _ = select_subset(cases)
    if doc.get("case_ids_in_selection_order") != ordered:
        raise SystemExit(
            "SUBSET DRIFT: subset.json's id list is not what rule "
            f"{SUBSET_RULE['id']} produces from the current frozen "
            "cases.ndjson. Refusing to measure against a drifted subset.")
    by_id = {c["id"]: c for c in cases}
    sel = [by_id[i] for i in ordered]
    verify_subset_constraints(sel)
    return doc, gate, cases, ordered, sel


def open_appender(mech):
    path = os.path.join(RESULTS, MECH[mech]["raw_path"])
    os.makedirs(RESULTS, exist_ok=True)
    seen = {call_key(r) for r in load_ndjson(path)}
    return Appender(path, seen), path


def cmd_transport(args):
    """Connect-only probe per endpoint. Recorded separately; never folded into
    model-latency statistics."""
    load_frozen_subset()
    key_jev = resolve_credential(LABEL_ENV)
    key_mimo = resolve_credential(LABEL_AUTHJSON)
    probes = []
    for mech, key in ((JEV, key_jev), (MIMO, key_mimo)):
        for i in range(1, TRANSPORT_PROBE_CALLS + 1):
            r = call_curl(MECH[mech]["endpoint"], None, key, mech,
                          connect_only=True)
            probes.append({
                "mechanism": mech,
                "endpoint": MECH[mech]["endpoint"],
                "probe": "connect_only_no_inference",
                "repeat": i,
                "http_status": r["http_status"],
                "bytes": r["bytes"],
                "curl_phases": {
                    "time_namelookup": (r["timings"] or {}).get("time_namelookup"),
                    "time_connect": (r["timings"] or {}).get("time_connect"),
                    "time_appconnect": (r["timings"] or {}).get("time_appconnect"),
                    "time_pretransfer": (r["timings"] or {}).get("time_pretransfer"),
                    "time_total": (r["timings"] or {}).get("time_total"),
                    "num_connects": (r["timings"] or {}).get("num_connects"),
                },
                "typed_error": r["typed_error"],
                "error_detail": r["error_detail"],
                "timestamp_utc": utc_now_iso(),
                "credential_source": MECH[mech]["credential_source"],
            })
    doc = {
        "schema_version": "jevp1-ops-transport-probe-1.0",
        "probed_at_utc": utc_now_iso(),
        "what_this_is": "Connect-only reachability. curl performs the DNS, TCP "
                        "and TLS handshake and then the request is abandoned "
                        "without an HTTP request line and WITHOUT inference, so "
                        "this measures network/transport overhead only.",
        "never_folded_into_model_latency": True,
        "calls": len(probes),
        "probes": probes,
        "interpretation_guard": "A difference here is a property of the network "
                                "path and the CDN edge, NOT of either model, and "
                                "cannot be attributed to Jev or to MiMo.",
    }
    with open(TRANSPORT_PROBE_PATH, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"transport probe: {len(probes)} connect-only calls -> "
          f"{TRANSPORT_PROBE_PATH}")
    for p in probes:
        cp = p["curl_phases"]
        print(f"  {p['mechanism']:>4} r{p['repeat']} "
              f"lookup={cp['time_namelookup']} connect={cp['time_connect']} "
              f"tls={cp['time_appconnect']} total={cp['time_total']} "
              f"err={p['typed_error'] or '-'}")
    return 0


def cmd_warm(args):
    """Warm-up (discarded) then the warm grid, case-major, sequential.

    Order is FIXED and recorded: case-major, i.e. every repetition of case 1 in
    ascending id order, then every repetition of case 2, and so on. Case-major
    (rather than rep-major) is chosen so that a repetition index means the same
    thing for every case, which is what the stability analysis needs.
    """
    doc, gate, cases, ordered, sel = load_frozen_subset()
    mech = args.mechanism
    key = resolve_credential(MECH[mech]["credential_source"])
    if not key:
        raise SystemExit("FATAL: credential did not resolve at call time.")
    app, path = open_appender(mech)
    by_id = {c["id"]: c for c in cases}

    # (phase, repeat, case_id) — the call key is (mech, phase, case, repeat,
    # concurrency, block, probe), so a resumed run re-derives the same keys and
    # the appender silently refuses to double-count.
    plan = []
    if args.reps < 1 or args.reps > WARM_REPS:
        raise SystemExit(
            f"REFUSING --reps {args.reps}: the frozen design is {WARM_REPS} warm "
            "repetitions per case. A lower value is allowed only for an "
            "explicitly reduced and labelled block; a higher value is never "
            "allowed.")
    if args.interval < 0:
        raise SystemExit(f"REFUSING --interval {args.interval}: negative.")
    if args.reps < WARM_REPS or args.interval > 0:
        print(f"warm: REDUCED/PACED block by request: reps={args.reps} (design "
              f"{WARM_REPS}), interval={args.interval}s (design 0.0). Rows are "
              f"labelled block={args.block!r} and are NOT comparable to the "
              "unpaced sequential throughput figure.", flush=True)
    if not args.skip_warmup:
        # Warm-up calls carry the FIRST WARMUP_CALLS canonical cases and are
        # labelled `warmup`. They are excluded from every statistic downstream.
        plan += [("warmup", i, ordered[i - 1]) for i in range(1, WARMUP_CALLS + 1)]
    for cid in ordered:
        plan += [("warm", rep, cid) for rep in range(1, args.reps + 1)]

    n_written, n_err = 0, 0
    for phase, repeat, cid in plan:
        row = run_one(mech, by_id[cid], key, phase, repeat, concurrency=1,
                      block=args.block)
        row["paced_interval_seconds"] = args.interval
        row["reduced_reps"] = (args.reps != WARM_REPS)
        if phase == "warmup":
            row["excluded_from_statistics"] = True
            row["warmup_note"] = ("discarded warm-up call; retained for audit "
                                  "only")
        if app.write(row):
            n_written += 1
            if row["typed_error"]:
                n_err += 1
                print(f"  ! {phase} {cid} rep={repeat} "
                      f"err={row['typed_error']} {row['error_detail'] or ''}")
        if n_written % 25 == 0:
            print(f"  {mech} {phase} {n_written} new calls, errors={n_err}",
                  flush=True)
    print(f"warm: {mech} wrote {n_written} new rows to {path} (errors={n_err})")
    return 0


def cmd_idle(args):
    """After >= IDLE_SECONDS of idleness, the next IDLE_CALLS calls."""
    doc, gate, cases, ordered, sel = load_frozen_subset()
    mech = args.mechanism
    key = resolve_credential(MECH[mech]["credential_source"])
    if not key:
        raise SystemExit("FATAL: credential did not resolve at call time.")
    app, path = open_appender(mech)
    if any(r.get("phase") == "idle" and r.get("block") == args.block
           for r in load_ndjson(path)):
        print(f"idle: {mech} block={args.block} already has idle rows; refusing "
              f"to double the probe.")
        return 0
    print(f"idle: {mech} idling {IDLE_SECONDS}s before the probe "
          f"(no calls in this window by design).", flush=True)
    time.sleep(IDLE_SECONDS)
    n = 0
    for i in range(1, IDLE_CALLS + 1):
        case = {c["id"]: c for c in cases}[ordered[i - 1]]
        row = run_one(mech, case, key, "idle", i, concurrency=1,
                      block=args.block)
        row["idle_seconds_before"] = IDLE_SECONDS
        if app.write(row):
            n += 1
            print(f"  idle {mech} {case['id']} total="
                  f"{row['curl_phases'].get('time_total')} "
                  f"err={row['typed_error'] or '-'}")
    print(f"idle: {mech} wrote {n} rows after {IDLE_SECONDS}s idle")
    return 0


def cmd_concurrency(args):
    """Fixed block of CONC_CASES x CONC_REPS calls at C = 1, 4, 8.

    The in-flight limit is REAL: at most C curl processes exist at any instant,
    and the next job starts only when a slot frees. Dispatching the whole block
    at once would make C=1 indistinguishable from C=12 and would silently
    measure the wrong thing.
    """
    doc, gate, cases, ordered, sel = load_frozen_subset()
    mech = args.mechanism
    key = resolve_credential(MECH[mech]["credential_source"])
    if not key:
        raise SystemExit("FATAL: credential did not resolve at call time.")
    app, path = open_appender(mech)
    by_id = {c["id"]: c for c in cases}
    block_cases = sorted(ordered)[:CONC_CASES]
    cfg = curl_config(key)
    existing = {(r.get("block"), r.get("concurrency"), r.get("case_id"),
                 r.get("repeat"))
                for r in load_ndjson(path) if r.get("phase") == "concurrency"}

    for c in CONC_LEVELS:
        jobs = [(cid, rep) for cid in block_cases
                for rep in range(1, CONC_REPS + 1)]
        todo = [j for j in jobs if (args.block, c, j[0], j[1]) not in existing]
        if not todo:
            print(f"concurrency: {mech} C={c} block={args.block} already fully "
                  f"recorded; skipping.")
            continue
        rows, running, t0 = [], [], time.monotonic()
        queue = list(todo)
        while queue or running:
            while queue and len(running) < c:
                cid, rep = queue.pop(0)
                body = build_call_body(mech, by_id[cid])
                p = subprocess.Popen(curl_argv_for(mech, body),
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True)
                running.append((p, cid, rep, body))
            p, cid, rep, body = running.pop(0)
            out, errout = p.communicate(input=cfg)
            rows.append((cid, rep, body, out, errout, p.returncode))
        makespan = round((time.monotonic() - t0) * 1000.0, 1)
        n_429 = n_err = n_2xx = 0
        for cid, rep, body, out, errout, rc in rows:
            row = parse_parallel_row(mech, by_id[cid], body, out, errout, rc,
                                     c, rep, makespan, args.block)
            if row["http_status"] == 429:
                n_429 += 1
            elif row["http_status"] and 200 <= row["http_status"] < 300:
                n_2xx += 1
            if row["typed_error"]:
                n_err += 1
            app.write(row)
        print(f"concurrency: {mech} C={c} block={args.block} calls={len(rows)} "
              f"makespan_ms={makespan} 2xx={n_2xx} http429={n_429} "
              f"errors={n_err}", flush=True)
    return 0


def curl_config(key):
    return 'header = "Authorization: Bearer %s"\n' % key


def curl_argv_for(mech, body):
    """The exact argv `call_curl` builds, so a parallel block spawns
    byte-identical requests. The credential arrives on stdin.

    `--config -` MUST be present, exactly as in `call_curl`. curl reads a
    config from stdin ONLY when `--config -` names it; without that token the
    piped `curl_config` bytes are silently discarded, the request goes out with
    no `Authorization` header, and the route answers
    `401 {"error":{"type":"AuthError","message":"Missing API key."}}`.
    Every call still fails, `time_total` collapses to TLS+response time
    (~0.2-0.3s), and the level looks FASTER than the sequential baseline -- a
    failure that reads as a speedup. The token was dropped here once already
    (36 rows, HTTP 401, preserved in
    `results/concurrency_defect_401.ndjson`); do not remove it again.
    """
    args = ["curl", "--silent", "--show-error", "--config", "-",
            "--max-time", str(TIMEOUT_SECONDS),
            "--write-out", CURL_WRITE_OUT,
            "--header", "Content-Type: application/json",
            "--header", "User-Agent: %s" % USER_AGENT]
    if mech == JEV:
        args += ["--header", "%s: %s" % (SESSION_HEADER,
                                        MECH[JEV]["session_header_value"])]
    else:
        args += ["--header", "%s: %s" % (SESSION_HEADER, session_id())]
    args += ["--data-binary", serialise(body), MECH[mech]["endpoint"]]
    return args


def parse_parallel_row(mech, case, body, out, errout, rc, concurrency, repeat,
                       makespan, block=None):
    """Reconstruct a row from an already-finished parallel curl process."""
    row = base_row(mech, case, "concurrency", repeat, concurrency, block, "fixed6x2")
    row["probe"] = None
    row["block_makespan_ms"] = makespan
    marker = "\n__OPS__"
    if marker not in (out or ""):
        row["typed_error"] = ERR_TIMEOUT if rc == 28 else ERR_NETWORK
        row["error_detail"] = (f"curl rc={rc} {(errout or '').strip()}")[:200]
        row["http_status"] = None
        row["curl_phases"] = {}
        row["bytes"] = None
        row["raw_response"] = out or ""
        row["usage"] = row["usage_flat"] = row["derived_cost_usd"] = None
        row["parsed"] = row["prediction"] = None
        row["parsed_label"] = row["parsed_probabilities"] = None
        row["parsed_max_prob"] = row["parsed_score"] = None
        return row
    body_txt, _, meta = out.rpartition(marker)
    tm = json.loads(meta)
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
    row["http_status"] = int(tm.get("http_code") or 0) or None
    row["bytes"] = tm.get("size_download")
    row["raw_response"] = body_txt.rstrip("\n")
    row["typed_error"] = classify(row["http_status"])
    row["error_detail"] = (None if row["typed_error"] is None
                           else f"HTTP {row['http_status']}")
    row["request_hash"] = request_hash(body)
    if row["typed_error"] is None:
        usage = _extract_usage(row["raw_response"])
        counts = token_counts(usage)
        row["usage"] = usage
        row["usage_flat"] = counts
        row["derived_cost_usd"] = derived_cost_usd(counts, MECH[mech]["model_id"])
        parsed, prediction, perr = parse_call(mech, row["raw_response"], case)
        row["parsed"] = parsed
        row["prediction"] = prediction
        if perr:
            row["typed_error"] = perr
            row["error_detail"] = "200 OK but unusable answer"
        row["parsed_label"] = (prediction or {}).get("label")
        row["parsed_probabilities"] = (prediction or {}).get("probabilities")
        row["parsed_max_prob"] = (prediction or {}).get("max_prob")
        row["parsed_score"] = (prediction or {}).get("score")
    else:
        row["usage"] = row["usage_flat"] = row["derived_cost_usd"] = None
        row["parsed"] = row["prediction"] = None
        row["parsed_label"] = row["parsed_probabilities"] = None
        row["parsed_max_prob"] = row["parsed_score"] = None
    return row


def cmd_probe(args):
    """INTERFACE PROBE — labelled, outside the grid, one call. Never mixed into
    the warm/concurrency statistics."""
    if args.mechanism != MIMO:
        raise SystemExit(
            "The interface probe is defined for MiMo only: one call with "
            "`logprobs: true` to test whether probability distributions are "
            "available under the frozen conditions. Jev's distribution "
            "availability is read from the FROZEN responses "
            "(`verify` mode), so it costs no call.")
    doc, gate, cases, ordered, sel = load_frozen_subset()
    key = resolve_credential(MECH[MIMO]["credential_source"])
    app, path = open_appender(MIMO)
    if any(r.get("probe") for r in load_ndjson(path)):
        print("probe: MiMo interface probe already recorded; skipping.")
        return 0
    by_id = {c["id"]: c for c in cases}
    # a noul case, so the probe is directly comparable to what Jev answers
    case = next(c for c in sel if c["questions"][0]["type"] == "noul")
    body = build_call_body(MIMO, case)
    body["logprobs"] = True
    row = run_one(MIMO, case, key, "interface_probe", 1, concurrency=1,
                  probe="logprobs", extra_headers=None, body_obj=body)
    row["probe_question_type"] = case["questions"][0]["type"]
    row["probe_parameter_added"] = {"logprobs": True}
    row["probe_note"] = (
        "One labelled call, OUTSIDE the warm/concurrency grid. Its latency and "
        "cost are NOT in any grid statistic. It answers one interface question: "
        "does the Go route return per-token logprobs for this model under the "
        "frozen parameters? The added `logprobs` field is the ONLY difference "
        "from a grid call and is confined to this row.")
    if app.write(row):
        print(f"probe: MiMo logprobs -> HTTP {row['http_status']} "
              f"err={row['typed_error'] or '-'}")
        lp = (row.get("parsed") or {}).get("logprobs")
        print(f"  logprobs present: {lp is not None}")
        if isinstance(lp, dict):
            print(f"  keys: {sorted(lp.keys())[:8]}")
    return 0


def cmd_verify(args):
    """Transport equivalence: curl-carried Jev answers vs the FROZEN urllib-carried
    rows, per case, on label and on distribution."""
    doc, gate, cases, ordered, sel = load_frozen_subset()
    frozen = {r["case_id"]: r for r in load_ndjson(
        os.path.join(PHASE1, "results", "jev_raw.ndjson"))}
    path = os.path.join(RESULTS, MECH[JEV]["raw_path"])
    warm_rows = [r for r in load_ndjson(path) if r.get("phase") == "warm"]
    by_case = {}
    for r in warm_rows:
        by_case.setdefault(r["case_id"], []).append(r)
    out = []
    for cid in sorted(by_case):
        rows = sorted(by_case[cid], key=lambda r: r["repeat"])
        f = frozen.get(cid)
        fpred = (f or {}).get("prediction") or {}
        f_label = fpred.get("label")
        f_probs = fpred.get("probabilities") or {}
        labels = [r.get("parsed_label") for r in rows]
        usable = [r for r in rows if r.get("typed_error") is None]
        agree = sum(1 for l in labels if l == f_label)
        # distribution agreement: max abs difference on the shared support
        diffs = []
        for r in usable:
            p = r.get("parsed_probabilities") or {}
            shared = set(p) & set(f_probs)
            if shared:
                diffs.append(max(abs(float(p[k]) - float(f_probs[k]))
                                  for k in shared))
        out.append({
            "case_id": cid,
            "question_type": rows[0].get("question_type"),
            "frozen_label": f_label,
            "curl_labels": labels,
            "curl_modal_label": max(set(labels), key=labels.count) if labels else None,
            "n_reps": len(rows),
            "n_usable": len(usable),
            "label_agreement_with_frozen": agree,
            "label_agreement_rate": (agree / len(labels)) if labels else None,
            "frozen_probabilities": f_probs,
            "frozen_max_prob": fpred.get("max_prob"),
            "curl_max_prob_min": min((r.get("parsed_max_prob") for r in usable
                                      if r.get("parsed_max_prob") is not None),
                                     default=None),
            "curl_max_prob_max": max((r.get("parsed_max_prob") for r in usable
                                      if r.get("parsed_max_prob") is not None),
                                     default=None),
            "max_abs_prob_diff_vs_frozen": max(diffs) if diffs else None,
        })
    n_cases = len(out)
    n_full = sum(1 for o in out if o["label_agreement_rate"] == 1.0)
    doc2 = {
        "schema_version": "jevp1-ops-transport-verify-1.0",
        "verified_at_utc": utc_now_iso(),
        "what_this_is": "Empirical validation that the curl transport carries Jev "
                        "the same way the frozen urllib transport did. Compares "
                        "the curl-transported label and probability distribution "
                        "for every subset case against the frozen "
                        "results/jev_raw.ndjson row for the same case.",
        "why_needed": "The frozen Jev transport was python-urllib; this run uses "
                      "curl so both mechanisms share one timing instrument. A "
                      "transport change is only harmless if it does not change "
                      "the answer, and that is checked rather than assumed.",
        "n_cases_checked": n_cases,
        "min_cases_required_by_design": 4,
        "cases_with_full_label_agreement": n_full,
        "n_cases_all_reps_match_frozen": n_full,
        "all_cases_agree": n_full == n_cases,
        "limits": [
            "Checked on the SUBSET's cases, not all 64. A curl/urllib difference "
            "that only manifests on an unselected case would not be seen.",
            "Jev is stochastic near the decision boundary (measured in the "
            "frozen preflight: the ambiguous anchor moved 0.59 -> 0.61), so a "
            "small probability difference is NOT evidence of a transport effect. "
            "A label difference on a saturated case would be.",
            "This validates the TRANSPORT, not the model. It says nothing about "
            "Jev's accuracy.",
        ],
        "per_case": out,
    }
    with open(os.path.join(RESULTS, "transport_verify.json"), "w",
              encoding="utf-8") as f:
        json.dump(doc2, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"verify: {n_cases} cases, {n_full} with every curl rep matching the "
          f"frozen label -> {os.path.join(RESULTS, 'transport_verify.json')}")
    for o in out:
        print(f"  {o['case_id']:>9} {str(o['question_type']):>6} "
              f"frozen={str(o['frozen_label']):>12} "
              f"agree={o['label_agreement_rate']} "
              f"maxdp={o['max_abs_prob_diff_vs_frozen']}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("subset")
    sub.add_parser("transport")
    sub.add_parser("verify")
    for name in ("warm", "idle", "concurrency", "probe"):
        p = sub.add_parser(name)
        p.add_argument("--mechanism", choices=list(MECHANISMS), required=True)
        p.add_argument("--block", default=None,
                       help="label distinguishing a re-run block from an earlier "
                            "one in the same raw file; the first block is left "
                            "null so an earlier run is never rewritten")
        if name == "warm":
            p.add_argument("--skip-warmup", action="store_true")
            p.add_argument("--reps", type=int, default=WARM_REPS,
                           help="warm repetitions per case. The design value is "
                                f"{WARM_REPS}; a LOWER value is permitted only "
                                "for a documented reduced/paced block, which "
                                "must be labelled with --block and reported as "
                                "reduced. A higher value is refused.")
            p.add_argument("--interval", type=float, default=0.0,
                           help="seconds to wait AFTER each call, before the "
                                "next one. 0 (the default) is the frozen "
                                "sequential condition. A positive value paces "
                                "the block; a paced block is NOT comparable "
                                "to the unpaced sequential throughput figure "
                                "and must be labelled with --block and reported "
                                "as paced.")
    args = ap.parse_args()
    return {
        "subset": cmd_subset, "transport": cmd_transport, "verify": cmd_verify,
        "warm": cmd_warm, "idle": cmd_idle, "concurrency": cmd_concurrency,
        "probe": cmd_probe,
    }[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
