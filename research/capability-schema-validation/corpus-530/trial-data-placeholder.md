---
title: Trial Data Placeholder — #530 Live Run
program: EDASES
layer: Research
document_type: Specification
status: Draft
authority: Derived
canonical_repository: edases
issue: 530
---

# Trial Data Placeholder (530)

Machine-readable trial data schema for live real-model A/B — reusable verbatim for EDASES comparison.

## Files

- `measurements/logs/*.jsonl` — one JSON object per call (variant × task × rep). Schema per `measurements/token-latency-scaffolding.md`.
- `measurements/summary.json` — aggregate placeholder (filled live).
- `corpus.jsonl` — authoritative 40-line corpus (input).

## Placeholder log row

```json
{"corpus":"530","variant":"minimal","task_id":"C5-T17","class":5,"repetition":1,"model":"placeholder","provider":"placeholder","temperature":0.7,"description_tokens":2588,"total_input_tokens":3500,"total_output_tokens":45,"op_selected":"search_users","arguments_submitted":{"query":"Alice"},"selection_correct":true,"arguments_correct":true,"task_success":true,"validation_result":"executed:ok","error":null,"executed":true,"latency_ms":120}
```

## Next session

Fill `model/provider/temperature/harness_version/tokenizer` per row; compute `description_tokens` via `measurements/compute_tokens.py` (cl100k_base 0.14.0); compute p50/p95 via `measurements/compute_latency.py`.

