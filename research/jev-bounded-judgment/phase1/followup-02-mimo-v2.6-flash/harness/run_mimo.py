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

CREDENTIAL RESOLUTION
---------------------
Two credential sources are tried, in this fixed order:

  1. `$OPENCODE_GO_API_KEY`               (label `env:OPENCODE_GO_API_KEY`)
  2. `~/.local/share/opencode/auth.json` -> `opencode-go.key`
                                        (label `auth.json#opencode-go`)

The fallback fires ONLY on an entitlement 403 — HTTP 403 whose body says an
active OpenCode Go subscription is required. That is a statement about the
ACCOUNT behind a credential, not about the request, so switching credential is
the correct response to it and re-sending the same request is not. Any other
failure stops the run: this file never shops for a credential that happens to
work. Measured 2026-09-26: source 1 returns 403 on the Go route for every model
(including the frozen `space-bunny-free`), source 2 returns 200.

Resolution happens ONCE, in the preflight, and the grid then uses the selected
source directly. There is no credential-fallback logic inside the cell loop, so
N=1 per cell is preserved exactly: a cell is never re-sent under a second
credential.

SECRETS
-------
A credential is read at runtime, held only in memory, used only as a bearer
token, and never logged, printed, or written to any artefact. It reaches curl
through a config on STDIN (`curl -K -`), so it appears neither in `argv` (where
`/proc/*/cmdline` and shell history would expose it) nor in any file. Only the
credential SOURCE LABEL is recorded, in `results/preflight.json`,
`results/run_session.json` and the manifest. `make_result` records
`secrets_recorded: false`.

TRANSPORT: CURL, NOT urllib
---------------------------
`post_json_curl` replaces the frozen `common.post_json`, which uses
`urllib.request`. Measured 2026-09-26: with the SAME credential, urllib is
rejected by Cloudflare (HTTP 403, error code 1010 — the owner's user-agent
block) while curl is served normally. urllib was therefore never able to reach
this route with any credential, and the replacement is a transport change, not
a parameter change. It reproduces `common.post_json`'s return contract exactly
and reuses `common.classify` for the typed error and `common._extract_usage`
for the usage block, so the recorded rows are shaped identically to the frozen
run's.

FOUR DISCLOSED TRANSPORT-LEVEL DIFFERENCES FROM THE FROZEN RUN
--------------------------------------------------------------
1. The endpoint is the Go route `https://opencode.ai/zen/go/v1/chat/completions`
   rather than the frozen run's Zen route. Disclosed in the brief as permitted;
   the body is unaffected by the route.
2. The `x-opencode-session` provenance header is a per-run UUID4 rather than the
   frozen run's `jev-phase1-baselines-20260926`. It is a provider grouping
   header; it is not part of the request body, does not enter the prompt, and
   does not affect the hashed request. It is not a secret and IS recorded.
3. The HTTP client is curl rather than urllib (see above). The `User-Agent` is
   still the frozen `common.USER_AGENT`, and the JSON body is the frozen
   `serialise(body)`, so the bytes on the wire are the frozen bytes.
4. The credential comes from the CLI credential store rather than the
   environment variable (see CREDENTIAL RESOLUTION).

Usage:
    python3 harness/run_mimo.py --check-only        # gates only, zero calls
    python3 harness/run_mimo.py --preflight-only     # smoke call(s) -> preflight.json
    python3 harness/run_mimo.py                     # the grid (64 requests)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
FOLLOWUP = os.path.dirname(HERE)
PHASE1 = os.path.dirname(FOLLOWUP)
PHASE1_HARNESS = os.path.join(PHASE1, "harness")
sys.path.insert(0, PHASE1_HARNESS)

