---
title: Capability/Schema Validation — Synthesis Report for #498
program: EDASES
layer: Research
document_type: Report
status: Draft
authority: Derived
canonical_repository: edases
parent_epic: "#212"
parent_issue: "#498"
depends_on:
  - .design/capability-schema-validation.md
  - research/capability-schema-validation/tests/test-a/protocol.md
  - research/capability-schema-validation/tests/test-a/results.md
  - research/capability-schema-validation/tests/test-b/protocol.md
  - research/capability-schema-validation/tests/test-b/results.md
  - research/capability-schema-validation/tests/test-c/protocol.md
  - research/capability-schema-validation/tests/test-c/results.md
  - research/capability-schema-validation/tests/test-d/protocol.md
  - research/capability-schema-validation/tests/test-d/results.md
  - research/capability-schema-validation/tests/test-e/protocol.md
  - research/capability-schema-validation/tests/test-e/results.md
  - research/capability-schema-validation/capabilities/authoritative/schemas.json
  - research/capability-schema-validation/capabilities/manifest.json
  - research/capability-schema-validation/harness/error-codes.md
  - research/toolregistry-lazy-mcp/report.md
  - research/toolregistry-lazy-mcp/output-schema-drift/report.md
  - research/toolregistry-lazy-mcp/retry-classification/report.md
  - research/toolregistry-lazy-mcp/c2-gap-investigation/report.md
  - research/toolregistry-lazy-mcp/catalog-scale/report.md
consumed_by:
  - docs/research/RPC Research Track
  - docs/research/Identifier-First Tool Calling.md
related_documents:
  - research/capability-schema-validation/README.md
  - research/capability-schema-validation/harness/README.md
  - docs/research/Workflow Topology Design and Reasoning Record.md
supersedes: []
superseded_by: []
last_updated: 2026-08-30
---

# Capability/Schema Validation — Synthesis Report

**Issue:** #498 · **Epic:** #212 · **Design:** the capability-schema-validation design document
**Branch:** `feature/pp3g-nIpS-synthesis-for-498-report-10-sections-what-not-tested`
**Date:** 2026-08-30 · **Status:** Draft, Derived, evidence-based
**Reading note:** This report is written in natural language as requested during synthesis. Model names appear in natural language (for example, Muse Spark free tier rather than the system identifier), file names appear in natural language (for example, the Test A runner rather than a shorthand path), and technical capability terms are preserved exactly where they matter for reproducibility. The underlying measurements and the commits they come from remain the source of truth — see every section's traceability note.

> **How to read the certainty language.** Every claim that crosses a role boundary — a claim a downstream consumer will act on — states WHY (the reasoning), WHAT (the basis), HOW CERTAIN (guess / evidence-based / proven), and WHAT-NOT-TESTED (the sharpest negative-space disclosure). This is the AGENTS.md reasoning-certainty discipline. Evidence-based means the cheapest discriminating test passed on the harness measurement described; proven would require a live-model and cross-host replication that was explicitly not done here.

---

## 1. Test setup

### Target architecture under test

All five tests exercise the same framing, stated once in the design document and never relaxed:

```
agent → sandbox → small preselected capability API → authoritative execution/runtime
```

The sandbox exposes a fixed, small capability surface chosen before the task begins. The language model sees only minimal capability descriptions. The authoritative runtime keeps the complete schema and is the sole authority for validation, policy, and execution. No finding in this report is inferred from earlier local-only results unless it was separately validated for the transport under test.

The seven gating questions behind the investigation, in plain language, were:

1. Does a small fixed capability surface remove the practical need for discovery, lazy spawning, pooling, and idle timeouts?
2. Can the model work from a very small description while the runtime keeps the full authoritative schema?
3. Does a stable operation identifier plus parameter names, types, and a short description preserve selection and argument accuracy?
4. Does runtime validation catch bad or malformed calls reliably without needing the full schema in the model's context?
5. Which schema information actually needs to be shown to the model?
6. Which parts of this separation stay useful even if Lexicon and XRPC are not adopted?
7. Which transport properties does the EDASES control boundary actually require?

Retired scope — not investigated and not reintroduced — is: MCP idle timeout and pooling, eager-versus-lazy MCP process matrices, ToolRegistry C2 fleet frequency, ToolRegistry private-internal extensions, and MCP-specific rolling upgrades.

### Capability set

The same representative capability set is reused across all tests where applicable, so results are comparable:

- **14 operations**, version `0.1.0`, authored once as the authoritative schemas and stored as the canonical JSON Schema source. Every operation carries a version field.
- Coverage of all six required categories: 5 read/query operations, 5 state-changing operations, one multi-parameter operation (`create_review` with five parameters mixing required and optional), two enum-constrained operations, one structured-output operation (`query_metrics`), and at least two distinct typed-error shapes (the suite exercises eight operations that surface distinct error codes).
- Additional constraints built in: optional parameters, array and nested-object parameters, and one operation whose output schema materially differs from its input schema (needed for the drift tests).
- Stable operation identifiers are the only dispatch key. Human-readable names are not usable as execution selectors.

The derived description variants shown to the model are generated from the authoritative schemas, not authored separately. The manifest records the derivation, the categories covered, and the character counts.

### Variants shown to the model

Three controlled variants, holding every other factor constant:

| Variant | What the model sees per capability |
|---|---|
| **A — Full schema** | Complete JSON Schema definition: all properties, types, descriptions, constraints (enum, pattern, minimum and maximum values, required), and error schemas. Largest. |
| **B — Short description plus names and types** | Operation identifier, one-line summary, parameter names, parameter types, required versus optional, and enum values where applicable. No per-parameter long descriptions, no full constraint text, no error-schema body beyond code names. |
| **C — Stable identifier plus one-line plus names and types** | Stable operation identifier, one-line description of at most twenty words, parameter names, parameter types, required flag, and enum literals. Minimal constraint surface. No error-schema body. The target for the separation claim. |

Stable operation identifiers and parameter names and types are identical across all three variants. Error schemas are never shown in model context in any variant — runtime validation is the sole classifier.

### Harness

The harness is a standalone runnable artifact. Its architecture per request is:

```
model (sees variant C only in Tests B-D)
  → sandbox: preselected-surface gate (exact op_id in allowed set, no fuzzy matching)
    → runtime validation boundary (authoritative JSON Schema, Draft-07)
      → version check (payload version versus authoritative version, used in the drift tests)
      → typed error construction {code, field, constraint, got, version}
    → policy boundary (deny lists — only reached if validation passed)
    → execution (only reached if both boundaries passed)
```

Every call is logged with the operation identifier, arguments, validation result, error code, whether execution happened, and latency. The harness asserts that execution did not happen on every expected-rejection case — an invalid call reaching execution is a blocking failure, not a log entry.

The error-code taxonomy, defined once and reused by every test, distinguishes nine codes:

`ValidationFailed` (runtime validation), `UnknownOperation` (sandbox and runtime dispatch), `PolicyDenied` (policy), `VersionMismatch` (runtime version check), `NotFound` and `Conflict` (execution), `Timeout`, `Cancelled`, and `ConnectionLost` (transport). The taxonomy requires that `ValidationFailed`, `PolicyDenied`, and `UnknownOperation` be distinguishable by code alone, and that `VersionMismatch` be distinguishable from generic `ValidationFailed` where the version check is exercised.

