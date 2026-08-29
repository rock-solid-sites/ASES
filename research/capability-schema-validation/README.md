---
title: Capability/Schema Validation — Research Index
program: EDASES
layer: Research
document_type: Guide
status: Active
authority: Derived
canonical_repository: edases
depends_on:
  - .design/capability-schema-validation.md
consumed_by:
  - research/capability-schema-validation/report.md
---

# Capability/Schema Validation — Research Index

Target architecture (non-negotiable framing):

```
agent → sandbox → small preselected capability API → authoritative execution/runtime
```

This directory is the sole home for the #498 swarm artifacts per `.design/capability-schema-validation.md` §10.

## Layout

```
research/capability-schema-validation/
├── README.md                          # This file — index + reproduction entry point
├── capabilities/
│   ├── authoritative/
│   │   └── schemas.json               # Full runtime schemas (canonical, version 0.1.0, 14 ops)
│   ├── derived/
│   │   ├── variant-a.json             # Full schema per §4 (31.7K chars, ~7941 tokens)
│   │   ├── variant-b.json             # Short desc + names/types (~2322 tokens)
│   │   └── variant-c.json             # Stable ID + one-line (≤20 words) + names/types (~1985 tokens)
│   └── manifest.json                  # {capabilities, version, derived_from, token counts, categories}
├── harness/
│   ├── README.md                      # How to run the harness
│   ├── error-codes.md                 # Typed error taxonomy (9 codes)
│   ├── sandbox.py                     # Preselected-surface gate (exact match only)
│   ├── runtime.py                     # Authoritative validation + policy + dispatch
│   └── run.py                         # CLI entry point (--smoke, --measure-tokens, --op/--args)
├── tests/
│   ├── test-a/
│   │   ├── protocol.md                # Pre-registered protocol + 22-task set + 5pp tolerance
│   │   └── results.md                 # Written by Phase 1 Track A
│   ├── test-b/
│   │   ├── protocol.md                # Written by Phase 1 Track B
│   │   └── results.md
│   ├── test-c/
│   │   ├── protocol.md
│   │   ├── results.md
│   │   └── schemas/
│   │       ├── c1/                    # Compatible additive mutation (Phase 1 Track C)
│   │       ├── c2/                    # Incompatible param mutation
│   │       ├── c3/                    # Incompatible output mutation
│   │       └── c4/                    # Removal / renaming
│   ├── test-d/
│   │   ├── protocol.md
│   │   └── results.md
│   └── test-e/
│       ├── protocol.md
│       ├── results.md
│       └── scripts/                   # Per-property scripts (Phase 2)
├── logs/
│   ├── test-a/                        # Raw harness logs per test
│   ├── test-b/
│   ├── test-c/
│   ├── test-d/
│   └── test-e/
└── report.md                          # Final 10-section synthesis (Phase 3, per §8)
```

## Reproduction entry point

From the repository root, after checking out `feature/pp3g-1eHz-phase-0-setup-for-498-capability-set-10-20-ops-be69`:

```bash
# 1. Inspect the harness
cat research/capability-schema-validation/harness/README.md
python research/capability-schema-validation/harness/run.py --help

# 2. Smoke validation (Phase 0 gate: valid→execute, malformed→rejected before execution)
python research/capability-schema-validation/harness/run.py --smoke

# 3. Token/char measurement (reports tiktoken cl100k_base when installed, else heuristic)
python research/capability-schema-validation/harness/run.py --measure-tokens

# 4. Single ad-hoc calls (examples covering 6 categories)
python research/capability-schema-validation/harness/run.py --op search_artefacts --args '{"query":"hello","limit":5}'
python research/capability-schema-validation/harness/run.py --op get_artefact --args '{"id":"art_abc-123"}'
python research/capability-schema-validation/harness/run.py --op create_review --args '{"artefact_id":"art_abc-123","verdict":"approve","rationale":"Rationale with enough length for validation"}'
python research/capability-schema-validation/harness/run.py --op set_severity --args '{"artefact_id":"art_abc-123","level":"high"}'
python research/capability-schema-validation/harness/run.py --op query_metrics --args '{"filter":{"type":"spec"},"group_by":"status","include_facets":true}'
python research/capability-schema-validation/harness/run.py --op submit_evidence --args '{"artefact_id":"art_abc-123","evidence_items":[{"source":"paper","content":"text"}]}'

# 5. Run per-test harnesses (each independently runnable; written in Phases 1–2)
python research/capability-schema-validation/tests/test-a/run.py   # Test A (Phase 1 Track A)
python research/capability-schema-validation/tests/test-b/run.py   # Test B
python research/capability-schema-validation/tests/test-c/run.py   # Test C
python research/capability-schema-validation/tests/test-d/run.py   # Test D
python research/capability-schema-validation/tests/test-e/run.py   # Test E (requires remote transport for full matrix)

# 6. Read the synthesis (Phase 3)
cat research/capability-schema-validation/report.md
```

Exact per-test commands are finalized in each `tests/test-*/protocol.md` during Phases 1–2.

## Design source

`.design/capability-schema-validation.md` — swarm-ready design for #498 (7 gating questions, capability set 10–20 ops, variants A/B/C, Tests A–E protocols with acceptance criteria, harness architecture, 10-section report outline, 4-phase swarm Plan).

## Phase 0 gate (to enter Phase 1)

* Capability set covers all six categories (14 ops) with `version: 0.1.0` on every op — `capabilities/authoritative/schemas.json`.
* Variants A/B/C generated and checked in — `capabilities/derived/variant-{a,b,c}.json` (C/A 0.25, B/A 0.292).
* Harness runs smoke gate — `python research/capability-schema-validation/harness/run.py --smoke` (valid→execute, malformed→rejected before execution).
* Error taxonomy committed — `harness/error-codes.md`.
* Task set + pre-registered thresholds committed — `tests/test-a/protocol.md` (22 tasks, 5pp tolerance, ≥3 repetitions, tiktoken cl100k_base).

## Retired scope (explicitly excluded, per design §9)

MCP idle-timeout/pooling, eager-vs-lazy MCP process matrices, ToolRegistry C2 fleet frequency, ToolRegistry private-internal extensions, MCP-specific rolling-upgrade behavior. Reintroduction requires an intervention log with trigger and justification.

## WHAT-NOT-TESTED (Phase 0)

* Phase 0 does not run Tests A–E; it lays the invariant artifacts those tests depend on. No claim about accuracy, validation fidelity, drift handling, authority separation, or transport semantics is supported by Phase 0 alone.
* Token counts reported here are heuristic `char/4` (tiktoken measured at harness runtime). No claim of production token cost without a named tokenizer version (§4.2).
