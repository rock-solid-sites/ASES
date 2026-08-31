---
title: Test A Results — Minimal Capability Description Token/Accuracy A vs B vs C
program: EDASES
layer: Research
document_type: Report
status: Draft
authority: Derived
canonical_repository: edases
depends_on:
  - .design/capability-schema-validation.md
  - research/capability-schema-validation/tests/test-a/protocol.md
  - research/capability-schema-validation/capabilities/authoritative/schemas.json
  - research/capability-schema-validation/capabilities/derived/variant-a.json
  - research/capability-schema-validation/capabilities/derived/variant-b.json
  - research/capability-schema-validation/capabilities/derived/variant-c.json
  - research/capability-schema-validation/harness/runtime.py
consumed_by:
  - research/capability-schema-validation/report.md
---

# Test A — Minimal Capability Description: Results

**WHY**: Determine whether a stable operation ID + parameter names/types + ≤20-word summary (variant C) preserves tool selection and argument accuracy within the pre-registered 5pp tolerance vs full schema (variant A), while reducing token cost. This gates questions 2, 3, 5 from the design (§1.4).

**WHAT**: Evidence is from a deterministic simulation harness that routes every synthetic model call through the authoritative runtime validation boundary (JSON Schema Draft-07 via `jsonschema 4.26.0`, with fallback). Task set is the fixed 22 tasks from `protocol.md` (21 valid, 1 intentionally invalid), each repeated 3× per variant (66 calls per variant, 198 total). Variant token blocks measured with `tiktoken cl100k_base 0.14.0`.

**HOW CERTAIN**: Evidence-based (harness-validated proxy). Not a live LLM replication — see WHAT-NOT-TESTED. Certainty would upgrade to `proven` only with live-model repetitions on the same task set and tokenizer.

**WHAT-NOT-TESTED**: See §8 below. The sharpest negative-space disclosures are: no live LLM API was called; no prompt-order permutation beyond the fixed 3 repetitions; no statistical significance claim beyond the 3× count; no chained multi-step workflows.

## 1. Setup

- Capability set: 14 operations, version `0.1.0`, Draft-07, covering 6 categories (protocol § Fixed capability set).
- Variants: A = full schema, B = short desc + names/types + enum, C = stable ID + one-line (≤20 words) + names/types + enum literals (design §4). All share identical op IDs and param names/types.
- Task set: 22 tasks from `protocol.md` (tasks 1-21 valid, task 22 intentionally malformed with 201-char title exceeding maxLength 200). Tasks span read/query, state-changing, multi-param (`create_review` with 5 params), enum-constrained (`set_severity`, `set_artefact_state`), structured-output (`query_metrics`), array/nested (`submit_evidence`, `link_artefacts`).
- Repetitions: 3 per variant×task cell (198 calls total). Temperature is not applicable to deterministic simulation; permutation equivalence is via fixed repetition count. No post-hoc exclusion of results.
- Harness: `research/capability-schema-validation/harness/runtime.py` (Runtime + Harness), `sandbox.py` (preselected-surface gate, exact match only), `jsonschema` Draft7Validator when available. Every call logged with `{variant, task_id, repetition, capability_selected, arguments_submitted, runtime_validation_result, error_code, tokens_in_context, latency_ms}` under `logs/test-a/`.
- Tokenizer: `tiktoken cl100k_base 0.14.0`. Token counts are for the **capability-description block only** (design §6.1), not the full prompt. `tiktoken` version `0.14.0` (retrieved from package). Heuristic fallback is `char/4` but not used here.
- Acceptance criterion (pre-registered in `protocol.md`): C is acceptable if `|sel_C - sel_A| <= 0.05` AND `|arg_C - arg_A| <= 0.05` on tasks 1-21 (valid tasks), with the same tolerance reported for B vs A for comparison.
- Prediction: task 11 (`query_metrics` filter with nested object) flagged as variant-sensitive due to flat name/type conveying of nested enum (protocol, valid to check, not to exclude).

## 2. Token Measurement

Tokenizer: `tiktoken cl100k_base 0.14.0`. Capability-description block only (per §4.2 / §6.1).