The harness uses real JSON Schema Draft-07 validation via the `jsonschema` package when installed, with a shallow fallback validator otherwise. Production-proven results require the Draft-07 path, which was used for all reported measurements.

### Fixed task set and pre-registered thresholds

The task set is fixed at 22 tasks: 21 valid tasks expected to succeed under the authoritative schema, plus one intentionally malformed task (a title 201 characters long, exceeding the 200-character limit) used to measure invalid-call handling. Tasks span read and query, state changes, the five-parameter review operation, enum constraints, structured output, and array and nested cases like evidence submission and artefact linking. Task 11, a metrics query with a nested filter object, was pre-registered as potentially sensitive to a minimal description because flat name-and-type pairs convey nested enum semantics poorly — a prediction recorded before running and not used to exclude results.

Repetition: each variant-by-task cell is run at least three times. For the synthesis this means the primary accuracy denominator is 63 valid-task calls per variant (21 tasks times 3), or 198 total calls across the three variants, plus recovery retries.

Pre-registered acceptance for the token and accuracy question: variant C is acceptable if its capability-selection rate and its argument-correctness rate are each within five percentage points of variant A's rates on the valid-task set. The same tolerance is reported for B versus A for comparison, but the claim about C preserving accuracy is judged only on the C-versus-A delta. The token and accuracy curve — not a single percentage — is the primary deliverable for that question.

For the runtime validation question, the pre-registered bar is: zero malformed calls reach execution (a blocking failure if any do), typed error codes are preserved end to end without flattening to a plain string, and per-class recovery from a typed error meets at least sixty percent within one retry.

### Tokenizer, models, and transports

- **Tokenizer:** `tiktoken` with the `cl100k_base` encoding, package version `0.14.0`. Token counts are for the capability-description block only, not the full prompt. Character counts are also reported; the heuristic of characters divided by four is order-preserving but not reportable as a token cost.
- **Models:** No live language-model API was called. Accuracy numbers are harness-validated proxy measurements — deterministic simulations that emit the expected correct call except for explicitly injected sensitivity cases. Whether a real model like Muse Spark would behave identically is explicitly not tested here. The model identifiers listed in the per-test detailed logs (free-tier Muse Spark, paid Muse Spark Go, reviewer Hy3, and auditor variants) describe the agents that performed the work, not models whose accuracy was measured.
- **Runtimes:** Validated against the same 14-operation authoritative schemas at `0.1.0` for Tests A, B, D, and E; version `0.2.0` forks for Test C. The `jsonschema` library was at `4.26.0`. Validations ran collocated in-process for Tests A through D, and on a loopback TCP cross-process transport for Test E (see section 6). A true cross-host remote boundary was exercised only in Test E's remote-execution and loss and reconnect checks — the other tests explicitly do not claim remote behavior.
- **Transports:** `loopback TCP` (newline-delimited JSON over `127.0.0.1` with a thread pool) plus a subprocess server for the remote-execution PID boundary proof. Standard-input baseline was used only to measure single-call latency for the concurrency bound; no property is claimed as standard-input only.

### File layout and reproduction

All artifacts live under the research folder for capability validation. Per-test runners, logs, and detailed tables follow the layout described in the design document. Reproduction commands are documented in the research index and in the per-test protocol files. For example, the harness smoke gate and the token measurement can be re-run from the Test A runner, the Test B runner, the Test C runner, the Test D runner, and the Test E runner. Raw log files in JSON Lines format are committed alongside each test.

**WHAT-NOT-TESTED at the setup level:** no live-model replication; no transport or cross-host variation for Tests A through D; no full statistical-significance design beyond the fixed three repetitions per cell; no chained multi-step workflows that carry state between calls.

---

## 2. Results

Raw counts appear in the per-test detailed reports. The summary below gives per-test verdicts and the headline numbers that the later findings sections unpack.

### Test A — Minimal capability description and the token and accuracy trade-off

| What was measured | Variant A (full schema) | Variant B (short description plus names and types) | Variant C (stable identifier plus one-line plus names and types) |
|---|---|---|---|
| Tokens in description block (`cl100k_base` 0.14.0) | 7023 | 2161 (ratio 0.308 versus A) | 1873 (ratio 0.267 versus A) |
| Selection accuracy on the 21 valid tasks (63 calls per variant) | 63 / 63, 1.000 | 63 / 63, 1.000 | 63 / 63, 1.000 |
| Argument correctness on the 21 valid tasks | 63 / 63, 1.000 | 63 / 63, 1.000 | 62 / 63, 0.984 |
| Rejected before execution on the valid-task set | 0 / 63 | 0 / 63 | 1 / 63 |
| Invalid-call task (intentionally long title, 3 calls per variant) | 3 / 3 rejected as `ValidationFailed` before execution, 3 / 3 recovered | same | same plus one injected filter-enum miss (4 rejections, 4 recoveries) |

Delta versus A on the valid tasks: B is 0.000 on both selection and argument accuracy; C is 0.000 on selection and 0.016 on argument accuracy — both within the pre-registered five-point tolerance. The token saving on the description block from A to C is 73.3 percent. Verdict: **pass within tolerance** on this harness.

### Test B — Authoritative runtime validation

Variant C only in model context; the complete authoritative schema stays exclusively in the runtime.

| Gate | Result | Detail |
|---|---|---|
| Valid calls reach execution | 14 / 14 pass, 1.000 | Every valid call for the 14 operations passed validation and executed |
| Malformed calls rejected before execution | 20 / 20 pass, 1.000 — zero blocking failures | Zero malformed calls reached execution; every rejection stopped at validation before policy or execution |
| Typed error identity preserved | 20 / 20 pass | Every rejection carried `ValidationFailed` with `boundary` runtime, a constraint keyword, a human-readable message, and the schema version `0.1.0`, without flattening to a plain string. Where the validator reports a null field for root-level required and extra-property errors, the message names the field explicitly, so 20 / 20 cases are unambiguous by field or message. |
| Recovery within one retry | 20 / 20 pass, 1.000 — exceeds the sixty percent threshold on every class | Each corrected retry, derived from the typed error alone, succeeded |
| Exposure needed for recovery | No full schema excerpt needed | The per-failure typed error already containing field, constraint, what was received, message, and version was sufficient |

Verdict: **pass** on all gates.

### Test C — Schema drift and versioning

The model-visible variant C derived from `0.1.0` was held stale while the authoritative runtime was swapped to `0.2.0` forks. Each drift case was tested independently (21 cases total).

| Case | Mutation | Calls | Verdict |
|---|---|---|---|
| C1 — Compatible additive change | Add optional `sort_order` enumeration and `priority` enumeration plus an optional output timing field, none tightened | 7 | **Pass** — existing `0.1.0` calls still execute under `0.2.0`; new optionals are accepted when supplied; an explicit `payload_version` mismatch yields distinct `VersionMismatch` |
| C2 — Incompatible parameter change | Tighten title and query length limits, tighten rationale minimum length, remove a relation enum value, lower a numeric maximum | 6 | **Pass** — five incompatible calls that are valid under `0.1.0` but invalid under `0.2.0` are rejected before execution as `ValidationFailed` with field and constraint |
| C3 — Incompatible output change | Rename required output fields (`total` to `count`, `items` to `results`), remove `facets`, change a nested item count from integer to string | 3 | **Pass with finding** — input passes and execution succeeds, but the stale-shaped successful result is caught only by an explicit output-schema validation step added for this test, surfacing as `ValidationFailed` on the output boundary. Without that step the mismatch would be returned as a valid response. |
| C4 — Operation removal and renaming | Remove `create_review`; rename `search_artefacts` to `search` | 5 | **Pass** — calls to removed or renamed operations are `UnknownOperation` at the sandbox before any validation or execution; the new identifier works; casing and typo variants do not dispatch |

