---
title: Test B Protocol — Authoritative Runtime Validation
program: EDASES
layer: Research
document_type: Protocol
status: Draft
authority: Derived
canonical_repository: edases
depends_on:
  - .design/capability-schema-validation.md
  - research/capability-schema-validation/capabilities/authoritative/schemas.json
  - research/capability-schema-validation/capabilities/derived/variant-c.json
  - research/capability-schema-validation/harness/runtime.py
  - research/capability-schema-validation/harness/sandbox.py
  - research/capability-schema-validation/harness/error-codes.md
consumed_by:
  - research/capability-schema-validation/tests/test-b/results.md
  - research/capability-schema-validation/report.md
---

# Test B — Authoritative Runtime Validation: Protocol

**Questions addressed:** 2, 4, 5 (design §1.4, §5.3).

Target architecture (non-negotiable framing):

```
model (sees variant C only) → sandbox → runtime validation (authoritative schema) → policy → execution
```

The model sees **only variant C** (`derived/variant-c.json`: stable ID + one-line ≤20 words + param names/types + required flag + enum literals). The complete authoritative schema (`authoritative/schemas.json`, Draft-07, `version: 0.1.0` on every op) lives **exclusively** in the runtime — not in model context, prompts, or system messages. Every call is routed through `sandbox → runtime validation → policy → execution` (`harness/runtime.py` + `harness/sandbox.py`).

## Valid-call set (covers all 14 ops)

These are submitted first to prove the harness executes valid calls under variant C. Each must pass validation and reach execution (`executed == true`, `validation:pass`, `policy:pass`, `execution:ok`).

| # | op_id | arguments |
|---|---|---|
| V1 | `search_artefacts` | `{"query":"hello","limit":5}` |
| V2 | `get_artefact` | `{"id":"art_abc-123"}` |
| V3 | `create_artefact` | `{"type":"spec","title":"Test artefact"}` |
| V4 | `update_artefact_status` | `{"id":"art_abc-123","status":"active","reason":"reviewed"}` |
| V5 | `create_review` | `{"artefact_id":"art_abc-123","verdict":"approve","rationale":"This is a good rationale with enough length for validation"}` |
| V6 | `set_severity` | `{"artefact_id":"art_abc-123","level":"high"}` |
| V7 | `set_artefact_state` | `{"artefact_id":"art_abc-123","state":"active","comment":"ok"}` |
| V8 | `query_metrics` | `{"filter":{"type":"spec"},"group_by":"status","include_facets":true}` |
| V9 | `list_reviews` | `{"artefact_id":"art_abc-123","verdict":"approve","limit":10}` |
| V10 | `get_capability_schema` | `{"op_id":"search_artefacts"}` |
| V11 | `submit_evidence` | `{"artefact_id":"art_abc-123","evidence_items":[{"source":"paper","content":"evidence text"}]}` |
| V12 | `link_artefacts` | `{"source_id":"art_abc-123","target_ids":["art_def-456"],"relation":"relates_to"}` |
| V13 | `archive_artefact` | `{"artefact_id":"art_abc-123","reason":"superseded by new design for clarity"}` |
| V14 | `validate_payload` | `{"op_id":"search_artefacts","payload":{"query":"hi"},"strict":true}` |

## Malformed-call matrix (6 classes, ≥2 cases per class)

Each case is expected to be **rejected before execution** (`executed == false`, `trace` ends at `validation:rejected:ValidationFailed` or `sandbox:rejected:UnknownOperation`). No side effects, no partial writes.

