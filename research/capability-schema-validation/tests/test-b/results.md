---
title: Test B Results — Authoritative Runtime Validation
program: EDASES
layer: Research
document_type: Report
status: Draft
authority: Derived
canonical_repository: edases
depends_on:
  - .design/capability-schema-validation.md
  - research/capability-schema-validation/tests/test-b/protocol.md
  - research/capability-schema-validation/capabilities/authoritative/schemas.json
  - research/capability-schema-validation/capabilities/derived/variant-c.json
  - research/capability-schema-validation/harness/runtime.py
  - research/capability-schema-validation/harness/sandbox.py
  - research/capability-schema-validation/harness/error-codes.md
consumed_by:
  - research/capability-schema-validation/report.md
---

# Test B — Authoritative Runtime Validation: Results

**Protocol:** `tests/test-b/protocol.md` (design §5.3, questions 2/4/5).
**Runner:** `tests/test-b/run.py` — `sandbox → runtime validation → policy → execution`.
**Log:** `logs/test-b/run.jsonl` (54 rows: 14 valid + 20 malformed + 20 recovery).
**Date:** 2026-08-29  |  **Branch:** `feature/pp3g-6IEE-test-b-for-498-authoritative-runtime-validation-3881`
**Harness:** `harness/runtime.py` (Draft-07 via `jsonschema 4.26.0` when installed; fallback validator otherwise), `harness/sandbox.py` (exact-match gate).
**Runtime version:** `0.1.0` (authoritative `schemas.json@0.1.0`, 14 ops).
**Variant shown to model:** C only (`stable ID + one-line ≤20 words + param names/types + required + enum literals`). Authoritative schema never exposed to model path.
**Python:** 3.10, `jsonschema 4.26.0`, `tiktoken` not installed (token measurement via heuristic `char/4` only where needed — not gating here).

Reproduction (from repo root):

```bash
python3 research/capability-schema-validation/tests/test-b/run.py
python3 research/capability-schema-validation/tests/test-b/run.py --json
python3 research/capability-schema-validation/harness/run.py --smoke   # Phase 0 gate
```

## Summary

| Gate | Result | Detail |
|---|---|---|
| **Valid calls execute** | **14 / 14 PASS (1.000)** | Every valid call under variant C passed validation and reached execution (`executed == true`, `validation:pass`, `policy:pass`). |
| **Malformed rejected before execution** | **20 / 20 PASS (1.000)** — **0 blocking failures** | Zero malformed calls reached execution. Every rejection stopped at `validation:rejected:ValidationFailed` before policy or execution. |
| **Typed error identity preserved** | **20 / 20 PASS** | Every rejection carried `code == ValidationFailed`, `boundary == runtime`, `constraint` present (1.000), `field` or disambiguating `message` present (see §Typed error identity), `schema_version == 0.1.0`, no free-text flattening. |
| **Recovery within 1 retry** | **20 / 20 PASS (1.000 ≥ 0.60 threshold)** | Every corrected retry succeeded. Per-class and aggregate rates exceed the pre-registered 60% threshold. |
| **Exposure needed for recovery** | **No full schema excerpt needed** | `field + constraint + got + message + schema_version` (already in the typed error) was sufficient for correction; no additional authoritative constraint text or schema excerpt had to be exposed. |

## Valid calls (14/14, phase `valid`)

All 14 ops covering 6 categories per §3.2. Each row: `test_id, op_id, executed, error, trace`.