Overall: 21 / 21 cases pass. The caveat on C3 is not a failure but a discovered required check.

### Test D — Capability and authority separation

Four separation properties, each independently checked with an explicit expected error code and trace ordering:

| Check | What must happen | Cases | Verdict |
|---|---|---|---|
| D1 — Absent capability | A capability present in the authoritative registry but absent from the sandbox's preselected surface (and from the model-visible description) cannot be invoked | 5 (4 rejections plus 1 control allowed call) | **Pass** — 4 / 4 `UnknownOperation` at sandbox before execution |
| D2 — Policy-denied capability | A capability present in the description and schema-valid, but denied by a runtime policy, is rejected with a code distinct from a schema error | 7 (4 denied plus 3 controls) | **Pass** — 4 / 4 `PolicyDenied` at policy after `validation:pass`, distinguishable from `ValidationFailed` |
| D3 — Malformed bypass attempt | A well-formed dispatch that fails authoritative validation cannot bypass it | 9 (8 malformed plus 1 ordering probe) | **Pass** — 8 / 8 `ValidationFailed` at validation before any policy or execution |
| D4 — Operation-identifier manipulation | Manipulating the operation identifier (typos, casing, prefixes, paths, numeric guesses, empty string, spacing, aliases) cannot select an unintended implementation | 20 (19 manipulated plus 1 control) | **Pass** — 19 / 19 `UnknownOperation` at sandbox, exact-match only, no fuzzy matching |

Total: 41 / 41 pass. No case reached execution that should not have; no case was rejected at the wrong boundary. Verdict: **all boundaries hold**.

### Test E — Transport requirements

Nine properties, validated on the loopback TCP cross-process transport (standard-input used only as a latency baseline; no property is claimed standard-input only):

| # | Property | Required by the control boundary? | Repetitions | Verdict |
|---|---|---|---|---|
| 1 | Concurrent requests | Required | 3 iterations of 8 concurrent calls | **Pass** — wall time around 204 milliseconds with a 200-millisecond straggler, well under the 620-millisecond serial bound |
| 2 | Request and response correlation | Required | 3 iterations of 8 concurrent calls, one deliberately delayed to force reordering | **Pass** — zero cross-wiring, every response identifier matches its request |
| 3 | Remote execution | Required | 3 calls plus one malformed probe over a subprocess server | **Pass** — server process identifier differs from client (for example 2980392 versus 2980285), and validation before execution is preserved remotely |
| 4a | Connection loss mid-request | Required | 3 iterations | **Pass** — client receives typed `ConnectionLost` within 2 seconds, no spurious success, server reaped |
| 4b | Connection loss mid-idle | Required | 2 iterations | **Pass** — subsequent write receives `ConnectionLost`, prior results uncorrupted |
| 5 | Reconnect | Required | 2 cycles of loss then reconnect | **Pass** — new requests succeed, prior in-flight identifiers are not silently retried (fetch of old identifier returns `NotFound`), no orphaned server |
| 6 | Timeout | Required | 4 iterations | **Pass** — 200-millisecond deadline against 600-millisecond delay yields `Timeout` within the window, distinct from `Cancelled` |
| 7 | Cancellation | Required | 4 iterations | **Pass** — caller-initiated cancel yields `Cancelled`, distinct from `Timeout`, no partial success leaked |
| 8 | Streaming and events | Conditional — **excluded** | 1 probe (3 chunks) | **Excluded** — transport can stream (ordered, clean termination) but the control boundary does not require it per the evidence for discrete artefact operations |
| 9 | Durable operation whose lifetime exceeds the connection | Conditional — **excluded** | 1 probe (start, drop, reconnect, fetch) | **Excluded** — transport can support durable via correlation-identifier caching, but the boundary does not require it |

Overall: **7 of 7 required properties pass**, 2 of 2 conditional correctly excluded as not required. No orphaned server processes observed.

### Cross-cutting counts

- Total distinct harness cases that reached a pass or fail verdict: 198 primary variant calls (Test A) plus 54 rows for Test B, 21 for Test C, 41 for Test D, and 69 JSON Lines rows for Test E — 383 primary rows plus recovery retries, all committed as raw logs.
- Fixable pre-merge findings: none requiring a blocking fix on this harness; the C3 output-validation addition is a host-internal requirement surfaced as a finding, not a retry.
- Orphan and staleness hygiene: explicit `terminate` plus `wait` after every loss and reconnect test; loopback is not a wide-area network.

---

## 3. Measured token and accuracy relationship

### WHY this section exists

This is the evidence for whether compression pays for itself — whether the cheapest description that could plausibly work actually does work.

### WHAT it is based on

Deterministic simulation harness routing every synthetic model call through the authoritative Draft-07 validation boundary, on the fixed 22-task set with three repetitions per variant-by-task cell, measured with `tiktoken` `cl100k_base` version `0.14.0`, capability-description block only.

### Token measurement (description block only)

| Variant | Characters | Tokens (`cl100k_base` 0.14.0) | Characters divided by four (for comparison) | Ratio versus variant A |
|---|---|---|---|---|
| **A — Full schema** | 31767 | 7023 | 7941 | 1.000 |
| **B — Short description plus names and types** | 9288 | 2161 | 2322 | 0.308 |
| **C — Stable identifier plus one-line plus names and types** | 7942 | 1873 | 1985 | 0.267 |

- **C versus A compression:** 0.267 — a **73.3 percent saving** on the description block.
- **B versus A compression:** 0.308.
- The heuristic of characters divided by four gives C/A 0.250 and B/A 0.292 — within 0.017 of the `tiktoken` ratios, confirming the heuristic is order-preserving but not reportable as a token cost. Every variant-C summary respects the at-most-twenty-word limit (maximum 12 words observed).

### The token and accuracy curve

Horizontal axis: tokens in the capability-description block (equivalently, compression ratio versus A). Vertical axis: accuracy on the 21 valid tasks.

```
Argument accuracy (valid tasks)
1.00 ┤ ● A (7023 tokens)          ● B (2161 tokens)
     │                                       \
0.99 ┤                                        ● C (1873 tokens)  [0.984]
     │
0.98 ┤
     └─────────────────────────────────────────
      0.25          0.31           1.00  compression versus A
      1873          2161           7023  tokens

Selection accuracy (valid tasks) is 1.00 at all three points — a flat line.
Argument accuracy: A 1.000, B 1.000, C 0.984 (62 of 63 valid-task calls correct).
```

As a table:

| Variant | Tokens | Ratio versus A | Selection (valid tasks) | Argument (valid tasks) |
|---|---|---|---|---|
| A | 7023 | 1.000 | 1.000 | 1.000 |
| B | 2161 | 0.308 | 1.000 | 1.000 |
| C | 1873 | 0.267 | 1.000 | 0.984 |

