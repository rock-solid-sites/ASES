# Reusable Case + Result Schema — Jev Bounded-Judgement Diagnostic

**Crosslink issue:** #565 · **Applies to:** Phase 1 and re-used unchanged by
Phases 2–4.
**Derivation:** this schema was derived from the Phase 1 preflight probes
(`results/preflight_evidence.json`) plus the interface facts in `README.md`.
Where preflight contradicts the README, the **measured** behaviour wins and the
discrepancy is called out below.

Everything here is JSON-serialisable and round-trips through NDJSON with no
loss. `harness/validate_cases.py` enforces the `MUST` constraints
structurally; `harness/score.py` consumes the result records.

---

## 1. Interface corrections established by preflight

`README.md` describes the request as
`{model, state, questions: {qid: {type: noul|choice|score, instructions, criteria}}}`.
Measured, the `criteria` container is **type-dependent**, and the flat form is
valid only for two of the three types:

| `type` | `criteria` container | Evidence | HTTP 200 shape |
|---|---|---|---|
| `noul` | **omit entirely** | P2a–P2e | `{"type":"noul","noul":0.99}` |
| `choice` | **object/dict** `option_key -> option_label` | P3a 200 vs P3b 422 `dict_type` | `{"type":"choice","choice":k,"confidence":c,"probabilities":{k:p}}` |
| `score`  | **array/list** of ordered labels | P3c 200 vs P3d 422 `list_type` | `{"type":"score","score":f,"confidence":c,"legend":{"0":l0,...},"probabilities":{"0":p0,...}}` |

Two further measured transport facts that any reimplementation MUST honour:

- **User-Agent is mandatory.** urllib's default `Python-urllib/3.10` is blocked
  by Cloudflare with `HTTP 403 / "error code: 1010"` (P5). Set an explicit
  `User-Agent`.
- **The Go chat endpoint is unavailable** with this credential
  (`HTTP 403 server_error`, "An active OpenCode Go subscription is required…",
  P4a). The same model ID is reachable on `/zen/v1/chat/completions` (P4b).
  This is a documented, disclosed route change — not a model substitution.

`state` accepts a string or an object; Phase 1 uses **string only**
(not tested for the object form). `instructions` accepts string, object, or
array; Phase 1 uses **string only** for every type (not tested otherwise).

---

## 2. Case record (`cases.ndjson`)

One JSON object per line, UTF-8, LF, no BOM, no trailing commas. Ordered by
`id` ascending. Fully synthetic: no real person, no secret, no real credential.

```jsonc
{
  "schema_version": "jevp1-case-1.0",     // MUST
  "id": "a-e01",                          // MUST, unique, stable, sort key
  "area": "A",                            // MUST, enum A|B|C|D
  "split": "train",                       // MUST, enum train|dev|test
  "difficulty": "easy",                   // MUST, enum easy|medium|hard
  "difficulty_note": "...",               // OPTIONAL, what makes it that tier

  "state": "The checkout service deployed ...",  // MUST, the ONLY model-visible text

  "questions": [                          // MUST, non-empty list
    {
      "qid": "q",                         // MUST, unique within the case
      "type": "noul",                     // MUST, enum noul|choice|score
      "instructions": "Did ...?",         // MUST, string
      "criteria": null                    // MUST-key; dict for choice, list for score, null for noul
    }
  ],

  "ground_truth": {                       // MUST
    "answerable": true,                   // MUST boolean
    "answer": "yes",                      // MUST-key; label or null when answerable=false
    "probabilities": {"yes":0.97,"no":0.03}, // OPTIONAL, ideal distribution
    "rationale": "The post-deploy health check returned 200 for all three probes.", // MUST
    "deciding_fact": "health check returned HTTP 200 for all three probes",          // MUST
    "abstain_expected": false,            // MUST boolean; true when low confidence/abstention is the correct behaviour
    "abstain_acceptable": false           // OPTIONAL boolean; true when either answer is defensible but a low-confidence response is still correct
  },

  "control": {                            // MUST
    "pair_id": "a-e01",                   // MUST; family id (own id for a standalone base)
    "variant_kind": "base",                // MUST, enum below
    "base_case_id": null,                  // MUST-key; the base case this perturbs, else null
    "deciding_fact": "health check returned HTTP 200 for all three probes", // MUST
    "label_map": null,                    // MUST-key; opaque_labels only: opaque key -> real role
    "option_order": null,                 // MUST-key; option_reorder only: the presented key order
    "perturbation_seed": null             // MUST-key; noise only: integer seed
  },

  "routing": null,                        // MUST-key; area D only
  "provenance": {                         // MUST
    "template_id": "T-A-EASY-01",
    "generator": "harness/gen_cases.py",
    "generator_version": "1.0.0",
    "synthetic": true,
    "contains_personal_content": false,
    "contains_secrets": false
  }
}
```