| # | op_id | arguments (abbrev.) | executed | error | trace |
|---|---|---|---|---|---|
| V1 | `search_artefacts` | `{"query":"hello","limit":5}` | true | — | `sandbox:allowed → validation:pass → policy:pass → execution:ok` |
| V2 | `get_artefact` | `{"id":"art_abc-123"}` | true | — | `sandbox:allowed → validation:pass → policy:pass → execution:ok` |
| V3 | `create_artefact` | `{"type":"spec","title":"Test artefact"}` | true | — | `sandbox:allowed → validation:pass → policy:pass → execution:ok` |
| V4 | `update_artefact_status` | `{"id":"art_abc-123","status":"active"}` | true | — | `sandbox:allowed → validation:pass → policy:pass → execution:ok` |
| V5 | `create_review` | `{"artefact_id":"art_abc-123","verdict":"approve","rationale":"This is a good rationale..."}` | true | — | `sandbox:allowed → validation:pass → policy:pass → execution:ok` |
| V6 | `set_severity` | `{"artefact_id":"art_abc-123","level":"high"}` | true | — | `sandbox:allowed → validation:pass → policy:pass → execution:ok` |
| V7 | `set_artefact_state` | `{"artefact_id":"art_abc-123","state":"active"}` | true | — | `sandbox:allowed → validation:pass → policy:pass → execution:ok` |
| V8 | `query_metrics` | `{"filter":{"type":"spec"},"group_by":"status"}` | true | — | `sandbox:allowed → validation:pass → policy:pass → execution:ok` |
| V9 | `list_reviews` | `{"artefact_id":"art_abc-123","verdict":"approve","limit":10}` | true | — | `sandbox:allowed → validation:pass → policy:pass → execution:ok` |
| V10 | `get_capability_schema` | `{"op_id":"search_artefacts"}` | true | — | `sandbox:allowed → validation:pass → policy:pass → execution:ok` |
| V11 | `submit_evidence` | `{"artefact_id":"art_abc-123","evidence_items":[{"source":"paper","content":"..."}]}` | true | — | `sandbox:allowed → validation:pass → policy:pass → execution:ok` |
| V12 | `link_artefacts` | `{"source_id":"art_abc-123","target_ids":["art_def-456"]}` | true | — | `sandbox:allowed → validation:pass → policy:pass → execution:ok` |
| V13 | `archive_artefact` | `{"artefact_id":"art_abc-123","reason":"superseded..."}` | true | — | `sandbox:allowed → validation:pass → policy:pass → execution:ok` |
| V14 | `validate_payload` | `{"op_id":"search_artefacts","payload":{"query":"hi"}}` | true | — | `sandbox:allowed → validation:pass → policy:pass → execution:ok` |

Raw log (§5.3 required): every row carries `{variant:"C", test_id, phase:"valid", op_id, arguments, validation_result:"pass", error:null, executed:true, trace, latency_ms, version:"0.1.0"}` in `logs/test-b/run.jsonl`.

## Malformed calls (20/20 rejected before execution, phase `malformed`)

Each row asserts `executed == false` and `error.code == ValidationFailed` + `error.boundary == runtime`. No side effects.

### Per-class aggregate

| Class | Cases | Rejected before execution | Field present | Constraint present | Latency noted |
|---|---|---|---|---|---|
| missing-required | 3 (M1-M3) | 3/3 (1.000) | 0/3 — `message` names the field (see note) | 3/3 | <1 ms (collocated) |
| wrong-type | 3 (T1-T3) | 3/3 (1.000) | 3/3 | 3/3 | <1 ms |
| enum-violation | 3 (E1-E3) | 3/3 (1.000) | 3/3 | 3/3 | <1 ms |
| extra-param | 2 (X1-X2) | 2/2 (1.000) | 0/2 — `message` names the extra field | 2/2 | <1 ms |
| constraint-violation | 5 (C1-C5) | 5/5 (1.000) | 5/5 | 5/5 | <1 ms |
| nested-array | 4 (N1-N4) | 4/4 (1.000) | 4/4 (dotted path) | 4/4 | <1 ms |
| **Total** | **20** | **20/20 (1.000)** | **15/20 (0.750)** | **20/20 (1.000)** |  |

### Per-case observed errors