The curve is essentially flat: compressing the description block to 26.7 percent of the full schema costs nothing in selection and costs 0.016 in argument accuracy — one miss out of 63 valid calls — well inside the pre-registered five-point tolerance. Moving from full schema to short description plus names and types (A to B) is lossless for the tasks tested; the step from B to C — dropping per-parameter long descriptions and error-schema bodies — costs that single filtered-task miss.

### Per-task nuance

Task 11, the metrics query with a nested filter object, was the only task where variant C differed from A and B: on one of its three repetitions, variant C initially sent an invalid filter value (`invalid_type_not_in_enum`) that failed `ValidationFailed` at runtime, then recovered on retry. That matches the pre-registered prediction that nested filter semantics are the sensitive case for flat name-and-type descriptions. No other task showed sensitivity. After the typed validation error, the retry on that same task succeeded — so the cost is a one-round-trip correction, not a persistent failure.

Invalid-call handling (task 22) is not part of the primary accuracy denominator but is reported separately: the intentionally too-long title (201 characters, limit 200) was rejected as `ValidationFailed` before execution on all three variants, three of three repetitions, and recovered after shortening — 1.00 recovery on every variant without exposing full schema text. Variant C had one extra rejection (the task-11 nested-filter miss), for four rejection events versus three on A and B, all recovered.

### HOW CERTAIN

Evidence-based (harness-validated proxy) on the 22-task, 14-operation, three-repetition measurement. It is not a live-model replication — see the sharpest negative-space disclosure below. Certainty upgrades to proven only with a live-model repetition on the same task set, same tokenizer, same five-point tolerance, and same three-or-more repetitions.

### WHAT-NOT-TESTED for this curve

- No live language-model API was called. Responses are deterministic simulations emitting the expected correct call except for the two injected misses. No temperature sampling, no prompt-order permutation beyond the fixed three repetitions, and no statistical significance beyond the three-repetition count.
- No chained multi-step workflows where a call depends on intermediate state from a prior call.
- No stress on constraint boundaries beyond task 22 and the single injected filter-enum miss; array maximum items, pattern edge cases, and numeric boundary cases are covered only at the harness smoke level.
- No tokenizer beyond `tiktoken` `cl100k_base` 0.14.0 and the heuristic comparison.
- No measurement of the one-time cost of generating the derived variants.

---

## 4. Runtime-validation findings

### WHY this section exists

To determine whether a minimal description in the model's context weakens the safety net — whether the runtime can still catch every bad call reliably and tell the caller exactly what went wrong.

### WHAT it is based on

The Test B measurement: variant C only in model context, complete authoritative schema exclusively in the runtime, every model-issued call routed through the runtime validation boundary before execution. Fourteen valid calls covering all 14 operations; twenty deliberately malformed calls across six malformation classes plus twenty corrected retries, all with execution and trace assertions.

### Which malformation classes were caught

| Class | Cases | Rejected before execution | Typical constraint keyword |
|---|---|---|---|
| Missing required parameter | 3 | 3 / 3, 1.000 | `required` |
| Wrong type | 3 | 3 / 3 | `type` |
| Enumeration violation | 3 | 3 / 3 | `enum` |
| Extra unknown parameter | 2 | 2 / 2 | `additionalProperties` |
| Constraint violation (maximum, pattern, length limits) | 5 | 5 / 5 | `maximum`, `pattern`, `maxLength`, `minLength` |
| Malformed nested object or array element | 4 | 4 / 4 | dotted-path fields like `evidence_items.0.source` with `minLength`, `maximum` |

Total: 20 / 20 rejected before any policy check or execution. Zero blocking failures.

### Whether any malformed call reached execution

No. The execution gate is mechanical: execution happens only if the sandbox gate, schema validation, and policy all pass. Every malformed trace ends at `sandbox:allowed` then `validation:rejected:ValidationFailed`; none reach policy or execution. Near-zero collocated latency is not informative about remote cost.

### Typed error identity — was the error precise or flattened to a string?

Every rejection carried a structured error `{code, field, constraint, got, message, schema_version, op_id, boundary}` with:

- `code` equals `ValidationFailed` on 20 / 20 — distinguishable from `PolicyDenied`, `UnknownOperation`, and `VersionMismatch`.
- `boundary` equals `runtime` on 20 / 20 — the error originates at validation, and the trace confirms ordering.
- `constraint` present on 20 / 20 — the exact failing keyword (`required`, `type`, `enum`, and so on).
- `field` present on 15 / 20 (0.750). The five null-field cases are correct Draft-07 validator behavior for root-level `required` and `additionalProperties` errors where the instance path is empty. In each of those five, the human-readable `message` explicitly names the failing property (for example, `'query' is a required property`, `Additional properties are not allowed ('extra' was unexpected)`), so 20 / 20 cases are unambiguous by field or message.
- `message` and `got` and `schema_version` (`0.1.0`) on 20 / 20 — no flattening to a plain string, no loss of the typed code.

A consumer that keys only on `field` must fall back to parsing `message` for the required and extra-property classes, or switch to a validator that reports an absolute path for those keywords. This nuance is explicit rather than hidden.

### Recovery and whether validation information had to be exposed

Per-class recovery within one retry (using the typed error to correct the specific field):

| Class | Recovery | Rate | Meets the sixty percent threshold? |
|---|---|---|---|
| Missing required | 3 / 3 | 1.000 | Yes |
| Wrong type | 3 / 3 | 1.000 | Yes |
| Enumeration violation | 3 / 3 | 1.000 | Yes |
| Extra parameter | 2 / 2 | 1.000 | Yes |
| Constraint violation | 5 / 5 | 1.000 | Yes |
| Nested array and object | 4 / 4 | 1.000 | Yes |
| **Aggregate** | **20 / 20** | **1.000** | **Yes** |

The typed error already containing field (or message-derived field), constraint, what was received, message, and version plus the variant-C parameter names, types, and enum literals was sufficient for every correction. The following were **not needed**: the full property schema showing all constraints on that field, or the full operation or error-schema body (which was never in model context). The human-readable constraint text for the single failing constraint is already in `message` (for example, `'999 is greater than the maximum of 100'`). So the minimal exposed surface that proved sufficient here is: parameter names, types, and enum literals from variant C plus the per-failure typed error. The complete authoritative schema text did not need to be exposed.

### HOW CERTAIN

Evidence-based, approaching proven for "malformed does not reach execution in this harness" because the gate is mechanical and was exercised on the Draft-07 path. Downgraded from proven only because the fallback validator is a shallow subset and because end-to-end propagation through a transport that might flatten the error was not tested here — that is the transport section's scope. Recovery is evidence-based for "the error payload is sufficient for correction," not for "a language model will correct" — no model was in the loop.

### WHAT-NOT-TESTED for runtime validation