### 2.1 `control.variant_kind` enum (MUST, exactly these seven)

| Value | Meaning | Invariant the validator enforces |
|---|---|---|
| `base` | unperturbed case | `base_case_id is null` |
| `option_reorder` | same options, different presentation order | same `label_map`-equivalent key set as `base_case_id`; GT unchanged |
| `opaque_labels` | option keys renamed to content-free tokens | `label_map` present, bijection onto the base's key set; GT unchanged after mapping back |
| `distractor` | large volume of plausible but irrelevant text appended | GT unchanged |
| `missing_evidence` | the deciding fact is removed from `state` | `answerable` MUST be `false`, `answer` MUST be `null`, `abstain_expected` MUST be `true` |
| `noise` | seeded whitespace/case/punctuation perturbation | GT unchanged |
| `irrelevant_change` | a semantically irrelevant content change in a contrastive family | GT **identical** to the referenced base's GT |

### 2.2 `routing` block (area D only; `null` elsewhere)

Legality is **deterministic** and computed from the machine-readable `signals`
block by `harness/routing_policy.py::compute_legality` **before** the case is
shown to any model. `harness/run_jev.py` and `harness/run_baselines.py` build
model requests from `state` + `questions` **only** — they never read `signals`,
`legal_roles`, or `expected_role`. `harness/score.py` **recomputes** legality
from `signals` and asserts it equals the stored block, so the stored value is
checked rather than trusted.

```jsonc
"routing": {
  "policy_rule_id": "foreman-routing-1.0",
  "signals": {                            // deterministic inputs, machine-readable
    "work_not_started": true,
    "specification_complete": true,
    "completed_work_present": false,
    "independent_check_needed": false,
    "unexplained_failure_present": false,
    "known_root_cause": false,
    "governing_assumption_invalid": false,
    "authority_boundary_exceeded": false,
    "owner_decision_required": false
  },
  "legal_roles": ["build", "escalate"],   // sorted
  "illegal_roles": ["review", "investigate", "repair", "redesign"],  // sorted
  "expected_role": "build"                // single best legal role, or null if none
}
```

Policy (deterministic, `foreman-routing-1.0`): a role is **legal** only if its
own precondition signal is set. `repair` requires `known_root_cause`;
`investigate` requires `unexplained_failure_present` AND NOT `known_root_cause`;
`redesign` requires `governing_assumption_invalid`; `escalate` requires
`authority_boundary_exceeded` OR `owner_decision_required`; `review` requires
`completed_work_present` AND `independent_check_needed`; `build` requires
`work_not_started` AND `specification_complete`. This makes the illegal
candidates *structurally* impossible, which is what makes the routing area
adversarial rather than merely descriptive.

### 2.3 Split discipline

`train` is the only split used to fit the measured prior/majority mechanism.
`dev` is used for threshold selection sanity; `test` is reported separately.
**Every contrastive family lives entirely inside one split** — both members of a
pair and every control that references one of them. The validator fails if a
`pair_id` spans splits.

---

## 3. Result record (`results/*.ndjson`)

One JSON object per line. A record is written for **every** (case, mechanism)
pair *even on failure*; a failure is a `typed_error` on a record, never a missing
line. Raw rows are never reduced to pass/fail.

```jsonc
{
  "schema_version": "jevp1-result-1.0",   // MUST
  "case_id": "a-e01",                    // MUST
  "mechanism": "jev",                    // MUST, enum below
  "request_hash": "sha256:<64 hex>",     // MUST; hash of the canonical JSON body actually sent
  "request_body": {"model":"jev-1.13-free","state":"...","questions":{"q":{...}}}, // MUST, exact body sent
  "endpoint": "https://opencode.ai/zen/v1/systemone", // MUST
  "model_id": "jev-1.13-free",           // MUST, exact model id as used
  "http_status": 200,                    // MUST; null for offline mechanisms
  "raw_response": "{\"model\":\"jev-1.13-free\",...}", // MUST, VERBATIM body, never paraphrased
  "parsed": {                            // MUST; null when parse failed
    "type": "noul", "noul": 0.99,
    "choice": null, "score": null, "confidence": null,
    "legend": null,
    "probabilities": {"yes": 0.99, "no": 0.01}
  },
  "prediction": {                        // MUST
    "label": "yes",                      // MUST; chosen label
    "probabilities": {"yes": 0.99, "no": 0.01}, // MUST-key; normalised over the case's label set
    "score": null,                       // MUST-key; raw numeric score for `score` type
    "max_prob": 0.99,                    // MUST
    "confidence_reported": 0.99,         // MUST; the API's own confidence, null if absent
    "confidence_formula": null           // MUST-key; (n*max(p)-1)/(n-1) recomputed locally
  },
  "abstained": false,                    // MUST
  "latency_ms": 701.7,                   // MUST; recorded, NEVER a scoring input
  "usage": {"input_tokens": 289, "output_tokens": 20}, // MUST; nulls for offline mechanisms
  "typed_error": null,                   // MUST; null | see enum
  "error_detail": null,                  // MUST; non-secret detail string
  "attempt": 1,                          // MUST, 1-based
  "retries": 0,                          // MUST
  "timestamp_utc": "2026-09-26T02:41:07Z",// MUST
  "harness_version": "1.0.0",            // MUST
  "secrets_recorded": false              // MUST, always false
}
```

