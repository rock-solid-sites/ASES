---
title: Test C Results — Schema Drift / Versioning
program: EDASES
layer: Research
document_type: Report
status: Draft
authority: Derived
canonical_repository: edases
depends_on:
  - .design/capability-schema-validation.md
  - research/capability-schema-validation/tests/test-c/protocol.md
  - research/capability-schema-validation/capabilities/authoritative/schemas.json
  - research/capability-schema-validation/tests/test-c/schemas/c1/schemas.json
  - research/capability-schema-validation/tests/test-c/schemas/c2/schemas.json
  - research/capability-schema-validation/tests/test-c/schemas/c3/schemas.json
  - research/capability-schema-validation/tests/test-c/schemas/c4/schemas.json
  - research/capability-schema-validation/harness/runtime.py
  - research/capability-schema-validation/harness/sandbox.py
  - research/capability-schema-validation/harness/error-codes.md
consumed_by:
  - research/capability-schema-validation/report.md
---

# Test C — Schema Drift / Versioning: Results

**Date:** 2026-08-29
**Runner:** `research/capability-schema-validation/tests/test-c/run.py` (deterministic, no LLM sampling)
**Harness:** `sandbox → runtime validation (Draft-07) → policy → execution → output validation` per `harness/runtime.py`
**Tokenizer:** not applicable (drift logic check, not token/accuracy)
**Schemas:** `v0 = 0.1.0` (14 ops) → `v1 = 0.2.0` forks per `schemas/{c1,c2,c3,c4}/schemas.json`; model-visible `variant-c.json@0.1.0` held stale
**Logs:** `research/capability-schema-validation/logs/test-c/{c1,c2,c3,c4,summary}.json` (21 cases, all PASS)

## Setup

Derived `variant-c.json` from `v0 0.1.0` was kept stale while the authoritative runtime was swapped to each `v1 0.2.0` fork. Each case was tested independently (not sequentially). The sandbox was initialized from the mutated schema's allowed set so that removal/renaming is visible at the sandbox boundary (exact-match only, no fuzzy matching). Calls are `v0`-shaped (valid under `v0`). Version-field check was exercised via explicit `payload_version="0.1.0"` against the `0.2.0` runtime.

## Results by case

### C1 — Compatible additive change (backward compatible)

Mutation: `search_artefacts` + optional `sort_order: enum[asc,desc]` (default `asc`); `create_artefact` + optional `priority: enum[low,medium,high]`; `search_artefacts` output + optional `query_time_ms: integer`. All optional, none tightened. 7 calls.

| # | Call | Expected | Observed `validation_result` | `executed` | `error.code` | Verdict |
|---|---|---|---|---|---|---|
| C1-1 | `search_artefacts {query:"hello",limit:5}` (no new param) | execute | `executed:ok` | true | — | **PASS** |
| C1-2 | `get_artefact {id:"art_abc-123"}` | execute | `executed:ok` | true | — | **PASS** |
| C1-3 | `create_artefact {type:"spec",title:"My Spec"}` (no priority) | execute | `executed:ok` | true | — | **PASS** |
| C1-4 | `query_metrics {filter:{type:"spec"}}` | execute | `executed:ok` | true | — | **PASS** |
| C1-5 | `search_artefacts {query:"hi",sort_order:"desc"}` (new param) | execute | `executed:ok` | true | — | **PASS** |
| C1-6 | `create_artefact {type:"spec",title:"T2",priority:"high"}` (new param) | execute | `executed:ok` | true | — | **PASS** |
| C1-7 | `search_artefacts {query:"hi"}` + `payload_version:"0.1.0"` vs mutating `0.2.0` op | reject `VersionMismatch` | `rejected:validation` | false | `VersionMismatch` (expected `0.2.0`, got `0.1.0`) | **PASS** |

**Finding C1:** `v0` calls without new optionals still validate and execute under `v1` — compatible additive change is backward compatible as expected. New optional params are accepted when supplied. Without `payload_version`, schema validation alone correctly allows `v0` payloads (no false rejection). With explicit `payload_version="0.1.0"`, the runtime returns distinct `VersionMismatch` before schema validation — version check is active and distinguishable from `ValidationFailed`.

Acceptance: **met** — C1 `v0` calls execute under `v1`; version mismatch is cleanly distinguished when version is carried.

### C2 — Incompatible parameter change (tightened constraints)

Mutations: `create_artefact.title` `maxLength 200→50`; `search_artefacts.query` `maxLength 200→50`; `create_review.rationale` `minLength 10→100`; `link_artefacts.relation` enum removes `relates_to`; `search_artefacts.limit` `maximum 100→20`. 6 calls.