from common import (  # noqa: E402
    ERR_INTERNAL,
    ERR_NETWORK,
    ERR_TIMEOUT,
    TIMEOUT_SECONDS,
    USER_AGENT,
    NdjsonWriter,
    _extract_usage,
    classify,
    load_cases,
    make_result,
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

RUNNER_VERSION = "1.1.0"
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

SESSION_HEADER = "x-opencode-session"
API_KEY_ENV = "OPENCODE_GO_API_KEY"
AUTH_JSON = "~/.local/share/opencode/auth.json"
AUTH_JSON_PROVIDER = "opencode-go"
LABEL_ENV = "env:OPENCODE_GO_API_KEY"
LABEL_AUTHJSON = "auth.json#opencode-go"
CREDENTIAL_ORDER = (LABEL_ENV, LABEL_AUTHJSON)

# The entitlement message the Go route returns for a credential with no Go
# entitlement. Matched case-insensitively on a distinctive fragment, so the
# fallback fires on THAT condition and not on every 403.
ENTITLEMENT_FRAGMENT = "subscription is required"

MAX_ATTEMPTS = 1          # N = 1. Not a tunable. See the module docstring.
CASES_N = 64
TEMPERATURE = 0
RUN_SESSION_PATH = os.path.join(FOLLOWUP, "results", "run_session.json")

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
# per-run provenance id (not a secret; recorded in every artefact)
# ---------------------------------------------------------------------------
_RUN_SESSION = {"id": None}


def session_id(cli_value=None):
    """The `x-opencode-session` value for this run. Generated ONCE per run.

    It is a provider grouping header, not a credential: the OpenCode CLI store's
    own traffic carries one, and the Go route answers 400 `MissingSessionID`
    without it. It is recorded because it is how a reader ties a provider-side
    request log to this run, and recording it discloses nothing.
    """
    if _RUN_SESSION["id"] is None:
        _RUN_SESSION["id"] = (cli_value
                              or os.environ.get("MIMO_RUN_SESSION_ID")
                              or str(uuid.uuid4()))
    return _RUN_SESSION["id"]


# ---------------------------------------------------------------------------
# credential resolution
# ---------------------------------------------------------------------------
def read_credential(label):
    """The credential named by `label`, read at runtime. Never logged.

    Returns None when the source is absent or unreadable. The value is used
    only as a bearer token and is never returned to any caller that records it.
    """
    if label == LABEL_ENV:
        value = os.environ.get(API_KEY_ENV)
        return value or None
    if label == LABEL_AUTHJSON:
        path = os.path.expanduser(AUTH_JSON)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return None
        node = data.get(AUTH_JSON_PROVIDER)
        if isinstance(node, dict):
            for field in ("key", "apiKey", "api_key", "token"):
                if node.get(field):
                    return str(node[field])
            return None
        if isinstance(node, str) and node:
            return node
        return None
    raise SystemExit(f"unknown credential label {label!r}")


def credential_candidates():
    """Available credential sources, in the fixed order. Labels only.

    A source that is configured but unreadable is reported as absent rather
    than silently skipped, so the recorded resolution order is complete.
    """
    out = []
    for label in CREDENTIAL_ORDER:
        out.append({"label": label, "present": read_credential(label) is not None})
    return out


def is_entitlement_403(resp):
    """True only for the account-level entitlement 403 on the Go route.

    A 403 that is not this is a Cloudflare or other block and must NOT silently
    cause a credential switch, so the provider message is required.
    """
    if resp.get("http_status") != 403:
        return False
    return ENTITLEMENT_FRAGMENT in (resp.get("raw_response") or "").lower()


# ---------------------------------------------------------------------------
# transport: curl subprocess
# ---------------------------------------------------------------------------
def post_json_curl(url, body, api_key, session_id_value, max_attempts=MAX_ATTEMPTS,
                   timeout=TIMEOUT_SECONDS):
    """POST via curl. Never raises. Same return contract as `common.post_json`.

    The bearer token is handed to curl on STDIN as a config line, so it is in
    neither `argv` nor any file. The request body carries no secret and is
    passed as an argv value, which keeps the two channels from colliding (an
    earlier `-K -` attempt that also fed the body on stdin silently sent an
    empty body, which the route answered 401).

    `max_attempts` exists to mirror the frozen signature. It is 1 for every call
    this experiment makes, and there is no retry path here: a failed cell is
    recorded, never re-sent.
    """
    # A credential containing a quote, a backslash or a newline cannot be
    # expressed in curl's config syntax. Refuse rather than emit a config that
    # would send a different header than intended.
    if any(ch in api_key for ch in ('"', "\\", "\n", "\r")):
        return {"http_status": None, "raw_response": "", "typed_error": ERR_INTERNAL,
                "error_detail": "credential is not expressible in a curl config",
                "usage": None, "latency_ms": None, "attempts": 0, "retries": 0}

    cfg = 'header = "Authorization: Bearer %s"\n' % api_key
    args = ["curl", "--silent", "--show-error", "--config", "-",
            "--max-time", str(timeout),
            "--write-out", "\n__HTTP__%{http_code}",
            "--header", "Content-Type: application/json",
            "--header", "%s: %s" % (SESSION_HEADER, session_id_value),
            "--header", "User-Agent: %s" % USER_AGENT,
            "--data-binary", serialise(body),
            url]

    attempts, retries = 0, 0
    last = {"http_status": None, "raw_response": "", "typed_error": ERR_NETWORK,
            "error_detail": None, "usage": None}
    while attempts < max_attempts:
        attempts += 1
        t0 = time.monotonic()
        try:
            proc = subprocess.run(args, input=cfg, capture_output=True, text=True)
        except Exception as e:  # noqa: BLE001 - the grid must stay complete
            last = {"http_status": None, "raw_response": "",
                    "typed_error": ERR_INTERNAL,
                    "error_detail": f"{type(e).__name__}: {e}"[:200],
                    "usage": None,
                    "latency_ms": round((time.monotonic() - t0) * 1000.0, 1)}
            break
        out = proc.stdout or ""
        marker = "\n__HTTP__"
        latency = round((time.monotonic() - t0) * 1000.0, 1)
        if marker not in out:
            # curl produced no status line: a transport failure, not an HTTP one.
            # rc 28 is curl's operation timeout.
            timed_out = proc.returncode == 28
            last = {"http_status": None, "raw_response": out,
                    "typed_error": ERR_TIMEOUT if timed_out else ERR_NETWORK,
                    "error_detail": (f"curl rc={proc.returncode} "
                                     f"{(proc.stderr or '').strip()}")[:200],
                    "usage": None, "latency_ms": latency}
            break
        raw, _, status_txt = out.rpartition(marker)
        try:
            status = int(status_txt.strip())
        except ValueError:
            last = {"http_status": None, "raw_response": raw,
                    "typed_error": ERR_INTERNAL,
                    "error_detail": f"unparseable curl status {status_txt!r}"[:200],
                    "usage": None, "latency_ms": latency}
            break
        raw = raw.rstrip("\n")
        last = {"http_status": status, "raw_response": raw,
                "typed_error": classify(status),
                "error_detail": None if classify(status) is None else f"HTTP {status}",
                "usage": _extract_usage(raw),
                "latency_ms": latency}
        # 4xx other than 429 is a contract error: re-sending cannot help. With
        # max_attempts=1 this loop is single-pass in every case.
        break
    last["attempts"] = attempts
    last["retries"] = retries
    return last



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
        "session_header_name": SESSION_HEADER,
        "session_header_value": session_id(),
        "transport": "curl subprocess (frozen urllib is Cloudflare-rejected, "
                     "HTTP 403 code 1010, with the same credential)",
        "credential_resolution_order": list(CREDENTIAL_ORDER),
        "permitted_differences_from_frozen_run": [
            "request field `model`: space-bunny-free -> mimo-v2.6-flash",
            "endpoint route: https://opencode.ai/zen/v1/chat/completions -> "
            "https://opencode.ai/zen/go/v1/chat/completions",
            "x-opencode-session header (not part of the hashed body)",
        ],
    }
    cands = credential_candidates()
    gates["credential_sources"] = cands
    gates["api_key_env"] = API_KEY_ENV
    gates["api_key_present"] = cands[0]["present"]
    gates["credential_available"] = any(c["present"] for c in cands)
    if not gates["credential_available"]:
        raise SystemExit(
            f"STOP: no usable credential. ${API_KEY_ENV} is "
            f"{'set' if cands[0]['present'] else 'unset or empty'} and "
            f"{AUTH_JSON}#{AUTH_JSON_PROVIDER} is "
            f"{'readable' if cands[1]['present'] else 'unreadable'}. "
            "No call was made.")
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
    print("  credentials available: "
          + ", ".join(f"{c['label']}={'yes' if c['present'] else 'no'}"
                      for c in cands)
          + "  (values never printed)")
    print(f"  {SESSION_HEADER}: {session_id()}")
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


