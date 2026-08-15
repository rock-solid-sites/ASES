---
title: Tools Distribution Architecture — Decision Test Framework
program: EDASES
layer: Research
document_type: Decision Record
status: Active
authority: Derived
canonical_repository: edases

depends_on:
  - docs/research/tools-distribution-architecture-review-input.md
  - docs/research/Tools Distribution Architecture Reviews.md
  - docs/research/Tools Distribution Architecture Synthesis.md

consumed_by:
  - Tools/monorepo drift remediation planning (#365 and descendants)
  - Operator architecture decisions (synthesis §5.3 decision points)

supersedes: []
last_updated: 2026-08-15
---

# Amendment — Tools Distribution Architecture Decision Test Framework

Status: Active. Supersedes: the original D1 and D5 sections of
`docs/research/Tools Distribution Architecture Decision Test Framework.md`.
Operator direction 2026-08-15.

## 0. Governing framing (applies to the whole document)

This migration is an **ongoing process**. The current-phase work — the interim
sync-tooling.sh plan, the one-time reverse-sync, and any transitional
machinery built to get from today's drifted state to the target state — is
**scaffolding**, not the intended architecture. Each of these will be retired
once the target topology works. Do not mistake the bootstrap mechanism for the
design; the design is the target state described below. The Decision Test
Framework tests the *target state* decisions; the transitional steps exist
only to reach that state.

## 1. Target state (operator-confirmed 2026-08-15)

- **One canonical home repo (Tools) owns each shared artifact.**
- **The fix happens once, in Tools, and is pushed mechanically to every
  consumer workspace** — the layer repos, tripn, `~/.local/bin`,
  `~/.config/opencode`. This is the settled flow direction.
- **The same tooling is used across every repo** by construction, because every
  workspace derives from the single canonical source.
- The reverse-sync (live→Tools) is a **one-time bootstrap seed**, necessary
  only because the live copies currently carry newer content (the #347 grok-ban,
  the #274 fork-identity guard, the memory-scope wrapper) that must not be lost
  when Tools becomes canonical. After the seed, reverse-sync is never needed
  again; the ongoing flow is Tools→everywhere.

## 2. D1 — REVISED: flow direction is operator-settled; test becomes forward-only flow verification

### 2.1 Why the original D1 historical audit was invalid

The original D1 proposed a historical audit (git log + mtimes over ~30 days) to
decide Tools→live vs live→Tools. This audit is **confounded**: during the entire
window, "Tools as canonical source" **did not exist** — Tools was dormant (last
commits to scripts/ and plugins/ were 2026-07-09 and 2026-07-15, ~a month before
the consolidation idea, which is only a few days old). The audit therefore
measured "where people happened to work," not "which direction survives as
canonical." Of course edits happened live: Tools was not established as the home.

### 2.2 Correct reading of the historical data

The data is **failure-mode evidence**, not a direction vote. The artifacts that
stayed current (user-level model plugin, live wrappers) are the single-copy
ones — people edit where the artifact actually runs. The dormant Tools copies
confirm the multi-copy drift failure mode. This is consistent with (and
corroborates) the reviews' core thesis; it does **not** argue for live-as-
canonical.

### 2.3 Settled decision

**Flow direction = Tools→everywhere (operator intent, 2026-08-15).** Not chosen
by measurement — chosen because single-source-of-truth with mechanical push is
the stated goal: "the fix happens in one place and gets pushed to the other
workspaces."

### 2.4 Remaining empirical question (the test that survives)

The direction is no longer in question. What must be verified forward is that
**the push mechanism actually keeps every workspace in sync**. The D1 test is
therefore re-scoped to a forward flow-verification window:

- **Signal:** after the seed + first pushes, does an edit made in Tools reach
  every consumer workspace (ASES, tripn, `~/.local/bin`, `~/.config/opencode`)
  without manual re-copying?
- **Test:** make one canonical change in Tools (e.g. a comment or a no-op
  semantic tweak in `crosslink-guard.ts`), run the push, and verify all four
  consumer locations converge to the new sha256 within the window; then make
  one consumer-local edit and verify it is detected (not silently overwritten).
- **Threshold:** all four consumers converge on a canonical change within one
  push cycle with zero manual steps; a consumer-local edit is detected and
  reported. If a consumer silently stays stale, the push mechanism is
  insufficient and must be fixed before declaring D reached.

This replaces the original D1 historical audit, which is removed.

## 3. D5 — REVISED: historical leg removed, prospective-only

The original D5 included a historical scan (git history + issue refs for
cross-repo-coordinated changes). Like D1, this leg is invalid: there were no
coordinated multi-repo changes to measure in a month where the monorepo idea
did not exist. The historical leg is removed. D5 keeps only the prospective
friction telemetry that rides the migration (log every cross-repo-coordinated
change + friction score during Phases 1–4). Threshold unchanged (≥5
coordinated changes/month with documented friction → revisit repo-of-repos).

## 4. What this changes in the migration plan

- **Phase 1 (reverse-sync)** is relabeled: it is a **one-time bootstrap seed**
  (capture live's newer content into Tools), not an ongoing reverse-sync
  workflow. The plan must state explicitly that the seed is executed once and
  the ongoing flow is Tools→everywhere.
- The **push mechanism is the core deliverable** of the migration. Its
  correctness is what D2 (symlink loading), D3 (user-level loading), and D4
  (drift window) actually verify — the D1 re-scope (2.4) adds the end-to-end
  convergence check that ties them together.
- The **interim sync-tooling.sh** remains a transition tool (per the original
  framework and the synthesis: E is migration-only). Its life is bounded by
  Phase 4 (retire transitional machinery).

## 5. WHAT-NOT-TESTED

- The forward flow-verification test (2.4) has not been run — it requires the
  seed + push mechanism to exist first.
- The historical re-reading (2.2) is an interpretation of data already
  gathered, not new evidence.
- The D1 original historical audit result (100% of edits originating live) was
  recorded on the test issue but is not treated as a direction vote anywhere in
  this amendment.

---


# Tools Distribution Architecture — Decision Test Framework

> **Purpose.** The synthesis (`Tools Distribution Architecture Synthesis.md`
> §5.3) identified seven open operator decision points. This document turns
> each into a **falsifiable experiment**: a measurable signal and a
> **predefined threshold**, so no decision is made on opinion. Every decision
> reads the result of a test instead.
>
> **Use.** Each decision is a gate. Decisions D2/D3 gate Phase-3 Class-1
> mechanics. Decisions D4/D5/D7 are Phase-4/5 gates that ride the migration
> itself. Run the cheapest discriminating test first (each section lists the
> cost-to-falsify).

---

## Test ordering (cheapest-first)

| Order | Decision | Test | Cost to falsify | Gates |
|-------|----------|------|-----------------|-------|
| 1 | D1 flow direction | historical edit audit | ~10 min, zero machinery | Phase 1 |
| 2 | D2 materialization | symlink-loading spike | ~10 min | Phase 3 Class-1 |
| 3 | D3 guard-plugin locus | user-level loading spike | ~10 min | Phase 3 Class-1 |
| 4 | D6 whitelist policy | A/B scratch spike | ~30 min | Phase 0 (whitelist fix) |
| 5 | D4 state machine | post-D drift window | rides migration | Phase 4 |
| 6 | D5 Tools placement | cross-repo friction telemetry | rides migration | Phase 4 |
| 7 | D7 machinery scale | dogfood skip-rate | rides migration | Phase 5 |

---

## D1 — Flow direction: Tools→live (D default) vs live→Tools (GLM's F)

**Question.** For machine-global artifacts (wrappers, model plugins), which
side is the authoritative source of edits?

**Signal.** Direction and persistence of actual edits over time.

**Test (cheapest, historical — no machinery).** Audit the last ~30 days:
- `git log --oneline` on `Tools/scripts/` and `Tools/plugins/` (which commits
  changed wrappers/plugins, when);
- file mtimes + content evolution on `~/.local/bin/{claude,opencode,
  crosslink-moe}` and `~/.config/opencode/plugins/{plugin.ts,
  dynamic-models.ts}`;
- where available, shell history or session notes showing live edits vs
  Tools edits.

Count, for each artifact, which side changed **first** and stayed current.

**Threshold.** If ≥2/3 of changes originate live and persist live without
flowing back → adopt live-as-canonical (F) as the initial state; if edits
originate in Tools or flow back to Tools within the window → adopt
Tools-as-canonical (D). Re-run after a workflow change (e.g. after the
tooling doc update) if flow is ambiguous.

**Note.** Single-machine assumption durability is a precondition (synthesis
WHAT-NOT-TESTED item 13): if a second machine is possible, symlink-based
answers (D2) weaken and F's single-copy-live becomes less portable.

---

## D2 — Class-1 materialization: user-level copy vs symlinks now

**Question.** For machine-global artifacts, is a symlink from the runtime
path to Tools loadable without silent failure?

**Signal.** Whether OpenCode/Claude resolve a symlinked plugin/script and
whether role resolution still works through the link.

**Test (spike, ~10 min).** In a **scratch repo** (never the real ASES):
1. Symlink `crosslink-guard.ts` into `.opencode/plugins/` (pointing at the
   canonical copy).
2. Start a session; confirm (a) the plugin **loads** (no silent drop — check
   for the guard's session-start behavior), (b) four-role `by_type`
   resolution reads per-repo `hook-config.json` via the working directory
   (not the link target's directory), (c) a sha256 self-check resolves to the
   real path (not a broken-relative-path failure).
3. Repeat for a wrapper: symlink `~/.local/bin/opencode` → Tools copy, run
   it, confirm the #274 fork-identity guard executes.

**Threshold.** Symlink loads with full role resolution → adopt symlinks for
Class 1 (Claude's position; wrappers are symlinked immediately regardless —
plain scripts, zero risk). Silent failure or degraded resolution → user-level
single-copy (D's safe default).

**Blocking.** This is blocking test 2 of the synthesis; it gates the Class-1
choice in Phase 3.

---

## D3 — Guard-plugin locus: user-level vs per-repo Class-2 fallback

**Question.** Do guard plugins work from user-level
(`~/.config/opencode/plugins/`), which would let all three divergent repo
copies be deleted?

**Signal.** User-level loading + per-repo role resolution through the
user-level path.

**Test (spike, ~10 min).** In a **scratch** session (never the real ASES
config):
1. Deploy the ASES guard plugins (`crosslink-guard.ts`,
   `orchestrator-guard.ts`, `rtk-guard.ts`) to `~/.config/opencode/plugins/`.
2. Verify (a) they load (no silent drop), (b) `by_type` role resolution reads
   the **repo-local** `hook-config.json` from the working directory (the
   `crosslinkDir` discovery must use cwd, not the plugin's own path), (c) all
   four roles (orchestrator/builder/reviewer/auditor) resolve correctly.
3. Run the gap-9 probe: does `crosslink init` deploy guard plugins? (Decides
   whether guard plugins are Class 1, Class 2, or crosslink-owned Class 4.)

**Threshold.** User-level loading with full per-repo role resolution →
user-level single copy (all repo copies deleted; 3-way divergence class dies).
Any break → guard plugins become Class-2 generated artifacts (7/7 fallback).

**Blocking.** This is blocking test 1 (+ gap 9) of the synthesis; it gates the
Class-1 vs Class-2 assignment in Phase 3.

---

## D4 — State-machine disposition: drop vs keep narrowed

**Question.** After D lands, does drift still actually occur, or is detection
moot?

**Signal.** Real drift events against the canonical manifest over a defined
window.

**Test (rides the migration).** During Phases 0–3, adopt the sync tooling with
`--check` as a **hard-failing verification command** (exit non-zero on any
destination mismatch) and **no promotion state machine** (no warn→hard-fail
ladder, no `--promote`). Record every `--check` run and every failure, with
the artifact and cause (genuine unsynced drift vs local edit vs
misconfiguration). Window: 2 weeks or N syncs (N ≥ 10), whichever is longer.

**Threshold.** >0 genuine drift events in a clean window (no intentional local
edits) → keep narrowed enforcement (fail-on-mismatch stays). 0 genuine events
for the full window → drop entirely (structural single-source made detection
moot; keep `--check` as an on-demand doctor command only).

**Position note.** Deepseek and Qwen say drop; GLM says keep a narrowed
version; ChatGPT says don't invest. This test resolves the 3-of-4 lean with
data instead of argument.

---

## D5 — Tools placement: sibling warehouse vs in-monorepo

**Question.** Does cross-repo coordination pain justify bringing Tools into
the monorepo?

**Signal.** Frequency and friction of logical changes that must touch two or
more repos.

**Test (historical + prospective).**
- Historical (cheap): scan git history + issue refs for commits/issues that
  represent one logical change spanning 2+ repos (e.g. a wrapper change +
  a playbook change + a tripn mirror). Count them and note the manual
  coordination steps required.
- Prospective (rides the migration): during Phases 1–4, log every
  cross-repo-coordinated change with a friction score (number of manual
  steps: separate commits, separate review, mirror rules). The migration
  itself is the stress test.

**Threshold.** ≥5 coordinated changes/month with documented friction (or any
single coordination failure that causes drift) → revisit the settled
repo-of-repos decision (Qwen's challenge gains evidence). Below threshold →
Tools stays a sibling warehouse with the pin/lockfile discipline.

**Note.** The default position is the settled repo-of-repos; this test exists
to give Qwen's lone challenge a fair, evidence-based hearing rather than
dismissing it by majority.

---

## D6 — Whitelist policy: discovery-first blocklist (A) vs curated + refresh (B)

**Question.** Which model-visibility policy minimizes staleness without
losing the forbidden-model guard?

**Signal.** (i) time-to-visibility of a newly-added model, (ii) dead-entry
accumulation, (iii) forbidden-model blocking effectiveness.

**Test (A/B spike, ~30 min).** Against the measured baseline (current:
refresh returns 5 models vs 7 whitelist entries, dead entries
`ling-3.0-flash-free`/`north-mini-code-free`, new models
`hy3`/`nemotron-3.5-lightning`/`muse-spark-1.2` invisible):
- **Policy A (discovery-first blocklist).** Add a new free model to the live
  catalog; measure time-to-visibility (target: appears on next `opencode
  models opencode` refresh, zero manual edits). Verify forbidden models
  (grok) remain absent.
- **Policy B (curated + mandatory refresh-validation).** Same, but measure
  the staleness window a validation job guarantees (job runs → flags missing
  new models / dead entries → human curates). Measure the worst observed
  staleness window.

**Threshold.** Adopt A if time-to-visibility < 1 day with zero manual edits
AND forbidden-block holds. Adopt B if curation is required AND the validation
job bounds the staleness window to an acceptable maximum. Decide on measured
latency + dead-entry count, not preference.

**Note.** Either beats today's undocumented fail-closed trap. The fix itself
(Phase 0) can be built on either; the test picks which survives.

---

## D7 — Machinery scale: `tools` CLI vs Makefile targets vs scripts

**Question.** Which form of the thin distribution tooling is least likely to
be skipped?

**Signal.** Skip-rate and recall-failure rate of the distribution operations
during the migration.

**Test (dogfood).** Implement the **minimal form first** (plain scripts in
`Tools/scripts/`). Instrument them with a one-line invocation log (append to
`/tmp/tools-usage.log`: command, timestamp, cwd). During Phases 1–4, also
record every time the operator (a) skips the operation when it should have
run, (b) cannot remember the exact command and needs a doc lookup.

**Threshold.** ≥2 missed sync/link/install events in the window → upgrade
affordance (Makefile target with tab-completion, then a `tools` CLI).
Additionally: if doc-lookups dominate, the command form with completion wins
regardless of skip-rate.

**Note.** All forms are thin wrappers (GLM's point); the choice is about which
form is least likely to be skipped, which is measurable.

---

## Acceptance gates summary

| Decision | Gate on | Run | Blocking test? |
|----------|---------|-----|----------------|
| D1 | Phase 1 (reverse-sync) | pre-migration | no |
| D2 | Phase 3 Class-1 choice | pre-Phase-3 | yes (synthesis blocking test 2) |
| D3 | Phase 3 Class-1 vs Class-2 | pre-Phase-3 | yes (synthesis blocking test 1 + gap 9) |
| D6 | Phase 0 (whitelist fix) | during Phase 0 | no |
| D4 | Phase 4 (retire machinery) | post-D window | no |
| D5 | Phase 4 (placement review) | rides migration | no |
| D7 | Phase 5 (enforcement) | rides migration | no |

---

## WHAT-NOT-TESTED

- No test in this framework has been **executed** as of 2026-08-15 — this is
  the plan of experiments, not their results.
- The D1 historical audit depends on the availability and interpretability of
  git history + file mtimes; partial history would weaken the 2/3 threshold
  (mitigation: prefer content-diff of the artifact families over timestamps).
- D4's "genuine drift" classification requires distinguishing intentional
  local edits from unsynced canonical changes; the operator must label each
  `--check` failure during the window or the threshold is meaningless.
- D5's historical scan relies on issue-ref discipline in commit messages;
  missing refs would undercount cross-repo changes (mitigation: also scan for
  multi-path commits touching 2+ of {Tools, ASES, tripn}).
- Cost/time estimates are planning estimates, not benchmarked.