| # | Call | Violated constraint | Expected | Observed `error` | `executed` | Verdict |
|---|---|---|---|---|---|---|
| C2-1 | `create_artefact {title: "A"*60}` | `title maxLength 50` | reject `ValidationFailed`/`maxLength` | `ValidationFailed` field `title` constraint `maxLength` | false | **PASS** |
| C2-2 | `search_artefacts {query: "q"*60}` | `query maxLength 50` | reject | `ValidationFailed` field `query` `maxLength` | false | **PASS** |
| C2-3 | `create_review {rationale: 20ch}` | `rationale minLength 100` | reject | `ValidationFailed` field `rationale` `minLength` | false | **PASS** |
| C2-4 | `link_artefacts {relation:"relates_to"}` | `relation enum` (removed) | reject | `ValidationFailed` field `relation` `enum` | false | **PASS** |
| C2-5 | `search_artefacts {limit:50}` | `limit maximum 20` | reject | `ValidationFailed` field `limit` `maximum` | false | **PASS** |
| C2-6 | `create_artefact {title:"hi"}` + `payload_version:"0.1.0"` | version mismatch | `VersionMismatch` | `VersionMismatch` expected `0.2.0` got `0.1.0` | false | **PASS** |

All five incompatible calls were rejected **before execution** (`executed == false`, `trace` ends at `validation:rejected:ValidationFailed`). Errors carry typed `field` + `constraint` + `got` + `message` + `schema_version` per `error-codes.md`. `VersionMismatch` is distinct from `ValidationFailed` when `payload_version` is supplied.

**Finding C2:** Tightened input constraints are caught at the validation boundary before any policy or execution. `v0`-valid / `v1`-invalid drift is not silently accepted. Error payload names the exact field and constraint — actionable without exposing the full new schema text.

Acceptance: **met** — `v0` calls invalid under `v1` are rejected before execution with typed `ValidationFailed` (field+constraint), distinguishable from `VersionMismatch`.

### C3 — Incompatible output change (output-schema drift)

Mutations: `query_metrics` output `total → count` (required rename), remove `facets`, change `items[].count` type `integer→string`; `search_artefacts` output `items → results` (required rename). 3 calls.

| # | Call | Input validation | Execution | Output validation vs `v1` outputSchema | Catching mechanism | Verdict |
|---|---|---|---|---|---|---|
| C3-1 | `query_metrics {filter:{type:"spec"}}` | pass | `executed:ok` result `{items:[{key:"all",count:1}], total:1}` | **FAIL** — `'count' is required` (has `total`), boundary `runtime:output` | `output_schema` | **PASS** (mismatch caught) |
| C3-2 | `search_artefacts {query:"hello"}` | pass | `executed:ok` result `{items:[], total:0, has_more:false}` | **FAIL** — `'results' is required` (has `items`), boundary `runtime:output` | `output_schema` | **PASS** (mismatch caught) |
| C3-3 | sanity: `v1`-shaped output `{items:[{key:"spec",count:"1"}], count:1}` vs `query_metrics@v1` | — | — | **PASS** (valid) | `none` | **PASS** |

**Finding C3:** Output incompatibility is **not** caught by input validation (input passes, execution succeeds). Without an explicit `validate_output` step, the stale `v0`-shaped result would be returned to the caller as a valid response — exactly the gap noted in the prior ToolRegistry C2 output-schema-drift finding (drift undetectable pre-spawn). With the added `Runtime.validate_output` check (Draft-07 `outputSchema`), the mismatch is caught before return, surfaced as `ValidationFailed` on `runtime:output` with required-field errors (`count` / `results`). The catching mechanism is **output-schema validation**, not input validation or a contract error — callers must not trust that execution success implies output-schema success.

**Gap reported:** The baseline harness (`Harness.call`) did not validate outputs until this test added `validate_output`. Any deployment that skips output validation will silently return stale-shaped outputs as successes. That residual gap is analogous to the retry-classification residual noted in design §5.4 — it requires a host-internal output check.

Acceptance: **met with finding** — `v0` output mismatched under `v1` is caught, but only by an explicit output-schema validation step added for this test; without it the mismatch is undetectable (finding, not a pass of the original harness).

### C4 — Operation removal / renaming (stable IDs)

Mutations: remove `create_review`; rename `search_artefacts → search` (old ID absent). 5 calls.

| # | Call | Expected | Observed | `executed` | `trace` | Verdict |
|---|---|---|---|---|---|---|
| C4-1 | `create_review {artefact_id:"art_abc-123", verdict:"approve", rationale:"Rationale with enough length for validation"}` | reject `UnknownOperation` | `rejected:sandbox` `UnknownOperation` hint `op_id not in preselected sandbox surface; no fuzzy matching` | false | `sandbox:rejected:UnknownOperation` | **PASS** |
| C4-2 | `search_artefacts {query:"hello"}` (old ID, now `search`) | reject `UnknownOperation` | `rejected:sandbox` `UnknownOperation` | false | `sandbox:rejected:UnknownOperation` | **PASS** |
| C4-3 | `search {query:"hello"}` (new ID) | execute | `executed:ok` | true | `sandbox:allowed → validation:pass → policy:pass → execution:ok` | **PASS** |
| C4-4 | `Search_Artefacts {query:"hi"}` (typo/casing) | reject `UnknownOperation` (no fuzzy) | `rejected:sandbox` `UnknownOperation` | false | `sandbox:rejected:UnknownOperation` | **PASS** |
| C4-5 | `create_review` + `payload_version:"0.1.0"` (removed) | reject `UnknownOperation` (precedence over version) | `rejected:sandbox` `UnknownOperation` | false | `sandbox:rejected:UnknownOperation` | **PASS** |

