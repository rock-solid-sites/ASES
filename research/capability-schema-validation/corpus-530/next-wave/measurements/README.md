---
title: Measurements Scaffolding — Next-Wave Corpus-530 (multi-rep, multi-model, second retry, EDASES reuse)
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
  schemas: 0.1.0
---

# Measurements — Next-Wave Corpus-530

**WHY** — Without pre-registered measurement definitions, tolerance, and pinned tokenizer/harness versions, the next live wave cannot be reproduced or compared to the current 07dfab42 baseline (48 A/B 95.8% vs 91.7% harness delta 4.2pp within 5pp, 71% token saving).

**WHAT** — This doc fixes all measurement definitions, tolerances, and versions for the next live wave that writes under `next-wave/measurements/` without yet running. Corpus-530 files are **strictly frozen** (see `../NO_MODIFY_CORPUS.md`).

**HOW CERTAIN** — Scaffolding only; templates under this directory are placeholders filed before live data.

**WHAT-NOT-TESTED** — No live trials yet; no significance beyond pre-registered 3 reps per variant per model.

## Frozen corpus (strict no-modify rule)

Do NOT modify: `../schemas/authoritative.json`, `../schemas/full.json`, `../schemas/minimal.json`, `../tasks.json`, `../malformed-recovery.json`, `../adversarial.json`, `../corpus.jsonl`, `../prompts/prompt-full.md`, `../prompts/prompt-minimal.md`. See `../NO_MODIFY_CORPUS.md`. Any modification requires a new corpus version and fresh issue.

## Pinned versions (required in every log row)

| Component | Version | Source | Notes |
|---|---|---|---|
| `schemas` | `0.1.0` per op and global | `../schemas/authoritative.json` `version` / `manifest.json` | 17 ops (14 base + 3 search_users/groups/projects), Draft-07, hidden constraints enforced at runtime |
| `tokenizer` | `tiktoken==0.14.0` `cl100k_base` | `measurements/compute_tokens.py`, `harness/run.py --measure-tokens`, next-wave logs `description_tokens` | Primary is description block only (spec §4.2); reportable only when tokenizer named; heuristic `chars/4` flagged if tiktoken absent |
| `jsonschema` | `4.26.0` Draft7Validator | `harness/runtime.py` | Fallback validator if not installed, but production requires `4.26.0` |
| `harness` | `0.1.0` | `harness/sandbox.py` + `harness/runtime.py` ordering `sandbox→validation→policy→execution`, trace logged | Next wave also logs `harness_variant` = `conventional` or `edases` alongside this version |
| `ToolRegistry / MCP` | `0.15.0` / `2.0.0` | design §9 retired scope | Version-bound prior work; not exercised (no lifecycle/discovery/pooling/idle-timeout added) |

Targets (frozen, already measured): `schemas/full.json` 8915 tok vs `schemas/minimal.json` 2588 tok, ratio 0.290, saving 71.0% (`cl100k_base 0.14.0`); `prompts/prompt-full.md` 8961 tok vs `prompts/prompt-minimal.md` 1181 tok. Next wave re-measures but does NOT rewrite.

## 5pp tolerance (pre-registered)

Minimal is **acceptable** if on the 24 well-formed tasks (6×4), averaged over **3 reps per variant per model**, temp>0 or seed-permuted order, **per model**:

```
| selection_min − selection_full | ≤ 0.05
| argument_min  − argument_full  | ≤ 0.05   (harness validation is PRIMARY; strict expected-equality is SECONDARY)
```

Same tolerance reported for `task_success`. Report per model and pooled. Raw counts (not only percentages) and token/accuracy curve `X = description_tokens(minimal)/description_tokens(full)` vs `Y = selection/argument` are primary. Prior single-rep baseline: selection delta 0.000 within, argument harness delta 0.042 within, strict delta 0.125 outside (driven by optional omission/wording that harness accepts — see `../report.md` §9).

Recovery gate (pre-registered, unchanged): ≥60% of typed rejections correctly recovered within 1 retry — recorded before run, not inferred post hoc; recovery metrics below.

## Token measurements (per variant, per call, per corpus)

| Metric | Scope | Tokenizer | Source |
|---|---|---|---|
| `description_tokens` | Capability-description block only (per spec §4.2) | `tiktoken cl100k_base 0.14.0` | `schemas/full.json` vs `schemas/minimal.json` via `compute_tokens.py` / `harness-bridge/run.py --measure-tokens` |
| `total_input_tokens` | Full prompt in (description block + instructions + user request + harness wrapper) | `cl100k_base 0.14.0` | Live runner log `input_tokens` |
| `total_output_tokens` | Model output (tool-call JSON) | `cl100k_base 0.14.0` | Live runner log `output_tokens` |
| `ratio_minimal_over_full` | `description_tokens(minimal)/description_tokens(full)` | 0.290 (frozen) | Reported with named tokenizer only |
| `total_tokens_ratio` | `total_input_tokens(minimal)/total_input_tokens(full)` | Optional | Aggregated |

