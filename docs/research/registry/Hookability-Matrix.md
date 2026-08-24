---
title: Hookability Matrix
program: EDASES
layer: Research
document_type: Registry
status: Active
authority: Derived
canonical_repository: edases

depends_on:
  - Agent Orchestration Playbook

consumed_by:
  - Hook Implementation Priorities

related_documents:
  - Failure Matrix
  - Model Routing Matrix
  - Harness Capability Matrix

supersedes: []
review_frequency: Quarterly (or when playbook changes)
last_reviewed: 2026-08-24

---

# Hookability Matrix

**Date:** 2026-08-24 (extended per #440; original 2026-08-18)
**Source:** Agent Orchestration Playbook hookability audit, corrected per #404 verdict. Covers all 13 playbook sections plus Summary. Every rule classified as hookable (a/b/c/d) or not hookable (e), with mechanism details and feasibility assessment. The #440 extension adds (1) per-surface validity re-classification of every enforcement row against the S1/S2 divergence established by #425, and (2) classification rows for the 2026-08-23/24 doctrine batch (fetch-method-selection, push-cadence, task-length atomization, never-assume-model, quota-parking failure class).
**Convention:** Rows are playbook rules. Columns describe hookability, mechanism, feasibility, and enforcement status. Enforcement entries carry a surface tag where validity is surface-dependent: **[S2]** = fork CLI 1.18.13-pp3g only, **[S1+S2]** = both surfaces, **[surface-independent]** = outside the OpenCode plugin system (Claude Code hook, systemd, shell wrapper).

---

## Purpose

This matrix classifies every rule in the Agent Orchestration Playbook by hookability — whether it can be structurally enforced via tooling or must remain prompt-enforced discipline. It serves as:

1. A reference for hook implementation work (which rules to enforce first)
2. A prioritization tool for the Hook Implementation Priorities document
3. A living record of enforcement status (what is already hook-enforced vs what is not)
4. A bridge between playbook rules and concrete hook/plugin implementations

Unlike the Failure Matrix (which maps failures to required semantics), this matrix maps rules to enforcement mechanisms.

---

## Mechanism Legend

| Letter | Mechanism | Description |
|--------|-----------|-------------|
| (a) | **Tool interception** | OpenCode `tool.execute.before` / `tool.execute.after` — intercept tool calls and block/modify/warn |
| (b) | **Prompt injection** | PostToolUse hook injects system guidance into agent context (e.g., "HALT" instruction) |
| (c) | **CLI enforcement** | Crosslink CLI modification — validate args, enforce sequencing, reject invalid commands |
| (d) | **Shell wrapper** | Pre-dispatch shell script that validates environment, injects flags, or blocks invocations |
| (e) | **Not hookable** | Requires model reasoning — understanding intent, semantics, or context; cannot be structurally enforced |

---

## Surface Re-Validation — S1 vs S2 (2026-08-24, per #425 evidence)

**Established empirically by #425 (closed 2026-08-23):** the two dispatch surfaces load different plugin sets, so mechanism (a) — OpenCode `tool.execute.before` plugin interception — is **surface-dependent**.

| Property | S1 — opencode2 beta TUI | S2 — fork CLI 1.18.13-pp3g |
|---|---|---|
| Plugin loading | Global fallback plugins only (`plugins/plugin.ts`, `plugins/interrupt.ts`); **worktree `.opencode/plugins/` guards NOT loaded** (`orchestrator-guard`, `crosslink-guard`, `rtk-guard` absent from v2 debug config) | Worktree `.opencode/opencode.json` loaded; all 3 plugins active — proven by runtime logs (guard ALLOW for builder `filesystem_write_file` 19:25:27; BLOCK for auditor 19:16:48) |
| Permission model | `{action, resource, effect}` shape; filesystem access routed through code-mode **execute sandbox** (`tools.filesystem.*` inside tool=execute), not discrete `filesystem_*` permission keys | `permission/pattern` Wildcard matcher; MCP tools evaluated with same engine as bash (degenerate pattern dimension `"*"`) |
| Frontmatter `filesystem_*` keys | Silently ignored (never evaluated) | Honored via Wildcard match |
| Default with no explicit entries | ALLOW on both surfaces (global `* allow` first rule) | ALLOW (same) |

**Consequences for this matrix:**

1. Every row enforced by an OpenCode plugin is re-classified **[S2]**: enforcement is real and log-proven on S2, and **absent on S1**. An agent dispatched through S1 gets prompt-level discipline only for those rules.
2. Claude Code hooks, the systemd watcher, shell wrappers, and crosslink CLI checks are **[surface-independent]** — they do not depend on OpenCode plugin loading.
3. New S2-side gap found by #425: `orchestrator-guard.ts` BLOCKED_TOOLS omits `filesystem_create_directory` and `filesystem_move_file` — an orchestrator can create/move files via MCP even on S2 (frontmatter deny would cover the permission layer; guard logging gap remains). The #434 narrow `.kickoff-status` write exemption (closed 2026-08-23) is a refinement of the same guard.
4. S1 coverage for write-path protection requires either a v2-side guard equivalent intercepting `tools.filesystem.*` inside execute, or an `execute` deny (too broad), or v2 parity work. No such mechanism exists today.

**Per-row surface tags** are applied inline below and consolidated here:

| Enforced rule (Summary #) | Mechanism | S1 validity | S2 validity |
|---|---|---|---|
| 1 Orchestrator write blocking (`orchestrator-guard.ts`) | (a) | ❌ not loaded | ✅ log-proven (+#434 marker exemption) |
| 2 Git push blocked (`crosslink-guard.ts`) | (a) | ❌ not loaded | ✅ |
| 3 Git merge blocked workers | (a) | ❌ not loaded | ✅ |
| 4 Git merge gated orchestrator | (a) | ❌ not loaded | ✅ |
| 5 Git commit gated active issue | (a) | ❌ not loaded | ✅ |
| 6–9 Comment discipline / active-issue / kill-pause flags | (a) | ❌ not loaded | ✅ |
| 10 RTK rewriting (`rtk-guard.ts`) | (a) | ❌ not loaded | ✅ |
| 11 Heartbeat (`heartbeat.py`) | Claude Code hook | ✅ surface-independent | ✅ |
| 12 Lifecycle watcher (`kickoff-notify.py`) | systemd (d) | ✅ surface-independent | ✅ |
| NEW 13 Model validation (`claude` wrapper) | (d) | ✅ surface-independent | ✅ |

---

## Existing Hook Infrastructure

**Verified:** 3 OpenCode plugins [S2-only] + 2 Claude Code hooks + 1 systemd watcher + 1 tmux watchdog loop + 1 launch wrapper (updated 2026-08-24 per #440; plugin loading divergence per #425)

| Category | File | Runtime | What it enforces | Surface validity |
|----------|------|---------|-----------------|------------------|
| **OpenCode plugin** | crosslink-guard.ts | OpenCode `tool.execute.before` | Blocked git commands, gated git (active issue), comment discipline, active-issue enforcement, kill/pause flags, allowed bash | **[S2]** — not loaded on S1 (#425) |
| **OpenCode plugin** | orchestrator-guard.ts | OpenCode `tool.execute.before` | Write/edit blocked for non-Builder agents (SOLE enforcer — see §1.1 correction); narrow `.kickoff-status` write exemption for read-only roles (#434) | **[S2]** — not loaded on S1 (#425) |
| **OpenCode plugin** | rtk-guard.ts | OpenCode `tool.execute.before` | Transparent RTK command rewriting | **[S2]** — not loaded on S1 (#425) |
| **Claude Code hook** | heartbeat.py | Claude Code PostToolUse | Agent heartbeats on 120s throttle | surface-independent |
| **Claude Code hook** | crosslink_config.py | Claude Code PreToolUse/PostToolUse | Shared config, crosslink binary resolution | surface-independent |
| **systemd watcher** | tools/kickoff-notify.py | systemd timer (**15s interval**, `ases-kickoff-notify.timer`) | Agent lifecycle monitoring (LAUNCHING→RUNNING→DONE/FAILED), STALLED detection (heartbeat-stale floor 900s scaled by timeout/2, debounced ×2 scans, 300s grace; timeout-overrun fallback), notify-send + webhook. No task-length/decomposition assessment. | surface-independent |
| **tmux watchdog loop** | scripts/liveness-watchdog.sh (v2, live) | detached tmux session, 120s cycle | Runs agent-liveness.py --json --all; JSONL log; verdict-diff flags (new/worsened/vanished LIKELY-FROZEN / STALE-SUSPECT / SESSION-GONE) posted to issue #429 with dedup + recovery memory. No opencode.log parsing → no quota-parking detection. | surface-independent |
| **launch wrapper** | ~/.local/bin/claude | bash pre-dispatch | STRICT model validation: FATAL exit on missing/`opus`/`sonnet`/`haiku` model args; systemd-run memory scope in tmux; exports CROSSLINK_AGENT_TYPE. Does NOT verify model against live catalog (`opencode models`). | surface-independent |

---

## §1 Division of Labor — Non-Negotiable

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Orchestrator never implements (no write/edit on orchestrator) | Yes | (a) | `orchestrator-guard.ts` blocks write/edit/apply_patch for non-Builder agents at `tool.execute.before`. #425: guard NOT loaded on S1 (global-fallback plugins only). #434: narrow `.kickoff-status` write exemption added. S2 gap: BLOCKED_TOOLS omits filesystem_create_directory/move_file. | ✅ HOOK [S2] — `orchestrator-guard.ts` (SOLE enforcer); ❌ S1 unenforced |
| Orchestrator never reviews own work | No | (e) | Requires understanding whether a review is of the agent's own output — semantic judgment, not syntactic | ❌ |
| Orchestrator never silently takes over failed agents | No | (e) | Requires detecting intent to retry/substitute — semantic understanding of agent behavior | ❌ |
| Workers never plan, review, or merge to master | Partial | (a)+(c) | Workers already blocked from merge/push by `crosslink-guard.ts`. Planning is a model-level instruction; reviewing is blocked by permission model (reviewer/auditor subagents only). #425: plugin not loaded on S1. | ✅ BOTH [S2] — HOOK: git push/merge blocked (`crosslink-guard.ts`); PERMISSION: task deny (`permissions.md`); ❌ S1: permission-model layer only |
| Operator never handed code to read/write | No | (e) | This is a human-role discipline — not applicable to hook enforcement | ❌ N/A (human role) |

---

## §2 Choose Your Tier — Kickoff vs Swarm

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Do not swarm what a single kickoff can do | No | (e) | Requires assessing feature size/complexity — human judgment | ❌ |
| Do not kickoff a multi-phase feature serially | No | (e) | Same — requires understanding the feature decomposition | ❌ |
| Prove serially, then fan out | No | (e) | Requires tracking whether a pattern has been proven — stateful reasoning | ❌ |
| Task tool ≠ orchestration tier (§2.1) | Partial | (a)+(e) | Could detect Task tool calls on orchestrator and block/warn, but enforcement requires understanding whether the call is "implementation" vs "read/research" — partially hookable via pattern matching on task descriptions, but fragile | ❌ Mostly |
| NEVER use Task tool for implementation | Partial | (a) | Could block `task` tool calls from orchestrator entirely, but that would break legitimate read/research uses. Could warn but not hard-block. | ❌ |
| NEVER use Task tool for review verdicts | No | (e) | Requires understanding the semantic content of the task request | ❌ |
| NEVER use Task tool for anything requiring durable worktree/commit | No | (e) | Same — semantic content judgment | ❌ |

---

## §3 Model Selection — Mandatory Explicit Pin

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Every kickoff/swarm command MUST include `--model` | Yes | (c)+(d) | **Re-classified 2026-08-24 (#440): PARTIALLY ENFORCED.** The `~/.local/bin/claude` launch wrapper FATAL-exits on missing/implicit Anthropic models (`opus`/`sonnet`/`haiku`) before opencode runs — mechanism (d), surface-independent. Gap: `crosslink kickoff run` itself does not check; a dispatch path bypassing the wrapper would not be caught. | ✅ PARTIAL HOOK — `claude` wrapper strict validation (d); CLI-level check still buildable |
| Verify model against live catalog before dispatch | Partial | (c)+(d) | Could shell-wrap `crosslink kickoff run` to first run `opencode models <provider>` and check the model ID exists. But requires knowing the provider — partial. **#440 finding: the claude wrapper does NOT do this** — it accepts any non-Anthropic string (e.g. a typo'd model ID passes the wrapper and fails only at stream time). Catalog verification remains entirely prompt-enforced. | ❌ Could build — confirmed gap |
| HALT if model unreachable (no silent fallback) | No | (e) | Requires understanding whether a fallback occurred — semantic agent behavior | ❌ |
| Do not use `claude-mode` CLI wrappers | Yes | (d) | A shell wrapper could detect and block `claude-mode` invocations | ❌ Could build |
| Free Zen models: verify they launch and complete promptly | No | (e) | Requires monitoring runtime behavior — too complex for a pre-hook | ❌ |
| Fall back to paid Go on rate-limit symptom | No | (e) | Runtime monitoring + decision — not hookable | ❌ |

---

## §4 Pre-Flight Checklist

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| 1. HEAD is clean and on expected branch | Yes | (c)+(d) | A pre-dispatch hook (shell wrapper or crosslink CLI) could run `git status --porcelain` and block if dirty. Could also check branch. | ❌ Could build |
| 2. Target model is accessible (`opencode models`) | Yes | (c)+(d) | Shell wrapper could run the check before dispatching | ❌ Could build |
| 3. Crosslink issue exists and is claimed | Yes | (c) | Crosslink CLI could verify issue claim before allowing `kickoff run` / `swarm launch` | ❌ Could build (already partially enforced — active-issue gate blocks commits, but not dispatch itself) |
| 4. Worktree directory is clean (no orphan `.kickoff-status`) | Yes | (c)+(d) | `crosslink kickoff cleanup --force` could be auto-run before dispatch, or a check could verify no orphans exist | ❌ Could build |
| 5. Feature branch does not already exist | Yes | (c)+(d) | Shell wrapper could check `git branch --list feature/<name>` before dispatch | ❌ Could build |
| 6. Prompt includes acceptance criteria, scope boundaries, commit convention | No | (e) | Requires understanding prompt content — semantic | ❌ |

---

## §5 Dispatch Protocol

### §5.1 Single-Agent Kickoff

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Print tmux attach command for operator | No | (e) | This is a guidance instruction for the model — "print X for the user" | ❌ |
| Record dispatch breadcrumb: `crosslink session action` | Partial | (c) | Could be auto-triggered by `crosslink kickoff run` inside the CLI itself — append a session action on successful dispatch | ❌ Could build |
| Do NOT poll obsessively (every 5-10 min) | No | (e) | Model behavior guidance | ❌ |
| Watch for checkpoint comments (missing = stalled) | No | (e) | Requires monitoring ongoing state — the watcher (§6.4) handles this, but the watcher itself is not a hook | ❌ |

### §5.2 Multi-Agent Swarm

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| One phase at a time (run `swarm gate` between phases) | Partial | (c) | Crosslink CLI could enforce gate-before-launch-next-phase sequencing | ❌ Could build |
| Budget windows are hard limits (agents terminated) | Partial | (c) | Crosslink CLI could enforce budget-window timeout enforcement (may already partially exist in swarm implementation) | ❌ Could build |
| Phases depend on each other (`blocked_by` edges) | Partial | (c) | Crosslink CLI could verify `blocked_by` edges before allowing phase launch | ❌ Could build |

### §5.3 Task-Matched Timeout Guidance

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Timeouts MUST be task-matched, never blanket 1h | Partial | (c)+(d) | Crosslink CLI could reject `--timeout 1h` (or >30m for non-complex tasks) on `kickoff run`. Or a shell wrapper could enforce. Requires knowing the task type to enforce correctly — so partial. | ❌ Could build |
| Two-signal stalled detection (timeout exceeded + no commit for >2x budget) | Partial | (c) | Crosslink CLI could implement the rate-clock check internally — compare last commit timestamp against expected interval. The watcher (§6.4) partially does this. | ✅ PARTIAL HOOK — §6.4 watcher |
| Checkpoints do NOT justify long timeout | No | (e) | Process discipline — model reasoning about timeout selection | ❌ |

### §5.4 Progress-Feedback Contract — Mandatory Checkpoint Comments

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Post `--kind observation` checkpoint comments at milestones | Partial | (a)+(c) | Could detect missing checkpoints via `crosslink session status` and inject a reminder/warning. A crosslink CLI hookpoint could check last checkpoint timestamp against budget. | ❌ Could build |
| Durability cadence (~5 min budget, role-aware) | Partial | (c) | Crosslink CLI could track time since last sync and warn/block if >5min without activity. Feasible but complex. | ❌ Could build |
| Use scannable prefix (`[PROGRESS] state=...`) | Partial | (c) | Crosslink CLI could validate checkpoint comment format before accepting it | ❌ Could build |
| Sync after posting (`crosslink issue comment ... && crosslink sync`) | Yes | (c) | Crosslink CLI could auto-sync after every `issue comment` call — or enforce that sync follows comment. | ❌ Could build |
| Missed check-in escalation (investigate after 2x budget) | No | (e) | Requires ongoing monitoring + judgment about when to escalate — the watcher handles mechanical detection but escalation is orchestrator judgment | ❌ |
| Task-awareness (<=10m trivial: midpoint optional) | No | (e) | Requires understanding task complexity to decide milestone cadence | ❌ |
| Session-action breadcrumbs are SUPPLEMENTARY only | No | (e) | Model guidance — "dont rely on X as progress signal" | ❌ |

### §5.5 Two-Repo Sync Requirement

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Changes to shared files MUST be mirrored to both repos | Partial | (c)+(d) | Could build a post-commit hook that detects changes to the shared file list and reminds/warns if only one repo was updated. But requires awareness of both repos. | ❌ Could build (reminder only) |
| Durability-cadence changes must be mirrored (§5.5 active amendment) | Same as above | Same | Same feasibility | ❌ |

### §5.6 Reviewer Independence — Isolated Sub-Issues

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Each reviewer posts to OWN isolated sub-issue | Partial | (c)+(d) | Crosslink CLI could verify that `crosslink swarm launch --agent reviewer` targets a fresh sub-issue, not one with existing reviewer comments. Could detect shared-thread dispatch. | ❌ Could build |
| Never dispatch multiple reviewers onto same issue thread | Partial | (c) | Crosslink swarm could block launching multiple reviewer agents on the same issue ID without creating sub-issues first | ❌ Could build |

### §5.7 Thin-Orchestrator Rule — Bounded Signals Only

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Orchestrator consumes bounded signals only (no large volume reads) | Partial | (a)+(b) | Could detect large `cat`/`read`/`diff` commands and block or warn. The bash allowlist already limits what the orchestrator can run, but `cat <large-file>` is allowed. Could add a file-size check. | ❌ Could build (partial) |
| Delegate whole-file reads to subagents | No | (e) | Requires understanding whether a read is "whole file" vs "partial" — semantic | ❌ |
| Pipe-chain gotcha awareness | No | (e) | Known limitation, not enforceable | ❌ |

### §5.8 Workflow Topology — Position Store, Staleness, Auditor, Review-Before-Consume

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Position store: structured position updates to durable store | Partial | (c) | Crosslink CLI could validate checkpoint comment format (§5.4 format enforcement) | ❌ Could build |
| Claims carry certainty disclosure (WHY/WHAT/HOW-CERTAIN/WHAT-NOT-TESTED) | No | (e) | Requires understanding claim content — semantic model reasoning | ❌ |
| Idle floor <= budget (§5.8.1) | Partial | (c) | Crosslink CLI could reject idle intervals >5min in agent config | ❌ Could build |
| Completed claims MUST carry artifact/commit/test-log link | No | (e) | Requires parsing the comment content for evidence links — possible but fragile; semantic judgment about what counts as "evidence" | ❌ Fragile |
| Phase-1 auditor dispatched alongside builder | Partial | (c) | Crosslink swarm could auto-dispatch auditor when launching builder | ❌ Could build |
| Phase-2 auditor post-hoc, model-varied | No | (e) | Requires understanding model variation strategy — complex orchestration logic | ❌ |
| Review-before-consume gate | Partial | (c) | Crosslink swarm gate could require reviewer verdict before allowing consumption | ❌ Could build |
| Pre-positioned AUDITOR (launched alongside Builder) | Partial | (c) | Crosslink swarm could auto-launch auditor agent when builder starts | ❌ Could build |
| Cheap staleness trigger (>2x expected interval) | Partial | (c) | Crosslink CLI/watcher could implement timestamp comparison. §6.4 watcher partially does this. | ✅ PARTIAL HOOK — §6.4 watcher |
| Orchestrator as single integration point | No | (e) | Architectural principle — not hookable | ❌ N/A |

### §5.9 Decision-Gating Build Artifacts Must Be Committed

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Decision-gating artifacts MUST be committed before session end | Partial | (c)+(d) | Could build a session-end hook (PostToolUse on session_end or a pre-exit hook) that checks for uncommitted artifacts in /tmp or worktree. Fragile — requires knowing whats "decision-gating". | ❌ Could build (fragile) |
| Treat /tmp as scratch, never home of decision-gating artifacts | No | (e) | Semantic understanding of what constitutes a decision-gating artifact | ❌ |
| Cleanup guards must never destroy uncommitted build state | Partial | (c) | `crosslink kickoff cleanup` could check for uncommitted changes before removing worktrees | ❌ Could build |

---

## §6 Monitoring and Verification

### §6.1 Status Checks

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Never trust status flags alone (.kickoff-status) | No | (e) | Model guidance — "verify against git commits, not flags" | ❌ |
| The durable primitive is ground truth (commits for builders, synced positions for read-only) | No | (e) | Conceptual principle | ❌ |
| Checkpoint comments are the progress signal | No | (e) | Conceptual principle | ❌ |
| Distinguish STALLED from WORKING (ps -o pid,etime,time,stat) | No | (e) | Requires runtime monitoring + judgment | ❌ |

### §6.2 Output Verification

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Verify output is non-empty | Partial | (c)+(d) | Could build a post-agent hook that checks agent output length and halts on empty/blank review. Crosslink CLI could verify agent output before returning. | ❌ Could build |
| Run deterministic verification (never LLM-based for safety gates) | No | (e) | Requires understanding whether verification is LLM-based vs deterministic — semantic | ❌ |
| Build from main checkout (not worktree) | No | (e) | Requires understanding the build context — semantic | ❌ |
| Verify against hub agent refs, not local DB | No | (e) | Requires understanding the verification target — semantic | ❌ |

### §6.3 The Micro-Gate (Per-Issue)

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| PASS with zero findings → close issue | Partial | (c) | Crosslink CLI could require a `--kind result` comment with zero findings before allowing `issue close` — partially enforced by comment discipline on close | ✅ PARTIAL HOOK — comment discipline |
| FAIL or any finding → fix and re-review | No | (e) | Requires understanding review verdict content — semantic | ❌ |
| Empty/silent review → CRASH protocol | Partial | (c) | Crosslink CLI could detect empty review output and trigger halt. Could check comment body length. | ❌ Could build |

### §6.4 Agent Lifecycle Watcher — Phase 1

*Surface re-validation 2026-08-24: systemd watcher rows are **[surface-independent]** — they monitor worktree files, not OpenCode plugin state, so they remain fully valid on S1 and S2 alike (#425 does not affect them).*

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| systemd timer runs every 15s | Yes | (d) | Already implemented — `ases-kickoff-notify.timer` + `tools/kickoff-notify.py` | ✅ HOOK — `kickoff-notify.py` (systemd) |
| LAUNCHING → RUNNING → DONE \| FAILED \| CI_FAILED state machine | Yes | (d) | Already implemented in watcher | ✅ HOOK — `kickoff-notify.py` |
| STALLED detection (heartbeat stale, 2 consecutive detections) | Yes | (d) | Already implemented. Threshold = max(900s floor, timeout_secs/2), debounced ×2 scans after 300s grace; timeout-overrun fallback when heartbeat missing. Covers stall detection only — does NOT assess task-length atomization (see §14). | ✅ HOOK — `kickoff-notify.py` |
| notify-send + optional webhook | Yes | (d) | Already implemented | ✅ HOOK — `kickoff-notify.py` |
| No destructive action (monitor + notify only) | N/A | N/A | Design decision — Phase 1 is intentionally inert | ✅ By design |

### §6.5 Hub Refs Are Ground Truth

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| NEVER run `crosslink sync` in main repo to refresh visibility | Partial | (c) | Crosslink CLI could detect and warn/block `sync` when run from the main repo (not a worktree). Could check `git rev-parse --git-common-dir` vs `--git-dir`. | ❌ Could build |
| Read hub agent refs, not local DB | No | (e) | Conceptual principle | ❌ |

### §6.6 Standing Workflow — Agent Status Notes + Wave Cleanup

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Every orchestrator turn ends with Agent Status note | No | (e) | Model guidance — "end each turn with status" | ❌ |
| Run `crosslink kickoff cleanup` after each dispatch wave | Partial | (c)+(d) | Could be auto-triggered by crosslink CLI after swarm gate/close operations | ❌ Could build |
| Phase 1 watcher is supplement, not substitute | N/A | N/A | Conceptual principle | ❌ N/A |

---

## §7 Failure Protocol — MANDATORY HALT

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| On ANY delegation failure: STOP IMMEDIATELY | No | (e) | Requires understanding that a failure occurred and responding to it — agent behavior, not tool-call interception | ❌ |
| Do not retry, do not substitute, do not self-execute | No | (e) | Same — requires understanding intent to retry/substitute | ❌ |
| Report failure clearly to operator | No | (e) | Same — agent communication behavior | ❌ |
| REMAIN HALTED until operator responds | Partial | (b) | Could build a PostToolUse hook that detects agent output containing error/failure keywords and injects a "HALT" instruction. But fragile — requires understanding error semantics. | ❌ Fragile |

### §7.1 Crash Recovery

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| ps aux to confirm whats alive | No | (e) | Manual investigation step | ❌ |
| Let running workers FINISH (dont kill mid-commit) | No | (e) | Judgment call | ❌ |
| Kill stale workers, re-assert signing key | Partial | (c)+(d) | Could build a crash-recovery script that auto-re-asserts signing key | ❌ Could build (partial) |
| `crosslink kickoff cleanup --force` to release orphans | Partial | (c)+(d) | Could be auto-run on crash detection by the watcher | ❌ Could build |
| Relaunch from hub state, never trust in-context memory | No | (e) | Requires understanding what "hub state" contains — semantic | ❌ |

---

## §8 Signing Key Discipline

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Re-assert driver key before every kickoff/worktree cleanup | Yes | (c)+(d) | Crosslink CLI could auto-re-assert signing key on `kickoff run` / `cleanup`. Or a shell wrapper could `git config --worktree --get user.signingkey` check. | ❌ Could build |
| Re-assert after every crash | Partial | (d) | Shell wrapper or watcher could re-assert key on crash recovery | ❌ Could build |
| Verify with `git config --worktree --get user.signingkey` | Yes | (c)+(d) | Crosslink CLI could verify signing key before dispatching agents | ❌ Could build |

---

## §9 Worktree and Branch Management

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Workers commit to feature branches only | Yes | (a) | Could detect branch name in `git commit` and block commits to non-feature branches. `crosslink-guard.ts` already blocks merge/push; could add branch-name validation. Not loaded on S1 (#425). | ✅ HOOK [S2] — `crosslink-guard.ts` (git merge/push blocked); ❌ S1 unenforced |
| Never merge to master from worker | Yes | (a)+(c) | `crosslink-guard.ts` already blocks `git merge` for workers. Not loaded on S1 (#425). | ✅ HOOK [S2] — `crosslink-guard.ts` (git merge blocked); ❌ S1 unenforced |
| Push is operator-gated | Yes | (a) | `crosslink-guard.ts` already blocks `git push` for all agents. Not loaded on S1 (#425). #438 designs converting the hard block into a permission-ask popup — see §14. | ✅ HOOK [S2] — `crosslink-guard.ts` (git push blocked); ❌ S1 unenforced |
| One scope per session | No | (e) | Requires understanding scope — semantic | ❌ |

### §9.1 Operator Git Convention — No Interactive Editors

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Operator git commands MUST include `--no-edit` | Partial | (d) | Shell wrapper could inject `--no-edit` automatically or block commands without it | ❌ Could build |

---

## §10 Gate Discipline for Unmonitored Waves

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Workers commit to feature branches; orchestrator does NOT push | Yes | (a) | Already enforced by `crosslink-guard.ts` blocking push for all agents. Not loaded on S1 (#425). | ✅ HOOK [S2] — `crosslink-guard.ts`; ❌ S1 unenforced |
| Nothing merges unreviewed | Partial | (a)+(c) | Merge is gated on active issue for orchestrator (§1 crosslink-guard.ts). But "reviewed" vs "unreviewed" is semantic — the gate only checks issue active, not review status. | ✅ PARTIAL HOOK — active-issue gate on merge |
| Skeletons/structure can run unattended; fidelity-sensitive work HELD | No | (e) | Requires classifying work as "skeleton" vs "fidelity-sensitive" — semantic judgment | ❌ |

---

## §11 Verification Asymmetry

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Committed ≠ verified | No | (e) | Conceptual principle | ❌ N/A |
| BUILD/RENDER from main checkout where paths resolve | No | (e) | Requires understanding build context — semantic | ❌ |
| Run deterministic verification | No | (e) | Requires understanding what verification to run — semantic | ❌ |

---

## §12 Documentation and Handoff

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| End every session with `crosslink session end --notes "..."` | Partial | (c)+(d) | Crosslink CLI could enforce notes presence on session end. Could block `session end` without `--notes`. | ❌ Could build |
| Post milestone checkpoint comments during work (§5.4) | Partial | (c) | See §5.4 analysis above | ❌ Could build |
| Record breadcrumbs as supplementary telemetry | No | (e) | Model guidance | ❌ |
| Reference issues in commits: `feat: description [#N]` | Yes | (c)+(d) | Crosslink CLI or shell wrapper could validate commit message contains `[#N]` reference. Pre-commit hook. | ❌ Could build |
| Never edit STATUS.md directly | Yes | (a) | OpenCode plugin could detect writes to STATUS.md and block. Or git hook could detect changes to STATUS.md. | ❌ Could build |
| Design prompts so fresh orchestrator can rebuild from hub state | No | (e) | Requires understanding prompt quality — semantic | ❌ |

---

## §13 Anti-Patterns

| Anti-Pattern | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| Using Task tool for implementation | Partial | (a) | Could detect orchestrator `task` calls with implementation keywords and warn. But semantic — fragile. | ❌ Fragile |
| Omitting `--model` on kickoff | Yes | (c)+(d) | Shell wrapper or crosslink CLI could check `kickoff run` args for `--model` | ❌ Could build |
| Blanket `--timeout 1h` | Partial | (c)+(d) | Crosslink CLI could reject oversized timeouts for non-complex tasks | ❌ Could build |
| Using `claude-mode` CLI wrappers | Yes | (d) | Shell wrapper could detect and block | ❌ Could build |
| Accepting empty review output | Partial | (c) | Crosslink CLI could check review output length before accepting | ❌ Could build |
| Orchestrator implementing directly | Yes | (a) | ✅ Already enforced by `orchestrator-guard.ts` blocking write/edit for non-Builder — **[S2] only** (#425: not loaded on S1) | ✅ HOOK [S2] — `orchestrator-guard.ts` |
| Parallelizing unproven patterns | No | (e) | Requires understanding whether a pattern is "proven" — semantic | ❌ |
| Trusting `.kickoff-status` flags | No | (e) | Model guidance — "verify against git commits" | ❌ |
| Waiting silently until timeout | No | (e) | Model behavior guidance | ❌ |
| Relying session actions for operator visibility | No | (e) | Model guidance | ❌ |
| Dispatching multiple reviewers on one thread | Partial | (c) | Crosslink swarm could block multi-reviewer dispatch without sub-issue creation | ❌ Could build |
| Merging to master from worktree | Yes | (a)+(c) | ✅ Already enforced — git merge blocked for workers, gated for orchestrator — **[S2] only** (#425) | ✅ HOOK [S2] — `crosslink-guard.ts` |
| Retrying a failed delegation | No | (e) | Requires understanding intent to retry — semantic | ❌ |
| LLM-based sampling for safety gates | No | (e) | Requires understanding verification method — semantic | ❌ |
| Pushing from orchestrator | Yes | (a) | ✅ Already enforced — git push blocked for all agents — **[S2] only** (#425); #438 popup design would soften this into an informed operator transition (§14) | ✅ HOOK [S2] — `crosslink-guard.ts` |
| Trusting static permission/model doc | Partial | (d) | Could build a freshness check that runs `opencode models` and compares against doc | ❌ Could build |
| Reading agent output from local SQLite | No | (e) | Conceptual principle | ❌ |
| Running `crosslink sync` in main repo to refresh visibility | Partial | (c) | Crosslink CLI could detect and warn/block blind sync from main repo | ❌ Could build |
| Ending orchestrator turns silently | No | (e) | Model behavior guidance | ❌ |
| Skipping `crosslink kickoff cleanup` between waves | Partial | (d) | Could auto-run cleanup after dispatch waves | ❌ Could build |
| Leaving decision-gating artifacts in /tmp only | Partial | (c)+(d) | Session-end hook could check for uncommitted artifacts in /tmp | ❌ Could build (fragile) |

---

## §14 Doctrine Additions — 2026-08-23/24 Batch [#440]

New rules from the 2026-08-23/24 doctrine batch, classified with the same columns. These postdate the 2026-08-18 baseline and are integrated per #440.

| Rule/Mandate | Hookable? | Mechanism(s) | Notes/Feasibility | Enforcement |
|---|---|---|---|---|
| **Fetch-method-selection** (knowledge page: local fetch = substrate, WebFetch = query; never chain sequential WebFetch as bulk ingestion — four research-agent freezes on 2026-08-23 followed this pattern, evidence #429 termination records + #423 forensics) | Yes | (a) | Three-state WebFetch pattern guard designed in #439: allow first queries → ASK operator on bulk-ingestion pattern → deny+teach at excess; counter resets on local clone/curl acquisition. Purely syntactic signal (tool name + call sequence count) — well-suited to `tool.execute.before`. As a plugin it inherits the S1/S2 divergence: **[S2] only** unless a v2 equivalent is built. | ❌ DESIGN ONLY — #439 open, not implemented |
| **Git push-cadence** (AGENTS.md: agents proactively propose push moments — after merge clusters, before cleanup/migration ops, at session end) | Partial | (a)+(e) | Two separable layers. Detection of `git push` is mechanical and already hard-blocked [S2]. The *cadence* judgment (when proposing a push is appropriate) is semantic — (e). #438 designs the middle ground: intercept push via permission-ask action, render native y/n popup to operator with ahead-count context, converting the hard block into an informed human transition. Popup would be plugin-based → **[S2]**. | ✅ HOOK [S2] for the hard block (`crosslink-guard.ts`); cadence timing ❌ (e); popup ❌ DESIGN ONLY — #438 open |
| **Task-length atomization** (>~45m estimated sequential single-agent work = decompose into swarm rather than raise timeout; playbook §5.3) | Partial | (c)+(d) | Dispatch-time check is buildable: crosslink CLI or wrapper could reject/flag `kickoff run` timeouts >45m, or flag tasks whose prompts estimate long sequential work (the latter is semantic). Runtime coverage that ALREADY exists: `kickoff-notify.py` STALLED detection at 15s timer cadence catches heartbeat-stale agents and timeout-overrun (elapsed > timeout_secs + 120s buffer) — but this detects a *stalled over-long agent after dispatch*; nothing assesses or enforces decomposition at dispatch. The gap is preventive, not detective. | ❌ Could build (dispatch-time); runtime overrun detection exists via §6.4 watcher |
| **Never-assume-model** (verify model IDs against live catalog before use; never guess/shorten/modify) | Partial | (d)+(c) | **#440 finding: partially enforced already.** The `claude` launch wrapper FATAL-exits on missing/implicit Anthropic model names (verified in wrapper source) — mechanism (d), surface-independent. Remaining gap: the wrapper accepts any non-Anthropic string without checking `opencode models <provider>`; a typo'd or stale model ID passes and fails only at stream time. Catalog verification could be added to the same wrapper (cheap: one subprocess call). | ✅ PARTIAL HOOK — `claude` wrapper strict validation (d); catalog-check gap confirmed, buildable in same wrapper |
| **Quota-parking failure class** (agent silently parks retrying on provider quota exhaustion: `AI_APICallError: Resource exhausted` / HTTP 429 with future-retry semantics in `~/.local/share/opencode/log/opencode.log`) | Yes | (d) | Log signature verified present in the live opencode.log (#440 inspection: repeated `stream error ... AI_APICallError: Resource exhausted ... 429` entries). Detection is mechanical log-scan: match AI_APICallError + quota-exhaustion text + repeated timestamps per session → PARKED-RETRYING verdict. Integration candidate: scripts/liveness-watchdog.sh v2 (live, 120s cycle, already posts verdict flags to #429) — v3 could parse opencode.log alongside tmux pane state. Neither existing watcher (kickoff-notify.py, liveness-watchdog.sh) reads opencode.log today — confirmed gap. | ❌ GAP — no detector exists; watchdog v3 integration candidate |

---

## SUMMARY — Rules Already Enforced

**~13 rules with hook/plugin enforcement** (12 at 2026-08-18 baseline + claude-wrapper model validation added #440; corrected from ~15 per #404 FINDING 7):

| # | Rule | Enforcement Mechanism | Type | Surface |
|---|------|----------------------|------|---------|
| 1 | Orchestrator write blocking (§1.1) | `orchestrator-guard.ts` — blocks write/edit/apply_patch for non-Builder agents; `.kickoff-status` exemption per #434 | HOOK | **[S2]** |
| 2 | Git push blocked (§9.2/§10.1/§13.15) | `crosslink-guard.ts` — blocked_git_commands | HOOK | **[S2]** |
| 3 | Git merge blocked for workers (§9.1) | `crosslink-guard.ts` — by_type.blocked_git_commands | HOOK | **[S2]** |
| 4 | Git merge gated on active issue for orchestrator (§9.3) | `crosslink-guard.ts` + hook-config.json by_type.gated_git_commands | HOOK | **[S2]** |
| 5 | Git commit gated on active issue (§10.1) | `crosslink-guard.ts` — gated_git_commands + active-issue sentinel | HOOK | **[S2]** |
| 6 | Comment discipline: plan comment before commit (§5.4) | `crosslink-guard.ts` — comment_discipline check | HOOK | **[S2]** |
| 7 | Comment discipline: result comment before close (§6.3) | `crosslink-guard.ts` — issue close detection | HOOK | **[S2]** |
| 8 | Active-issue enforcement for writes (§13.15) | `crosslink-guard.ts` — strict mode blocks write/edit/bash without active issue | HOOK | **[S2]** |
| 9 | Kill/pause flags (§7) | `crosslink-guard.ts` — highest-priority check | HOOK | **[S2]** |
| 10 | RTK command rewriting (§8) | `rtk-guard.ts` — tool.execute.before, transparent rewrite | HOOK | **[S2]** |
| 11 | Heartbeat/liveness tracking (§6.4) | `.claude/hooks/heartbeat.py` — PostToolUse, throttled 120s | HOOK (Claude Code) | surface-independent |
| 12 | Agent lifecycle watcher (§6.4) | `tools/kickoff-notify.py` — systemd timer (15s), monitor + notify only | HOOK (systemd) | surface-independent |
| 13 | Implicit/default model rejection (§3) | `~/.local/bin/claude` wrapper — FATAL exit on missing/opus/sonnet/haiku (#440) | HOOK (shell wrapper) | surface-independent |

**Additionally enforced via permission model (NOT hooks):**
- Task deny for orchestrator/worker (permissions.md edit:deny, task:deny)
- Bash allowlist for orchestrator (hook-config.json agent_overrides)

These are permission-model constraints (permissions.md, hook-config.json), not hook/plugin enforcement. They were previously counted in the "~15" figure — this overstatement is corrected per #404 FINDING 3 and 7.

**Surface caveat (#425, applied #440):** all `[S2]` rows are unenforced on the S1 opencode2 beta TUI, which loads global-fallback plugins only. S1 dispatches rely on prompt discipline plus the surface-independent rows (11–13) for structural enforcement.

---

## SUMMARY — Highest-Value Hookable Rules Not Yet Enforced

These are the rules where hook enforcement would provide the most value (high failure frequency, low implementation cost). **Top-3 re-ranked 2026-08-24 (#440) against the night's failure classes** (agent freezes: native-stream ×2 + kickoff freeze ×1 on ox-alpha; WebFetch bulk-ingestion freezes #429/#423; quota-parking 429s confirmed in opencode.log):

1. **§14 Quota-parking PARKED-RETRYING detector** — extend `scripts/liveness-watchdog.sh` (v3) to parse `~/.local/share/opencode/log/opencode.log` for AI_APICallError/quota-exhaustion signatures and emit a PARKED-RETRYING verdict alongside existing tmux-pane verdicts. Directly addresses tonight's silent-parked agents that look alive but make no progress. **Mechanism: (d), LOW effort — watchdog loop and flag channel already live.**

2. **§14 Fetch-method-selection three-state guard (#439)** — WebFetch sequence counter in a `tool.execute.before` plugin: allow first queries, ASK on bulk-ingestion pattern, deny+teach at excess. Addresses the documented four-freeze ingestion pattern. **Mechanism: (a), LOW-MEDIUM effort — design exists; [S2]-only until v2 parity.**

3. **§14 Never-assume-model catalog verification** — add one `opencode models <provider>` subprocess check to the existing `claude` wrapper so typo'd/stale model IDs fail at dispatch with a clear message instead of at stream time. Complements the wrapper's existing implicit-model block. **Mechanism: (d), LOW effort — wrapper already exists and is the enforcement point.**

Remaining high-value items from the 2026-08-18 baseline:

4. **§4 Pre-flight checks (HEAD clean, issue claimed, branch not exists)** — Crosslink CLI pre-dispatch validation. Prevents wasted agent launches. **Mechanism: (c)+(d), LOW effort.**

5. **§5.3 Timeout validation / task-length atomization** — Crosslink CLI could reject blanket `--timeout 1h` and flag >45m sequential estimates for decomposition (§14). Prevents operator starvation of feedback. **Mechanism: (c), LOW effort.**

6. **§12 Issue reference in commits** — Pre-commit hook validating `[#N]` in commit message. **Mechanism: (c)+(d), LOW effort.**

7. **§12 `crosslink session end --notes` enforcement** — Block session end without notes. **Mechanism: (c), LOW effort.**

8. **§8 Signing key re-assertion** — Auto-re-assert before dispatch. **Mechanism: (c)+(d), MEDIUM effort.**

9. **§5.5 Two-repo sync reminder** — Post-commit hook detecting shared-file changes. **Mechanism: (d), MEDIUM effort.**

10. **§6.5 Blind-sync prevention** — Block `crosslink sync` from main repo. **Mechanism: (c), LOW effort.**

11. **§5.9 /tmp artifact check** — Session-end hook checking for uncommitted decision-gating artifacts. **Mechanism: (c)+(d), MEDIUM effort (fragile).**

12. **§5.6 Multi-reviewer isolation** — Crosslink swarm enforces sub-issue creation. **Mechanism: (c), MEDIUM effort.**

13. **§14 Git push-ask popup (#438)** — Convert the S2 hard block into a permission-ask popup with ahead-count context. Valuable but operator-workflow-changing; sequenced after the failure-class detectors above. **Mechanism: (a), MEDIUM effort — design exists.**

---

## What CANNOT Be Hooked (Requires Model Reasoning)

~40% of playbook rules are inherently non-hookable because they require understanding intent, semantics, or context:

- All "why its dangerous" rationale rules (the model must understand the danger)
- All "correct behavior" substitution rules (the model must choose the correct alternative)
- Tier selection judgment (kickoff vs swarm vs sentinel)
- Timeout estimation by task type
- Prompts with acceptance criteria
- Distinguishing skeleton from fidelity-sensitive work
- Whether a pattern is "proven"
- Whether work is "decision-gating"
- All failure-response behavior (halt, report, wait)

These remain prompt-enforced discipline and cannot be structurally guaranteed.

---

**Post-#404 Correction Notes:** This matrix applies the 4 factual corrections from the #404 audit verdict. The matrix's value as a hookability audit is intact — the corrections address factual accuracy, not structural flaws. Key changes: (1) infrastructure table now distinguishes 3 OpenCode plugins from 2 Claude Code hooks + 1 systemd watcher; (2) §1.1 orchestrator write blocking correctly attributed to orchestrator-guard.ts alone; (3) all "already enforced" items now labeled HOOK, PERMISSION, or BOTH; (4) hook-enforced count corrected to ~12 (10 direct + 2 infra).

**Post-#440 Extension Notes (2026-08-24):** Surface re-validation per #425 supersedes the surface-neutral framing above: the 3 OpenCode plugins are [S2]-only, so the effective structural-enforcement count on S1 is 3 (rows 11–13), not 13. §14 adds the 2026-08-23/24 doctrine batch. Scope addendum on #440 (2026-08-24 01:14) explicitly defers #442 (Observer role) and #441 (ases-tools CLI) classification to a follow-up pass — they are intentionally absent from this revision.

---

## Source / Provenance

- **Primary source:** Corrected inventory result comment on issue #391 (2026-08-18 16:51) — "## CORRECTED INVENTORY (post-#404): Agent Orchestration Playbook Hookability Audit"
- **Original inventory:** Issue #391 result comment (2026-08-18 06:06) — "## FULL INVENTORY: Agent Orchestration Playbook Hookability Audit"
- **Corrections applied from:** Issue #404 audit verdict (CONDITIONAL PASS) — 4 factual corrections
- **File creation:** Issue #410 — repository document promoted from issue comment to registry file
- **Session:** 2026-08-18, pp3g-0WU8 (builder agent) + orchestrator
- **2026-08-24 extension:** Issue #440 — surface re-validation evidence from #425 (closed); doctrine-batch sources: fetch-method-selection knowledge page + #439 design, AGENTS.md push-cadence rule + #438 design, playbook §5.3 atomization rule, model-discipline rules + `claude` wrapper inspection, opencode.log quota-parking signatures; watcher/watchdog source inspection (`tools/kickoff-notify.py`, `scripts/liveness-watchdog.sh`, `tools/ases-kickoff-notify.timer`); session pp3g-w9QQ (builder agent, relaunch of frozen predecessor)

---

## Maintenance

### Update Protocol

1. **After playbook changes:** review affected rules and update hookability classifications.
2. **After hook implementations:** update the "Enforcement" column for newly enforced rules.
3. **Quarterly review:** comprehensive review of all entries; verify enforcement status; retire outdated entries.
4. **After incidents:** if a failure reveals a rule that should have been hookable, add a new entry.

### Version History

| Date | Change | Author |
|------|--------|--------|
| 2026-08-18 | Initial creation from #391 corrected inventory (post-#404) | pp3g-qO5v + orchestrator |
| 2026-08-24 | #440 extension: per-surface re-validation of all enforcement rows per #425 (S1 opencode2 beta does not load worktree plugins; [S2] tags applied); infrastructure table updated (liveness-watchdog.sh v2, claude wrapper, 15s timer detail); §14 added classifying the 2026-08-23/24 doctrine batch (fetch-method-selection #439 design, push-cadence #438 design, task-length atomization, never-assume-model partial hook found, quota-parking gap); priorities re-ranked against 2026-08-23/24 failure classes; enforced count 12→13 | pp3g-w9QQ (builder) + orchestrator |

---

## Relationship to Other Documents

- **Failure Matrix** — routes failures to required semantics; this matrix classifies playbook rules by hookability for the same implementation pipeline
- **Model Routing Matrix** — routes models to tasks; this matrix routes rules to enforcement mechanisms
- **Harness Capability Matrix** — evaluates harness capabilities; this matrix evaluates rule enforceability
- **Agent Orchestration Playbook** — the source document being classified; rules in the playbook are the rows of this matrix
- **Hook Implementation Priorities** — the downstream consumer; this matrix provides the input for hook implementation prioritization