All removed/renamed calls were rejected at the **sandbox** boundary (`sandbox:rejected:UnknownOperation`) before runtime validation or execution — no dispatch, no fuzzy routing. The new ID `search` correctly executes; casing/typo variants do not dispatch.

**Finding C4:** Stable operation IDs + exact-match dispatch provide a clean failure mode — `UnknownOperation` before execution, distinguishable from `ValidationFailed` / `VersionMismatch` / `PolicyDenied`. No silent re-routing via name similarity.

Acceptance: **met** — removed/renamed calls are `UnknownOperation` before execution, not fuzzy-routed.

## Version-check findings (cross-cutting)

* Version carry: When `payload_version` is omitted, validation is purely schema-driven — `v0` payloads that are still schema-compatible under `v1` (C1) correctly pass; `v0` payloads that violate `v1` constraints (C2) correctly fail as `ValidationFailed`. This is expected — version is not inferred.
* Version enforcement: When `payload_version="0.1.0"` is carried against a `0.2.0` mutated op, the runtime returns distinct `VersionMismatch {expected_version:"0.2.0", actual_version:"0.1.0", op_id}` before any schema inspection, with `executed==false`. This is demonstrated in C1-7 and C2-6.
* Stale-without-version: A stale `0.1.0` description that still passes `v1` schema validation without a version field will **not** be flagged — version inertness without version carry is the expected semantics, not a bug. Consumers that need stale-detection must carry and check `payload_version` (finding, not a failure).

## Stable IDs + runtime checks — clean failure mode?

**Yes, with one caveat:**

* Input drift (C2) and removal/rename (C4) produce typed errors (`ValidationFailed` with field+constraint, `UnknownOperation`) before execution, without requiring the caller to possess the full new schema. The error is actionable (`field`, `constraint`, `got`) per §7.2.
* C1 additive drift produces no error — backward compatibility is preserved without caller action.
* Output drift (C3) is the exception: the caller **does** receive a successful execution result unless the host adds an explicit `validate_output` step. Once added, the output mismatch is surfaced as `ValidationFailed` at `runtime:output` — still actionable, but the additional check is host-internal work, not free. This matches the prior C2 finding that output-schema drift mitigation bounds cost but requires classification/validation work.

Overall, stable IDs + runtime schema/version checks **do** provide a clean, typed failure mode for input/ID drift. Output drift requires a symmetric output validation to achieve the same guarantee.

## Logs

Raw logs committed under `research/capability-schema-validation/logs/test-c/`:

* `c1.json` — 7 entries (4 backward-compat + 2 new-param + 1 version)
* `c2.json` — 6 entries (5 constraint violations + 1 version)
* `c3.json` — 3 entries (2 drift + 1 sanity)
* `c4.json` — 5 entries (2 removed/renamed + 1 new-ID + 1 fuzzy + 1 version)
* `summary.json` — `{total:21, passed:21, failed:0, overall_pass:true}`

Reproduction:

```bash
python3 research/capability-schema-validation/tests/test-c/run.py        # all cases
python3 research/capability-schema-validation/tests/test-c/run.py --case c1
python3 research/capability-schema-validation/tests/test-c/run.py --case c2
python3 research/capability-schema-validation/tests/test-c/run.py --case c3
python3 research/capability-schema-validation/tests/test-c/run.py --case c4
python3 research/capability-schema-validation/harness/run.py --smoke     # harness gate
```

## WHAT-NOT-TESTED (AGENTS.md)

* Not tested: concurrent/compound drift (multiple cases applied together); only single-case independent mutations were exercised.
* Not tested: live rolling upgrade or propagation delay — mutation is a file swap from `0.1.0` to `0.2.0`, not a running service reload with in-flight requests.
* Not tested: real LLM generations from stale `variant-c.json` — the test checks the **runtime** failure mode given a stale-shaped payload, not whether the model would emit that shape (Test A scope).
* Not tested: output drift for ops beyond `query_metrics` and `search_artefacts`; other outputs may have different sensitivity.
* Not tested: automatic migration / compat shims — the test is for detection/rejection, not transparent forward-migration.
* Not tested: `stdio`-only vs remote transport effects (Test E scope) — drift is transport-independent here (local harness).
* Not tested: version-range negotiation — only exact `payload_version` equality is checked, not semver-range compatibility.
