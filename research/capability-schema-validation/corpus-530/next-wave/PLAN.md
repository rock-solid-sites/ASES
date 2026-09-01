---
title: Next-Wave Multi-Rep / Multi-Model Plan — Corpus-530 (strict freeze)
program: EDASES
layer: Research
document_type: Plan
status: Active
authority: Derived
canonical_repository: edases
issue: 530
---

# Multi-Rep / Multi-Model Plan — Next Live Wave for Corpus-530

**WHY** — The single-rep single-model evidence (openai/gpt-4o-mini, 48 A/B 95.8% vs 91.7% harness delta 4.2pp within 5pp, 71% token saving, recovery 4/12 strict) is the cheapest discriminating test, not publication-grade. The question requires significance (≥3 reps) and cross-model generality (open model via OpenRouter) before claiming minimal preserves reliability.

**WHAT** — This doc is the plan for the *next* live session. It fixes the design without running it now. Corpus-530 schemas/tasks/prompts stay verbatim; prompts are not rewritten; schemas are not regenerated.

**HOW CERTAIN** — Evidence-based scaffolding only; no live calls in this commit. The plan is checkable: rep counts, model IDs, seed-permuted order, and file paths are explicit.

**WHAT-NOT-TESTED** — No live trials yet; no significance claim; no second-retry live evidence; no EDASES harness added here (prep doc only).

## Frozen inputs (strict no-modify rule)

These files are copied verbatim, not regenerated:

- `research/capability-schema-validation/corpus-530/schemas/authoritative.json` — 17 ops 0.1.0, Draft-07, hidden constraints retained (numeric range 1-100, pattern ^art_..., ^cur_..., semver, uri, date-time, mutually constrained filter.type↔group_by, relation↔bidirectional, additionalProperties:false, maxLength) — runtime truth.
- `schemas/full.json` (Variant A, 8915 tokens cl100k_base 0.14.0) vs `schemas/minimal.json` (Variant B, 2588 tokens, ratio 0.290, all summaries ≤20w, enum literals visible) — model-facing blocks swapped only.
- `prompts/prompt-full.md` vs `prompts/prompt-minimal.md` — templates with `{{user_request}}` substitution; ordering identical; hidden-constraint notice present only in minimal.
- `tasks.json` (24 tasks in 6×4 classes), `malformed-recovery.json` (12), `adversarial.json` (4 D1-D4), `corpus.jsonl` (40 lines).

**Guard:** Before any live run, `harness-bridge/run.py --smoke` must still be 18/18 and `harness-bridge/validate.py` must pass 40 lines / 6×4 / enums / ≤20w / distinct codes.

## Design

### Repetitions: 3 reps per variant per brief (per model)

- **Per model:** Each of the 24 well-formed tasks runs once per rep × 2 variants = 48 per rep set. With 3 reps: 24×2×3 = **144 A/B trials per model**.
- **Total A/B across 2 models:** 144×2 = **288 well-formed trials**.
- **Recovery (Test C):** 12 malformed cases × 2 models = 24 base correction trials; plus second-retry harness where triggered (minLength/pattern empty-string, see SECOND_RETRY.md) — at most +24 second-retry calls if every correction fails with empty string. Bounded total recovery attempts ≤48 per wave.
- **Adversarial (Test D):** 4 cases × 2 models is not needed (D is harness-deterministic, no model) — run once via harness and log under `adversarial.jsonl` (4 rows), shared across models.

### Models: 2 via OpenRouter (keep current + one open)

- **Model 1 (anchor, keep current):** `openai/gpt-4o-mini` via `openrouter`, version pinned at run time (report `fp_*` if returned), temperature `0.0` with seed 42 on prior run; next wave uses **temperature 0.7 for discriminating reps** (brief: temp>0 or permutation required for significance) — record actual.
- **Model 2 (open, via openrouter):** One open model. Operator choice at live-run time; current recommender cheapest suitable is `minimax/minimax-m2.5` or `qwen/qwen-2.5-72b-instruct` via same gateway — record exact `model_id` returned by OpenRouter. Fallback if unavailable: any open instruct model ≥7B with JSON tool-call history (e.g., `meta-llama/llama-3.1-70b-instruct`, `qwen/qwen-2.5-72b-instruct`, `deepseek/deepseek-chat`) — must be **open weights** per brief.

Pin in logs per row: `model_id`, `provider="openrouter"`, `temperature`, `seed`, `tool_calling_config="json_object mode, prompt demands JSON {op_id,arguments}, no function-calling API, parse timeout 2s"`, `system_prompt="prompts/prompt-full.md vs prompt-minimal.md"`, `harness_version="0.1.0"`, `schemas_version="0.1.0"`, `tokenizer="tiktoken cl100k_base 0.14.0"`.

### Order: seed-permuted

- Base seed `42` (as prior 07dfab42). For each rep `r ∈ {0,1,2}`, shuffle the 48 jobs (24 full + 24 minimal, same instances) with `random.Random(42 + r)`.
- This holds task set identical across variants while randomizing condition order per brief (required for unbiased position).
- Malformed recovery order is file order (R01→R12) plus any triggered second retries appended; adversarial order D1→D4.

### Fixed prompts/schemas verbatim

- No rewriting of prompts or regeneration of schemas between reps or models. The only varying inputs are `variant` (full vs minimal block) and `rep` (order seed + temperature if >0). Prompts stay frozen templates; schemas stay frozen files.

