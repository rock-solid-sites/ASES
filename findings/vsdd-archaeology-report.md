---
title: VSDD Archaeology — Fork Baseline for EDASES Thin-API
program: EDASES
layer: Research
document_type: Analysis
status: Draft
authority: Derived
crosslink_issue: 500
source_repo: https://github.com/dollspace-gay/vsdd-cli
clone_path: /tmp/vsdd-cli
commit_range: 5ccf740..6d4fad0
commit_count: 186
date_range: 2026-05-27 .. 2026-07-29
generated: 2026-08-27
author_role: Consolidator (synthesis of Tasks A-D + reviewer Cycle 2)
evidence_discipline: WHY/WHAT/HOW CERTAIN/WHAT-NOT-TESTED per AGENTS.md
cheapest_test: git log/show/ls-tree + grep probes; no Cargo build per constraint
---

# VSDD Archaeology — Fork Baseline for EDASES Thin-API (Crosslink #500)

> **Scope.** Code archaeology, not implementation. Determine the latest historical commit that contains most infrastructure we want while predating major VSDD-specific machinery — per `to-file/VSDD-archaeology.md` 8-section structure. All hashes/dates verified via `git -C /tmp/vsdd-cli log --all --oneline --date=short --format="%h %ad %s"` and `ls-tree -r --name-only | wc -l`. No `cargo build/test` executed (WHAT-NOT-TESTED).

> **Evidence posture.** Every cross-role claim states WHY/WHAT/HOW CERTAIN/WHAT-NOT-TESTED. File-count and commit-message claims are `proven` or `evidence-based` (git history); behavioral claims without line-read are `evidence-based`; runtime claims are `guess` and marked UNKNOWN.

Clone verified read-only at `/tmp/vsdd-cli` (`https://github.com/dollspace-gay/vsdd-cli`, `origin/main`, HEAD `6d4fad0` 2026-07-29, 186 commits, 0 tags, linear `main`).

---

## 1. Repository Timeline — Chronological Architectural Milestones

Classification: **KEEP** (minimal API) · **EXTRACT** (useful but higher ASES layer) · **DROP** (VSDD-specific) · **REPLACE** (concept useful, protocol unsuitable) · **UNKNOWN**.

File counts via `ls-tree -r --name-only <hash> | wc -l`.