### 3.1 `mechanism` enum (MUST)

Ordered by cost. This order defines "cheapest preceding mechanism" for the
incremental-gain metric and is therefore normative, not descriptive.

| # | `mechanism` | Kind | Endpoint | Cost |
|---|---|---|---|---|
| 0 | `prior` | offline, measured from **train** split majority | none | free, ~0 |
| 1 | `rule` | offline, deterministic signal→label rules | none | free, ~0 |
| 2 | `lexical` | offline, token-overlap / keyword scoring | none | free, ~0 |
| 3 | `jev` | TypeSafe AI System One | `/zen/v1/systemone` | Free/Unlimited tier |
| 4 | `general_model` | cheap chat model, fixed template | `/zen/v1/chat/completions` | Space Bunny Free (0/0) |

`mechanism` values are stable across Phases 2–4 so results concatenate.

### 3.2 `typed_error` enum (MUST)

`null` on success. On failure, one of:

| Code | Meaning |
|---|---|
| `http_4xx` | non-retryable client status (400/401/403/404/422 …); body preserved in `raw_response` |
| `http_5xx` | retryable server status; retried with backoff, final attempt recorded |
| `http_429` | rate limited; retried with backoff, `retry_after` honoured if present |
| `network_timeout` | socket/URL timeout after all retries |
| `network_error` | DNS, TLS, connection reset, or other transport failure |
| `parse_error` | HTTP 200 but the body did not match the expected question type |
| `empty_content` | HTTP 200 but the general model returned no usable text |
| `not_attempted` | mechanism not run at all (recorded so the grid stays complete) |
| `internal_error` | harness bug; always a bug to fix, never a silent skip |

Every code is a `str`; `error_detail` carries a non-secret message.

### 3.3 Parsing and normalisation contract

- `noul`: the API returns only `noul` = P(yes). The harness expands it to
  `{"yes": noul, "no": 1 - noul}`. This is the P2-verified semantics
  (`noul` = P(yes)): pass-anchor 0.99, fail-anchor 0.01.
- `choice`: `probabilities` is a dict over the presented keys. The harness maps
  keys back through `control.label_map` when present, so predictions are always
  in real role names.
- `score`: `probabilities` is a dict keyed by stringified index; `legend` maps
  index → label. The harness maps to labels and records the raw `score` float.
- `confidence` is recorded as reported **and** independently recomputed as
  `(n*max(p) - 1) / (n - 1)` (clamped to [0,1], `null` for n=1). The reported
  field is *not* `max(p)` — measured 0.13 vs `max(p)` 0.27 (P3a) — so threshold
  sweeps use the reported field and the recomputed field is reported alongside.
- Normalisation: if a probability vector does not sum to 1, it is stored raw
  and `prediction.normalised` records whether a rescale was applied. No silent
  rescaling.

### 3.4 What is and is not a scoring input

Scoring inputs: `prediction.label`, `prediction.probabilities`,
`prediction.confidence_reported`, `ground_truth`, `routing.signals`, `split`,
`area`, `control`. These are all fixed by the case file and the response body.

Explicitly **not** scoring inputs: `latency_ms`, `timestamp_utc`, `attempt`,
`retries`, `usage`, `http_status`. These are recorded for cost and reliability
analysis only. No threshold, ordering, or verdict may depend on them. This keeps
`score.py` byte-reproducible across re-runs of the same raw files.

---

## 4. Manifest (`results/manifest.json`)

`MUST` contain: exact model IDs, exact endpoint URLs, git branch and commit,
UTC start/end timestamps, `sha256` of `cases.ndjson` and of every result file,
environment notes (Python version, stdlib-only confirmation), and retry/error
counts per mechanism. `MUST NOT` contain any credential or its length-bearing
substring.

---

## 5. Deliberate Phase 1 limitations (declared up front)

- **One question per case.** The multi-question request shape and the README's
  "latency flat in question count" claim are therefore **not tested** in Phase 1.
  The schema supports it (`questions` is a list).
- **`state` as an object** and **`instructions` as object/array** are **not
  tested**; the schema carries only the string forms the runner exercised.
- **`prior` is global, not per-area.** A per-area or per-difficulty prior would
  be a stronger baseline and is not computed here.
- **Statistical power.** At n=62 the cheapest-test-first bar applies: no
  significance test is claimed, and no result is extrapolated beyond the sample.