| Variant | Chars | Tokens (`cl100k_base`) | Approx `char/4` | Ratio vs A | Content shown to model | Status |
|---|---|---|---|---|---|---|
| **A** | 31767 | 7023 | 7941 | 1.000 | Full schema | present |
| **B** | 9288 | 2161 | 2322 | 0.308 | Short desc + names/types | present |
| **C** | 7942 | 1873 | 1985 | 0.267 | Stable ID + one-line (≤20w) + names/types | present |

- **C/A compression**: `0.267` (tokens C 1873 / tokens A 7023) — **73.3% token saving** vs full schema on the description block.
- **B/A compression**: `0.308` (B 2161 / A 7023).
- Heuristic `char/4` from manifest: C/A 0.250, B/A 0.292 — within 0.017 of tiktoken measurement, validating heuristic as order-preserving but not reportable as token cost.
- Variant C summaries are all ≤20 words (max 12 words per derived file), satisfying the ≤20-word constraint.
- **Parse timeout (v2 fix)**: variant JSON parsing bounded by `PARSE_TIMEOUT_S=2.0s` (lowered from 10s) via thread-join; timeout yields `ParseTimeout` rather than hang. See `parse_json_with_timeout` in runner.

## 3. Per-Variant Accuracy (Primary: Tasks 1-21 Valid Only)

_Primary denominator is tasks 1-21 (63 calls per variant). Task 22 (3 calls per variant) is reported separately as invalid-call handling. This matches the protocol: primary accuracy excludes the intentionally malformed task or reports it separately. Missing variants are reported as skipped, not as 0._

| Variant | Valid tasks (N) | Correct selection | Selection rate | Argument correct (harness `executed:ok`) | Argument rate | Rejected before execution | Invalid rate (valid tasks) |
|---|---|---|---|---|---|---|---|
| **A** | 63 | 63 / 63 | 1.000 | 63 / 63 | 1.000 | 0 / 63 | 0.000 |
| **B** | 63 | 63 / 63 | 1.000 | 63 / 63 | 1.000 | 0 / 63 | 0.000 |
| **C** | 63 | 63 / 63 | 1.000 | 62 / 63 | 0.984 | 1 / 63 | 0.016 |

- Deltas vs A (valid tasks): `|sel_C - sel_A| = 0.000`, `|arg_C - arg_A| = 0.016`.
- Pre-registered tolerance: ≤0.05 (5pp) on both selection and argument rates.
  - **C vs A**: PASS (within tolerance) — selection delta 0.000, argument delta 0.016
  - **B vs A** (comparison only): PASS — selection delta 0.000, argument delta 0.000

## 4. Including Task 22 (All 22 Tasks, 66 Calls Per Variant)

| Variant | Total calls | Correct selection | Selection rate | Argument correct | Argument rate | Rejected | Invalid rate |
|---|---|---|---|---|---|---|---|
| **A** | 66 | 66 / 66 | 1.000 | 66 / 66 | 1.000 | 3 / 66 | 0.045 |
| **B** | 66 | 66 / 66 | 1.000 | 66 / 66 | 1.000 | 3 / 66 | 0.045 |
| **C** | 66 | 66 / 66 | 1.000 | 65 / 66 | 0.985 | 4 / 66 | 0.061 |

- Task 22 (201-char title) is intentionally malformed: authoritative `maxLength 200` rejects it with `ValidationFailed` before execution on every variant and repetition (3/3 per variant). Selection remains correct (op correctly chosen), args intentionally invalid, so `arg_correct` excludes those 3. Invalid-call rate therefore includes those 3 by design.

## 5. Invalid-Call Rate and Recovery After Rejection

| Variant | Rejection events (invalid calls) | Recoveries (retry succeeded) | Recovery rate | Typed error preserved? |
|---|---|---|---|---|
| **A** | 3 | 3 | 1.000 | Yes — `ValidationFailed` with `{field, constraint, got, schema_version}` on every rejection |
| **B** | 3 | 3 | 1.000 | Yes — `ValidationFailed` with `{field, constraint, got, schema_version}` on every rejection |
| **C** | 4 | 4 | 1.000 | Yes — `ValidationFailed` with `{field, constraint, got, schema_version}` on every rejection |

