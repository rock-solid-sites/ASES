---
title: Corpus 530 — Real-Model Minimal Tool-Calling Corpus (24+12+4)
program: EDASES
layer: Research
document_type: Guide
status: Active
authority: Derived
canonical_repository: edases
issue: 530
---

# Corpus 530 — Real-Model Minimal Tool-Calling Corpus

**Issue:** #530 · **Branch:** `feature/pp3g-squu-phase-1-lay-out-correct-530-tool-calling-corpus-under`
**Status:** Scaffolding (no live model run) — reusable verbatim for EDASES A/B
**Authoritative:** `schemas/authoritative.json` (17 ops, 0.1.0, extends 14-op set 17ed2631)
**Minimal:** `schemas/minimal.json` (stable ID + ≤20w summary + names/types + required/optional + enum literals; hidden constraints NOT exposed)

## What this is

Tool-calling A/B corpus for the question: can a real model reliably select and construct tool calls from the **reduced description** while the runtime retains the **complete authoritative schema**? Previous round: 73.3% token reduction, 100% selection, 98.4% argument within 5pp, 20/20 malformed rejected, 20/20 scripted corrections from typed errors, enum literals must remain visible, output validation required. Remaining uncertainty (this corpus tests): correction was scripted, not real model.

Model-facing contract only — not connector lifecycle, MCP transport, or EDASES state machine. Establishes clean conventional baseline **reusable verbatim** for later EDASES-vs-Lexicon comparison.

## Layout

```
corpus-530/
├── manifest.json                    # counts, classes, pinned versions, reuse note
├── tasks.json / tasks.md            # 24 well-formed in 6×4 classes
├── malformed-recovery.json/.md      # 12 malformed recovery (missing required … +4 balanced)
├── adversarial.json/.md             # 4 adversarial D1-D4 distinct codes, no execution
├── corpus.jsonl                     # 40 lines consolidated (24+12+4)
├── schemas/
│   ├── authoritative.json           # 17 ops, 0.1.0, Draft-07, hidden constraints retained
│   ├── full.json                    # full baseline (Variant A) for token comparison
│   └── minimal.json                 # minimal (stable ID + ≤20w + names/types + required/optional + enum literals)
├── prompts/
│   ├── prompt-full.md               # full schema prompt (with capabilities block)
│   ├── prompt-minimal.md            # minimal prompt (hidden-constraint notice, ≤20w summaries)
│   ├── prompt-full.template.md      # template with {capabilities_block} placeholder
│   ├── prompt-minimal.template.md   # template with {capabilities_block} placeholder
│   └── manifest.json                # prompt registry, reuse invariant
├── failure-taxonomy.md              # D1 UnknownOperation / D2 ValidationFailed / D3 PolicyDenied / D4 OutputValidationFailed distinct
├── pinned-versions.md               # tiktoken 0.14.0 cl100k_base, jsonschema 4.26.0, ToolRegistry/MCP, 0.1.0
├── tolerance.md                     # 5pp threshold
├── harness-reuse.md                 # sandbox→validation→policy→execution (reuses ../harness/)
├── harness-bridge/                  # thin shims over ../harness with corpus-530 schemas path
│   ├── run.py
│   └── validate.py
└── measurements/
    ├── token-latency-scaffolding.md # description_tokens, total in/out, selection/argument/task, p50/p95, recovery metrics
    ├── compute_tokens.py            # tiktoken cl100k_base when installed
    ├── compute_latency.py           # p50/p95 from logs
    ├── summary.json                 # placeholders (filled live)
    └── logs/.gitkeep
```

## 6 Classes (4 each = 24)

| # | Class | Subtypes / note |
|---|---|---|
| 1 | Simple scalars | single scalar param |
| 2 | Enum-dependent | required/optional/multiple/semantically similar — literals must stay visible |
| 3 | Nested structures | object, array-of-objects, nested optional, nested enum |
| 4 | Required/optional ambiguity | omit/supply/multiple/similar meanings |
| 5 | Semantically similar tools | search_users / groups / projects close descriptions — stable ID discriminates |
| 6 | Constraint-sensitive hidden | 4 hidden: numeric range (1-100), string pattern/format (^art_..., semver, uri), mutually constrained (filter.type↔group_by), schema constraint (additionalProperties:false / maxLength) causing ValidationFailed without exposing to model |

## 12 Malformed Recovery + 4 Adversarial

- **12 malformed:** missing required, wrong type, invalid enum, invalid nested field, missing nested required, hidden range violation, invalid combination, malformed array/object +4 balanced. All `ValidationFailed` before execution; one-retry/multi-retry measured.
- **4 adversarial D1-D4:** D1 `UnknownOperation` (absent/hallucinated), D2 `ValidationFailed` (malformed bypass), D3 `PolicyDenied` (schema-valid but denied), D4 `OutputValidationFailed` (output shape). Distinct codes, no execution (D4 no success return), distinguishable by code alone.

## Minimal representation

Stable op ID + concise description (≤20 words) + names/types + required/optional + **enum literals visible**. ≤20w summaries verified. Hidden from minimal: `minimum/maximum, minLength/maxLength, pattern, format (uri/date-time/semver), additionalProperties:false, mutually-constrained rules`. Runtime (`authoritative.json`) retains and enforces; violation → typed `ValidationFailed`/`OutputValidationFailed`.

## Reproduction (no live model in this commit)

```bash
# tokens
python research/capability-schema-validation/corpus-530/measurements/compute_tokens.py
python research/capability-schema-validation/harness/run.py --measure-tokens  # base 14-op
python research/capability-schema-validation/corpus-530/harness-bridge/run.py --measure-tokens
# smoke (authoritative validation before execution)
python research/capability-schema-validation/corpus-530/harness-bridge/run.py --smoke
python research/capability-schema-validation/corpus-530/harness-bridge/validate.py
# single ad-hoc with corpus-530 schemas
python research/capability-schema-validation/corpus-530/harness-bridge/run.py --op search_users --args '{"query":"alice"}'
```

Live A/B (deferred to fresh session):
```bash
# placeholder — live runner will fill measurements/logs/*.jsonl and summary.json
python research/capability-schema-validation/corpus-530/harness-bridge/run.py --live --variant full --out measurements/logs/full.jsonl
python research/capability-schema-validation/corpus-530/harness-bridge/run.py --live --variant minimal --out measurements/logs/minimal.jsonl
```

## Pinned versions & tolerance

- `tiktoken cl100k_base 0.14.0`, `jsonschema 4.26.0`, `schemas 0.1.0`, `ToolRegistry 0.15.0 / MCP 2.0.0` (retired scope)
- **5pp tolerance:** `|sel_min - sel_full| ≤0.05` AND `|arg_min - arg_full| ≤0.05` on 24 tasks, ≥3 reps, temp>0

## Reusable verbatim for EDASES A/B

Keep `schemas/authoritative.json` unchanged (runtime truth). Swap only the model-facing block (`schemas/full.json` vs `schemas/minimal.json`) and prompt (`prompts/prompt-full.md` vs `prompts/prompt-minimal.md`). Harness ordering `sandbox→validation→policy→execution` unchanged. No state-machine/policy/lifecycle/discovery/pooling/idle-timeout added (kickoff constraint).

## WHAT-NOT-TESTED

- No live-model call in this scaffolding commit — all success/latency fields are placeholders.
- No statistical significance beyond pre-registered ≥3 reps.
- No chained multi-step workflows carrying state.
- No transport/cross-host variation (collocated harness only).
