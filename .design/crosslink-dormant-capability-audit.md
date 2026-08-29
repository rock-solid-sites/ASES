# Crosslink Dormant Capability Audit — Track B: Native File & Tool Restriction

* Program: ASES / EDASES Research — `feature/dormant-capability-audit` (#505)
* Date: 2026-08-28
* Deployed Crosslink: `0.9.0-beta.1+37789b51-dirty` (`crosslink --version`, see §1)
* Source tree: `/home/claude-code/projects/crosslink` @ `v0.9.0-beta.1-60-g37789b51` (HEAD)
* Authority: `docs/research/agent-tooling-and-permission-enforcement-reviewed.md` §2.4/§2.5, `docs/research/registry/Hookability-Matrix.md`, `.crosslink/hook-config.json` vs `crosslink/resources/crosslink/hook-config.json`
* Deliverable contract: per-feature table `deployed behaviour + source line + V2 interaction + activate / fix-then-activate / leave-dormant`, plus explicit answer for **restricted-kickoff-to-allowed-files** natively, with **WHY / WHAT / HOW CERTAIN / WHAT-NOT-TESTED** per claim (AGENTS.md).

---

## 0. Execution summary — what this audit is and is not

**Claim 0 — Scoping.**

* **WHY:** Prior Track B runs (pp3g-A7nr 2026-08-27 09:53 plan, pp3g-1c2j resume) died frozen with no deliverable (observer evidence bundles preserved). This run re-verifies every dormant feature the issue enumerates and answers one product question natively: *which subset of “restrict a kickoff agent to an explicit allowed-files set” can be achieved without new Engine code?*
* **WHAT:** This document is the answer. §1 establishes deployed-vs-source fidelity. §2 is the per-feature decision table. §3 expands each row with WHY/WHAT/HOW-CERTAIN/WHAT-NOT-TESTED. §4 answers the restricted-kickoff subset question. §5 states the recommended activation sequence.
* **HOW CERTAIN:** Proven — the table is derived from `crosslink --help`, `crosslink config list`, `crosslink kickoff run --help`, `crosslink workflow diff/trail`, live `hook-config.json`, and line-level source reads cited per row. Re-verified 2026-08-28.
* **WHAT-NOT-TESTED:** No live `crosslink kickoff run` was executed (host is production ASES checkout; spawning agents would create branches/worktrees and side-effect hub state). No container runtime (`docker`/`podman`) was probed live — `launch.rs` container path is source-verified only. No stale-lock stealing, signing-enforced push, or sentinel daemon start was exercised — classified by reading `lock_check.rs`/`signing.rs`/sentinel code rather than by runtime mutation.

---

## 1. Deployed vs source fidelity

Moved here so every per-feature claim below inherits a grounded baseline rather than repeating it.

### 1.1 Deployed binary

```
$ crosslink --version
crosslink 0.9.0-beta.1+37789b51-dirty

$ crosslink --help           # 27 subcommands incl. kickoff, workflow, integrity, knowledge, locks
$ crosslink config list      # 30+ keys, see §1.3
$ crosslink kickoff run --help  # flags: --container, --verify, --model, --timeout, --branch, --base,
                                #        --doc, --skip-permissions, --permission-mode, --agent-type
$ crosslink workflow --help  # subcommands: diff, trail
$ crosslink integrity --help # subcommands: counters, hydration, locks, schema, layout, sign-backfill
$ crosslink knowledge --help # subcommands: add, show, list, edit, remove, sync, import, search
$ crosslink locks --help     # subcommands: list, check, claim, release, steal
```

Evidence preserved in `crosslink --help` / `config list` transcripts captured during this session; `crosslink workflow diff` output reproduced in §3.11.

### 1.2 Source HEAD

```
/home/claude-code/projects/crosslink @ v0.9.0-beta.1-60-g37789b51
  + dirty: one uncommitted diff stat matching deployed +37789b51-dirty marker
  Files inspected:
    crosslink/src/commands/kickoff/launch.rs    (build_agent_command, sandbox, backstop, container)
    crosslink/src/commands/kickoff/prompt.rs    (build_allowed_tools, build_prompt)
    crosslink/src/commands/kickoff/helpers.rs   (read_kickoff_allowed_tools, detect_conventions, has_manifest)
    crosslink/src/commands/kickoff/run.rs       (extend allowed_tools, kickoff launch flow)
    crosslink/src/commands/kickoff/plan.rs      (build_allowed_tools_plan)
    crosslink/src/commands/kickoff/types.rs     (KickoffOpts: permission_mode, agent_type, base, container)
    crosslink/src/commands/config_registry.rs   (REGISTRY — canonical key definitions)
    crosslink/src/utils.rs                      (read_agent_type, read_agent_binary)
    crosslink/src/lock_check.rs                 (read_auto_steal_config, auto_steal_if_configured)
    crosslink/src/signing.rs                    (host_crosslink_dir, generate_agent_key)
    crosslink/src/commands/workflow.rs          (workflow diff/trail)
    crosslink/resources/crosslink/hook-config.json  (embedded defaults)
    .crosslink/hook-config.json                 (ASES deployed config — this repo)
```

The single delta between the deployed binary version string (`+37789b51-dirty`) and source `git describe` (`-60-g37789b51`) is the dirty working tree marker — not a code delta. Source citations below use line-stable anchors (function names + nearby comments) rather than bare line numbers to survive churn; numeric lines are given as of HEAD for checkability and are marked “as of HEAD”.

### 1.3 ASES deployed config (effective)

`crosslink config list` (abridged, full JSON in `.crosslink/hook-config.json`):

```
tracking_mode                 strict                 [hot]   Workflow
comment_discipline            encouraged             [hot]   Workflow
kickoff_verification          local                  [hot]   Agents
kickoff.allowed_tools         (none)                 [hot]   Agents  ← dormant empty
signing_enforcement           audit                  Security
auto_steal_stale_locks        false                  [hot]   Security
sentinel.enabled              (none)→false           [hot]   Sentinel ← dormant
sentinel.default_agent.model  opencode/ling-…-free   [hot]
blocked_gated/allowed_bash    see file — 15 blocked + 1 gated + 49 allowed prefixes
agent_overrides.tracking_mode relaxed                (builder context only)
agent_overrides.by_type       orchestrator/builder/reviewer/auditor  ← S2-only enforcement
```

Keys **absent** from the deployed file (hence dormant) even though source reads them:

`kickoff.timeout_backstop_secs`, `sandbox.command`, `watchdog.*`, `agent.binary`, `template_required_fields`, `sentinel.interval_minutes`/`max_concurrent_agents` (rely on embedded defaults), `kickoff.allowed_tools` array.

*WHY this matters:* Absence is not “unused” — every absent key is a code path that compiles, is tested, and is documented (helpers.rs, launch.rs, config_registry.rs) but is never exercised in ASES because the JSON omits it. The audit treats absence-as-dormancy, not absence-as-nonexistence.

### 1.4 V2 (hub-layout) interaction — one paragraph for all rows

Crosslink’s durable store is the `crosslink/hub` branch (issues as JSON, comments with `--kind`, locks as ref-advertised state) plus `crosslink/knowledge` for pages. `hook-config.json` itself is **not** hub-synced — it is a repo-local file whose content is observed via `crosslink workflow diff` but not versioned through the hub. Consequently: features gated on `hook-config.json` (allowed_tools, tracking_mode, comment_discipline, signing_enforcement, auto_steal, sentinel) are **V2-adjacent** (they shape how agents interact with the hub but are not themselves hub state), while features that touch the hub directly (workflow trail, integrity hydration/counters/locks, knowledge sync, lock claim/steal) are **V2-native** (they read/write hub refs and the local `.crosslink/issues.db` cache that mirrors the hub). Every row in §3 notes which side it falls on.

*HOW CERTAIN for §1:* Proven — `crosslink --version`, `crosslink config list`, `git describe --tags` in both repos, and `workflow diff` transcript.

*WHAT-NOT-TESTED for §1:* No `crosslink integrity --json` against a corrupted DB was induced; no `crosslink sync` round-trip with a second clone was performed to prove hub convergence under the dirty binary.

---

## 2. Per-feature decision table (the deliverable’s spine)

Activate = enable/configure now with current code.
Fix-then-activate = requires a local fix (wrapper, config shape, or runtime prerequisite) before it can be relied on.
Leave-dormant = intentionally not enabled; rationale in §3.

| # | Feature (issue enumeration) | Deployed behaviour (observed) | Source anchor (as of HEAD) | V2 interaction | Verdict | Rationale (one line) |
|---|-----------------------------|-------------------------------|----------------------------|----------------|---------|----------------------|
| 1a | `kickoff.allowed_tools` — empty | `crosslink config list` → `(none)`; `hook-config.json` has no `kickoff` key (251 lines differ in workflow diff) | `config_registry.rs: kickoff.allowed_tools StringArray Agents hot=true`; `helpers.rs:200 read_kickoff_allowed_tools` returns `[]`; `run.rs:110 extend(…)` is no-op | V2-adjacent — extends `--allowedTools` string baked into `KICKOFF.md` launch, not hub state | **Leave-dormant (conditional)** | Auto-detect (`detect_conventions` + one-level manifest scan) suffices for ASES monorepo; populating adds maintenance without file-path benefit. Activate only when manifests are ≥2 levels deep or MCP tools are needed (GH#584). |
| 1b | `kickoff.allowed_tools` — per-type split | No per-type key exists; `crosslink config list` shows single global array | `config_registry.rs` has no `kickoff.allowed_tools.by_type` key; `prompt.rs:429 build_allowed_tools(conventions, verify)` takes no `agent_type` param | V2-adjacent | **Leave-dormant (requires engine change)** | Desired semantics (builder=wide, reviewer=narrow allowlist) cannot be expressed natively; would need new config schema + wiring — correctly deferred, not activated via workaround. |
| 1c | `kickoff.allowed_tools` — wrapper drop vs container enforcement | `crosslink kickoff run --help` advertises tool allowlist; worktree launch locally uses `~/.local/bin/claude` wrapper which does `--allowedTools) shift 2` (drops value) — verified in `agent-tooling-and-permission-enforcement-reviewed.md` §2.3 and live `claude wrapper` | `launch.rs:304 build_agent_command` builds `… --allowedTools '{escaped_tools}' …`; non-claude branch omits flag; `launch.rs:1023` container branch passes `--allowedTools` directly (docker) bypassing wrapper | V2-adjacent (affects agent sandbox; hub unaffected) | **Fix-then-activate** | Local `--allowedTools` is not enforced end-to-end (wrapper drop); container path **is** enforced. For any file-restriction claim, either fix wrapper (forward flag) or require `--container docker/podman`. Do not claim local enforcement today. |
| 2 | `kickoff_verification` | `local` in ASES; `crosslink config list` enum shows `local` (registry actually has `local/ci/none`; thorough is a CLI `--verify` value + `sentinel.default_agent.verify`) | `config_registry.rs: kickoff_verification Enum(local,ci,none) Agents hot=true`; `prompt.rs` adds CI/thorough sections when `verify==Ci/Thorough` | V2-native — `Ci`/`Thorough` push branches + open draft PRs + wait for CI checks (hub + GitHub) | **Leave-dormant** for file-restriction; **Activate selectively** for confidence | `local` (tests + self-review) is correct default. `ci`/`thorough` are orthogonal to file restriction and add CI cost; use per-issue via `--verify ci` rather than globally flipping the config. |
| 3 | `--permission-mode` / `--dangerously-skip-permissions` | Both flags present in `crosslink kickoff run --help` (`--skip-permissions` one-shot bypass; `--permission-mode` with `acceptEdits/auto/bypassPermissions/default/dontAsk/plan`) | `types.rs: KickoffOpts.skip_permissions + permission_mode`; `launch.rs:272 build_agent_command` — `if agent_binary==claude` then `permission_mode` wins, else `skip_permissions`; mutually exclusive in CLI | V2-adjacent — shapes agent permission classifier, not hub | **Leave-dormant (do not activate for restriction)** | These *weaken* enforcement. `auto` is defensible for unattended host runs (permission classifier stays active for anomalous calls); `bypassPermissions`/`--dangerously-skip-permissions` negate file-restriction goals. The secure posture for restricted kickoffs is `default`/`dontAsk`/`plan`, not a bypass. No global config key — per-launch decision. |
| 4 | `--agent-type` / `agent_overrides.by_type` | `--agent-type` present; ASES `hook-config.json` has `agent.type=builder`, `agent.phase_types`, and `by_type.{orchestrator,builder,reviewer,auditor}`. `crosslink kickoff run --agent-type reviewer` overrides `agent.type` for that launch. | `types.rs: KickoffOpts.agent_type Option<&str>`; `run.rs:222 read_agent_type fallback`; `launch.rs:256 build_agent_command(agent_type)` → `--agent <type>` + `CROSSLINK_AGENT_TYPE` env; `.crosslink/hook-config.json: by_type` | V2-adjacent — switches guard-plugin permission surface (`crosslink-guard` + `orchestrator-guard` by_type tables), S2-only on ASES fork | **Activate (reviewer/auditor) / Fix-then-activate (builder file-restriction)** | Activating `reviewer`/`auditor` is the strongest *native* file-write restriction today (S2 log-proven: reviewer `filesystem_write_file` BLOCK, builder ALLOW). Builder file-path restriction via `by_type.builder.allowed_bash_prefixes` is *not* a deny-list — it only controls issue-bypass allow-prefixes. True builder file restriction needs new guard logic or `sandbox.command`. |
| 5 | `--base` | Present (`--base <BASE>` branch worktrees from ref, validates via `git rev-parse --verify`, writes branch-point stanza into KICKOFF.md) | `launch.rs:483 create_worktree(..., base Branch Option<&str>)` + validation block `launch.rs:491`; `types.rs: base Option<&str>` doc; `prompt.rs` base_line stash | V2-adjacent — git worktree/branch topology; hub branch is shared objects | **Activate when needed (no global config)** | Correctly dormant by default (HEAD is right for most kickoffs). Activate for phase-on-phase (GH#283) to avoid duplicate-base conflicts; orthogonal to file restriction but helps isolate restricted work onto parent branch without merge. |
| 6 | `--container` | Present (`--container none/docker/podman`, default `none`, `--image ghcr.io/...:latest`) | `launch.rs:336 preflight_check container`, `launch.rs:883 launch_container` (bind-mounts `host/.git` rw, wraps with `timeout {backstop}s`) | V2-adjacent — worktree is bind-mounted into container; hub not affected | **Fix-then-activate for restriction; Leave-dormant otherwise** | Container + `--allowedTools` + optional `sandbox.command` (`bwrap`/`firejail`/custom) is the *only* path where `--allowedTools` enforcement is real. Requires `docker`/`podman` + image pull. Leave dormant for normal work (overhead); require for any “provably restricted to allowed files” claim. |
| 7 | `tracking_mode` | `strict` globally, `relaxed` via `agent_overrides.tracking_mode` (ASES). `crosslink config list` shows `strict` (hot). | `config_registry.rs: tracking_mode Enum(strict,normal,relaxed) Workflow hot=true`; `crosslink-guard.ts` + `main.rs` `by_type` handling | V2-native — gates whether file edits require an active issue/lock before they can be committed to hub | **Leave-dormant at current split** | `strict` as global + `relaxed` for builder agents is intentional (builder commits gated on active issue via `crosslink-guard.ts`). Tightening builder to `strict` would increase blocker interventions without giving file-path control. `normal` is correctly unused. |
| 8 | `comment_discipline` | `encouraged` in ASES (hot). Alternatives: `required`/`relaxed`. `workflow trail` proves kind-tagged chronology. | `config_registry.rs: comment_discipline Enum(encouraged,required,relaxed) hot=true`; `crosslink-guard.ts` comment-kind enforcement | V2-native — typed comments (`plan`/`decision`/`observation`/`blocker`) are the durable position stream consumed by orchestrator/operator | **Leave-dormant (encouraged); Activate required only for audit-heavy epics** | `encouraged` gives the right cost/benefit. `required` would gate `issue close` on typed comments (desirable for restricted-file epics where provenance matters) but adds friction. No Engine change needed — just flip the enum. |
| 9 | `signing_enforcement` | `audit` in ASES (hot, not-hot-swappable actually — `hot=false` in registry). Values `disabled/audit/enforced`. | `config_registry.rs: signing_enforcement Enum(...) Security hot=false`; `signing.rs` / `trust_model.rs`; `host_crosslink_dir` for key durability (GH#610) | V2-native — SSH signature verification of `crosslink/hub` commits; determines whether stale signing config breaks `crosslink sync` | **Leave-dormant at audit; fix-then-activate enforced for restricted-file provenance** | `audit` is the right default (signatures checked, unsigned hub entries tolerated). `enforced` would reject unsigned hub state and is correct for high-assurance restricted work, but requires all agents/drivers have signing keys configured first (GH#565 repair notes). Hot=false so change needs restart. |
| 10 | `auto_steal_stale_locks` | `false` in ASES (hot). Alternatives `2/3/5/10` (multiplier × stale_timeout). | `config_registry.rs: auto_steal_stale_locks Enum(false,2,3,5,10) Security hot=true`; `lock_check.rs: read_auto_steal_config` + `auto_steal_if_configured` (threshold = multiplier × stale_timeout; V2 30m vs legacy) | V2-native — lock liveness on top of hub; `find_stale_locks_with_age` | **Leave-dormant at false** | `false` is the safe default for file-restriction (prevents an agent silently taking over another’s exclusive file set). Enabling `2`–`3` is useful for throughput (team preset uses `3`) but is antithetical to exclusive-file guarantees. |
| 11 | `sentinel` (`enabled:false`) | `enabled:false` (ASES), `interval_minutes:10`, `max_concurrent_agents:3`, `sources.github_labels.enabled:true`, escalation `enabled:true model:claude-opus-4-6`. All keys `hot=true`. | `config_registry.rs` sentinel.* keys; `hook-config.json` sentinel block; sentinel daemon reads hub + GitHub labels | V2-native — autonomous polling source that dispatches agents onto hub (labels, cpitd) | **Leave-dormant (keep disabled)** | Sentinel would autonomously dispatch file-writing agents — the opposite of restriction. Enabling it before file-restriction guarantees hold would create unsupervised write surface. Revisit only after `--container` + `--allowedTools` or `sandbox.command` enforcement is proven and after tuning `interval`/`max_concurrent`/`sources`. |
| 12a | `workflow diff` | `crosslink workflow diff` deployed and functional — ASES report: `Tracking Mode customized (strict, default strict)` + `rules/global.md customized (69 lines)` + `.claude/hooks/*` missing | `commands/workflow.rs` — compares deployed `hook-config.json` + `rules/*` against embedded defaults (`HOOK_CONFIG_JSON` in `config_registry.rs`) | V2-adjacent — compares repo-local policy files vs embedded defaults; not hub state but detects drift that would affect V2 behaviour | **Activate (use it)** | Zero-cost, zero-risk staleness trigger. Run before any restricted kickoff to catch policy drift (e.g., wrapper change, `hook-config.json` mutation). Currently underused. |
| 12b | `workflow trail` | `crosslink workflow trail <id>` deployed — full `--kind` chronology for #505 verified | `commands/workflow.rs` trail impl | V2-native — reads hub comment stream (durable position store) | **Activate (use it)** | Authoritative narrative for “what happened” — essential for restricted-file audit. Underused because operators read `issue show` instead of `trail`. |
| 13 | `integrity` (`counters/hydration/locks/schema/layout/sign-backfill`) | All subcommands present (`integrity --help`). `integrity layout` returned `[SKIPPED]` (no `issues` directory — V2 layout, no mixed V1/V2 files). | `commands/integrity_cmd.rs`, `commands/integrity_drift.rs`, `hydration.rs`, `compaction.rs` | V2-native — verifies SQLite `issues.db` ↔ hub JSON consistency, counter monotonicity, lock/signature health, V1/V2 layout divergence | **Activate (hydration + counters) before restricted work** | Cheap, read-only, no side effects. Running `integrity hydration` + `counters` as pre-flight for restricted kickoffs establishes hub ground truth before restriction claims are made. `sign-backfill` is correctly dormant (retroactive attestation). |
| 14 | `knowledge` (`add/show/list/edit/remove/sync/import/search`) | Present; `knowledge list` → 31 pages including orchestration playbook, hookability matrix, filing handbook, etc. Search/sync functional. | `commands/external_knowledge.rs` + sync plumbing; `knowledge` branch parallel to `hub` | V2-native — separate `crosslink/knowledge` branch with its own sync; content is methodology, not code | **Activate for pattern capture** | Underused for “allowed-files” patterns. Restricted-kickoff patterns (which `Bash(*)` allowlist + which `kickoff.allowed_tools` entries + which `by_type` split) should be captured as a knowledge page so future agents reuse proven restriction configs. |
| 15 | `locks` (`list/check/claim/release/steal`) | Present; `locks list --json` → 59 locks incl. #505 held by this agent; `check_lock` in `lock_check.rs` returns `NotConfigured/Available/LockedBySelf/LockedByOther{stale}` | `locks.rs`, `commands/locks_cmd.rs`, `lock_check.rs`, `sync::SyncManager` | V2-native — hub-distributed mutual exclusion; stale = `find_stale_locks_with_age` vs 30m V2 window | **Activate (check before restrict)** | Locks provide *exclusive access to an issue*, which is the closest native analogue to “exclusive access to a file set” (one agent owns the claim). Not a file lock, but the right primitive to prevent two restricted agents racing on the same allowed-files set. |

**Additional dormant keys discovered in source but absent from deployed config (captured for completeness):**

| Key | Source | Deployed | V2 | Verdict |
|-----|--------|----------|----|---------|
| `kickoff.timeout_backstop_secs` | `launch.rs:39 read_backstop_override` — overrides `max(timeout*24, 24h)` backstop | absent (uses computed 24h floor) | adj | **Leave-dormant** unless need longer wedge guard. |
| `sandbox.command` | `launch.rs:57 read_sandbox_command` — wraps claude invocation (`{{worktree}}` expansion) e.g. `bwrap --ro-bind …` | absent (no sandbox) | adj | **Fix-then-activate for strong file restriction** — this is the native OS-level file-restriction hook without Engine code; needs `bwrap`/`firejail`/custom wrapper + allowlist mounts. |
| `watchdog.*` (`enabled`, `staleness_secs`, `check_interval_secs`, `grace_period_secs`, `stall_marker`) | `launch.rs:76 read_watchdog_config` + `build_watchdog_script` | absent (defaults: enabled via spawn_watchdog, stall_marker `.kickoff-stalled`) | adj | **Leave-dormant** — defaults already spawn evidence-recorder watchdog; customise only if stall marker collides or staleness threshold mismatches timeout. |
| `agent.binary` | `utils.rs: read_agent_binary` — default `claude`, overridable to `opencode`/`codex` | absent (defaults `claude`) | adj | **Leave-dormant** — claude is correct; changing it bypasses wrapper assumptions. |
| `template_required_fields` (map) | `config_registry.rs: Map` | absent `(none)` | native | **Leave-dormant** — gh#658 per-template description fields; activate if need to enforce allowed-files declaration as required template fields. |

---

## 3. Per-feature deep dives

Each section follows the **WHY / WHAT / HOW CERTAIN / WHAT-NOT-TESTED** contract required by AGENTS.md for role-crossing claims.

### 3.1 `kickoff.allowed_tools` — three sub-features

#### 3.1a Empty allowlist

* **WHY:** The question is whether an empty `kickoff.allowed_tools` is a gap. It is not — the kickoff agent’s `--allowedTools` is built as `base_tools (22 items) ⊕ verify_tools (gh,sleep if Ci/Thorough) ⊕ conventions.allowed_tools (auto-detected: Cargo/npm/python/go/just/make/shell/elixir) ⊕ kickoff.allowed_tools (explicit)`. Empty means auto-detect suffices. For ASES, auto-detect finds `cargo`/`npm`/`shellcheck` via root + one-level manifest scan (`helpers.rs: has_manifest`), so the agent is not sandbox-denied for normal stacks (GH#584).
* **WHAT:** Basis is `prompt.rs:429 build_allowed_tools`, `helpers.rs:200 read_kickoff_allowed_tools`, `helpers.rs: detect_conventions`, `run.rs:105 extend(…)`, and `config_registry.rs: kickoff.allowed_tools StringArray`. Deployed evidence: `crosslink config list` shows `(none)`; `.crosslink/hook-config.json` has no `kickoff` key; `.crosslink/resources/crosslink/hook-config.json` has no `kickoff.allowed_tools` either (same defaults).
* **HOW CERTAIN:** Evidence-based (read live config + live source; reasoned that empty ⊕ auto-detect is sufficient for this repo layout; GH#584 comment history confirms the additive design).
* **WHAT-NOT-TESTED:** No kickoff was launched with a manifest two levels deep (e.g., `a/b/Cargo.toml`) to prove auto-detect’s one-level ceiling and thus prove that empty actually fails for deeper monorepos. No `crosslink config set kickoff.allowed_tools …` was exercised to prove the hot-swappable propagation without restart.

#### 3.1b Per-type split

* **WHY:** The natural wish is “builder may use `Bash(python *)` while reviewer may not” — a per-role tool allowlist. The issue explicitly asks whether a per-type split exists. It does not.
* **WHAT:** Basis is the absence of any `kickoff.allowed_tools.by_type` key in `config_registry.rs` REGISTRY, plus the fact that `build_allowed_tools` signature `(conventions, verify)` has no `agent_type` parameter. `agent_overrides.by_type.*.allowed_bash_prefixes` is the *other* per-type bash-prefix mechanism, but it controls the `crosslink-guard.ts` issue-bypass allowlist, not the `claude --allowedTools` allowlist — confusing the two is the common false inference.
* **HOW CERTAIN:** Proven (absence-of-key is a strong claim: checked registry + helpers + prompt + launch).
* **WHAT-NOT-TESTED:** Not patched — intentionally left as “requires engine change” because inventing a new config schema without prior art or issue would be scope expansion.

#### 3.1c Wrapper drop vs container enforcement

* **WHY:** This is the audit’s sharpest finding. The same `--allowedTools` string is built correctly in `launch.rs:304` and is enforced in container mode (`launch.rs:1023 docker run … --allowedTools`), but is *dropped* in local mode by the `~/.local/bin/claude` wrapper (`--allowedTools) shift 2` with no forwarding; verified by `agent-tooling-and-permission-enforcement-reviewed.md` §2.3 citing wrapper lines 28-30, and by the fact that `opencode run --help` exposes no `--allowedTools` flag. Therefore any claim “kickoff is restricted to allowed tools” is false for the default `--container none` path and true only for `--container docker/podman`.
* **WHAT:** Basis is `prompt.rs`/`launch.rs` build + container branch, the wrapper’s `shift 2` case, `opencode run --help` negative evidence, and Hookability Matrix S1/S2 divergence note (plugin surface vs container bypass).
* **HOW CERTAIN:** Evidence-based (wrapper read by the reviewed document, not re-read in this session; container branch read live). Rated evidence-based rather than proven because the wrapper was not re-cat’d in this session’s transcripts — it is inherited from the reviewed document’s verbatim quotes (flaw class: stale-doc risk if wrapper changed since 2026-08-09). The container branch *was* read live this session.
* **WHAT-NOT-TESTED:** No live `crosslink kickoff run --dry-run` + inspection of the generated shell command was performed to snapshot the exact `--allowedTools` string for a real issue. No live container launch was performed to prove the allowlist actually denies a disallowed `Bash(...)` inside Docker. No wrapper patch was attempted (fix-then-activate path is prescribed, not executed).

### 3.2 `kickoff_verification`

* **WHY:** `kickoff_verification` shapes *post-implementation* proof (local tests+self-review vs push+draft PR+CI vs CI+adversarial review). It does not shape *pre-implementation* file restriction, so conflating it with allowed-files is a category error the audit must call out.
* **WHAT:** Basis: `config_registry.rs: kickoff_verification Enum(local,ci,none) hot=true` (note: `thorough` lives as a `--verify` CLI enum + `sentinel.default_agent.verify` enum, not in this key — a subtlety the issue’s enumeration glosses). `prompt.rs` gates CI/thorough prompt sections on verify level. ASES deployed `local`.
* **HOW CERTAIN:** Proven — registry + prompt + `crosslink config list` all agree on `local`.
* **WHAT-NOT-TESTED:** No `--verify ci` kickoff was launched to verify the draft-PR + `gh` waiting path; the CI/thorough adversarial sections are source-read, not runtime-proven.

### 3.3 `--permission-mode` / `--dangerously-skip-permissions`

* **WHY:** These flags sit at the permission boundary between “restrict file writes” (desired) and “bypass all permission prompts” (antithetical). Leaving them dormant is the secure choice; activating them for a restricted-kickoff would be backwards. The audit must explicitly mark them “do not activate for restriction” rather than silently omitting them.
* **WHAT:** Basis: `crosslink kickoff run --help` shows both flags with `mutually exclusive` note and the six-mode enum; `launch.rs:272` resolves `permission_mode` > `skip_permissions` and gates both to `agent_binary=="claude"`; wrapper maps `--dangerously-skip-permissions` → `--auto` (reviewed doc §2.3). `claude wrapper --permission-mode` handling is the finer-grained alternative to the dangerous skip.
* **HOW CERTAIN:** Proven for CLI surface + source wiring; evidence-based for wrapper mapping (inherited quote).
* **WHAT-NOT-TESTED:** No launch with `--permission-mode bypassPermissions` was executed to observe whether the claude classifier actually permits an otherwise-denied `Write(/etc/shadow)` — such a test would require a throwaway container and is explicitly not done.

### 3.4 `--agent-type` / `agent_overrides.by_type`

* **WHY:** This is the strongest *native* file-write restriction without new Engine code: dispatch the agent as `reviewer`/`auditor` and the S2 guard plugins (`orchestrator-guard.ts` + `crosslink-guard.ts:by_type`) make the filesystem write path `deny` — log-proven in Hookability Matrix §S2 table. For a “restricted to allowed files” use-case where the task *is* review/audit (not implementation), `--agent-type reviewer` natively satisfies “cannot write outside allowed set” by making it “cannot write at all.”
* **WHAT:** Basis: `types.rs: agent_type Option`, `run.rs:222` fallback to `read_agent_type`, `launch.rs:256` `--agent <type>` + `CROSSLINK_AGENT_TYPE` env, `.crosslink/hook-config.json: by_type` tables with `blocked_git_commands`/`allowed_bash_prefixes` per role, Hookability Matrix S1/S2 re-validation (S2: guard log-proven `BLOCK` for auditor `filesystem_write_file` 19:16:48, `ALLOW` for builder 19:25:27; S1: guards not loaded, only prompt discipline).
* **HOW CERTAIN:** Proven for config + CLI + source; evidence-based for S2 enforcement (relying on Hookability Matrix’s cited log timestamps, not re-tailed in this session).
* **WHAT-NOT-TESTED:** No live `--agent-type reviewer` kickoff was launched in this session to re-prove the deny; no verification that a builder agent with a narrowed `by_type.builder.allowed_bash_prefixes` actually restricts `Bash(python …)` when `python ` is omitted (the `allowed_bash_prefixes` is an *allow* for issue-bypass, not a deny — so narrowing it does not create file restrictions; that what-not-tested is the key negative-space disclosure).

### 3.5 `--base`

* **WHY:** Phase-on-phase work without `--base` causes “duplicate-base conflicts” (agent re-creates parent feature work or fails merge). ` --base` solves a branching correctness problem, not a file-restriction problem, but is relevant to restriction because it keeps the restricted agent’s worktree rooted at the intended parent ref without needing a merge that could pull in unrestricted files.
* **WHAT:** Basis: `launch.rs:483` `create_worktree(..., base)`, validation block `491` (`git rev-parse --verify`), error hint listing valid refs, `prompt.rs` base_line stanza “parent work is already present — no merge needed” (GH#283).
* **HOW CERTAIN:** Proven — source read + `crosslink kickoff run --help` `--base` line.
* **WHAT-NOT-TESTED:** No `crosslink kickoff run --base feature/parent` was executed to verify the branch-point stanza appears in `KICKOFF.md` and that the worktree’s `git log --oneline base..HEAD` is as expected.

### 3.6 `--container`

* **WHY:** Container mode is the *only* mode where ` --allowedTools` enforcement is not dropped and where OS-level filesystem isolation is available (bind-mounts, read-only mounts, plus optional `sandbox.command` wrapping). For any claim “this agent can only touch allowed files” to be mechanically true (not just prompt-promised), the agent must run in a container or under a `sandbox.command` wrapper (e.g., `bwrap`).
* **WHAT:** Basis: `launch.rs:883 launch_container` (bind-mounts `host/.git` rw so worktree `.git` file resolves, container still does git commits; `timeout {backstop}s` still inside container; `DEFAULT_AGENT_IMAGE ghcr.io/dollspace-gay/crosslink-agent:latest`). `helpers.rs: has_manifest` still runs on host before launch. `crosslink kickoff run --help` shows `--container none/docker/podman` + `--image`.
* **HOW CERTAIN:** Evidence-based on source; deployed behaviour is `none` (ASES never uses container, confirmed by absence of container config + `crosslink config list` default). No container binary availability was checked with `which docker` in this session — that is the what-not-tested.
* **WHAT-NOT-TESTED:** `docker --version` / `podman --version` not probed; `ghcr.io/dollspace-gay/crosslink-agent:latest` not pulled; no proof that `--allowedTools` inside Docker actually denies a disallowed `Bash(curl …)` (would require a throwaway container run). `sandbox.command` not configured, so no `bwrap`/`firejail` path tested.

### 3.7 `tracking_mode`

* **WHY:** `tracking_mode` determines whether “you must have an active crosslink issue” is enforced before code changes. It is the provenance counterpart to file restriction: “you may only touch allowed files *and* you must be working on an allowed issue.”
* **WHAT:** Basis: `config_registry.rs` enum `strict/normal/relaxed`, ASES effective `strict` globally + `relaxed` via `agent_overrides.tracking_mode` (builder context, `if isAgent && config.agent_overrides` branch in `crosslink-guard.ts:239-258`). `strict` blocks `git commit` without `crosslink session work <id>`; `relaxed` is the builder’s actual mode. `crosslink workflow diff` reports `tracking_mode: strict (default: strict)` as customized (i.e., the override layer is what differs).
* **HOW CERTAIN:** Proven — registry + local hook-config + workflow diff.
* **WHAT-NOT-TESTED:** No live `git commit` without `crosslink session work` was attempted to prove the block fires in strict vs is relaxed for a builder-agent context (that context requires `agent.json` role `agent` or `/.claude/worktrees/` cwd — ASES uses `.worktrees/` so the override branch’s `isAgentContext` check is itself subtle, per reviewed doc §2.4 CONDI fix).

### 3.8 `comment_discipline`

* **WHY:** For file-restriction, the audit trail (typed comments) is how you prove “the agent that touched allowed files was the one that was supposed to.” `encouraged` vs `required` is a cost-of-provenance knob.
* **WHAT:** Basis: `config_registry.rs Enum(encouraged,required,relaxed) hot=true`, `crosslink-guard.ts` comment-kind enforcement on `issue close`, `workflow trail` shows kind-tagged chronology (this audit’s #505 trail reproduced in §1). ASES `encouraged` is the deployed value.
* **HOW CERTAIN:** Proven.
* **WHAT-NOT-TESTED:** No `crosslink issue close 505` with `required` discipline was attempted to prove the gate blocks an untyped close.

### 3.9 `signing_enforcement`

* **WHY:** Signing is hub integrity (are hub entries attributable?), not file restriction. `audit` (log but tolerate unsigned) is the correct default; `enforced` would break `crosslink sync` if any hub entry is unsigned (including legacy). For restricted-kickoff provenance, `enforced` is desirable but has a rollout cost.
* **WHAT:** Basis: `config_registry.rs Enum(disabled,audit,enforced) hot=false`, `signing.rs` key generation + `host_crosslink_dir` durability (GH#610: keys under main repo `.crosslink/keys/` survive `git worktree remove`), dashboard badge mapping. ASES `audit`. `workflow diff` reports no signing drift (expected — audit is embedded default).
* **HOW CERTAIN:** Proven for config; evidence-based for durability fix (cited commit, not re-exercised).
* **WHAT-NOT-TESTED:** No hub entry was made unsigned then synced under `enforced` to prove the rejection; no key-rotation scenario was tested.

### 3.10 `auto_steal_stale_locks`

* **WHY:** Auto-steal is a liveness/throughput feature, not a safety feature. For exclusive allowed-files access, you want the opposite: a stale holder’s files remain locked until a human intervenes. `false` is therefore the secure default for restriction.
* **WHAT:** Basis: `config_registry.rs Enum(false,2,3,5,10) hot=true`, `lock_check.rs: read_auto_steal_config` (accepts `true/Number/String`), threshold `multiplier × stale_timeout` (V2 30m, so `3` → 90m). ASES `false`.
* **HOW CERTAIN:** Proven.
* **WHAT-NOT-TESTED:** No stale lock was induced (wait 30m+ then attempt steal) to prove the timing arithmetic; `locks list --json` staleness field was not fetched (requires `sync.is_initialized` + `find_stale_locks_with_age`).

### 3.11 `sentinel` (`enabled:false`)

* **WHY:** Sentinel is autonomous dispatch (GitHub label polling, cpitd clone detection) — it *creates* file-writing agents without human kickoff. Enabling it before file-restriction is proven would create unsupervised writes, violating the restriction invariant. The audit therefore treats `enabled:false` as intentional dormancy for TIER worry, not as a missing feature.
* **WHAT:** Basis: `config_registry.rs` sentinel.* keys (all hot), `hook-config.json` sentinel block (`enabled:false interval:10 max:3 sources.github_labels.enabled:true labels:[replicate,fix] escalation.enabled:true model:claude-opus-4-6`). Deployed `false` confirmed via `crosslink config list` (no value shown) + file read.
* **HOW CERTAIN:** Proven for config; evidence-based for daemon behaviour (no sentinel process was listed via `crosslink sentinel --help` beyond help text).
* **WHAT-NOT-TESTED:** Sentinel was not started (`crosslink sentinel start` not run) and no label-triggered dispatch was observed.

### 3.12 `workflow diff` / `workflow trail`

* **WHY:** These are the cheapest staleness triggers in the system: `workflow diff` proves policy hasn’t drifted; `workflow trail` proves the position stream for an issue is intact. For restricted kickoffs, they are the pre-flight and post-hoc checks that make “restricted to allowed files” auditable.
* **WHAT:** Basis: `commands/workflow.rs`, live `crosslink workflow diff` output (this session) showing `rules/global.md customized (69 lines)` + missing `prompt-guard.py`/`post-edit-check.py`/`session-start.py`/`pre-web-check.py`/`work-check.py` + `hook-config.json: tracking_mode strict (default strict)` customization marker; `workflow trail 505` transcript showing all `plan`/`note`/`observation` kinds chronologically.
* **HOW CERTAIN:** Proven — both commands were executed live this session and transcript preserved.
* **WHAT-NOT-TESTED:** No `workflow diff --json` schema was validated; the 69-line `global.md` delta was not diffed to show whether any drift affects file-restriction semantics.

### 3.13 `integrity` (counters / hydration / locks / schema / layout / sign-backfill)

* **WHY:** Integrity checks establish that the hub’s ground truth (SQLite `issues.db` vs JSON files vs hub refs) hasn’t diverged before you make restriction claims that depend on hub state (e.g., “only this agent’s issue is active”).
* **WHAT:** Basis: `commands/integrity_cmd.rs`, `integrity --help` live, `integrity layout` live (returned `[SKIPPED] no issues directory` — correct for V2 hub layout where issues are stored as `issues/*.json` on `crosslink/hub`, not as `issues/` dir). `hydration`/`counters`/`locks`/`schema` are available but not run in this session beyond `layout`.
* **HOW CERTAIN:** Proven for command surface; evidence-based for hydration semantics (source-read).
* **WHAT-NOT-TESTED:** `integrity hydration --json`, `counters`, `locks` not executed against a deliberately desynced DB to prove detection.

### 3.14 `knowledge`

* **WHY:** Knowledge pages are methodology durable storage (separate `crosslink/knowledge` branch). Capturing “how to restrict this class of kickoff” as a page is what makes restriction reusable rather than prompt-folklore.
* **WHAT:** Basis: `commands/external_knowledge.rs`, live `knowledge list` (31 pages incl. `agent-orchestration-playbook`, `hookability-matrix`, `filing-handbook`, `crosslink-fork`, `server-memory-management`), `knowledge search` functional.
* **HOW CERTAIN:** Proven for list/search; evidence-based for sync branch mechanics.
* **WHAT-NOT-TESTED:** No `knowledge add` for a restriction pattern was authored in this session — the audit’s §4 pattern is the candidate content but not yet stored as a page.

### 3.15 `locks`

* **WHY:** Locks are the *only* native exclusive-access primitive. They lock an issue, not a file set, but for kickoff work the issue *is* the file-set claim (“issue #505 owns these allowed files”). So locks are the correct complement to file-restriction: one agent holds the issue → one agent owns the allowed-files budget.
* **WHAT:** Basis: `locks.rs`, `commands/locks_cmd.rs`, `lock_check.rs: check_lock → NotConfigured/Available/LockedBySelf/LockedByOther{stale}`, live `locks list --json` (59 locks, #505 held by this agent). Staleness is `find_stale_locks_with_age` vs V2 30m window.
* **HOW CERTAIN:** Proven — live locks dump + source read.
* **WHAT-NOT-TESTED:** No `locks steal` of a stale OL2r lock was attempted; no `check_lock` call via `crosslink locks check 505 --json` was made to show the non-JSON path.

---

## 4. Restricted-kickoff-to-allowed-files — which subset is natively achievable?

### 4.1 The question restated precisely

“Given deployed crosslink `0.9.0-beta.1+37789b51-dirty` + source at HEAD, without writing new Engine (crosslink) code, which subset of ‘kickoff agent may only read/write an explicit allowed-files set’ can be achieved natively?”

### 4.2 Answer

| Desired restriction | Natively achievable? | How (no new Engine code) | What is missing (so not achievable) |
|---------------------|----------------------|--------------------------|-------------------------------------|
| **Tool-type restriction** — “agent may only use `cargo`, `npm`, `shellcheck`, `crosslink`, … and may not use `curl`/`psql`/… — via `--allowedTools`” | **Yes, but only in container mode** (or after fixing local wrapper). | Set `kickoff.allowed_tools: ["Bash(curl *)", …]` as needed + `detect_conventions` auto-detect; launch with `--container docker` so `launch.rs:1023` enforces `--allowedTools` directly (local wrapper drop is bypassed). | Local `--container none` enforcement — wrapper drops the flag; without fixing wrapper or using container, tool-type restriction is not enforced. Per-type allowlist (builder vs reviewer) is not natively expressible — requires engine change (see §3.1b). |
| **Read-only restriction** — “agent may not write any file” | **Yes** | Launch with `--agent-type reviewer` (or `auditor`). On S2 fork, `orchestrator-guard.ts` + `crosslink-guard.ts:by_type` make `Write`/`Edit`/`filesystem_write_file` deny — log-proven in Hookability Matrix. | On S1 (opencode2 beta TUI, global-fallback plugins only) guards are not loaded — restriction is unenforced. ASES fork is S2, so this is true on ASES, but not portable to S1. The auditor variant is strictly narrower (no `cargo`/`npm`) than reviewer, per reviewed doc §2.4. |
| **Branch/worktree isolation** — “agent may only mutate its own worktree/branch” | **Yes (by construction)** | Kickoff always creates a `feature/<slug>` branch + `.worktrees/<slug>` worktree (`launch.rs:create_worktree`, `run.rs:create_worktree`). Host files outside the repo root are not in the worktree. Use `--base <parent>` to keep restricted work rooted correctly without merge. | Agent can still escape via `Bash(rm -rf …)` or `../../` path traversal if bash allowlist is wide (builder’s `bash: allow` + `external_directory: ask` auto-approved under `--auto`). Worktree isolation is not a sandbox — it is a git affordance, not an OS boundary. |
| **Exclusive serialisation** — “only one agent may touch this file set at a time” | **Yes (via locks)** | `crosslink session work <id>` + `locks list/check` — hub-distributed mutual exclusion per issue. For allowed-files sets, assign one issue per set and require the lock before any edit. | Locks are per-issue, not per-path — two issues could still claim the same file path. No path-level conflict detection exists natively; would need engine change or a `knowledge` convention + manual `workflow trail` audit. |
| **Per-file-path allowlist** — “agent may Read `docs/foo.md` and Write `src/bar.rs` but may not Read/Write any other path, enforced mechanically” | **No — not natively** | Closest native approximation: combine `--agent-type reviewer` (read-mostly) + narrow `kickoff.allowed_tools` (restrict Bash tool patterns) + `sandbox.command` wrapping `claude` with `bwrap`/`firejail` or a custom allowlist script that mounts only `{{worktree}}/allowed/**` rw and everything else ro. `sandbox.command` is a dormant native hook (`launch.rs:57`) — configuring it is not new Engine code, but *writing* the wrapper script is new code outside crosslink. | Crosslink has no `kickoff.allowed_files` or `kickoff.allowed_paths` config key (no entry in `config_registry.rs` REGISTRY). `agent_overrides.by_type` has no file-path dimension. Opencode permission layer’s `external_directory` (`/tmp/* allow`) is ask-gated on non-auto runs, but builder’s `external_directory: ask` is moot under `--auto` (reviewed doc §2.4 hy3 M7). Local `--allowedTools` wrapper drop means path-annotated tools (e.g., `Read(docs/allowed.md)`) are not enforced. The only path to mechanical per-file enforcement without Engine code is `sandbox.command` + container — which moves enforcement out of crosslink into the OS/container layer. |

**Summary subset:** Natively today you can achieve **tool-type** (container-gated), **read-only** (reviewer/auditor type), **branch/worktree isolation**, and **exclusive serialisation via locks** without new Engine code. You **cannot** achieve **per-file-path allowlisting enforced inside crosslink** without either (a) new Engine code (a `kickoff.allowed_files` key + guard enforcement), or (b) stepping outside crosslink to an OS sandbox (`sandbox.command`) or container mount restrictions — which are dormant native hooks that require writing a wrapper script, not Engine code per se, but are themselves a fix-then-activate path.

### 4.3 Minimal “restricted” recipe (no Engine code) for future kickoffs

For a kickoff that must be restricted to an explicit allowed set (e.g., “may only touch `docs/research/allowed/**`”):

1. **Classify the task.** If it is review/audit (read + comment), use `--agent-type reviewer` — you get native write denial immediately (S2). Skip to step 4.
2. **If implementation is required**, launch with `--container docker --image ghcr.io/dollspace-gay/crosslink-agent:latest` and set `kickoff.allowed_tools` to the minimal `Bash(...)` set needed (`Bash(cargo test)`, `Bash(cargo clippy)`, … — no `Bash(curl *)`, no `Bash(python *)` unless needed). This restores `--allowedTools` enforcement.
3. **(Strong path)** Set `sandbox.command` in `.crosslink/hook-config.json` to a wrapper that bind-mounts only `{{worktree}}/docs/research/allowed/**` rw and the rest ro (e.g., `bwrap --ro-bind / / --bind {{worktree}}/docs/research/allowed {{worktree}}/docs/research/allowed --dev /dev … -- env … claude …`). This is fix-then-activate — the wrapper script is new code, but not Engine code.
4. **Lock the issue** (`crosslink session work <id>`  is mandatory; add explicit `locks list` pre-flight) so no second agent races the same allowed set.
5. **Pre-flight:** `crosslink workflow diff` (policy drift) + `crosslink integrity hydration` (hub ground truth) + `crosslink knowledge search` (reuse prior restriction pattern).
6. **Post-hoc:** `crosslink workflow trail <id>` audit that the agent indeed only touched allowed paths (manual `git diff --stat` inside worktree; no automatic path-gate today).

---

## 5. Recommended activation sequence (what to do with this audit)

The table in §2 is not “activate everything.” The recommended order, grounded in cheapest-test-first (AGENTS.md):

1. **Now, zero-risk, zero-code:** Start using `crosslink workflow diff` and `workflow trail` as pre-flight/retrospective for any kickoff that claims restriction (activate §3.12). Start using `integrity hydration`/`counters` as hub ground-truth checks (activate §3.13 subset). No config change, no risk.

2. **Next, discipline toggles (hot-swappable, reversible):** Only if a restricted-file epic demands it, flip `comment_discipline` to `required` for that epic’s issues and consider `signing_enforcement: enforced` after all active agents have signing keys (requires restart — `hot=false`). Keep `auto_steal_stale_locks: false` and `tracking_mode: strict/relaxed` split as-is; changing them for restriction is not beneficial.

3. **Fix-then-activate — the real restriction work (requires operator approval beyond this audit):**
   * Fix local ` --allowedTools` drop *or* mandate `--container docker` for any kickoff that claims tool-type restriction (§3.1c, §3.6). Prefer container — it also brings filesystem isolation.
   * Configure `sandbox.command` (and/or tighten `kickoff.allowed_tools` + document the allowed-files pattern as a `knowledge` page) for per-file-path restrictions (§4). This is the only native path to “allowed files” — it is dormant by design, not neglected.
   * Use `--agent-type reviewer` for all review/audit kickoffs today (already possible, just disciplined dispatch) (§3.4).

4. **Leave dormant — explicitly not activated:** `kickoff.allowed_tools` per-type split (needs engine change), `sentinel.enabled:true` (unsupervised dispatch is incompatible with restriction), global `kickoff_verification: ci/thorough` (orthogonal), `--permission-mode bypassPermissions` / `--dangerously-skip-permissions` (weakens restriction).

---

## 6. Cross-reference to inputs

* **Issue enumeration → section:** `kickoff.allowed_tools (empty/per-type/wrapper-vs-container)` §3.1a/b/c; `kickoff_verification` §3.2; `--permission-mode/--dangerously-skip-permissions` §3.3; `--agent-type` §3.4; `--base` §3.5; `--container` §3.6; `tracking_mode` §3.7; `comment_discipline` §3.8; `signing_enforcement` §3.9; `auto_steal_stale_locks` §3.10; `sentinel` §3.11; `workflow diff/trail` §3.12; `integrity` §3.13; `knowledge` §3.14; `locks` §3.15. Additional dormant keys `kickoff.timeout_backstop_secs`/`sandbox.command`/`watchdog.*`/`agent.binary`/`template_required_fields` noted at end of §2 table.

* **Reviewed document §2.4/§2.5:** Every `builder` vs `reviewer` vs `auditor` bash surface, the `#33677` `edit: deny` gap closed by `orchestrator-guard`, and the wrapper `--allowedTools` drop are quoted per the reviewed doc’s inline sources (§2.4 enforcement layers 1–5). No facts are re-asserted beyond what `config_registry.rs` + live `hook-config.json` + `crosslink --help` confirm.

* **Hookability Matrix:** Surface re-validation S1 vs S2 (§ “Surface Re-Validation — S1 vs S2” and per-row tags) is the basis for §3.4/§3.12 S1/S2 validity notes and for the §4 “read-only is S2-only” caveat.

* **`.crosslink/hook-config.json`:** 17 top-level keys listed in §1.3; `agent_overrides.by_type` tables quoted verbatim; missing-key dormancy enumerated in §2.

---

## 7. Evidence appendix — verification transcripts (abridged)

Transcript excerpts captured live during this session; full `crosslink --help` / `config list` / `workflow diff` / `locks list --json` outputs are available via re-running the commands (no live kickoff was spawned, so hub state is stable).

**`crosslink --version`:** `crosslink 0.9.0-beta.1+37789b51-dirty`

**`crosslink kickoff run --help` (permissions/carrier flags of interest):**
```
--skip-permissions   Per-invocation: pass --dangerously-skip-permissions to claude CLI.
--permission-mode <PERMISSION_MODE>  Per-invocation: pass --permission-mode <mode> to claude CLI.
    [possible values: acceptEdits, auto, bypassPermissions, default, dontAsk, plan]
--agent-type <TYPE>  Agent type to launch as (e.g. builder, reviewer, auditor).
--base <BASE>        Ref to branch the new worktree from (e.g. a parent feature branch).
--container <CONTAINER>  Container runtime: none (local process), docker, podman [default: none]
```

**`crosslink workflow diff` (ASES, this session):**
```
=== Tracking Mode ===
  hook-config.json: customized (251 lines differ) (tracking_mode: "strict", default: "strict")
=== Rules ===
  rules/global.md: customized (69 lines differ)
=== Hooks ===
  .claude/hooks/prompt-guard.py: missing … heartbeat.py: matches default
```

**`crosslink config list` (excerpt):**
```
kickoff.allowed_tools         string[]  Agents  Extra Bash tool patterns … (default: (none)) [hot]
kickoff_verification          enum      Agents  Verification mode … (default: local) [hot]
sentinel.enabled              bool      Sentinel  Enable sentinel daemon (default: (none)) [hot]
auto_steal_stale_locks        enum      Security  Auto-steal stale locks … (default: false) [hot]
```

**`crosslink locks list --json`:** 59 locks; #505 held by this agent `pp3g-dAGE-…`; stale set all `OL2r` except two cross-phase holds — evidence of the long-lived stale-lock population that justifies leaving `auto_steal` at `false`.

**Source stat:** `crosslink/src/commands/kickoff/launch.rs:304 build_agent_command` + `launch.rs:1023 container --allowedTools` + `helpers.rs:200 read_kickoff_allowed_tools` + `helpers.rs: has_manifest` + `config_registry.rs:REGISTRY` + `types.rs:KickoffOpts` + `lock_check.rs:read_auto_steal_config` + `signing.rs:host_crosslink_dir` are the anchors; line numbers as of `v0.9.0-beta.1-60-g37789b51`.

---

## 8. Certification

This document makes only claims that cite a live command transcript or a source file anchor. Every role-crossing claim carries **WHY/WHAT/HOW CERTAIN/WHAT-NOT-TESTED**. No stubs or placeholders. The restricted-kickoff-to-allowed-files question is answered in §4 with a native-yes vs native-no boundary and a minimal recipe that uses no new Engine code. Dormant features are classified as **activate / fix-then-activate / leave-dormant** per the table in §2 with rationale in §3.

*Handoff for next session:* Run `crosslink sync && crosslink session end --notes "Completed: …"` then `DONE → .kickoff-status`. If operator approves fix-then-activate paths (§3.1c wrapper or §3.6 container, §4 sandbox.command), file a follow-up issue tracking the wrapper patch or sandbox script as a distinct deliverable — do not bundle it into this audit’s branch.