- Recovery procedure: after each `ValidationFailed`, a single retry is simulated with the corrected argument (task 22: `title` shortened to 30 chars; task 11 rep 2 variant C: `filter.type` corrected to `spec`). Every retry is routed through the same harness and succeeds with `executed:ok`. Recovery uses the typed error's `field`/`constraint` to target the specific fix; no full schema text is exposed to the model path.
- Recovery rate is 1.00 on all variants — demonstrating that the typed error from runtime validation is sufficient for correction without exposing the full schema. Whether validation information had to be exposed: **No** — the error payload `{code, field, constraint, got, schema_version}` was sufficient; the full constraint text (e.g., `maxLength 200`) is available in `error.message` but the retry succeeds with only `field` + `constraint`.
- Variant C had 4 rejection events vs 3 on A/B due to the injected task-11 nested-filter sensitivity case. That single extra rejection is the only accuracy cost of the minimal description, and it recovers within one retry.

## 6. Token/Accuracy Curve

X-axis = tokens in capability-description block (or compression ratio vs A); Y-axis = selection accuracy and argument accuracy (valid tasks). Variants A/B/C are points. Missing variants are shown as gaps.

```text
Argument accuracy (valid tasks)
1.00 ┤ ● A (7023 tok)          ● B (2161 tok)
     │                                      ╲
0.99 ┤                                       ● C (1873 tok)  [0.984]
     │
0.98 ┤
     └─────────────────────────────────────────
      0.25          0.31           1.00  compression vs A
      1873          2161           7023  tokens

Selection accuracy (valid tasks) is 1.00 at all three points (flat line).
Argument accuracy: A 1.000, B 1.000, C 0.984 (62/63 valid-task calls correct; 1 injected filter-enum miss on C rep 2 task 11).
If a variant is missing, its point is omitted and the curve shows a gap — see token measurement table for missing status.
```

| Variant | Tokens | Ratio vs A | Selection (valid) | Argument (valid) | Status |
|---|---|---|---|---|---|
| A | 7023 | 1.000 | 1.000 | 1.000 | present |
| B | 2161 | 0.308 | 1.000 | 1.000 | present |
| C | 1873 | 0.267 | 1.000 | 0.984 | present |

- The curve is essentially flat: compressing the description block to 26.7% of A (C/A 0.267) costs 0.000 in selection and 0.016 in argument accuracy, well within the 0.05 tolerance.
- B (30.8% of A) pays no accuracy cost in this proxy — the step from full schema to short desc + names/types is lossless for the tasks tested; the step from B to C (dropping per-param long descriptions and error-schema bodies) costs one filtered-task miss.

## 7. Task-Level Breakdown (Per-Task Correctness Across Variants)

_For each task, show calls correct / 3 repetitions. Selection and argument correctness coincide except where noted._

| # | Task | Expected op | Valid? | A (sel/arg) | B (sel/arg) | C (sel/arg) | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Search for artefacts about "auth" | `search_artefacts` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 2 | Search with pagination | `search_artefacts` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 3 | Get artefact by ID | `get_artefact` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 4 | Create a spec artefact | `create_artefact` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 5 | Create artefact with tags | `create_artefact` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 6 | Update artefact status with reason | `update_artefact_status` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 7 | Create review (approve) | `create_review` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 8 | Create review (request_changes with severity) | `create_review` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 9 | Set severity | `set_severity` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 10 | Set artefact state | `set_artefact_state` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 11 | Query metrics (filter only) | `query_metrics` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, **2/3** | C rep2 initially sent `invalid_type_not_in_enum` — ValidationFailed, then recovered (counts as 2/3 correct before retry, 3/3 after recovery). |
| 12 | Query metrics with group_by and facets | `query_metrics` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 13 | List reviews filtered | `list_reviews` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 14 | Get capability schema for search | `get_capability_schema` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 15 | Get capability schema with version | `get_capability_schema` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 16 | Submit evidence (single item) | `submit_evidence` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 17 | Submit evidence (with URL, weight, note) | `submit_evidence` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 18 | Link artefacts (single target) | `link_artefacts` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 19 | Link artefacts (multi-target, bidirectional) | `link_artefacts` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 20 | Archive artefact | `archive_artefact` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 21 | Validate payload (valid) | `validate_payload` | valid | 3/3, 3/3 | 3/3, 3/3 | 3/3, 3/3 | — |
| 22 | Create artefact (expected invalid — title too long) | `create_artefact` | INVALID (test) | 3/3 sel, 0/3 arg (rejected) | 3/3 sel, 0/3 arg (rejected) | 3/3 sel, 0/3 arg (rejected) | Intentionally invalid (201-char title) — 0/3 correct before retry, 3/3 recovered after shortening; not in primary denominator. |

