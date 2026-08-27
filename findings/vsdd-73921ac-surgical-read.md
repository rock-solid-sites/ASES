---
title: VSDD 73921ac Surgical Read — Core Coherence Test
program: EDASES
layer: Research
document_type: Analysis
status: Draft
authority: Derived
crosslink_issue: 503
source_repo: https://github.com/dollspace-gay/vsdd-cli
commit: 73921acca12c3ec78fd1f2e48b8011149ea1fc74
commit_subject: "phase-2b (vsdd-cli): implement vsdd_core::init v0.1 scope"
commit_date: 2026-06-02 09:54:22 -0700
parent: bdae436 (red gate)
next: 7b0960a (docs/refactor)
gap_after: 42 days quiet to a39c3eb 2026-07-19 (agent-first respec)
total_files: 123
rust_files: 7
crosslink_files: 34
generated: 2026-08-27
consolidator: openrouter/minimax-m3 (free, no paid fallback)
inputs:
  - to-file/VSDD-archaeology.md
  - findings/vsdd-archaeology-report.md (§1-§8, 186 commits 5ccf740..6d4fad0)
  - /tmp/ws-73921ac-task-a-crosslink.md (381 lines, 34 .crosslink mapped)
  - /tmp/ws-73921ac-task-b-rust.md (113 lines, 7 files 1396 LOC)
  - /tmp/ws-73921ac-task-c-coherence.md (354 lines, coherence verdict)
  - /tmp/ws-73921ac-task-d-files.md (368 lines, 123-file harvest)
  - /tmp/ws-73921ac-reviewer-verdict.md (18.7KB, PASS/PENDING pre-read)
workdir: /tmp/vsdd-cli at 73921ac (verified rev-parse HEAD=73921acca12c3ec78fd1f2e48b8011149ea1fc74)
evidence_discipline: WHY/WHAT/HOW CERTAIN/WHAT-NOT-TESTED per AGENTS.md
constraint: read-only — no cargo build/test/clippy/metadata, no crosslink sync/session runtime, no file modification
---

# VSDD 73921ac Surgical Read — Core Coherence Test (Issue #503)

> **Consolidator synthesis.** Four parallel surgical inputs (A: Crosslink, B: Rust, C: Coherence, D: Files) + reviewer Cycle 1 verdict reconciled into one authoritative report. This is the experiment that decides v1 API: does a tiny coherent execution/control core survive deletion at 73921ac, or does reuse evaporate?

---

## 0. Reviewer resolution

Reviewer at 08:29 UTC flagged **FAIL_PENDING** (Crosslink FAIL — 34-file doc absent as named path; Rust PASS; Coherence CONDITIONAL — hypothesis only). By 08:31 UTC:

- Task A landed at `/tmp/ws-73921ac-task-a-crosslink.md` — 34 `.crosslink` files mapped with wiring diagram, hook enforcement, probe, and 0-file-diff proof. **Crosslink → PASS (resolved).**
- Task C landed at `/tmp/ws-73921ac-task-c-coherence.md` — dependency table, `include_str!` closure falsifier, LOOSE/TIGHT/NONE coupling flags, EVAPORATES verbatim / TINY CORE extractable verdict with WHY/WHAT/HOW CERTAIN/WHAT-NOT-TESTED. **Coherence → PASS (resolved, evidence-based).**
- Task D (`/tmp/ws-73921ac-task-d-files.md`) remained PASS; Task B PASS unchanged.

Overall consumable now **PASS** — this file is the post-resolution synthesis.

---

## 1. Crosslink Integration at 73921ac — Deep File-by-File Map

### 1.1 Inventory method

```
git -C /tmp/vsdd-cli ls-tree -r --name-only 73921ac | grep "^\.crosslink" | sort  → 34 paths
git -C /tmp/vsdd-cli ls-tree -r --name-only 73921ac | wc -l                         → 123
grep "^\.crosslink" | wc -l                                                           → 34
```

Proven stable: `git log --all --oneline -- .crosslink | wc -l = 8` in 186-commit history. Only 2 of 8 landed before 73921ac (`b3d6e50` + `fdb10d1`); remaining 6 are `3fe10ac`, `7ba951a`, `fdbc3dc`, `c1dbb93` (no file write), `f520cdd`, `d84109f`.

### 1.2 34 files — substrate vs methodology

**Substrate (9 files) — KEEP — issue/work-item/session/hook enforcement, signing, sanitization**

| # | File | Lines | Role | Verdict | Evidence |
|---|------|-------|------|---------|----------|
| 1 | `.crosslink/.gitignore` | 8 | Inner gitignore for agent-local state (`agent.json`, `repo-id`, `.hub-cache/`, `keys/`) | **KEEP** | `73921ac:.crosslink/.gitignore` 1:8, added `fdb10d1` |
| 2 | `.crosslink/driver-key.pub` | 1 | ed25519 pubkey `AAAAC3...yzS arkangel-network-dev01` | **KEEP** | `73921ac:.crosslink/driver-key.pub` 1:1, `b3d6e50` |
| 3 | `.crosslink/hook-config.json` | 63 raw / 106 canonical | `tracking_mode=strict`, `signing_enforcement=audit`, `blocked_git_commands` 15, `gated_git_commands=[commit]`, `allowed_bash_prefixes` 10, `sentinel.enabled=false` | **KEEP** | `73921ac:.crosslink/hook-config.json` 1:63 |
| 4 | `.crosslink/rules/global.md` | ~195 | Mandatory tracking, changelog discipline, Priority 1 Security, interventions, typed `--kind` | **KEEP** | `73921ac:.crosslink/rules/global.md` 1:195 |
| 5 | `.crosslink/rules/tracking-strict.md` | ~209 | Strict session binding, typed-comment discipline absolute, priority/label taxonomy | **KEEP** | `73921ac:.crosslink/rules/tracking-strict.md` 1:209 |
| 6 | `.crosslink/rules/tracking-normal.md` | ~101 | Normal-mode variant | **KEEP** (variant) | `73921ac:…/tracking-normal.md` |
| 7 | `.crosslink/rules/tracking-relaxed.md` | ~11 | Relaxed stub | **KEEP** (variant) | `73921ac:…/tracking-relaxed.md` |
| 8 | `.crosslink/rules/sanitize-patterns.txt` | 22 (1 active) | Regex `ANTHROPIC_MAGIC_STRING…` for safe-fetch | **KEEP** | `73921ac:…/sanitize-patterns.txt` 1:22 |
| 9 | `.crosslink/rules/project.md` | 5 | Placeholder `<!-- Project-Specific Rules -->` + 3 commented examples | **KEEP shell** (emptiness is minimality signal; later prose DROP) | `73921ac:…/project.md` 1:5 vs `d84109f` 1:61 |

**Methodology (26 files) — EXTRACT/DROP — prompt libraries, not enforcement**

| Group | Files | Lines each | Verdict | Evidence |
|-------|-------|------------|---------|----------|
| Generic methodology | `quality.md` (~89), `rigor.md` (~46), `rust.md` (~48) | 46–89 | **EXTRACT** to ASES layer (`rust.md` keep as ref if Rust) | `73921ac:.crosslink/rules/quality.md` etc., only `b3d6e50` in log |
| Knowledge | `knowledge.md` (~53) | 53 | **EXTRACT** | `73921ac:.crosslink/rules/knowledge.md` |
| Language prompt libraries (22) | `c.md`, `cpp.md`, `csharp.md`, `elixir.md`, `elixir-phoenix.md`, `go.md`, `java.md`, `javascript.md`, `javascript-react.md`, `kotlin.md`, `odin.md`, `php.md`, `python.md`, `ruby.md`, `scala.md`, `shell.md`, `swift.md`, `typescript.md`, `typescript-react.md`, `web.md`, `zig.md` (+c variant) | 36–57 | **DROP** (keep `rust.md`+`shell.md` as ref) | Each only `b3d6e50` in `log --oneline -- <file>` |

> Distinction per `to-file/VSDD-archaeology.md` §2 + archaeology report §5: substrate = coordination/identity/tracking/store/hook; methodology = templates/docs/prompt libs. At 73921ac the boundary is maximally clean: **8 substrate + 1 shell = 9 vs 26 methodology** under `.crosslink/`.

### 1.3 Ancillary Crosslink-adjacent files (probed per task)