## Success metrics (per variant, per model, over 24 tasks × 3 reps)

| Metric | Definition | Denominator |
|---|---|---|
| `selection_success` | `correct_op_selected / total_calls` (exact stable ID) | 24 tasks × 3 reps |
| `argument_success (harness)` | `calls with executed:ok / total_calls` (authoritative JSON Schema, Draft-07) judged via authoritative.json, not minimal | same |
| `argument_success (strict)` | `submitted arguments == expected_args` (subset equality) | same — reported secondary |
| `task_success` | `selection ∧ argument(harness) ∧ executed:ok` | same |
| `validation_failures` | count where `ValidationFailed` before execution | +12 malformed |
| `retries` | count of corrected retries after ValidationFailed | per malformed |
| `one_retry_success` | `successful_retry_on_first_attempt / total_rejections` | 12 per model |
| `second_retry_success` | `successful_on_second_enriched_attempt / failed_first_retries_with_empty_string` | ≤3 per model (only empty-string minLength/pattern) |
| `multi_retry_success` | `successful_within_2_retries / total_rejections` | 12 per model |

## Latency metrics (per call, per model, per variant)

| Metric | Definition |
|---|---|
| `latency_ms` | Per-call wall time harness.dispatch→response/error (ms) |
| `p50` | Median latency per variant per model |
| `p95` | 95th percentile per variant per model |
| `retry_latency_ms` | Latency for retry calls (first and second) |

## Recovery-specific metrics (12 malformed, per model)

| Metric | Definition |
|---|---|
| `recovery_tokens` | Input+output tokens for corrected retry call |
| `second_retry_prompt_tokens` | Tokens for enriched constraint text (field+constraint+message+example) — not full schema |
| `total_tokens_incl_failed` | failed call + error + retry prompt + correction (and second-retry if fired) |
| `invents_info` | whether corrected call invents unrelated optional params |
| `changes_unrelated` | whether corrected call changes args beyond indicated field |

## Adversarial metrics (4 D1-D4, harness-deterministic)

| Metric | Definition |
|---|---|
| `distinct` | `code` alone distinguishes D1 UnknownOperation vs D2 ValidationFailed vs D3 PolicyDenied vs D4 OutputValidationFailed (runtime:output) |
| `no_execution` | no execution before/instead of success return |

## Log schemas for next wave

Per-trial JSONL under `next-wave/measurements/logs/`:

- `ab_<model>_<variant>_r<rep>.jsonl` (well-formed 24 per rep per variant) — schema mirrors `../measurements/summary.json` and `../../harness/README.md`.
- `recovery.jsonl` (12 per model, plus second-retry enrichment rows under `second_retry/logs/`) — per-case typed error, first retry, second retry if triggered, tokens, invents check.
- `adversarial.jsonl` (4 rows, shared) — D1-D4.

Placeholders (filed now, overwritten live):

- `measurements/multi_rep_summary.json` — aggregated 3-rep per-model per-variant per-class rates, delta, within_5pp, tokens, p50/p95.
- `measurements/model_comparison.json` — cross-model table (openai/gpt-4o-mini vs open model), delta across models, harness vs strict gap.
- `measurements/second_retry/schema.json` + `README.md` + `logs/.gitkeep` — second-retry log schema.

## EDASES reuse note (measurements level)

Same corpus-530 (17-op schemas 0.1.0, full vs minimal prompts) is reused verbatim for the later **EDASES vs conventional** comparison. Keep `authoritative.json` unchanged; swap only the model-facing block and prompt. `harness-bridge/run.py` stays unchanged — swap only the runtime (`Runtime`/`Harness` interface) and record `harness_variant: conventional|edases` alongside pinned versions (`tiktoken 0.14.0`, `jsonschema 4.26.0`, `harness 0.1.0`, `schemas 0.1.0`). See `../EDASES_A_B.md`.

## Computation helpers

- Compute helper (already exists, reused): `../measurements/compute_tokens.py` (cl100k_base 0.14.0 when installed), `../measurements/compute_latency.py`.
- Next-wave extended helper (next live session): `next-wave/measurements/live_run_next.py` (to be added) — 3 reps ×2 variants ×2 models, seed-permuted order, second-retry loop, writes to `next-wave/measurements/logs/` and aggregates to `multi_rep_summary.json` + `model_comparison.json`.

## WHAT-NOT-TESTED (measurement negative-space disclosure)

- No live model or latency measured in this scaffolding commit — all timing/token aggregates are placeholders.
- Single-rep 07dfab42 baseline retained; significance requires ≥3 reps per model (not yet collected).
- No second-retry live evidence yet; counts bounded at ≤24 second retries per wave.
- No EDASES state harness added here; measurements for it share these definitions when it lands.
