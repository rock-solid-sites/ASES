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

> **Current research navigation (2026-11-24).** This is a retained EDASES-derived research series, not a current execution architecture, capability authorization or mandatory test program. Upstream EDASES currency has not been verified. The original setup description below is preserved for reproducibility; its historical branch, harness, launch and orchestration instructions are not current operating instructions.

## Experimental sequence and present evidence

The two experiments address a common question: how much tool information must be shown to a model, when validation and authorization are enforced at the actual runtime boundary? The earlier experimental architecture is an object of investigation, not an imposed realization of the current ASES Kernel.

| Evidence stage | Result and limit |
| --- | --- |
| [#498 A–E synthesis](report.md) and [Test A proxy results](tests/test-a/results.md) | 14 operations, 22 tasks, three description variants; 73.3% description-token reduction, 98.4% minimal proxy argument accuracy versus 100% full; 20/20 malformed calls rejected and 20/20 **scripted** corrections (Test B). These are harness/proxy findings, not a live model's accuracy or correction rate. The confusing [test-a-live results path](tests/test-a-live/results.md) also explicitly reports proxy evidence, not a live LLM experiment. |
| [Test C drift](tests/test-c/results.md), [Test D authority separation](tests/test-d/results.md), [Test E transport](tests/test-e/results.md) | Scoped schema/version/authority checks and loopback TCP/subprocess results; seven required transport properties passed in the tested setup. The earlier synthesis uses loose remote/cross-host language: the transport record establishes loopback and a process boundary, not cross-host partitions, TLS or production network behavior. The then-conditional exclusion of streaming and durable operations concerned that discrete-operation experiment only, not current Work Unit continuity or model-streaming requirements. |
| [#530 Phase 0 corpus audit](audit-validation-brief-corpus-vs-spec.md) | The methodology-brief corpus and tool-calling corpus have distinct domains. Both were retained; do not combine them because each has 24+12+4 cases. |
| [Corpus 530](corpus-530/README.md), [live A/B report](corpus-530/report.md), [machine-readable summary](corpus-530/measurements/summary.json) | 17-operation corpus; one live GPT-4o-mini route and one repetition per variant (48 A/B trials), 12 recovery trials and four deterministic adversarial cases. See the separate harness and strict expected-argument outcomes below. |
| [Next-wave plan](corpus-530/next-wave/PLAN.md), [second-retry design](corpus-530/next-wave/SECOND_RETRY.md), [EDASES A/B preparation](corpus-530/next-wave/EDASES_A_B.md) | Prospective experiments only at the reviewed source revision. The 288 planned A/B trials across two models and three repetitions, second live recovery attempt and conventional-vs-EDASES runtime comparison are not completed results. [Multi-rep summary](corpus-530/next-wave/measurements/multi_rep_summary.json) and [model comparison](corpus-530/next-wave/measurements/model_comparison.json) retain null measurement fields. These are preserved proposals, not a current execution queue or authority to launch models. |

### Corpus 530 measured distinction

| Measure | Full | Minimal | Interpretation |
| --- | ---: | ---: | --- |
| Description-block tokens (cl100k_base 0.14.0) | 8,915 | 2,588 | 71.0% reduction; not whole-request token saving or measured money saved |
| Operation selection | 24/24 | 24/24 | No observed difference in this sample |
| Harness-valid arguments | 23/24 | 22/24 | 4.2 percentage-point loss; within the five-point threshold |
| Strict expected arguments | 23/24 | 20/24 | 12.5 percentage-point loss; outside threshold |

The [summary JSON](corpus-530/measurements/summary.json) uses strict argument equality for its main aggregate, so its `within_5pp: false` is consistent with the report's **harness-based** pass. Do not merge the two metrics or silently prefer the more favorable one. Schema validity is not preservation of task intent; conversely exact literal equality may penalize semantically acceptable alternatives, so interpret individual disagreements against the actual task. In the live recovery sample, 8/12 corrected calls were harness-valid but only 4/12 strictly matched the expected correction, compared with 20/20 scripted recovery in the earlier series. Content-length failures and the parse failure remain evidence of limitations. D1–D3 discriminate input-side denial boundaries; D4 exercises a manual output-validator check after a successful input execution and returns the literal ValidationFailed code with an output boundary. It does not establish four distinct literal codes, absence of execution in D4, or automatic post-execution output validation in the normal call path.

### Retained principles and current authority

Stable operation identity, small task-relevant descriptions, complete authoritative validation at the effect boundary, typed error evidence, and separating capability exposure from actual authorization remain useful research findings and design candidates. The single-model experiment does not establish universal compression sufficiency, equivalent intent preservation, live recovery reliability or an adopted EDASES-specific runtime. Its description/token and accuracy results are distinct from model routing, provider entitlement and resource authorization. Current requirements and realization decisions are governed by the [Execution Engine Vision](../../docs/architecture/Execution%20Engine%20Vision.md), [Kernel-0 Evidence Packet](../../docs/research/kernel-0/Kernel-0-Evidence-Packet.md), [Realization and Assurance Selection Method](../../docs/methodology/Implementation%20Realization%20and%20Assurance%20Selection%20Method.md), [task-scoped information method](../../docs/methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md), and applicable [current skills](../../skills/current/README.md). The Resource Solver operation-to-route crosswalk remains separate experimental research ([PR #62](https://github.com/rock-solid-sites/ASES/pull/62), WNASES-17 / ASES-20); it is not adopted by these observations.

**Reproducibility:** preserve the [strict corpus freeze](corpus-530/next-wave/NO_MODIFY_CORPUS.md), including schemas, tasks, prompts, manifests and bridge scripts. Preserve original reports, raw logs, measurement templates and runner history; new experiments require their own explicit scope, source pins and approved funding/route. The source revision reviewed here is [97415b6d](https://github.com/rock-solid-sites/ASES/tree/97415b6df7206a2b946baab9057776efadc4d7c7/research/capability-schema-validation). No experiment was re-run in this reconciliation. Use this index to find evidence rather than treating the retained commands, old Crosslink synchronization or proposed model substitutions as an active workflow.

## Preserved #498 setup and reproduction record

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