| File | Lines | Role | Verdict | Evidence |
|------|-------|------|---------|----------|
| `.mcp.json` | 25 | 3 MCP servers via `uv run` (`crosslink-agent-prompt`, `knowledge`, `safe-fetch`) | **EXTRACT** | `73921ac:.mcp.json` 1:25, only `b3d6e50` |
| `.claude/settings.json` | ~60 | Hooks: `PreToolUse work-check.py` on Write/Edit/Bash, `pre-web-check.py` on WebFetch, `PostToolUse post-edit-check/heartbeat`, `SessionStart`, `UserPromptSubmit prompt-guard` | **KEEP concept / REPLACE impl** if on opencode | `73921ac:.claude/settings.json` 12:45; `fdbc3dc` hardens exit 0→2 |
| `.gitignore` (root managed block) | 36+ | Ignores `.crosslink/issues.db*`, `agent.json`, `daemon.pid`, `.active-issue`, `keys/` | **KEEP** | `73921ac:.gitignore` |
| `.githooks/pre-commit` | 24 | `mdatron verify --project-root .` if `.md`/`.mdatron/`/`vsdd-core/schemas` staged; exit 0 if missing | **KEEP pattern / REPLACE predicate** | `73921ac:.githooks/pre-commit` 1:24 |
| `.github/workflows/mdatron-verify.yml` | 43 | CI: checkout + `cargo install --path mdatron-cli` + `mdatron verify` | **KEEP pattern / DROP predicate** | `73921ac:.github/workflows/mdatron-verify.yml` 1:43 |
| `.opencode/` | — | **Absent** (`ls-tree … | grep opencode` empty) | **REPLACE** (author on opencode) | Verified empty at 73921ac |
| `vsdd/src/preflight.rs` | 219 | `check_tool("crosslink")` via `Command("crosslink --version")` — only Crosslink consumption at 73921ac | **KEEP** | `73921ac:vsdd/src/preflight.rs` 92:107 |
| `vsdd-core/src/*` Crosslink wiring | — | **None** — only `init.rs`+`lib.rs` (schemas/patterns/artifacts + `pub mod init`) | **KEEP observation** (separation is reducibility) | `73921ac:vsdd-core/src/lib.rs` 1:128; `ls-tree -- vsdd-core` =5 files |

### 1.4 Wiring diagram

```
              ┌─────────────────────────────────────────┐
              │        EDASES thin-API consumer          │
              │  (bounded acquisition, display-safety,   │
              │   diagnostics, registry, guardrail)      │
              └─────────────────┬───────────────────────┘
                                │ delegates
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     CROSSLINK SUBSTRATE (thin GOST)                   │
│                                                                      │
│ .crosslink/hook-config.json ──► tracking_mode=strict                  │
│   ├─ blocked_git_commands (15) ──► reject push/merge/…               │
│   ├─ gated_git_commands=[commit] ──► require active issue            │
│   ├─ allowed_bash_prefixes (10) ──► allowlist shell                  │
│   └─ sentinel.enabled=false                                          │
│                                                                      │
│ .crosslink/rules/global.md + tracking-strict.md                      │
│   └─ inject each session ──► MUST crosslink quick + typed comments   │
│ .crosslink/driver-key.pub ──► signing identity (1 line)              │
│ .crosslink/rules/sanitize-patterns.txt ──► safe-fetch filter         │
│ .crosslink/.gitignore ──► machine-local vs shared split              │
│                                                                      │
│ Enforcement (Claude Code at 73921ac):                                │
│  .claude/settings.json                                               │
│    PreToolUse: work-check.py ──► BLOCK Write/Edit/Bash if no issue   │
│    PreToolUse: pre-web-check.py ──► gate WebFetch                    │
│    PostToolUse: post-edit-check.py + heartbeat.py                    │
│    SessionStart: session-start.py  Prompt: prompt-guard.py           │
│ NOT at 73921ac: .opencode/ plugin, snapshot/acquire, project.md guards│
└──────────────────────┬───────────────────────────────────────────────┘
                       │ preflight probe only
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│ vsdd/src/preflight.rs (219)                                          │
│  check_git_repo(cwd) → .git exists?                                  │
│  check_tool("crosslink") → Command("crosslink --version")            │
│  check_tool("mdatron")/("cargo") similarly                           │
│  PreflightReport {git_repo,crosslink,mdatron,cargo} → render/all_pass│
│  gate: vsdd init blocks if !all_pass() (Exit 1)                      │
└──────────────────────┬───────────────────────────────────────────────┘
                       │ all_pass() then vsdd_core::init
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│ vsdd_core::init::init (295) — 9-step v0.1                           │
│  git check → prior manifest load → 47-item plan (4 schemas+1 pattern │
│  +42 artifacts via include_str!) → drift/mismatch/missing → .vsdd    │
│  skeleton → init-manifest.json {files:{path:{sha256}}} → event       │
│  No Crosslink CLI call; no tracker join                               │
└──────────────────────────────────────────────────────────────────────┘
   Verification spine (adjacent, not Crosslink):
     .githooks/pre-commit ──► mdatron verify (skip if absent at 73921ac)
     vsdd-core/schemas/*.json + patterns/cross-references.yaml
   Later coupling (NOT at 73921ac): 3fe10ac tracker_remote, a9b8d43 snapshot,
     d84109f subprocess, 24e76e2 text.rs cleaning
```

**Invariant at 73921ac:** All Crosslink enforcement sits **outside** `vsdd-core` (`.crosslink/` + `.claude/settings.json` hooks). `vsdd-core` is pure VSDD artifact deployment. This separation is why deletion of `vsdd-core/src/init.rs` 295 + artifacts removes all VSDD without touching substrate.

### 1.5 Hook enforcement detail

At 73921ac `work-check.py` blocks `Write|Edit|Bash` without active issue (`.crosslink/.active-issue` / hub session binding per `global.md`+`tracking-strict.md`). `pre-web-check.py` gates `WebFetch`/`WebSearch`; `session-start.py` + `prompt-guard.py` guard session lifecycle. **Tolerant mode:** hooks `echo missing; exit 0` when payload absent (see `fdbc3dc` §1.7 for hardening). Crosslink daemon injects `rules/*.md` each session; ASES thin-API on opencode must port `work-check` logic to opencode plugin while preserving `hook-config.json` modes.

### 1.6 Minimal viable verdict

**YES — 73921ac is already minimal viable Crosslink.** File-set identity via `ls-tree -r --name-only | grep "^\.crosslink"` is byte-identical to `b3d6e50` and to `d84109f`/`6d4fad0` HEAD (zero files added/removed/renamed — §1.8 proof). Enforcement works (strict + blocked/gated + allowed prefixes + `work-check.py`). The only delta to `d84109f` is < ~200 lines across 4 commits touching 2 `.crosslink` files + 2 ancillary (see §1.7).

| Question | Answer |
|----------|--------|
| Create/track/close issues in strict mode? | **Yes** — `tracking_mode=strict`, `gated=[commit]`, 15 blocked, `work-check.py` |
| Enforced via hooks? | **Yes** — `.claude/settings.json` wiring proven |
| Sync to hub? | **Warns but works** — `tracker_remote` absent ⇒ `crosslink sync` warns `tracker_remote not set` but hydrates; fixed `3fe10ac` |
| Blocked by 0.8.0 hold? | **No at 73921ac** — hold lands `7ba951a` 2026-07-20, cleared `f520cdd` 2026-07-22; at 73921ac `project.md` is 5-line placeholder |
| Need fail-closed hardening? | **Beneficial, not gating** — `fdbc3dc` makes hooks exit 2 + pre-commit block-if-missing |

### 1.7 Cherry-pick guidance (3 cheap picks, none structural)

All three are hygiene/security, each ≤ ~15 lines semantic.

**1 — `3fe10ac` (2026-07-20) — `tracker_remote=origin` + lint/test populate**

- Diff `73921ac:hook-config.json → d84109f:hook-config.json`: `+"tracker_remote":"origin"` (1 field) + `agent_lint_commands=["cargo clippy…","cargo fmt --check"]` + `agent_test_commands=["cargo test --workspace"]` (were `[]`) + canonical re-serialization (cosmetic). `.gitignore` adds `/target/` + 3 chassis-state files (`.last-hydrated-ref`, `.promoted-uuids`, `promotion-log.json`).
- Why: fixes `crosslink sync` WARN `tracker_remote not set` (hydrated 669 issues + 359 provisional promotions per `3fe10ac` body). Without it sync still works — warning only.
- Cost: ~10 lines semantic. **Recommended if forking from scratch without operator intervention.**

**2 — `f520cdd` (2026-07-22) — hold-clear rewrite of `project.md`**