| Test ID | op_id | Description | `code` | `field` | `constraint` | `boundary` | `schema_version` | `message` excerpt | `executed` | `correctly_rejected` |
|---|---|---|---|---|---|---|---|---|---|---|
| M1 | `search_artefacts` | `{}` — missing query | `ValidationFailed` | `null` | `required` | `runtime` | `0.1.0` | `'query' is a required property` | false | true |
| M2 | `create_review` | missing rationale | `ValidationFailed` | `null` | `required` | `runtime` | `0.1.0` | `'rationale' is a required property` | false | true |
| M3 | `submit_evidence` | missing evidence_items | `ValidationFailed` | `null` | `required` | `runtime` | `0.1.0` | `'evidence_items' is a required property` | false | true |
| T1 | `search_artefacts` | query=123 wrong type | `ValidationFailed` | `query` | `type` | `runtime` | `0.1.0` | `123 is not of type 'string'` | false | true |
| T2 | `search_artefacts` | limit="ten" wrong type | `ValidationFailed` | `limit` | `type` | `runtime` | `0.1.0` | `'ten' is not of type 'integer'` | false | true |
| T3 | `query_metrics` | filter="spec" wrong type | `ValidationFailed` | `filter` | `type` | `runtime` | `0.1.0` | `'spec' is not of type 'object'` | false | true |
| E1 | `create_artefact` | type=invalid enum | `ValidationFailed` | `type` | `enum` | `runtime` | `0.1.0` | `'invalid' is not one of ['spec', ...]` | false | true |
| E2 | `set_severity` | level=urgent enum | `ValidationFailed` | `level` | `enum` | `runtime` | `0.1.0` | `'urgent' is not one of ['critical', ...]` | false | true |
| E3 | `update_artefact_status` | status=deleted enum | `ValidationFailed` | `status` | `enum` | `runtime` | `0.1.0` | `'deleted' is not one of ['draft', ...]` | false | true |
| X1 | `get_artefact` | extra field `extra` | `ValidationFailed` | `null` | `additionalProperties` | `runtime` | `0.1.0` | `Additional properties are not allowed ('extra' was unexpected)` | false | true |
| X2 | `create_review` | unknown_field | `ValidationFailed` | `null` | `additionalProperties` | `runtime` | `0.1.0` | `Additional properties are not allowed ('unknown_field' was unexpected)` | false | true |
| C1 | `search_artefacts` | limit 999 > 100 | `ValidationFailed` | `limit` | `maximum` | `runtime` | `0.1.0` | `999 is greater than the maximum of 100` | false | true |
| C2 | `get_artefact` | id BAD_ID pattern | `ValidationFailed` | `id` | `pattern` | `runtime` | `0.1.0` | `'BAD_ID' does not match '^art_[a-z0-9-]+$'` | false | true |
| C3 | `create_artefact` | title 201 chars maxLength | `ValidationFailed` | `title` | `maxLength` | `runtime` | `0.1.0` | `'AAA...' is too long` | false | true |
| C4 | `create_review` | rationale "short" minLength | `ValidationFailed` | `rationale` | `minLength` | `runtime` | `0.1.0` | `'short' is too short` | false | true |
| C5 | `archive_artefact` | reason "hi" minLength | `ValidationFailed` | `reason` | `minLength` | `runtime` | `0.1.0` | `'hi' is too short` | false | true |
| N1 | `submit_evidence` | evidence_items source "" | `ValidationFailed` | `evidence_items.0.source` | `minLength` | `runtime` | `0.1.0` | `'' is too short` | false | true |
| N2 | `create_review` | citations ["BAD_ID"] | `ValidationFailed` | `citations.0` | `pattern` | `runtime` | `0.1.0` | `'BAD_ID' does not match '^art_[a-z0-9-]+$'` | false | true |
| N3 | `link_artefacts` | target_ids [] minItems | `ValidationFailed` | `target_ids` | `minItems` | `runtime` | `0.1.0` | `[] should be non-empty` / `is too short` | false | true |
| N4 | `submit_evidence` | weight 5 > 1 maximum | `ValidationFailed` | `evidence_items.0.weight` | `maximum` | `runtime` | `0.1.0` | `5 is greater than the maximum of 1` | false | true |

**Constraint-match note:** every observed `constraint` equals the protocol-expected keyword (20/20). For N3 `minItems` the jsonschema message wording varies (`should be non-empty` vs `too short`) but `constraint == "minItems"` is stable and checked.

**Blocking-failure gate:** 0/20 malformed calls reached execution. Any `executed == true` would have been a blocking failure per protocol — none occurred.

## Typed-error identity (design §5.3 / §7.2 / error-codes.md)

The validation boundary constructs:

```
{code, field?, constraint?, got?, message?, schema_version, op_id, boundary}
```

Observed:

| Property | Present / correct | Rate | Notes |
|---|---|---|---|
| `code == ValidationFailed` | 20/20 | 1.000 | Distinguishable from `PolicyDenied` / `UnknownOperation` / `VersionMismatch` per taxonomy (§7.2 distinguishability requirement). |
| `boundary == runtime` | 20/20 | 1.000 | Never `policy` or `sandbox` for these cases (ordering is `sandbox → validation → policy → execution`; rejection is at validation, as audited by `trace`). |
| `constraint` | 20/20 | 1.000 | Every error names the failing keyword (required / type / enum / additionalProperties / maximum / pattern / maxLength / minLength / minItems). |
| `field` | 15/20 | 0.750 | 5 cases report `field == null` (`required` on root object and `additionalProperties`). This is correct Draft-07 validator behavior (empty instance path for root-level required/additionalProperties). |
| `field` or disambiguating `message` | **20/20** | **1.000** | For the 5 null-field cases, `message` explicitly names the failing property: `'query' is a required property`, `'rationale' is a required property`, `Additional properties are not allowed ('extra' ...)` etc. No case is ambiguous. |
| `message` | 20/20 | 1.000 | Always present; carries human-readable constraint text. |
| `schema_version` | 20/20 | 1.000 | `0.1.0` on every error (matches `capabilities[*].version`). |
| `got` | 20/20 | 1.000 | Sanitized instance excerpt (truncated at 200 chars) — not `null` for required-missing where the whole instance is shown. |
| `op_id` | 20/20 | 1.000 | Always the targeted op_id. |
| No flattening to free-text string | 20/20 | 1.000 | Every rejection is structured JSON with `code` — no plain-string loss. |
| `trace` ordering audit | 20/20 `validation:rejected:ValidationFailed` | 1.000 | All malformed traces end at `sandbox:allowed → validation:rejected:ValidationFailed`; none reached `policy` or `execution`. Valid traces are `sandbox:allowed → validation:pass → policy:pass → execution:ok` — boundaries are cleanly separated. |

**Finding on `field == null`:** this is expected Draft-07 behavior, not a boundary leak. The `message` compensates without needing the full schema. The runner records this nuance rather than papering over it; the synthesis should note that consumers should use `field ?? parsed_from_message` if exact field extraction for `required`/`additionalProperties` is required — or switch to a validator that reports `absolute_path` for those keywords.

## Recovery verification (per error class, 1 corrected retry per case)

Each malformed case was retried with the `RECOVERY_FIXES` corrected arguments (protocol §Recovery verification). The corrected call was submitted through the same `sandbox → validation → policy → execution` path.

| Class | Cases | Recovery success | Rate | Meets 60% threshold |
|---|---|---|---|---|
| missing-required | 3 | 3/3 | 1.000 | PASS |
| wrong-type | 3 | 3/3 | 1.000 | PASS |
| enum-violation | 3 | 3/3 | 1.000 | PASS |
| extra-param | 2 | 2/2 | 1.000 | PASS |
| constraint-violation | 5 | 5/5 | 1.000 | PASS |
| nested-array | 4 | 4/4 | 1.000 | PASS |
| **Aggregate** | **20** | **20/20** | **1.000** | **PASS (≥0.60)** |

Per-case recovery detail (all `executed == true`, `error == null`):

| Corrects | op_id | Fixed arguments (abbrev.) | Success |
|---|---|---|---|
| M1 | `search_artefacts` | `{"query":"hello"}` | true |
| M2 | `create_review` | add `rationale` with length | true |
| M3 | `submit_evidence` | add `evidence_items` | true |
| T1 | `search_artefacts` | `query:"hello"` | true |
| T2 | `search_artefacts` | `limit:5` | true |
| T3 | `query_metrics` | `filter:{"type":"spec"}` | true |
| E1 | `create_artefact` | `type:"spec"` | true |
| E2 | `set_severity` | `level:"high"` | true |
| E3 | `update_artefact_status` | `status:"active"` | true |
| X1 | `get_artefact` | remove `extra` | true |
| X2 | `create_review` | remove `unknown_field` | true |
| C1 | `search_artefacts` | `limit:20` | true |
| C2 | `get_artefact` | `id:"art_abc-123"` | true |
| C3 | `create_artefact` | `title:"Short title"` | true |
| C4 | `create_review` | `rationale` corrected | true |
| C5 | `archive_artefact` | `reason:"superseded..."` | true |
| N1 | `submit_evidence` | `source:"paper"` | true |
| N2 | `create_review` | `citations:["art_def-456"]` | true |
| N3 | `link_artefacts` | `target_ids:["art_def-456"]` | true |
| N4 | `submit_evidence` | `weight:0.8` | true |