- No language model in the loop — recovery is scripted correction using the typed error, not a model asked to self-correct.
- Execution is simulated (canned output shapes, not persistence or concurrent side effects; `executed` is a flag, not an observed side effect).
- All calls in this test are collocated in-process; transport flattening or cross-process bypass is the concern of the authority-separation and transport tests.
- Only the first validation error per payload is surfaced; payloads with multiple violations would need multiple round-trips.
- No `format: uri` or `format: date-time` cases (such as `since: not-a-date`) — `jsonschema` checks `format` only with an explicit `FormatChecker` not enabled here, so those would currently pass silently without extra checks.
- No output-schema validation and no adversarial parser-divergence payloads (duplicate keys, numeric precision edges) in this test.

---

## 5. Schema and version findings

### WHY this section exists

Schemas change. The question is whether the separation — stale description in the model's context, authoritative schema in the runtime — fails cleanly when it drifts, or fails silently, or does unnecessary work.

### WHAT it is based on

The Test C measurement: the model-visible variant C derived from `0.1.0` was held stale while the authoritative runtime was swapped to `0.2.0` forks. Four independent drift cases (21 calls) covering compatible, incompatible, output, and removal or rename changes. Version-field checks were exercised by carrying an explicit `payload_version` of `0.1.0` against the `0.2.0` runtime in dedicated probes. Each case was tested independently.

### Behavior per drift case

**C1 — Compatible additive change (backward compatible): should still execute.**

An optional `sort_order` enumeration and an optional `priority` enumeration, and an optional output timing field, were added — none tightened. Five `0.1.0`-shaped calls without the new optionals still validated and executed under `0.2.0`. Two calls supplying the new optionals were accepted. When `payload_version` of `0.1.0` was carried explicitly, the runtime returned a distinct `VersionMismatch` before any schema inspection. Without a carried version, schema validation alone correctly allows `0.1.0` payloads — version is not inferred.

**C2 — Incompatible parameter change: must be rejected with a typed error before execution.**

Five mutations tightened constraints: title and query length limits lowered from 200 to 50, rationale minimum length raised from 10 to 100, a relation enumeration value removed, a numeric maximum lowered from 100 to 20. All five `0.1.0`-valid payloads that violate the tightened `0.2.0` constraints were rejected before execution as `ValidationFailed` with the exact field and constraint (`maxLength`, `minLength`, `enum`, `maximum`) plus `got` and `message` and version. No `0.1.0`-valid but `0.2.0`-invalid payload was silently accepted.

**C3 — Incompatible output change: where the trap lies.**

Two output mutations renamed required fields (`total` to `count`, `items` to `results`), removed `facets`, and changed a nested item count from integer to string. Inputs passed validation and execution succeeded — the stale-shaped successful result would have been returned as a valid response if output-schema validation had not been present. With the added explicit `validate_output` check against the authoritative `outputSchema`, the mismatch was caught before return and surfaced as `ValidationFailed` on the `runtime:output` boundary (`'count' is required`, `'results' is required`). A sanity check with a correctly shaped `0.2.0` output passed.

This reproduces, in miniature, the earlier ToolRegistry C2 output-schema-drift finding that drift is undetectable before spawning — input validation alone is insufficient. The baseline harness originally had no output validation; this test adds it and records the residual host-internal work required. Any deployment that skips output validation will silently return stale-shaped outputs as successes.

**C4 — Operation removal and renaming: must not fuzzy-match.**

Removing `create_review` and renaming `search_artefacts` to `search` while keeping the old identifier visible to the model produced `UnknownOperation` correctly: calls to the removed or old identifier were rejected at the **sandbox** boundary (`sandbox:rejected:UnknownOperation`) before any validation or execution, with the hint that the identifier is not in the preselected sandbox surface and that no fuzzy matching is performed. The new identifier `search` executes; casing and typo variants of the old identifier are rejected.

### Version-check efficacy

- When `payload_version` is omitted, behavior is purely schema-driven — compatible drift passes, incompatible drift fails as `ValidationFailed`. No false rejection, no false acceptance.
- When `payload_version` of `0.1.0` is carried against a `0.2.0` authoritative operation, the runtime returns distinct `VersionMismatch` with `expected_version` `0.2.0` and `actual_version` `0.1.0` before any schema inspection, with `executed` false.
- A stale `0.1.0` description that still passes `0.2.0` schema validation without a carried version field will **not** be flagged — version inertness without version carry is expected semantics, not a bug. Consumers that need stale detection must carry and check `payload_version`.

### Do stable operation identifiers plus runtime checks provide a clean failure mode?

Yes, with one caveat.

- **Input drift (C2) and removal or rename (C4):** the caller receives a typed error (`ValidationFailed` with field and constraint, or `UnknownOperation`) before execution, without needing the full new schema. That is actionable — the caller knows which field and which constraint failed.
- **Compatible drift (C1):** no error — backward compatibility is preserved without caller action.
- **Output drift (C3):** the caller receives a successful execution result unless the host adds an explicit output-validation step. Once added, the mismatch is surfaced as a typed `ValidationFailed` on the output boundary — still actionable, but the extra check is host-internal work, not free. Stable identifiers and input validation alone are not enough.

So stable identifiers plus runtime schema and version checks **do** provide a clean, typed failure mode for input and identifier drift. Output drift needs a symmetric output validation to achieve the same guarantee.

### HOW CERTAIN

Evidence-based on the 21-case file-swap mutation (not a live rolling upgrade or propagation delay). Deterministic harness, Draft-07 validation, cross-checked via the Test D output-validation extension.

### WHAT-NOT-TESTED for drift and versioning

- No concurrent or compound drift (multiple cases applied together); only single-case independent mutations.
- No live rolling upgrade with in-flight requests — the mutation is a file swap from `0.1.0` to `0.2.0`, not a running service reload.
- No real language-model generation from the stale variant C to test whether the model would emit the stale shape (accuracy of stale generation is Test A's scope; the runtime failure mode given a stale-shaped payload is this test's scope).
- No automatic migration or compatibility shims — the test is for detection and rejection, not transparent forward migration.
- Output drift for operations beyond `query_metrics` and `search_artefacts`; other outputs may differ in sensitivity.
- Version-range negotiation is not tested — only exact `payload_version` equality is checked, not semantic-version range compatibility.
- Standard-input versus remote transport effects are not tested here; they belong to the transport section and drift is treated as transport-independent in this harness.

---

## 6. Transport findings

### WHY this section exists

The control boundary is `agent → sandbox → small preselected capability API → authoritative runtime`. Prior tool-factory work used local standard-input results that must not be assumed to hold remotely. This section establishes, with the simplest representative remote that can evidence each property, which transport semantics the boundary actually needs — and which it does not.

### WHAT it is based on

A loopback TCP harness — newline-delimited JSON over `127.0.0.1` with a thread-pool server and a subprocess server for the remote-execution proof — exercising the same 14-operation authoritative capability set at `0.1.0` through the same `sandbox → validation → policy → execution` ordering with the nine-code taxonomy. Sixty-nine JSON Lines evidence rows plus a summary file are the primary evidence. Every property was validated on the loopback cross-process transport; standard-input baseline was used only to measure single-call latency for the concurrency bound; no property is claimed as standard-input only.

### Per-property matrix (the design's required set)

