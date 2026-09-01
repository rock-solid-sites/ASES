---
title: Next-Wave Scaffolding — Corpus-530 Multi-Rep / Multi-Model + Second-Retry + EDASES A/B Prep
program: EDASES
layer: Research
document_type: Guide
status: Active
authority: Derived
canonical_repository: edases
issue: 530
---

# Next-Wave Scaffolding — Corpus-530 (strict freeze, no live run)

**Issue:** #530 · **Branch:** `feature/pp3g-uqy5-prepare-next-test-wave-for-530-corpus-530-scaffolding`
**Corpus frozen:** `research/capability-schema-validation/corpus-530/` (17-op schemas 0.1.0, 24 tasks in 6×4, 12 malformed, 4 adversarial D1-D4, prompts/prompt-full.md + prompt-minimal.md) — **DO NOT MODIFY**.
**This directory:** `next-wave/` — scaffolding/docs only for the next live wave. No live model calls in this commit. No state-machine/policy/lifecycle added at this layer (scaffolding only).

## Freeze invariant (hard rule, repeated in every doc here)

> **Strict no-modify-corpus rule:** `schemas/authoritative.json`, `schemas/full.json`, `schemas/minimal.json`, `tasks.json`, `malformed-recovery.json`, `adversarial.json`, `corpus.jsonl`, `prompts/prompt-full.md`, `prompts/prompt-minimal.md`, `prompts/*.template.md`, `manifest.json` under `corpus-530/` are **frozen**. Edits require a new corpus version and a fresh issue. This directory adds scaffolding *around* the frozen corpus; verification checks that no corpus file hash changed.

## What this wave adds (without running)

| Task | Artefact | Purpose |
|------|----------|---------|
| (1) Multi-rep/multi-model plan | `PLAN.md` | 3 reps × 2 variants × 2 models, seed-permuted order, fixed prompts/schemas verbatim |
| (2) Second-retry harness | `harness-bridge/second_retry.py` + `SECOND_RETRY.md` | On minLength/pattern empty-string failures, second retry with full constraint text (field+constraint+message+similar valid example) without exposing full schema |
| (3) EDASES A/B prep | `EDASES_A_B.md` | How same corpus-530 (17-op, full vs minimal prompts) is reused verbatim against EDASES harness (state+permitted transitions) vs conventional harness — keep `harness-bridge/run.py` unchanged, just swap runtime |
| (4) Measurements scaffolding | `measurements/` | `multi_rep_summary.json` template, `model_comparison.json` template, `second_retry/` logs + schema, EDASES reuse notes |
| (5) Measurement docs | `measurements/README.md` | 5pp tolerance, pinned versions (tiktoken 0.14.0, jsonschema 4.26.0), no-modify rule |
| (6) Smoke verify | `harness-bridge/run.py --smoke` 18/18 | Proves freeze didn't break harness ordering sandbox→validation→policy→execution |

## Layout

```
next-wave/
├── README.md                      # this file (freeze invariant, layout)
├── PLAN.md                        # multi-rep/multi-model plan
├── SECOND_RETRY.md                # second-retry design (constraint text without full schema)
├── EDASES_A_B.md                  # EDASES vs conventional reuse doc (swap runtime, run.py unchanged)
├── harness-bridge/
│   └── second_retry.py            # recovery harness: should_second_retry() + build_second_retry_prompt()
├── measurements/
│   ├── README.md                  # tolerance, pinned versions, no-modify rule
│   ├── multi_rep_summary.json     # template (placeholders, not live results)
│   ├── model_comparison.json      # template (placeholders)
│   ├── model_comparison.md        # template description
│   ├── second_retry/
│   │   ├── schema.json            # JSON schema for second_retry log rows
│   │   ├── README.md              # second-retry log description
│   │   └── logs/.gitkeep
│   └── logs/.gitkeep              # next live wave writes measurements/logs/*.jsonl here
└── NO_MODIFY_CORPUS.md            # explicit freeze guard copy (mirrors this section)
```

## Reproduction (no live model)

```bash
# verify freeze untouched and scaffolding still valid
python research/capability-schema-validation/corpus-530/harness-bridge/run.py --smoke        # must be 18/18
python research/capability-schema-validation/corpus-530/harness-bridge/validate.py           # 40 lines, 6×4, enums, ≤20w, hidden constraints, distinct codes
python research/capability-schema-validation/corpus-530/next-wave/harness-bridge/second_retry.py --self-test
python research/capability-schema-validation/corpus-530/next-wave/harness-bridge/second_retry.py --check-examples
```

Live run (deferred — not executed in this scaffolding commit):
```bash
# Filled by next live session; writes under next-wave/measurements/logs/
python research/capability-schema-validation/corpus-530/next-wave/harness-bridge/second_retry.py --live-dry-run --help
# actual live invocation will be documented in PLAN.md §Reproduction and wired via measurements/live_run_next.py (to be added next session)
```

## Pinned versions & tolerance (scoped to this scaffolding)

- **Tokenizer:** `tiktoken==0.14.0` `cl100k_base` — description_tokens is primary (spec §4.2); heuristic `chars/4` flagged when tiktoken absent.
- **jsonschema:** `4.26.0` Draft-07 via `harness/runtime.py` (Draft7Validator).
- **Harness:** `0.1.0` sandbox→validation→policy→execution ordering, exact stable-ID gate, trace logged.
- **Schemas:** `0.1.0` 17 ops (14 base + 3 search_users/groups/projects), authoritative frozen.
- **5pp tolerance:** Minimal acceptable if `|sel_min − sel_full| ≤ 0.05` AND `|arg_min − arg_full| ≤ 0.05` on 24 tasks, ≥3 reps, temp>0 or seed-permuted order; raw counts + token/accuracy curve X=tokens(minimal)/tokens(full) vs Y=selection/argument are primary.

## WHAT-NOT-TESTED (negative-space disclosure)

- No live model calls in this commit — all next-wave summary fields are placeholders.
- No statistical significance beyond pre-registered ≥3 reps (plan only).
- No second-retry live evidence (dry-run flags only, no model).
- No EDASES state-machine/policy/lifecycle/discovery added at this layer — just prep doc for next wave swapping runtime.
- No corpus modification verification via automated hash gate yet (manual `git diff` check this commit; full hash gate deferred to live session).

## Dependency

- Frozen corpus: `../manifest.json`, `../pinned-versions.md`, `../tolerance.md`, `../failure-taxonomy.md`, `../harness-reuse.md`.
- Prior live evidence: `../measurements/summary.json` (07dfab42, 48 A/B 95.8% vs 91.7% harness delta 4.2pp within 5pp, 71% token saving 2588/8915) — retained as baseline, not overwritten.