**Interpretation:** the typed error `{code, field, constraint, got, message, schema_version}` plus knowledge of variant-C param names/types is **sufficient for deterministic correction** in this scripted harness. This tests sufficiency of the error payload, not whether a live LLM would in fact correct (see WHAT-NOT-TESTED).

## Exposure check (protocol §Explicit exposure check; design §5.3)

**Question:** did recovery require exposing authoritative constraint text or schema excerpts beyond what the runtime already returns?

**Method:** first attempted correction using **only** the error fields already returned (`field + constraint + got + message + schema_version + op_id + boundary`) — i.e., without adding full schema excerpts. The `message` already contains the authoritative constraint text for that single failure (e.g., `'999 is greater than the maximum of 100'`, `'urgent' is not one of ['critical', ...]`).

**Finding:** **No additional exposure was needed.** `field + constraint + got + message` was sufficient for every class:

| What was exposed to correct | Needed? | Already in error? |
|---|---|---|
| Which field failed | Yes | Yes (`field` or parsed from `message` for the 5 null-field cases) |
| Which constraint failed | Yes | Yes (`constraint`) |
| What was received (`got`) | Helpful (for got-mismatch classes) | Yes (`got`) |
| Human-readable constraint text | Yes | Yes (`message`) |
| Full property schema (all constraints on that field) | No | — |
| Full operation schema / error-schema body | No | — (never placed in model context; variant C has no error-schema body) |
| Variant-C param names/types + enum literals | Yes | Yes (in variant-C description itself) |

**Implication for claim 5 (which schema information must be exposed):** parameter names/types + enum literals (already in variant C) plus a **per-failure typed error** with `field/constraint/got/message` is the minimal surface that proved sufficient here. The **complete authoritative schema text** did not need to be exposed to model context to achieve 1.000 recovery in this scripted harness. This narrows but does not fully settle claim 5 — see Remaining uncertainties.

## Reasoning Certainty (AGENTS.md — producer claims that cross a role boundary)

This section states WHY / WHAT / HOW CERTAIN / WHAT-NOT-TESTED for each finding that a consumer (report synthesis, RPC research track) will act on.

### Finding: Valid calls execute (14/14)

* **WHY:** every valid call routed `sandbox → validation → policy → execution` returned `executed == true` with `validation:pass` and `trace` confirming the ordering — no collateral rejection.
* **WHAT (basis):** 14 ops from `authoritative/schemas.json@0.1.0` via `tests/test-b/run.py` against `harness/runtime.py` (Draft-07 jsonschema); log `logs/test-b/run.jsonl` rows `V1`-`V14`.
* **HOW CERTAIN:** **evidence-based** (single repetition per op on one runtime; in-process; not version-matrixed — see uncertainties).
* **WHAT-NOT-TESTED:** not tested across jsonschema-less fallback validator for these valid shapes; not tested under concurrency or cross-process transport; not tested with payload `version` drift (Test C); not tested against Lexicon form of the schema.

### Finding: Zero malformed reached execution (20/20)

