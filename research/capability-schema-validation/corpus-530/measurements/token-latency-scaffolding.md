---
title: Token/Latency Measurement Scaffolding — #530
program: EDASES
layer: Research
document_type: Specification
status: Active
authority: Derived
canonical_repository: edases
issue: 530
pinned_versions:
  tokenizer: tiktoken cl100k_base 0.14.0
  jsonschema: 4.26.0
  harness: research/capability-schema-validation/harness/
---

# Token/Latency Scaffolding (530)

Measurement scaffolding for real-model A/B (full vs minimal). Placeholders are filled by the live run; this file defines schema and computation so next session can run verbatim.

## Token measurements (per variant, per call, per corpus)

| Metric | Scope | Tokenizer | Source |
|---|---|---|---|
| `description_tokens` | Capability-description block only (per spec §4.2) | `tiktoken cl100k_base 0.14.0` (reportable); heuristic `chars/4` only when tiktoken absent, flagged `heuristic` | `schemas/full.json` vs `schemas/minimal.json` via `harness/run.py --measure-tokens` or `measurements/compute_tokens.py` |
| `total_input_tokens` | Full prompt in (description block + instructions + user request + harness wrapper) | `cl100k_base 0.14.0` | Live runner log `input_tokens` |
| `total_output_tokens` | Model output (tool-call JSON) | `cl100k_base 0.14.0` | Live runner log `output_tokens` |
| `ratio_C_over_A` | `description_tokens(minimal)/description_tokens(full)` | cl100k_base | Reported as 0.xxx |
| `total_tokens_ratio` | `total_input_tokens(minimal)/total_input_tokens(full)` | cl100k_base | Optional |

**Why description_tokens is primary:** Instructions and user request are held constant across variants; variation is the description block.

## Success metrics (per variant, over 24 tasks × ≥3 reps)

| Metric | Definition | Denominator |
|---|---|---|
| `selection_success` | `correct_op_selected / total_calls` (exact stable ID match) | 24 tasks × reps (or per class) |
| `argument_success` | `calls_with_all_arguments_correct / total_calls` (all required present, types correct, enum valid, no extra violating authoritative schema) judged against authoritative.json, not minimal | same |
| `task_success` | selection_success AND argument_success AND executed==true (for valid 24) | same |
| `validation_failures` | count where `ValidationFailed` before execution | same + 12 malformed |
| `retries` | count of corrected retries attempted after ValidationFailed | per malformed |
| `one_retry_success` | `successful_retry_on_first_attempt / total_rejections` | 12 |
| `multi_retry_success` | `successful_within_N_retries / total_rejections` (N configurable, default 2) | 12 |

## Latency metrics (per call)

| Metric | Definition |
|---|---|
| `latency_ms` | Per-call wall time from harness.call dispatch to response/error (ms) |
| `p50` | Median latency per variant |
| `p95` | 95th percentile latency per variant |
| `retry_latency_ms` | Latency for corrected retry calls (separate distribution) |

## Recovery-specific metrics (12 malformed)

| Metric | Definition |
|---|---|
| `recovery_tokens` | Input+output tokens for the corrected retry call |
| `one_retry_success` | Retry succeeds on first attempt (no new ValidationFailed) |
| `multi_retry_success` | Succeeds within 2 retries |

## Placeholder log schema (JSONL per call)

```json
{
  "corpus": "530",
  "variant": "full|minimal",
  "task_id": "C1-T01",
  "class": 1,
  "repetition": 1,
  "model": "placeholder",
  "provider": "placeholder",
  "temperature": 0.7,
  "prompt_file": "prompts/prompt-full.md",
  "harness_version": "0.1.0",
  "tokenizer": "tiktoken cl100k_base 0.14.0",
  "description_tokens": 8760,
  "total_input_tokens": 9000,
  "total_output_tokens": 45,
  "op_selected": "search_users",
  "arguments_submitted": {"query":"alice"},
  "expected_op": "search_users",
  "expected_args": {"query":"alice"},
  "selection_correct": true,
  "arguments_correct": true,
  "task_success": true,
  "validation_result": "executed:ok",
  "error": null,
  "executed": true,
  "retries": 0,
  "latency_ms": 123,
  "timestamp": "placeholder"
}
```

Adversarial D1-D4 placeholder adds `expected_code`, `expected_boundary`, `trace`.

## Pinned versions (measurement)

- `tiktoken==0.14.0` with encoding `cl100k_base` (harness `run.py` reports tiktoken when installed else heuristic with explicit flag).
- `jsonschema==4.26.0` (Draft-07) via `harness/runtime.py` (fallback only heuristic; production uses Draft7Validator).
- `ToolRegistry==0.15.0 / MCP==2.0.0` (version-bound prior work, retired scope per design §9; not exercised in this corpus — recorded for traceability).
- `harness_version` from `capabilities/manifest.json` version `0.1.0`.
- `model` / `provider` / `temperature` recorded per log row at live-run time (placeholders until live session).

## 5pp tolerance (pre-registered, for reporting)

Minimal acceptable if `|selection_minimal - selection_full| ≤ 0.05` AND `|argument_minimal - argument_full| ≤ 0.05` on 24 well-formed tasks (or 22-task subset if reusing prior suite), ≥3 reps, temperature>0 or prompt-order permutation. Same tolerance reported for task_success. Token/accuracy curve X=tokens(minimal)/tokens(full) vs Y=selection/argument success is primary deliverable; ratio without named tokenizer version not reportable.

## Computation helpers

- `measurements/compute_tokens.py` — measures description_tokens for schemas/full.json and schemas/minimal.json (chars, approx, tiktoken).
- `measurements/compute_latency.py` — placeholder; live runner fills latency_ms/p50/p95 from logs.
- Logs dir: `research/capability-schema-validation/corpus-530/measurements/logs/` (populated by live run; .gitkeep committed).
- Summary placeholder: `measurements/summary.json` (pre-filled with nulls; live run overwrites).

## WHAT-NOT-TESTED

- No live model or latency measurement in this scaffolding commit — all timing/token fields are placeholders to be filled by next session's live A/B run.
- Cost of regenerating derived variants (single authoring cost, not per-call) — not measured here.

