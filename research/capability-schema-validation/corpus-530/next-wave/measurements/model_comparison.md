---
title: Model Comparison Template — Next-Wave 530 (2 models, 3 reps)
program: EDASES
layer: Research
document_type: Specification
status: Active
authority: Derived
canonical_repository: edases
issue: 530
---

# Model Comparison Template — 2 Models (gpt-4o-mini + open model via openrouter)

`measurements/model_comparison.json` is the machine-readable template; this doc is the human-readable description of that file.

## Design

- **Models:** `openai/gpt-4o-mini` (anchor, keep current from 07dfab42) + one open model via `openrouter` (operator choice at live time; recommender `qwen/qwen-2.5-72b-instruct` or `minimax/minimax-m2.5`). Both via same gateway, same `temperature 0.7`, same seed-permuted order, same frozen prompts/schemas.
- **Table (per model, averaged over 3 reps, 24 tasks × 3 = 72 per variant):** selection, arg harness, arg strict, task, p50/p95, recovery first-retry harness vs second-retry enriched.
- **Cross-model delta:** `|model2 - model1|` per variant for selection and arg harness; `minimal_sufficiency_consistent_across_models` = whether both models agree that minimal passes within_5pp.
- **Token/accuracy curve:** X = `2588/8915 = 0.290` (minimal/full description_tokens, `tiktoken cl100k_base 0.14.0`) vs Y = selection/arg per model per variant.

## Why this template exists before live data

So the next live session can write without deciding what to measure. `model_comparison.json` placeholders are overwritten live; `multi_rep_summary.json` feeds this template.

## EDASES reuse note

Same template structure applies when the EDASES harness comparison lands: add a `harness_variant` column (`conventional` vs `edases`) while reusing the same model comparison rows. Corpus freeze unchanged.

## Pinned versions & tolerance

- `tiktoken 0.14.0 cl100k_base`, `jsonschema 4.26.0`, `harness 0.1.0` `schemas 0.1.0`, 5pp `|sel_min-sel_full|≤0.05 AND |arg_min-arg_full|≤0.05` per model averaged over 3 reps.