| # | Commit | Date | Files | What was introduced | Why it matters to EDASES fork | Verdict |
|---|--------|------|-------|---------------------|-------------------------------|---------|
| M0 | `5ccf740` | 2026-05-27 | 3 | **Initial commit.** `README.md` (857 lines) + `DESIGN-METHODOLOGY.md` (931 lines). No code, no `.crosslink`. | Establishes no forkable substrate before this; all else layers atop prose. | **DROP** (prose) · underlying idea "spec governs behavior" = EXTRACT to methodology |
| M1 | `b3d6e50` | 2026-05-27 | 38 | **Crosslink substrate deploy.** `.crosslink/` 34 files (`hook-config.json`, `rules/*.md` ~27, `knowledge.md`, `driver-key.pub`), `.mcp.json` (3 MCP stdio servers), `.gitignore` (crosslink ignores), `.claude/settings.json`. `tracking_mode=strict`, `signing=audit`, sentinel disabled, `blocked_git_commands` + `gated_git_commands=[commit]` + `allowed_bash_prefixes`. | **Earliest viable fork.** Entire Crosslink integration in one commit. | **KEEP** — primary fork reason |
| M2 | `ad92d82` | 2026-06-01 | 107 | **Cargo workspace + JSON Schemas.** `Cargo.toml` workspace (pinned `rust-toolchain.toml` 1.88), `vsdd-core` library (3 JSON schemas: `phase-primer.json`, `domain-prompt.json`, `supplement.json` via `jsonschema` draft 2020-12 strict), `vsdd` binary `init --check --ci-mode` stub (clap). 11 tests. | First Rust code; establishes workspace shape + schema discipline. | Workspace+discipline **KEEP** · 3 VSDD schemas **DROP** · supplement-loader concept **EXTRACT** |
| M3 | `9ff02dc`+`8407f5a`+`bf99abe`+`8a28512`+`87feb82` | 2026-06-01 → 2026-06-02 | 108→119 | **Verification & enforcement spine (pre-contract).** `9ff02dc` vsdd init pre-flight (git/crosslink/mdatron/cargo checks). `8407f5a` require `schema_class`. `bf99abe` `mdatron/patterns/cross-references.yaml` (E0207/E0208). `8a28512` `.githooks/pre-commit` running `mdatron verify` on staged markdown. `87feb82` `.github/workflows/mdatron-verify.yml` CI. | Earliest deterministic enforcement + verification machinery (priorities 3 & 4). | `mdatron verify` gate + CI **KEEP** · E0207/E0208 rules **EXTRACT** · preflight probe pattern **UNKNOWN** |
| M4 | `df4b93b`→`73921ac` | 2026-06-02 | 123 at `73921ac` | **Init implementation + cross-reference.** `73921ac` green — 9-step `vsdd_core::init::init()`: git check → prior manifest → 47-item plan (4 schemas+1 pattern+42 artifacts via `include_str!`) → drift/skip/overwrite → `.vsdd/events.jsonl`+`config.yaml` skeleton → `init-manifest.json` `{files:{path:{sha256}}}` nested → `ProjectInitialized` event. Idempotent (first=49 files, second=0), `sha2` dep. | Core file deployment with collision handling (5-category drift), sha256 manifest, atomic skeleton. Last commit before July respec. | Drift+manifest+idempotent loop **KEEP** · 42 VSDD artifacts **DROP** · drift categories **REPLACE** · event shape **UNKNOWN** |
| M5 | `a39c3eb` | 2026-07-19 | — | **Agent-first VSDD toolkit respec.** `.design/agent-first-vsdd-toolkit.md` (261 lines) + `2.md` (186): 9 behavioral contracts, 12 reqs, 12 AC, 5 open questions. Supersedes May corpus. | Pivot where substrate → system accelerates; code faithful to contract after this. | **DROP** prose · contracts **EXTRACT** |
| M6 | `fdbc3dc` | 2026-07-20 | — | **Data authoring R1 + fail-closed wiring.** `templates/registry/installed-artifact-manifest.md` (23 entries, 8 surfaces) + JSON schema, `.claude/settings.json` fail-closed (exit 2 if payload missing, was 0), `.githooks/pre-commit` blocks if `mdatron` absent (was skip). | Fail-closed is security-relevant primitive. | Fail-closed discipline **KEEP** · installed-artifact manifest **DROP** |
| M7 | `3fe10ac`+`7ba951a` | 2026-07-20 | — | **Layer 0: chassis-config + project guards.** `3fe10ac` `.gitignore` carve-outs + `hook-config.json` canonical re-serialization + `tracker_remote=origin`, `7ba951a` `rules/project.md` interim guards (plain-names register, crosslink 0.8.0 hold with defects #29/#30/#14, identity/privacy, commit-trailer). | Crosslink config hygiene for fork that keeps Crosslink. | **KEEP** (`tracker_remote`, hold metadata) |
| M8 | `46a71e4`+`fc7a7f8`+`3bd5d8c`+`437d6fa`→`6b7bf72` | 2026-07-19–20 | — | **Contract amendments batch (8 commits).** Attended/autonomous split, chassis-affordance, session-shape, verification arch, retrieval-shaped artifacts, milestone phasing, process-integrity, spec-review loop. | Mass contract growth demonstrates inflection — each amendment widens VSDD surface later code must implement. | **DROP** · `process-integrity` **UNKNOWN** |
| M9 | `fdbc3dc`→`0fd2146` (6 rounds) | 2026-07-20 | — | **Six data sets:** `86ad653` economics, `15ac4a3` dispatch+act-to-affordance, `630594d` gate data, `9574bd5` statusline, `8affbe5` state schema + composition scope, `fdbc3dc` installed-artifact manifest. All `markdown-with-frontmatter` + JSON schemas under `.mdatron/schemas/`. | "Versioned data set" primitive — 9 pairs (18 contract items). Data-driven design (frontmatter = governed data, validated at `mdatron verify`) is deepest structural choice. | Data contents **DROP** · carrier `markdown-with-frontmatter` **REPLACE** · economics/dispatch sets **EXTRACT** |
| M10 | `48c5584`→`358c6d6`→`52a980d` | 2026-07-21 | 197 at `d7fe1fc` | **Layer 1: state + registry.** `48c5584` red gate (25 failing tests: `state/{read,write,schema,mod}`, `registry/{frontmatter,mod,sets}`, `diagnostics`). `358c6d6` green: 9 registry loaders (schema-pair validation), state reader (`validate_bytes`, version gate), atomic temp+rename write (forward-only `published`, gate-consistency), `Diagnostic` from statusline tokens, `serde_yaml_ng 0.10`. 31+25 tests green. | Core persistence + registry loading primitive (structured results, execution boundary). | `state` atomic read/write+version gate **KEEP** · `registry` frontmatter+typed-loader pattern **KEEP** · `Diagnostic` tokens **REPLACE** |
| M11 | `efe0107`→`a9b8d43`→`287d1ab` | 2026-07-21–22 | 270 at `287d1ab` | **Layer 2: snapshot, answer derivation, integrity.** `efe0107` red gate (13 failing): `snapshot/{mod,acquire}`, `answer/{derive,integrity,mod}`, `integrity_shell/{refs,substrate}`, convergence corpus 10 fixtures, `dispatch-data.json` 0.2.0. `a9b8d43` green: derivation rule table, 5 snapshot-scoped integrity checks, refs query (grammar-compiled), substrate 3-valued check, acquisition (milestones via list parse, session from status JSON, tracker-join empty = declared residue). 96 tests green. `287d1ab` Layer 2 boundary (20 fixtures). | Snapshot acquisition + phase answer derivation + integrity — most complex new primitive (verification/check execution + structured results). | `Snapshot` acquisition seam + `bounded_read`+`subprocess` **KEEP** · derivation rules **EXTRACT** · integrity kinds **DROP** · convergence oracle **REPLACE** |
| M12 | `74b0186` | 2026-07-22 | 270 | **Core removal — drop `mdatron-core` seam.** Shim `vsdd-core/src/schema_check.rs` (`jsonschema` 0.18 draft 2020-12), `cross_references.rs` drives `mdatron` binary `verify --json`. `Cargo.lock` -144 lines. | Binary-first directive; shim is portable schema-pair primitive. | **KEEP** (`schema_check.rs` pattern) |
| M13 | `d84109f`→`a49206f`→`870836c` | 2026-07-22 | — | **Layer 2 fix passes R1–R3.** `d84109f` bounded subprocess tier + shell honesty + uniform gate conjunct; `a49206f` whole-run deadline (channels + remaining budget, `TimedOut`), 4 KiB stderr cap with sanitize-first truncation; `870836c` degenerate HOME, stderr posture, tempfile trees. | Security/lifecycle hardening — directly backportable. | **KEEP** = `subprocess.rs` + deadline + sanitize ordering |
| M14 | `94c30d1`→`24e76e2` | 2026-07-25–28 | ~300 | **Layer 3: status renderings + terminal cleaning (largest expansion).** `94c30d1` red gate 18 tests, `09d1a43` green (segment/human/machine/broken/`multi.rs`, `vsdd status --machine/--statusline/--repo-set`), rounds 1–5: identity on broken lines, terminal cleaning, budget instruments, display-spoofing, `Default_Ignorable`, machine form at source. `498eb52` bound broken-state quoted, `24e76e2` rebuild cleaning on `Default_Ignorable` (`icu_properties` `Cc/Cf/Zl/Zp` + DICP, `clean_json_strings`). | Renderings = VSDD presentation; cleaning = generic safety. Largest VSDD accretion. | Renderers **DROP** · `text.rs` concept **KEEP** but impl **REPLACE** (VSDD-shaped) |
| M15 | `a6bc62b`→`d146019`→`6d4fad0` | 2026-07-27–29 | 300 | **Guardrails + routing-before-fix + mdatron 0.4.0.** `a6bc62b` Layer 2 `unrouted-findings` query (REQ-5 forward-only), `a736eb7` Slice 1 design (`finding-query join`), `d146019` Slice 1 gate + CI: `gate_verdict` Pass/Block/Unverifiable + `vsdd gate [--machine]` + `.github/workflows/routing-gate.yml`, `c94ba2e` mdatron 0.4.0 adoption, `6d4fad0` E0093 forcing-seam block. | Latest HEAD — strongest guardrail, but most VSDD machinery accumulated. `vsdd gate` + CI are only head-relevant primitives not present mid-July. | Gate predicate **DROP** · gate-verdict pattern + `routing-gate.yml` shape **KEEP** (generic) · vocab blocks **DROP** |

**Summary counts (verified):** `b3d6e50` 38 → `ad92d82` 107 → `73921ac` 123 → `d7fe1fc` 197 → `287d1ab` 270 → `6d4fad0` 300. Linear history, no branches — every milestone supersets prior.

---

## 2. Crosslink Integration Timeline

**WHY:** Crosslink integration is the primary fork reason — before evaluating any VSDD code we must know what Crosslink surface the fork inherits.
**WHAT:** `git log --all --oneline -- .crosslink` (8 commits), `--diff-filter=A` (first adds), `show --stat` at each, and `ls-tree` diff b3d6e50 vs HEAD.
**HOW CERTAIN:** proven for log/file-presence; evidence-based for contents; WHAT-NOT-TESTED: no `crosslink sync`/`crosslink --version`/hook execution executed (file-presence claim only, not runtime-proven).
**CHEAPEST TEST:** `log -- .crosslink | wc -l` + `ls-tree -r --name-only b3d6e50 | grep crosslink` before any source read — confirms stable substrate without building.

### 2.1 First integration

- **Commit `b3d6e50` 2026-05-27** `crosslink init: deploy substrate (hooks, rules, MCP servers, signing)` — 36 files, 2013 insertions. Only commit where `.crosslink/` appears via `--diff-filter=A` (verified: `ls-tree 5ccf740` has zero `.crosslink` files; `ls-tree b3d6e50` has 33).
- Contents: `hook-config.json` (`tracking_mode=strict`, `signing_enforcement=audit`, sentinel disabled, `blocked_git_commands` push/merge/rebase/reset/clean/stash/tag, `gated_git_commands=[commit]`, `allowed_bash_prefixes=[crosslink, git status/diff/log, cargo test/build, npm…]`, `agent_overrides` relaxed for push --force), `rules/` 27 files (`global.md` 195 lines, `tracking-strict.md` 209, `quality.md` 89, `sanitize-patterns.txt` 22 etc.), `driver-key.pub`, `.mcp.json` (MCP servers via `uv run`), `.claude/settings.json`, `.gitignore` 36 lines. Classification: **KEEP**.

### 2.2 Major subsequent changes (only 8 commits touch `.crosslink` in 186 — proven stable)

| Commit | Date | Change | Verdict |
|--------|------|--------|---------|
| `fdb10d1` | 2026-05-27 | Track `.crosslink/.gitignore` per convention (inner gitignore for agent files) | **KEEP** trivial |
| `7ba951a` | 2026-07-20 | Project rules interim guards: plain-names register, crosslink 0.8.0 hold with 4 known defects (#29,#30,#14 + rebinding), identity/privacy, commit-trailer | KEEP hold metadata · DROP register prose |
| `3fe10ac` | 2026-07-20 | Chassis-config reconciliation: `hook-config.json` canonical re-serialization + **`tracker_remote=origin`** + Rust lint/test populated, `.gitignore` chassis-state ignores | **KEEP** (`tracker_remote` fixes hub sync warning) |
| `fdbc3dc` | 2026-07-20 | `rules/project.md` +12 lines (sanctioned phrases, concrete referents) — fail-closed manifest round | DROP/EXTRACT |
| `c1dbb93` | 2026-07-21 | Layer-1 oracle artifacts carry crosslink work — indirect hit in `log -- .crosslink` filter; no `.crosslink/` file write | UNKNOWN |
| `f520cdd` | 2026-07-22 | **0.8.0 hold cleared**, `rules/project.md` scope ruling rewrite (24 lines) | **KEEP** (documents upstream #29/#30/#14 patched, hub v3) |
| `d84109f` | 2026-07-22 | Layer 2 round 1 — `rules/project.md` bounded subprocess tier rule | **KEEP** (subprocess tier = enforcement primitive) |
| `a736eb7` | 2026-07-29 | Crosslink consumption deepening: `templates/statusline` wiring + `acquire_snapshot` crosslink tracker join (milestones via `crosslink` CLI, session from status JSON) — not a `.crosslink/` file but Crosslink consumption | **KEEP** conceptually |

*Note:* `.mcp.json` landed at `b3d6e50` and never modified after (only that hash in MCP history). Language rules `rules/rust.md` etc. untouched since `b3d6e50`.

### 2.3 Current integration (at `6d4fad0` 2026-07-29 HEAD)

- `hook-config.json`: `tracking_mode=strict`, `tracker_remote=origin`, `agent_overrides` relaxed, sentinel disabled, `agent_lint_commands=[cargo clippy, cargo fmt --check]`, `agent_test_commands=[cargo test --workspace]`, `signing_enforcement=audit`. No direct `.crosslink` touch after `d84109f` 2026-07-22 — HEAD adds no new hook-config beyond `3fe10ac`→`d84109f`.
- Rules: `rules/project.md` at fix-pass state (bounded subprocess tier + 0.8.0 cleared). Language rules unchanged since init.
- MCP: `.mcp.json` at `b3d6e50` state.
- Sibling knowledge pages referenced by `a39c3eb` under `.crosslink/knowledge` — not probed, marked UNKNOWN.

### 2.4 Smallest viable integration

**Recommendation: `b3d6e50` alone is smallest viable.**

- **WHY:** Delivers 100% of Crosslink substrate in one commit; later changes are surgical patches (`tracker_remote=origin`, hold-clear, project rules prose) totaling < ~100 lines net. Any fork starting at `b3d6e50` gets working strict-mode Crosslink with no later machinery.
- **WHAT:** `show --stat b3d6e50` 36 files; HEAD vs `b3d6e50` `hook-config.json` diff = `tracker_remote` + lint/test populate + canonical serialization only.
- **HOW CERTAIN:** evidence-based (stat + message evidence, not byte-diffed).
- **WHAT-NOT-TESTED:** actual `crosslink sync`/issue lifecycle at `b3d6e50` not executed; claim is file-presence not runtime.

*Pragmatic floor for a thin-API that delegates to Crosslink via subprocess:* `b3d6e50` is floor, but a tool that runs `crosslink` commands benefits immediately from `73921ac` (preflight probe) or `d7fe1fc` (bounded subprocess) — see §3 runners-up.

### 2.5 Later changes important enough to backport selectively

If forking at `b3d6e50` or `73921ac`, cherry-pick these (no machinery bloat, security/process value):

1. `3fe10ac` — `tracker_remote=origin` + Rust lint/test + `.gitignore` chassis-state ignores. Cost ~10 lines. Fixes hub sync warning.
2. `f520cdd` — 0.8.0 hold cleared (24-line `project.md` swap). Prevents stale hold confusion.
3. `d146019` CI shape `.github/workflows/routing-gate.yml` (68 lines) — but VSDD-shaped; keep **pattern** (install crosslink → `crosslink sync` → run `vsdd gate` as required check), DROP predicate.
4. `fdbc3dc` fail-closed wiring (exit 2 if payload missing) — 12 lines `.claude/settings.json` + 8 `.githooks/pre-commit`. Generic safety.
5. `45068fd` provenance honesty (state verdicts as `unverified-self-report`) — aligns with sandbox fix priority.

Whole later Crosslink drift is ≤ ~200 lines across 4 commits.

---

## 3. Candidate Fork Points — 3–5 Plausible Commits + Preferred Baseline

Criteria: latest commit containing most wanted infra (Crosslink, agent/work-item/session, hooks, verification, structured results, execution boundary, capability/sandbox, RPC) while predating major VSDD accretion. All hashes/dates verified; file counts via `ls-tree`.

### Candidate A — `b3d6e50` 2026-05-27 — Minimal Crosslink substrate (38 files)

- **Capabilities:** 100% Crosslink substrate (hooks, rules, MCP, signing, `.claude/settings.json` seed), `.gitignore`. No Rust. Only commit with zero VSDD code surface.
- **Unwanted machinery:** Essentially none — `DESIGN-METHODOLOGY.md` prose doc only.
- **Missing vs later:** Workspace + schemas (`ad92d82`), init deploy + drift/manifest (`73921ac`), verification spine (`bf99abe`/`8a28512`/`87feb82`), fail-closed (`fdbc3dc`), `state`/`registry` (`358c6d6`), `snapshot`/`acquire` (`a9b8d43`), subprocess/sanitize (`d84109f`→`a49206f`), schema shim (`74b0186`), terminal cleaning (`24e76e2`), gate/CI (`d146019`).
- **Complexity:** ⭐ Minimal (~38 files, ~2k lines). Deletion ~0; implementation ~max (primitives must be authored).
- **Recommendation:** Viable if team prefers scratch-build on Crosslink chassis. Not preferred if team wants hardened primitives.

### Candidate B — `ad92d82` 2026-06-01 — Workspace + schema discipline (107 files)

- **Capabilities:** A + Rust workspace (pinned 1.88), `vsdd-core` schemas-as-`&'static str` (3 JSON schemas, draft 2020-12 strict), `vsdd init` stub (clap only), 11 tests.
- **Unwanted since A:** 18 `.claude/commands/*` phase/domain prompts + 14 `supplements/` prose — 69 files droppable prose.
- **Missing vs HEAD:** Init impl (`73921ac` 9-step deploy), drift/manifest/sha2, cross-refs, hooks/CI spine, state/registry/snapshot — all later layers.
- **Complexity:** ⭐⭐ Small (107 files, but 69 droppable; true code ~5 files).
- **Recommendation:** Weak — gains little over A while inheriting prompt-library bloat; no enforcement primitives yet. Not preferred over A or C.

### Candidate C — `73921ac` 2026-06-02 — Completed `vsdd init` deploy ⭐ **PREFERRED (primary)**

- **Capabilities:** B + `vsdd_core::init` fully implemented (9-step, 42 artifacts via `include_str!`, nested manifest `{files:{path:{sha256}}}`, drift/skip/overwrite, `.vsdd/events.jsonl`+`config.yaml` skeleton, idempotency proven, `sha2` dep), `schemas::require schema_class`, `.mdatron/patterns/cross-references.yaml` (E0207/E0208), `.githooks/pre-commit` (`mdatron verify`), `.github/mdatron-verify.yml` CI, red→green for init and cross-refs, whole suite green. **123 files** (+16 over B, `init.rs` 295 lines).
- **Unwanted since B:** Same 69 prompt/supplement prose as B (droppable). No `design/agent-first` contract, no data sets, no Layer 1–3 rendering/terminal complexity, no status/gate. **Last commit before July agent-first respec and Layer-1–3 waterfall** (verified: next commit after `73921ac` is `7b0960a` then 42-day gap to `a39c3eb` 2026-07-19).
- **Missing vs HEAD:** `fdbc3dc` fail-closed wiring, Layer 1 `state` atomic write + `registry` typed loaders + shim `schema_check.rs`, Layer 2 `snapshot/acquire` + `answer/derive` + integrity + bounded `subprocess` + sanitize, `text.rs` cleaning, `vsdd gate` + routing-gate CI, hold-clear — each small/atomic to backport; none mandatory for thin-API (can author simpler).
- **Complexity:** ⭐⭐⭐ Moderate (~123 files; deletable prose ~69). **Inflection elbow** (see §4).
- **Recommendation:** **Strong — preferred if charter is "minimum useful code surface" literally.** Keeps Crosslink (100%) + enforcement spine + `vsdd init` drift/manifest at lowest methodology cost; predates respec + Layer-1–3 accretion. Cherry-pick `3fe10ac` (`tracker_remote`), `f520cdd` (hold-clear), `fdbc3dc` fail-closed, `74b0186` shim pattern — all <200 net lines.

### Candidate D — `d7fe1fc` 2026-07-21 — Layer 1 boundary (state + registry done) (197 files)

- **Capabilities:** C + full July respec contracts + six data-set schemas + Layer 1 `state` (read/write/schema/mod + `bounded_read` 1 MiB) + `registry` (frontmatter/sets/mod + 9 loaders) + `diagnostics` + `fdbc3dc` fail-closed + Layer 0 chassis guards. Tests ~73→96 green.
- **Unwanted since C:** `.design/agent-first-vsdd-toolkit.md` + 6 data-set pairs (economics/dispatch/gate/statusline/state/composition — each `.md` + JSON schema) + `docs/refactor/` expansion + VSDD `Diagnostic` token set. Bulk of `.mdatron/schemas/` grew 4→12.
- **Missing vs HEAD:** Snapshot/acquisition, answer derivation, integrity checks (5), refs/substrate queries, subprocess bounded tier + whole-run deadline + sanitize, `text.rs` cleaning, status renderings, `vsdd gate` + routing-gate CI, later hardenings. Half of accretion still ahead (D→HEAD +103 files).
- **Complexity:** ⭐⭐⭐⭐ Large (197 files, `vsdd-core/src` 1→~11 files).
- **Recommendation:** Viable if thin-API genuinely needs state/registry primitives immediately and can absorb 1-layer methodology cost. `state` atomic temp+rename + version gate + `bounded_read` are most reusable. **Alternative preferred if persistence required day one.**

### Candidate E — `287d1ab` 2026-07-22 — Layer 2 boundary (snapshot + derivation + integrity) (270 files)

- **Capabilities:** D + snapshot `acquire.rs` (bounded runner + `crosslink`-CLI milestones + status JSON session + tracker-join residue), `answer/derive.rs` (rule table) + `integrity.rs` (5 checks) + `integrity_shell/refs.rs`+`substrate.rs` + `subprocess.rs` + convergence corpus 20 fixtures + `schema_check.rs` shim (`74b0186`) + fix passes R1–R3. Tests ~96 green.
- **Unwanted since D:** `answer/derive` rule table (VSDD routing), 5 VSDD integrity checks, convergence fixtures (VSDD oracle). Methodology depth ~doubled.
- **Missing vs HEAD:** Layer 3 renderings + `text.rs` terminal cleaning + `vsdd gate` guardrail + `routing-gate.yml` CI + mdatron 0.4.0 + hardenings. Largest blob.
- **Complexity:** ⭐⭐⭐⭐⭐ Very large (270→300 +30 but dense code in `status/` + `text.rs`).
- **Recommendation:** Not preferred — by here VSDD methodology outweighs thin-API value. Same primitives re-authorable from smaller API.

### Summary matrix

| Dimension | A `b3d6e50` 2026-05-27 | C `73921ac` 2026-06-02 | D `d7fe1fc` 2026-07-21 | E `287d1ab` 2026-07-22 |
|-----------|----------------------|----------------------|----------------------|----------------------|
| Crosslink | ✅ 100% | ✅ 100% (+`tracker_remote` cherry-pick) | ✅ + hold-clear | ✅ same |
| Enforcement spine | ❌ | ✅ `mdatron verify` + CI | ✅ fail-closed | ✅ same |
| `vsdd init` deploy | ❌ | ✅ 9-step | ✅ same | ✅ same |
| `state`/`registry` | ❌ | ❌ | ✅ atomic write + typed loaders | ✅ same |
| `snapshot`/`answer`/`integrity`/`subprocess` | ❌ | ❌ | ❌ | ✅ |
| VSDD bloat to delete | ~0 | ~69 prose files | ~120 prose+data | ~160 heavy |
| Append layers still missing | all | state→gate | snapshot→gate | renderings→gate |
| Deletion work | minimal | small | moderate | large |

### One preferred baseline

> **PREFERRED: `73921ac` `phase-2b (vsdd-cli): implement vsdd_core::init v0.1 scope` — 2026-06-02 — 123 files.**
>
> **Alternative (if state persistence needed day one): `d7fe1fc` `LAYER 1 BOUNDARY COMMIT` — 2026-07-21 — 197 files.** Keeps `state` atomic write + registry loaders + `bounded_read` hardening; requires deleting `.design/` + 8 data schemas + VSDD token table.
>
> **WHY C over A/B:** C is the latest small-substrate frame — captures enforcement + drift/manifest without swallowing Layer 1–3. The 42-day quiet (2026-06-02 → 2026-07-19) proves it sits on the inflection's lower lip; starting one commit later imports the nine-contract + data-driven waterfall. Cheapest-test-first: forgone primitives (bounded read/subprocess) at C are small, isolated, and explicitly backportable (see §7), whereas forgone methodology at D/E is 74–147 files of entangled VSDD logic.
>
> **WHY not HEAD `6d4fad0`:** 300 files, 79 post-`73921ac` commits, 6 data-set pairs, 5-layer renderings — most code is VSDD methodology system (brief warns "Do not treat methodology features as API primitives merely because they are implemented").
>
> **HOW CERTAIN:** evidence-based for existence/file-counts (proven via `ls-tree`); evidence-based for contents (commit bodies + `show --stat`); WHAT-NOT-TESTED: no source lines fully line-read for `state/write.rs`, `subprocess.rs`, `text.rs`; no `cargo test` runtime verification; no `crosslink sync` exercise.

---

## 4. Feature Growth Map — Where Complexity Came From

**WHY:** Locate natural `small Crosslink/verification substrate → large VSDD methodology system` point.
**WHAT:** `ls-tree -r --name-only | wc -l` per milestone + `cut -d/ -f1 | sort | uniq -c` + `show --stat`.
**HOW CERTAIN:** evidence-based on file-count/message; WHAT-NOT-TESTED: no `tokei` LOC, no `cargo bloat`, no churn histogram.

### Aggregate growth

```
b3d6e50   38 files  ─┐  crosslink substrate only (0% Rust)
ad92d82  107 files  ─┤  + workspace + schemas + 69 prompt/supplement prose  (+69, +182%)
73921ac  123 files  ─┤  + init.rs + CI/patterns  (+16, +15%)          ← elbow #1: small substrate ends
d7fe1fc  197 files  ─┤  + state/registry/fail-closed/contracts  (+74, +60%)
287d1ab  270 files  ─┤  + snapshot/answer/integrity/subprocess  (+73, +37%)
6d4fad0  300 files  ─┘  + renderings/terminal-gate/CI/hardening (+30, +11% but dense)
```

### Natural substrate → methodology transition

```
small Crosslink/verification substrate
        ↓  2026-06-02 73921ac — last small commit (123 files)
═══════════════════════════════════════════ 42-day quiet (2026-06-02 → 2026-07-19) — zero commits
large VSDD methodology system
        ↑  2026-07-19 a39c3eb — agent-first toolkit respec lands (261-line contract + 186-line companion)
```

- **Before gap:** 123 files, ~4 commits/week, prose + small init enforcement. Verification substrate is literally `.githooks/pre-commit` + one pattern file + one CI workflow + `init` drift loop (~400 net lines non-prose).
- **After gap:** 197 files at next boundary (`d7fe1fc`, 2 days later) with 9 contracts + 6 data-set pairs + `state`/`registry` modules + 25 failing gate tests. Then +73 to `287d1ab` next day (snapshot system), +30 to HEAD (renderings). **77% of all tracked files (177 of 300) land after the respec**, in **13 days** (2026-07-19 → 2026-07-29) vs 4 months prior for first 123.
- **Therefore `73921ac` sits precisely on the inflection's lower lip** — last commit before substrate → system jump. Starting there excludes inherent bloat; starting one commit later (`a39c3eb` or beyond) imports nine-contract + data-driven architecture.

### Growth attribution by subsystem

| Subsystem | Introduced | Files at HEAD | Classification | Growth story |
|-----------|------------|---------------|----------------|--------------|
| `.crosslink` | `b3d6e50` 2026-05-27 | ~34 | **KEEP** | Flat — 8 touches total; negligible growth; proven stable |
| `.claude/commands` + `supplements` | `ad92d82` 2026-06-01 | 28 + 14 | **DROP** (prompt libraries) | Step jump at `ad92d82`; never updated after June — dead prose; easy `DROP` |
| `vsdd-core/schemas` + `.mdatron/schemas` | `ad92d82` (3) | 12 schemas | **DROP** content / **KEEP** draft 2020-12 discipline | 3→12 schemas (4×) all after respec; each schema ⇒ loader ⇒ fixture ⇒ rule ⇒ check |
| `.crosslink/rules/project.md` + `hook-config` | `b3d6e50` seed | ~50 lines net | **KEEP** hook-config; **DROP** register | Slow linear edits; not growth driver |
| `.githooks` + `.github` CI | `8a28512` + `87feb82` then `d146019` | 4 files | **KEEP** discipline; **DROP** VSDD gate predicate | Stepwise: pre-commit (1), CI (1), routing-gate (1) — tiny, value-dense |
| `vsdd-core/src/init.rs` | `73921ac` 2026-06-02 | 1 file, 295 lines | **KEEP** loop / **DROP** artifact list | Single file, no further edits — fixed cost |
| `vsdd-core/src/state` + `registry` + `bounded_read` + `diagnostics` | `48c5584`→`358c6d6` 2026-07-21 | ~11 src files | **KEEP** state/read/write + loader + bounded_read; **DROP** Diagnostic tokens | Concentrated Layer-1 burst; then polishing |
| `vsdd-core/src/snapshot` + `answer` + `integrity_shell` + `subprocess` | `efe0107`→`a9b8d43` + `d84109f`→`a49206f` 2026-07-22 | ~7 src files | **KEEP** subprocess/acquire seam generic; **EXTRACT/DROP** answer/integrity VSDD | Layer-2 burst; fixtures 10→22 track schema count |
| `vsdd/src/status` + `vsdd-core/src/text.rs` | `94c30d1`→`24e76e2` Layer 3 | 7 files + `text.rs` | **DROP** renderers; **REPLACE** `text.rs` | Largest per-file density; most methodology presentation |
| `vsdd/src/status` + gate `vsdd gate` | `d146019` 2026-07-29 | +86 lines main.rs | **KEEP** gate pattern / **DROP** routing concept | Isolated thin slice |

**Takeaway for ASES:** Complexity did not accrue from Crosslink, workspace, init, or hooks — those are flat/stable. It accrued from **data-driven contract expansion** (schemas → loaders → fixtures → checks → renderings → guardrails) after `a39c3eb`. The pivot is architectural choice ("markdown-with-frontmatter is governed data"), not organic growth. A thin-API fork rejecting that choice can land at `73921ac` and never incur the later 177-file/13-day waterfall, losing only re-authoring cost for the few generic primitives (state persistence, subprocess bound, schema shim) that are themselves small, isolated, and explicitly backportable.

---

## 5. Surviving Primitive Candidates — "If We Stripped Everything Else Away…"

Do NOT design API — name the smallest mechanisms that appear to be doing irreducible, non-duplicated, generic work. Each entry: file(s), what it actually does, commit evidence.

| # | Primitive | File(s) + commit evidence | Irreducible work | Note |
|---|-----------|---------------------------|------------------|------|
| 1 | **Bounded file read** | `vsdd-core/src/bounded_read.rs` (`MAX_ARTIFACT_BYTES=1_048_576`, `take(CAP+1)`) — `8189017` 2026-07-21 L1C2 fix pass | Caps pre-parse materialization — memory concern at read layer; every Layer-1 read uses it; oversize → diagnostic never panic | Generic, zero extra deps beyond `std::fs` |
| 2 | **Bounded subprocess runner** | `vsdd-core/src/subprocess.rs` (deadline 10s, caps 1 MiB/4 KiB stderr, `Subprocess` enum, thread-per-pipe) — `d84109f` 2026-07-22 L2R1, hardened `a49206f` (whole-run deadline) + `870836c` | Whole-run deadline covering child + pipe reads, `TimedOut→kill+wait`, honest `NotFound` (= only `ENOENT`) vs `SpawnBroken`/`Refused`/`TimedOut`/`Oversize` | Best-engineered file in repo; directly the execution/control boundary the brief seeks |
| 3 | **Terminal/display cleaning** | `vsdd-core/src/text.rs` (`is_terminal_unsafe`, `clean_for_terminal`, `clean_json_strings` over `Cc/Cf/Zl/Zp` ∪ `Default_Ignorable_Code_Point` via `icu_properties` compiled_data) — `ff331dd`→`24e76e2` 2026-07-26 rebuild | Property-defined bidi/Trojan Source (CVE-2021-42574) defense; whole-of-output key+value pass closes field-by-field miss class | Six enumeration rounds proved enumeration fails; property is the primitive |
| 4 | **Atomic boundary-evidenced state write** | `vsdd-core/src/state/write.rs:write_state` (requires `BoundaryEvidence{commit}`, forward-only `published`, unique-temp-plus-rename via `tempfile::NamedTempFile` RAII) — `358c6d6` 2026-07-21 L1 green, hardened `a49206f`/`870836c` | Atomicity + boundary-evidence + forward-only immutability — generic for any boundary-committed artefact; crash-durability explicitly out-of-scope, recovery = restore-from-boundary | Primitive is atomic write; `published` forward-only rule is methodology |
| 5 | **Pure validate-bytes core** | `vsdd-core/src/state/read.rs:validate_state_bytes` (pure over bytes, no IO, `validate_bytes` → `Result<State, Diagnostic>`, version gate) — `48c5584`→`358c6d6` | Deterministic, testable validation separable from effectful read wrapper; trust-boundary (adopter-edited `.vsdd/state.yaml` never panics) | Property-test target |
| 6 | **Corroboration snapshot acquisition (purity-split)** | `vsdd-core/src/snapshot/{mod,acquire}.rs` (`Snapshot` + `acquire_snapshot(repo_root)` → `AcquisitionOutcome::Acquired|Absent|Unusable`, milestones via `run_bounded`, fix `a8888cd` 2026-07-29 empty-state) — `a9b8d43` 2026-07-21 L2 green | Explicitly-acquired materialized view + purity split (acquire once, derive pure) + outcome-not-error + `FindingFieldsAcquired` gating | Field set VSDD-shaped; pattern generic |
| 7 | **Diagnostic (rustc-shaped, vocabulary-driven)** | `vsdd-core/src/diagnostics.rs` (`Diagnostic{file,kind,machine_token,location,message,recovery_action,recovery_text}`) — `358c6d6` L1 green | Structured, recoverable error with vocabulary-driven remediation; location via `serde_yaml_ng::Error::location` | Shape generic; vocabulary VSDD-specific |
| 8 | **Schema-pair validation at load** | `vsdd-core/src/schema_check.rs` + `registry/mod.rs` (`jsonschema` draft202012 compile-once/validate-many, value-free `SchemaViolation`) — `74b0186` 2026-07-22 core removal | Load-time schema enforcement for adopter-editable versioned data sets | vsdd consumes mdatron BINARY, shim owns self-validation |
| 9 | **Fail-closed acquisition semantics** | `snapshot/acquire.rs` + `answer/derive.rs` degraded (`Acquired→None`, `Absent→"tracker-absent"`, `Unusable→"tracker-unusable"`, integrity skipped under degraded, degraded never changes next-action) — `a9b8d43` + `870836c` | Fail-closed degraded reporting: never pass vacuously, never swap Absent/Unusable | Bootstrap conflations declared (#753/#763) |
| 10 | **Multi-repo composition helper** | `vsdd/src/status/multi.rs` + `status/mod.rs:bounded_line` (per-repo `mpsc::recv_timeout` budget, `"no answer within budget"` breach) — `09d1a43` 2026-07-25 L3 | Per-member deadlines so one wedged repo cannot stall whole composed display; dedup on canonical spelling (#781) | Higher-layer UX but primitive pattern keepable |
| 11 | **Guardrail predicate shape** | `vsdd-core/src/answer/integrity.rs:unrouted_findings` + `status` + `main.rs:Gate` (extracted shared predicate → `gate_verdict` Pass/Block/Unverifiable, fail-closed, `SPINE_ONLY` gating) — `d146019` 2026-07-29 | One-predicate, no-divergence shape + fail-closed taxonomy + field-readiness gating | Specific predicate routing-before-fix is VSDD; shape is generic |

*Sources:* `git show --stat` at hashes above, `ls-tree -r --name-only` file lists, commit-message bodies describing behavioral contracts. No `cargo build` executed — so compile/dependency viability (jsonschema+icu_properties+tempfile) is unproven at each hash (WHAT-NOT-TESTED).

---

## 6. Things We Already Have Elsewhere — Do Not Duplicate

Distinguishes "already exists" from "verified sufficient" (brief §6).

| Capability in vsdd-cli | Elsewhere owner | Already exists? | Verified sufficient? | Verdict for fork |
|------------------------|-----------------|-----------------|----------------------|------------------|
| Crosslink coordination (issues, milestones, sessions, comments, hub sync) | **Crosslink** (`.crosslink/` substrate, `hook-config.json:tracking_mode:strict`, `driver-key.pub`) | ✅ exists | Not verified — vsdd's `snapshot/acquire` human-parses `crosslink milestone list`; ASES needs stable JSON surface | Do not duplicate tracker; REPLACE query transport when crosslink exposes machine surface |
| Work items / identity (agent identity, session/work-item lifecycle) | **Crosslink** (`session status --json`) | ✅ exists | Not verified — declares two bootstrap conflations (#753 session Absent vs Refused indistinguishability; #763 milestone gauge vs finding count) | Do not duplicate identity; fix upstream or live with declared conflation |
| Filesystem restrictions (allowed paths, capability bounding) | **Crosslink** `hook-config.json:allowed_bash_prefixes` + `rules/*.md` + ASES `AGENTS.md` D1–D4 doctrine | ✅ exists | Partial — allowlist is advisory inside agent harness, not kernel boundary; vsdd has no OS sandbox | Consume Crosslink restrictions; mark UNKNOWN whether kernel sandbox needed |
| Observer / audit store (position-emitting agents, durable store, cheap staleness, AUDITOR, reviewer) | **EDASES Observer** swarm v1.1 resilience design (`.design/observer-swarm-v1.1` → main `3fc3c60a`, fixes #460/#465/#466) + `docs/research/Workflow Topology Design` | ✅ exists | Partially verified — vsdd's `.vsdd/events.jsonl` append log is local mirror of Observer durable store | Do not duplicate observer; thin API acquires from Crosslink, delegates audit to Observer |
| ASES hooks / enforcement (pre-commit, CI gates) | **ASES** `.crosslink/hook-config.json` (`blocked_git_commands`, `gated_git_commands`) + `AGENTS.md` reasoning-certainty (`WHY/WHAT/HOW CERTAIN/WHAT-NOT-TESTED`) | ✅ exists | Not sufficient for ASES primitive needs — vsdd's `vsdd gate` + `routing-gate.yml` (process-integrity query) is distinct guardrail pattern | Keep ASES hooks; add generic guardrail shape, not VSDD predicate |
| Execution-engine work (statecharts, artefact lifecycles, property graph, XState v5, provenance) | **Execution Engine research** (`research/execution-engine-ui/synthesis/…`, Crosslink #14–21, `Execution Engine Vision.md`) | ✅ exists | Explicitly not sufficient — central tension is lifecycle-ownership (engine claims state that statechart reserves); reversed composition unevidenced | Do not lift vsdd's `state.yaml` into engine; engine needs own artefact lifecycle (REPLACE) |
| RCP research (formal checks) | **Existing RCP** research | ✅ research exists | Not as shared primitive — vsdd's `answer/integrity` is VSDD predicates, not RCP | Do not duplicate; ASES RCP defines own checks |
| Verification engine (`mdatron`) | **Mdatron** (tool-to-tool) | ✅ exists | Consumed as binary since `74b0186`; not a library | Do not vendor; pin & invoke; `schema_check` shim is only in-crate carry |
| Sandbox/container boundary (landlock/seccomp/bwrap/ns/cgroup) | **Unknown** — none of Crosslink/Observer/EDASES documents kernel sandbox | ❌ does not exist | UNKNOWN | Mark UNKNOWN — vsdd is PATH-trusting, FS-unconfined; decide in EDASES scope |

**Rule of thumb:** Crosslink owns coordination/identity/tracking/store. Thin API owns bounded acquisition, display-safety, diagnostics, schema-validated registry shape, atomic boundary-evidenced writes, and guardrail shape. VSDD owns phases, prompts, supplements, economics, convergence corpora, routing/letter-cluster predicates.

---

## 7. Later Fixes Worth Backporting — Do Not Backport, Just List

If baseline predates late-July hardening, these later commits are important enough to selectively preserve. Grouped by kind; each line: single commit, precise date, subject, why it matters. **No patch was applied.**

### 7.1 Security / Provenance / Display Safety (8 commits)

| Commit | Date | Subject | Why worth preserving |
|--------|------|---------|----------------------|
| `45068fd` | 2026-07-27 | `fix(security): mark state-sourced gate verdicts as unverified-self-report` (#818 F1) | Provenance honesty — state-sourced verdicts are self-report, not corroboration; without it status can lie about verification |
| `8087223` | 2026-07-27 | `fix(security): address the #818 Fix 1 cold-review revise (provenance + surface tests)` | Hardens F1 with tests + surface auditing |
| `498eb52` | 2026-07-26 | `harden(layer-3): bound + mark-untrusted the broken-state quoted content` (#818) | Bounds+marks quoted broken-state as untrusted — spoofing defense for failure path |
| `24e76e2` | 2026-07-26 | `feat(layer-3): rebuild terminal cleaning on the Default_Ignorable property` (#813) | Property-based cleaning (replaces hand-enumeration); six rounds proved enumeration always one short — critical if baseline predates |
| `52f9432` | 2026-07-27 | `fix pass, Layer 3 round 5: default-ignorable ranges, machine form at source, real wiring pins` (#798-#801) | Closes machine-form pass (sanitize at source, whole-of-output key+value) + wiring pins |
| `94d3c2c` | 2026-07-26 | `fix pass, Layer 3 round 3: display-spoofing cleaning, path-line miss, real falsifiers` (#788-#791) | Path-line miss + display-spoofing cleaning |
| `ff0d3a3` | 2026-07-26 | `fix pass, Layer 3 round 2: close the terminal-cleaning hole` (#784-#786) | Terminal-cleaning hole close |
| `ff331dd` | 2026-07-26 | `fix pass, Layer 3 round 1: identity on broken lines, terminal cleaning, budget instruments` (#776-#782) | Budget instruments + broken-line identity |

### 7.2 Crosslink Compatibility / Protocol / Lifecycle (6 commits)

| Commit | Date | Subject | Why worth preserving |
|--------|------|---------|----------------------|
| `a8888cd` | 2026-07-29 | `fix(milestone-leg): parse crosslink 'No milestones found.' as empty list` (#829) | Empty-repo milestone list: without it, lawful empty repo reports `Unusable` not `Acquired` |
| `f520cdd` | 2026-07-22 | `rules: the crosslink 0.8.0 hold is cleared` (#742) | Crosslink 0.8.0 compat — stale hold blocks startup if baseline predates |
| `74b0186` | 2026-07-22 | `core removal, vsdd half: drop the mdatron-core library seam` (#764) | vsdd consumes mdatron BINARY only (#739 boundary) — cleaner tool-to-tool seam |
| `25851ca` | 2026-07-21 | `contract: the mdatron boundary batch, tier rule, state re-home` (#739) | Declares vsdd↔mdatron tool-to-tool contract; without it boundary undocumented |
| `d146019` | 2026-07-29 | `Slice 1: the routing-before-fix guardrail — vsdd gate + CI leg` (#820) | Guardrail shape (fail-closed taxonomy + field-readiness + `vsdd gate` + `routing-gate.yml`) — predicate VSDD but shape generic |
| `a736eb7` | 2026-07-29 | `design: routing-before-fix guardrail` (#820) | Design artifact documenting REQ-4/5/7 (field-readiness, universe boundary) |

### 7.3 Process Lifecycle / Correctness / Sandbox (8 commits)

| Commit | Date | Subject | Why worth preserving |
|--------|------|---------|----------------------|
| `d84109f` | 2026-07-22 | `fix pass, Layer 2 round 1: bounded subprocess tier, shell honesty` (#746-#754) | Bounded tier + shell honesty (only `NotFound` is offline) — correctness of acquisition path |
| `a49206f` | 2026-07-22 | `fix pass, Layer 2 round 2: whole-run deadline, sanitize ordering` (#756-#763) | Whole-run deadline + sanitize-before-truncate — lifecycle gap close |
| `870836c` | 2026-07-22 | `fix pass, Layer 2 round 3: misreported gauge, degenerate-HOME, stderr posture, tempfile trees` (#766-#769) | Gauge + HOME + stderr handling |
| `8189017` | 2026-07-21 | `layer 1 code-round-2: the capped reader lands` (#731) | Capped reader + promised pin — without it reads have no materialization bound |
| `daacdc8` | 2026-07-21 | `layer 1 code-round fix pass: eight dispositions across write path` (#720) | Write-path dispositions incl. lost-update documentation + forward-only |
| `2eae830` | 2026-07-21 | `fix: record-destined machine forms render repo-relative paths` (#737) | Repo-relative paths for record-destined output |
| `d2c4a3d` | 2026-07-21 | `contract: machine-identifying content barred from records` (#730) | Privacy/correctness contract |
| `f1b6809` | 2026-07-21 | `wire the executable cross-field constraints (mdatron #73)` (#729) | Registry integrity constraints — without it registry can drift |

### 7.4 mdatron Compatibility Fixes (6 commits)

| Commit | Date | Subject | Why worth preserving |
|--------|------|---------|----------------------|
| `c94ba2e` | 2026-07-29 | `chore(mdatron): adopt 0.4.0 — bump pins, drop prose from jurisdiction` (#830) | mdatron 0.4.0 jurisdiction + pin — without it, `mdatron verify` flags `W0045` on superseded prose |
| `eac6589` | 2026-07-27 | `fix(test): seed cross_references TempProject jurisdiction via mdatron init` (#816) | Harness jurisdiction fix — without it tests vacuously pass |
| `0d4b489` | 2026-07-28 | `test(harness): positive controls make cross_references silent tests non-vacuous` (#822 F1) | Positive controls |
| `3ea9cdb` | 2026-07-27 | `chore(mdatron): proper v0.3.0 init + pin pre-commit to 0.3.x window` (#816) | Pre-commit pin — before it, hook floats and breaks |
| `067d58e` | 2026-07-29 | `feat(guardrail): arm the E0091 letter-cluster prohibition` (#823) | Vocabulary wiring |
| `6d4fad0` | 2026-07-29 | `feat(guardrail): arm the E0093 deprecated-term block` (#832) HEAD | Terminology grounding |

**Minimal critical set if forking at `73921ac`:** `f520cdd` + `74b0186` + `8189017` + `d84109f`/`a49206f` + `a8888cd` + `24e76e2` + `45068fd`/`498eb52` — seven patches, all ≤ ~200 lines except `text.rs` with `icu_properties` dep.

*If preferred baseline is HEAD (`6d4fad0` 2026-07-29), nothing to backport — already present.*

---

## 8. Recommendation

> **Minimum useful code surface rationale.** The thin-API owns bounded acquisition, display-safety, diagnostics, schema-validated registry shape, atomic boundary-evidenced writes, and guardrail shape. It does NOT own Crosslink coordination (already upstream), Observer/Engine lifecycles (already research), or VSDD's 42 prompts/18 domains/9 data sets/5-layer status renderings (methodology). The recommendation is therefore the earliest commit that still contains the reusable surface, not the commit that preserves most VSDD functionality. Deletion cost must not exceed authoring cost of the few portable primitives.

```
RECOMMENDED BASELINE: 73921ac  (phase-2b (vsdd-cli): implement vsdd_core::init v0.1 scope)
                       2026-06-02, vsdd-cli, 123 files
                       Verified: git -C /tmp/vsdd-cli ls-tree -r --name-only 73921ac | wc -l = 123
                       Hash confirmed via git -C /tmp/vsdd-cli log --all --format="%h %ad %s" --date=short
                       Parent bdae436 red gate; next commit 7b0960a docs/refactor binary-first plan (+22 reviews)
                       Gap after: 42 days quiet (2026-06-02 → 2026-07-19 a39c3eb respec) — inflection lower lip

ALTERNATIVE (if state persistence required day one): d7fe1fc  (LAYER 1 BOUNDARY COMMIT)
                       2026-07-21, vsdd-cli, 197 files (+74 over 73921ac, adds state/registry/bounded_read)
                       Keep only if thin-API must own persisted state on day one and can absorb
                       1-layer methodology cost (.design/ + 8 data schemas + Diagnostic tokens)

WHY:   73921ac is the last commit before the 42-day quiet and the a39c3eb agent-first respec
       that drives 77% of all tracked files (177 of 300) in 13 days. It contains the only
       filesystem primitive that is generically reusable (drift/sha256 manifest/idempotent
       deployment loop — 295-line init.rs + 47-item plan) and the only enforcement spine
       (mdatron verify pre-commit + CI) while predating the Layer-1–3 waterfall (state machine
       + snapshot/answer/integrity + status renderings + terminal-cleaning + guardrails).
       The bounded primitives forgone at 73921ac (bounded_read 8189017, subprocess d84109f/a49206f,
       schema shim 74b0186, cleaning 24e76e2, provenance 45068fd) are each small, isolated,
       and explicitly backportable (<200 lines except text.rs with icu_properties). By contrast,
       forgone methodology at d7fe1fc/287d1ab is 74–147 files of entangled VSDD logic (state schema
       + 9 registry sets + derivation rules + integrity checks + convergence corpus) that must be
       surgically deleted — deletion exceeds authoring cost. The execution boundary that d84109f
       provides is real but its cheapest falsifier (honest NotFound vs Unusable, whole-run deadline)
       can be re-derived from the documented primitives without inheriting the VSDD state shape.
       Cheapest-test-first therefore prefers the baseline that falsifies the premise "init can be
       naive" (73921ac already does) over one that also forces the premise "state machine is needed."

WHAT:  Based solely on git history (186 commits, 5ccf740 2026-05-27 .. 6d4fad0 2026-07-29, verified via
       git log --all --oneline --date=short, git show --stat at M0–M15, git ls-tree -r --name-only
       | wc -l at b3d6e50/ad92d82/73921ac/d7fe1fc/287d1ab/6d4fad0, grep verification for rpc/ipc/transport/
       sandbox/finops/observability empty paths, and direct reads of bounded_read.rs/subprocess.rs/text.rs/
       state/read.rs/state/write.rs/snapshot/acquire.rs/diagnostics.rs at HEAD). No cargo build/test,
       no crosslink install/sync, no file modification per constraint.

HOW CERTAIN: evidence-based for history/seam/file-count claims (proven via git log + ls-tree + show --stat);
             evidence-based for KEEP/EXTRACT/DROP/REPLACE classifications that cite file paths + commit bodies;
             guess for runtime/compile claims (cargo was never executed, dependency convergence at each SHA
             not validated, subprocess deadline pipe-deadlock avoidance not live-fired, terminal-cleaning
             Default_Ignorable property not probed with adversarial bidi payloads, crosslink hook execution not observed).

WHAT-NOT-TESTED: No cargo build / cargo test --workspace / clippy at any candidate SHA (explicitly forbidden by
                 archaeology constraint) — so "tests green / clippy zero" at 73921ac is producer-reported from
                 commit messages, not independently verified; consumer must treat as unverified-self-report.
                 No crosslink sync / session status --json / milestone list runtime exercise — file presence proven,
                 behavior unproven (especially human-format milestone list parse + session Absent vs Refused
                 conflation #753/#763). No line-level audit of vsdd-core/src/state/write.rs atomicity window,
                 vsdd-core/src/text.rs DICP cleaning, or vsdd-core/src/subprocess.rs deadline under descendant-
                 held pipes; behavioral claims rest on commit bodies + fix-pass enumerations. No schema JSON semantic
                 review — DROP classification of 12 schemas rests on filenames + commit prose, not schema content.
                 No routing-gate.yml workflow dispatch log inspection. No mdatron binary equivalence at 0.4.0.
                 No symlink/TOCTOU probe of bounded_read, no bidi/ZWJ fuzz of text.rs, no symlink dedup probe of
                 multi.rs per-repo budget.

KEEP:
  - .crosslink substrate (hooks/rules/MCP/signing/sanitize-patterns) as deployed at b3d6e50,
    reconciled at 3fe10ac/7ba951a, migrated at f520cdd 2026-07-22.
  - Bounded execution discipline shape (to backport, not yet at 73921ac): vsdd-core/src/bounded_read.rs
    (MAX_ARTIFACT_BYTES 1 MiB), vsdd-core/src/subprocess.rs (run_bounded, 10s deadline, 1 MiB cap,
    NotFound vs Unusable honesty, threaded pipe), vsdd-core/src/state/write.rs atomic temp+rename
    + vsdd-core/src/state/read.rs enumerated Absent/Malformed/PermissionOrIo — keep the PATTERN this
    report documents, cherry-pick via §7 if thin-API owns execution boundary.
  - At 73921ac itself: drift/sha256 manifest/idempotent deployment loop (generic artifact deployment
    primitive), mdatron verify fail-closed pre-commit gate + CI workflow (deterministic enforcement
    slot), Cargo workspace shape + jsonschema draft202012 discipline, diagnostic shape vocabulary-driven
    (file/kind/machine_token/location) with value-free violations.
  - CI shape after backport: .github/workflows/vsdd-test.yml + mdatron-verify.yml running own tests on PR
    (pin peer binary to tag, not floating main).

EXTRACT: (useful, belongs in higher ASES/methodology layer, not API primitive)
  - Registry-set mechanism (versioned, schema-validated registry with repair vocabulary) — lift the
    loader pattern (frontmatter-split + typed-loader + schema_check shim), not the 9 VSDD data sets.
  - Data-driven design discipline (markdown-with-frontmatter = governed data validated at mdatron verify)
    + convergence-corpus + schema-pair discipline (oracle → fixtures → red gate → green → fix passes)
  - Composition/scope vocabularies (economics/gate/dispatch/act-to-affordance/statusline-data) wiring
    constraints vs declarative — useful as methodology libraries.
  - Answer/Purity split (pure derive(pure) vs acquire(effectful) decomposition), multi-repo status
    composition (bounded_line with per-repo budget), preflight plan→walk→manifest automaton — lift
    pattern for capability-allowlist, replace VSDD payloads.

DROP:
  - All VSDD payload: vsdd-core/src/artifacts 42 include_str! bundles (10 primers + 18 domains + 14
    supplements), supplements/*.md (14), .claude/commands/vsdd-phase-*.md / vsdd-domain-*.md (28),
    templates/ registry mirrors, methodology.md + DESIGN-*.md prose (+ .design/ toolkit), review-log/*,
    manual-tests/convergence fixtures as shipped (20 VSDD-shaped triads), economics/gate/dispatch/
    statusline data set contents, E0091/E0093 vocabulary prohibitions (letter-cluster/deprecated-term),
    vsdd gate routing-before-fix predicate + vsdd status renderings (human/machine/segment/multi/broken
    + instruments) as shipped, installed-artifact-manifest VSDD shape.

REPLACE: (concept useful, protocol/impl unsuitable)
  - Peer verifier: mdatron binary → ASES verifier (own JSON Schemas + executable cross-field constraints);
    keep binary-on-PATH tool-to-tool seam (#739) + fail-closed pre-commit version pin (0.4.x #830).
  - Crosslink parse surface: snapshot/acquire's human-format "No milestones found." parse (#829, a8888cd)
    → stable JSON/RPC surface when crosslink exposes it (declared conflations #753 session, #763 gauge);
    keep run_bounded tier, replace parser when contract exists.
  - MCP transport: .mcp.json uv→python local servers (agent-prompt/knowledge/safe-fetch) → keep local uv
    pattern, re-wire knowledge fetch to ASES durable store / publication stream (ORCHESTRATOR.md §5.8).
  - Sandbox boundary: vsdd has no OS sandbox (seccomp/cgroup/container) — only bounded tier + text cleaning
    + allowlists. Thin-API must decide whether to wrap execution in real sandbox and thread outcome into snapshot.
  - Terminal cleaning impl if forking at 73921ac: VSDD's DICP property (24e76e2) still correct generic primitive
    (Cc/Cf/Zl/Zp + Default_Ignorable via icu_properties compiled_data) — replace only wiring to VSDD record shapes.

BACKPORT FROM LATER HISTORY (if forking at 73921ac; small, isolated, apply in this order — cheapest falsifier first):
  1. 3fe10ac 2026-07-20 — tracker_remote=origin + Rust lint/test + .gitignore chassis-state ignores (~10 lines).
  2. f520cdd 2026-07-22 — 0.8.0 migration (.crosslink/rules/project.md + .gitignore) — one small commit, unblocks agent.
  3. fdbc3dc 2026-07-20 — fail-closed hook/pre-commit wiring (exit 2 if payload missing) (12+8 lines).
  4. 74b0186 2026-07-22 — schema_check.rs shim (jsonschema 0.18 draft202012, value-free) — refactor, not bloat.
  5. 8189017 2026-07-21 — bounded_read.rs capped reader (MAX_ARTIFACT_BYTES + oversize detectable) — caps pre-parse.
  6. d84109f 2026-07-22 + a49206f 2026-07-22 — bounded subprocess tier (whole-run deadline, sanitize ordering,
     ENOENT-only NotFound #747, PATH honesty #754, deadlock-safe threaded pipes) + shell_red_gate corpus.
  7. a8888cd 2026-07-29 — "No milestones found." empty-state mirror in snapshot/acquire.rs (3-line parse branch).
  8. 24e76e2 2026-07-26 (+94d3c2c/800878a/ff0d3a3/52f9432) — text.rs property-based cleaning (Default_Ignorable,
     icu_properties compiled_data + unicode_general_category, two sinks) + Cargo dep — mid-size but isolated.
  9. 498eb52 2026-07-26 — broken.rs bound+mark-untrusted before rendering (quoted state content).
 10. 45068fd 2026-07-27 + 8087223 — GateProvenance::UnverifiedSelfReport + human/machine provenance honesty.
 11. 5a6ed06 2026-07-29 (+3ea9cdb/c94ba2e) — CI repoint: vsdd-test.yml running own tests on PR, pin peer to tag v0.4.0.
  Total drift ≤ ~300 lines (+ text.rs + icu dep); everything else is deletable methodology.

REMAINING QUESTIONS:
  1. Minimal surface scope — does thin-API own execution boundary? If yes, the bounded primitives (items 5–6
     above) become mandatory; if no, they are optional and 73921ac's forgone set is sufficient. Lean toward
     "thin-API owns at least bounded_read + subprocess + text cleaning" even if it delegates filtering.
  2. Crosslink human-format vs JSON — snapshot/acquire.rs declares #753/#763 conflations explicitly because
     crosslink exposes no JSON milestone list today. Backport path for thin-API depends on upstream crosslink
     exposing a stable machine surface; until then human-parse remains brittle.
  3. mdatron → ASES verifier cut line — vsdd shows three seams: library seam (dropped #764 #739 boundary),
     DSL Field Defined() (#12 codes), and vocabulary registry. ASES must locate own schema enforcement
     (issue #498 follow-up) before deleting vsdd-core/schema_check.
  4. Lifecycle ownership — vsdd's PhaseAnswer.derive claims state that EDASES synthesis reserves for XState
     statecharts. The reversed composition (statechart owns lifecycle, engine only schedules) is unevidenced.
     Forking a state machine that owns lifecycle risks contradiction with execution-engine-ui synthesis (High:
     property graph + XState v5). Decision belongs in Research layer, not on reduction branch.
  5. Bounded cost vs hard enforcement — who decides? DOE-STD-3022 / cost-rubric vocabulary lives in economics-data
     + instruments, not in subprocess. Execution Engine Vision separates cost (telemetry) from enforcement (hook/CI).
     Where budget enforcement lives (thin-API vs engine) is unmapped.
  6. Filesystem sandbox sufficiency — vsdd's sandbox is bounded ops + allowlists, not kernel sandboxing. ASES
     already has .crosslink path allowlists + AGENTS.md D1–D4 doctrine; whether verified sufficient for EDASES
     thin-API (and whether to re-expose capabilities à la CapTP/WASI) was not tested this session.
  7. Compile viability of historical SHAs — no cargo build/test executed per constraint. Rust 1.88 pin + Cargo.lock
     at 73921ac not validated to compile today; serde_yaml vs serde_yaml_ng split (#717) and mdatron-core removal may
     leave historical SHAs unbuildable without lock re-resolution — cheapest test is `cargo test --workspace` on the
     reduction branch before invoking any upstream marker.
```

---

## Appendix — Evidence & Limitations

- **Probes executed:** `git log --all --oneline -- <path> | wc -l` per path (Task D table, 16 paths, 8 non-zero), `git log --all --oneline --date=short --format="%h %ad %s"` per candidate, `git ls-tree -r --name-only <hash> | wc -l` at b3d6e50/ad92d82/73921ac/d7fe1fc/287d1ab/6d4fad0, `git show --stat` at each milestone (Task A table), `ls-tree | grep -i rpc/ipc/transport/sandbox/finops/observability` at HEAD (0 results for rpc/ipc/transport — itself evidence), `ls-tree | grep -i hook/event/verif/observ/mcp/schema` spot-checks.
- **File paths cited are code/history evidence, not README claims.** Where README/design claims diverge (e.g., MCP tool surface 4 tools documented in DESIGN-OBSERVABILITY but grep shows no `vsdd/src/mcp_serve/` at HEAD — server never materialized), the grep/code evidence is preferred and mismatch is noted.
- **No `cargo build/test`, no `crosslink --version`/`sync`, no file modification** per `to-file/VSDD-archaeology.md` Constraints (verified: `git -C /tmp/vsdd-cli status` clean, clone at `/tmp` not source repo).
- **WHAT-NOT-TESTED (negative space):** All `WHAT-NOT-TESTED` items in §8 apply release-wide. Additionally: per-candidate `git show --stat` outputs not attached per candidate for brevity; `hook-config.json` HEAD vs `b3d6e50` not byte-diffed (stat-level only — small byte differences could exist); convergence-corpus fixture semantics (20 fixtures at `287d1ab`) not individually audited; `.crosslink/knowledge` pages not enumerated.
- **Prior work merged:** Task A timeline (16 milestones M0→M15, 5 candidates, growth inflection 42-day gap, file counts); Task B systemic lens (subprocess/bounded_read/text.rs primitives, RPC absent, MCP stdio only, no OS sandbox); Task C structured lens (31 subsystems, 11 primitives, 11 already-elsewhere rows, 24 backports in 4 groups); Task D raw tables (per-path counts, 8 milestones 3→300 files, HEAD breakdown 116 vsdd-core / 34 .crosslink / 29 .claude etc.); reviewer Cycle 2 verdict (CONDITIONAL — fixes applied: precise dates via `--date=short`, §2 smallest-viable narrative consolidated, §3 candidate matrix with verified hashes/dates, §8 WHY/WHAT/HOW CERTAIN/WHAT-NOT-TESTED block).

---

*End of report — 2026-08-27 Consolidator synthesis, issue #500. Next step is a human decision on the baseline before creating the reduction branch (per `ORIENTATION.md` layer discipline — do not modify ASES implementation until Research→Methodology decision is recorded).*