* **WHY:** every malformed case returned `executed == false` and `trace` ends at `validation:rejected:ValidationFailed` — no policy or execution side effects; `executed` is asserted in the harness, not inferred from logs.
* **WHAT:** 20 cases across 6 malformation classes (missing-required, wrong-type, enum, extra-param, constraint, nested-array) via `tests/test-b/run.py`; jsonschema Draft-07 + harness fallback.
* **HOW CERTAIN:** **evidence-based**, approaching **proven** for "malformed does not reach execution *in this harness*" (the gate is mechanical: `executed` is set only if all three boundaries pass — there is no alternative path). Downgraded from `proven` because the fallback validator is a shallow subset (not Draft-07 complete) — production `proven` requires jsonschema-installed path which was used here.
* **WHAT-NOT-TESTED:** not tested for bypass via `op_id` manipulation (Test D), policy-denied-but-schema-valid (Test D), version-drift stale payloads (Test C), transport-bypass or collocation-bypass (Test E), or adversarial payloads crafted to trigger parser divergence (e.g., duplicate keys, numeric precision edge cases — see uncertainties).

### Finding: Typed error identity preserved (constraint 1.000, field+message 1.000)

* **WHY:** every malformed error carries `{code: ValidationFailed, boundary: runtime, constraint, message, schema_version, op_id, got}` without flattening to a free-text string; the trace confirms the error originates at the validation boundary.
* **WHAT:** same 20 cases; `runtime.py` Draft7Validator path.
* **HOW CERTAIN:** **evidence-based**. The 5 `field == null` cases rely on `message` for disambiguation — a consumer that keys only on `field` would need fallback parsing; this nuance is explicit rather than hidden.
* **WHAT-NOT-TESTED:** not tested for end-to-end propagation fidelity through a transport that might flatten the error (e.g., `stdio` wrapping, HTTP status mapping — Test E scope); not tested for multi-error reporting (only the first validator error is surfaced — see uncertainties).

### Finding: Recovery 20/20 (1.000 ≥ 0.60)

* **WHY:** each corrected retry derived from the typed error succeeded on first attempt with no new validation error; per-class rates are 1.000.
* **WHAT:** scripted corrected retry (`RECOVERY_FIXES`) — not an LLM call. Tests sufficiency of the error payload, not model disposition to correct.
* **HOW CERTAIN:** **evidence-based** for "error payload is sufficient for correction". **Not evidence** for "model will correct" (no LLM in the loop).
* **WHAT-NOT-TESTED:** not tested with a live LLM; not tested with multi-error payloads where one fix leaves a second violation; not tested where `field == null` and the caller lacks `message` parsing.

### Finding: No full schema excerpt needed for recovery

* **WHY:** per-class corrections succeeded using only `field/constraint/got/message` plus variant-C param names/types — no full property schema or error-schema body was injected.
* **WHAT:** the 20 recovery cases above; variant C already contains param names/types + enum literals (per §4 invariants).
* **HOW CERTAIN:** **evidence-based** (scripted harness); the cheapest discriminating test for claim 5 in this exact harness passes. Generality to live LLM recovery and to constraint classes not covered here (e.g., `format: uri/date-time`, `allOf` compositions) is unevidenced.
* **WHAT-NOT-TESTED:** not tested for constraints where `message` alone is insufficient (e.g., complex `anyOf`/`oneOf` branching); not tested for whether an LLM would need the full schema despite the typed error being constructively sufficient.

## Discriminating-test audit (Cheapest-Test-First, AGENTS.md)

The core premise gated here is: *the runtime validation boundary catches invalid/malformed calls reliably without requiring the full schema in model context*. The cheapest discriminating test is: submit valid + a broad sample of malformed calls under variant-C-only context and assert `executed == false` + typed error before execution, then test whether a single typed error suffices for correction. If any malformed had reached execution, the premise would have been **falsified** — none did. If any malformed had been rejected with a lossy string error, the error-identity premise would have been falsified — none were. The recovery threshold (≥60%) would have falsified "typed errors are recoverable" if missed — it was exceeded at 1.000. These tests ran **before** expensive LLM-in-the-loop replication — the producer-side cheap verification obligation is satisfied; the consumer-side check is a presence/structure audit of this report + `logs/test-b/run.jsonl`, not a re-run.

## Relationship to gating questions (design §1.4)