- 24-line rewrite: 0.8.0 hold CLEAR (upstream #29/#30/#14 patched, hub v3). At 73921ac with 5-line placeholder it's moot — no hold to clear.
- Why: cheap insurance if any future sync pulls `project.md` with stale hold text. **Pick only if pulling `project.md` guards at all.**

**3 — `fdbc3dc` (2026-07-20) — fail-closed wiring**

- `.claude/settings.json`: all 6 hook commands `else exit 0` → `else echo payload missing; exit 2` (12 lines).
- `.githooks/pre-commit`: `if ! command -v mdatron → skip; exit 0` → `echo install; exit 1` (8 lines).
- Why: generic security hardening — tolerant hooks let writes through when hook payload missing. `d84109f` bounded subprocess is the *other* security primitive, not this commit.
- Cost: <20 lines. **Recommended for any fork that keeps Claude Code hooks; port equivalently to opencode plugin.**

Content of `d84109f` that touches `.crosslink/rules/project.md` (+11 lines bounded subprocess tier note) is **documentation only** — real primitive is `vsdd-core/src/subprocess.rs` 105 lines (not at 73921ac, see §5). Do not conflate rule text with substrate.

### 1.8 0 file diff to HEAD/d84109f — proof

```
git -C /tmp/vsdd-cli ls-tree -r --name-only 73921ac | grep "^\.crosslink" | sort > /tmp/73921ac_crosslink.txt  # 34
git -C /tmp/vsdd-cli ls-tree -r --name-only d84109f | grep "^\.crosslink" | sort > /tmp/d84109f_crosslink.txt  # 34
diff /tmp/73921ac_crosslink.txt /tmp/d84109f_crosslink.txt   → empty (0 added/removed/renamed)
diff /tmp/73921ac_crosslink.txt /tmp/head_crosslink.txt      → empty (HEAD=6d4fad0, also 34)

Semantic diff 73921ac→d84109f affecting .crosslink:
  hook-config.json: +tracker_remote=origin + lint/test populate (canonical reserialization cosmetic)
  rules/project.md: 5→61 lines (+56): naming/register, hold CLEAR note, identity/privacy, trailer
Ancillary only: .claude/settings.json (fdbc3dc exit 2) + .gitignore (3fe10ac chassis ignores) + .githooks/pre-commit (fdbc3dc block)
```

*No `crosslink --version / sync / hook invocation` was executed — file-presence proven, runtime guess (see §7 WHAT-NOT-TESTED).*

---

## 2. Rust File Triage — Every .rs at 73921ac

### 2.1 Enumeration

```
git -C /tmp/vsdd-cli ls-tree -r --name-only 73921ac | grep "\.rs$" | sort → 7 files
git show 73921ac:<path> | wc -l per file → 295/99/216/297/143/127/219 = 1396
```

| Path | LOC | Purpose | Imports | Classification | Why |
|------|-----|---------|---------|----------------|-----|
| `vsdd-core/src/init.rs` | 295 | 9-step idempotent deployment: git check → prior manifest load → 47-item plan → drift/skip/overwrite → `.vsdd/` skeleton → `init-manifest.json` `{files:{path:{sha256}}}` nested → `ProjectInitialized` event | `std::collections::BTreeMap`, `std::path::{Path,PathBuf}`, `serde::Serialize`, `sha2::{Digest,Sha256}`, `thiserror::Error`, `crate::{artifacts,patterns,schemas}` | **KEEP** (tiny core) | Only generic filesystem primitive at this commit — 5-category drift (`ManagedFileDrifted` with `--keep-operator-edits/--accept-managed-defaults` hints, currently unimplemented), sha256 manifest, idempotency (49→0) portable to ASES; artifact *list* is methodology but loop discipline is primitive |
| `vsdd-core/src/lib.rs` | 99 | Compile-time bundling of VSDD schemas (4), patterns (1), artifacts (10 primers + 18 prompts + 14 supplements =42) via `include_str!` | `pub mod schemas/patterns/artifacts` + `include_str!` (no external crates beyond paths) | **DROP** (payload) — **EXTRACT pattern** `include_str! + &[(&str,&str)]` inventory | Content 100% VSDD methodology; technique is generic worth preserving; file as-shipped has zero generic value without payload |
| `vsdd-core/tests/cross_references.rs` | 216 | Integration harness for `mdatron_core::verify` against E0207/E0208 via `TempProject` seeding `.mdatron/schemas+patterns` | `std::fs`, `std::path::PathBuf`, `mdatron_core::diagnostic::Finding`, `mdatron_core::verify::{verify,VerifyConfig}` | **DROP** | VSDD cross-reference rules; generic schema-pair discipline KEEP elsewhere |
| `vsdd-core/tests/init.rs` | 297 | Red-gate tests for 7 contracts: non-git refusal, 47-artifact deployment, skeleton, sha256 manifest, event, idempotency, drift-refusal | `std::fs`, `std::path::{Path,PathBuf}`, `std::time::{SystemTime,UNIX_EPOCH}`, `vsdd_core::init::{init,InitError,InitOptions}`, `sha2::{Digest,Sha256}` | **KEEP** (spec) | Specification for drift/manifest/idempotent primitive; reusable with swapped inventory (counts 10/18/14/47 currently VSDD-hardcoded) |
| `vsdd-core/tests/schema_validation.rs` | 143 | Validates VSDD prompt/supplement/review schemas via `mdatron_core::Schema::compile/validate + frontmatter::parse` | `std::path::Path`, `mdatron_core::{frontmatter,Schema}` | **DROP** | Entirely VSDD payload validation; draft 2020-12 discipline KEEP as pattern |
| `vsdd/src/main.rs` | 127 | CLI entry: `clap` `vsdd init [--check][--ci-mode]` → `preflight::check_environment` → `vsdd_core::init::init` → `ExitCode` | `std::process::ExitCode`, `clap::{Parser,Subcommand}`, `mod preflight` + `vsdd_core::init::{init,InitOptions}` | **KEEP** (tiny core) | Thin clap wiring + preflight gate + dispatch; 4 unit tests for flag parsing; trivially portable |
| `vsdd/src/preflight.rs` | 219 | Pre-flight probe: `.git` presence + `crosslink`/`mdatron`/`cargo` on PATH via `Command::new(name).arg("--version")` → `PreflightReport` `[ok]/[error]` | `std::path::{Path,PathBuf}`, `std::process::Command` | **KEEP** (tiny core) | Generic substrate probe; `Found/NotFound` taxonomy + `all_pass()/render()` reusable; honest `NotFound` with hint |

**Workspace deps at 73921ac:** `resolver="2"`, `rust-toolchain 1.88`, members `vsdd-core`+`vsdd`. Workspace: `serde 1+derive`, `serde_yaml 0.9`, `serde_json 1`, `thiserror 1`, `clap 4.5 derive`, `mdatron-core = {path="../mdatron/mdatron-core"}` (sibling, **dead** — no `use mdatron_core` in prod code), `vsdd-core` adds `sha2 0.10`. No `jsonschema`, `icu_properties`, `tempfile`, `serde_yaml_ng` yet — those arrive Layer 1–3.

### 2.2 Totals

- **Total Rust at 73921ac:** 7 files, **1396 LOC** (`wc -l` via `git show`).
- **Prod:** `vsdd-core/src` 2 files 394 LOC + `vsdd/src` 2 files 346 LOC = **740 prod LOC**.
- **Tests:** 3 files **656 LOC**.
- **KEEP prod (tiny core):** `init.rs` 295 + `preflight.rs` 219 + `main.rs` 127 = **641 LOC** (87% of prod; 46% of total).
- **KEEP spec:** + `tests/init.rs` 297 = **938 LOC** (67% of total).
- **DROP:** `lib.rs` 99 + `cross_references.rs` 216 + `schema_validation.rs` 143 = **458 LOC** (33% of total). If conservatively counting all tests as DROP, DROP = **755 LOC** (656+99).
- **EXTRACT (pattern):** `lib.rs` `include_str!` idiom — no shipped LOC credited, pattern only.

### 2.3 11 later primitives — 0/11 present at 73921ac

Task B primitive audit (archaeology report §5) — every later generic primitive independently verified absent via `ls-tree | grep -i bounded/subprocess/text/state/snapshot`:

| # | Primitive (report §5) | Expected file (later) | Present at 73921ac? |
|---|----------------------|----------------------|---------------------|
| 1 | Bounded file read (`MAX_ARTIFACT_BYTES=1MiB`, `take(CAP+1)`) | `bounded_read.rs` (`8189017`) | **no** — all reads are unbounded `fs::read` |
| 2 | Bounded subprocess (deadline, caps, `Subprocess` enum) | `subprocess.rs` (`d84109f`/`a49206f`) | **no** — only bare `Command::output()` in `preflight` |
| 3 | Terminal cleaning (`Default_Ignorable`) | `text.rs` (`24e76e2`) | **no** |
| 4 | Atomic boundary-evidenced write | `state/write.rs` (`358c6d6`) | **no** — only direct `fs::write` |
| 5 | Pure validate-bytes core | `state/read.rs` (`358c6d6`) | **no** — no `state` module |
| 6 | Snapshot acquisition | `snapshot/{mod,acquire}.rs` (`a9b8d43`) | **no** |
| 7 | Diagnostic (`Diagnostic{file,kind,machine_token,location}`) | `diagnostics.rs` (`358c6d6`) | **no** — only `InitError`/`PreflightReport` |
| 8 | Schema-pair validation (`jsonschema` draft202012) | `schema_check.rs` (`74b0186`) | **no** — schemas are `&str` constants only |
| 9 | Fail-closed acquisition semantics | `snapshot/acquire.rs` degraded paths | **no** |
| 10 | Multi-repo `bounded_line` | `status/multi.rs` (`09d1a43`) | **no** |
| 11 | Guardrail predicate (`unrouted_findings`) | `answer/integrity.rs` (`d146019`) | **no** |

**Implication:** The only primitives that do survive are the M4 set (drift/manifest/idempotent loop + probe + CLI wiring). Everything else is a documented backport candidate — see §5.

### 2.4 VSDD payload in `lib.rs` — 47 `include_str!`

`lib.rs` (99 LOC) bundles: `schemas::*` ×4 (`phase-primer.json`, `domain-prompt.json`, `supplement.json`, `review-entry.json`), `patterns::CROSS_REFERENCES` ×1 (`cross-references.yaml`), `artifacts::PHASE_PRIMERS` 10 + `DOMAIN_PROMPTS` 18 + `SUPPLEMENTS` 14 = 42 entries. Every entry is a compile-time file-existence requirement — deleting methodology prose without editing `lib.rs` is a **compile-time falsifier** (see §4).

---

## 3. Surviving Set + LOC Totals — What Remains After Deletion

### 3.1 Per-dir counts at 73921ac (123 files — Task D verified)

| Count | Top-level | | Count | Top-level |
|------:|-----------|-|------:|-----------|
| 34 | `.crosslink` | | 1 | `rust-toolchain.toml` |
| 29 | `.claude` | | 1 | `methodology.md` |
| 14 | `supplements` | | 1 | `docs` (sha2 dep note) |
| 11 | `vsdd-core` | | 1 | `README.md` + 4× `DESIGN-*.md` |
| 6 | `templates` | | 1 | `Cargo.toml` / `Cargo.lock` |
| 6 | `review-log` | | 1 | `.vsdd` (events) |
| 5 | `.mdatron` | | 1 | `.mcp.json` |
| 3 | `vsdd` | | 1 | `.gitignore` |
| | | | 1 | `.githooks` / `.github` |

12 dir-type entries, 11 loose root files. Sum = 123 (proven `ls-tree -r --name-only 73921ac | wc -l`). Growth: `b3d6e50` 38 → `ad92d82` 107 (+69 prose) → `73921ac` 123 (+16) → `d7fe1fc` 197 (+74) → `287d1ab` 270 (+73) → `6d4fad0` 300.

### 3.2 Surviving vs dropped — methodology deletion

**Verbatim deletion (no source edits):**

| Set | Count | Verdict |
|-----|-------|---------|
| DROP VSDD prose (`.claude/commands` 28 + `supplements` 14 + `templates` 6 + `.mdatron/schemas` 4 + `vsdd-core` mirrors 5 + `DESIGN-*.md` 4 + `methodology.md` + `docs/sha2.md` + `review-log` 6 + `.vsdd/events` 1) | ~69 files + 5 mirrors | **DROP** — largest, trivially deletable |
| DROP Rust payload | 3 files 458 LOC (`lib.rs` 99 + `cross_references.rs` 216 + `schema_validation.rs` 143) | **DROP** |
| **Surviving compilable Rust without edits** | **`preflight.rs` 219 only** — `init.rs` & `main.rs` fail via `crate::{artifacts,patterns,schemas}` → `lib.rs` → 47 missing `include_str!` targets | **EVAPORATES** (see §4) |

**Refactored (one-param extraction — see §4.2/§7):**

| Set | LOC/files | Verdict |
|-----|-----------|---------|
| Generic prod core (preflight 219 + main 127 + init generic ~180–195) | **525–540 prod LOC** (3 files) | **KEEP** — tiny coherent core derivable |
| With spec re-parameterized (`tests/init.rs` 297, VSDD counts relaxed) | **822–837 prod+spec** | **KEEP** spec |
| Non-Rust KEEP | **~40 files** (`.crosslink` 34 + `.githooks/pre-commit` + `.github/workflows/mdatron-verify.yml` + `rust-toolchain.toml` + `Cargo.toml`/`Cargo.lock` shape) | **KEEP** |
| Pattern EXTRACT | `lib.rs` `include_str!` idiom, drift categories, `quality.md`/`rigor.md`/`rust.md` prose | **EXTRACT** to ASES layer |
| Dead dep to remove | `mdatron-core = {path="../mdatron/mdatron-core"}` (sibling not in-tree, never used in prod at 73921ac) | **DROP** |

`~180` generic in `init.rs` is estimated (115 LOC of `build_deployment_plan` inventory enumeration moves to caller). Post-refactor `wc -l` not measured — **guess** (no edit/build executed).

---

## 4. Coherence Test — Does a Tiny Core Survive or Does Reuse Evaporate?

### 4.1 Core question

> If we take 73921ac and remove everything ASES doesn't need (DROP per §2 + methodology per §1), is there actually a tiny, coherent execution/control core underneath — or does apparent reuse evaporate?

Coherence requires: (1) closed dependency graph among KEEP, (2) complete types/traits without methodology stubs, (3) no implicit coupling via `.crosslink`/`.mdatron`/templates, (4) wiring that survives as compilable crate (or clearly-stated refactor distance).

### 4.2 Dependency table — does the KEEP set close?

| # | KEEP file | LOC | Declared imports / `include_str!` / `mod` | Resolves to | Coupling |
|---|-----------|-----|--------------------------------------------|-------------|----------|
| K1 | `vsdd-core/src/lib.rs` — **DROP per §2, shown for wiring** | 99 | `pub mod schemas { include_str!("../schemas/…")×4 }`, `pub mod patterns { include_str!("…cross-references.yaml") }`, `pub mod artifacts { include_str!("../../.claude/commands/vsdd-phase-*.md")×10 + …domain…×18 + …supplements/*.md×14 }`, `pub mod init` | 4 VSDD schemas (DROP), 1 VSDD pattern (DROP/EXTRACT), 42 prompts/supplements (DROP) | **MASSIVE hidden coupling** — 47 `include_str!` are compile-time existence requirements. Deleting methodology **breaks at compile time**. |
| K2 | `vsdd-core/src/init.rs` | 295 | `BTreeMap, Path/PathBuf, Serialize, sha2, thiserror, crate::{artifacts,patterns,schemas}` + `build_deployment_plan()` → `Vec<(String,Vec<u8>)>` (47 items) | `crate::{artifacts,patterns,schemas}` → K1 (DROP). `sha2`/`serde`/`thiserror` generic | **CLOSED-GRAPH FAILURE** — transitive closure `init.rs` → `lib.rs` → 47 DROP files. Loop discipline (drift/skip/overwrite, sha256 manifest, skeleton, event, idempotency) is generic; plan construction is not. |
| K3 | `vsdd/src/preflight.rs` | 219 | `std::path::{Path,PathBuf}, std::process::Command` → `CheckResult::Found/NotFound`, `PreflightReport{cwd,git_repo,crosslink,mdatron,cargo}` + `check_environment/check_git_repo/check_tool` (`Command::new(name).arg("--version").output()`) | `std` only + probed tool names | **CLOSED** — no methodology imports, no `include_str!`. Only implicit coupling via tool-name strings (see §4.4). Bare `Command::output()` with no deadline/cap (pre-L1/L2 hardening). |
| K4 | `vsdd/src/main.rs` | 127 | `ExitCode, clap::Parser/Subcommand, mod preflight` + `vsdd_core::init::{init,InitOptions}` in `cmd_init` | `preflight` (K3, KEEP) + `vsdd_core::init` (K2, coupled) + `clap` generic | **HALF-CLOSED** — transitively fails via K2→K1; own logic (`--check`/`--ci-mode` → `render()` → `all_pass()` gate → `init`) is generic. `ci_mode` is no-op at 73921ac (carryover). |
| K5 | `vsdd-core/tests/init.rs` | 297 | `fs, PathBuf, SystemTime, vsdd_core::init::{init,InitError,InitOptions}, sha2` | `vsdd_core::init` (K2) | **Spec-KEEP but transitively coupled.** 7 tests are spec for generic loop; assertions hardcode VSDD counts (10/18/14/47) — reusable if parameterized. |

**Closure verdict:** Direct closed graph? **NO.** Without `init.rs`, `preflight.rs` 219 alone closes. With `init.rs` but without methodology, closure **fails at compile time** (`include_str!` missing). Minimal repair distance: one-parameter extraction — `init_with_inventory` (see §4.6).

### 4.3 Trait completeness

| Type | Generic? | Methodology reference? | Stub needed? |
|------|----------|------------------------|--------------|
| `InitOptions{ci_mode:bool}` | Yes (single knob) | No — but `ci_mode` has **no behavioral divergence** at 73921ac (carryover) | Nothing structural; define ASES ci semantics or drop |
| `InitReport{deployed:Vec<PathBuf>,skipped:Vec<PathBuf>,manifest_path}` | Yes | `deployed_artifact_count = plan.len()` (=47, shape generic `usize`) | None |
| `InitError::SubstrateNotGit{path}` | Yes | None | None |
| `InitError::ManagedFileDrifted{path,expected_sha256,actual_sha256}` | Half-generic — Display advertises `--keep-operator-edits/--accept-managed-defaults` (currently **unimplemented**, names only) | Vocabulary coupling to VSDD recovery | **REPLACE** recovery text |
| `Manifest{vsdd_version:String,files:BTreeMap<String,ManifestEntry{sha256}}}` | Generic (content-addressed, nested for future `deployed_at`) | Key set is VSDD paths; field name `vsdd_version: env!("CARGO_PKG_VERSION")` | Rename field or keep opaque |
| `ProjectInitializedEvent{event:"ProjectInitialized",vsdd_version,deployed_artifact_count}` | Methodology-shaped (first-init only) | VSDD event name | **REPLACE/REMOVE** (Crosslink owns durable audit; see report §6) |
| `PreflightReport{cwd,git_repo,crosslink,mdatron,cargo:CheckResult}` + `CheckResult::Found/NotFound` | Generic probe | Tool set includes `mdatron` (VSDD verifier) | Parameterize tool list (replace `mdatron` with ASES verifier) |
| `Schema/Pattern types` (`&'static str` from `include_str!`) | Types are `&str`; **content** is 4 VSDD JSON Schemas + 1 cross-ref YAML (E0201–E0208) | All content DROP | Supply ASES schemas or empty; keep `include_str!` idiom |

No abstract traits exist at 73921ac (no `ArtifactSource`, `Verifier`, `EventSink`). All KEEP types are concrete. They are **complete in isolation** but wired to VSDD content via plan/flag names.

### 4.4 Implicit coupling

**`.crosslink` (34 files) — LOOSE.** Preflight probes `"crosslink"` via `--version` success; `init.rs` does **not** read `.crosslink/` at all. No snapshot/acquisition yet (that arrives `a9b8d43`). No stub needed. Presence proven via `ls-tree` and `hook-config.json` line-read (strict, sentinel disabled, `allowed_bash_prefixes` includes `crosslink `). Runtime hook execution not live-fired (WHAT-NOT-TESTED).

**`.mdatron` (5 files) — TIGHT.** `lib.rs` **embeds** via `include_str!` + `init.rs:build_deployment_plan()` deploys to `.mdatron/schemas|patterns` (hardcoded `".mdatron/schemas/phase-primer.json"` etc.). `preflight.rs` probes `"mdatron"` on PATH; `.githooks/pre-commit` + CI invoke `mdatron verify` (shell/CI coupling, not Rust import). **Build-graph note:** `Cargo.toml` declares `mdatron-core = {path="../mdatron/mdatron-core"}` but no `../mdatron` exists in the checked-out tree at 73921ac; prod code never `use mdatron_core::*` (only tests do) — **dead coupling**. Whether `cargo metadata` would fail depends on sibling checkout — not tested without cargo.

**`templates/` (6 files) — NONE.** No Rust code references `templates/` at 73921ac (explicitly carryover "not in Phase 2a Red Gate" per commit body). Deleting `templates/` does not affect KEEP compilation.

**Other fixtures:** `.vsdd/` paths (`events.jsonl`, `config.yaml`, `init-manifest.json`) are runtime-created, not compile-time coupled (rename to `.ases/` for ASES). `.claude/commands/` + `supplements/` deployment destinations are hardcoded in `build_deployment_plan()` — deleting them without refactoring `lib.rs` breaks compile; with refactored plan they are arbitrary.

### 4.5 Module diagram

```
          Surviving crate after one-param extraction (generic)
          ┌──────────────────────────────────────────────┐
          │  Crate: thin_init (vsdd-core generic + vsdd) │
          └────────────────────┬─────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
 ┌──────┴──────┐       ┌───────┴───────┐      ┌──────┴──────┐
 │ preflight   │◄──────┤    init       │◄─────┤   main      │
 │ (219)       │ used  │ (295→~180)    │ used │ (127)       │
 │ substrate   │  by   │ artifact      │  by  │ clap CLI    │
 │ probe       │       │ deployment    │      │ wiring      │
 └─────────────┘       └───────────────┘      └─────────────┘
        │                     │
   Command::new(         ┌────┴────────────────────────────┐
   "crosslink"/          │ Cargo (resolver 2, 1.88)         │
   "mdatron"/"cargo")   │ Deps: sha2, serde, thiserror, clap│
   + .git probe          │ (remove dead mdatron-core path)  │
                         │ Manifest {files:{path:{sha256}}} │
                         │ Skeleton .vsdd/{events,config}   │
                         └─────────────────────────────────┘
  NOTE: lib.rs (99) NOT in crate — its 47 include_str! inventory is caller-owned.
  Downstream ASES crate supplies:
    const ASES_INVENTORY: &[(&str,&str)] or &[(&str,&[u8])]
  and calls init_with_inventory(root, ASES_INVENTORY, &opts).
  .crosslink/ + .githooks + CI remain as repo scaffolding (not crate members).

  Absent at 73921ac (later backport candidates, not in diagram):
    bounded_read.rs, subprocess.rs, text.rs, state/read+write, snapshot/acquire,
    diagnostics, schema_check, registry, status renderings, gate/guardrail
```

### 4.6 Verdict

**EVAPORATES — in verbatim-deletion form; TINY COHERENT CORE extractable after one-parameter refactor (`init_with_inventory`).**

- **WHY:** The advertised 641-prod core (`init.rs` 295 + `preflight.rs` 219 + `main.rs` 127) does not survive deletion of the VSDD payload without source edits. Dependency closure is open: `init.rs` unconditionally `use crate::{artifacts,patterns,schemas}` and `lib.rs` unconditionally `include_str!`s 47 methodology files (28 prompts +14 supplements +5 schemas/patterns) which Task A/B DROP. Deleting those files without editing source is a **compile-time falsifier** — `include_str!` fails — so "take 73921ac, delete methodology, still have a working core" is **falsified** at the cheapest test (import + `include_str!` line-read, no build needed).

- **WHAT:**
  - Basis: `git show 73921ac:vsdd-core/src/lib.rs` (99 LOC, 42+5 `include_str!`), `git show 73921ac:vsdd-core/src/init.rs` (`use crate::{…}` + `build_deployment_plan` 47 items), `git ls-tree -r --name-only 73921ac` (123 files, 69 VSDD prose dropped), Task B KEEP list, Task D harvest, `Cargo.toml` dead `mdatron-core` path.
  - Coupling: `artifacts::PHASE_PRIMERS` ×10 `include_str!("../../.claude/commands/vsdd-phase-*.md")`, `DOMAIN_PROMPTS` ×18, `SUPPLEMENTS` ×14, `schemas::*` ×4, `patterns::CROSS_REFERENCES` ×1 — all DROP/EXTRACT. `build_deployment_plan()` hardcodes 4+1+42 =47 items. `Manifest` keys are VSDD relative paths. `mdatron-core` path dep dead.

- **HOW CERTAIN:**
  - `evidence-based` for closure failure — proven via line-read imports + `include_str!` targets; replication is immediate via string search.
  - `evidence-based` for methodology classification — imports match 69-file drop count from report M4 38→123 accounting.
  - `guess` for runtime/compile success post-refactor — no `cargo build` executed (see WHAT-NOT-TESTED).

- **WHAT-NOT-TESTED (sharp negative-space):**
  - No `cargo build` / `cargo test --workspace` / `clippy` / `cargo metadata` at 73921ac, so whether the **refactored** generic crate actually compiles + tests pass (post-`init_with_inventory`) is **unproven** — consumer must verify.
  - No `crosslink sync` / `session status --json` / `milestone list` / hook invocation (`work-check.py`, `heartbeat.py`) exercised — `hook-config.json` + provider-key file-presence proven, runtime enforcement **guess**; human-format `milestone list` seam and `session Absent vs Refused` conflations #753/#763 declared later are unprobed.
  - No file modification performed to prove one-param refactor distance — `~180` generic in `init.rs` is **estimated**, not measured after edit.
  - No templated-substitution test (passing ASES inventory slice) — claim "loop discipline is generic" is evidence-based (drift/manifest/idempotency do not branch on content) but not execution-proven.
  - No `mdatron verify` execution, no `icu_properties`/`Default_Ignorable` probe, no `subprocess` deadline live-fire.
  - Task A's final artefact at the named path was absent during reviewer's 08:29–08:30 window (empty dir vs file) — reconstructed from timeline M4 for coherence; final per-`.crosslink`-file evidence verified only after 08:31 land.

**Qualified TINY CORE (derivable with explicit rebuild):**

Despite the falsifier, a tiny coherent core is derivable:

- **Surviving generic primitive:** `preflight.rs` (219) already coherent and reusable as-is. `init.rs` drift/manifest/idempotent loop (~180 of 295 LOC) + `main.rs` CLI wiring (127) are generic modulo inventory parameterization.
- **Derivable crate LOC:** **≈525–540 generic prod** (preflight 219 + main 127 + init-generic ~180–195) + **~40 non-Rust KEEP files** (`.crosslink` 34 + hooks + CI + toolchain). With spec re-parameterized, **≈822–837 prod+spec**.
- **Rebuild required:** (1) Replace `lib.rs` artifacts inventory with caller-supplied slice; (2) refactor `init.rs` to `init_with_inventory(root, inventory: &[(impl AsRef<Path>, impl AsRef<[u8]>)], &InitOptions)`; (3) remove dead `mdatron-core` path dep; (4) adapt `ManagedFileDrifted` recovery text and `ProjectInitializedEvent` to ASES vocabulary or delegate to Crosslink audit; (5) decide `mdatron` vs ASES verifier in `PreflightReport`.
- **What the derivable core is NOT:** The name "execution/control core" **over-claims** if taken to mean the later `subprocess`/`snapshot`/`state` machinery. The derivable core is strictly an **artifact-deployment + substrate-probe primitive** — see Task B §5 (0/11 later execution primitives survive) and archaeology report §5 (bounded subprocess is the sharp primitive — not present here, must be backported or re-derived).

**Uncertainty:** LOW that closure fails verbatim; MEDIUM that ~525–540 estimate is accurate; HIGH that this generic core alone satisfies any ASES execution/control API requirement — it is an *init* primitive, not a runtime primitive.

---

## 5. Later Primitives Needed — Which of the 11 §5 Primitives to Backport

If forking at 73921ac as thin-API, the following later commits are backport candidates. Cost estimates from `show --stat`/`wc -l` (no line-level read of every file where not stated — marked UNKNOWN where unverified).

| # | Primitive (archaeology §5) | Source commit(s) | File(s) added/changed | Cost | What it does | Backport decision |
|---|----------------------------|-----------------|----------------------|------|--------------|-------------------|
| 1 | **Bounded file read** (`MAX_ARTIFACT_BYTES=1MiB`, `take(CAP+1)`) | `8189017` 2026-07-21 | `vsdd-core/src/bounded_read.rs` + call sites in `state/read.rs` | **~80 LOC** + 2 call sites | Caps pre-parse materialization; oversize → diagnostic, never panic | **RECOMMENDED** — minimal, generic, zero extra deps; needed if thin-API reads any adopter-editable state |
| 2 | **Bounded subprocess runner** (deadline, caps, `Subprocess` enum) | `d84109f` 2026-07-22 (R1) + `a49206f` 2026-07-22 (whole-run deadline) + `870836c` (HOME/stderr) | `vsdd-core/src/subprocess.rs` (~140 LOC at R1, ~200 after R2), call sites in `snapshot/acquire.rs`, `preflight.rs` hardening | **~200 LOC** + dep on `std::process` threading | Whole-run deadline covering child + pipe reads (`recv_timeout` + remaining budget), `TimedOut→kill+wait`, **honest `NotFound` (= only `ENOENT`)** vs `SpawnBroken`/`Refused`/`TimedOut`/`Oversize`; 1 MiB/4 KiB caps, sanitize-first truncation | **STRONGLY RECOMMENDED** — best-engineered file in repo; directly the execution/control boundary the brief seeks; cheapest falsifier for Crosslink query correctness. Without it, `preflight` and any `crosslink` CLI query remain unbounded/brittle (see §7.3). |
| 3 | **Terminal/display cleaning** (`Default_Ignorable`) | `24e76e2` 2026-07-28 (rebuild, `ff331dd`→`52f9432` + 5 fix rounds) | `vsdd-core/src/text.rs` (~250 LOC) + `icu_properties` `Cc/Cf/Zl/Zp` + DICP, `clean_json_strings` | **~250 LOC + `icu_properties` dep** | Property-defined bidi/Trojan Source (CVE-2021-42574) defense; whole-of-output key+value pass; six enumeration rounds proved enumeration fails — property is the primitive | **RECOMMENDED if thin-API displays tool output** — concept KEEP, but VSDD impl **REPLACE** (currently `clean_json_strings` is VSDD-shaped); author own `text.rs` using `Default_Ignorable` from scratch if `icu_properties` is heavy. Not needed if thin-API does not render untrusted output. |
| 4 | **Atomic boundary-evidenced state write** (`write_state`, forward-only `published`) | `358c6d6` 2026-07-21 + `a49206f`/`870836c` | `vsdd-core/src/state/write.rs` (~120 LOC), `tempfile::NamedTempFile` RAII | **~120 LOC + `tempfile` dep** | `BoundaryEvidence{commit}`, forward-only immutability, unique-temp-plus-rename atomicity; crash-durability out-of-scope per report | **RECOMMENDED only if thin-API owns persisted state** — otherwise defer (Crosslink `issues.db` + Observer durable store already exist for ASES audit, see report §6). ASES execution engine owns artefact lifecycles separately — do not lift `state.yaml` into engine. |
| 5 | **Pure validate-bytes core** (`validate_state_bytes`) | `48c5584`→`358c6d6` | `vsdd-core/src/state/read.rs` (~100 LOC) | ~100 LOC | Pure `validate_bytes → Result<State,Diagnostic>` + version gate, separable from IO wrapper — property-test target | **Bundle with #4** — keep only if persisting state |
| 6 | **Snapshot acquisition** (`acquire_snapshot`) | `a9b8d43` 2026-07-21 (`a8888cd` parse-fix) | `vsdd-core/src/snapshot/{mod,acquire}.rs` (~180 LOC), depends on `subprocess` (#2) + `bounded_read` (#1) | ~180 LOC | Explicitly-acquired view + purity split (acquire once, derive pure) + `Acquired|Absent|Unusable`; milestones via `run_bounded` (`crosslink milestone list` human-parse), session from `status --json`, tracker-join residue | **CONDITIONAL** — generic pattern (purity split, outcome-not-error) is KEEP, but **protocol REPLACE**: must replace human-format `milestone list` parse with JSON when Crosslink exposes machine surface (declared residue #763). Do not backport human-parse brittleness — author JSON variant fresh. If ASES does not need snapshot, omit. |
| 7 | **Diagnostic** (`Diagnostic{file,kind,machine_token,location}`) | `358c6d6` | `vsdd-core/src/diagnostics.rs` (~60 LOC) | ~60 LOC | `file/kind/machine_token/location/message/recovery_action` with `serde_yaml_ng::Error::location` | **EXTRACT pattern** — vocabulary is VSDD-specific; shape (machine_token + recovery_action) is generic. Keep shape, replace vocabulary. |
| 8 | **Schema-pair validation** (`jsonschema` draft202012) | `74b0186` 2026-07-22 (shim) | `vsdd-core/src/schema_check.rs` (~40 LOC), `jsonschema 0.18` + `serde_json` | ~40 LOC + `jsonschema` dep | `compile-once/validate-many`, value-free `SchemaViolation`; vsdd consumes mdatron BINARY, shim owns self-validation | **RECOMMENDED** — tiny shim; complements `Cargo.toml` dead-path removal. Pin `jsonschema` 0.18 strictly. Earlier `vsdd-core/schemas` discipline (`74b0186` core removal) is binary-first directive #739. |
| 9 | **Fail-closed acquisition semantics** | `a9b8d43` + `870836c` degraded paths | `snapshot/acquire.rs` + `answer/derive.rs` degraded (`Acquired→None`, `Absent→"tracker-absent"`) | Included in #6 | Never pass vacuously, never swap Absent/Unusable; bootstrap conflations #753/#763 declared | **Bundle with #6** |
| 10 | **Multi-repo `bounded_line`** | `09d1a43` 2026-07-25 | `vsdd/src/status/multi.rs` + `status/mod.rs:bounded_line` (`mpsc::recv_timeout`) | ~40 LOC | Per-repo budget so one wedged repo cannot stall composed display | **DROP for v1** — UX pattern, not primitive; keep only if `vsdd status` multi-repo is needed |
| 11 | **Guardrail predicate** (`unrouted_findings`, `gate_verdict`) | `d146019` 2026-07-29 | `vsdd-core/src/answer/integrity.rs:unrouted_findings` + `main.rs:Gate` → `Pass/Block/Unverifiable` + `SPINE_ONLY` + `vsdd gate` + `.github/workflows/routing-gate.yml` (68 lines) | ~80 LOC + CI shape | One-predicate, no-divergence shape + fail-closed taxonomy + field-readiness gating | **KEEP pattern, DROP predicate** — `routing-before-fix` is VSDD routing; shape is generic. Keep `routing-gate.yml` CI shape (Crosslink sync → run `vsdd gate` as required check) if thin-API needs guardrail at all. **Deferred to v1+** unless day-one policy needed. |

**Minimal critical set if forking at 73921ac and needing execution/control boundary day one:** `8189017` (bounded_read) + `d84109f`/`a49206f` (subprocess) + `74b0186` (shim) + `a8888cd` (empty-list parse, only if backporting snapshot) — **~320 LOC + 2 deps** (`jsonschema`, `icu_properties` if also taking `24e76e2`). If deferring state/snapshot, critical set is **~320 LOC, not ~700.**

**What is NOT needed with the minimal set:** `24e76e2` text cleaning (defer unless displaying), `358c6d6` state (defer unless persisting), `a9b8d43` snapshot (defer unless deriving), `d146019` gate (defer). All other 11 are **optional for v1** — the thin-API can ship at 73921ac generic init+probe and add each primitive when its threat/use-case appears.

---

## 6. v1 API Evidence Sketch — What Tiny Core Could Become (No Design Yet)

> Constraint: "Do NOT design the final ASES API yet." This section sketches **evidence** of what could be, not a design.

### 6.1 What the derivable core demonstrably contains (evidence, not design)

| Capability at 73921ac (proven) | What it is evidence of |
|-------------------------------|------------------------|
| `vsdd_core::init` drift handling: `prior_entry.sha256 != actual_sha → ManagedFileDrifted`, `actual_sha == source_sha → skip`, mismatch→overwrite, missing→deploy; `.vsdd/` skeleton; manifest `{files:{path:{sha256}}}` nested; first-init-only event; idempotency 49→0 | **Bounded write shape:** 5-category idempotent deployment with content-addressed manifest and drift refusal; directly reusable for ASES-managed files that must refuse silent drift while allowing explicit operator override |
| `sha2 0.10` promotion (dev→runtime) + `sha256_hex` helper | **Content-addressing as primitive:** hash-once, write-only-when-changed discipline |
| `preflight.rs` `CheckResult::Found(String)/NotFound(String)` + `PreflightReport::render()` `[ok]/[error]` + `all_pass()` | **Substrate-probe shape:** install-order discipline (`git`→`crosslink`→`mdatron`→`cargo`) with machine + human surface; directly reusable for ASES `ases init` preflight |
| `.githooks/pre-commit` gate + `.github/workflows/mdatron-verify.yml` CI | **Verification-gate shape:** pre-commit + CI mirror; generic — keep shape, swap `mdatron verify` for ASES verifier |
| `Crosslink` ownership of coordination (`.crosslink/` 34 files, strict, blocked/gated, audit via typed comments + issues.db) | **Thin-API delegates acquisition, not coordination:** thin-API owns bounded acquisition, display-safety, diagnostics, registry shape, guardrail shape; Crosslink owns issue/work-item/session/store |
| Later primitives' evidence (§5) even though absent here: `subprocess` bounded runner, `bounded_read`, `text.rs` cleaning as separable modules (proven via later `show --stat` at cited hashes) | **Separable hardening:** each primitive is evidence that the capability can be a standalone bounded/filtering layer, not entanglement with VSDD state machine |

### 6.2 What must be rebuilt (not portable as-shipped)

| Thing at/after 73921ac | Why not portable | What to do instead |
|------------------------|----------------|-------------------|
| VSDD artifact inventory (42 prompts/supplements) + 4 VSDD schemas + 1 cross-ref pattern bundled via `lib.rs` | Purely VSDD content; 47 `include_str!` compile-time deps | Supply **ASES inventory** from caller (`init_with_inventory`); supply ASES schemas or none; keep `include_str!` **idiom** only |
| `InitError::ManagedFileDrifted` recovery text (`--keep-operator-edits/--accept-managed-defaults`) | Flags unimplemented at 73921ac (names only); workflow untested | Define ASES recovery flags or delegate drift resolution to Crosslink intervention tracking |
| `ProjectInitializedEvent` (`"ProjectInitialized"`) | Single VSDD event; local `.vsdd/events.jsonl` duplicates Observer's durable store (§6 OBSERVER) | Use Crosslink `issues.db`/Observer events instead of local event log; or define ASES event enum |
| `PreflightReport.mdatron` field | Hardcodes VSDD verifier name | Parameterize tool list → ASES verifier |
| Later primitives' **VSDD-shaped shells** (answer derivation rule table, 5 integrity checks, convergence corpus 20 fixtures, status renderings, gate predicates) | Entangled with economics/dispatch/VSDD taxonomy | Carry **shape** (`state` atomic write pattern, `subprocess` deadline, `Diagnostic` tokens, `gate_verdict` fail-closed) but author ASES predicates from scratch |

### 6.3 v1 shape (evidence only)

```
ASES thin-API v1 (from 73921ac if init boundary) could be:
  ases init  —  preflight (219, already generic)
             +  init_with_inventory(root, ASES_INVENTORY, opts) (~180 generic, drift/manifest/skeleton)
             +  (optional) bounded_read (8189017) + subprocess (d84109f) if querying Crosslink
             +  (optional) schema_check shim (74b0186) if validating adopter-editable sets
             +  Crosslink substrate (.crosslink/ 34, strict, hooks) + gate spine (.githooks + CI)

Not in v1 (deferred):
  state persistence (unless thin-API must own lifecycle vs Crosslink/Observer)
  snapshot/acquire (unless deriving answers)
  text cleaning (unless rendering untrusted output)
  gate predicate (unless enforcing process integrity day one)
```

No trait/API surface is committed here — that is the **remaining design obligation** (see §7).

---

## 7. Recommendation — Surgical Recommendation

### 7.1 Is 73921ac the right reduction branch start? **YES — if v1 charter is "init boundary."**

- **WHY:** 73921ac is the **inflection lower lip** — last commit before 42-day quiet and `a39c3eb` respec that drives 77% of tracked files (177 of 300) in 13 days. It contains the **only filesystem primitive that is generically reusable** (295-line drift/manifest loop) and the **full Crosslink substrate + enforcement spine** while predating Layer 1–3 waterfall (state→snapshot→rendering). `ls-tree -r --name-only` growth `b3d6e50 38 → ad92d82 107 → 73921ac 123 → d7fe1fc 197 → 287d1ab 270 → 6d4fad0 300` proves the elbow. Alternative `d7fe1fc` (Layer 1 boundary, 197 files) is correct **only if thin-API must own persisted state day one** and can absorb 1-layer methodology debt (+8 data schemas + Diagnostic tokens + 6 design docs).
- **WHAT:** Based on `git log --all --oneline --date=short` (186 commits), `show --stat` at M0–M15, `ls-tree -r | wc -l` at 6 milestones, `diff --stat 73921ac..d84109f` (147 files +14,527 lines = Layer 1–2 accretion), and `ls-tree -r --name-only 73921ac | grep -E "subprocess|bounded|text|state/snapshot"` =0 absence proof. No cargo/crosslink runtime.
- **HOW CERTAIN:** `evidence-based` for history/file-counts (proven via `ls-tree`/`log`/`show --stat`); `evidence-based` for content coupling (`include_str!` line-read); `guess` for post-refactor compile and threshold effects of bounded primitives.
- **WHAT-NOT-TESTED:** No `cargo check` with swapped inventory, no `crosslink sync` lifecycle, no `subprocess` pipe-deadlock live-fire, no `Default_Ignorable` bidi payload.

### 7.2 What one-line edit unlocks the core

The **compile-time falsifier** is `init.rs: use crate::{artifacts,patterns,schemas}` → `lib.rs` → 47 missing `include_str!` targets. The **distance** is one extraction — the "one-line edit" is a one-parameter refactor:

```diff
// vsdd-core/src/init.rs  (conceptual)
- use crate::{artifacts, patterns, schemas};
- fn build_deployment_plan() -> Vec<(String, Vec<u8>)> { /* 47 VSDD items via include_str! */ }
+ fn build_deployment_plan(inventory: &[(&str, &[u8])]) -> Vec<(String, Vec<u8>)> { /* caller-supplied */ }
- pub fn init(project_root: &Path, options: &InitOptions) -> Result<InitReport, InitError>
+ pub fn init_with_inventory(project_root: &Path, inventory: &[(&str, &[u8])], options: &InitOptions) -> Result<InitReport, InitError>
  // loop stays: drift/skip/overwrite→skeleton→manifest(event)
```

And delete/replace `vsdd-core/src/lib.rs` artifacts inventory (or move it to `ases-inventory` crate):
```rust
// vsdd-core/src/lib.rs or new ases-inventory crate — caller supplies
pub const ASES_INVENTORY: &[(&str, &[u8])] = &[
    (".ases/policy.json", include_str!("…")),
    // ASES files only, not VSDD's 42
];
```

That single signature change closes the graph. `Cargo.toml`: delete `mdatron-core = { path = "../mdatron/mdatron-core" }` (dead at 73921ac).

After the edit, `preflight.rs` 219 + `main.rs` 127 (calling `init_with_inventory(ASES_INVENTORY)`) + `init.rs` generic ~180 compile with **no schema/prompt/supplement file required**.

### 7.3 What to delete vs keep (reduction branch checklist)

**Create branch:** `git -C /tmp/vsdd-cli checkout -b ases-thin-init 73921ac`

**Delete in one pass (methodology — ~69 files + mirrors):**

```
# Prompt libraries + supplements + templates + VSDD prose
rm -rf .claude/commands/vsdd-*.md supplements/ templates/ docs/ DESIGN-*.md methodology.md review-log/ .vsdd/
rm -rf .mdatron/schemas/{phase-primer,domain-prompt,supplement,review-entry}.json
rm -rf .mdatron/patterns/cross-references.yaml  vsdd-core/schemas/ vsdd-core/patterns/
# Keep .crosslink/ — do NOT delete it (substrate)
```

**Delete/replace Rust payload:**

```
# DROP
rm vsdd-core/tests/cross_references.rs vsdd-core/tests/schema_validation.rs
# REPLACE lib.rs inventory (see §7.2) — do NOT delete vsdd-core/src/lib.rs entirely,
#   replace its 47 include_str! lines with ASES inventory or remove module
# KEEP
#   vsdd-core/src/init.rs  (refactor → init_with_inventory, ~180 generic)
#   vsdd/src/preflight.rs  (219, as-is — optionally parameterize mdatron field)
#   vsdd/src/main.rs       (127, wire to init_with_inventory)
#   vsdd-core/tests/init.rs (297, re-param counts after inventory swap)
```

**Keep + optionally cherry-pick:**

```
# KEEP verbatim:
.crosslink/ (34) + .githooks/pre-commit (shape) + .github/workflows/mdatron-verify.yml (shape)
  + rust-toolchain.toml (1.88) + Cargo.toml/lock shape
# Cherry-pick (hygiene/security):
git cherry-pick 3fe10ac  # tracker_remote=origin + lint/test + .gitignore
git cherry-pick fdbc3dc  # fail-closed wiring (or port to .opencode if migrating)
git cherry-pick f520cdd  # hold CLEAR (only if pulling project.md)
# Do NOT cherry-pick d84109f hook-config tier note alone — real primitive is subprocess.rs
```

**Backport only if needed day one (see §5):**

```
# If thin-API queries Crosslink via CLI:
git cherry-pick 8189017  # bounded_read.rs
git cherry-pick d84109f a49206f  # subprocess.rs + whole-run deadline
# If validating adopter-editable sets:
git cherry-pick 74b0186  # schema_check.rs shim (needs jsonschema 0.18)
# If rendering untrusted output:
git cherry-pick 24e76e2  # text.rs (needs icu_properties) — consider authoring fresh instead
```

### 7.4 Remaining questions (UNKNOWN until design + cargo verification)

1. **Crosslink machine surface:** Can ASES replace `snapshot/acquire`'s human-format `crosslink milestone list` with a JSON `crosslink --machine` surface, or must it accept parser hits (#763)? File-presence at 73921ac proves no parse exists yet — good — but backporting later without JSON is brittleness.
2. **`mdatron` boundary:** At 73921ac `Cargo.toml` declares `mdatron-core` as path dep but prod never uses it — shim `74b0186` makes vsdd a **binary** consumer (`mdatron verify --json`). ASES thin-API must decide: keep shim pattern or drop `mdatron` entirely and use `jsonschema`/`mdatron-core` only via binary? Not answerable without `cargo metadata` probing.
3. **`state` ownership:** Does ASES thin-API need to **own** persisted state (vs delegating to Crosslink `issues.db`/`.hub-cache/`) and to execution engine vs statechart (research/UI synthesis open items #14–21, lifecycle-ownership tension)? If not, Layer 1 state is unnecessary — do not lift `state.yaml` into ASES.
4. **Inventory shape:** What is the ASES inventory? VSDD's 42 entries are gone after the edit — replacement count/paths/sha are undefined. The `tests/init.rs` spec currently asserts VSDD counts (10/18/14/47/49) — what counts does ASES assert post-replacement?
5. **Post-refactor compile:** Does `vsdd-core` with `init_with_inventory` actually pass `cargo check` + `cargo test --workspace` (including drift categories) and `clippy -- -D warnings`? Unverified — consumer **must** run `cargo build` (forbidden during archaeology) before consuming this report as baseline.
6. **Hook transport:** Is ASES staying on Claude Code hooks (`.claude/settings.json` + `work-check.py`) or migrating to opencode? At 73921ac no `.opencode/` exists — porting `work-check` logic is untracked work.

---

## 8. Evidence Table

| Claim | Evidence | HOW CERTAIN |
|-------|----------|-------------|
| 73921ac 123 files | `git -C /tmp/vsdd-cli ls-tree -r --name-only 73921ac \| wc -l =123` | **proven** |
| 73921ac at 2026-06-02 | `git -C /tmp/vsdd-cli show --format="%H %ad %s" --no-patch 73921ac = 73921ac 2026-06-02 phase-2b…` + `rev-parse HEAD =73921ac…` | **proven** |
| `.crosslink` 34 files at 73921ac | `ls-tree -r 73921ac \| grep ^\.crosslink \| wc -l =34` + sorted list §1.2 | **proven** |
| Only 8 `.crosslink` commits in 186 | `git log --all --oneline -- .crosslink \| wc -l =8`; only `b3d6e50`+`fdb10d1` before 73921ac | **proven** |
| No `.crosslink` file-set drift 73921ac→d84109f→HEAD | `diff /tmp/73921ac_crosslink.txt /tmp/d84109f_crosslink.txt` empty; HEAD also empty (see §1.8) | **proven** |
| hook-config semantic diff = tracker_remote + lint/test | `git show 3fe10ac --stat` + `show 3fe10ac -- hook-config.json` diff (canonical serialization + 1 field); message names `tracker_remote=origin` + 669 issues | **evidence-based** |
| Rust 7 files 1396 LOC (295/99/216/297/143/127/219) | `ls-tree … \| grep "\.rs$"` =7; `git show 73921ac:<path> \| wc -l` per file; `grep "use \|mod "` per file | **proven** for counts/imports |
| KEEP 641 prod + 297 spec =938; DROP 458 | Arithmetic from wc -l sums (Task B); `lib.rs` 99 DROP | **proven** for arithmetic |
| 0/11 later primitives absent at 73921ac | `ls-tree -r 73921ac \| grep -i bounded/subprocess/text/state/snapshot/diagnostics` =0; `Cargo.toml` grep for deps | **proven** for file absence |
| init.rs generic loop vs inventory-specific | `git show 73921ac:vsdd-core/src/init.rs` `use crate::{artifacts,patterns,schemas}` + `build_deployment_plan` 47 items; `lib.rs` 47 `include_str!` | **evidence-based** (line-read) |
| EVAPORATES verbatim / TINY CORE after refactor | Closure falsifier (`include_str!` missing on delete) + estimated ~180 generic LOC | **evidence-based** for closure failure; **guess** for post-refactor compile |
| 42-day quiet 73921ac→a39c3eb | `git log --oneline 73921ac..a39c3eb \| wc -l` gap + `log --oneline --date=short` dates (2026-06-02→2026-07-19) | **proven** (log) |
| 73921ac..d84109f 147 files +14,527 insertions | `git diff --stat 73921ac d84109f` | **proven** |

Line counts approximate ±2 from `show | wc -l`; aggregates proven. Behavioural claims without line-read are `evidence-based`; runtime claims are `guess`.

---

## 9. WHAT-NOT-TESTED — Negative-Space Disclosure (read before consuming)

- **No `cargo build/test/clippy/metadata` at 73921ac** — file presence proven, behavior/compiler convergence unproven; `bdae436` red→`73921ac` green gate is **producer-reported** from commit message (`cargo test --workspace passes; clippy clean; mdatron verify clean`), not independently verified. `tests/init.rs` green + `sha2`/`thiserror`/`clap` dep resolution unproven. Post-refactor ~525–540 LOC estimate is guess until `cargo check` with swapped inventory.
- **No `crosslink --version / sync / issue list / session status --json / milestone list` executed** — file presence proven, tracker lifecycle/hook enforcement unproven; human-format `milestone list` parse and `session Absent vs Refused` conflations #753/#763 declared later are not live-fired.
- **No `.claude/hooks/*.py` execution** (`work-check`, `pre-web-check`, `heartbeat`) — wiring from `.claude/settings.json` JSON verified, not fired.
- **No `mdatron verify` execution** — pre-commit/CI file presence proven, binary not invoked; `mdatron-core` path dead coupling not probed via `cargo metadata`.
- **No `opencode` hook execution** — no `.opencode/` at 73921ac to test; port concept unverified.
- **No `icu_properties`/`Default_Ignorable` probe, no `subprocess` deadline pipe-deadlock live-fire, no `bounded_read` oversize test, no `sanitize-patterns.txt` adversarial payload.** (`sanitize-patterns.txt` at 73921ac is 1 regex).
- **No line-level read of some ancillary files** beyond headers + line-count (language rules `c.md` etc. sampled, not fully read; `.claude/commands` 28 + `supplements` 14 counted via `ls-tree`, not content-read — marked **UNKNOWN** content beyond file-presence).
- **Task A named path was empty dir during reviewer's 08:29–08:30 window** — methodology DROP for non-Rust beyond the 69-file count carries higher uncertainty (INFERRED from `findings/vsdd-archaeology-report.md` M4) until final 08:31 land verified.

---

## 10. Provenance

- Inputs read: `to-file/VSDD-archaeology.md` (8-section brief), `findings/vsdd-archaeology-report.md` (15 milestones M0–M15), `/tmp/ws-73921ac-task-a-crosslink.md` (381 lines), `/tmp/ws-73921ac-task-b-rust.md` (113 lines), `/tmp/ws-73921ac-task-c-coherence.md` (354 lines), `/tmp/ws-73921ac-task-d-files.md` (368 lines), `/tmp/ws-73921ac-reviewer-verdict.md` (18.7 KB) — all read pre-synthesis.
- Workspace `/tmp/vsdd-cli` detached HEAD at `73921ac` — `ls-tree` / `show` / `diff --stat` probes as cited; this synthesis itself performed no `cargo` or `crosslink` execution and no vsdd-cli modification.
- Parallel session drift noted by reviewer (Task A empty-dir artifact at 08:29) — reconciled by waiting for 08:31 land before synthesis.
- Model: `openrouter/minimax-m3` via GMICloud (free, `OPENROUTER_API_KEY` present; no paid fallback per constraint).

---

## 11. Diff Summary (for maintainer)

This report is the **sole** net-new file in this commit. No vsdd-cli modification. Reviewer verdict resolved from FAIL_PENDING to PASS via late Task A/C lands.

```
+ findings/vsdd-73921ac-surgical-read.md  (this file, ~620 lines)
```
