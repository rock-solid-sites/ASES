---
title: Failure Taxonomy — #530 Tool-Calling Corpus
program: EDASES
layer: Research
document_type: Reference
status: Active
authority: Derived
canonical_repository: edases
issue: 530
depends_on:
  - research/capability-schema-validation/corpus-530/schemas/authoritative.json
  - research/capability-schema-validation/corpus-530/schemas/minimal.json
  - research/capability-schema-validation/harness/error-codes.md
---

# Failure Taxonomy (530)

Single source for classifying every tool-calling failure in the 24+12+4 corpus.
Codes are distinguishable by `code` alone (no string parsing).

## Primary error codes (runtime boundaries)

| Code | Boundary | When emitted | Payload fields | Reporting |
|---|---|---|---|---|
| `ValidationFailed` | `runtime` (input) | Arguments fail authoritative JSON Schema (type, required, enum, pattern, minimum/maximum, minLength/maxLength, additionalProperties, nested, mutually-constrained) | `{code, field?, constraint?, got?, message, schema_version, op_id, boundary:"runtime"}` | D2-style malformed; includes hidden range/pattern/mutual/schema constraints NOT exposed in minimal |
| `UnknownOperation` | `sandbox` (preselected surface) or `runtime` fallback | `op_id` not in allowed set / not in authoritative registry; exact stable-ID match only, no fuzzy | `{code, op_id, hint?, boundary:"sandbox"}` | D1-style hallucinated/absent capability |
| `PolicyDenied` | `policy` (after validation:pass) | Schema-valid call denied by runtime policy (deny list, resource deny) | `{code, policy, reason, op_id, boundary:"policy"}` | D3-style policy boundary |
| `OutputValidationFailed` | `runtime:output` | Input passed and execution produced output that violates authoritative outputSchema (e.g., total→count, items→results, missing facets) | `{code:"OutputValidationFailed" (logical) / ValidationFailed with boundary runtime:output, field, constraint, got, schema_version, op_id}` | D4-style output violation; in harness serialized as `ValidationFailed` with `boundary:"runtime:output"` but reported distinctly as D4 for corpus accounting |

**Distinctness requirement:** D1 `UnknownOperation` vs D2 `ValidationFailed` vs D3 `PolicyDenied` vs D4 `OutputValidationFailed` must be distinguishable by `code` (or `code+boundary` for D4). A generic rejection with the wrong code is a failure of that check.

## ValidationFailed sub-classes (12 malformed recovery)

| Sub-class | Constraint | Example |
|---|---|---|
| missing_required | `required` | `{}` missing query |
| wrong_type | `type` | `query:123` |
| invalid_enum | `enum` | `type:"invalid"` |
| invalid_nested_field | `type` (nested) | `filter:"spec"` string not object |
| missing_nested_required | `required` (nested) | `evidence_items[0]` missing content |
| hidden_range_violation | `maximum`/`minimum` | `limit:999` (1–100 hidden) |
| invalid_combination | `mutually_constrained` | `filter.type==group_by` |
| malformed_array | `minItems`/`type` | `target_ids:[]` |
| malformed_object | `additionalProperties` | `get_artefact` extra field |
| balanced missing_required | `required` | `create_review` missing rationale |
| balanced invalid_enum | `enum` | `level:"urgent"` |
| balanced hidden_pattern | `pattern` | `id:"BAD_ID"` |

## Success vs failure accounting

- **Selection success**: `selected op_id == expected op_id` (exact match).
- **Argument success**: all arguments validate against authoritative schema (`ValidationFailed` absent) AND values equal expected (or equivalent).
- **Task success**: selection success AND argument success AND (for valid tasks) `executed==true` with output validating against outputSchema.
- **Validation failure**: `ValidationFailed` before execution (counts toward retry/recovery metrics).
- **Retry**: single corrected retry after `ValidationFailed`; measure `recovery_tokens`, `one_retry_success` (first retry succeeds), `multi_retry_success` (succeeds within N retries).

## Non-errors (not failures)

- Optional field omitted correctly (R/O ambiguity class) — not a failure if required present.
- Enum literal present in minimal (must stay visible) — omission in minimal is a corpus defect, not a model failure.

## WHAT-NOT-TESTED

- Retry classification nuances (retryable vs non-retryable beyond one corrected retry) — input from `research/toolregistry-lazy-mcp/retry-classification/report.md`, not re-derived.
- Transport error propagation fidelity (Timeout/Cancelled/ConnectionLost) — Test E scope, not this corpus.
- State-machine/policy/lifecycle/discovery/pooling/idle-timeout — explicitly out of scope per kickoff.