| Class | # | op_id | arguments | Expected `code` | Expected `constraint` / signal |
|---|---|---|---|---|---|
| Missing required | M1 | `search_artefacts` | `{}` | `ValidationFailed` | `required` (query) |
| Missing required | M2 | `create_review` | `{"artefact_id":"art_abc-123","verdict":"approve"}` (no rationale) | `ValidationFailed` | `required` (rationale) |
| Missing required | M3 | `submit_evidence` | `{"artefact_id":"art_abc-123"}` (no evidence_items) | `ValidationFailed` | `required` |
| Wrong type | T1 | `search_artefacts` | `{"query":123}` | `ValidationFailed` | `type` |
| Wrong type | T2 | `search_artefacts` | `{"query":"hi","limit":"ten"}` | `ValidationFailed` | `type` |
| Wrong type | T3 | `query_metrics` | `{"filter":"spec"}` (string not object) | `ValidationFailed` | `type` |
| Enum violation | E1 | `create_artefact` | `{"type":"invalid","title":"t"}` | `ValidationFailed` | `enum` |
| Enum violation | E2 | `set_severity` | `{"artefact_id":"art_abc-123","level":"urgent"}` | `ValidationFailed` | `enum` |
| Enum violation | E3 | `update_artefact_status` | `{"id":"art_abc-123","status":"deleted"}` | `ValidationFailed` | `enum` |
| Extra unknown param | X1 | `get_artefact` | `{"id":"art_abc-123","extra":"x"}` | `ValidationFailed` | `additionalProperties` |
| Extra unknown param | X2 | `create_review` | `{"artefact_id":"art_abc-123","verdict":"approve","rationale":"Rationale with enough length","unknown_field":"oops"}` | `ValidationFailed` | `additionalProperties` |
| Constraint violation | C1 | `search_artefacts` | `{"query":"hi","limit":999}` (max 100) | `ValidationFailed` | `maximum` |
| Constraint violation | C2 | `get_artefact` | `{"id":"BAD_ID"}` (pattern `^art_[a-z0-9-]+$`) | `ValidationFailed` | `pattern` |
| Constraint violation | C3 | `create_artefact` | `{"type":"spec","title":"` + 201-char string `"}` (maxLength 200) | `ValidationFailed` | `maxLength` |
| Constraint violation | C4 | `create_review` | `{"artefact_id":"art_abc-123","verdict":"approve","rationale":"short"}` (minLength 10) | `ValidationFailed` | `minLength` |
| Constraint violation | C5 | `archive_artefact` | `{"artefact_id":"art_abc-123","reason":"hi"}` (minLength 5) | `ValidationFailed` | `minLength` |
| Nested / array error | N1 | `submit_evidence` | `{"artefact_id":"art_abc-123","evidence_items":[{"source":"","content":"text"}]}` (minLength 1 on source) | `ValidationFailed` | `minLength` |
| Nested / array error | N2 | `create_review` | `{"artefact_id":"art_abc-123","verdict":"approve","rationale":"Rationale with enough length","citations":["BAD_ID"]}` (pattern on citations) | `ValidationFailed` | `pattern` |
| Nested / array error | N3 | `link_artefacts` | `{"source_id":"art_abc-123","target_ids":[],"relation":"relates_to"}` (minItems 1) | `ValidationFailed` | `minItems` |
| Nested / array error | N4 | `submit_evidence` | `{"artefact_id":"art_abc-123","evidence_items":[{"source":"paper","content":"text","weight":5}]}` (maximum 1 on weight) | `ValidationFailed` | `maximum` |

Total malformed cases: 20 (exceeds minimum). Additional policy/unknown-op cases are tested in Test D, not here.

## Typed-error identity check

For every malformed case, the error returned to the caller must carry the **structured typed error** per `harness/error-codes.md` and `harness/runtime.py`:

```
{code, field?, constraint?, got?, message?, schema_version?, op_id?, boundary?}
```

Checks:

* `code == "ValidationFailed"` and `boundary == "runtime"` for all 20 cases above.
* `field` names the failing property (or `field == null` only where the validator reports no path — then `message` must still identify the failing property).
* `constraint` names the failing keyword (`required`, `type`, `enum`, `additionalProperties`, `maximum`, `pattern`, `maxLength`, `minLength`, `minItems`, etc.).
* No case returns a free-text string without `code`/`constraint`. Code → string flattening is a **failure** of the error-identity claim.
* The error is observed end-to-end (runtime → harness result → log) without loss. Log records `error.code`, `error.field`, `error.constraint`, `error.boundary`, `error.schema_version`.

## Recovery verification

After each typed rejection, the harness tests whether a **single corrected retry** succeeds without introducing a new error (simulates model recovery given the typed error). The corrected arguments are:

