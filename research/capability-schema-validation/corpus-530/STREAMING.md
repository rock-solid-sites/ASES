---
title: Streaming & Strict Git Boundary — #530 Phase 1
program: EDASES
layer: Research
document_type: Note
status: Active
authority: Derived
canonical_repository: edases
issue: 530
---

# Streaming & Strict Git Boundary (530 Phase 1)

## Streaming

- This corpus was laid out via incremental writes under `research/capability-schema-validation/corpus-530/` — no `/tmp`-only artifacts remain in final commit. All decision-gating artifacts (schemas, minimal, tasks, malformed, adversarial, corpus.jsonl, prompts, failure taxonomy, token scaffolding, logs placeholders) are in git.
- Visible checkpoint cadence: POST-PLAN (plan comment), MIDPOINT (this file's batch committed with <2m from plan), FINAL result before session end — each with `crosslink sync`.
- No state-machine/policy/lifecycle/discovery/pooling/idle-timeout added per kickoff constraint.

## 45s Visible

- Plan posted at T+0, POST-PLAN checkpoint immediately after, MIDPOINT after first meaningful unit (schemas+tasks+malformed+adversarial+prompts+taxonomy+scaffolding), FINAL at commit. Each checkpoint `sync`s so operator sees progress via issue comments, not silent work.

## <2m Checkpoint

- First `crosslink issue comment --kind observation` + `crosslink sync` within 2 minutes of plan — satisfied.

## Strict Git Boundary

- Allowed: `git status`, `git diff`, `git log`, `git show`, `git branch` (listing), `git add`, `git commit` (gated on active issue via `crosslink session work 530`).
- Hard-blocked (not executed): `git push`, `merge`, `rebase`, `cherry-pick`, `reset`, `checkout .`, `restore .`, `clean`, `stash`, `tag`, `am`, `apply`, `branch -d/-D/-m`. Operator performs push/merge.
- Determinism: all writes under `research/capability-schema-validation/corpus-530/`; no sibling `Tools/` consolidation needed.

