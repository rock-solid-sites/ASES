---
title: Capability/Schema Validation Design — Minimal Capability Descriptions, Runtime-Authoritative Schemas, and Transport Semantics
program: EDASES
layer: Research
document_type: Design
status: Draft
authority: Derived
canonical_repository: edases
parent_epic: "#212"
parent_issue: "#498"

depends_on:
  - docs/standards/Documentation Standard.md
  - docs/standards/Concept - Levels of Abstraction.md
  - docs/standards/Canonical Terminology.md
  - docs/research/Identifier-First Tool Calling.md
  - docs/research/Workflow Topology Design and Reasoning Record.md
  - research/toolregistry-lazy-mcp/report.md
  - research/toolregistry-lazy-mcp/output-schema-drift/report.md
  - research/toolregistry-lazy-mcp/retry-classification/report.md
  - research/toolregistry-lazy-mcp/c2-gap-investigation/report.md
  - research/toolregistry-lazy-mcp/catalog-scale/report.md
  - docs/ORCHESTRATOR.md
  - .crosslink/knowledge/agent-orchestration-playbook.md
  - .crosslink/knowledge/model-discipline.md

consumed_by:
  - research/capability-schema-validation/** (all phase outputs)
  - research/capability-schema-validation/report.md (final synthesis)

related_documents:
  - .design/observer-swarm-v1.1-resilience.md
  - docs/research/Proposed Implementation Layer - Decision Record.md
  - docs/research/Tools Distribution Architecture Decision Test Framework.md

supersedes: []
superseded_by: []
last_updated: 2026-08-29
---

# Capability/Schema Validation — Research Design Document

## 1. Purpose and Scope

### 1.1 What this document is

This document is the **swarm-ready design** for issue #498 — *ASES Capability/Schema Validation*. It decomposes the investigation into executable phases, each with precise protocols, acceptance criteria, artifact locations, and reproducibility requirements. It is the sole source of truth for the swarm launched from this design.

### 1.2 What this document is not

* Not an engine implementation or architecture redesign.
* Not an extension of the old lazy-MCP / `ToolRegistry` lifecycle prototype unless a gating question explicitly requires it.
* Not a publication-grade statistical study. The goal is to distinguish obvious effects with enough repetitions to falsify the core claims, not to achieve publication-grade significance.

### 1.3 Target architecture (non-negotiable framing)

```text
agent → sandbox → small preselected capability API → authoritative execution/runtime
```

* The **sandbox** exposes a fixed, small capability surface selected before the task begins.
* The **model** sees only minimal capability descriptions.
* The **runtime** retains the complete authoritative schema and is the sole authority for validation, policy, and execution.
* No inference about this architecture may be drawn solely from prior stdio-local results unless separately validated for the transport under test.

### 1.4 Seven gating questions (from #498)

1. Does a fixed, preselected capability surface eliminate the practical need for token-lazy discovery, process-lazy spawning, pooling, and idle-timeout management?
2. Can the model use a very small capability description while the runtime retains the complete authoritative schema?
3. Does a stable operation identifier + parameter names + short description preserve tool/capability selection and argument accuracy?
4. Does runtime validation against the authoritative schema catch invalid/malformed calls reliably without requiring the full schema in model context?
5. Which schema information actually needs to be exposed to the model?
6. Which parts of this separation remain useful if Lexicon/XRPC itself is not adopted?
7. Which transport properties are actually required by the EDASES control boundary?

These questions gate the claims recorded in the final synthesis. No claim is considered supported until the cheapest discriminating test for that claim has been run (Cheapest-Test-First, AGENTS.md).

---

## 2. Relationship to Prior Work

| Prior work | Relationship | Boundary |
|---|---|---|
| `research/toolregistry-lazy-mcp/` (lazy proxy, drift, retry-classification, C2-gap, catalog-scale) | Inputs and constraints; version-bound to `toolregistry 0.15.0 / mcp 2.0.0` — re-validate on upgrade (trigger #279 under #212). | Do **not** re-run or extend the lazy-MCP / `ToolRegistry` lifecycle prototype unless required to answer one of the seven questions above. MCP/ToolRegistry-specific lifecycle questions are explicitly **retired** (see §9). |
| `docs/research/Identifier-First Tool Calling.md` | Parent research framework. Phases 2-4 of that programme map to Tests A/B here; Phase 5 partially overlaps. | This design is scoped to capability/schema/transport validation, not the full Phases 0-6 programme. |
| `docs/research/Workflow Topology Design and Reasoning Record.md` | Provides the workflow-topology principles (reasoning certainty, cheapest-test-first, position-emitting agents, AUDITOR as in-flight divergence verifier). | Swarm phases in this design obey that topology (pre-positioned AUDITOR, position store, staleness trigger). |
| Lexicon/XRPC | One candidate for the authoritative schema layer. | Tests are structured so that findings about minimal descriptions and runtime-authoritative validation are reported separately from Lexicon-specific findings (see §5, §7, §11). |

---

## 3. Capability Set Definition

### 3.1 Purpose

A single representative capability set is reused across Tests A-D so that results are comparable. Transport (Test E) references the same set where applicable.

### 3.2 Coverage requirements

The set MUST contain **10-20 operations** and MUST cover all six required categories:

| # | Category | Minimum coverage | Example shapes (adapt to domain) |
|---|---|---|---|
| 1 | Read / query | >= 2 ops | `search_artefacts(query, limit, cursor?)`, `get_artefact(id)` |
| 2 | State-changing operation | >= 1 op | `create_artefact(type, title, body)` or `update_status(id, status)` |
| 3 | Operation with several parameters | >= 1 op | `create_review(artefact_id, verdict, severity, rationale, citations[])` — 4+ params, mixed required/optional |
| 4 | Operation with enum / constrained values | >= 1 op | `set_severity(level: enum[critical, high, medium, low])`, `set_state(state: enum[draft, active, archived])` |
| 5 | Operation producing structured output | >= 1 op | `query_metrics(filter) → {items:[], total, cursor, facets{}}` with nested schema |
| 6 | Operation with meaningful typed errors | >= 2 distinct error shapes | `NotFound {code, artefact_id}`, `ValidationFailed {code, field, constraint, got}`, `Conflict {code, expected_version, actual_version}` |

### 3.3 Additional constraints

* Include at least one operation with **optional parameters** and one with **array / nested-object** parameters (these are the accuracy-sensitive cases per Identifier-First Tool Calling §Landscape Review).
* Include at least one operation with **output schema that materially differs** from its input schema (required for drift test C — incompatible output change).
* All operations expose a **stable operation identifier** (opaque, non-semantic where possible) that is the only identifier the model may use to select an implementation. Human-readable names must NOT be usable as execution selectors.
* Schemas are authored once in the authoritative runtime. Model-visible descriptions are **derived** artifacts, not sources of truth.

### 3.4 Authoritative schema form

* Author the full schemas in a single canonical form consumable by runtime validation (JSON Schema preferred; Lexicon form acceptable if a bidirectional mapping is demonstrated — the mapping itself is then a tested artifact, not an assumed convenience).
* Version field is mandatory on every schema (`version: string`, semver or date-based — pick one and document it). Version is used verbatim in drift tests (Test C).

### 3.5 Deliverable

`research/capability-schema-validation/capabilities/`:

* `authoritative/schemas.json` (or equivalent) — full runtime schemas.
* `derived/variant-a.json`, `variant-b.json`, `variant-c.json` — minimal descriptions per §4.
* `manifest.json` — `{capabilities, version, derived_from, generated_at}`.

---

## 4. Variant Definitions (A / B / C)

These three variants are the controlled manipulation for Test A. All other factors (task set, harness, repetition count) are held constant across variants.

| Variant | Content shown to the model per capability | Approx. token budget guidance |
|---|---|---|
| **A — Full schema** | Complete JSON Schema / Lexicon definition: all properties, types, descriptions, constraints (enum, pattern, min/max, required), error schemas. | Baseline (largest). Measured, not assumed. |
| **B — Short description + names/types** | Operation name (stable ID) + one-line summary + parameter names + parameter types + required/optional + enum values where applicable. No per-parameter long descriptions, no full constraint text, no error-schema detail beyond error-code names. | Intermediate. |
| **C — Stable ID + one-line + names/types** | Stable operation ID + one-line description (<= 20 words) + parameter names + parameter types + required flag + enum literals. Minimal constraint surface. No error-schema body. | Smallest. Target for the separation claim. |

### 4.1 Invariants across variants

* Stable operation IDs are identical across A/B/C.
* Parameter **names and types** are present in all three variants (the Identifier-First re-review hypothesizes this is the minimum for argument construction — Test A measures whether it holds).
* Error schemas are **never** shown in model context in any variant — runtime validation is the sole error-classification authority (Test B checks whether this costs accuracy).

### 4.2 Reporting requirement

For each variant, record the exact character count, token count (specify tokenizer and version), and tool-description block as it appeared to the model. Token numbers without a named tokenizer version are not reportable.

---

## 5. Test Protocols

### 5.1 Global experimental controls

* **Fixed capability set** from §3 is used for every test unless the test definition explicitly mutates it (Test C).
* **Fixed task set**: author a task set of **>= 20 tasks** spanning the six categories, each task requiring 1-3 capability calls with verifiable success criteria. Reuse the same tasks across variants where possible; where a task is variant-sensitive, note the difference explicitly.
* **Repetition**: each variant × task cell is run **>= 3 times** with temperature > 0 or with prompt-order permutation sufficient to distinguish obvious selection/argument effects from single-run noise. Report per-cell counts. Do not claim statistical significance beyond what the repetition count supports.
* **Harness logging**: every call records `{variant, task_id, repetition, capability_selected, arguments_submitted, runtime_validation_result, error_code_if_any, tokens_in_context, latency_ms}`. Logs are committed under `research/capability-schema-validation/logs/`.
* **No silent fallback**: if any harness step silently retries or reshapes a call before runtime validation sees it, the test is invalid — such shaping must be disabled or logged as a failed control.

### 5.2 Test A — Minimal capability description

**Question addressed:** 2, 3, 5.

**Setup:**

1. Construct the capability set (§3) and task set (§5.1).
2. Generate variants A/B/C (§4).
3. Run each task under each variant with the repetition count from §5.1.

**Measures (per variant):**

* Correct capability selection rate (selected == expected). Report as `correct / total`.
* Argument correctness rate (all required params present, types correct, enum values valid, no extraneous params that violate the authoritative schema). Measured against the **authoritative schema**, not the minimal description.
* Invalid-call rate (calls rejected by runtime validation).
* Recovery-after-rejection rate (given a rejection with the typed error from the runtime, does the next call from the model succeed without human intervention? — ties to Test B's harness).
* Prompt/token size in context (characters + tokens per §4.2).

**Acceptance criteria:**

* Define them **before** running: e.g., "C is acceptable if capability-selection rate is within 5pp of A and argument-correctness within 5pp of A on the fixed task set." The concrete thresholds are a pre-registration choice — record the chosen thresholds in `research/capability-schema-validation/tests/test-a/protocol.md` and do not adjust post hoc.
* Report the token/accuracy curve explicitly: `tokens(C) / tokens(A)` vs. accuracy deltas. A claim that "C preserves accuracy" is unsupported if the measured delta exceeds the pre-registered tolerance, even if the absolute accuracies look high.

**Output:**

* `research/capability-schema-validation/tests/test-a/protocol.md`
* `research/capability-schema-validation/tests/test-a/results.md` (with per-variant tables)
* Raw logs under `research/capability-schema-validation/logs/test-a/`

---

### 5.3 Test B — Authoritative runtime validation

**Question addressed:** 2, 4, 5.

**Setup:**

1. Give the model **only variant C** (the minimal description).
2. Keep the complete authoritative schema exclusively in the runtime — not in model context, not in any prompt template, not in tool-use system messages.
3. Route every model-issued call through a runtime validation boundary before execution.

**Procedure:**

1. Submit a set of **valid calls** (covering all operations in the capability set) and verify they pass validation and execute.
2. Submit deliberately **malformed calls** covering at minimum:
   * Missing required parameter.
   * Wrong type (string where number expected, etc.).
   * Enum violation.
   * Extra unknown parameter.
   * Constraint violation (e.g., `limit > max`, `title` too long where a maxLength exists).
   * Malformed nested object / array element type error.
3. Verify each malformed call is **rejected before execution** — no side effects, no partial writes, no log pollution that implies execution occurred. The harness must assert `executed == false` on every expected-rejection case.
4. Verify **typed/structured error identity is preserved** — the error returned to the caller carries `{code, field?, constraint?, got?}` per the authoritative error schema, not a free-text string. Record whether the model receives the typed error verbatim or a lossy translation.
5. Verify the model can **recover from representative validation failures** — after a typed rejection, does the model's next call correct the specific field/error without introducing a new error? Measure per-error-class recovery rate.

**Acceptance criteria:**

* Zero malformed calls reach execution. Any execution of a schema-invalid call is a **blocking failure** of the separation claim.
* Typed error codes are preserved end-to-end (runtime → caller → model-visible error) without loss. Any code → string flattening is reported as a failure of the error-identity claim.
* Recovery rate per error class is reported; a threshold for "acceptable recovery" is pre-registered (e.g., >= 60% of typed rejections are correctly recovered within 1 retry) — do not infer acceptability post hoc.

**Explicit check:**

* Record **whether any validation information had to be exposed to the model** to achieve recovery (e.g., did the error message need to include the authoritative constraint text?). Any such exposure is a finding that narrows claim 5 (which schema information must be exposed).

**Output:**

* `research/capability-schema-validation/tests/test-b/protocol.md`
* `research/capability-schema-validation/tests/test-b/results.md`
* Raw logs under `research/capability-schema-validation/logs/test-b/`

---

### 5.4 Test C — Schema drift / versioning

**Question addressed:** schema correctness over time; versioning claim.

**Setup:**

* Start from the authoritative schemas at `version = v0` with model-visible descriptions derived from `v0`.
* Mutate the authoritative schemas to `v1` **after** the derived descriptions have been generated, without regenerating the model-visible descriptions (simulating stale cache / delayed propagation).

**Required mutation cases (each tested independently against `v0` descriptions):**

| Case | Mutation | Expected runtime behavior |
|---|---|---|
| C1 — Compatible additive change | Add an optional parameter with a default, or add an optional output field. | Calls using `v0` descriptions should still validate and execute (backward compatible). |
| C2 — Incompatible parameter change | Rename a required parameter, change its type, or tighten a constraint (e.g., `string → enum`, `maxLength 100 → 50`). | Calls using `v0` descriptions must be rejected by runtime validation with a typed error that names the drift (not a generic failure). |
| C3 — Incompatible output change | Change the output schema shape (rename/remove a field, change a field type). | Runtime must not validate output against the stale `v0` expectation; the mismatch must be caught before the result is returned to the model as a valid response. How it is caught (output validation vs. typed error vs. contract check) is itself a finding. |
| C4 — Operation removal / renaming | Remove an operation or rename its stable ID while keeping the old ID's description visible to the model. | Calls to the removed/renamed operation must be rejected as `NotFound` / `UnknownOperation` before execution — not routed to an unrelated operation by name similarity. |

**Procedure for each case:**

1. Capture `v0` schemas + derived `C` descriptions.
2. Apply the mutation to the authoritative schema → `v1`.
3. Submit valid `v0`-shaped calls (valid under `v0`, potentially invalid under `v1`).
4. Record: `validation_result`, `error_code`, `executed`, `latency`, `spawns/side-effects`.

**Acceptance criteria:**

* C1: `v0` calls still execute under `v1` authoritative schemas.
* C2-C4: `v0` calls that are invalid under `v1` are rejected before execution, with a typed error that distinguishes "drift/version mismatch" from "generic invalid call" where possible. If the runtime cannot distinguish, that is reported as a finding (not a pass).
* Version field from §3.4 must be checked at the validation boundary — a stale version that still passes validation is a finding that the versioning mechanism is inert.
* Do **not** reproduce the old `ToolRegistry` C2 experiment unless needed to answer the drift-mismatch undetectability question directly — the C2 output-schema-drift finding (retrofit §5.2 results: drift undetectable pre-spawn, classification mitigation bounds cost to ~1.35-2.2x) is an input, not a template to re-run.

**Open question to answer:**

* Whether stable operation IDs + runtime schema/version checks provide a clean failure mode — specifically, does the caller receive an error that is actionable without exposing the full new schema?

**Output:**

* `research/capability-schema-validation/tests/test-c/protocol.md`
* `research/capability-schema-validation/tests/test-c/results.md`
* Mutated schemas under `research/capability-schema-validation/tests/test-c/schemas/{c1,c2,c3,c4}/`

---

### 5.5 Test D — Capability / authority separation

**Question addressed:** runtime remains authoritative; model description is never authority.

**Required checks (each independently verifiable, no silent pass):**

| Check | Setup | Expected result |
|---|---|---|
| D1 — Absent capability | A capability exists in the authoritative registry but is **not** in the sandbox's preselected set and **not** in the model-visible description. The model is prompted to try to invoke it (or hallucinates it). | Call is rejected at the sandbox/runtime boundary before execution; no execution side effects. |
| D2 — Policy-denied capability | A capability is in the model-visible description and passes schema validation, but a runtime policy denies it (e.g., role, tenancy, artefact ownership). | Call passes schema validation but is rejected at the policy boundary with a distinct `PolicyDenied` / `Forbidden` error, not a schema error. The two rejection reasons must be distinguishable. |
| D3 — Malformed bypass attempt | Submit a request that is well-formed enough to be dispatched but fails authoritative schema validation (e.g., type confusion, injection in string fields that violates a pattern, extra fields that would escalate privilege if ignored). | Rejected by schema validation before any policy check or execution. No bypass. |
| D4 — Operation-identifier manipulation | Submit a call where the operation identifier is manipulated (typo-squat, prefix injection, alternative casing, numeric ID guessing, path-like traversal) to select an unintended operation. | Only exact stable ID matches are dispatched; any non-exact ID is `UnknownOperation`. No fuzzy matching. The model cannot select an arbitrary implementation by manipulating the identifier. |

**Harness requirements:**

* Each check is a dedicated test case with an explicit `expected_error_code` — a generic rejection with the wrong code is a failure of that check.
* Log the full validation trace where available (schema validation → policy check → dispatch) so that the ordering of boundaries is auditable.

**Acceptance criteria:**

* All four checks reject before execution, with the correct typed error code for the failing boundary.
* Any check where the wrong boundary rejects (e.g., a policy-denied call rejected as a schema error) is a finding that the boundaries are not cleanly separated, even if the call was ultimately blocked.

**Output:**

* `research/capability-schema-validation/tests/test-d/protocol.md`
* `research/capability-schema-validation/tests/test-d/results.md`

---

### 5.6 Test E — Transport requirements

**Question addressed:** 7.

**Constraint:** Do **not** test MCP lifecycle features (idle-timeout, pooling, eager-vs-lazy matrices). Establish the **minimum transport semantics** the EDASES control boundary requires, using the simplest representative transports needed to establish each property. Compare `stdio` only as a local baseline; do **not** infer remote behavior from prior stdio results.

#### 5.6.1 Required transport properties to establish

Each property below must be tested independently with a pass/fail criterion. A property that is not required by the control boundary is a finding of exclusion, not a skipped test — record the reasoning for exclusion.

| Property | Definition | Minimal test |
|---|---|---|
| **Concurrent requests** | Multiple in-flight requests at the same time, without serializing at the transport. | Issue N concurrent calls (N >= 4) and verify all complete, results match the correct requests, and total wall time is < N × single-call latency (demonstrates non-serial execution where expected). |
| **Request/response correlation** | Every response is unambiguously matched to its request, even under concurrency and reordering. | Under concurrent load, verify each response carries the correct correlation ID and payload for its request. Inject a delayed response and confirm no cross-wiring. |
| **Remote execution** | Capability executes on the authoritative runtime, not in the sandbox process. | Prove execution locality (e.g., runtime PID / host identity differs from sandbox; or a side-effect is visible only on the runtime). Do not assume collocation. |
| **Connection loss** | Behavior when the transport drops mid-request and mid-idle. | Kill the transport under both conditions; record whether in-flight requests receive a typed error, whether idle state is preserved or requires re-establishment, and whether partial writes are possible. |
| **Reconnect** | Ability to re-establish after loss without manual intervention and without leaking prior state. | After a loss, reconnect and verify that (a) new requests succeed, (b) prior in-flight requests are not silently retried with different semantics, and (c) no orphaned server processes remain (cf. catalog-scale orphan finding: `toolregistry 0.15.0 / mcp 2.0.0` orphans on owner death without explicit close). |
| **Timeout** | A per-request deadline after which the caller receives a typed timeout error and the runtime can decide to cancel or continue. | Issue a deliberately slow operation; verify the caller receives `Timeout` within the deadline and the runtime's disposition of the operation is observable (cancelled vs. still running). |
| **Cancellation** | Caller-initiated cancellation of an in-flight request, distinct from timeout. | Issue a long-running operation, cancel it mid-flight, verify the runtime stops work (or explicitly reports it will continue) and no partial side effects leak as success. |
| **Streaming / events** *(conditional)* | Incremental result delivery (progress, partial output, logs) if the control boundary requires it. | If streaming is claimed as required, demonstrate a streaming operation (e.g., log tail, multi-step progress) and verify ordering, backpressure, and clean termination. If not required, record the exclusion with reasoning tied to the EDASES control-flow evidence. |
| **Durable operation whose lifetime exceeds the connection** *(conditional)* | An operation that continues (or can be queried) after the originating transport drops. | If durable operations are claimed as required, demonstrate: start operation → drop transport → reconnect → query status → retrieve result. If not required, record the exclusion with reasoning. |

#### 5.6.2 Transport selection

* Use the **simplest representative transport(s)** that can evidence each property. A single transport that covers all required properties is acceptable; multiple transports are acceptable if that reduces incidental complexity.
* `stdio` may be used only as a **baseline** transport. Any property validated only on `stdio` must be flagged as `stdio-only` and not claimed for remote transports without a separate remote validation.
* At least one transport under test must exercise a **true remote / cross-process** boundary (not loopback-optimized stdio) for the `remote execution`, `connection loss`, and `reconnect` properties.

#### 5.6.3 Harness

* Each property test is an independent script under `research/capability-schema-validation/tests/test-e/`.
* Each script logs `{property, transport, iterations, pass/fail per iteration, latency, error_code, notes}`.
* Orphan-process checks are mandatory after `connection loss` and `reconnect` tests (per the catalog-scale finding that `toolregistry 0.15.0 / mcp 2.0.0` orphans without explicit close — see §2).

**Output:**

* `research/capability-schema-validation/tests/test-e/protocol.md`
* `research/capability-schema-validation/tests/test-e/results.md` (per-property pass/fail matrix)
* Raw logs under `research/capability-schema-validation/logs/test-e/`

---

## 6. Token / Accuracy Measurement Plan

This plan applies to Test A (§5.2) and is referenced by the final synthesis.

### 6.1 Token measurement

* Tokenizer: record the exact tokenizer name and version used (e.g., `tiktoken cl100k_base 0.6.0` or the model API's reported `usage.prompt_tokens`). Token counts without a named tokenizer version are not accepted.
* Scope: measure the **capability-description block only** (the tool/capability listing injected into the model context), not the full prompt, so that A/B/C deltas are isolated from task-prompt variance.
* Report both characters and tokens; report `tokens(C)/tokens(A)` and `tokens(B)/tokens(A)` ratios.

### 6.2 Accuracy measurement

* **Capability selection accuracy** — `correct_capability_selected / total_calls`. Per-task and aggregate.
* **Argument correctness** — `calls_with_all_arguments_correct / total_calls`. Correctness is judged against the **authoritative schema**, not the minimal description.
* **Invalid-call rate** — `rejected_by_runtime / total_calls`.
* **Recovery rate** — `successful_retry_after_rejection / total_rejections` (from Test B's typed-error harness; reported jointly with Test A deltas).

### 6.3 Pre-registration

Before running, record in `research/capability-schema-validation/tests/test-a/protocol.md`:

* Accuracy tolerance that defines "C preserves accuracy" (e.g., within 5pp of A on both selection and argument correctness).
* Minimum repetition count and token-measurement method.
* Any task that is expected to be variant-sensitive and why. These expectations are not used to exclude results post hoc — they are predictions to be checked.

### 6.4 Reporting shape

Produce a token/accuracy curve: x-axis = tokens (or compression ratio vs. A), y-axis = selection accuracy and argument accuracy. Mark variants A/B/C as points. The curve — not a single "accuracy is X%" claim — is the primary deliverable for the token/accuracy question.

---

## 7. Runtime Validation Harness

### 7.1 Architecture

```text
model (sees variant C only)
  │
  │  capability call {op_id, arguments}
  ▼
sandbox (preselected surface gate — checks op_id ∈ allowed set)
  │
  ▼
runtime validation boundary (authoritative schema — JSON Schema / Lexicon)
  │  ├─ schema validation (types, required, enums, patterns, constraints)
  │  ├─ version check (payload version ≡ authoritative version for drift tests)
  │  └─ typed error construction {code, field?, constraint?, got?, version?}
  ▼
policy boundary (deny-list / role check — only reached if schema validation passed)
  │
  ▼
execution (only reached if both boundaries passed)
```

### 7.2 Requirements

* The harness is a standalone runnable artifact under `research/capability-schema-validation/harness/`.
* Every call is logged with `{op_id, arguments, validation_result, error_code, executed, latency_ms, version}`.
* The harness asserts `executed == false` for every expected-rejection case — execution of an invalid call is a blocking failure, not a log entry.
* Error-code taxonomy is defined once in `research/capability-schema-validation/harness/error-codes.md` and reused by Tests B/C/D/E. Error codes must distinguish at minimum: `ValidationFailed`, `UnknownOperation`, `PolicyDenied`, `VersionMismatch`, `Timeout`, `Cancelled`, `ConnectionLost`.
* The sandbox and runtime may be collocated for Tests A-D, but the harness must log the validation ordering (sandbox gate → schema validation → policy → execution) so that boundary separation is auditable. For Test E's `remote execution` check, collocation is explicitly disallowed.

### 7.3 What the harness must NOT do

* Must not silently reshape, coerce, or retry calls before runtime validation sees them (control violation — see §5.1).
* Must not expose authoritative schema text to the model path (the exposure check in Test B §5.3 would then be tautologically failed).

---

## 8. Report Outline (10 sections)

The final synthesis at `research/capability-schema-validation/report.md` MUST contain exactly these 10 sections, in order. No synthesis is complete until all 10 are present.

1. **Test setup** — capability set, task set, variants, harness, repetition counts, tokenizer, model(s) and versions, runtime versions, transport(s) under test. Enough detail to reproduce.
2. **Results** — per-test results (A-E) in the order defined in §5, with per-variant and per-property tables. Raw counts, not only percentages.
3. **Measured token/accuracy relationship** — the token/accuracy curve from §6.4, with `tokens(C)/tokens(A)` ratio and accuracy deltas vs. pre-registered tolerances.
4. **Runtime-validation findings** — Test B synthesis: which malformation classes were caught, whether any reached execution, error-identity preservation, recovery rates, and whether validation information had to be exposed to the model.
5. **Schema/version findings** — Test C synthesis: behavior per drift case (C1-C4), version-check efficacy, whether stable operation IDs + version checks provide a clean failure mode, any residual gaps requiring host-internal changes (analogous to the retry-classification gaps in prior work).
6. **Transport findings** — Test E synthesis: per-property pass/fail matrix, which transports were used, `stdio-only` qualifications, whether durable/streaming operations are required by the EDASES boundary, and what minimum transport semantics are actually required.
7. **Claims supported** — enumerated claims from §1.4 that the evidence supports, with the specific test rows that support each claim and the certainty level (`evidence-based` vs. `proven` per AGENTS.md Reasoning Certainty).
8. **Claims falsified / modified** — enumerated claims that the evidence contradicts or narrows, with the specific failing rows and the modified claim wording.
9. **Remaining uncertainties** — explicitly list what was **not** tested, what was tested only on `stdio`, what version-bound caveats apply (`toolregistry 0.15.0 / mcp 2.0.0` etc.), and what `WHAT-NOT-TESTED` disclosures remain per AGENTS.md.
10. **Explicit recommendation for which findings should feed the RPC research** — which results warrant incorporation into the RPC / Lexicon research track, which do not, and why. Include the Lexicon-not-adopted branch: which separation findings remain useful even if Lexicon/XRPC is not adopted.

Each findings section (3-6) must include a `WHAT-NOT-TESTED` disclosure per AGENTS.md — the sharpest check against false confidence.

---

## 9. Retired Scope — Explicitly Excluded

The following are **out of scope** for this investigation unless a new architectural reason emerges that is directly tied to one of the seven gating questions (§1.4). Any proposal to reintroduce retired scope must be logged as an intervention with trigger and justification, and reviewed before work proceeds.

* MCP idle-timeout / pooling behavior.
* Eager-vs-lazy MCP process matrices.
* `ToolRegistry` C2 fleet frequency.
* `ToolRegistry` private-internal extensions.
* MCP-specific rolling-upgrade behavior.
* Any re-derivation of the old `ToolRegistry` lifecycle prototype beyond the narrow reuse permitted in §2 and §5.4.

The absence of these topics from the final synthesis is a **scoping decision**, not an omission — the synthesis must state that they were retired and why.

---

## 10. File Layout

All research artifacts live under `research/capability-schema-validation/`. No artifacts are committed under `/tmp`.

```text
research/capability-schema-validation/
├── README.md                          # Index + reproduction entry point
├── capabilities/
│   ├── authoritative/
│   │   └── schemas.json               # Full runtime schemas (canonical)
│   ├── derived/
│   │   ├── variant-a.json             # Full schema per §4
│   │   ├── variant-b.json             # Short desc + names/types
│   │   └── variant-c.json             # Stable ID + one-line + names/types
│   └── manifest.json                  # {capabilities, version, derived_from}
├── harness/
│   ├── README.md                      # How to run the harness
│   ├── error-codes.md                 # Typed error taxonomy (see §7.2)
│   ├── sandbox.py                     # Preselected-surface gate
│   ├── runtime.py                     # Authoritative validation + dispatch
│   └── run.py                         # CLI entry point for ad-hoc calls
├── tests/
│   ├── test-a/
│   │   ├── protocol.md                # Pre-registered protocol + thresholds
│   │   └── results.md                 # Per-variant tables
│   ├── test-b/
│   │   ├── protocol.md
│   │   └── results.md
│   ├── test-c/
│   │   ├── protocol.md
│   │   ├── results.md
│   │   └── schemas/
│   │       ├── c1/                    # Compatible additive mutation
│   │       ├── c2/                    # Incompatible param mutation
│   │       ├── c3/                    # Incompatible output mutation
│   │       └── c4/                    # Removal / renaming
│   ├── test-d/
│   │   ├── protocol.md
│   │   └── results.md
│   └── test-e/
│       ├── protocol.md
│       ├── results.md
│       └── scripts/                   # Per-property scripts (concurrent, loss, etc.)
├── logs/
│   ├── test-a/
│   ├── test-b/
│   ├── test-c/
│   ├── test-d/
│   └── test-e/
└── report.md                          # Final 10-section synthesis (§8)
```

---

## 11. Swarm Phases

Execution is a **four-phase swarm** with strict ordering and gate criteria. No phase may begin until the gate for the prior phase has passed.

### Phase 0 — Setup (serial, blocks everything)

**Goal:** Lay the invariant artifacts that every subsequent phase depends on.

**Work:**

* Author the capability set (§3) with full authoritative schemas and version field.
* Derive variants A/B/C (§4) and the manifest.
* Define the error-code taxonomy (`harness/error-codes.md`).
* Implement the harness (`harness/sandbox.py`, `harness/runtime.py`, `harness/run.py`) with execution-gate assertions.
* Author the fixed task set and record pre-registered thresholds (tolerances, repetition counts, tokenizer choice) in `tests/test-a/protocol.md`.
* Create the directory layout per §10 and a `README.md` reproduction entry point.

**Gate to Phase 1:** Capability set covers all six categories (10-20 ops) with version field; variants A/B/C generated and checked in; harness runs `valid calls → execute` and `malformed calls → rejected before execution` on a smoke-task; error taxonomy committed; task set + pre-registered thresholds committed.

**Artifacts:** `capabilities/**`, `harness/**`, `tests/test-a/protocol.md` (pre-registered), `README.md`.

---

### Phase 1 — Parallel Tests A-D (four-way fan-out, depends on Phase 0 gate)

Four independent tracks run in parallel. Each track owns its test directory and its log directory; no cross-track file writes.

| Track | Test | Depends on | Owns |
|---|---|---|---|
| Track A | Test A (§5.2) — Minimal descriptions + token/accuracy | Phase 0 | `tests/test-a/`, `logs/test-a/` |
| Track B | Test B (§5.3) — Authoritative runtime validation | Phase 0 | `tests/test-b/`, `logs/test-b/` |
| Track C | Test C (§5.4) — Schema drift / versioning | Phase 0 | `tests/test-c/`, `logs/test-c/` |
| Track D | Test D (§5.5) — Capability / authority separation | Phase 0 | `tests/test-d/`, `logs/test-d/` |

**Per-track requirements:**

* Follow the protocol in the corresponding §5 section verbatim; any deviation is logged as a finding, not silently corrected.
* Each track writes `protocol.md` (if not already pre-registered) and `results.md` with per-row tables and `WHAT-NOT-TESTED` disclosures.
* Each track runs the cheapest discriminating test first within its scope and records the result before committing to expensive repetitions.
* No track may import or depend on another track's `results.md` — the synthesis (Phase 3) is the sole integration point.

**Gate to Phase 2:** All four tracks have `protocol.md` + `results.md` + raw logs committed; no track has a blocking failure that is unrecorded (blocking failures are findings, not reasons to withhold commit).

---

### Phase 2 — Transport (Test E, depends on Phase 1 gate)

**Goal:** Establish the minimum transport semantics required by the EDASES control boundary (§5.6).

**Work:**

* For each property in the §5.6.1 table, run the minimal test with the simplest representative transport(s).
* Apply the `stdio-only` qualification rule (§5.6.2) — any property validated only on `stdio` is flagged as such and not claimed for remote transports.
* Run orphan-process checks after `connection loss` and `reconnect` tests.
* Record the inclusion/exclusion reasoning for conditional properties (streaming, durable operations).

**Gate to Phase 3:** `tests/test-e/protocol.md` + `results.md` (per-property pass/fail matrix) + raw logs committed; `stdio-only` qualifications applied where needed; orphan checks recorded.

---

### Phase 3 — Synthesis (depends on Phase 2 gate)

**Goal:** Produce the single concise 10-section report per §8.

**Work:**

* Synthesize per-test results into §§2-6 of the report, preserving the token/accuracy curve, error-identity findings, drift findings, and per-property transport matrix.
* Derive §§7-10: claims supported, claims falsified/modified, remaining uncertainties (with `WHAT-NOT-TESTED`), and explicit RPC-feed recommendation (including the Lexicon-not-adopted branch).
* Apply AGENTS.md Reasoning Certainty to every claim that crosses a role boundary: state WHY, WHAT (basis), HOW CERTAIN (guess / evidence-based / proven), and WHAT-NOT-TESTED.
* Ensure the report records retired scope (§9) and does not reintroduce it.

**Output:** `research/capability-schema-validation/report.md` — the only artifact that is consumed downstream. All other phase outputs are evidence, not conclusions.

---

## 12. Model Routing and Fallback Chains

Model selection is operator-gated and mechanically enforced (AGENTS.md §Model Discipline; `.crosslink/knowledge/model-discipline.md`). No launch may assume a model ID — verify live with `opencode models <provider>` before each launch. The fallback chains below are **ordered preferences**, not automatic fallbacks — each fallback requires a fresh operator approval comment on the active issue before retry.

| Role / phase | Primary (free-tier, where permitted) | First fallback (paid Go) | Second fallback / auditor |
|---|---|---|---|
| Phase 0 Setup (builder) | `opencode/muse-spark-1.2-contributor-free` | `opencode-go/muse-spark-1.2-contributor` | — |
| Phase 1 Tracks A-D (builder, parallel) | `opencode/muse-spark-1.2-contributor-free` | `opencode-go/muse-spark-1.2-contributor` | — |
| Phase 2 Transport E (builder) | `opencode/muse-spark-1.2-contributor-free` | `opencode-go/muse-spark-1.2-contributor` | — |
| Phase 3 Synthesis (builder) | `opencode/muse-spark-1.2-contributor-free` | `opencode-go/muse-spark-1.2-contributor` | — |
| Reviewer (per-track, pre-consumption audit) | `opencode/hy3-1.2-reviewer-free` | `opencode-go/hy3-1.2-reviewer` | — |
| Auditor (one-role / two-phase, in-flight divergence verifier) | `opencode-go/big-pickle-1.2-auditor` | `opencode/mimo-1.2-auditor-free` | `opencode-go/minimax-m3-1.2-auditor` |

**Rules:**

* Do **not** use free-tier (Zen) models for kickoff/swarm agents where rate limits have caused failures — the `opencode-go/*` fallback is the production path. Free-tier use is permitted only under auditor supervision per the 2026-08-23 operator override, and any 405 / `retry-after` / consent-gate signature in `opencode.log` triggers immediate fallback to the paid Go model from the same family.
* Model IDs must be copied exactly from `opencode models <provider>` output — never guessed, shortened, or modified.
* Each swarm launch (`crosslink kickoff run`, `crosslink swarm launch`) requires its **own** `--kind approval` comment from the operator containing the exact `--model` ID (enforced by `orchestrator-guard.ts`; block signature `AGENT LAUNCH BLOCK — Did your operator approve a model selection?`).

---

## 13. Resilience and Git Boundary

These constraints are non-negotiable for every phase. They exist to keep the swarm observable and to bound loss on stall/death.

### 13.1 Visibility

* No phase may be silent for >= 2 minutes. Post `crosslink issue comment <id> "[PROGRESS] state=... completed=... next=... blocker=..." --kind observation` at the milestone cadence from `agent-orchestration-playbook.md` §5.4 and **sync after posting** (`crosslink sync`). Session-action breadcrumbs (`crosslink session action "..."`) are supplementary telemetry only and do not reach the hub.
* Every launch must emit a visible signal within **45 seconds** of start (first checkpoint or log line). A launch that is silent past 45s is presumed stalled.

### 13.2 Streaming

* Invocations stream output; buffering the entire result until the end is not acceptable. The operator must be able to observe progress incrementally.

### 13.3 Strict git boundary (hard rule)

* All decision-gating artifacts (generated schemas, derived variants, harness code, protocols, results, logs — but not ephemeral `/tmp` caches) must be **committed to git** on the feature branch before the session ends. Nothing is left only in `/tmp`. Reconstructability from git alone is required (`agent-orchestration-playbook.md` §5.9; cf. #271).
* No `git push` / `merge` / `rebase` / `reset` / `clean` / `checkout .` / `restore .` / `stash` / `tag` / `am` / `apply` / `branch -d/-D/-m` — these are blocked by `crosslink-guard`. `git commit` is gated on an active Crosslink issue (`crosslink session work <id>` first).

### 13.4 Durability cadence (role-aware)

* **Builders:** commit incrementally every ~5 minutes of work — small, resume-friendly commits, so a death loses at most one commit's worth.
* **Reviewers/auditors (read-only roles):** treat `crosslink issue comment <id> "<position>" --kind observation && crosslink sync` as the durability write, at the same ~5-minute cadence.
* The ~4-comment cap is not a durability throttle — durability writes are not throttled; the ~5-minute budget is the bound.

### 13.5 Stall detection

* The watcher checks mechanical liveness; the **pre-positioned AUDITOR** (per `Workflow Topology Design and Reasoning Record.md` §Workflow Topology) verifies claim-vs-evidence divergence and flags the orchestrator; the **orchestrator** owns the bounded action set. The swarm design's job is to keep the position stream advancing — never to self-investigate staleness.

---

## 14. Verification Steps (Design-Level)

These are the checks the swarm operator and reviewer apply to determine whether the design has been faithfully executed. They are not the checks the tests themselves run.

1. **Design doc validity:** `rg --grep "TODO|FIXME|..." .design/capability-schema-validation.md` returns zero; all seven questions from §1.4 are traceable to at least one test section (A-E) with acceptance criteria; no retired scope (§9) appears in any protocol except as an explicit exclusion statement.
2. **Frontmatter validity:** `docs/standards/Documentation Standard.md` required fields present (`title`, `program`, `layer`, `document_type`, `status`, `authority`, `canonical_repository`, `depends_on`, `consumed_by`); `program == EDASES`, `layer == Research`, `document_type == Design`, `status == Draft`, `authority == Derived`; `depends_on` references only equal-or-higher abstraction layers (Research → no lower-layer depends).
3. **File layout:** `research/capability-schema-validation/` exists with the structure from §10; no research artifacts live under `/tmp` in any committed state.
4. **Harness gating:** the harness demonstrably rejects a malformed call before execution (`executed == false`) on a smoke test; error codes distinguish `ValidationFailed` from `PolicyDenied` from `UnknownOperation`.
5. **Variant integrity:** `variant-c.json` contains only stable IDs + one-line descriptions + names/types (+ enum literals) — no full constraint text, no error-schema bodies; `variant-a.json` round-trips the authoritative schema; token counts per §4.2 are recorded.
6. **Drift harness:** mutated schemas for C1-C4 exist under `tests/test-c/schemas/{c1,c2,c3,c4}/` and each case is tested independently; version field is checked at the validation boundary.
7. **Transport matrix:** `tests/test-e/results.md` contains the per-property pass/fail matrix from §5.6.1 with `stdio-only` qualifications applied; orphan-process checks are recorded after loss/reconnect tests.
8. **Synthesis completeness:** `research/capability-schema-validation/report.md` contains all 10 sections from §8 in order with `WHAT-NOT-TESTED` disclosures per AGENTS.md; claims in §§7-8 cite specific test rows and state certainty levels.
9. **Adversarial review:** reviewer findings (if any) are recorded on the working issue before the synthesis is considered consumed. The reviewer is a pre-consumption readiness audit (Workflow Topology), not a post-hoc gate.
10. **Git boundary:** `git log --oneline` shows incremental commits per phase (not a single end-of-work squash); `git status` after the final commit is clean of decision-gating artifacts; no artifact exists only in `/tmp`.

---

## 15. Reproduction Entry Point

From the repository root, after checking out the feature branch:

```bash
# 1. Inspect the harness
cat research/capability-schema-validation/harness/README.md
python research/capability-schema-validation/harness/run.py --help

# 2. Run a smoke validation
python research/capability-schema-validation/harness/run.py \
  --variant derived/variant-c.json \
  --smoke

# 3. Run per-test harnesses (each is independently runnable)
python research/capability-schema-validation/tests/test-a/run.py   # Test A
python research/capability-schema-validation/tests/test-b/run.py   # Test B
python research/capability-schema-validation/tests/test-c/run.py   # Test C
python research/capability-schema-validation/tests/test-d/run.py   # Test D
python research/capability-schema-validation/tests/test-e/run.py   # Test E (requires remote transport for full matrix)

# 4. Read the synthesis
cat research/capability-schema-validation/report.md
```

Exact commands are finalized in `research/capability-schema-validation/README.md` during Phase 0.

---

## 16. Intervention Triggers

Log an intervention (`crosslink issue intervene 498 "..." --trigger <type> --context "..."`) if any of the following occur:

* A gating question (§1.4) cannot be answered with the fixed capability set without reintroducing retired scope — trigger `scope`.
* The minimal description (variant C) cannot preserve accuracy within the pre-registered tolerance even after the cheapest augmentation (parameter names/types) — trigger `design`.
* Runtime validation cannot distinguish a drift case (C2-C4) from a generic malformed call — trigger `finding` (not a blocker; record as a gap analogous to the retry-classification residual gaps).
* A transport property required by the EDASES boundary cannot be demonstrated with any available transport — trigger `evidence`.
* Any blocked action (`git push`, `merge`, etc.) is required to proceed — trigger `policy` and report to the operator; do not loop on the block.

---

*End of design document. Swarm execution begins at Phase 0. The pre-positioned AUDITOR is the sole in-flight divergence verifier; the reviewer is the pre-consumption readiness audit before synthesis is consumed.*