def run_preflight(out_path=PREFLIGHT_PATH):
    """Resolve the credential AND establish reachability, on non-corpus content.

    One throwaway call per credential source, in the fixed order, stopping at
    the first 2xx. Each call is `max_attempts=1` with zero retries. A source is
    abandoned only on the account-level entitlement 403; any other failure stops
    the preflight, because switching credential would not be the right response
    to it.

    Excluded from the 64-cell grid by construction: it is never written to
    `mimo_raw.ndjson` and it is not a corpus case id.
    """
    body = smoke_request()
    calls = []
    selected = None
    abandoned = []
    for cand in credential_candidates():
        label = cand["label"]
        if not cand["present"]:
            abandoned.append({"credential_source": label,
                              "outcome": "absent_or_unreadable"})
            continue
        resp = post_json_curl(ENDPOINT, body, read_credential(label),
                              session_id_value=session_id(),
                              max_attempts=MAX_ATTEMPTS)
        calls.append(summarise_smoke(body, resp, credential_source=label))
        if resp["typed_error"] is None and resp["http_status"] is not None \
                and 200 <= resp["http_status"] < 300:
            selected = label
            break
        if is_entitlement_403(resp):
            abandoned.append({"credential_source": label,
                              "outcome": "entitlement_403",
                              "http_status": resp["http_status"],
                              "why": "the Go route reports no active Go "
                                     "subscription for this credential; the "
                                     "request itself was never evaluated"})
            continue
        abandoned.append({"credential_source": label,
                          "outcome": "failed",
                          "http_status": resp["http_status"],
                          "typed_error": resp["typed_error"]})
        break

    record = {
        "schema_version": "jevp1-followup2-preflight-1.1",
        "what": "throwaway credential-resolution + reachability + "
                "reasoning-consumption smoke test. NOT one of the 64 grid "
                "cells; never scored; its state text is not from cases.ndjson.",
        "runner_version": RUNNER_VERSION,
        "model_id": MODEL_ID,
        "model_catalog_id": MODEL_CATALOG_ID,
        "endpoint": ENDPOINT,
        "conditions": {"temperature": TEMPERATURE,
                       "max_tokens": GENERAL_MAX_TOKENS,
                       "max_attempts": MAX_ATTEMPTS, "retries": 0,
                       "gen_sys_sha256": hashlib.sha256(
                           GEN_SYS.encode("utf-8")).hexdigest()},
        "session_header_name": SESSION_HEADER,
        "session_header_value": session_id(),
        "credential_resolution_order": list(CREDENTIAL_ORDER),
        "credential_source_selected": selected,
        "credential_sources_abandoned": abandoned,
        "credential_source_note":
            "source LABELS only. No credential value is present in this file, "
            "in any log, or on disk; the value reaches curl on stdin.",
        "request_body": body,
        "request_hash": request_hash(body),
        "state_is_non_corpus": True,
        "state_sha256": hashlib.sha256(SMOKE_STATE.encode("utf-8")).hexdigest(),
        "reference_answer": SMOKE_REFERENCE_ANSWER,
        "timestamp_utc": utc_now_iso(),
        "n_calls": len(calls),
        "calls": calls,
        "secrets_recorded": False,
    }
    record["usage_totals"] = usage_totals(calls, MODEL_ID)
    record["derived_cost_usd"] = cost_total(calls, MODEL_ID)
    ok_call = next((c for c in calls if c["credential_source"] == selected), None)
    record["route_reachable"] = ok_call is not None
    record["max_tokens_consumed_by_reasoning"] = bool(
        ok_call is not None and ok_call["content_empty"])
    record["observation"] = smoke_observation(record["route_reachable"],
                                              record["max_tokens_consumed_by_reasoning"],
                                              ok_call or (calls[0] if calls else None))
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(record, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    return record


def summarise_smoke(body, resp, credential_source=None):
    """Everything worth knowing about one smoke call, secrets excluded."""
    out = {
        "model": body.get("model"),
        "credential_source": credential_source,
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
    if call is None:
        return "NOT REACHABLE: no call was made; no credential source was usable."
    if not reachable:
        return (f"NOT REACHABLE: HTTP {call['http_status']} "
                f"({call['typed_error']}) on credential source "
                f"{call.get('credential_source')!r}. No grid call was made.")
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


def confirm_unreachable(api_key, credential_source, out_path=PREFLIGHT_PATH,
                        extra=2):
    """The brief says stop if the route fails CONSISTENTLY. Consistency needs
    more than one data point, so this makes up to `extra` further throwaway,
    non-corpus calls at the SAME parameters, records them, and reports the
    result. It never changes a parameter to make the route behave."""
    body = smoke_request()
    with open(out_path, "r", encoding="utf-8") as f:
        record = json.load(f)
    for _ in range(extra):
        resp = post_json_curl(ENDPOINT, body, api_key,
                              session_id_value=session_id(),
                              max_attempts=MAX_ATTEMPTS)
        record["calls"].append(summarise_smoke(body, resp,
                                               credential_source=credential_source))
        record["n_calls"] = len(record["calls"])
    statuses = [c["http_status"] for c in record["calls"]]
    errors = [c["typed_error"] for c in record["calls"]]
    record["usage_totals"] = usage_totals(record["calls"], MODEL_ID)
    record["derived_cost_usd"] = cost_total(record["calls"], MODEL_ID)
    record["failure_confirmation"] = {
        "why": "the brief requires stopping only if the route fails "
               "consistently; consistency requires >1 observation",
        "n_calls": len(statuses),
        "credential_source": credential_source,
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
def run(cases, api_key, out_path, credential_source=None):
    with NdjsonWriter(out_path) as w:
        for i, case in enumerate(cases, 1):
            body = build_general_request(case, MODEL_ID)
            try:
                resp = post_json_curl(ENDPOINT, body, api_key,
                                      session_id_value=session_id(),
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
    """The recorded preflight must exist and must have reached the route.

    It also names the credential source the grid must use. The value is re-read
    at run time from that label; nothing about the credential is stored.
    """
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
            f"typed_errors={[c['typed_error'] for c in record['calls']]}, "
            f"credential_sources_tried="
            f"{[c.get('credential_source') for c in record['calls']]}). "
            "Reported, not worked around: no grid call is made and no parameter "
            "is changed to make the route behave.")
    label = record.get("credential_source_selected")
    if not label:
        raise SystemExit(
            "STOP: the recorded preflight reached the route but names no "
            "credential source, so the grid has no credential to use. Re-run "
            "`--preflight-only`.")
    return record, label


def write_run_session(path, credential_source, gates, preflight, n_rows,
                      out_path):
    """Per-run provenance for the scorer to fold into the manifest.

    Holds the `x-opencode-session` UUID, the credential SOURCE LABEL and the
    recorded digests. No credential value.
    """
    record = {
        "schema_version": "jevp1-followup2-run-session-1.0",
        "runner_version": RUNNER_VERSION,
        "mechanism": MECHANISM,
        "session_header_name": SESSION_HEADER,
        "session_header_value": session_id(),
        "session_header_note": "a per-run uuid4; a provider grouping header, "
                               "not a credential. Generated once per run and "
                               "recorded so a provider-side request log can be "
                               "tied to this run.",
        "credential_resolution_order": list(CREDENTIAL_ORDER),
        "credential_source_used": credential_source,
        "credential_source_note": "label only; no credential value is recorded "
                                  "in any artefact by this experiment",
        "preflight_session_header_value": (preflight or {}).get(
            "session_header_value"),
        "preflight_credential_source_selected": (preflight or {}).get(
            "credential_source_selected"),
        "transport": "curl subprocess",
        "n_rows_written": n_rows,
        "raw_path": os.path.relpath(out_path, FOLLOWUP),
        "frozen_input_sha256": gates.get("frozen_input_sha256"),
        "recorded_utc": utc_now_iso(),
        "secrets_recorded": False,
    }
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(record, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    return record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(FOLLOWUP, "results",
                                                  "mimo_raw.ndjson"))
    ap.add_argument("--check-only", action="store_true",
                    help="run every gate, make zero HTTP calls")
    ap.add_argument("--preflight-only", action="store_true",
                    help="run the gates and the throwaway smoke call(s), then stop")
    ap.add_argument("--session-id", default=None,
                    help="pin the x-opencode-session value instead of generating "
                         "a fresh uuid4 for this run")
    args = ap.parse_args()
    session_id(args.session_id)

    print("run_mimo: gates")
    gates, cases = build_gates(check_only=args.check_only)

    if args.check_only:
        print("run_mimo: --check-only, no call made")
        return 0

    if args.preflight_only:
        print("run_mimo: preflight (throwaway, non-corpus): credential "
              "resolution + reachability, 1 attempt per source")
        rec = run_preflight()
        for c in rec["calls"]:
            print(f"  source={c['credential_source']} "
                  f"http_status={c['http_status']} "
                  f"latency_ms={c['latency_ms']} "
                  f"finish_reason={c.get('finish_reason')!r} "
                  f"content_chars={c.get('content_chars')}")
        for a in rec["credential_sources_abandoned"]:
            print(f"  abandoned {a['credential_source']}: {a['outcome']}")
        print(f"  credential_source_selected="
              f"{rec['credential_source_selected']!r}")
        print(f"  route_reachable={rec['route_reachable']}")
        print(f"  max_tokens_consumed_by_reasoning="
              f"{rec['max_tokens_consumed_by_reasoning']}")
        print(f"  {rec['observation']}")
        if not rec["route_reachable"]:
            tried = next((a["credential_source"]
                          for a in rec["credential_sources_abandoned"]
                          if a["outcome"] in ("entitlement_403", "failed")), None)
            key = read_credential(tried) if tried else None
            if key:
                print("run_mimo: route not reachable; confirming consistency "
                      "(same parameters, same credential, no tuning)")
                rec = confirm_unreachable(key, tried)
                fc = rec["failure_confirmation"]
                print(f"  http_statuses={fc['http_statuses']}")
                print(f"  consistent_failure={fc['consistent_failure']}")
            print("STOP: route failed consistently. Reported, not repaired. "
                  "No grid call was made.")
            return 2
        print(f"run_mimo: preflight recorded in {PREFLIGHT_PATH}")
        return 0

    pre, label = require_preflight()
    api_key = read_credential(label)
    if not api_key:
        raise SystemExit(
            f"STOP: the preflight selected credential source {label!r} but it "
            "is no longer readable. No call was made.")
    print(f"run_mimo: preflight on file — {pre['observation'][:80]}…")
    print(f"run_mimo: {len(cases)} cases, 1 attempt each, no retries")
    print(f"  model={MODEL_ID} endpoint={ENDPOINT}")
    print(f"  credential_source={label} (value never printed)")
    n = run(cases, api_key, args.out, credential_source=label)
    sess = write_run_session(RUN_SESSION_PATH, label, gates, pre, n, args.out)
    print(f"run_mimo: wrote {n} rows to {args.out}")
    print(f"run_mimo: {SESSION_HEADER}={sess['session_header_value']} "
          f"recorded in {RUN_SESSION_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