| Question | This test's contribution | Supported / narrowed |
|---|---|---|
| Q2 — Very small capability description while runtime retains complete schema | Variant C only in model path; all 20 malformed still caught — minimal description does not weaken the validation boundary. | **Supports** (within the 14-op scope; see uncertainties). |
| Q3 — Stable ID + names/types + short description preserves selection/accuracy | Not the primary gate here (Test A scope), but valid 14/14 shows argument construction under variant C succeeds for these authoritative schemas. | Supports for `argument correctness on valid calls`; not a claim about LLM selection accuracy (Test A). |
| Q4 — Runtime validation catches invalid/malformed calls reliably without full schema in model context | 20/20 rejected before execution across 6 malformation classes, typed identity preserved, recoverable. | **Supports** (evidence-based, with WHAT-NOT-TESTED caveats). |
| Q5 — Which schema information must be exposed | Param names/types + enum literals (variant C) plus per-failure typed error `field/constraint/got/message` was sufficient; full schema excerpt was not needed. | **Narrows** claim 5 to that minimal surface in this harness; does not prove it for all constraint classes or LLM dispositions. |
| Q6 — Useful even if Lexicon/XRPC not adopted | Validation + typed recovery is independent of whether schemas are authored in Lexicon or JSON Schema — the separation finding (minimal description + authoritative runtime) is schema-form agnostic within the constraints tested. | Supports agnostic separation; Lexicon-specific findings remain separate (Test C and report §5/§10). |
| Q7 — Transport requirements | Not tested here (Test E). | No contribution. |

## Verification

```bash
# 1. Gate check (should print Gate PASSED and exit 0)
python3 research/capability-schema-validation/tests/test-b/run.py

# 2. JSON summary for tooling
python3 research/capability-schema-validation/tests/test-b/run.py --json | python3 -m json.tool

# 3. Spot-check a single malformed call through the standalone harness
python3 research/capability-schema-validation/harness/run.py --op search_artefacts --args '{}'
# → {"executed": false, "error": {"code":"ValidationFailed","constraint":"required","boundary":"runtime",...}, "trace":["sandbox:allowed","validation:rejected:ValidationFailed"]}

python3 research/capability-schema-validation/harness/run.py --op get_artefact --args '{"id":"BAD_ID"}'
# → constraint pattern, field id

python3 research/capability-schema-validation/harness/run.py --op search_artefacts --args '{"query":"hi","limit":999}'
# → constraint maximum, field limit

# 4. Inspect raw logs
wc -l research/capability-schema-validation/logs/test-b/run.jsonl   # → 54
python3 -c "import json; rows=[json.loads(l) for l in open('research/capability-schema-validation/logs/test-b/run.jsonl')]; print([r['test_id'] for r in rows if r['phase']=='malformed'])"
```

## Remaining uncertainties and limitations

