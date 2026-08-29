---
title: Test A Protocol — Minimal Capability Description
program: EDASES
layer: Research
document_type: Protocol
status: Draft
authority: Derived
canonical_repository: edases
depends_on:
  - .design/capability-schema-validation.md
  - research/capability-schema-validation/capabilities/authoritative/schemas.json
  - research/capability-schema-validation/capabilities/derived/variant-a.json
  - research/capability-schema-validation/capabilities/derived/variant-b.json
  - research/capability-schema-validation/capabilities/derived/variant-c.json
  - research/capability-schema-validation/harness/error-codes.md
consumed_by:
  - research/capability-schema-validation/tests/test-a/results.md
  - research/capability-schema-validation/report.md
---

# Test A — Minimal Capability Description: Protocol

**Questions addressed:** 2, 3, 5 (from design §1.4).

## Fixed capability set

14 operations, version `0.1.0`, covering all six required categories (design §3.2):

| Category | Ops |
|---|---|
| Read / query (≥2) | `search_artefacts`, `get_artefact`, `list_reviews`, `get_capability_schema`, `query_metrics` (5) |
| State-changing (≥1) | `create_artefact`, `update_artefact_status`, `archive_artefact`, `link_artefacts`, `submit_evidence` (5) |
| Multi-param (≥1, 4+ params) | `create_review` (`artefact_id`, `verdict`, `severity?`, `rationale`, `citations?`) |
| Enum / constrained (≥1) | `set_severity` (`critical/high/medium/low`), `set_artefact_state` (`draft/active/archived`) |
| Structured output (≥1) | `query_metrics` → `{items:[{key,count,avg_score}], total, facets{by_type,by_status}}` |
| Typed errors (≥2 shapes) | `NotFound`, `ValidationFailed`, `Conflict`, `PolicyDenied`, `VersionMismatch`, `UnknownOperation` across 8 ops |

Additional constraints satisfied: optional params (`search_artefacts.cursor`, `create_artefact.body/tags`, `create_review.citations`, `set_artefact_state.comment`, `submit_evidence.note`, `link_artefacts.bidirectional`), array/nested (`create_artefact.tags[]`, `create_review.citations[]`, `submit_evidence.evidence_items[]`, `link_artefacts.target_ids[]`, `query_metrics.facets{}`), output differs from input (`query_metrics` filter → nested facets).

Authoritative schemas: `research/capability-schema-validation/capabilities/authoritative/schemas.json` (Draft-07, `version: 0.1.0` on every op). Model-visible descriptions are derived artifacts `derived/variant-{a,b,c}.json`.

## Variants (controlled manipulation)

| Variant | Content shown to model per capability |
|---|---|
| **A — Full schema** | Complete JSON Schema: all properties, types, descriptions, constraints (enum, pattern, min/max, required), error schemas. |
| **B — Short description + names/types** | Operation ID + summary + param names + param types + required/optional + enum values where applicable. No per-param long descriptions, no full constraint text, no error-schema body beyond code names. |
| **C — Stable ID + one-line + names/types** | Stable operation ID + one-line description (≤20 words) + param names + param types + required flag + enum literals. Minimal constraint surface. No error-schema body. |

All variants share identical stable operation IDs and identical param names/types. Token counts per `capabilities/manifest.json` (heuristic char/4): A 7941, B 2322, C 1985; C/A 0.25, B/A 0.292. Harness `run.py --measure-tokens` reports `tiktoken cl100k_base` when installed, else heuristic with explicit flag.

## Fixed task set (≥20 tasks, each 1–3 calls, verifiable success criteria)

Tasks are reused across variants where possible; variant-sensitive tasks are flagged explicitly (design §5.1). The task set is:

| # | Task | Expected capability call(s) | Success criterion |
|---|---|---|---|
| 1 | Search for artefacts about "auth" | `search_artefacts(query="auth")` | correct op selected, query present, required pattern satisfied |
| 2 | Search with pagination | `search_artefacts(query="spec", limit=5, cursor="cur_abc123")` | all params validated against authoritative schema |
| 3 | Get artefact by ID | `get_artefact(id="art_abc-123")` | id pattern `^art_[a-z0-9-]+$` |
| 4 | Create a spec artefact | `create_artefact(type="spec", title="My Spec")` | type enum valid, title length 1–200 |
| 5 | Create artefact with tags | `create_artefact(type="decision", title="T", body="Body text", tags=["a","b"])` | optional body/tags validated |
| 6 | Update artefact status with reason | `update_artefact_status(id="art_abc-123", status="active", reason="reviewed")` | status enum, reason 1–500 |
| 7 | Create review (approve) | `create_review(artefact_id="art_abc-123", verdict="approve", rationale="This is a good rationale with enough length")` | verdict enum, rationale 10–2000 |
| 8 | Create review (request_changes with severity) | `create_review(artefact_id="art_abc-123", verdict="request_changes", severity="high", rationale="Detailed rationale for changes needed...", citations=["art_def-456"])` | 5 params, mixed required/optional, citations array |
| 9 | Set severity | `set_severity(artefact_id="art_abc-123", level="critical")` | level enum critical/high/medium/low |
| 10 | Set artefact state | `set_artefact_state(artefact_id="art_abc-123", state="active", comment="ok")` | state enum, optional comment |
| 11 | Query metrics (filter only) | `query_metrics(filter={"type":"spec"})` | filter object with enum type, structured output expected |
| 12 | Query metrics with group_by and facets | `query_metrics(filter={"type":"review","since":"2026-01-01T00:00:00Z"}, group_by="status", include_facets=true)` | nested output `facets{by_type,by_status}` |
| 13 | List reviews filtered | `list_reviews(artefact_id="art_abc-123", verdict="approve", limit=10)` | optional artefact_id + verdict enum + limit 1–50 |
| 14 | Get capability schema for search | `get_capability_schema(op_id="search_artefacts")` | op_id exists, structured output |
| 15 | Get capability schema with version | `get_capability_schema(op_id="search_artefacts", version="0.1.0")` | version semver pattern |
| 16 | Submit evidence (single item) | `submit_evidence(artefact_id="art_abc-123", evidence_items=[{source:"paper", content:"evidence text"}])` | array min 1, nested content 1–2000 |
| 17 | Submit evidence (with URL, weight, note) | `submit_evidence(artefact_id="art_abc-123", evidence_items=[{source:"url-source", url:"https://example.com", content:"text", weight:0.8}], note="optional note")` | optional url (uri), weight 0–1, optional note |
| 18 | Link artefacts (single target) | `link_artefacts(source_id="art_abc-123", target_ids=["art_def-456"], relation="relates_to")` | target_ids array 1–10, relation enum |
| 19 | Link artefacts (multi-target, bidirectional) | `link_artefacts(source_id="art_abc-123", target_ids=["art_def-456","art_ghi-789"], relation="depends_on", bidirectional=true)` | array + enum + optional boolean |
| 20 | Archive artefact | `archive_artefact(artefact_id="art_abc-123", reason="superseded by new design for clarity")` | reason 5–500, pattern `^art_[a-z0-9-]+$` for artefact_id |
| 21 | Validate payload (valid) | `validate_payload(op_id="search_artefacts", payload={"query":"hi"}, strict=true)` | payload object, op_id exists, returns `{valid:true}` |
| 22 | Create artefact (expected invalid — title too long, for negative test) | `create_artefact(type="spec", title="<201-char string>")` | used to measure invalid-call rate; authoritative maxLength 200 |

Tasks 1–21 are expected to succeed (valid under authoritative schema). Task 22 is intentionally malformed and measures invalid-call handling. For variant comparison, the primary accuracy denominator excludes task 22 (or reports it separately as invalid-call rate).