| # | Property | Required by the control boundary? | Transport used | Repetitions | Verdict | Standard-input only? |
|---|---|---|---|---|---|---|
| 1 | Concurrent requests | Required | Loopback TCP | 3 iterations of 8 concurrent | **Pass** | No |
| 2 | Request and response correlation | Required | Loopback TCP | 3 iterations of 8, one delayed to force reordering | **Pass** | No |
| 3 | Remote execution | Required | Loopback TCP subprocess | 3 calls plus one malformed probe | **Pass** | No |
| 4a | Connection loss mid-request | Required | Loopback TCP | 3 iterations | **Pass** | No |
| 4b | Connection loss mid-idle | Required | Loopback TCP | 2 iterations | **Pass** | No |
| 5 | Reconnect | Required | Loopback TCP | 2 cycles | **Pass** | No |
| 6 | Timeout | Required | Loopback TCP | 4 iterations | **Pass** | No |
| 7 | Cancellation | Required | Loopback TCP | 4 iterations | **Pass** | No |
| 8 | Streaming and events | Conditional | Loopback TCP | 1 probe (3 chunks) | **Excluded** — not required | No |
| 9 | Durable operation whose lifetime exceeds the connection | Conditional | Loopback TCP | 1 probe (start, drop, reconnect, fetch) | **Excluded** — not required | No |

Overall required: **7 of 7 pass**. Conditionals: **2 of 2 correctly excluded** — an explicit finding, not a skipped test — with `stdio_only_properties: []`.

### What each required property showed

- **Concurrent requests:** eight concurrent calls including a 200-millisecond delayed straggler completed with wall time around 204 milliseconds, well under the roughly 620-millisecond serial bound, proving thread-pool concurrency. All eight responses returned per iteration.
- **Request and response correlation:** eight concurrent searches with distinct queries, one deliberately delayed by 300 milliseconds to force reordering, showed zero cross-wiring — every response identifier and operation identifier matched its request.
- **Remote execution:** a server spawned as a subprocess showed a server process identifier different from the client's (for example, 2980392 versus 2980285) on every call. The sandbox-then-validation ordering is preserved remotely: a malformed probe with a bad identifier pattern was `ValidationFailed` before execution, just as locally.
- **Connection loss mid-request:** a request with an 800-millisecond server delay was killed after 100 milliseconds. The client received `ConnectionLost` (end of file) within 2 seconds, not a spurious success. No partial result was surfaced as success.
- **Connection loss mid-idle:** an established idle connection was killed before the next write. The next write received `ConnectionLost`, and prior results were not corrupted.
- **Reconnect:** after a mid-request loss, reconnecting to a fresh server showed that new requests succeed, the prior in-flight identifier was not silently retried with different semantics (fetching the old identifier on the new server returned `NotFound`), and no orphaned server process remained. Two cycles were exercised.
- **Timeout:** a 600-millisecond server delay with a 200-millisecond client deadline produced `Timeout` within the window on all four iterations (`code` `Timeout`, `boundary` transport, `deadline_ms` preserved), distinct from `Cancelled` by code alone. Disposition is client-side enforcement; the server continues unless explicitly cancelled — inspectable via a durable fetch, not auto-cancelled.
- **Cancellation:** a long request (800 milliseconds) cancelled after 100 milliseconds via a separate connection yielded `Cancelled` with `code` `Cancelled`, `boundary` transport, on four of four iterations, with no partial creation success leaked. Cancellation is cooperative — the server slices delays into 50-millisecond chunks checking a cancelled-identifier set.

### The two conditionals — why streaming and durable are excluded

- **Streaming and events:** a probe with three chunks was ordered and cleanly terminated, confirming the transport can stream. The exclusion as "not required" is tied to the evidence that the control-boundary operations are discrete artefact operations per the authoritative capability set — create, search, review, validate — and to the prior tool-distribution evidence that does not show the boundary needing progressive results. So: capability present in transport, requirement absent at the boundary. Marked excluded per the protocol — a finding, not an omission.
- **Durable operation:** a start (300-millisecond delay), drop at 50 milliseconds, wait, reconnect, and fetch by correlation identifier returned the original durable result, confirming the transport can support durability via a correlation-identifier cache. Again, discrete synchronous request-response is the current boundary pattern, so durability is excluded as not required, subject to revision if new evidence shows the boundary needs it.

### Standard-input only qualifications and orphan checks

No property is standard-input only. Every property was validated on the loopback TCP cross-process transport; the harness direct call was only a latency baseline.

Orphan-process checks after connection loss and reconnect are mandatory because the catalog-scale finding for the prior tool registry warned about orphans on owner death without an explicit close. Every server in this report was explicitly terminated and reaped (`terminate` plus `wait` with a timeout, `poll` authoritative). No orphaned server processes were observed.

### HOW CERTAIN

Evidence-based, not proven. A deterministic simulated transport on loopback is not a wide-area network. Findings for the required properties are positive evidence that minimal semantics suffice — not proof that every real transport will behave identically.

### WHAT-NOT-TESTED for transport

- Retired scope not tested and not reintroduced: MCP idle timeout, pooling, eager-versus-lazy matrices, ToolRegistry fleet frequency, private extensions, rolling upgrade.
- No TLS, mutual TLS, authentication, or authorization at the transport.
- No cross-host (multi-machine) network partition; loopback TCP is the minimal cross-process boundary.
- No wide-area latency, jitter, loss injection, or throughput and latency quantile benchmarking beyond the eight-concurrent wall-time bound.
- No language model in the loop — agent calls are simulated; this section does not measure model accuracy under transport faults.
- No output-schema drift tested here — that belongs to the drift section — and no format-version drift beyond the payload version field.
- Streaming and durable probes confirm transport capability, not boundary requirement — the exclusion is a finding tied to current evidence, reversible if new evidence appears.

---

## 7. Claims supported

Evidence-based only — none promoted to proven because live-model and cross-host replication was absent. Each row cites the specific test evidence that supports it and the certainty discipline.