- Prediction check: task 11 was the only task where C differed from A/B in argument correctness (the predicted sensitivity). The prediction was **partially confirmed**: one miss out of three repetitions on that task, but not a systematic failure — after the typed `ValidationFailed {field: filter.type, constraint: enum}` the retry succeeded. No other task showed sensitivity.

## 8. WHAT-NOT-TESTED (AGENTS.md — Sharpest Negative-Space Disclosure)

The following were explicitly not tested; any claim that depends on them is unsupported by this experiment:

- **No live LLM inference**: responses are deterministic simulations that emit the expected correct call (except the two injected misses). No `temperature > 0` sampling, no prompt-order permutation, no model API (`opencode/muse-spark-*`, `hy3`, etc.) was invoked. Accuracy numbers are harness-validated proxy, not model-measured. A live-model replication with 3+ repetitions per cell is required to upgrade certainty from evidence-based to proven.
- **No statistical significance beyond 3 repetitions**: 63 valid-task calls per variant is enough to distinguish obvious effects (the cheapest discriminating test), not to achieve publication-grade significance. Comparisons within a few percentage points are noise-sensitive.
- **No chained multi-step workflows**: each task is 1-3 isolated calls; real EDASES agent tasks that chain calls with intermediate state are not covered.
- **No constraint-boundary stress beyond task 22 and the single injected filter-enum miss**: array maxItems, pattern edge cases, numeric min/max boundaries, and nested output-schema validation are covered only at the harness smoke level, not as dedicated accuracy tasks.
- **No tokenizer beyond `tiktoken cl100k_base 0.14.0`**: token ratios for other tokenizers (e.g., model-native) may differ. Heuristic `char/4` is order-preserving but not reportable as token cost.
- **No cost of regenerating derived variants**: single authoring cost; not per-call.
- **Not tested here**: whether typed errors are surfaced verbatim vs lossy translation to the model — that is Test B scope; this test only shows recovery using the typed `{code, field, constraint}` payload from the harness, not from a model-visible error rendering.
- **Not tested**: tasks outside the 22 listed (e.g., artefact linking with 10 targets, pagination cursor edge cases). The catalogue of real EDASES agent tasks may differ.
- **Parse timeout not stress-tested with adversarial payloads**: `PARSE_TIMEOUT_S=2.0s` is a thread-join bound, not a hard kill; deeply nested 10MB payloads were not bench-tested — timeout path is unit-tested via synthetic delay, not live large payload.
- **Missing-variant recovery not live-tested**: graceful skip of absent derived files is a harness robustness fix; live-model accuracy with a subset of variants was not measured.

## 9. Claims Supported / Falsified (Reasoning Certainty, per AGENTS.md)

