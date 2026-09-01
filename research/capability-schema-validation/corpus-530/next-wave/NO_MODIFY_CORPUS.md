---
title: No-Modify-Corpus Guard — #530 Next-Wave Freeze
program: EDASES
layer: Research
document_type: Note
status: Active
authority: Derived
canonical_repository: edases
issue: 530
---

# No-Modify-Corpus Guard

Any edit to the frozen files below invalidates the corpus and requires a new version + fresh issue. This file is the explicit guard copy referenced by `README.md`, `PLAN.md`, and `measurements/README.md`.

## Frozen paths (relative to repo root)

```
research/capability-schema-validation/corpus-530/schemas/authoritative.json
research/capability-schema-validation/corpus-530/schemas/full.json
research/capability-schema-validation/corpus-530/schemas/minimal.json
research/capability-schema-validation/corpus-530/tasks.json
research/capability-schema-validation/corpus-530/malformed-recovery.json
research/capability-schema-validation/corpus-530/adversarial.json
research/capability-schema-validation/corpus-530/corpus.jsonl
research/capability-schema-validation/corpus-530/prompts/prompt-full.md
research/capability-schema-validation/corpus-530/prompts/prompt-minimal.md
research/capability-schema-validation/corpus-530/prompts/prompt-full.template.md
research/capability-schema-validation/corpus-530/prompts/prompt-minimal.template.md
research/capability-schema-validation/corpus-530/prompts/manifest.json
research/capability-schema-validation/corpus-530/manifest.json
```

Also covered: `harness-bridge/run.py` and `harness-bridge/validate.py` are frozen (shims over `../harness/`, not corpus data but ordered harness-bridge); any functional change to `run.py` must be recorded separately and is NOT allowed as part of this scaffolding-only wave without operator approval.

## Check

```bash
git diff -- research/capability-schema-validation/corpus-530/schemas/ \
  research/capability-schema-validation/corpus-530/tasks.json \
  research/capability-schema-validation/corpus-530/malformed-recovery.json \
  research/capability-schema-validation/corpus-530/adversarial.json \
  research/capability-schema-validation/corpus-530/corpus.jsonl \
  research/capability-schema-validation/corpus-530/prompts/
# must be empty on this branch relative to main
```

## Pinned versions bound to frozen corpus

- `tiktoken==0.14.0` `cl100k_base`
- `jsonschema==4.26.0`
- `schemas==0.1.0`, `harness==0.1.0`
- `ToolRegistry 0.15.0 / MCP 2.0.0` (retired scope, version-bound prior work)

## 5pp tolerance bound to frozen corpus

Minimal acceptable if `|sel_min − sel_full| ≤0.05` AND `|arg_min − arg_full| ≤0.05` (harness validation primary) on 24 tasks, ≥3 reps, temp>0 or seed-permuted order.

## What IS allowed in `next-wave/`

- Docs (`PLAN.md`, `SECOND_RETRY.md`, `EDASES_A_B.md`, `README.md`, `measurements/*`)
- Harness extension: `harness-bridge/second_retry.py` (additive recovery, does NOT edit `run.py`)
- Measurement scaffolding under `next-wave/measurements/` (templates with placeholders, not corpus edits)
