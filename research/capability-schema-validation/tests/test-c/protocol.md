---
title: Test C Protocol — Schema Drift / Versioning
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
  - research/capability-schema-validation/harness/error-codes.md
  - research/capability-schema-validation/harness/runtime.py
  - research/capability-schema-validation/harness/sandbox.py
consumed_by:
  - research/capability-schema-validation/tests/test-c/results.md
  - research/capability-schema-validation/report.md
---

# Test C — Schema Drift / Versioning: Protocol

**Questions addressed:** schema correctness over time; versioning claim (design §1.4 Q2-4, §5.4).

## Setup

* Start from the authoritative schemas at `version = 0.1.0` (`v0`) with model-visible descriptions derived from `v0` (`variant-c.json@0.1.0`, ≤20-word summaries + param names/types + enum literals).
* Mutate the authoritative schemas to `v1 = 0.2.0` **after** the derived descriptions have been generated, without regenerating the model-visible descriptions (simulating stale cache / delayed propagation).
* Each mutation case C1-C4 is tested independently against the same `v0` descriptions — four independent forks from `v0`, not a sequential chain.

## Mutation cases

| Case | Mutation detail (authoritative `v1` at `0.2.0`) | Files | Expected runtime behavior for `v0`-shaped calls |
|---|---|---|---|
| **C1 — Compatible additive change** | Add optional input parameter `sort_order: enum[asc, desc]` (default `asc`) to `search_artefacts`; add optional input parameter `priority: enum[low, medium, high]` (no default required) to `create_artefact`; add optional output field `query_time_ms: integer >=0` to `search_artefacts` outputSchema. All additions are optional and additive — no required field removed or tightened. Version bump `0.1.0 → 0.2.0` on mutated ops + global version. | `schemas/c1/schemas.json` | Calls using `v0` descriptions (without the new optional params) should still validate and execute (backward compatible). |
| **C2 — Incompatible parameter change** | Tighten constraints: `create_artefact.title` `maxLength 200 → 50`; `search_artefacts.query` `maxLength 200 → 50`; `create_review.rationale` `minLength 10 → 100`; `link_artefacts.relation` enum `["depends_on","supersedes","relates_to"] → ["depends_on","supersedes"]` (remove `relates_to`); `search_artefacts.limit` `maximum 100 → 20` (tighten). Each tightening makes a `v0`-valid call invalid under `v1`. Version bump `0.1.0 → 0.2.0`. | `schemas/c2/schemas.json` | Calls using `v0` descriptions that exercise the tightened surface must be rejected by runtime validation **before execution** with typed `ValidationFailed` that names the drifted `field` + `constraint` (not a generic failure). |
| **C3 — Incompatible output change** | Change `query_metrics` output shape: rename required field `total` → `count` (type integer), remove optional `facets` object, change `items[].count` type from `integer` to `string` (type incompatible). Change `search_artefacts` output: rename `items` → `results` (required). Version bump `0.1.0 → 0.2.0`. | `schemas/c3/schemas.json` | Runtime must not return a `v0`-shaped result as valid under `v1`. The mismatch must be caught before the result is returned as a success response. How it is caught (output-schema validation vs typed error vs contract check) is itself a finding (design §5.4). |
| **C4 — Operation removal / renaming** | Remove `create_review` operation entirely from the authoritative registry. Rename `search_artefacts` stable ID → `search` (old ID `search_artefacts` no longer exists). `list_reviews` is kept to avoid cascade confusion. Version bump `0.1.0 → 0.2.0`. | `schemas/c4/schemas.json` | Calls to the removed/renamed operations using the stale `v0` IDs must be rejected as `UnknownOperation` (sandbox or runtime boundary) before execution — not routed to an unrelated operation by name similarity or fuzzy match. |

All four schemas carry `version: 0.2.0` globally and per mutated capability (unmutated ops keep `0.1.0` where not bumped to make version checking explicit; mutated ops are `0.2.0`).

## Procedure (per case)

1. Capture `v0` schemas + derived `C` descriptions (already committed at Phase 0).
2. Load the mutated authoritative schema `schemas/<case>/schemas.json` as the runtime's authoritative source (runtime `Runtime(schemas_path)`).
3. Sandbox is initialized with the **mutated** allowed set (for C4 the removed/renamed IDs are absent from `allowed`; for C1-C3 the full set remains).
4. Submit valid `v0`-shaped calls (valid under `v0`, potentially invalid under `v1` for C2-C4):
   * C1: 4 calls without new optional params (should execute), plus 1 call that explicitly sends the new param to confirm it is accepted.
   * C2: 5 calls each violating exactly one tightened constraint (long title, long query, short rationale, `relates_to` relation, limit 50).
   * C3: 2 calls that produce output (`query_metrics`, `search_artefacts`) — validate output against `v1` outputSchema explicitly via `Runtime.validate_output`.
   * C4: 3 calls — `create_review` (removed), `search_artefacts` (renamed old ID), `search` (new ID, should succeed if called).