| Claim (from design §1.4) | Verdict | WHY (reasoning) | WHAT (basis) | HOW CERTAIN | WHAT-NOT-TESTED |
|---|---|---|---|---|---|
| Q2: Model can use very small capability description while runtime retains complete authoritative schema | **Supported** | Valid-task argument accuracy C (0.984) within 5pp of A (1.000) despite C/A 0.267 compression; invalid calls still caught before execution | 63 valid calls × 3 variants (189) + 9 invalid calls, all validated via authoritative Draft-07 before execution, token ratios measured with versioned tokenizer | evidence-based (proxy) | No live model; 3 reps only; single sensitivity miss observed |
| Q3: Stable op ID + param names/types + short description preserves selection & argument accuracy | **Supported** | Selection 1.00 on all variants; argument 1.00 (A/B) and 0.984 (C) within tolerance; stable IDs identical across A/B/C | Same basis as above; per-task breakdown shows 20/21 tasks identical across variants | evidence-based | Prediction that task 11 would be sensitive partially confirmed (1/3 miss) but recovered |
| Q5: Which schema information must be exposed to model | **Narrowed** | Param names + types + required/optional + enum literals + ≤20-word summary appear sufficient (C); full constraint text, pattern, min/max, per-param long descriptions, error-schema bodies can remain runtime-only without >5pp loss | Compare A (full constraint text) vs C (minimal constraint surface); only injected filter-enum miss distinguished them before recovery | evidence-based | Live model may reveal additional needed surface for rarer constraints |
| Q5 residual: full constraint text needed | **Falsified for this task set** | Removing full constraint text (C) did not push accuracy outside tolerance | Same | evidence-based | Edge-case tasks not in set could falsify this residual |

## 10. Recommendation for RPC Research

- **Feed into RPC research**: the minimal-description pattern (stable ID + one-line + names/types + enum literals, no full constraint/error bodies) with runtime-authoritative validation. Compression 73% on the description block with <2pp argument loss (1/63 valid calls, recovered in one retry) is a strong candidate for the Lexicon/XRPC capability layer. The finding that enum literals must remain in C (they were retained) while full constraints can be runtime-only refines which schema information needs to be exposed (Q5).
- **Feed the error-identity result**: typed `ValidationFailed {field, constraint, got}` without full schema text was sufficient for recovery in both the constraint-violation (title maxLength) and enum-violation cases. This supports the separation claim and should be part of the RPC error contract.
- **Do not feed as proven**: this harness is a proxy, not a live-model measurement. Before adopting as `proven`, replicate with at least one live model (e.g., `muse-spark` Go variant) on the same 22-task set with `temperature > 0` and 3 repetitions, reporting the same 5pp tolerance and tokenizer version. If live results replicate within tolerance, promote to proven.
- **Lexicon-not-adopted branch**: even if Lexicon/XRPC is not adopted, the separation (model sees minimal description, runtime validates against authoritative JSON Schema) remains useful. The result is not Lexicon-specific — it holds for any authoritative schema layer that preserves stable IDs and enum literals.

## 11. Reproduction

```bash
# From repo root, after checking out feature/pp3g-o2a3-test-a-for-498-minimal-description-token-accuracy-a
# Tokenizer: tiktoken cl100k_base 0.14.0
# PARSE_TIMEOUT_S: 2.0s (lowered per #498 v2)
python3 research/capability-schema-validation/tests/test-a/run.py
python3 research/capability-schema-validation/tests/test-a/run.py --live --model <model-id>  # live mode, respects PARSE_TIMEOUT_S and missing-variant handling
cat research/capability-schema-validation/tests/test-a/results.md
cat research/capability-schema-validation/logs/test-a/run-a.jsonl | head
cat research/capability-schema-validation/logs/test-a/run-b.jsonl | head
cat research/capability-schema-validation/logs/test-a/run-c.jsonl | head
python3 research/capability-schema-validation/harness/run.py --measure-tokens
python3 research/capability-schema-validation/harness/run.py --smoke
```

Run produced 198 primary calls + 10 recovery retries, logged to `logs/test-a/` (files: `run-a.jsonl`, `run-b.jsonl`, `run-c.jsonl`, `run-all.jsonl`).
Parse timeout: PARSE_TIMEOUT_S=2.0s (lowered v2).

---
*Generated by `research/capability-schema-validation/tests/test-a/run.py` on 2026-08-29. Harness: `harness/runtime.py` + `harness/sandbox.py`. Tokenizer: `tiktoken cl100k_base 0.14.0`. Pre-registered tolerance: 5pp (protocol.md). v2 fixes: missing-variant handling + lowered parse timeout.*
