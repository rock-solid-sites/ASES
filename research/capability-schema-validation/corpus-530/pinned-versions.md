---
title: Pinned Versions — #530 Corpus
program: EDASES
layer: Research
document_type: Reference
status: Active
authority: Derived
canonical_repository: edases
issue: 530
---

# Pinned Versions (530)

Recorded for reproducibility; live run must echo these versions in logs.

| Component | Version | Source | Notes |
|---|---|---|---|
| `schemas` | `0.1.0` per op and global | `corpus-530/schemas/authoritative.json` `version` | 17 ops (14 base + 3 similar tools); extends `capabilities/authoritative/schemas.json@0.1.0` |
| `tokenizer` | `tiktoken==0.14.0` `cl100k_base` | `harness/run.py --measure-tokens` + `measurements/compute_tokens.py` | Reportable; heuristic `chars/4` only when tiktoken absent, flagged `heuristic` |
| `jsonschema` | `4.26.0` | `harness/runtime.py` Draft7Validator | Fallback validator if not installed, but production requires Draft-07 |
| `ToolRegistry` | `0.15.0` | design §9 retired scope | Version-bound prior work; not exercised (no lifecycle/discovery/pooling/idle-timeout added) |
| `MCP` | `2.0.0` | design §9 retired scope | Same |
| `harness` | `0.1.0` | `harness/sandbox.py` + `harness/runtime.py` (sandbox→validation→policy→execution ordering) | Exact-ID gate, no fuzzy; ordering trace `sandbox→validation→policy→execution` |
| `model` | placeholder | live session fills | provider, temperature, harness version per log row |
| commits | `17ed2631` (A) `fbca4975` (B) `baa35bf7` (C) `b719ca30` (D) `dcf4f313` (E) + this corpus `pp3g-squu` | prior swarm | For 5pp tolerance baseline reference |

**Generation timestamp:** `2026-09-01T00:00:00Z` (schemas `generated_at`).