Variant-sensitive expectation: task 11 (`query_metrics` with nested filter) is predicted to be more sensitive to minimal description (reason: nested object semantics not conveyed by flat name/type pairs). This prediction is recorded here and not used to exclude results post hoc (design §6.3).

## Repetition and model config

* Each variant × task cell is run **≥3 times** (design §5.1). Report per-cell counts.
* Temperature > 0 or prompt-order permutation sufficient to distinguish obvious selection/argument effects from single-run noise.
* Model(s) and exact versions are recorded in `results.md` (not here — this is pre-registration; the version string is filled at run time). At minimum, record `model_id` and `temperature`.
* Tokenizer for token/accuracy curve: `tiktoken cl100k_base` (harness reports `cl100k_base` version via `tiktoken` package version when available; otherwise heuristic `char/4` with explicit `heuristic` flag per design §6.1). Scope is **capability-description block only** (§6.1), not full prompt.

## Measures (per variant)

* **Correct capability selection rate** — `correct_capability_selected / total_calls` (selected == expected per task table).
* **Argument correctness rate** — `calls_with_all_arguments_correct / total_calls` (all required params present, types correct, enum values valid, no extraneous params violating authoritative schema; judged against authoritative schema, not minimal description).
* **Invalid-call rate** — `rejected_by_runtime / total_calls` (calls rejected by runtime validation boundary before execution).
* **Recovery-after-rejection rate** — `successful_retry_after_rejection / total_rejections` (given typed error from runtime, does next call succeed without human intervention; ties to Test B harness; reported jointly).
* **Prompt/token size** — characters + tokens per §4.2; report `tokens(C)/tokens(A)` and `tokens(B)/tokens(A)`.

## Pre-registered acceptance criteria (§5.2)

> **C is acceptable if capability-selection rate is within 5 percentage points (pp) of A and argument-correctness within 5pp of A on the fixed task set (tasks 1–21, 3 repetitions, temperature > 0).**

Concretely:

* Let `sel_A`, `arg_A` be selection and argument-correctness rates under variant A.
* Let `sel_C`, `arg_C` be the same under variant C.
* Accept if `|sel_C - sel_A| <= 0.05` AND `|arg_C - arg_A| <= 0.05`.
* The same tolerance is reported for B vs A for comparison, but the claim that "C preserves accuracy" is evaluated only on the C-vs-A delta.

Token/accuracy claim is unsupported if the measured delta exceeds the pre-registered tolerance, even if absolute accuracies look high (design §5.2).

Additional threshold: report compression `tokens(C)/tokens(A)` — no acceptance gate, but the curve (tokens vs accuracy) is the primary deliverable for the token/accuracy question (design §6.4). A ratio without a named tokenizer version is not reportable (§4.2).

## Reporting shape

* Produce the token/accuracy curve: x-axis = tokens (or compression ratio vs A), y-axis = selection accuracy and argument accuracy. Mark variants A/B/C as points.
* Raw counts, not only percentages (design §8.2).
* Per-variant tables with `{variant, tasks, repetitions, correct_selected, arg_correct, rejected, tokens, ratio}`.

## Logging

Every call records `{variant, task_id, repetition, capability_selected, arguments_submitted, runtime_validation_result, error_code_if_any, tokens_in_context, latency_ms}` under `research/capability-schema-validation/logs/test-a/` (design §5.1). No silent fallback: any harness step that silently retries/reshapes before runtime validation invalidates the test.

## WHAT-NOT-TESTED (AGENTS.md)

* Not tested: statistical significance beyond the reported repetition count (≥3). No claim of publication-grade significance.
* Not tested: tasks outside the 22 listed (e.g., multi-step chained workflows) — catalogue of real EDASES agent tasks may differ.
* Not tested: cost of regenerating derived variants (single authoring cost; not per-call).
* Not tested here: whether typed errors are surfaced verbatim to the model vs lossy translation — that is Test B scope.

## Verification before Phase 1

This protocol file must be committed before Phase 1 tracks begin (Phase 0 gate). `results.md` under same directory is written by Phase 1 Track A.
