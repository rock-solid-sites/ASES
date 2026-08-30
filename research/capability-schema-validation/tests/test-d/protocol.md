---
title: Test D Protocol — Capability / Authority Separation (D1-D4)
program: EDASES
layer: Research
document_type: Protocol
status: Draft
authority: Derived
canonical_repository: edases
depends_on:
  - .design/capability-schema-validation.md
  - research/capability-schema-validation/capabilities/authoritative/schemas.json
  - research/capability-schema-validation/harness/sandbox.py
  - research/capability-schema-validation/harness/runtime.py
  - research/capability-schema-validation/harness/error-codes.md
consumed_by:
  - research/capability-schema-validation/tests/test-d/results.md
  - research/capability-schema-validation/report.md
---

# Test D — Capability / Authority Separation: Protocol

**Questions addressed:** Runtime remains authoritative; model description is never authority (design §5.5, issue #498 Test D).

**Target architecture:** `agent → sandbox → small preselected capability API → authoritative execution/runtime` (design §1.3). The runtime, not the model description, must remain authoritative.

## Prerequisites

* Authoritative schemas: `research/capability-schema-validation/capabilities/authoritative/schemas.json` (version `0.1.0`, 14 capabilities per `capabilities/manifest.json`).
* Harness: `research/capability-schema-validation/harness/{sandbox.py,runtime.py,run.py,error-codes.md}` with execution-gate assertion `executed == false` for every expected-rejection case.
* Error taxonomy: single source `harness/error-codes.md` — codes `ValidationFailed`, `UnknownOperation`, `PolicyDenied`, `VersionMismatch`, `NotFound`, `Conflict`, `Timeout`, `Cancelled`, `ConnectionLost`. Distinguishability: `ValidationFailed` vs `PolicyDenied` vs `UnknownOperation` by `code` alone.
* Sandbox: exact stable-ID match only, no fuzzy matching (harness `sandbox.py:check`).

## Global controls (design §5.1)

* Fixed capability set reused from Phase 0 (§3). No mutation except where a check explicitly restricts the sandbox surface (D1) or policy (D2).
* Fixed harness ordering auditable via `trace`: `sandbox → validation → policy → execution`. Each result carries `trace` and `validation_result` for boundary ordering audit.
* No silent reshape/coercion/retry before runtime validation (harness must not pre-process).
* Each check is a dedicated test case with an explicit `expected_error_code` — a generic rejection with the wrong code is a **failure** of that check (design §5.5 Harness requirements).

## Required checks (design §5.5 — independently verifiable, no silent pass)

### D1 — Absent capability

| Field | Value |
|---|---|
| **Claim** | A capability absent from the sandbox cannot be invoked. |
| **Setup** | The authoritative registry contains 14 ops at `0.1.0`. The sandbox is configured with a **restricted preselected surface** that excludes at least 4 operations. Model-visible description contains only the allowed ops. The test attempts to invoke an excluded op with schema-valid arguments (and also with one hallucinated op not in the registry at all). |
| **Restricted surface used** | `allowed = {search_artefacts, get_artefact, create_artefact, create_review, set_severity, query_metrics, list_reviews, get_capability_schema, submit_evidence, link_artefacts}` (10 ops). **Excluded** (present in registry but absent from sandbox): `update_artefact_status`, `set_artefact_state`, `archive_artefact`, `validate_payload`. |
| **Cases** | D1.1 `archive_artefact` (excluded, valid args) — must be `UnknownOperation` at sandbox. D1.2 `set_artefact_state` (excluded, valid args) — `UnknownOperation` at sandbox. D1.3 `update_artefact_status` (excluded, valid args) — `UnknownOperation` at sandbox. D1.4 hallucinated `delete_artefact` (not in registry at all) — `UnknownOperation` at sandbox. D1.5 valid allowed op still executes (`search_artefacts`) — control that restriction does not block allowed ops. |
| **Expected result** | Each excluded/hallucinated call is rejected at the **sandbox boundary** before any validation/policy/execution (`validation_result == "rejected:sandbox"`, `error.code == "UnknownOperation"`, `error.boundary == "sandbox"`, `executed == false`). No side effects. |
| **Trace assertion** | `trace == ["sandbox:rejected:UnknownOperation"]` for D1.1-D1.4; control D1.5 trace is `["sandbox:allowed","validation:pass","policy:pass","execution:ok"]`. |
| **Why this falsifies** | If any excluded call reached validation or execution, the sandbox preselection would not be authoritative. |

### D2 — Policy-denied capability

| Field | Value |
|---|---|
| **Claim** | A capability present in the model description but denied by runtime policy is rejected. Schema validation passes; the policy boundary rejects with a distinct code. |
| **Setup** | Capability is in the model-visible description and its arguments are **schema-valid** under the authoritative schema. A runtime policy denies it. Two policy forms are tested: (a) op-level deny, (b) resource-level deny. |
| **Cases** | D2.1 op-level deny `search_artefacts` with `policy={"deny":["search_artefacts"]}` — valid args `{"query":"hello"}` — expect `PolicyDenied` at policy. D2.2 op-level deny `create_artefact` with `deny=["create_artefact"]` — valid args `{"type":"spec","title":"T"}` — `PolicyDenied` at policy. D2.3 resource-level deny `get_artefact` with `policy={"deny_resources":["art_denied-001"]}` and args `{"id":"art_denied-001"}` — `PolicyDenied` at policy. D2.4 resource-level deny `archive_artefact` with `deny_resources=["art_secret-001"]` — `PolicyDenied` at policy. D2.5 control: same ops without deny policy must execute (valid→execute). |
| **Expected result** | Schema validation passes; policy rejects: `validation_result == "rejected:policy"`, `error.code == "PolicyDenied"`, `error.boundary == "policy"`, `executed == false`. The error code is **not** `ValidationFailed` or `UnknownOperation` — the two rejection reasons are distinguishable by code alone. |
| **Trace assertion** | `trace == ["sandbox:allowed","validation:pass","policy:rejected:PolicyDenied"]` for D2.1-D2.4. Control traces include `policy:pass → execution:ok`. Any `validation:rejected:ValidationFailed` on these cases is a **boundary-separation failure** even if blocked (design §5.5 acceptance). |
| **Negative control** | A schema-invalid call with a deny policy must be rejected at **validation**, not policy — `validation:rejected:ValidationFailed` precedes policy, proving ordering. That case is covered jointly with D3 ordering check D3.6. |

### D3 — Malformed bypass attempt

| Field | Value |
|---|---|
| **Claim** | A malformed request cannot bypass runtime validation, even when well-formed enough to be dispatched. |
| **Setup** | Submit requests that pass the sandbox (known op_id) but fail authoritative JSON Schema validation. Cover malformation classes from Test B §5.3 minimally plus privilege-escalation-shaped extra fields. |
| **Cases** | D3.1 missing required param: `search_artefacts` with `{}` (missing `query`) — `ValidationFailed`/`required`. D3.2 wrong type: `search_artefacts` with `{"query":123}` — `ValidationFailed`/`type`. D3.3 enum violation: `create_artefact` with `{"type":"invalid","title":"t"}` — `ValidationFailed`/`enum`. D3.4 extra unknown param (privilege-escalation probe): `get_artefact` with `{"id":"art_abc-123","admin":true,"role":"superuser"}` and `additionalProperties:false` — `ValidationFailed`/`additionalProperties`. D3.5 constraint violation (over max): `search_artefacts` with `{"query":"hi","limit":999}` where max 100 — `ValidationFailed`/`maximum`. D3.6 pattern violation (injection in string field): `get_artefact` with `{"id":"BAD_ID; DROP TABLE"}` where pattern `^art_[a-z0-9-]+$` — `ValidationFailed`/`pattern`. D3.7 nested array type error: `submit_evidence` with `{"artefact_id":"art_abc-123","evidence_items":[{"source":"","content":""}]}` (empty source violates minLength 1, or missing required) — `ValidationFailed`. D3.8 policy-irrelevant extra with valid shape: `create_review` with `{"artefact_id":"art_abc-123","verdict":"approve","rationale":"Rationale long enough","escalate":true}` — `ValidationFailed`/`additionalProperties`. |
| **Expected result** | Every case: `validation_result == "rejected:validation"`, `error.code == "ValidationFailed"`, `error.boundary == "runtime"`, `executed == false`. Rejection occurs **before** any policy check or execution — the `trace` must be `["sandbox:allowed","validation:rejected:ValidationFailed"]` with no `policy:*` entry. A case that reached `policy:rejected` or `execution:*` is a bypass. |
| **Ordering probe** | D3 cases use a deny policy in one sub-case (e.g., D3.1 with `deny=["search_artefacts"]`) to assert validation still precedes policy: trace must remain `sandbox:allowed → validation:rejected`, not `policy:rejected`. |

### D4 — Operation-identifier manipulation

| Field | Value |
|---|---|
| **Claim** | The model cannot select an arbitrary implementation by manipulating the operation identifier. Only exact stable ID matches are dispatched. |
| **Setup** | Submit calls where `op_id` is manipulated in ways a model might hallucinate/guess (typo, casing, prefix injection, path traversal, numeric guessing, whitespace). Arguments are schema-valid for the intended target, so dispatch is the only gate under test. All variants must be `UnknownOperation` at sandbox (or runtime fallback) and **no** fuzzy match must occur. |
| **Cases** | D4.1 typo-squat missing letter: `search_artefact` (missing `s`) — `UnknownOperation`. D4.2 typo extra letter: `search_artefactsx` — `UnknownOperation`. D4.3 casing: `Search_Artefacts` and `SEARCH_ARTEFACTS` and `search_Artefacts` — each `UnknownOperation`. D4.4 prefix injection: `internal__search_artefacts`, `admin_search_artefacts` — `UnknownOperation`. D4.5 path traversal: `../search_artefacts`, `search_artefacts/../admin`, `search_artefacts%2Fadmin` — `UnknownOperation`. D4.6 numeric guessing: `"0"`, `"1"`, `"999"` — `UnknownOperation`. D4.7 empty/whitespace: `""`, `" search_artefacts"`, `"search_artefacts "` — `UnknownOperation`. D4.8 alias-guess: `getArtefact`, `get-artefact`, `artefact.get` — `UnknownOperation`. D4.9 exact valid control: `search_artefacts` with valid args — must dispatch (`executed==true`). |
| **Expected result** | Every manipulated ID: `error.code == "UnknownOperation"`, `executed == false`, `validation_result` is `rejected:sandbox` (since sandbox exact-match gate catches it before runtime). `trace == ["sandbox:rejected:UnknownOperation"]`. The runtime fallback `UnknownOperation` boundary is also `UnknownOperation` but at sandbox the claim is strictly sandbox-first — an implementation that only covers runtime fallback but allows fuzzy sandbox matching is a **failure**. |
| **No-fuzzy assertion** | The sandbox check is `op_id in allowed` exact match (python `set` membership). No substring, case-folding, Levenshtein, or prefix routing. This is asserted by source inspection in results.md and by passing all D4 cases. |

## Acceptance criteria (design §5.5)

* All four checks reject **before execution**, with the correct typed error code for the failing boundary:
  * D1 → `UnknownOperation` at sandbox.
  * D2 → `PolicyDenied` at policy (after `validation:pass`).
  * D3 → `ValidationFailed` at runtime validation (before policy).
  * D4 → `UnknownOperation` at sandbox.
* Any check where the wrong boundary rejects is a finding that boundaries are not cleanly separated, even if ultimately blocked (e.g., a policy-denied call rejected as `ValidationFailed` is a separation failure).
* Each check is a dedicated test case with explicit `expected_error_code` — a generic rejection with wrong code is a failure.
* The full `trace` ordering is logged and auditable for every case.

## Logging

Every call records `{check, case_id, op_id, arguments, payload_version?, policy?, validation_result, error, executed, result, latency_ms, version, trace, expected_code, pass}`.

* Raw logs: `research/capability-schema-validation/logs/test-d/d1.jsonl` through `d4.jsonl` (and combined `all.jsonl`).
* Each entry is a single JSON object per line (JSONL), commit-tracked per `.design` file layout and `agent-orchestration-playbook.md` §5.9.
* Harness NEver silently retries/reshapes; authoritative schema text is never printed to model path.

## What this protocol does NOT test (WHAT-NOT-TESTED for the protocol itself)

* Not tested here: token/accuracy, runtime-typed-error recovery after `ValidationFailed`, or multi-step argument correctness — those are Tests A/B scope.
* Not tested here: schema drift/versioning interaction with authority — Test C scope; Test D version is pinned at `0.1.0` with no drift mutations.
* Not tested: Lexicon/XRPC-specific authority propagation or cryptographic operation attestation — this test measures JSON Schema + harness-enforced boundaries only.
* Not tested: policy content beyond op-deny and resource-deny (no tenancy/role-hierarchy, no ABAC, no time-window policies).
* Not tested: concurrent/transport-level bypass (race between validation and execution, TOCTOU) — Test E scope.

## Verification

Before results are claimed:

1. `python3 research/capability-schema-validation/tests/test-d/run.py` exits `0` with all cases `PASS` or with `FAIL` explicitly recorded as findings (no silent pass).
2. `python3 research/capability-schema-validation/harness/run.py --smoke` still passes `12/12` (Phase 0 gate unbroken).
3. No artifact exists only in `/tmp`; all logs are committed under `logs/test-d/`.

## Reproducibility

From repo root on the feature branch:

```bash
python3 research/capability-schema-validation/tests/test-d/run.py          # run D1-D4
python3 research/capability-schema-validation/tests/test-d/run.py --json   # emit raw JSONL to stdout
python3 research/capability-schema-validation/tests/test-d/run.py --case D2  # filter by check prefix
```