## Counts at a glance

| Cell | n (per model) | n (total 2 models) |
|------|---------------|-------------------|
| A full well-formed | 24×3 = 72 | 144 |
| B minimal well-formed | 24×3 = 72 | 144 |
| **Total A/B well-formed** | 144 per model | **288** |
| Test C recovery (first retry) | 12 per model | 24 |
| Second retry (triggered only) | ≤12 per model | ≤24 |
| Test D adversarial (harness) | 4 (shared) | 4 |

## Measurements (per brief workflow)

Per trial (JSONL row) — same schema as `../measurements/summary.json` and `../measurements/token-latency-scaffolding.md`:

- `description_tokens` (full 8915 vs minimal 2588, ratio 0.290, tokenizer `tiktoken cl100k_base 0.14.0`)
- `total_input_tokens`, `total_output_tokens` (tool-call JSON)
- `selection_correct`, `arguments_correct` (harness validation vs expected), `task_success`, `validation_result`, `error {code, field, constraint, got, message, boundary}`, `executed`, `trace`
- `retries` (0 for A/B, 1 for recovery first retry, up to 2 with second retry)
- `latency_ms`, `p50/p95` per variant per model
- Recovery: `correction_tokens`, `total_tokens_incl_failed`, `invents_info`, `changes_unrelated`, `one_retry_success`, `second_retry_success`
- Adversarial: `expected_code`, `code_returned`, `boundary`, `distinct`, `no_execution`

Aggregated templates produced next wave under `next-wave/measurements/`:

- `measurements/multi_rep_summary.json` — per-variant per-model per-class rates (selection/argument/task), delta, within_5pp, tokens, p50/p95; placeholder now, filled live.
- `measurements/model_comparison.json` — cross-model table (openai/gpt-4o-mini vs open model) per variant, delta across models, harness vs strict gap.
- `measurements/second_retry/` — second-retry log schema + logs placeholder for enriched retries.

## 5pp tolerance (pre-registered, unchanged)

Minimal acceptable if on the 24 well-formed tasks, averaged over 3 reps, **per model**:

```
| selection_min − selection_full | ≤ 0.05
| argument_min  − argument_full  | ≤ 0.05  (harness validation is primary; strict expected-equality reported secondary)
```

Reported per model and pooled. Prior single-rep evidence: selection delta 0.000 within, argument harness delta 0.042 within, strict delta 0.125 outside (driven by optional omission/wording, see report §9). Token/accuracy curve X=`description_tokens(minimal)/description_tokens(full)` vs Y=selection/argument is primary.

## Reproduction (scaffolding only — no live calls yet)

```bash
# frozen corpus still intact (18/18 smoke includes 3 similar tools, hidden range/pattern, array/object constraints)
python research/capability-schema-validation/corpus-530/harness-bridge/run.py --smoke
python research/capability-schema-validation/corpus-530/harness-bridge/validate.py
python research/capability-schema-validation/corpus-530/measurements/compute_tokens.py

# next-wave scaffolding self-tests (no network, no model)
python research/capability-schema-validation/corpus-530/next-wave/harness-bridge/second_retry.py --self-test
python research/capability-schema-validation/corpus-530/next-wave/harness-bridge/second_retry.py --check-examples
# verify templates are valid JSON
python -c "import json,pathlib; print(json.loads(pathlib.Path('research/capability-schema-validation/corpus-530/next-wave/measurements/multi_rep_summary.json').read_text())['corpus'])"
python -c "import json,pathlib; print(json.loads(pathlib.Path('research/capability-schema-validation/corpus-530/next-wave/measurements/model_comparison.json').read_text())['corpus'])"
```

Next live session (deferred):
```bash
# requires OPENROUTER_API_KEY via ~/.local/share/opencode/auth.json or env
MODEL_ID=openai/gpt-4o-mini TEMPERATURE=0.7 python research/capability-schema-validation/corpus-530/next-wave/measurements/live_run_next.py --model openai/gpt-4o-mini --reps 3 --variants full,minimal --seed 42
MODEL_ID=qwen/qwen-2.5-72b-instruct TEMPERATURE=0.7 python research/capability-schema-validation/corpus-530/next-wave/measurements/live_run_next.py --model qwen/qwen-2.5-72b-instruct --reps 3 --variants full,minimal --seed 42
# logs → next-wave/measurements/logs/ab_<model>_<variant>_r<rep>.jsonl, recovery, second_retry, adversarial
# summaries → next-wave/measurements/multi_rep_summary.json + model_comparison.json (overwrites placeholders)
```

## Stop condition for this scaffolding phase

This scaffolding phase stops before any live model call. Deliverable is docs + harness module + templates under `next-wave/` with `harness-bridge smoke 18/18` passing. No corpus files modified (checked via `git diff -- research/capability-schema-validation/corpus-530/schemas/ research/capability-schema-validation/corpus-530/tasks.json research/capability-schema-validation/corpus-530/prompts/`).

## Dependencies

- `../manifest.json`, `../pinned-versions.md` (tiktoken 0.14.0 cl100k_base, jsonschema 4.26.0), `../tolerance.md` (5pp), `../failure-taxonomy.md`, `../harness-reuse.md`.
- Prior live report `../report.md` (07dfab42) — baseline not overwritten; next summary under `next-wave/measurements/multi_rep_summary.json`.