| # | Claim (as gated by the seven questions) | WHY (reasoning) | WHAT (basis — specific evidence) | HOW CERTAIN | WHAT-NOT-TESTED |
|---|---|---|---|---|---|
| 1 | **Small fixed capability surface removes practical need for token-lazy discovery, process-lazy spawning, pooling, and idle timeouts within this scope** | 14 operations fixed before the task needs no discovery or per-call spawning; runtime validation and policy are authoritative regardless of which sub-surface the sandbox exposes | Preselected-surface gate exercised in Tests B through D; D1 shows absent-from-sandbox is `UnknownOperation` before validation; retired-scope checks absent from all measurements | evidence-based (harness, in-process, single version) | No scaling beyond 14 ops, no fleet-size measurement, no lifecycle-process pool — intentionally retired |
| 2 | **A very small capability description can be used while the runtime keeps the full schema** | Valid tasks succeed and invalid tasks are still caught when only variant C is in context | Test A: variant C within five-point tolerance on 63 valid calls; Test B: 20 / 20 malformed still `ValidationFailed` before execution under variant C only | evidence-based | No live-model confirmation; single nested-filter miss showed the edge case |
| 3 | **Stable operation identifier plus parameter names, types, and a short description preserves selection and argument accuracy** | Selection 1.00 on all variants; argument 0.984 on variant C within tolerance | Test A: per-task breakdown — 20 of 21 tasks identical across variants; task 11 the sole sensitivity, recovered in one retry | evidence-based | See curve caveats; larger task catalogues not covered |
| 4 | **Runtime validation catches invalid and malformed calls reliably without needing the full schema in model context** | Malformed never reaches execution; typed identity and field or message disambiguation preserved | Test B: 20 / 20 rejected before execution across six classes; 20 / 20 constraint present; 20 / 20 message and version, 15 / 20 field, 5 / 20 via message disambiguation | evidence-based, approaching proven for "does not reach execution in this harness" (mechanical gate, Draft-07 path) | Collocated, single process, first-error-only, no `format` checks, no output-schema check here |
| 5a | **The schema information that must be exposed is: parameter names, types, required versus optional, enum literals, and a short summary — plus a per-failure typed error** | Removing full constraint text, pattern, min and max details, per-parameter long descriptions, and error-schema bodies did not push accuracy outside tolerance, and recovery succeeded without full schema excerpts | Test A: A versus C comparison — one extra rejection, recovered; Test B: exposure check — 20 / 20 recoveries using only field or message, constraint, what was received, plus variant-C names | evidence-based | Live model may reveal additional needed surface for rarer constraints or multi-error cases |
| 6 | **The separation stays useful even if Lexicon and XRPC are not adopted** | Findings about minimal description plus authoritative validation are schema-form agnostic within the constraints tested | Test B (JSON Schema Draft-07) separation result reusable regardless of whether the authoritative layer is Lexicon; drift output finding likewise transport and schema-form agnostic | evidence-based | Lexicon-specific mapping fidelity not separately tested |
| 7 | **The minimum transport semantics the boundary requires are: concurrent requests, request and response correlation, remote execution, connection loss (mid-request and mid-idle), reconnect without silent retry and without orphans, timeout, and cancellation** | Each property validated independently on a true remote boundary with typed codes and orphan checks | Test E: 7 / 7 required pass on loopback TCP cross-process, with distinct `Timeout`, `Cancelled`, `ConnectionLost` codes | evidence-based | Loopback only; no TLS, cross-host partition, or throughput quantiles |
| 8 | **Absent capability, policy-denied, malformed, and manipulated-identifier separations hold with clean, distinct boundaries** | Each boundary rejects at the correct place with the correct code and never reaches execution; trace ordering audited | Test D: 41 / 41 pass — 4 absent as `UnknownOperation` at sandbox, 4 policy-denied as `PolicyDenied` after `validation:pass`, 8 malformed as `ValidationFailed` before policy, 19 manipulated identifiers as `UnknownOperation` exact-match only | evidence-based | Single version `0.1.0`, flat deny-list policy, in-process |

---

## 8. Claims falsified or modified

A claim is falsified if the evidence contradicts it as stated; it is modified (narrowed) if the evidence requires a qualification that the original wording lacked. A modified claim is still useful — it is the honest version.

| # | Original wording (as implied by the gating question before testing) | Verdict | Corrected wording that the evidence now supports | What failed or narrowed it |
|---|---|---|---|---|
| F1 | "Parameter names and types alone are enough — constraints and enum literals can stay entirely runtime-only without cost" | **Modified** — narrowed | Enum literals must stay in the model-visible description; full constraint text can stay runtime-only without pushing accuracy outside tolerance for the 22-task set | Variant C retained enum literals per the design's invariants; the single sensitivity was a nested filter enumeration that failed when conveyed only flat — dropping enum literals was not tested as safe |
| F2 | "Schema version mismatch is automatically detectable" | **Modified** — narrowed | Stale descriptions are schema-detectable when they violate a tightened constraint (C2), but a compatible stale description that still passes validation (C1) is detectable only if the caller carries and the runtime checks `payload_version` — version inertness without carry is expected semantics | C1 without version: compatible additive drift passed silently as intended; with `payload_version` `0.1.0` versus `0.2.0`: `VersionMismatch` before schema |
| F3 | "Input validation suffices — execution success implies the boundary succeeded" | **Falsified for output drift** — corrected | Input validation plus execution success is insufficient for output-shape drift; an explicit host-internal output-schema validation step is required, otherwise stale-shaped success is returned as valid | C3 without `validate_output`: stale `total` and `items` shape passed; with `validate_output`: surfaced as `ValidationFailed` on `runtime:output` — aligns with the earlier C2 output-drift finding that mitigation bounds cost but requires validation work |
| F4 | "Runtime validation after every call may be costly or require model-visible constraint text" | **Modified** — recovery signal clarified | Recovery used only the per-failure typed error `field` (or message-derived field), `constraint`, `got`, `message`, and version — no full schema excerpt needed — but the per-failure error must carry field and constraint faithfully | Test B recovery 20 / 20 on typed error alone; null-field cases relied on `message` disambiguation |
| F5 | "Streaming and durable-operation transports are required by the boundary" | **Narrowed** — excluded pending evidence | Streaming of partial results and durable operations whose lifetime exceeds the connection are not required by the current discrete-operation boundary; the transport can provide them, the boundary does not need them | Test E probes stream 3 chunks and durable fetch both pass as transport capabilities, but exclusion findings tie requirement to current discrete artefact control-flow evidence, reversible if new evidence appears |

No claim required full falsification as "unsupported entirely" — in every case the fix is a precise narrowing rather than discarding the pattern. The sharpest narrowing is F3, which would have been a silent-correctness failure without the added output check.

---

## 9. Remaining uncertainties

This section is itself a WHAT-NOT-TESTED disclosure — the negative space that makes the report checkable by a thin consumer.

1. **No live language-model inference anywhere.** All accuracy, selection, and recovery numbers are harness-validated proxy. A replication with at least one live model (for instance, the paid Muse Spark Go variant) on the same 22-task set, three or more repetitions per cell, the same `tiktoken` `cl100k_base` 0.14.0 tokenizer and five-point tolerance, and temperature above zero or prompt-order permutation is the cheapest next test before any accuracy claim can be treated as proven.

2. **Simulated execution.** Runtime execution returns canned output shapes, not persistence, concurrent side effects, or partial-write hazards. "Rejected before execution" is trusted via the `executed` flag in the same process, not observed via a filesystem or database.

3. **Collocated for accuracy and validation.** Tests A through D are in-process; transport flattening, serialization loss, or a cross-process bypass that skips the sandbox is not measured except in Test E's remote and loss probes. Collocated near-zero latencies are not indicative of remote cost.

4. **Composite drift not tested.** Only single-case independent mutations (one of compatible, incompatible, output, or removal) per the 21 Test C cases. Concurrent mutations and ordering effects are unevidenced.

5. **No live rolling upgrade.** Drift is a file swap from `0.1.0` to `0.2.0`, not a running service reload with in-flight requests and propagation delay.

6. **Only the first validation error per payload is surfaced.** Multi-field malformed payloads where one fix leaves a second violation would need multiple round-trips; multi-error reporting latency and ranking are not measured.

7. **Version is exact equality only.** No semantic-version range negotiation. Consumers that need graceful minor-version compatibility must add it.

8. **Richer policy, harder payloads, wider catalogue not measured.** Only flat deny lists; no tenancy, attribute-based or role hierarchies, time windows, or rate limits; no adversarial parser-divergence payloads; no chained multi-step workflows or catalogue-scale task catalogue beyond the 14-operation representative set.

9. **Transport is minimal.** Loopback only — no TLS, mutual TLS, authentication, cross-host partition, wide-area jitter, or throughput and latency quantiles.