| Malformed | Corrected arguments | Why |
|---|---|---|
| M1 `{}` | `{"query":"hello"}` | add missing required |
| M2 (no rationale) | add `"rationale":"Corrected rationale with enough length"` | add missing required |
| M3 (no evidence_items) | add `"evidence_items":[{"source":"paper","content":"ok text"}]` | add missing required |
| T1 `query: 123` | `query: "hello"` | correct type |
| T2 `limit: "ten"` | `limit: 5` | correct type |
| T3 `filter: "spec"` | `filter: {"type":"spec"}` | correct type |
| E1 `type: invalid` | `type: "spec"` | valid enum |
| E2 `level: urgent` | `level: "high"` | valid enum |
| E3 `status: deleted` | `status: "active"` | valid enum |
| X1 extra field | remove `extra` | no unknown property |
| X2 unknown_field | remove `unknown_field` | no unknown property |
| C1 `limit: 999` | `limit: 20` | within max |
| C2 `BAD_ID` | `art_abc-123` | matches pattern |
| C3 title 201 chars | title 10 chars | within maxLength |
| C4 rationale short | rationale 30 chars | within minLength |
| C5 reason `hi` | `reason: "superseded by new design for clarity"` | within minLength |
| N1 empty source | `source: "paper"` | minLength |
| N2 BAD_ID citation | `citations: ["art_def-456"]` | pattern |
| N3 empty target_ids | `target_ids: ["art_def-456"]` | minItems |
| N4 weight 5 | `weight: 0.8` | within max |

Measure:

* Per-error-class recovery rate: `successful_corrected_retry / total_cases_in_class` (must succeed on first retry with no new validation error).
* Aggregate recovery rate: `total_successful_retries / total_malformed_cases`.
* Pre-registered threshold: **≥60% of typed rejections are correctly recovered within 1 retry** (design §5.3) is the gate for "acceptable recovery". Report the observed rate; do not infer acceptability post hoc.

## Explicit exposure check

Record **whether any validation information had to be exposed to the model** to achieve recovery — i.e., did the error payload need to include `field`/`constraint`/`message`/`schema_version` beyond `code` alone?

Procedure:

* First attempt recovery using **only** `{code, field, constraint, got}` (without the full authoritative constraint text or schema excerpt). This is what the harness already returns.
* Note in `results.md` whether `field+constraint+got+message` was sufficient for correction, or whether the full schema excerpt would have been needed.
* Any need to expose authoritative constraint text beyond `field/constraint/got` is a finding that narrows claim 5 (which schema information must be exposed).

## Harness invocation

```bash
# from repo root
python3 research/capability-schema-validation/tests/test-b/run.py
python3 research/capability-schema-validation/tests/test-b/run.py --json   # machine-readable summary
python3 research/capability-schema-validation/tests/test-b/run.py --log-dir research/capability-schema-validation/logs/test-b
```

The runner logs every call as JSONL under `logs/test-b/`:

```
{variant, test_id, op_id, arguments, validation_result, error, executed, trace, latency_ms, version, phase}
```

Phases: `valid`, `malformed`, `recovery`. All 14 + 20 + 20 = 54 calls are logged. The runner asserts `executed == false` for every `malformed` case and exits non-zero on any execution of an invalid call (blocking failure per design §5.3).

## Acceptance criteria

* **Zero** malformed calls reach execution. Any `executed == true` on a malformed case is a **blocking failure** of the separation claim.
* Typed error codes are preserved end-to-end without loss for every malformed case. Any case returning a plain string or generic code is reported as a failure of the error-identity claim.
* Recovery rate per error class and aggregate is reported; threshold for "acceptable recovery" is **≥60% within 1 retry** — recorded here before the run, not inferred post hoc.
* Exposure check result is recorded explicitly in `results.md`.

## Output

* `tests/test-b/protocol.md` — this file (committed before the run; Phase 0 gate analogue for Test B).
* `tests/test-b/run.py` — runnable harness for this test.
* `logs/test-b/run.jsonl` — raw per-call logs (54 rows).
* `tests/test-b/results.md` — per-class tables, raw counts, accepted/rejected tallies, recovery rates, trace ordering audit, and WHAT-NOT-TESTED disclosures.

## WHAT-NOT-TESTED (AGENTS.md)

* Not tested: statistical significance beyond the repetition count (single repetition per case here; variance to be addressed by Tests A and D repetitions). No claim of publication-grade significance.
* Not tested: model-in-the-loop recovery (no LLM is called; recovery is simulated via scripted corrected retry, which tests whether the typed error is *sufficient* for correction, not whether a specific model *would* correct). A follow-up with an LLM-in-the-loop harness is required before claiming model-side recovery efficacy.
* Not tested: schema drift / versioning (Test C), policy/authority separation beyond validation (Test D), transport semantics (Test E).
* Not tested: output-schema validation (output is simulated; the harness does not validate runtime-generated output against `outputSchema` — that gap is noted for Test C's C3 finding).
* Not tested: cost of generating variant C (single authoring cost, not per-call).
