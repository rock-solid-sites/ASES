---
title: EDASES A/B Comparison Prep — Same Corpus-530 Reused Verbatim (Conventional vs EDASES Harness)
program: EDASES
layer: Research
document_type: Guide
status: Active
authority: Derived
canonical_repository: edases
issue: 530
---

# EDASES A/B Comparison Prep — Reuse Corpus-530 Verbatim

**WHY** — The brief deliberately establishes a clean conventional baseline (full vs minimal, sandbox→validation→policy→execution) *before* introducing any EDASES harness variation. The next wave must be able to run the *same* 24+12+4 corpus against two runtimes without rewriting tasks/prompts/schemas.

**WHAT** — This doc prescribes how the **identical** `research/capability-schema-validation/corpus-530/` corpus (17-op authoritative 0.1.0, `schemas/full.json` 8915 tok vs `schemas/minimal.json` 2588 tok ratio 0.290, prompts/prompt-full.md vs prompt-minimal.md) is reused verbatim for an **A/B architecture comparison**: Conventional harness vs EDASES harness (state + permitted transitions). The existing `harness-bridge/run.py` stays **unchanged**; only the runtime behind `Harness.call` is swapped.

**HOW CERTAIN** — Scaffolding prep only; no EDASES state-machine added here. The reuse invariant is checkable (hash verbatim).

**WHAT-NOT-TESTED** — No lifecycle/policy/discovery/pooling/idle-timeout implementation in this layer; no live EDASES run yet; no transport or multi-host variation.

## Corpus freeze (no rewrite)

All of the following stay verbatim across both harness conditions:

- Authoritative schemas: `../schemas/authoritative.json` (17 ops, 0.1.0, Draft-07, frozen) — runtime truth for both harnesses.
- Model-facing blocks: `../schemas/full.json` (Variant A) and `../schemas/minimal.json` (Variant B) — same `cl100k_base` token counts (8915 vs 2588) for both harnesses.
- Prompts: `../prompts/prompt-full.md` and `../prompts/prompt-minimal.md` (templates with `{{user_request}}`) — identical ordering, instructions, hidden-constraint notice.
- Corpus: `../tasks.json` (24 in 6×4), `../malformed-recovery.json` (12), `../adversarial.json` (4 D1-D4), `../corpus.jsonl` (40 lines).

No task description, expected op/args, or schema file is rewritten for EDASES.

## What "EDASES harness" means (and does not mean here)

At this layer, **EDASES harness** is defined minimally as: *the same sandbox→validation→policy→execution ordering* plus **state-aware permitted-transition checks** that conventional harness does not enforce — e.g., rejecting a transition that is schema-valid but lifecycle-illegal (such as `update_artefact_status` to an illegal status, or archiving an already-archived artefact with `Conflict`), and returning a distinct `code` (mapped to `Conflict` or `PolicyDenied` depending on whether the denial is lifecycle vs policy) without executing.

This prep does **not** add that implementation now. It only documents the swap point so the next live wave can run without rewriting corpus:

```
Model (sees full OR minimal block, verbatim promts)
    ↓
harness-bridge/run.py (UNCHANGED — thin shim over ../harness)
    ↓
Conventional runtime: Runtime(schemas_path=corpus-530/schemas/authoritative.json) + Sandbox + Harness.call
    — OR (swap) —
EDASES runtime:     Runtime(schemas_path=same) + Sandbox + State-permitted-transition gate + Harness.call
    ↓
Ordered trace: sandbox → validation → policy → execution (conventional)
               sandbox → validation → policy → permitted-transitions → execution (EDASES, additive)
```

The ordering `sandbox→validation→policy→execution` is **preserved**; EDASES only inserts an additive `permitted-transitions` gate after `policy:pass` and before `execution`, returning a typed error if violated.

## Swap runtime, not run.py (contract)

`harness-bridge/run.py` is frozen at this layer. The existing shim already does:

```python
from sandbox import Sandbox
from runtime import Runtime, Harness
runtime = Runtime(schemas_path=CORPUS_SCHEMAS)   # authoritative 0.1.0 verbatim
sandbox = Sandbox(schemas_path=CORPUS_SCHEMAS)
harness = Harness(sandbox, runtime)
```

For the EDASES A/B, the next wave introduces `next-wave/harness-bridge/edases_runtime.py` (or reuses a sibling module) that **implements the same `Runtime`/`Harness` interface** (`call(op, args, policy=None) -> {validation_result, error, executed, trace, version, latency_ms}`) but injects the permitted-transition check. `run.py` is not edited; callers swap the imported `Runtime`/`Harness` class via injection or a thin wrapper:

- **Conventional condition:** `from runtime import Runtime, Harness` (as today, 18/18 smoke).
- **EDASES condition:** `from next_wave.harness_bridge.edases_runtime import Runtime, Harness` (same interface, plus state gate off same `authoritative.json`).

Both conditions share:

- Same `schemas_path` (frozen).
- Same `harness/version` reported (`0.1.0` plus an additive `edases_v0.1.0-transition-gate` tag in the EDASES log).
- Same measurement plumbing: `description_tokens` (full/minimal), `total_input_tokens`, `total_output_tokens`, `selection/argument/task`, `validation_failures`, `retries`, `latency p50/p95`, recovery metrics, adversarial distinct codes.

## Measurement parity (same definitions across both harnesses)

| Metric | Definition | Across harnesses |
|--------|------------|------------------|
| `selection_success` | exact stable-ID match | identical denominator 24×3 reps per variant per model |
| `argument_success` | `executed:ok` (authoritative JSON Schema) — primary; strict expected-equality secondary | identical |
| `task_success` | selection ∧ argument ∧ executed:ok | identical |
| `validation_failures` | `ValidationFailed` before execution | identical (plus additive EDASES transition failures counted separately as `Conflict`/`PolicyDenied` when triggered) |
| Token / latency | `description_tokens` (8915 vs 2588, ratio 0.290, tiktoken 0.14.0), total in/out, p50/p95 | identical tokenizer & harness version tag |
| Recovery | first retry via `field+constraint+got+message`; second retry (see SECOND_RETRY.md) applies identically to both harnesses | identical |
| Adversarial D1-D4 | distinct codes no execution | identical; EDASES adds that D4 output validation remains `runtime:output` |

The only column that differs is the **additional EDASES-permitted-transition rejection** count, reported separately so A/B remains comparable on schema-validity metrics.

## Reuse notes for next live wave

1. **Do not regenerate** prompts or schemas for the EDASES condition — same prompt files are mounted.
2. **Keep run.py unchanged** per brief — verify by `git diff -- research/capability-schema-validation/corpus-530/harness-bridge/run.py` empty before live wave.
3. **Record harness variant** per row: `harness_variant: "conventional"` vs `"edases"` alongside pinned versions (`tiktoken 0.14.0`, `jsonschema 4.26.0`, `harness 0.1.0`, `schemas 0.1.0`).
4. **Do not add** lifecycle/discovery/pooling/idle-timeout beyond the permitted-transition gate at this comparison — deeper lifecycle is tracked separately (issues #14–#21, execution-engine UI synthesis reference).
5. **Verbatim check:** Before comparison, `sha256sum research/capability-schema-validation/corpus-530/schemas/authoritative.json research/capability-schema-validation/corpus-530/schemas/minimal.json research/capability-schema-validation/corpus-530/prompts/prompt-*.md research/capability-schema-validation/corpus-530/tasks.json` must match the committed hashes on `main` (or recorded in `next-wave/measurements/README.md`).

## What-NOT-TESTED (negative-space disclosure)

- No state-machine/policy/lifecycle/discovery implementation is committed at this layer — this doc only pre-commits the reuse protocol and swap point.
- No EDASES-specific transition table is committed yet (deferred to the harness issue that introduces `edases_runtime.py`; until then, conventional is the only executable harness).
- No transport/cross-host variation; collocated harness only.
- No chained multi-step workflows carrying state (single tool-call trials only).

## Dependencies

- Frozen corpus: `../manifest.json`, `../harness-reuse.md`, `../failure-taxonomy.md`, `../pinned-versions.md`, `../tolerance.md`.
- Conventional harness: `../../harness/` (`sandbox.py`, `runtime.py`, `error-codes.md`, `run.py`).
- Prior evidence: `../report.md` (07dfab42), `../measurements/summary.json` — conventional baseline retained.
- Next-wave harnesses: `harness-bridge/second_retry.py` (additive, harness-agnostic).

## Reproduction (no live model)

```bash
# conventional smoke stays 18/18 with frozen corpus
python research/capability-schema-validation/corpus-530/harness-bridge/run.py --smoke
# next-wave scaffolding still without EDASES runtime — conventional only until edases_runtime lands
python research/capability-schema-validation/corpus-530/next-wave/harness-bridge/second_retry.py --self-test
```