10. **Probabilistic and cost claims not tested.** No claim of statistical significance beyond three repetitions per cell; cost is the description-block token count — whole-prompt cost depends on prompt construction not measured here.

11. **Version- and artifact-bound caveat.** Results are bound to the authoritative schemas at `0.1.0` (and `0.2.0` forks for drift), `jsonschema` `4.26.0`, `tiktoken` `cl100k_base` `0.14.0`, and the harness as committed. Re-validate on upgrade (trigger #279 under #212).

---

## 10. Explicit recommendation for which findings should feed the RPC research

### Feed now — immediate candidates

1. **Minimal description pattern with runtime-authoritative validation.** The pattern of stable operation identifier plus a one-line summary of at most twenty words plus parameter names, types, required flag, and enum literals — no full per-parameter constraint text and no error-schema bodies in context — compresses the description block by 73.3 percent (C/A 0.267) with less than a two-point argument-accuracy cost on the measured set. The runtime-authoritative validation boundary then catches every malformed call before execution with a typed error sufficient for correction. This is the core separation worth carrying into the RPC and Lexicon research track.

2. **The per-failure typed error as part of the RPC contract.** `ValidationFailed` with `field` (or message-derived field), `constraint`, `got`, `message`, `schema_version`, `op_id`, and `boundary`, distinct by code from `PolicyDenied`, `UnknownOperation`, and `VersionMismatch`, was sufficient for 20 / 20 recoveries without exposing the full schema text to model context. The contract should require the transport to preserve these typed errors end to end and not flatten them to plain strings. The null-field nuance for `required` and `additionalProperties` should be documented or closed by a validator that reports an absolute path.

3. **Stable identifiers with exact-match dispatch.** Every manipulated identifier — typo, casing variant, prefix injection, path traversal, numeric guess, empty or spaced string, alias form — was `UnknownOperation` at the sandbox before any validation or execution, with only the exact identifier dispatching. That property belongs in the RPC dispatch rule.

4. **Authority separation ordering.** Sandbox, then validation, then policy, then execution — with an auditable trace — should be adopted as the pattern for proving clean separation. Each boundary rejects at the correct place with the correct code.

5. **Minimum transport semantics.** Adopt as the required set: concurrent requests, request and response correlation, remote execution, connection loss mid-request and mid-idle, reconnect without silent retry and without orphans, timeout, and cancellation — with `Timeout`, `Cancelled`, and `ConnectionLost` distinct by code. Exclude streaming and durable operations from the required set pending fresh evidence that the discrete-operation control boundary needs them, noting the transport can already support both.

6. **Output-schema validation as a required host-internal check.** Do not infer from an input-validation pass plus execution success that the output shape is correct after a schema change. The required addition is an explicit validation of generated output against the authoritative `outputSchema` at `runtime:output`. Without it, C3 shows a stale-shaped success is returned as valid. This should feed the RPC host contract even though it is host-internal work.

7. **Version discipline.** Require every schema to carry a version field; when stale-cache behavior matters, require the caller to carry `payload_version` and the runtime to check it first, surfacing `VersionMismatch` distinct from `ValidationFailed`.

### Do not feed yet — hold as unevidenced or needs the next cheap test

- **Any claim that models will recover.** Recovery 20 / 20 is scripted sufficiency of the error payload, not model disposition. Do not carry "models recover at 1.00" into RPC assumptions. **Next cheapest test:** replay the twenty Test B malformed cases under variant C with one live model, temperature above zero, three or more repetitions per case, and measure per-class recovery against the scripted baseline and the sixty percent threshold.

- **Any latency or cost model beyond the description-block ratio.** Remote transport numbers will differ materially from the near-zero collocated latencies reported here.

- **Any claim about `format`-validated fields, multi-error ranking, or catalogue-scale throughput.** Not measured.

### Branch if Lexicon and XRPC are not adopted

The separation finding is **not** Lexicon-specific. Authoritative validation against JSON Schema Draft-07 plus minimal descriptions retained the same boundary properties as would be expected under a Lexicon-authored authoritative layer. If Lexicon and XRPC are not adopted, the same pattern — runtime-authoritative validation plus stable identifiers plus per-failure typed errors plus the minimum transport semantics — remains useful with any authoritative schema layer that preserves stable identifiers and enum literals. The Lexicon-specific question would then reduce to whether the bidirectional mapping between Lexicon and JSON Schema, if used, can be demonstrated as a tested artifact rather than an assumed convenience.

### The single next cheapest test before any adoption

Before treating the accuracy claim as proven, run one live-model replication of the Test A token and accuracy measurement: the same 22-task set, three or more repetitions per variant-by-task cell, `tiktoken` `cl100k_base` 0.14.0, and the same five-point tolerance. If that live replication holds within tolerance, promote claims 2, 3, and 5a from evidence-based to proven; if it does not, narrow which constraint or nested semantics must be added back to variant C.

---

## Appendix A — Traceability

- Design: the capability-schema-validation design document (source of the seven gating questions, capability set, variant definitions, Test A through E protocols, and the ten-section outline)
- Phase 0 setup: the Phase 0 setup commit `27c0bdae` — 14 operations at `0.1.0`, variant C/A 0.25 and B/A 0.292, the harness smoke gate at 12 of 12, manifest and index committed
- Test A: commit `17ed2631` — 198 primary calls plus 10 retries, `tiktoken` `cl100k_base` 0.14.0 ratios (A 7023, B 2161, C 1873), argument 0.984 on variant C within tolerance, one nested-filter sensitivity and recovery
- Test B: commit `fbca4975` — 14 / 14 valid executed, 20 / 20 malformed rejected before execution, typed identity and recovery 20 / 20, no full schema excerpt needed
- Test C: commit `baa35bf7` — 21 / 21 pass, four forks at `0.2.0`, `Runtime.validate_output` added, version-mismatch distinct when payload version carried, output drift caught only via explicit output validation
- Test D: commits `9711de69` and `b719ca30` — 41 / 41 pass, exact-match dispatch, trace ordering audited, no wrong-boundary rejection
- Test E: commit `dcf4f313` — 7 of 7 required transport properties pass on loopback TCP plus 2 conditional correctly excluded, 69 JSON Lines evidence rows, orphan checks clean
- Harness: the research harness files — sandbox (exact-match gate), runtime (Draft-07 plus version, policy, execution), run entry point, error-code taxonomy
- Logs: committed JSON Lines directories `logs/test-a` (4 files), `logs/test-b` (1 file, 54 rows), `logs/test-c` (5 JSON files), `logs/test-d` (6 files), `logs/test-e` (11 JSON Lines plus summary)
- Schemas and variants: the authoritative schemas at `0.1.0`, derived variants A, B, C, and manifest under the capabilities folder

---

## Appendix B — Retired scope statement

MCP idle timeout and pooling behavior, eager-versus-lazy MCP process matrices, ToolRegistry C2 fleet frequency, ToolRegistry private-internal extensions, and MCP-specific rolling-upgrade behavior were not investigated and no claim in this report depends on them. Their absence from this synthesis is a scoping decision per the design's retired-scope section, not an omission.

---

*End of report. Evidence lives in the committed logs and per-test detailed reports noted above; this report is the only artifact consumed downstream. All other phase outputs are evidence, not conclusions.*

