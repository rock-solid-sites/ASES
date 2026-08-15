---
title: Tools Distribution Architecture — One-Shot Review Input
program: EDASES
layer: Research
document_type: Review Input
status: Draft
authority: Derived
canonical_repository: edases
last_updated: 2026-08-14
---

# Tools Distribution Architecture — One-Shot Review Input

## Purpose

This document is a self-contained briefing for an independent architectural
review. It explains a real, observed drift problem in the AI-agent tooling
distribution system of an active research project, the fix currently proposed,
and five alternative architectural positions already collected from separate
reviews. The reviewer is asked to discuss the pros and cons of each option and
either recommend one or propose something different.

The reviewer does not need repository access to respond, but may inspect the
referenced paths if available. All claims in this document were verified against
the actual filesystem on 2026-08-14; where a claim was not independently
executed-tested, it is marked.

---

## 1. Project context (who we are)

The project is a disciplined AI-assisted-software-engineering research programme
with three abstraction layers, each a **separate git repository**:

- **EDASES** — research layer (evidence, findings, methodology research).
- **ASES** — methodology layer (the layer this document lives in; operational
  rules for AI agents, workflow-topology design, review procedures).
- **Execution Engine** — a future, not-yet-existing layer that will enforce
  methodology. Its concrete shape is undetermined.

Two more repositories complete the picture:

- **Tools** (`~/projects/Tools`) — a **general warehouse** (NOT a layer) for
  reusable AI-agent infrastructure: guard plugins, CLI wrappers, model plugins,
  skills, hooks, agent definitions, scripts. It is the intended canonical source
  for this tooling.
- **tripn-astro** (`~/projects/tripn-astro`) — a separate **client** project
  that consumes the same tooling. Not a monorepo member.

Plus one fork:

- **crosslink fork** (`~/projects/crosslink`) — a Rust CLI (`crosslink`) that
  provides issue tracking, agent orchestration (kickoff/swarm), sessions, and
  repo initialization. It **embeds** a set of resources (hooks, skills, commands,
  MCP servers, crosslink rules) in its binary via `build.rs` and deploys them
  into every tracked repo via `crosslink init`.

The intended long-term structure is a **repo-of-repos** monorepo (the three
layer repos, logically grouped, no submodules), with Tools as a sibling
warehouse. This structural decision was made and is treated as settled by the
people requesting this review — but it is explicitly open to challenge if the
reviewer has reason to doubt it.

---

## 2. The drift problem (the reason this review exists)

Shared tooling is distributed to consumers by **copying files into each
consumer repo**, and the copies have drifted in multiple independent ways.
Verified current state:

| # | Artifact | Observed drift |
|---|----------|----------------|
| 1 | **Guard plugins** (`crosslink-guard.ts`, `orchestrator-guard.ts`, `rtk-guard.ts`) — enforce four-role permission model (orchestrator/builder/reviewer/auditor) | Three divergent copies: ASES 42.1 KB (newest), tripn 37.6 KB, Tools 33.5 KB (oldest). The Tools "canonical" copy is the oldest. ASES copy has per-role `by_type` resolution the Tools copy lacks. |
| 2 | **CLI wrappers** (`claude`, `opencode`, `crosslink-moe`) | Live `~/.local/bin/claude` (3.0 KB) is ahead of Tools/scripts copy (2.4 KB): live has `--agent`, `CROSSLINK_AGENT_TYPE`, tmux `--auto`, correct quoting; Tools copy lacks these and has a prompt-quoting bug. Live `~/.local/bin/opencode` (3.6 KB) has a fork-identity guard (#274) the Tools copy (1.5 KB) lacks. `crosslink-moe` identical. |
| 3 | **Model plugins** (`plugin.ts`, `dynamic-models.ts`) — provider suppression + free-model whitelist + models-cache merge | Tools/plugins/plugin.ts (51 lines, Jul 9) is BEHIND the deployed `~/.config/opencode/plugins/plugin.ts` (133 lines, Aug 10): repo copy missing #347 grok-ban + whitelist work. `plugin.ts` and `dynamic-models.ts` are near-duplicates that have already diverged from each other. |
| 4 | **models-cache.json** | Stale (dated Jul 25), merged into provider configs by the model plugins; no working regeneration mechanism. |
| 5 | **freeZenModels whitelist** | Stale: blocks newly-added free models from appearing (reproduced: refresh returns 5 models vs 7 whitelist entries); carries dead entries; undocumented UX trap. |
| 6 | **hook-config precedence** | LIVE BUG: `git merge` appears in BOTH the per-role gated list (`by_type.orchestrator.gated_git_commands`) AND the top-level blocked list (`blocked_git_commands`); the global block is checked first in the plugin, so orchestrator merges are falsely hard-blocked despite the role override. |
| 7 | **Init-deployed snapshots** | `Tools/.claude/hooks+commands+mcp` are gitignored on-disk snapshots deployed by `crosslink init` — no canonical git source; on-disk copies differ from the binary's current embedded resources. |
| 8 | **`.ases/` boundary** | An aspirational integration-boundary design (documented in `EDASES-Methodology-Feedback-and-Enforcement.md` §3) — not implemented; tripn has no `.ases/` directory. |

**Root observation:** every artifact that exists in N places has drifted. The
single-copy artifacts (e.g. the user-level model-whitelist plugin) are the ones
that stayed current. This is evidence that the drift is **structural to the
copy-out model**, not a one-off execution mistake.

---

## 3. The fix currently proposed (interim plan, under review)

The current plan (already revised twice through adversarial review) is:

- **Tools remains one warehouse repo** as the canonical source for guard
  plugins, wrappers, model plugins, and the 2 shared crosslink skills.
- **Reverse-sync first**: push the newest ASES guard plugins and the live
  `~/.local/bin` wrappers back into Tools so Tools becomes the true source.
- **`sync-tooling.sh`**: a deploy script that copies canonical content into
  each layer repo (`.opencode/plugins/`, `.claude/skills/`) and to tripn.
  `.crosslink/rules/` is **excluded** — rules are layer-owned, never synced.
- **Consumer-side drift detection**: a sha256 canonical manifest written at
  each destination; the guard plugin checks its own loaded file at session
  start. A state machine: State 0 (no marker = no-op) → State 1 (warn) →
  State 2 (hard-fail), with promotion a deliberate operator action
  (`--promote`) after a clean `--check`.
- **Git-only atomicity**: direct writes, per-destination operator commits, no
  transaction log/backup dir.
- **Correctness bugs fixed regardless of architecture**: hook-config precedence
  (item 6), plugin.ts/dynamic-models.ts consolidation, models-cache
  regeneration, whitelist verification.

Five independent reviews judged this plan **acceptable as interim
stabilization but not as the end state** — it is a "managed version of
copy-out" that reduces but does not eliminate drift.

---

## 4. Five alternative architectural positions (from independent reviews)

Five separate reviewers (GLM5.2, Luna, Kimi K2.7, Qwen3.7 Plus, Big Pickle)
were asked the same open question: does the current system make sense, and what
would you build instead? Their positions:

### Option A — Extend the crosslink binary to embed everything (GLM5.2, Qwen3.7)

Move guard plugins, wrappers, and agents INTO the crosslink binary as embedded
resources (like hooks/skills/commands/mcp/rules already are). `crosslink init`
becomes the **single distribution channel** for all shared artifacts. Drift
becomes structurally impossible — there is exactly one source (the binary) and
one deployment mechanism (init).

- **Pros (as argued):** one channel; drift structurally impossible; atomic
  (rebuild binary + init); reuses the proven `init` mechanism; no new sync
  script, manifest, or state machine; simpler than the interim plan.
- **Cons / concerns (as raised):** couples unrelated release cadences — a
  plugin change forces a Rust binary rebuild; makes crosslink the accidental
  owner of OpenCode/Claude-specific tooling it was never meant to own; binary
  bloat; the dev loop becomes edit-Tools → rebuild-binary → init (heavier than
  edit-Tools → sync).

### Option B — Tools as a versioned distribution source (Luna)

Keep the layer repos. Tools publishes **immutable per-release bundles**
(manifest + checksums + compatibility metadata + lockfile). Consumers **pin a
bundle version**; installation is generated and atomic; consumer copies are
**generated artifacts, never hand-edited sources**. A deliberate
promote/import command creates a new Tools release — never silent inference
from a live copy. Replace the warn→hard-fail drift state machine with a
narrower invariant: fail install/CI when a pinned bundle is incomplete,
tampered, or generated output is dirty.

- **Pros (as argued):** keeps layer repos; versioned, reproducible, auditable;
  installation failures are caught at install/CI time rather than at runtime;
  deliberately prevents "live copy silently becomes canonical."
- **Cons / concerns (as raised):** more moving parts than the current plan (a
  packaging/release system for what is mostly markdown/bash/ts); for 3 layer
  repos a full release pipeline may be over-engineered; consumer copies are
  still copies (just pinned); generated-artifact discipline must be enforced by
  CI.

### Option C — Reference-based consumption, no copies (Kimi K2.7)

**REJECT the copy model entirely.** Consumers **reference** Tools rather than
copy from it: git submodules or symlinks so `ASES/.opencode/plugins/
crosslink-guard.ts` → `Tools/plugins/crosslink-guard.ts`, `~/.local/bin/opencode`
→ `Tools/scripts/opencode`, `~/.config/opencode/plugins/plugin.ts` →
`Tools/plugins/plugin.ts`. Split ownership cleanly: the fork owns only
crosslink-specific embedded resources; OpenCode plugins/wrappers/model policies
belong in Tools and are removed from the init payload. Layer repos keep only
layer-owned config (hook-config, project rules, opencode.json, role agents).

- **Pros (as argued):** eliminates physical copies → drift structurally
  impossible by construction; minimal machinery; single edit point.
- **Cons / concerns (as raised):** symlinks are machine-absolute (break other
  machines/CI/containers); submodules have UX cost with worktrees; OpenCode
  plugin loading from a symlinked/submodule path is **untested** (could be
  broken by load-path assumptions); `crosslink init` regenerates `.claude`
  hooks, which conflicts with symlinking the same paths; cross-repo
  portability suffers.

### Option D — Three-class artifact locus (Big Pickle)

Classify each artifact by **where it must live**, and pick the mechanism per
class rather than one mechanism for everything:

1. **Machine-global, single-copy** (wrappers, model plugins, guard plugins):
   move to **user-level** `~/.config/opencode/plugins/` and `~/.local/bin` —
   ONE copy, edited there, with Tools as the versioned upstream
   (install-from-Tools discipline, never edit-live). The model-whitelist plugin
   already lives user-level and is the only non-diverged artifact — evidence for
   this class.
2. **Per-repo deploy-time materialization** (skills, hooks, commands, mcp):
   **pinned copy-out** — a checked-in `.tools-pin` (Tools commit hash); the
   sync script checks out the pinned commit and materializes; a **generated**
   sha256 manifest is checked in so git itself exposes divergence. Submodules
   are the git-native version; packages are the long-term answer if the fleet
   grows.
3. **Layer-owned policy** (rules/, hook-config base, agent definitions, .ases/):
   stay in-repo, NEVER synced.

Plus: fix the correctness bugs NOW, independent of architecture choice.

- **Pros (as argued):** most concrete and least invasive of the five; the
  user-level precedent is proven (it is the only non-diverged artifact);
  respects the fact that different artifacts have different correct loci;
  keeps the repo-of-repos intact.
- **Cons / concerns (as raised):** moving guard plugins to user-level relies on
  untested assumption that opencode loads all plugin types identically at
  user-level (strong precedent, not executed); pin-file + script still carries
  some copy-out; requires new discipline (never-edit-live) to work.

### Option E — (default if no alternative chosen) Interim sync-tooling.sh plan

The §3 plan as the shipped end state: Tools canonical + sync script + drift
markers + git-only atomicity. Simpler than A/B/D, but keeps copies and keeps
drift possible (detected rather than prevented).

- **Pros (as argued):** already reviewed twice and APPROVED; minimal new
  machinery; fixes the correctness bugs; works today.
- **Cons / concerns (as raised):** five reviewers all judged it interim, not
  end-state; a "managed copy-out" that still requires discipline and can still
  drift; the state machine and manifest are additional artifacts that must
  themselves be maintained.

---

## 5. Questions for discussion

The reviewer is asked to discuss — not just score — the options:

1. **Diagnosis check:** is "copy-out is structurally flawed" the right
   diagnosis, or is the real problem something else (e.g. missing discipline, a
   specific broken process, the layer split itself)?
2. **Pros/cons per option:** for Options A–E, what are the strongest arguments
   for and against each? Which arguments are strongest, which are weak?
3. **Recommended option:** is one option clearly better for this project's
   scale (a single-operator, single-machine setup with 3 layer repos + 1 client
   + 1 fork)? Is a hybrid of A/B/C/D better than any single one?
4. **Undisputed bug fixes:** are the correctness fixes (hook-config precedence,
   plugin consolidation, models-cache, whitelist) correctly scoped as
   independent of the architecture choice, or does the architecture decision
   change which bugs matter?
5. **Anything else:** is there an option F — a system the reviewers so far have
   not proposed — that addresses the drift problem better than any of A–E?
6. **Verification gaps:** which claims in this document should be
   executed-tested before committing to the chosen option? (Known gaps: symlink
   plugin loading, user-level guard-plugin loading, `crosslink init --force`
   collateral, crosslink binary embedding feasibility.)

---

## 6. Final question

**Given the drift evidence, the interim plan, and Options A–E above — do you
recommend one of these options (which, and why), a hybrid, or a completely
different system that addresses these issues better?**
