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

> **Local applicability, 2026-11-24 (ownership/direction only):** This records operator decisions and prospective tests for the August tooling fleet, not a current operational launch, copy, reverse-sync or permission contract. The [research synthesis's current ownership disposition](Tools%20Distribution%20Architecture%20Synthesis.md) separates the durable authority question from the historical warehouse topology. Amendment 1 supersedes the original D1 direction-selection test: forward direction was operator-settled for that environment; the forward convergence and consumer-local edit detection test was not run at its recorded cutoff. D5's retrospective friction comparison was also removed. Do not interpret the old historical audit or planned thresholds as current fleet verification. Current ASES instruction retrieval follows the [current skills index](../../skills/current/README.md); current software adaptation follows the [upstream compatibility method](../methodology/Software%20Customization%20and%20Upstream%20Compatibility%20Method.md). Other amendments, provider visibility and correctness experiments retain their distinct scopes pending individual reconciliation. Original record preserved.

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

# Amendment 2 — Tools Distribution Architecture Decision Test Framework

> **Local research reconciliation (2026-11-25) — migration and correctness-test evidence.** This section qualifies the original test plan and subsequent amendments without erasing their sequence. An operator decision, a prospective test, an observed fault, a recorded test result and a verified deployment are different facts. The original August plan's statement that no tests had been executed is qualified by the later recorded D1 historical audit and D6 scratch spike. Do not interpret the remaining proposed checks as completed results or current acceptance gates.

### Decision-test disposition at the reviewed source cutoff

| Question | Recorded state and scope |
| --- | --- |
| D1 — source direction | Historical edit audit recorded 100% live-origin edits; Amendment 1 explains its confounding by a dormant warehouse and supersedes the direction-selection test. Forward flow was an operator decision for that fleet, not proof of convergence. The revised end-to-end propagation and consumer-local edit detection check was explicitly unrun at the amendment cutoff. No subsequent verified outcome recovered here. |
| D2 — symlink materialization | Prospective scratch spike: actual plugin loading, role/config resolution relative to consumer working directory, resolved-path integrity and wrapper behavior. No verified result recovered. The original claim that wrappers are risk-free is not evidence; test quoting, executable resolution and actual execution where material. |
| D3 — user-level guard locus | Prospective user-level loading and per-repo role resolution, plus init deployment-payload probe. No verified result recovered. The old global versus generated-local decision and deletion of consumer copies are not current instructions. |
| D4 — drift detection | Prospective clean-window measurement, distinguishing accidental drift, intentional local changes and configuration errors. Amendment 2 separates transition scaffolding from durable checks. No verified measurement window recovered. Zero observed drift in a finite window would not prove impossibility of future drift. |
| D5 — warehouse placement | Amendment 1 removes confounded retrospective coordination counts; prospective cross-repo friction measurement survives. No verified telemetry recovered. Historical thresholds and physical repo topology do not constitute current requirements. |
| D6 — catalog visibility | Recorded scratch A/B outcome and dated policy decision in Amendments 3–4; limited to catalog injection/visibility. See the separate local D6 reconciliation below. No actual provider invocation or live-token validation established by that record. |
| D7 — machinery scale | Amendment 2 changes the subject from transitional scripts to the surviving distribution mechanism. Prospective dogfood skip/recall measurement; no verified window or comparative result recovered. Retain the usability question, not the original scripts or thresholds as mandatory gates. |

### Correctness fixes: fault evidence versus verification

The review input records actual dated observations of hook-config precedence, duplicated/diverged model plugins and stale cache behavior. Amendment 2 explicitly states its three corresponding fix verifications had not run as of 2026-08-15. The D6 result does not close them by association.

| Proposed regression | Evidence needed if the analogous problem recurs |
| --- | --- |
| Gate/block precedence | Test authorized operation through its actual gate, rejection without required authority, and either rejection of an ambiguous overlapping configuration at load time or an explicit audited non-overlapping configuration. Do not equate a corrected list with enforcement proof; the old merge command/issue gate is historical. |
| Plugin consolidation | Demonstrate union of applicable behaviors, negative controls, and absence of duplicate application in the effective runtime configuration. One remaining source file or a successful package build cannot establish that only one plugin loads. Preserve forbidden-model policy separately from its historical hook implementation. |
| Cache regeneration | Identify the exact producer, cache identity/path, consumer and source revision; distinguish generated payload stability from freshness metadata. Verify refresh against an authoritative source, repeatability under the same source/input, correct consumer selection, and behavior for stale/missing data. Two distinct caches can have different freshness; success on one does not prove the other is current. A stale merge should not be presumed safe. |

The old Crosslink/RTK and OpenCode guard configuration is preserved as [historical harness evidence](../historical/Harness%20Setup%20and%20Permission%20Design%20History.md), not an active migration assignment. Current [task-scoped information](../methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md), [upstream compatibility](../methodology/Software%20Customization%20and%20Upstream%20Compatibility%20Method.md), and [current skills](../../skills/current/README.md) govern applicable present work. Independent current shared/project-local policy publication (WNASES-18), permission/source exposure (WNASES-19), and fresh-chat skill-selection behavior (WNASES-23) retain distinct scopes; their existence does not establish historical deployment or current enforcement.

**Surviving research and ownership:** repeatable artifact distribution, effective configuration and cache coherence, mechanism usability, and cross-repository maintenance friction are shared or independent software-tooling questions. These may inform ASES methods but are not automatically ASES Engine requirements. Actual product/harness fixes and release validation belong to their verified implementation owners; current ownership and deployed state of the old fleet are not established here. Preserve the useful experimental designs as reusable examples; do not reopen the August migration or turn every historical test into a backlog item.

**Verification limit:** the reviewed ASES records and bounded owner-source/commit search did not recover later execution reports for these tests; original legacy issue records and scratch artifacts were not accessible in this reconciliation. This is not evidence that the tests were never performed. Source cutoff: [c88e529d](https://github.com/rock-solid-sites/ASES/tree/c88e529d1b3d3e524b831793ef3dddc764581b99). No tests, distribution operations, model invocations or configuration changes were performed during this documentation review.

Status: Active. Supersedes: nothing (adds to Amendment 1). Operator direction
2026-08-15. Applies on top of Amendment 1 (`framework-amendment.md`).

## 1. D7 — REVISED: the test chooses the surviving push mechanism, not the scaffolding

The original D7 test reads "implement the minimal form first (plain scripts in
Tools/scripts/), track skip-rate." This conflates two different artifacts:

- **The scaffolding** — `sync-tooling.sh` and its transitional machinery. This
  is explicitly temporary (Amendment 1 §0, §4; the synthesis: E is
  migration-only). Its skip-rate is **not** evidence about the target state.
- **The surviving push mechanism** — the durable tooling that distributes
  canonical Tools content to consumers once the target topology is in place
  (`tools doctor/link/install/promote`-style thin tooling, or Makefile
  targets, or equivalent). This IS the core deliverable of the migration
  (Amendment 1 §4). Its skip-rate is what D7 must measure.

**Revision:** D7 tests the form of the **surviving mechanism**, not the
scaffolding. The dogfood window begins only when the surviving mechanism
exists in its minimal form and the scaffolding is on its way out. Measure the
surviving mechanism's skip-rate and recall-failure rate. Threshold unchanged
(≥2 missed sync/link/install events in the window → upgrade affordance;
doc-lookups dominate → command form with completion wins). The scaffolding's
own skip-rate during the transition is recorded as context but is NOT a D7
input.

## 2. NEW — Phase-0 correctness-fix verification (adds to the framework)

The framework currently has no explicit verification for the four Phase-0
correctness bug fixes (hook-config precedence, plugin.ts/dynamic-models.ts
consolidation, models-cache regeneration, whitelist). D6 covers the whitelist
A/B. The other three get verifications here:

### 2.1 Hook-config precedence fix — regression verification

The live bug: `git merge` appears in BOTH `by_type.orchestrator.gated_
git_commands` AND top-level `blocked_git_commands`; the global block is
checked first, so orchestrator merges are falsely hard-blocked despite the
role override.

- **Signal:** an orchestrator-role `git merge --no-ff` with an active issue
  either passes the gated path or is blocked.
- **Test:** (a) with the fix applied and an active issue, run an orchestrator
  `git merge --no-ff` in a scratch repo → must pass the gated path (not be
  hard-blocked as "PERMANENTLY FORBIDDEN"); (b) with NO active issue, the
  same merge → must be blocked (gating still enforced); (c) schema-level:
  load the config through a blocked∩gated overlap check → an ambiguous config
  (same command in both lists) must be **rejected** at load time, not silently
  resolved.
- **Threshold:** (a) passes, (b) blocks, (c) rejects overlap. Any deviation =
  fix incomplete.

### 2.2 plugin.ts / dynamic-models.ts consolidation — verification

- **Signal:** a single consolidated model plugin carries the union of both
  behaviors without regression.
- **Test:** deploy the consolidated plugin to a scratch user-level config;
  verify (a) #347 grok-ban still blocks forbidden providers, (b) the
  models-cache merge still applies (when a valid cache exists), (c) the
  provider-suppression behavior from both originals is preserved, (d) no
  duplicate application (the #103 double-apply root cause is gone).
- **Threshold:** all four hold in a live session smoke test.

### 2.3 models-cache regeneration — verification

- **Signal:** a deterministic regeneration command produces a current cache
  and is idempotent.
- **Test:** run the regeneration command; verify (a) the cache timestamp
  advances and reflects the live catalog, (b) re-running produces identical
  output (idempotent), (c) the plugin, given the fresh cache, no longer merges
  stale provider configs (spot-check that a provider's models match the
  regenerated cache).
- **Threshold:** (a)–(c) hold. If no deterministic regeneration is possible,
  the merge must be **removed** (documented decision) rather than left stale.

## 3. Note on D4 (state-machine disposition)

Amendment 1's framing (transitional machinery is scaffolding) strengthens D4's
"drop entirely" outcome: since the state machine is scaffolding, the question
is whether detection survives at all. The existing D4 test (0 genuine drift
events in a clean window → drop) is consistent and unchanged.

## 4. WHAT-NOT-TESTED

- The D7 revision's distinction (scaffolding skip-rate vs surviving-mechanism
  skip-rate) requires the surviving mechanism to exist in minimal form; it
  cannot be measured pre-migration.
- The Phase-0 fix verifications (2.1–2.3) require the fixes to be applied
  first; none are run as of 2026-08-15.
- 2.1(c) schema-level overlap rejection assumes the schema fix (Qwen's
  preferred approach over a one-line list edit) is adopted; if the one-line
  edit is used instead, (c) is replaced by a config-audit check.

---

# Amendment 3 — D6 decision note (whitelist policy: Policy A + B-watchdog, provider-list policy)

> **Local research reconciliation (2026-11-25) — provider/model visibility, D6.** Amendment 3 records the August scratch A/B spike and the operator's discovery-policy decision; Amendment 4 specifies its subsequent historical manifest. They are evidence and a dated policy decision for the then-existing OpenCode fork, not the current ASES launch authorization or a present provider configuration. Original text preserved.

### Distinct questions and scope of the result

- The original D6 question was catalog freshness, dead entries and forbidden-model visibility. In the recorded #379 scratch fixture, the pp3g binary exposed seven built-in models; the plugin whitelist could contract that set but could not add new entries. The models-map merge exposed newly added zero-price entries, with visibility in seconds and no manual edits; the forbidden-pattern block held in that fixture. A curated allowlist with refresh validation could detect list drift without overcoming the binary's visibility cap. The decision favored discovery-first merging (A), retaining validation as a secondary watchdog (B), not automatic dispatch.
- The experiment did not exercise a network-dependent refresh, real-token account, full picker/UI selection or actual model invocation. The original scratch artifacts are described in the record, not independently recovered in this reconciliation. The later provider manifest and native token-gating behavior were specified/observed, not verified by a subsequent live-token test in this record. The historical disabled-provider list and paid-visible carve-out describe dated account circumstances; do not copy them into a current config or infer present balances, eligibility or provider-wide prohibitions.
- The current [agent-launch skill](../../skills/current/agent-launch/SKILL.md) governs dispatch: exact caller-side model, provider/endpoint, host, authorized account/funding mode and verified allowance/limits; no inferred substitute, automatic fallback or unauthorized overflow. The xAI/Grok exclusion remains permanent; Luna is restricted to the approved ChatGPT Plus/Codex subscription route. Other provider routes are not blanket-banned (Phoenix Grove has distinct authorization). A displayed model, a working credential, a zero-price listing or a positive balance alone does not authorize use. Visibility filtering is not an enforcement proof.
- Keep catalog discovery/freshness, credential reachability, account-specific entitlement/current availability, demonstrated capability/task fit, scoped authorization and measured execution/billing distinct. The [Capability Registry](registry/AI%20Capability%20Registry%20Specification.md) and [Model Routing Matrix](registry/Model-Routing-Matrix.md) are descriptive research evidence. The [Resource Solver reconciliation](Resource%20Solver%20Specification%20Reconciliation%202026-11-02.md) separately proposes account-scoped admission and metering; it is not a verified universal admission implementation. Do not revive a second registry or assume the old picker plugin satisfies those proposed controls.

**Surviving research and ownership:** discoverability and stale-catalog management are general/shared tooling questions, with actual implementation owned by the relevant harness/plugin repository; cross-project or independent subject grouping remains unresolved. ASES owns its task-specific dispatch and funding authorization decisions, and the Resource Solver owns its distinct experimental allocation/admission question. An interesting unresolved investigation is whether fresh catalog observations can inform selection without implying authority or concealing legitimate choices, with account-specific provenance and explicit unknown state. Do not treat that as authorization for a new plugin, watchdog, model launch or migration. Current deployed picker/plugin behavior is unverified. This is separate from the transition and specific correctness-fix evidence (D1–D5/D7 and Phase 0), which still requires individual review.

Source cutoff: [ee70fa50](https://github.com/rock-solid-sites/ASES/tree/ee70fa50d8e9ff855592fc95a06bdf6950447d7e). No catalog refresh, provider call, config modification, or experimental rerun performed.

Status: Active. Supersedes: nothing (adds to Amendment 2). Operator direction
2026-08-15. Applies on top of Amendment 2. Records the DECIDED D6 outcome from
the A/B spike (issue #379). The decision-note text below is preserved intact.

# Decision note — D6 whitelist policy (appended to Decision Test Framework)

Status: Decided. Operator-approved 2026-08-15. Test evidence: issue #379
(D6 A/B spike, scratch-only, all artifacts /tmp/d6-spike/artifacts/).

## Finding (empirical, from the spike)

- The pp3g-fork **binary has a baked-in 7-model set** for the `opencode`
  provider; `--pure`/no-cache runs return the same 7 regardless of
  models.json. The plugin whitelist can only **contract** that set; it can
  never expand it.
- The **only** mechanism that expands visibility is the plugin's **models-map
  merge**: config-added models surface if they are free (cost 0) AND
  new-to-binary. This is what enables discovery.
- Policy A (discovery-first blocklist + auto-derived models-map merge from the
  live catalog): time-to-visibility = **seconds with zero manual edits**;
  forbidden block holds; zero dead-entry surface.
- Policy B (curated allowlist + refresh-validation): validation bounds *list*
  drift but **cannot make a new model visible** (binary cap) — it bounds the
  wrong thing.
- 20 free models are currently marked deprecated in the live catalog (drift
  beyond the original baseline).

## Decision

**Phase-0 whitelist fix = Policy A's mechanism as the foundation:**
forbidden-pattern blocklist (grok/x-ai, the existing #347 guards) +
auto-derived models-map merge (every cost-0 model from the live catalog) on
launch. No curated allowlist.

**Keep Policy B's validation as a cheap secondary watchdog:** a scheduled
refresh-validation run against the live catalog flags dead entries
(DEAD=missing/deprecated) and registry changes. It bounds dead-entry
accumulation without gating visibility.

**Provider list policy (operator direction, same date):** remove providers
that are not needed, or shorten provider model lists to free-only models for
now. The free-only restriction is *automatic* under Policy A's mechanism
(only cost-0 models surface); provider *removal* is expressed as an explicit,
documented disabled-provider list in the canonical plugin (same family as the
#347 forbidden-pattern blocklist). Future expansion is: edit the documented
list in the canonical source → push to consumers (the D7 surviving push
mechanism) → watchdog validates. Quick and documented by construction.

## How this fits the architecture

- Lives in the canonical model plugin (Tools after the reverse-sync seed);
  Phase 0 applies it once, Phase 1 seeds it, the D7 mechanism pushes it.
- Provider suppression = the documented disabled-provider list; the fix is a
  one-file edit in the canonical source, then push. No reverse-sync ever
  again after the seed.
- Regression coverage = Phase-0 fix verification 2.2 (plugin consolidation)
  and 2.3 (models-cache regeneration) in the framework.
- The D6 A/B mechanism and this provider policy are recorded here so the
  future change path is a documented, mechanical edit, not tribal knowledge.

## WHAT-NOT-TESTED

- No network-reliant `--refresh` runs; no full UI/selection test; no actual
  provider call (catalog-only injection); the fork binary's baked-in set is
  out of scope.
- The disabled-provider list contents (which providers to remove vs shorten)
  are an operator decision pending; the mechanism is decided, the manifest is
  not yet written.

---

# Amendment 4 — Provider Visibility Policy (operator-confirmed 2026-08-15)

Status: Decided. Applies on top of Amendment 3 (D6 decision note). This is the
concrete provider-manifest policy for the Phase-0 plugin fix.

## Governing principle

**Provider visibility is driven by credentials + usable-credit state, not by a
static catalog manifest.**

- opencode already token-gates providers: providers without API tokens do NOT
  appear in the `/models` list. We do not fight or duplicate this (no static
  removal list for token-less providers — it would break the moment a token is
  added).
- Our policy layer handles only what opencode does not: free-only filtering,
  the paid-visible carve-out, and explicit disabled/forbidden entries.

## The policy (three layers)

**Layer 1 — token-gating (native).** No API token → invisible. Owned by
opencode; untouched by us.

**Layer 2 — free-only merge with a paid-visible carve-out (Policy A
mechanism).** Providers WITH tokens surface free (cost-0) models only, EXCEPT
providers on the explicit `paid_visible_allowlist` (active paid credit), which
surface their full list and stay auto-updated from the live catalog.

**Layer 3 — explicit disabled/forbidden list.** Only where a specific reason
requires hiding despite a token:
- grok/x-ai (#347 forbidden, permanent)
- `google-vertex-anthropic` — Vertex promo credits cannot be used for Anthropic
  models, so its Anthropic models must not surface (Vertex's other usable
  models may surface normally)
- providers with a token but no active credit that are paid-only
- `deepseek` — kept disabled (per operator: both deepseek models are obtained
  via the opencode/opencode-go providers, so the direct deepseek provider adds
  nothing)

## The concrete manifest (canonical, lives in the Tools plugin)

| Category | Members | Result |
|---|---|---|
| `paid_visible_allowlist` | `opencode-go` | Full visibility, always updated from live catalog (our main paid provider) |
| `disabled_providers` | `deepseek`, `openai`, `cloudflare`, `cloudflare-ai-gateway` (existing) + `google-vertex-anthropic` + grok/x-ai forbidden block (#347) | Hidden |
| Free-only auto-merge | everything else with a token (e.g. `nvidia` 96/100 free, `cohere` 1/14 free, `google-vertex` non-Anthropic) | Free (cost-0) models only, derived from live catalog on launch |
| Token-less providers | the ~180 remaining | Already invisible via native token-gating; untouched |

**Note on cohere/nvidia (operator 2026-08-15):** no credits held for either;
only free-tier models are viable for now. This needs no list entry — the
free-only merge surfaces exactly their free models, and if no token is held
they are invisible via Layer 1.

## How future changes stay quick and documented

- **Add a token for a new provider** → free models appear automatically (no
  edit).
- **Start paying for a provider** → one-line addition to
  `paid_visible_allowlist`.
- **Credit runs out / stop using** → one-line removal from the allowlist (or
  add to disabled).
- **Provider's Anthropic models become usable** (Vertex case) → one-line
  removal from disabled.
- All edits happen once in the canonical Tools plugin, pushed to every
  consumer via the D7 surviving push mechanism, validated by the B-watchdog
  (Amendment 3). Never per-machine editing.

## Relation to the D6 decision (Amendment 3)

This is a refinement of D6's "provider list policy": the free-only restriction
is automatic under Policy A's mechanism; provider removal is the documented
`disabled_providers` list; and the paid-visible carve-out for `opencode-go` is
the one case where free-only must NOT apply. The D6 A/B mechanism is
unchanged; this fills in the manifest contents that Amendment 3 left pending
("the disabled-provider list contents are an operator decision pending").

## WHAT-NOT-TESTED

- The specific provider visibility behavior (with real tokens) is not
  executed-tested; the token-gating claim (Layer 1) is the user's observed
  behavior, not a fresh experiment.
- `google-vertex-anthropic` disabling and the exact free-model surfacing for
  nvidia/cohere are specified from catalog data + operator statement, not
  verified in a live token'd session.
- The manifest is written as policy here; the Phase-0 implementation
  (plugin.ts consolidation + D6 A mechanism) is a separate task that consumes
  this policy.

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