5. For each call record: `{case, op_id, arguments, payload_version, validation_result, error_code, error_field, error_constraint, executed, result_or_output_valid, latency_ms, schema_version, trace}`.
6. Additionally test **version-field check**: submit a call with explicit `payload_version="0.1.0"` against the `0.2.0` runtime and verify whether a stale version that would otherwise pass validation is caught as `VersionMismatch` (design §5.4 acceptance: stale version that still passes is a finding that versioning is inert).

## Acceptance criteria

* **C1**: `v0` calls without new optionals still execute under `v1` authoritative schemas (`executed == true`, `validation_result == executed:ok`). Adding the new optional param also executes. No `VersionMismatch` when `payload_version` is omitted; with explicit `payload_version="0.1.0"` the runtime reports `VersionMismatch` if version checking is strict (logged as finding, not a failure of C1).
* **C2-C4**: `v0` calls that are invalid under `v1` are rejected **before execution** (`executed == false`), with a typed error that distinguishes the boundary:
  * C2 → `ValidationFailed` with correct `field` + `constraint` (`maxLength`, `minLength`, `enum`, `maximum`).
  * C3 → output validation fails (not returned as success); the catching mechanism is reported (output-schema `ValidationFailed` or contract error, not silently returned).
  * C4 → `UnknownOperation` at sandbox or runtime boundary, `executed == false`, not fuzzy-routed.
* **Version field**: Version is checked at the validation boundary when `payload_version` is supplied. A stale version that still passes validation without `payload_version` is expected (validation is schema-based), but with `payload_version="0.1.0"` against `0.2.0` the runtime must return `VersionMismatch` — if it does not, that is a finding that versioning is inert (not a pass).
* Where the runtime cannot distinguish drift (e.g., returns generic `ValidationFailed` without field/constraint), that is reported as a finding (not a pass) per design §5.4.
* Do NOT reproduce the old ToolRegistry C2 experiment — the prior finding (drift undetectable pre-spawn, classification mitigation bounds cost to ~1.35-2.2x) is an input, not a template.

## Harness

* Implementation: `research/capability-schema-validation/tests/test-c/run.py` — standalone runnable, imports `harness.sandbox.Sandbox` and `harness.runtime.Runtime/Harness`, iterates C1-C4, writes per-case logs under `logs/test-c/c{1..4}.json` and a summary `logs/test-c/summary.json`.
* Runtime output validation: `Runtime.validate_output(op_id, output)` added to `runtime.py` to check `outputSchema` (Draft-07) via `Draft7Validator`; returns `(ok, error)` analogous to `validate`.
* Error codes per `harness/error-codes.md`: `ValidationFailed`, `UnknownOperation`, `VersionMismatch`, etc., with `boundary` tag.

## Repetition

* Each call listed above is run once deterministically (schema drift is a logic check, not a stochastic model effect). No temperature/model variance is required for this test — the claim is about authoritative validation, not model sampling.

## Logging

* Raw logs: `research/capability-schema-validation/logs/test-c/c1.json`, `c2.json`, `c3.json`, `c4.json`, `summary.json`.
* Each log entry: `{case, op_id, arguments, payload_version, validation_result, error, executed, output_valid?, latency_ms, schema_version, trace}`.
* No silent reshape/coercion before runtime validation; `executed == false` is asserted for every expected-rejection case.

## WHAT-NOT-TESTED (AGENTS.md)

* Not tested: concurrent drift (multiple mutations applied simultaneously); only single-case independent drift is covered.
* Not tested: rolling-upgrade / live-reload propagation delay — the mutation is a file swap, not a live service reload.
* Not tested: real LLM calls with stale `variant-c.json` prompts — the test validates the **runtime failure mode** given stale descriptions, not whether the model would have emitted the stale shape in a live generation (that is Test A scope).
* Not tested: output drift for operations beyond `query_metrics` and `search_artefacts` — other ops may have different output-schema sensitivity.
* Not tested: automatic schema migration / compat shims — the test is for detection/rejection, not transparent migration.
