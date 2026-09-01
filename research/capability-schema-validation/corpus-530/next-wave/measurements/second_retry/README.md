---
title: Second-Retry Logs — Next-Wave 530 (empty-string recovery)
program: EDASES
layer: Research
document_type: Specification
status: Active
authority: Derived
canonical_repository: edases
issue: 530
---

# Second-Retry Logs — Corpus-530 Next Wave

Logs for the **second retry** that fires only on **minLength/pattern empty-string** failures (`got == '""'`, constraint ∈ {minLength, pattern}) after the first retry failed. See `../../SECOND_RETRY.md` for trigger predicate and enrichment design.

## Placement

- **Per-row JSONL:** `next-wave/measurements/second_retry/logs/*.jsonl` — one row per triggered second retry (at most 3 per model per wave, observed R01,R05,R10 empty-string cases).
- Also mirrored as `measurements/logs/recovery.jsonl` rows with `retry_number=2` when that file aggregates.

## Row shape

Schema: `schema.json` in this directory. Key fields:

- `parent_id` (e.g., `R01`, `R05`, `R10`) — links to first retry row `id`.
- `field` / `constraint` / `got` / `first_retry_error` — the failing ValidationFailed for the empty string.
- `example_valid_value` — similar valid example from corpus (e.g., `query:"hello"`, `evidence_items.0.content:"evidence text from experiment"`, `rationale:"This rationale has enough length to pass hidden minLength ten"`) — **not** a schema excerpt.
- `second_retry_prompt_text` / `second_retry_prompt_tokens` — enriched constraint text (field+constraint+message+example), `cl100k_base 0.14.0` counted, **without full schema** (guard forbids `$schema`, `inputSchema`, `additionalProperties`, or a JSON Schema block).
- `second_retry_raw_output` / `op_corrected` / `args_corrected` / `parse_error` / `second_retry_validation_result` / `second_retry_error` / `second_retry_executed` / `second_retry_success`.

## What is NOT logged here

- First retry rows remain under `measurements/logs/recovery.jsonl` per model (12 per model).
- No full `authoritative.json` or other op schemas are included in the row — guard checked by `harness-bridge/second_retry.py --check-examples`.

## Non-goals

Scaffolding only — no EDASES state harness added here; logs are harness-agnostic and apply equally to conventional vs EDASES conditions once that comparison lands.

## Guard

```bash
python research/capability-schema-validation/corpus-530/next-wave/harness-bridge/second_retry.py --check-examples  # no $schema / inputSchema leak
python research/capability-schema-validation/corpus-530/next-wave/harness-bridge/second_retry.py --self-test     # trigger predicate + examples clean
```