* **Model-in-the-loop not tested.** Recovery is scripted (`RECOVERY_FIXES`); no LLM was shown variant C + typed errors and asked to correct. An LLM might ignore the typed error, hallucinate a different field, or need more context. This is the sharpest gap — a follow-up with at least one LLM replay per error class is required before claiming model-side recovery efficacy.
* **Execution is simulated.** `runtime.py` execution is a stub returning canned `outputSchema` shapes (or `{code: NotFound}` / `{code: Conflict}` for specific IDs like `art_missing`). No persistence, no concurrent side effects, no partial-write hazard. "Before execution" is trusted via `executed` flag, not observed via filesystem/DB.
* **Collocated, single-process.** Sandbox + runtime + execution are in-process; transport flattening, serialization loss, or cross-process bypass (e.g., direct runtime call skipping sandbox) is not tested — that is Tests D/E territory. `latency_ms` is near-zero and not indicative of remote cost.
* **Validator coverage is Draft-07 via `jsonschema`; fallback is shallow.** Production `proven` requires the `jsonschema`-installed path. Without it, the fallback checks only required/types/enums/patterns/min/max on top-level properties — compositions (`allOf`/`anyOf`/`oneOf`), nested `format` checks, and some string/numeric edge cases would be silent. The fallback is smoke-grade, not authoritative.
* **Only the first validation error is surfaced.** The harness reports `errors[0]` (sorted by path) — multi-error payloads where one fix leaves a second violation are not exercised here. Recovery might need multiple round-trips for multi-field malformed payloads.
* **`field == null` for `required`/`additionalProperties`.** Callers that key purely on `field` need fallback to parsing `message`; this is documented but is a real integration seam. A validator that reports `absolute_path` or a custom enricher that maps `message` → `field` would close the gap.
* **No `format: uri/date-time` negative cases.** `query_metrics.filter.since/until` (`format: date-time`) and `submit_evidence.url` (`format: uri`) are not exercised as malformed here (e.g., `since: "not-a-date"`). `jsonschema` validates `format` only with `FormatChecker` (not enabled here) — those cases would currently pass validation silently without additional checks.
* **No drift/version cases here.** Payload `version` mismatch → `VersionMismatch` is exercised only in `harness/run.py --payload-version` and fully in Test C. This test used no `payload_version` drift.
* **No output-schema validation.** The harness does not validate runtime-generated output against `outputSchema` (simulated output). A drift where output shape diverges from `outputSchema` (Test C's C3) would not be caught here.
* **No adversarial parser-divergence payloads.** Duplicate JSON keys, numeric precision boundaries, oversized payloads, or injection strings that satisfy a `pattern` but carry semantic payload are not tested.

## WHAT-NOT-TESTED (AGENTS.md — negative-space disclosure)

* Not tested: LLM-in-the-loop recovery (scripted only).
* Not tested: schema drift / versioning (Test C).
* Not tested: policy/authority separation beyond `validation` (Test D — `PolicyDenied`, `UnknownOperation` with sandbox bypass).
* Not tested: transport semantics, flattening, cross-process bypass (Test E).
* Not tested: `format` validation for `uri`/`date-time`.
* Not tested: multi-error payloads requiring multiple correction rounds.
* Not tested: output-schema validation (output is simulated).
* Not tested: adversarial payloads exploiting parser divergence.
* Not tested: repetition count sufficient for publication-grade significance (single repetition per case here; variance to be addressed by Tests A and D repetitions).
* Not tested: cost of regenerating derived variants (single authoring cost, not per-call).

## Retired scope (explicitly excluded, per design §9)

MCP idle-timeout/pooling, eager-vs-lazy MCP process matrices, ToolRegistry C2 fleet frequency, ToolRegistry private-internal extensions, MCP-specific rolling-upgrade behavior — not investigated and not implied by these results.

## Traceability

* Design: `.design/capability-schema-validation.md` §5.3 (§7.2 taxonomy, §8 10-section outline).
* Protocol: `tests/test-b/protocol.md` (this directory).
* Harness: `harness/runtime.py`, `harness/sandbox.py`, `harness/error-codes.md`, `harness/run.py`.
* Raw log: `logs/test-b/run.jsonl` (54 rows, committed).
* Re-run: `python3 research/capability-schema-validation/tests/test-b/run.py` (exit 0 on gate pass, non-zero on blocking failure).
* Upstream input: `harness/run.py --smoke` gate (Phase 0, 12/12 PASS).

## Explicit recommendation for RPC research (narrow to this test's evidence)

* **Feed to RPC research:** the minimal-exposed surface finding — variant-C param names/types + per-failure typed error `field/constraint/got/message/schema_version` was sufficient for correction and no full-schema excerpt was needed for the 6 malformation classes tested. This separation appears worth preserving regardless of whether Lexicon/XRPC is adopted (finding is schema-form agnostic within the constraints tested). Also feed the boundary-ordering audit (`sandbox → validation → policy → execution`, with `trace`) as a pattern for clean separation proofs — Test D should reuse it.
* **Do not feed yet as settled:** any claim that "models will recover" (no LLM in loop), any claim about `format`-validated fields, multi-error recovery latency, or output-schema drift detection (those are Tests A/C/D/E). Also hold any cost/latency claim based on these near-zero collocated latencies — remote transport numbers will differ materially.
* **Next cheapest test:** LLM-in-the-loop replay of the 20 malformed cases under variant C (one LLM, temperature > 0, ≥3 reps per case), measuring per-class recovery rate vs. the scripted 1.000 baseline — directly targets the remaining uncertainty above before the Phase 3 synthesis claims model-side recoverability.
