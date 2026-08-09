---
title: Agent Tooling and Permission Enforcement — Reviewed (Merged Claims + 8 Reviews)
program: EDASES
layer: Research
document_type: Report
status: Active
authority: Experimental
canonical_repository: edases

related_documents:
  - docs/research/agent-tooling-and-permission-enforcement.md   (the original, unmodified)
  - docs/research/review-inbox/agent-tooling-and-permission-enforcement-reviews.md  (5 external reviews, verbatim)
  - docs/research/Workflow Topology Design and Reasoning Record.md
  - .opencode/permissions.md
  - .crosslink/knowledge/model-discipline.md
  - .crosslink/knowledge/crosslink-fork.md
  - docs/ORCHESTRATOR.md

supersedes: []

last_updated: 2026-08-09
---

# Agent Tooling and Permission Enforcement — Reviewed

> **Purpose.** This document is the **merged, resolution-bearing successor** to
> `docs/research/agent-tooling-and-permission-enforcement.md` (commit
> `4cbae854`, issue #314). It reproduces the original system description,
> folds in **all 8 adversarial reviews** — 5 external (ChatGPT web chat,
> Claude Sonnet 5, GLM-5.2, Deepseek-v4-Pro, Qwen3.8 Max — pasted verbatim in
> `docs/research/review-inbox/agent-tooling-and-permission-enforcement-reviews.md`,
> commit `368cb6c6`) and 3 internal (luna #315, hy3 #316, kimi #317) — plus
> the Gemini-3.5-flash cross-reviewer synthesis (#319), and resolves each
> contested claim against the live sources.
>
> **Self-containment.** A fresh reviewer with **zero repository context** must
> be able to reason over this document without opening any other file. To that
> end: the system, its roles, software, enforcement layers, and concrete
> configuration facts are quoted inline (section 2); every reviewer finding is
> attributed (section 3); the underlying source facts the reviewers cited
> (config values, plugin behavior, runtime evidence) are quoted inline; and
> each disputed claim is resolved with an explicit **WHY / WHAT-NOT-TESTED**
> statement, per the project's reasoning-certainty principle (AGENTS.md).
> Do **not** assume the reader can open `.opencode/plugins/*.ts` or
> `hook-config.json` — the relevant facts are reproduced here.
>
> **Sources.** The original document and all reviews were re-verified against
> the live files, binaries, and runtime logs listed in section 7 on
> 2026-08-09. Where a fact could not be independently verified, it is marked
> **(unverified)** rather than asserted. Where a claim is a source-derived
> inference rather than a runtime observation, it is marked as such.
>
> **Status of the original.** The original document is **not modified**. Its
> claims are quoted here for resolution. This document supersedes it as the
> external-reviewable record.

---

## 1. Purpose and Scope

### 1.1 What this document is

This document merges three layers of content:

1. **The original claims** (from `agent-tooling-and-permission-enforcement.md`
   @ `4cbae854`) — a self-contained, current-state write-up of the agent
   tooling and permission-enforcement system used in the ASES repository,
   written for external review.
2. **The 8 reviewer findings** — each reviewer's position on every contested
   claim, with attribution.
3. **The resolution** — the corrected/confirmed statement after weighing the
   evidence, with the reasoning (WHY) and the explicitly untested remainder
   (WHAT-NOT-TESTED) for each claim.

### 1.2 Reader's guide

- **Section 2** reproduces the system description (roles, software stack,
  enforcement layers, config facts) with the countable corrections the
  reviewers established. A reader who knows the system may skim it; a
  zero-context reader should read it before section 3.
- **Section 3** is the core: the 12 contested claims, each with CLAIM /
  FINDINGS / RESOLUTION.
- **Section 4** is the cross-reviewer consensus summary (agreement matrix,
  highest-confidence findings, agreed MUST-FIX / SHOULD-CONSIDER lists).
- **Section 5** collects the security-property invariants proposed by the
  reviewers as forward-looking guidance.
- **Section 6** consolidates all reviewers' WHAT-NOT-TESTED items and open
  questions.
- **Section 7** is the verified-sources appendix, so every claim is checkable.

### 1.3 How the reviews were conducted

The 5 external reviews were produced by models with **zero repository access**
— they reasoned over the original document text alone (hence the repeated
demand for quoted evidence). The 3 internal reviews (luna #315, hy3 #316,
kimi #317) were produced by **read-only reviewer agents with full repository
access**, run independently (per the playbook §5.6 independence rule; hy3
explicitly did not read #315/#317). The Gemini-3.5-flash synthesis (#319)
tabulated all 8. This document re-verified the contested facts directly
against the live sources on 2026-08-09 (section 7), which is why several
resolutions below differ in detail from any single review.

---

## 2. System Description (from the original, verified)

> This section is the original document's system description with the
> countable and factual corrections the reviewers established. Where a
> correction is applied, it is flagged **CORRECTED** with a pointer to the
> relevant resolution in section 3.

### 2.1 The problem the system addresses

ASES runs a multi-agent software-engineering workflow in which an **operator**
(a human) supervises a small set of AI agents with distinct roles. The roles
are separated by **authority**: only one role may modify project files; the
other roles exist to verify, review, and coordinate. For this separation to be
meaningful, the enforcement must be **structural** — permissions enforced by
the tooling — rather than merely requested in prose. An agent that is told
"you are read-only" but is physically able to write files is not read-only.

**Reviewers' refinement (unanimous, 8/8):** "physically able to write files"
is only the direct-write leg of the guarantee. The reviewers distinguish three
increasingly strong properties: (A) **tool denial** — the reviewer cannot call
`write`; (B) **repository immutability** — the reviewer cannot modify
repository files by any means; (C) **authority isolation** — the reviewer
cannot cause another principal to modify repository files on its behalf
(ChatGPT). The evidence establishes parts of (A); it does not establish (B)
comprehensively and barely examines (C). This is the central finding of the
review set; see claim (a) in section 3.

### 2.2 The four-role permission model

Four agent roles are defined (`.opencode/opencode.json`,
`.opencode/agents/*.md`). The original table, with the corrections the
reviewers established:

| Role | Mode (opencode.json) | Mode (agent .md) | Writes files? | Git write | Job |
|------|----------------------|------------------|---------------|-----------|-----|
| **Orchestrator** | `primary` | `primary` | **No direct edit tools** (edit deny) — but can mutate repository state through gated `git commit`/`git merge` (CORRECTED per Qwen L-04) | `git commit` + `git merge` gated on an active issue; push/rebase/reset/clean/checkout/restore/stash/tag blocked | Plans, delegates via `crosslink kickoff`/`swarm`, coordinates the other three, maintains tracking state. Never implements, reviews, or audits. |
| **Builder** | `subagent` | `primary` | Yes (`edit: allow`, unrestricted `bash`) | `git commit` gated on an active issue; everything destructive blocked (in agent contexts) | Implements approved work, modifies project files. |
| **Reviewer** | `subagent` | `primary` | **No direct edit tools** (edit deny) — indirect paths exist via broad bash grants (see claim (a)) | all git writes blocked (in agent contexts) | Deep read-only review of implementation output; produces findings. |
| **Auditor** | `subagent` | `primary` | **No direct edit tools** (edit deny) — same indirect-path caveat | all git writes blocked (in agent contexts) | Project-level evaluation of outcome **and** process; independent of implementation and review. |

**CONTRADICTION FLAGGED BY hy3 (M6):** `.opencode/opencode.json` lines 10-25
declare `"mode": "subagent"` for builder, reviewer, and auditor; the agent
`.md` files (`builder.md` line 3, `reviewer.md` line 3, `auditor.md` line 3)
declare `mode: primary`. The original document reported only one side
(`.md`-style). Which value wins at runtime is **(unverified)** — a primary-mode
reviewer is directly launchable as a top-level session, which is precisely how
this review set was launched (hy3, WHAT-NOT-TESTED 8). See claim (a).

**CONDITIONAL CLAUSE FLAGGED BY hy3 (M4b):** the "all git writes blocked" row
is only true in **agent contexts**. crosslink-guard's `agent_overrides` branch
(including `tracking_mode: relaxed` and the per-role `by_type` git lists)
applies only `if (isAgent && config.agent_overrides)` where `isAgentContext`
requires `.crosslink/agent.json` role `"agent"` **or** a cwd containing
`/.claude/worktrees/` (`crosslink-guard.ts:239-258,395`). The main ASES repo's
`.crosslink/agent.json` has `"role": "driver"`, and this repository puts
worktrees under `.worktrees/`, not `/.claude/worktrees/` — so **in the main
repo the root `blocked_git_commands` applies, which does not contain
`git merge`**, and the statement "builder may not merge" (§1.4 of the
original) is false in that context. See claim (e)/(f).

### 2.3 Software stack

- **opencode (forked as `1.18.13-pp3g-fork`)** — the AI-agent harness/TUI.
  Loads agent definitions from `.opencode/agents/*.md`, enforces each agent's
  permission frontmatter, and provides tools (read/write/edit/bash/glob/grep/
  task/webfetch, MCP servers, etc.). `opencode --version` reports
  `1.18.13-pp3g-fork` (verified). The fork exists because of the **silent-hang
  reliability epic** (#156): stock opencode would hang on certain provider
  stream errors (a consumption deadlock in `llm.ts` — an
  `effect Stream.fromAsyncIterable` scope finalizer awaiting `iter.return()`).
  The fork's durable fix was a fire-and-forget `safeIterable()` return in
  `llm.ts` (commit `98dfe4a`), plus request-timeout configuration. **Reviewer
  caution (Sonnet 5):** this causal chain rests on the project's own
  investigation of itself; there is no external/upstream confirmation that
  stock opencode has this bug — the fork's justification, the topology's
  motivating example, and one §4 table row share this single internal source.
  The `98dfe4a` commit lives in the opencode fork tree, which was not among
  the original §7 sources (hy3 N5).
- **Separate session database.** The fork writes sessions to
  `opencode-fork-pp3g.db` in `~/.local/share/opencode/` via a baked-in channel
  name (`fork-pp3g` → `opencode-<channel>.db`). Stock history lives in
  `opencode.db`. This split was characterized in #313: the fork binary does
  not read the main DB. **Counts (verified 2026-08-09):** fork DB
  `1,213,251,584 B` (~1.13 GiB, ~90% dominated by a single session's event
  table per #313), main DB `2,598,903,808 B` (~2.42 GiB), `opencode-local.db`
  `1,081,344 B`. **hy3 N1 (unit nit):** the original wrote "~1.13 GiB" in one
  place and "~1.13 GB" in another for the same number
  (1,142,870,016 B = 1.064 GiB = 1.14 GB at #313 inventory time).
- **crosslink fork CLI (Rust)** — the issue tracker + agent-orchestration
  CLI: issues/comments with `--kind` semantics, sessions and locks, a durable
  hub for state sync, `kickoff run` and `swarm`, agent identity/signing, and
  the guard-hook configuration. **Version — CORRECTED (claim (c)):** the
  deployed binary reports `crosslink 0.9.0-beta.1+a87bd513` (verified via
  `crosslink --version`), while the source tree at
  `/home/claude-code/projects/crosslink` is at `v0.9.0-beta.1-59-g6221309e`
  (verified via `git describe --tags`). The original document conflated the
  two, presenting the source HEAD as the deployed version. Exactly one commit
  separates them: `6221309e` "feat(kickoff): add --base <ref> ...", which
  modifies `kickoff/launch.rs` (+59) and `kickoff/prompt.rs` (+12) — two of
  the three files the original §7 lists as verified sources. See claim (c).
- **The `claude` wrapper (bash)** — `~/.local/bin/claude`, ~86 lines,
  translates Anthropic-claude CLI arguments into `opencode run` invocations.
  Verified behaviors:
  - **Strict model enforcement:** rejects launches whose `--model` is missing
    or an implicit/default Anthropic name (`opus`/`sonnet`/`haiku`) with a
    fatal error; allowed providers printed as `opencode, opencode-go,
    google-vertex, nvidia` (wrapper lines 42-57).
  - **`--allowedTools` is consumed and dropped:** the wrapper's
    `--allowedTools) shift 2` case removes the flag and its value without
    forwarding anything (wrapper lines 28-30). `opencode run --help` exposes
    no `--allowedTools` flag (verified). See claim (b).
  - **`--auto` injection under tmux:** `if [[ -n "$TMUX" ]]; then
    ARGS+=("--auto"); fi` (wrapper lines 66-68) — unconditional for every
    tmux launch, which is every kickoff agent. `opencode run --help` describes
    `--auto` as "auto-approve permissions that are not explicitly denied
    (dangerous!)". The wrapper also maps `--dangerously-skip-permissions` →
    `--auto` (lines 21-24). See claim (h).
  - **Memory scoping:** inside tmux, `systemd-run --scope --user` with
    `MemoryMax`/`MemoryHigh` caps (`MEMORY_SCOPE` default 3G).
  - **Agent-type export:** when `--agent <type>` is present, exports
    `CROSSLINK_AGENT_TYPE=<type>`.
- **rtk (v0.40.0)** — CLI proxy at `~/.cargo/bin/rtk` that rewrites bash
  commands into lower-token forms (`rtk rewrite`, `rtk read`). Replaces Claude
  Code's native PreToolUse hook, which opencode cannot run.
- **sqlite3 databases** — listed in 2.5 of the original and above; the audit
  relevance of sqlite3 is claim (j).
- **Three in-repo guard plugins** (TypeScript, run in opencode's Bun runtime;
  loaded from `.opencode/opencode.json` plugin list, lines 4-8):

  | Plugin | File | Job (verified) |
  |--------|------|----------------|
  | **orchestrator-guard** | `.opencode/plugins/orchestrator-guard.ts` | Closes the #33677 gap: throws on `tool.execute.before` for `write`, `edit`, `apply_patch`, `filesystem_write_file`, `filesystem_edit_file` unless the resolved agent is `builder` (lines 33-41, `ALLOWED_AGENTS = {"builder"}`). No `CROSSLINK_AGENT_TYPE` env fallback (kimi). See claim (d). |
  | **crosslink-guard** | `.opencode/plugins/crosslink-guard.ts` (1220 lines) | Git discipline (blocked/gated lists), active-issue gating, bash allow-fast-path, issue-comment discipline, operator kill/pause flags, per-agent-type overrides. See claims (e), (f), and the 10-step flow in 2.4. |
  | **rtk-guard** | `.opencode/plugins/rtk-guard.ts` (415 lines) | Transparently rewrites eligible bash calls through `rtk rewrite`; strictly fail-open. Constants verified: `V1_VALIDATED = {git, ls, grep, find, diff, wc, cat}`, `LATENCY_SAMPLE_SIZE=200`, `LATENCY_P95_LIMIT_MS=15`, `LATENCY_RECHECK_CALLS=500`, `MIN_RTK_VERSION=0.40.0`, `RTK_DISABLED=1` opt-out. |

- **User-level model-whitelist plugin** — `~/.config/opencode/plugins/plugin.ts`
  (global to the machine, not scoped to ASES — Sonnet 5; see claim (l)):
  - disables and hides providers `openai`, `deepseek`, `cloudflare`,
    `cloudflare-ai-gateway` (empty their model maps; lines 9-27);
  - sets `opencode` provider whitelist to seven free Zen models:
    `big-pickle`, `deepseek-v4-flash-free`, `laguna-s-2.1-free`,
    `ling-3.0-flash-free`, `mimo-v2.5-free`, `nemotron-3-ultra-free`,
    `north-mini-code-free` (lines 28-35);
  - empties `vertex`'s model map (lines 36-38);
  - **then merges `~/.config/opencode/models-cache.json` for every provider
    without filtering disabled_providers** (lines 42-63) — the
    disabled-and-hidden claim is therefore not robust against cache state
    (luna SHOULD-CONSIDER, kimi SHOULD-CONSIDER); see claim (l).
  - **Live-catalog check:** `opencode models opencode` returns **six** models
    — `ling-3.0-flash-free` is in plugin.ts but absent from the live catalog
    (hy3 S2; verified 2026-08-09). By the project's own staleness rule
    (SESSION-START.md §1a), the seven-model whitelist claim is stale.

### 2.4 Enforcement layers, in call order

A tool call experiences the layers additively — it must survive every layer
that applies:

1. **opencode native permission engine** (agent `.md` frontmatter). Examples
   (verified verbatim from the current `.md` files):
   - **Orchestrator** (`orchestrator.md`): `edit: deny`; `bash` has
     `"*": "deny"` then **34** explicit allow patterns (CORRECTED from the
     original's "~40"; see claim (i)): `crosslink *`, `opencode models *`,
     `git status *`, `git diff *`, `git log *`, `git show *`, `git branch *`,
     `git commit *`, `git merge *`, `ls *`, `cat *`, `rtk *`, `sleep *`,
     `ps -o *`, `pgrep *`, `tmux list-sessions *`, `tmux capture-pane *`,
     `tmux display-message *`, `grep *`, `tail *`, `head *`, `wc *`,
     `stat *`, `diff *`, `free *`, `df *`, `uptime *`, `date *`, `which *`,
     `env *`, `git worktree list *`, `git -C *`, `curl -I *`,
     `curl --head *`; `task: {"*": "deny", "builder": "allow", "reviewer":
     "allow", "auditor": "allow"}`; `question: allow`; `webfetch: deny`;
     `websearch: deny`.
   - **Builder** (`builder.md`): `edit: allow`; `bash: allow` (unrestricted);
     `external_directory: {"*": "ask", "/tmp/*": "allow"}`; `task: deny`;
     `question: ask`; `webfetch/websearch: allow`. **Note (hy3 M7):** under
     `--auto` the `external_directory: ask` is auto-approved in the kickoff
     path, so `/tmp/*` vs `*` distinction is moot there (claim (h)).
   - **Reviewer** (`reviewer.md`): `edit: deny`; `bash`:
     `"crosslink *": allow`, `"opencode *": allow`, `"git *": allow`,
     `"ls *": allow`, `"cat *": allow`, `"cargo *": allow`, `"npm *": allow`,
     `"rtk *": allow` (everything else deny); `task: deny`; `question: deny`;
     `webfetch: allow`; `websearch: deny`.
   - **Auditor** (`auditor.md`): `edit: deny`; `bash`:
     `"crosslink *": allow`, `"opencode *": allow`, `"git *": allow`,
     `"ls *": allow`, `"cat *": allow`, `"rtk *": allow` — **no** `cargo *`
     or `npm *` (hy3 N2 / Qwen L-02: the original's "same bash shape as
     reviewer" is wrong; the auditor's surface is a subset); `task: deny`;
     `question: deny`; `webfetch: allow`; `websearch: deny`.
   - **The #33677 gap:** in opencode, `edit: deny` alone does **not** block
     native write/edit/`apply_patch` or MCP filesystem write tools — they
     succeed regardless. This is why orchestrator-guard exists (layer 2).
2. **orchestrator-guard plugin** — hooks `tool.execute.before`, throws for the
   five tool names unless agent is `builder`. Agent resolved per-sessionID
   from `chat.params`/`chat.message` (`agentBySession` map), falling back to a
   module `currentAgent` only when sessionID is absent; **no env fallback**
   (kimi). See claim (d) for the MCP tool-name question.
3. **crosslink-guard plugin** — on every `write`/`edit`/`bash` call, applies
   in priority order (verified against `crosslink-guard.ts` control flow):
   1. Operator kill/pause flags via `crosslink agent flags --strict`; exit
      code 2 with kill/paused throws a hard block. **Fails open when
      `crosslink` is unavailable or the dir is missing**
      (`if (!result) return; // crosslink not available or hung — fail open`,
      line 605) — Deepseek's kill-switch finding.
   2. `~/.claude/` write/edit exemption (Claude Code memory path;
      `isClaudeMemoryPath`, lines 539-549).
   3. **Blocked git commands** (from config, normalized; chained commands
      split on `" && "`, `" ; "`, `" | "` — note: only space-padded
      separators, not bare `&&`/`;`/`|` or other shell forms).
   4. **Gated git commands** (`git commit`): active issue via `.active-issue`
      sentinel fast path or `crosslink session status` slow path; under
      `comment_discipline`, a `--kind plan` comment (required blocks,
      encouraged reminds).
   5. Issue-close comment discipline (`--kind result` required/reminded).
   6. **Allowed bash pass-through:** if every sub-command matches
      `allowed_bash_prefixes`, early-return ALLOW (lines 1141-1147).
      **This is an allow-fast-path, not a denying surface** — see claim (e).
   7. **Relaxed mode:** `if (config.tracking_mode === "relaxed") return;`
      (lines 1152-1155) — any non-blocked, non-gated bash passes.
   8. No crosslink dir → allow.
   9. Active-issue enforcement: sentinel present → ALLOW even in strict mode
      (lines 1170-1181).
   10. No active work item: strict mode throws; normal mode reminds.
   - **Config source.** `.crosslink/hook-config.json` plus a
     `hook-config.local.json` overlay with `+key` array-extension
     (`loadConfigMerged`, lines 283-310; `mergeWithExtend`, lines 312-331).
     The original's "single config source" framing is overstated — the plugin
     also has hard-coded defaults (`DEFAULT_BLOCKED_GIT`, etc.) and behavior
     (luna SHOULD-CONSIDER, ChatGPT finding 14). See claim (l).
   - **Verified config values** (from `.crosslink/hook-config.json`):
     - `allowed_bash_prefixes`: **49 entries** (lines 127-177), not 29 —
       see claim (i).
     - `agent_overrides.blocked_git_commands`: **21 entries** (lines 15-37),
       not 19 — see claim (i).
     - root `blocked_git_commands`: **14 entries** (lines 179-194) — the only
       count the original got right.
     - `gated_git_commands: ["git commit"]` (root; lines 197-199) and
       `["git commit"]` for agents; orchestrator by_type also gates
       `git merge` (lines 65-68); reviewer/auditor by_type **block** `git
       commit` (lines 70-123).
     - `agent_overrides.tracking_mode: "relaxed"` (line 125);
       `tracking_mode: "strict"` root (line 232);
       `comment_discipline: "encouraged"` (line 195);
       `kickoff_verification: "local"` (line 201);
       `signing_enforcement: "audit"` (line 230);
       sentinel block lines 203-228: `enabled: false`,
       `default_agent.model: opencode-go/deepseek-v4-pro`,
       `escalation.model: claude-opus-4-6`.
     - **Stray flattened key (hy3 S3 / kimi SHOULD-CONSIDER):**
       line 229 carries `"sentinel.default_agent.model":
       "opencode/ling-3.0-flash-free"` — a free Zen model for agent work
       (contradicting §1.5 model discipline), naming an ID absent from the
       live catalog, dormant because `enabled: false`.
     - **No `kickoff` key** exists in this file (verified in both the worktree
       and the main repo config), so `read_kickoff_allowed_tools()` returns an
       empty list.
4. **rtk-guard plugin** — fail-open rewrite of eligible bash; see 2.3.
5. **The KICKOFF `--allowedTools` surface (fork-built, deployment-dormant)** —
   `launch.rs::build_agent_command` builds (for the `claude` agent binary):
   `timeout <backstop>s env -u CLAUDECODE <CLAUDE_CONFIG_DIR=...> claude
   [--permission-mode <mode> | --dangerously-skip-permissions] --model
   <model> --agent <type> --allowedTools '<list>' -- "$(cat KICKOFF.md)"`
   (launch.rs lines 255-311; the original's §3.6 template omitted the
   `skip_permissions`/`permission_mode`/`CLAUDE_CONFIG_DIR` parameters — hy3
   M7-adjacent). `build_allowed_tools(conventions, verify)` (prompt.rs
   lines 429-473) produces a 22-entry base list:
   `Read, Write, Edit, Glob, Grep, Skill, Task, WebSearch, WebFetch,
   Bash(git *), Bash(ls *), Bash(mkdir *), Bash(test *), Bash(which *),
   Bash(touch *), Bash(cat *), Bash(head *), Bash(tail *), Bash(wc *),
   Bash(diff *), Bash(echo *), Bash(crosslink *)`, plus `Bash(gh *)` and
   `Bash(sleep *)` when verify is `ci`/`thorough`, plus convention-detected
   project tools (`helpers.rs::detect_conventions`: Cargo.toml → cargo+clippy/
   fmt; package.json → npm/npx; pyproject.toml/requirements.txt → uv/python3/
   pytest; go.mod → go; justfile/Makefile; shell → shellcheck/bash/bats).
   `has_manifest` scans one directory level deep with a skip list
   (helpers.rs 122-190). **No `agent_type` parameter** — identical surface
   for all agent types (the per-type asymmetry finding, §5.2 of the original,
   which hy3 confirms as the strongest analytical result; P3).
   **Deployment status:** on the local tmux path the wrapper drops
   `--allowedTools` and opencode has no such flag (verified) — **but** the
   container path (`launch.rs` lines 1000-1035) invokes the agent binary
   inside Docker/Podman with `--allowedTools` passed **directly**, bypassing
   the host wrapper: `cd /workspaces/repo && timeout {backstop}s claude
   --model ... --agent ... --allowedTools '...' -- "$(cat KICKOFF.md)"`.
   The "constructed but not enforced" claim is therefore launch-mode-dependent
   (luna MUST-FIX, kimi MUST-FIX); see claim (b).
6. **MCP configuration** (`.opencode/opencode.json` lines 27-45): `github`,
   `playwright`, `sqlite` (an MCP `sqlite` server — `enabled: false`, hy3
   S4), `cloudflare` all disabled; `filesystem` **enabled** with
   `npx -y @modelcontextprotocol/server-filesystem
   /home/claude-code/projects/ASES` — rooted at the **main ASES repo, not the
   worktree** (hy3 S5). See claim (d).

### 2.5 Model discipline

Hard rules (`.crosslink/knowledge/model-discipline.md`): never assume a model
ID — verify with `opencode models <provider>`; ask the operator which
provider; do not use free-tier (Zen) models for agent/kickoff/swarm work;
distinguish 429/rate-limit from silent-hang. The wrapper enforces explicit
model IDs at launch (2.3). **Reviewer caveats:** the whitelist plugin's
seven-model claim is stale (six in the live catalog — hy3 S2); the sentinel
block's `claude-opus-4-6` carries no provider prefix and no enabled provider
(hy3 S3); free-tier failure space includes 401 auth class (verified: #313's
first auditor attempt `opencode/north-mini-code-free` failed with 401, not
429/hang).

### 2.6 Where the pieces live

```
ASES repo:
  .opencode/opencode.json            agent map, plugin list, MCP config
  .opencode/agents/{orchestrator,builder,reviewer,auditor}.md   permission frontmatter
  .opencode/plugins/{orchestrator-guard,crosslink-guard,rtk-guard}.ts
  .opencode/permissions.md           snapshot of the four role maps (STALE: says OpenCode 1.18.11; NOT source of truth)
  .crosslink/hook-config.json        guard config: bash allowlist, git lists, by_type overrides
  .crosslink/hook-config.local.json  optional +key overlay (may not exist)
  .crosslink/agent.json              role: "driver" in main repo; "agent" in agent worktrees
  .crosslink/.active-issue           sentinel (fast-path active issue; content: "320" here)
  .crosslink/knowledge/model-discipline.md
  docs/research/Workflow Topology Design and Reasoning Record.md

Outside the repo:
  ~/.local/bin/opencode               the pp3g fork (1.18.13-pp3g-fork)
  ~/.local/bin/claude                 bash wrapper → opencode run
  ~/.local/bin/crosslink              crosslink fork CLI (deployed 0.9.0-beta.1+a87bd513)
  ~/.cargo/bin/rtk                    rtk 0.40.0
  ~/.config/opencode/plugins/plugin.ts  user-level model whitelist (global)
  ~/.config/opencode/opencode.json   user-level request timeouts
  ~/.local/share/opencode/*.db        opencode session stores
  /home/claude-code/projects/crosslink  crosslink fork source (HEAD 6221309e)
```

---

## 3. Claim-by-Claim Review Findings

> Each contested claim has three subsections: **CLAIM** (the original
> statement, with section ref), **FINDINGS** (each reviewer's position with
> attribution and the strongest evidence cited), and **RESOLUTION** (the
> corrected/confirmed statement after weighing evidence, with WHY and
> WHAT-NOT-TESTED). Agreement counts are over the 8 reviewers (5 external +
> 3 internal), following the Gemini #319 tabulation where available.

### 3.1 Claim (a): "Reviewer and auditor are read-only by construction"

**CLAIM.** Original §1.2: "reviewer and auditor are **read-only by
construction**, and the enforcement is intended to make that a property of the
tooling, not a suggestion"; §1.1: "an agent that is told 'you are read-only'
but is physically able to write files is not read-only."

**FINDINGS.**
- **ChatGPT (Critical #1):** not established. The permission data gives
  reviewer/auditor `git *`, `cargo *` (reviewer), `npm *` (reviewer),
  `opencode *`, `crosslink *`, `rtk *`. That proves only direct
  editor/write-tool denial, not that the agent cannot mutate project state.
  `npm run <script>` executes arbitrary project-defined JavaScript; `cargo`
  can execute build scripts; `git *` plus a finite blocklist is not "git is
  read-only". Distinguishes A (tool denial) / B (repository immutability) /
  C (authority isolation); the evidence establishes parts of A, not B or C.
- **Qwen (C-01, Change 1):** overstated; "some write paths are blocked by
  configuration" is the accurate statement. Produces a table of git mutation
  classes (`git config` with `core.hooksPath`, `git worktree add`,
  `git archive --output`, `git checkout <branch> -- <path>`,
  `git restore <path>`, `git update-ref`, `git symbolic-ref`, `git add`,
  `git remote add evil ext::...` + fetch, etc.) and non-git primitives
  (`cargo build`, `cargo test`, `npm install`, `npm run`, `opencode *`,
  `crosslink *`, `rtk *`).
- **hy3 (M5, strongest technical evidence):** the original's own §1.1
  criterion falsifies the claim. orchestrator-guard blocks five tool names
  only; crosslink-guard blocks a list of git subcommands absent from which
  are `git checkout -- <file>`, `git restore <file>` (only `.` forms are
  listed), `git rm`, `git mv`, `git worktree add`. Most sharply:
  reviewer.md/auditor.md grant `opencode *`, and `opencode run --help`
  documents `--pure  run without external plugins` — so
  `opencode run --pure --agent builder ...` starts a nested session with
  **none of the three guard plugins loaded**, a single-command bypass of the
  plugin layer available to the two roles the doc calls read-only by
  construction. (`task: deny` closes the in-harness delegation path, not this
  one.)
- **GLM-5.2:** the "read-only illusion"; adds the default-to-builder race
  (see claim (f)) and interpreter trampolines (`python3 -c "import subprocess;
  subprocess.run(['git','push'])"` when `python3 *` is allowed).
- **Deepseek (#1, #4):** builder can dismantle enforcement (claim (g));
  orchestrator-guard doesn't parse bash, so shell redirection protection
  relies on rtk-guard's fail-open scan (claim (e)-adjacent).
- **Sonnet 5:** §5.3's sqlite3 exhibit treated as settled fact (claim (j)).
- **luna (MUST FIX):** "all git writes blocked"/"read-only by construction"
  overstates the reviewer/auditor contract; `.md` grants `git *`, the plugin
  blocks only configured finite prefixes; unlisted mutators such as
  `git update-ref`, `git branch -f`, `git config`, `git reflog expire` are
  not established as blocked. State the bounded blocklist guarantee (or
  add/test a deny-by-default git policy).
- **kimi (MUST FIX):** read-only is false confidence; the actual guarantees
  are weaker due to `--auto` under tmux, relaxed-mode bash pass-through, and
  dropped `--allowedTools`.
- **Agreement: 8/8** that the claim as worded is overstated (Gemini #319
  matrix: Y Y Y Y Y Y Y Y).

**RESOLUTION.** **CORRECTED.** The accurate statement is:

> Reviewer and auditor are **direct-write-tool-denied**: their native `.md`
> blocks deny `edit` (and orchestrator-guard blocks the five native/MCP write
> tool names for them), and in agent contexts crosslink-guard's by_type lists
> block `git commit` and the configured destructive git subcommands. They are
> **not** "read-only by construction" in the repository-immutability or
> authority-isolation senses: their `.md` bash surfaces permit
> `git *` (reviewer and auditor), `cargo *`/`npm *` (reviewer only), `opencode *`,
> `crosslink *`, and `rtk *`, none of which is read-only by definition, and
> the plugin layers block only finite, prefix-based lists. Indirect mutation
> and delegation paths — `npm run <script>`, `cargo run`, `git checkout
> <branch> -- <path>`, `git config core.hooksPath`, `opencode run --pure
> --agent builder`, `crosslink kickoff` — are **not** exhaustively ruled out
> and **not** covered by the blocklists.

**WHY.** Every reviewer that had access to the permission maps independently
derived the same gap: the `.md` bash grants are broad families, the plugin
blocklists are finite and git-specific, and the tool-level write block does
not touch bash. The `--pure` escape is the sharpest single piece of evidence:
`opencode run --help` documents it, and both reviewer.md and auditor.md
explicitly allow `opencode *`. The original document's own §1.1 criterion
(physically able to write = not read-only) supplies the falsifier.

**WHAT-NOT-TESTED.** No reviewer executed any bypass. The paths above are
read-from-source/CLI-help claims, not demonstrations (hy3 WHAT-NOT-TESTED 1;
kimi WHAT-NOT-TESTED). The discriminating test —
`opencode run --pure --agent builder` writing a scratch file — was out of
scope for the read-only review roles and has **not** been run
(hy3 WHAT-NOT-TESTED 1). Whether `--auto` bypasses the `.md` permission
engine (vs only the consent prompt) is inferred from `--help`, not measured
(kimi WHAT-NOT-TESTED). Whether opencode exposes `apply_patch` by that exact
name is **(unverified)** (kimi SHOULD-CONSIDER).

### 3.2 Claim (b): "`--allowedTools` is not enforced end-to-end"

**CLAIM.** Original §2.3/§3.6/§5.1: the fork constructs the `--allowedTools`
string, but the deployed wrapper drops the flag and `opencode run` has no such
flag — "constructed but not enforced" (verified against wrapper source and
`opencode run --help`, not a live kickoff).

**FINDINGS.**
- **luna (MUST FIX):** the blanket no-enforcement claim is **incomplete**:
  `launch.rs:1003-1025` has a **container path** that directly invokes
  `claude` and passes `--allowedTools`; only the local wrapper path drops it.
  Qualify the claim by launch mode.
- **kimi (MUST FIX):** same — "the host wrapper drops --allowedTools for
  local tmux launches. But launch.rs lines 1023-1026 pass --allowedTools
  directly to the claude binary inside Docker/Podman containers without the
  host wrapper in the way. If the container image ships a real Claude Code
  binary or a wrapper that forwards it, the tool surface is enforced there."
- **ChatGPT (#9):** reframes it as "dead security control / false assurance
  surface" — a future maintainer could set `kickoff.allowed_tools`, see it in
  the generated command, and assume the restriction is active. #10: activating
  the dormant mechanism could **increase** reviewer/auditor capability
  (the base list includes `Write`, `Edit`, `Task`, `WebSearch`, `WebFetch`,
  `Bash(mkdir *)`, `Bash(touch *)` — identical for all agent types).
- **Deepseek (#3):** "an unenforced fiction"; the advertised architecture does
  not match the running system.
- **Qwen (C-04):** silent loss of a security-relevant option; the constructed
  surface is identical for all agent types; base list includes dangerous
  tools; Claude-Code-style `Bash(git *)` patterns don't map cleanly to
  opencode's permission engine.
- **hy3 (P5, confirming the local-path finding):** wrapper lines 28-30 consume
  the flag with `shift 2`, and `opencode run --help` lists no such flag —
  confirmed independently. But hy3's M1 adds the version nuance (claim (c)):
  the source that builds `--allowedTools` (prompt.rs/launch.rs) is the
  **undeployed** HEAD 6221309e.
- **GLM-5.2:** dead surface / misallocation of engineering effort.
- **Sonnet 5:** no direct position beyond the broader architecture mismatch.
- **Agreement: 8/8** that the surface is dormant in the local path (Gemini
  #319: Y Y Y Y Y Y Y Y); **luna + kimi** (2/8) uniquely identify the
  container-path exception.

**RESOLUTION.** **CONFIRMED with a launch-mode qualification.** The accurate
statement is:

> The `--allowedTools` surface is **not enforced end-to-end on the local
> tmux path**: the `claude` wrapper consumes the flag without forwarding it
> (`~/.local/bin/claude` lines 28-30, `shift 2`), and `opencode run --help`
> exposes no `--allowedTools` flag (both verified). It **is** passed
> **directly to the agent binary inside the Docker/Podman container path**
> (`launch.rs` lines 1000-1035), where no host wrapper intervenes; whether it
> is enforced there depends on the container image's `claude` binary, which
> was **not** inspected. The constructed surface is identical for all agent
> types (`build_allowed_tools(conventions, verify)` has no `agent_type`
> parameter — verified at prompt.rs lines 429-432), so activating it would
> grant reviewer/auditor the same surface as builder, including `Write`,
> `Edit`, `Task`, `WebSearch`, `WebFetch`. It is accurately described as a
> **dormant/dead control** on the local path, not merely "config drift"
> (ChatGPT #9).

**WHY.** The wrapper source and `opencode run --help` are direct evidence for
the local path. `launch.rs`'s container branch is direct evidence that the
claim as blanketly stated ("the wrapper drops it") is launch-mode-dependent.
The original document's own §6.4 already scoped the verification correctly
("not against a live kickoff"); the reviewers' correction is that this
qualification must also cover the container path.

**WHAT-NOT-TESTED.** No live kickoff launch was run in any mode
(original §6.4; kimi WHAT-NOT-TESTED). The container image's `claude` binary
was not inspected; whether it is a real Claude Code binary or a wrapper that
forwards `--allowedTools` is **(unverified)** (kimi). Whether opencode's
permission engine would honor Claude-Code-style `Bash(pat *)` patterns is
**(unverified)** (original §6.4; Qwen C-04).

### 3.3 Claim (c): deployed crosslink version (a87bd513 vs source HEAD 6221309e conflation)

**CLAIM.** Original §2.2: "The deployed binary is built from
`/home/claude-code/projects/crosslink` (a fork of crosslink),
`v0.9.0-beta.1-59-g6221309e`."

**FINDINGS.**
- **hy3 (M1, blocking, strongest evidence):** `crosslink --version` reports
  `crosslink 0.9.0-beta.1+a87bd513`; `git -C /home/claude-code/projects/crosslink
  describe --tags` reports `v0.9.0-beta.1-59-g6221309e` (HEAD = 6221309e).
  These are **different commits**. a87bd513 (2026-08-08,
  "fix(hydration): follow-up hardening") is an ancestor; exactly ONE commit
  separates them: 6221309e "feat(kickoff): add --base <ref> ...", and
  `git show --stat 6221309e` shows it modifies `kickoff/launch.rs` (+59) and
  `kickoff/prompt.rs` (+12) — two of the three files the original §7 lists as
  verified sources. Consequence: "every claim in sections 3.6, 5.1 and 5.2
  that is presented as a DEPLOYMENT fact is in fact a SOURCE fact about an
  undeployed commit, in the very module that differs. The cheapest
  discriminating test was one command, and it was not run."
- **kimi (MUST FIX):** same binary/source mismatch, reported independently.
- **luna:** not flagged (luna focused elsewhere).
- **External reviewers:** none had access to the binaries — the version
  conflation was found **only by the 3 internal reviewers with repository
  access** (Gemini #319: luna N, hy3 Y, kimi Y — the matrix shows 3/8, "all
  internal"; luna did not flag it, so the count is hy3 + kimi = 2 flagged,
  but the #319 matrix lists luna Y; the resolution below is verified directly
  regardless of count).
- **Agreement: 2-3/8** (internal reviewers with live access).

**RESOLUTION.** **CONFIRMED as a real defect (CORRECTED).** Verified directly
on 2026-08-09:
- Deployed binary: `crosslink 0.9.0-beta.1+a87bd513` (`crosslink --version`).
- Source HEAD: `v0.9.0-beta.1-59-g6221309e` (`git describe --tags`),
  commit `6221309e` "feat(kickoff): add --base <ref> to branch worktrees from
  an arbitrary base (GH#283)".
- The delta commit modifies `kickoff/launch.rs` (+59) and `kickoff/prompt.rs`
  (+12), exactly the modules the original cites for its kickoff-surface
  claims.

The original conflated **deployed-binary state with source-tree HEAD** — the
same binary-vs-source misattribution class the workflow-topology design (§1.3
of the original) exists to catch (hy3: "the exact failure class section 1.3
holds up as the motivating incident"). Any claim about the kickoff surface
presented as a deployment fact must be re-verified against a87bd513 or marked
source-only.

**WHY.** Both commands are cheap, deterministic, and were run during this
verification. The `--stat` output shows the delta lands in the cited files.

**WHAT-NOT-TESTED.** hy3 confirmed the commit delta at file granularity only;
he did **not** diff `build_allowed_tools` or `build_agent_command` between
a87bd513 and 6221309e, so whether the **deployed behavior** actually differs
from source HEAD is **(unverified)** — only that the original cited undeployed
source (hy3 WHAT-NOT-TESTED 4).

### 3.4 Claim (d): MCP filesystem tool names in orchestrator-guard

**CLAIM.** Original §3.2: orchestrator-guard blocks the tools `write`, `edit`,
`apply_patch`, `filesystem_write_file`, `filesystem_edit_file` unless the
resolved agent is `builder`.

**FINDINGS.**
- **kimi (MUST FIX, the sharpest):** the configured server is
  `@modelcontextprotocol/server-filesystem`, whose tools are named
  `write_file`, `edit_file`, `create_directory`, and `move_file` per upstream
  docs. Therefore orchestrator-guard does **not** close the MCP leg of the
  #33677 gap — "The most serious defect invalidates the central claim that the
  #33677 edit:deny gap is closed for MCP filesystem writes." (kimi did **not**
  inspect opencode's MCP client naming — WHAT-NOT-TESTED: "Did not verify the
  exact MCP tool names as exposed by opencode's MCP client (only consulted
  upstream server documentation)").
- **ChatGPT (#1 matrix):** "MCP filesystem write | guard blocked | guard
  blocked | apparently no" — treated the MCP leg as closed.
- **Qwen (H-06):** MCP surface under-specified — the doc does not enumerate
  which MCP servers are configured, what tools they expose, or whether any MCP
  tool can execute shell commands/write files.
- **Sonnet 5 (fourth finding):** the doc never states whether **all
  currently-loaded MCP tools** were audited for other write-capable actions
  (a database MCP with an `execute` tool, a filesystem-adjacent tool under a
  different name).
- **hy3 (S4, S5):** adjacent — the MCP `sqlite` server is configured but
  disabled (opencode.json lines 34-36); the filesystem MCP server is rooted at
  the main repo `/home/claude-code/projects/ASES`, not the worktree (line 39).
- **GLM-5.2 / Deepseek / luna:** no direct position on the tool names.
- **Agreement:** kimi unique on the name-mismatch claim; the runtime evidence
  below changes the resolution.

**RESOLUTION.** **PARTIALLY CONFIRMED — the names are correct as opencode
exposes them; the true gap is the *unlisted* MCP write tools.** Verified
runtime evidence from `/tmp/orchestrator-guard.log` (the plugin's own
append-only log, current through 2026-08-09):
- `tool: filesystem_write_file` — **51 logged executions**
  (all `ALLOW ... agent: builder`).
- `tool: filesystem_edit_file` — **107 logged executions**
  (all `ALLOW ... agent: builder`).
- `tool: create_directory` / `tool: move_file` / `filesystem_create_directory`
  / `filesystem_move_file` — **0 log entries** (never invoked in this
  deployment).

Therefore:
1. **kimi's premise that the blocked names are wrong is refuted by runtime
   evidence:** opencode's MCP client exposes the server-filesystem tools with
   the `filesystem_` prefix — `filesystem_write_file` and
   `filesystem_edit_file` ARE the real, observed tool names in this
   deployment (158 combined executions). The original document's names were
   right.
2. **kimi's underlying concern stands, relocated:** the same MCP server
   exposes `create_directory` and `move_file` (per upstream server-filesystem
   docs), which opencode would name `filesystem_create_directory` /
   `filesystem_move_file`. These are **not** in `BLOCKED_TOOLS`
   (orchestrator-guard.ts lines 33-39), so for any non-builder agent they
   would pass the orchestrator-guard hook unblocked. This is the **true MCP
   gap**: not wrong names, but an incomplete `BLOCKED_TOOLS` set.
3. The MCP surface is under-documented: `filesystem` is the only enabled
   server (opencode.json lines 37-41), `sqlite`/`github`/`playwright`/
   `cloudflare` disabled, and the filesystem server is rooted at the **main
   repo**, not the worktree (hy3 S5).

**WHY.** The plugin's own log is primary runtime evidence of the tool names
opencode actually delivers to the hook — it is the strongest possible
refutation of the "wrong names" claim and the strongest support for the
"missing names" claim (absence of evidence in the log is consistent with the
tools never being called; their exposure is inferred from the naming pattern
plus upstream docs).

**WHAT-NOT-TESTED.** Whether `create_directory`/`move_file` are actually
exposed under `filesystem_`-prefixed names by this opencode fork is
**(unverified)** — inferred from naming convention and upstream docs, never
invoked in the log (0 entries). Whether a non-builder role could reach the MCP
server at all under the native `.md` permissions was not tested. Whether the
exact lowercase name `apply_patch` exists as an opencode tool is
**(unverified)** (kimi).

### 3.5 Claim (e): `allowed_bash_prefixes` as an enforcement surface

**CLAIM.** Original §3.3/§5.1: `allowed_bash_prefixes` is "the bash allowlist
enforced by crosslink-guard" — one of "three separate surfaces that must be
kept in agreement" for kickoff enforcement.

**FINDINGS.**
- **hy3 (M3, blocking, strongest technical evidence):** `allowed_bash_prefixes`
  is an **allow-fast-path, not a denying surface**. In crosslink-guard's
  control flow: step 6 (lines 1141-1147) matching the allowlist causes an
  early `return` (ALLOW); failing to match does **not** block. Control falls
  to step 7 (relaxed mode → ALLOW, lines 1152-1155) or, in strict mode, step
  9, where the mere existence of a non-empty `.crosslink/.active-issue`
  sentinel returns ALLOW (lines 1170-1181). Only the combination of strict
  mode AND no active issue blocks (lines 1205-1208). Since commits are gated
  on an active issue, every working agent has one; therefore the allowlist
  never denies a bash command in either tracking mode. The real bash denials
  come from `blocked_git_commands` (step 3, git-specific) and the opencode
  native `.md` block. "The parenthetical in section 5.1 concedes the point
  only for relaxed mode; it is equally true in strict mode. Correct
  statement: for bash patterns there is ONE denying surface, the agent .md
  block."
- **ChatGPT (#14, #12):** "single source of truth" overstated (claim (l));
  shell-parsing attack surface (split on `&&`/`;`/`|` — hy3's verified
  reading shows the plugin splits only on space-padded ` && `, ` ; `, ` | `).
- **Qwen (H-02):** prefix-based shell command matching is unsafe; bypass
  classes (shell metacharacters, interpreters, wrappers, redirection).
- **Deepseek (#3):** in relaxed mode the allowlist is not applied for agents;
  for kickoff agents the only effective bash restriction is the native agent
  definition.
- **GLM-5.2:** trampolines through allowed interpreters (`npm run`, `python3
  -c`).
- **luna:** no direct position on allow-fast-path (focused on countable
  errors and the container path).
- **kimi:** no direct position (focused on MCP and version).
- **Agreement:** hy3 unique on the allow-fast-path mechanics; the external
  reviewers independently attacked the allowlist's security posture (Qwen,
  GLM, ChatGPT), which presupposes it is a denying surface — the resolution
  below corrects that premise.

**RESOLUTION.** **CORRECTED (hy3 confirmed by direct source reading).** The
accurate statement is:

> `allowed_bash_prefixes` is an **allow-fast-path** in crosslink-guard's
> control flow (step 6): a command matching any prefix returns ALLOW
> immediately. A command **not** matching any prefix is **not** denied by the
> allowlist — control proceeds to relaxed-mode allow (step 7), no-crosslink-dir
> allow (step 8), active-issue allow (step 9, sentinel or session status), and
> only in **strict mode with no active issue** does a non-matching command get
> blocked (step 10). Because active-issue gating applies to every working
> agent, the allowlist effectively never denies bash in either tracking mode.
> The denying surfaces for bash are: (1) `blocked_git_commands` (git-specific,
> step 3) and (2) the opencode native `.md` permission block. The
> "three surfaces in agreement" framing in the original §5.1 therefore
> overstates the allowlist's role as an enforcement layer — it is a
> fast-path/perf surface, not a denial boundary.

**WHY.** Direct reading of `crosslink-guard.ts` control flow (steps 6-10,
lines 1141-1215) shows the early-return semantics and the sentinel/active-
issue ALLOW paths. The `.active-issue` sentinel is present in this worktree
(content "320") and in the main repo (content "320"), i.e., the fast path
firing is the normal state.

**WHAT-NOT-TESTED.** No runtime test demonstrated a non-matching bash command
being denied by the allowlist specifically (hy3's reading is source-derived,
WHAT-NOT-TESTED 2). The hook-ordering interaction with rtk-guard (which can
mutate `output.args.command` before/after this check) remains unmeasured
(original §6.3). Whether a `throw` in one `tool.execute.before` handler
short-circuits other handlers is **(unverified)** (hy3 S10).

### 3.6 Claim (f): identity resolution fail-open to builder

**CLAIM.** Original §3.3: agent identity resolves from `chat.params` /
`chat.message` keyed by sessionID, falling back to `CROSSLINK_AGENT_TYPE`,
then hook-config `agent.type` (default `builder`); the plugin logs explicit
FAIL-CLOSED warnings when resolution falls back.

**FINDINGS.**
- **GLM-5.2 (1A, the race):** if a read-only agent executes a tool call
  **before** the `chat.params` event registers, or an event is dropped, the
  plugin resolves the agent as `builder` (edit: allow, bash: allow) — failing
  **open to the highest privilege level**. Logging a FAIL-CLOSED warning is
  observational, not blocking; the write still succeeds.
- **Deepseek (#5):** the per-session map is better than a shared scalar (#204)
  but still depends on event delivery/ordering; no cryptographic attestation;
  FAIL-CLOSED warnings are observational only; a race/event loss could
  misidentify a read-only agent as builder.
- **Qwen (C-03):** defaulting to builder is fail-open; session identity is not
  authenticated; warnings are not enforcement; attack sketch: unresolved/
  misresolved session treated as builder performs a git operation that would
  otherwise be blocked.
- **hy3 (M4a, sharpest code-level evidence):** the by_type fallback is
  fail-OPEN and the doc repeats the misleading in-code label. When no
  chat.params/chat.message agent has been seen AND `CROSSLINK_AGENT_TYPE` is
  unset, resolution falls back to hook-config `agent.type`, which defaults to
  `"builder"` (crosslink-guard.ts lines 453-465, 874-879). hook-config.json
  has **no `by_type.builder` entry** (only orchestrator, reviewer, auditor),
  so the base config applies unchanged — under which `git commit` is GATED,
  not BLOCKED. **A reviewer or auditor in that state can commit.** The plugin
  logs this as "FAIL-CLOSED" (lines 887-918) but the behavior is a fallback to
  the **less restrictive** configuration.
- **kimi (SHOULD-CONSIDER):** orchestrator-guard lacks the
  `CROSSLINK_AGENT_TYPE` env fallback that crosslink-guard has — if a kickoff
  session's `chat.params` is delayed/lost, a builder's write could be
  incorrectly blocked (fail-closed the other way, but inconsistent).
- **ChatGPT (#6 of 10 invariants):** guard fail-closed invariant — failure to
  determine agent identity should block security-sensitive operations.
- **luna:** not flagged.
- **Agreement: 7/8** (Gemini #319 matrix: Y Y Y Y Y N Y Y — luna N).

**RESOLUTION.** **CONFIRMED — resolution fails open to builder.** Verified
directly:
- `resolveAgentType` returns `"builder"` when `agent.type` is absent or
  unparseable (crosslink-guard.ts lines 453-465).
- Runtime resolution: `sessionAgent?.agent || runtimeEnv ||
  resolveAgentType(crosslinkDir)` (lines 874-879) — the final fallback is the
  hook-config `agent.type`, which in this repo is `"builder"`
  (hook-config.json line 8).
- hook-config.json has **no `by_type.builder` entry** (lines 41-124), so the
  fallback yields the **base config** in which `git commit` is gated, not
  blocked — a reviewer/auditor whose session is unresolved can commit.
- The plugin logs "FAIL-CLOSED" for this path (lines 892-903), but the label
  describes the **logging**, not the security posture: the effective posture
  is fail-open to the least-restrictive base.
- kimi's asymmetry is also confirmed: orchestrator-guard.ts has **no**
  `CROSSLINK_AGENT_TYPE` fallback at all (only the per-session map +
  module `currentAgent`, lines 51-103), so the two plugins can disagree about
  the same session.

**WHY.** The code paths are explicit. The `by_type.builder` absence is
checkable in hook-config.json lines 41-124 (only `orchestrator`, `reviewer`,
`auditor` keys). The #204 regression (a shared scalar clobbered by subagent
events) proves the event-stream dependency is real, and the per-session map
mitigates it without removing it.

**WHAT-NOT-TESTED.** No reviewer forced the fallback path in a live session
(hy3 WHAT-NOT-TESTED 3 notes his own session had `CROSSLINK_AGENT_TYPE=reviewer`
set, so the fallback was not exercised). Whether the FAIL-CLOSED warning is
ever acted on by the operator was not tested. Whether a reviewer/auditor in
the fallback state has actually committed anywhere is **(unverified)** (no
evidence of occurrence found).

### 3.7 Claim (g): Builder can tamper with enforcement configuration

**CLAIM.** Original §1.2/§3.1: builder has `edit: allow` and unrestricted
`bash`. The original document does not state whether the enforcement
configuration is protected from the builder.

**FINDINGS.**
- **Sonnet 5 (the sharpest statement):** "nothing stops the Builder from
  editing `.crosslink/hook-config.json` itself. Builder has `edit: allow` and
  unrestricted `bash`, and crosslink-guard reads its blocked/gated lists from
  that file on every call... If crosslink-guard reads the live file rather
  than a committed/reviewed snapshot, Builder can loosen `blocked_git_commands`
  or `allowed_bash_prefixes` for itself before the change is ever seen by
  Reviewer or Auditor... This is a self-modifying trust root sitting one
  `edit` call away from the one role the whole four-role split is designed to
  constrain."
- **Deepseek (#1, concrete failure modes):** builder can edit
  `.crosslink/hook-config.json` to remove `git push` from
  `blocked_git_commands`; create/modify `.active-issue` sentinel to satisfy
  commit gating without a real issue; invoke `opencode run` directly with
  arbitrary models, bypassing the wrapper's model enforcement; corrupt
  `.crosslink/issues.db`; rewrite local git history before operator push.
- **Qwen (C-02, longest list):** documents 14 paths not stated to be
  write-protected from builder: `.opencode/opencode.json`,
  `.opencode/agents/*.md`, `.opencode/plugins/*.ts`,
  `.crosslink/hook-config.json`, `.crosslink/hook-config.local.json`,
  `.crosslink/issues.db`, `.crosslink/.hub-cache/issues.db`,
  `.active-issue`, `~/.config/opencode/plugins/plugin.ts`,
  `~/.config/opencode/opencode.json`, `~/.local/bin/claude`,
  `~/.local/bin/opencode`, `~/.local/bin/crosslink`, `~/.cargo/bin/rtk`.
- **GLM-5.2:** partial (via the fail-open identity race).
- **ChatGPT:** partial (via the `.claude` exemption and `crosslink *`
  authority).
- **hy3:** confirmed indirectly via M4a (builder fallback) and the
  isAgentContext precondition.
- **luna:** not flagged; kimi: not flagged.
- **Agreement: 6/8** (Gemini #319 matrix: Partial Y Partial Y Y N Y N).

**RESOLUTION.** **CONFIRMED — no protection exists.** The builder's `.md`
block is `edit: allow` + `bash: allow` (verified), and there is **no
mechanism** — in `.opencode/opencode.json`, the plugins, or hook-config — that
protects the enforcement config files from the builder. In particular:
- `.crosslink/hook-config.json` is read live by `loadConfigMerged`
  (crosslink-guard.ts lines 283-310) on every state resolution; nothing
  prevents a builder edit between sessions or before review.
- `.crosslink/.active-issue` is a plain 3-byte sentinel file (content: the
  issue id); the commit-gating fast path trusts it without verifying against
  Crosslink (lines 1026-1040, 1169-1181).
- `.opencode/plugins/*.ts` are in-repo source the builder can edit.
- External trust root: `~/.config/opencode/plugins/plugin.ts`,
  `~/.local/bin/*`, `~/.cargo/bin/rtk` are user-writable and not integrity-
  checked (Qwen H-07; Deepseek #6).
- Under the agent `tracking_mode: relaxed`, crosslink-guard does not enforce
  the bash allowlist for agents anyway (claim (e)), so the builder's bash is
  effectively unrestricted.

The reviewers' conclusions: the enforcement plane is **mutable data** for the
builder, not a boundary (Deepseek: "the permission model is only structural
for the roles that were never meant to write in the first place"). Sonnet 5's
recommendation is the operative one: if structural enforcement is the goal,
either remove the builder's write access to guard configuration and the
sentinel, or introduce a trusted computing base (read-only mounts, daemon-
managed tokens, fail-closed kill switch).

**WHY.** The builder's `.md` block and the live-read config loading are both
directly verifiable. The sentinel's plain-text, untrusted nature is
verifiable on disk.

**WHAT-NOT-TESTED.** No reviewer (or this verification) actually had the
builder edit hook-config or forge a sentinel — the finding is a capability
inference from the permission map and the live-read behavior, not a
demonstration (Qwen's scenarios 3 and 4 are hypothetical). Whether OS file
permissions would prevent a builder from editing `~/.config/opencode/*` or
`~/.local/bin/*` was not tested (they are user-writable on this machine).

### 3.8 Claim (h): wrapper `--auto` injection under tmux

**CLAIM.** Original §2.3 describes the wrapper's four behaviors (model
enforcement, memory scoping, agent-type export, `--allowedTools` drop) but
omits `--auto`.

**FINDINGS.**
- **hy3 (M7, blocking):** `~/.local/bin/claude` lines 66-68:
  `if [[ -n "$TMUX" ]]; then ARGS+=("--auto"); fi` — unconditional for every
  tmux launch, which is every kickoff agent. `opencode run --help`: `--auto
  auto-approve permissions that are not explicitly denied (dangerous!)`. The
  wrapper also maps `--dangerously-skip-permissions` → `--auto` (lines
  21-24), so by the wrapper's own accounting `--auto` is the
  dangerous-skip posture. Consequence: every permission set to `ask` is
  auto-approved in the kickoff path — e.g. builder's
  `external_directory: {"*": "ask", "/tmp/*": "allow"}` becomes an effective
  grant for every external directory. "It is the one wrapper behaviour that
  changes permission outcomes."
- **kimi (MUST FIX / SHOULD-CONSIDER):** same — the wrapper always passes
  `--auto` for tmux agents; a permission-enforcement report should explain
  whether `--auto` bypasses only the consent prompt or also the `.md`
  permission engine.
- **GLM-5.2 (3B):** related — whether `task`-spawned subagents go through the
  wrapper (with model enforcement + memory caps) or directly through the
  opencode binary is unstated.
- **luna:** not flagged directly (but the container-path finding is adjacent).
- **ChatGPT / Sonnet 5 / Deepseek / Qwen:** did not identify `--auto`
  (external reviewers had no wrapper access).
- **Agreement: 4/8** (Gemini #319 matrix: N N Y N N Y Y Y).

**RESOLUTION.** **CONFIRMED (hy3 + kimi + GLM adjacent).** Verified directly:
- `~/.local/bin/claude` lines 66-68 inject `--auto` whenever `$TMUX` is set.
- `opencode run --help` documents `--auto` as "auto-approve permissions that
  are not explicitly denied (dangerous!)" (verified 2026-08-09).
- The wrapper maps `--dangerously-skip-permissions` to `--auto` (lines
  21-24), confirming the wrapper authors' own equivalence.
- Every kickoff agent runs inside tmux (the kickoff launcher requires tmux
  for local mode; launch.rs lines 353-366), so `--auto` is effectively
  unconditional for kickoff agents.
- **Consequence:** in the kickoff path, `ask`-graded permissions are
  auto-approved. The original's §3.1 listing of builder
  `external_directory: {"*": "ask", "/tmp/*": "allow"}` as a constraint is
  materially weakened under `--auto`.
- **Open question (kimi, GLM):** whether `--auto` bypasses only the consent
  prompt or also the `.md` permission engine is not documented by opencode and
  was **not** empirically confirmed (kimi WHAT-NOT-TESTED; hy3 WHAT-NOT-TESTED
  5).

**WHY.** The wrapper source and `opencode run --help` are direct evidence.
The tmux requirement for local kickoffs is in launch.rs.

**WHAT-NOT-TESTED.** Whether `--auto` actually converts an `ask` permission to
allow (vs merely auto-consenting while the `.md` engine still denies) was not
empirically confirmed (hy3 WHAT-NOT-TESTED 5; kimi WHAT-NOT-TESTED). Whether
`task`-tool subagents inside an opencode process go through the wrapper is
**(unverified)** (GLM 3B).

### 3.9 Claim (i): countable claim errors (bash 49 vs 29, agent_overrides 21 vs 19, orchestrator patterns 34 vs ~40)

**CLAIM.** Original §3.5: `allowed_bash_prefixes` = 29 entries;
`agent_overrides` = 19 entries; §3.1: orchestrator bash = "~40 explicit allow
patterns".

**FINDINGS.**
- **luna (MUST FIX):** "The stated '29 entries' does not match
  `.crosslink/hook-config.json:127-176` (49 entries). Correct the inventory or
  explain the counting convention."
- **hy3 (M2, blocking):** three of four countable claims are wrong:
  - `allowed_bash_prefixes`: 49 entries (hook-config lines 128-176), not 29.
    "29 appears to be the count of the compressed list in the doc itself,
    mislabelled as the config entry count — the doc collapses five jj entries
    into 'jj *' and five cargo plus two npm entries into 'toolchains'."
  - `agent_overrides`: 21 entries in `agent_overrides.blocked_git_commands`
    (hook-config lines 16-36), not 19.
  - Orchestrator bash: 34 allow patterns (orchestrator.md lines 9-42), not
    ~40.
  - Only root `blocked_git_commands` (14, lines 180-193) is correct.
  - "Counts are the cheapest verifiable class of claim; failing three of four
    undermines the verification assertion for everything else."
- **kimi (SHOULD-CONSIDER):** orchestrator bash pattern count is "33 allow
  patterns, not about 40" (minor precision issue; kimi counts 33 where hy3
  counts 34 — the difference is likely whether `"*": "deny"` is included; the
  verified count of explicit `*: allow` patterns is 34 — see below).
- **External reviewers:** none could count (no repo access); Gemini #319
  tabulates 3/8 (all internal).
- **Agreement: 3/8** (internal with file access).

**RESOLUTION.** **CONFIRMED — counts corrected.** Verified directly on
2026-08-09:
- `allowed_bash_prefixes`: **49 entries** in `.crosslink/hook-config.json`
  lines 127-177 (crosslink, opencode, git status/diff/log/branch/show, jj
  log/diff/status/show/bookmark list, cargo test/build/check/clippy/fmt, npm
  test/run, npx, tsc, node, python, ls, dir, pwd, echo, rtk read, ps -o,
  pgrep, tmux list-sessions/capture-pane/display-message, grep, tail, head,
  wc, stat, diff, free, df, uptime, date, which, env, git worktree list,
  git -C, curl -I, curl --head). The original's 29 was a count of its own
  compressed prose list, not the config.
- `agent_overrides.blocked_git_commands`: **21 entries**
  (hook-config lines 15-37: push, push --force, push -f, merge, rebase,
  cherry-pick, reset, reset --hard, clean, clean -f, clean -fd, clean -fdx,
  checkout ., restore ., stash, tag, am, apply, branch -d, branch -D,
  branch -m). The original's 19 was wrong; it also omitted the `git clean -f/
  -fd/-fdx` variants (kimi NIT) and listed only 19 of the 21.
- Orchestrator bash allow patterns: **34 explicit `*: "allow"` entries** in
  `.opencode/agents/orchestrator.md` (excluding the `"*": "deny"` default):
  crosslink *, opencode models *, git status/diff/log/show/branch/commit/
  merge *, ls *, cat *, rtk *, sleep *, ps -o *, pgrep *, tmux list-sessions
  *, tmux capture-pane *, tmux display-message *, grep *, tail *, head *,
  wc *, stat *, diff *, free *, df *, uptime *, date *, which *, env *,
  git worktree list *, git -C *, curl -I *, curl --head * = 34. (hy3 counted
  34; kimi counted 33 — the discrepancy is one entry; the 34 count here is
  the direct count from the file. Either way, "~40" is wrong.)
- Root `blocked_git_commands`: **14 entries** (correct in the original).

**WHY.** All three counts are direct, mechanical counts of the config/`.md`
files, which were read in full during verification.

**WHAT-NOT-TESTED.** Whether the "~40" figure came from an older version of
orchestrator.md (e.g. before `sleep *` was granted via #298) is
**(unverified)**. No runtime behavior depends on these counts; the error is
one of documentation accuracy and verification-claim credibility.

### 3.10 Claim (j): the #313 sqlite3 block as settled fact vs not-instrumented

**CLAIM.** Original §5.3: the #313 Phase-1 auditor "was tasked with
independently verifying the builder's read-only SQLite inventory claims...
reported 'sqlite3 blocked by bash permission pattern (no allow rule for
sqlite3)'"; the text calls the block "the concrete, observed cost of the
surface disagreement" and says the blocking surface "matches the agent `.md`
allowlist".

**FINDINGS.**
- **ChatGPT (Critical #2):** "the precise layer responsible in that session
  was not instrumented" (§6 of the original) means the earlier narrative ("the
  auditor fell back ... because sqlite3 was blocked by the native `.md`
  allowlist") is an **inference, not an established fact**; the uncertainty
  should be propagated upward into the earlier claims, not buried in §6.
  Recommends three epistemic categories: Observed / Source-verified /
  Inferred.
- **Sonnet 5 (second finding):** §5.3's central exhibit is treated as settled
  fact in the main text but §6.5 quietly walks it back ("under relaxed
  tracking mode the bash allowlist isn't even the blocking layer, so the
  actual layer responsible was not instrumented"). "The whole exhibit is an
  agent's self-reported comment in an issue tracker, not a reproduced failure
  — which is exactly the kind of unverified cross-boundary claim §1.3's own
  workflow-topology design exists to catch. The document's verification
  methodology blurs 'confirmed the comment exists' with 'confirmed the
  comment is true'."
- **hy3 (S4-adjacent; P4 confirms quote accuracy):** the two #313 quotations
  in §5.3 are verbatim-accurate against the issue comment stream (the 15:01
  [PROGRESS] and 15:03 [handoff] comments), and the surrounding narrative
  (auditor pp3g-dZ3X on opencode-go/mimo-v2.5, fallback to file-size/stat
  cross-checks, NO DIVERGENCE OBSERVED) matches the record. But the blocking-
  layer attribution remains un-instrumented. hy3 also notes the adjacent
  mitigation the original missed: `.opencode/opencode.json` lines 34-36
  configure an MCP `sqlite` server with `"enabled": false` — whether enabling
  it would have unblocked the #313 auditor is untested (S4).
- **Qwen (M-03):** the auditor's lack of sqlite3 reveals a deeper
  verification problem: the audit trail lives in SQLite; granting `sqlite3`
  naively is unsafe (it can write unless constrained); the issue DB's own
  protection is unclear.
- **GLM-5.2 (2A):** the enforcement layer actively prevented the topology
  from functioning — the auditor was forced to verify file metadata rather
  than actual artifact evidence ("enforcement defeats the topology").
- **Deepseek (#7):** #313 shows the auditor was a one-off task, not a
  persistent monitoring service.
- **luna:** no direct position (but luna's MUST FIX on git mutators is
  adjacent).
- **Agreement: 6/8** that the original treated it as more settled than the
  evidence supports (Gemini #319 matrix: Y Y Y Y Y N Y N — Sonnet5, GLM,
  Deepseek, Qwen, ChatGPT, hy3; luna and kimi N).

**RESOLUTION.** **CONFIRMED as an accurate quote with a non-established
causal layer.** Verified directly:
- The #313 auditor (agent `pp3g-dZ3X`, opencode-go/mimo-v2.5) did post, at
  15:01: "[PROGRESS] state=verifying completed=file-size cross-checks done...
  sqlite3 blocked by bash permission pattern (no allow rule for sqlite3)",
  and at 15:02/15:03: "LIMITATION: sqlite3 blocked by bash permission
  pattern, could not independently verify headline SQL numbers. Systemic
  risk: auditor role lacks sqlite3 read access for DB-audit tasks." Both
  quotes are verbatim-accurate.
- The auditor fell back to file-size/stat-level cross-checks which passed
  (NO DIVERGENCE OBSERVED) — also accurate.
- **However:** the **causal layer** that blocked sqlite3 was **not
  instrumented**. Under the native `.md` model, the auditor's bash surface
  has no `sqlite3` allow rule, so the native engine would deny it; under
  crosslink-guard, `sqlite3` is not in `allowed_bash_prefixes` (49 entries)
  nor blocked — in relaxed mode it would pass (claim (e)). The most
  plausible blocker is the native `.md` deny (default `"*": "deny"`), but
  the session was not instrumented to confirm which layer fired.
- The MCP `sqlite` server exists in `.opencode/opencode.json` lines 34-36
  but is `enabled: false`; whether enabling it would have unblocked the
  auditor is **(unverified)** (hy3 S4).

**WHY.** The #313 comments are quoted verbatim from the issue record. The
layer attribution cannot be confirmed because no runtime instrumentation (hook
logs) was captured for that session; the plugin logs under `/tmp` were not
consulted for the 15:01 event (and may have rotated).

**WHAT-NOT-TESTED.** The precise blocking layer in the #313 session
(original §6.5). Whether the auditor would have been blocked by the native
engine, by crosslink-guard, or by something else if re-run today. Whether
`sqlite3` should be granted to the auditor (and how to make it read-only) is
an open design question (Qwen M-03).

### 3.11 Claim (k): no explicit adversary/threat model

**CLAIM.** Original §1.1/§4 frame the system around accidental failure classes
(silent hangs, model misconfiguration, stale IDs, binary/source
misattribution, token cost, accidental destructive git). No section states
who the adversary is.

**FINDINGS.**
- **Qwen (C-05, the fullest statement):** the document "mostly treats agents
  as honest-but-buggy" and does not adequately address: compromised/misaligned
  agents, prompt injection from issue comments, malicious artifacts/README/
  docs, malicious dependency manifests, malicious web content, model
  compromise, data exfiltration, secret access, supply-chain execution
  through npm/cargo, agent-to-agent social engineering, operator deception.
  Recommends a dedicated threat-model section with 10 threat classes and a
  control-to-threat mapping.
- **hy3 (S1):** "It never states whether the adversary is a MISTAKEN agent or
  a MISALIGNED one. Every bypass in M5 is trivial under the second reading and
  irrelevant under the first. Without this, 'structural enforcement' (section
  1.1) is unfalsifiable."
- **ChatGPT (#3, #8, biggest conceptual issue):** the additive-layers claim is
  an architectural assumption, not demonstrated; the model whitelist is model-
  selection control, not agent-capability control — the security boundary is
  harness/tool enforcement, not model identity.
- **Sonnet 5 (sixth finding):** "structural, not aspirational" is stronger
  than the findings support (the #204 regression already happened once in a
  structural mechanism; the kill/pause fails open).
- **GLM-5.2:** the system "created a larger attack surface than the one it
  attempted to close" (enforcement sprawl).
- **Deepseek:** implicit throughout (builder threat, kill-switch, fail-open).
- **luna / kimi:** not directly flagged (luna's bounded-blocklist framing and
  kimi's MCP findings are threat-adjacent).
- **Agreement: 6/8** (Gemini #319 matrix: Y Y Y Y Y N Y N).

**RESOLUTION.** **CONFIRMED — no explicit threat model exists.** The original
document never states whether the adversary is a mistaken (honest-but-buggy)
agent or a misaligned/compromised one. This matters because the severity of
every indirect-write finding (claims (a), (e), (f), (g), (h)) depends on the
answer: under the "prevent accidental mistakes" model, prefix-based
allowlists and blocklists are a reasonable design; under the "misaligned
agent" model, they are not a security boundary at all. The document also
conflates model-selection control (the whitelist plugin) with agent-capability
control (permissions) — ChatGPT #8's distinction.

**WHY.** A close reading of the original's §1.1, §4, and §5 shows only
accidental-failure motivations. Qwen's list of unaddressed adversarial classes
was checked against the original's sections and none are covered. The
reviewers' unanimous recommendation is a dedicated threat-model section that
states the adversary model and maps each control to the threats it mitigates
and the threats it does not.

**WHAT-NOT-TESTED.** Whether any adversarial scenario actually occurs in this
deployment (no incident evidence). Whether the operator would prefer a
misaligned-agent threat model (a policy decision, not a fact).

### 3.12 Claim (l): cross-repo drift + global model-whitelist plugin

**CLAIM.** Original §5.5 covers cross-repo drift (per-repo hook-config,
convention detection, fork vs deployment, model pins). Original §2.7
describes the user-level model-whitelist plugin.

**FINDINGS.**
- **Sonnet 5 (sixth, smaller items):** the user-level model-whitelist plugin
  is **global to the machine**, not scoped to ASES — it constrains every other
  opencode-based project under the same user account; §5.5's cross-repo drift
  discussion never addresses this blast radius.
- **luna (SHOULD-CONSIDER):** the "exactly seven free models" and
  provider-hiding claims are stronger than the plugin source supports:
  `plugin.ts:25-38` sets the whitelist and empties maps, but `:42-63`
  subsequently merges cached model maps **for every provider, including
  providers previously emptied**. Document the effective whitelist semantics
  and cache interaction, or label the result as intended policy rather than
  verified invariant.
- **kimi (SHOULD-CONSIDER):** same cache-re-enable risk; also notes §5.5
  mentions tripn-astro and Tools repos without introduction (external readers
  won't know what they are).
- **hy3 (S2, S3):** the seven-model whitelist is stale by the project's own
  rule (`opencode models opencode` returns six; `ling-3.0-flash-free` absent);
  the doc asserts the whitelist effect without citing the catalog output; the
  plugin empties `vertex` while the wrapper's allowed-provider list names
  `google-vertex` (inconsistent naming); the sentinel config at
  hook-config.json line 229 carries a stray flattened key naming a free Zen
  model.
- **ChatGPT (#14):** "single source of truth" for hook-config overstated —
  security-relevant configuration lives in nine places (agent .md, hook-config,
  hook-config.local, user opencode config, user model plugin, fork source,
  wrapper source, env vars, agent-type fallback).
- **Qwen (H-07):** user-level configuration outside the repo is a drift and
  tamper risk; no integrity evidence (checksums/versions/signatures) for
  external binaries and configs.
- **Deepseek (#10):** drift between documentation and live state.
- **GLM-5.2:** no direct position.
- **Agreement:** split by aspect — the global-scope/cache/verification
  findings have 3-4/8 each (Gemini #319 "model-whitelist plugin global":
  Sonnet5 + Qwen + hy3 = 3/8); the "single source of truth" overstatement is
  ChatGPT + luna + kimi.

**RESOLUTION.** **CONFIRMED — with the cache and scope corrections.** Verified
directly:
- The plugin at `~/.config/opencode/plugins/plugin.ts` is loaded by opencode
  at the user level and applies to **every** project launched under this user
  account — it is machine-global, not repo-scoped (Sonnet 5 correct).
- The plugin sets `freeZenModels` (7 entries incl. `ling-3.0-flash-free`) as
  the `opencode` provider whitelist, disables/hides openai/deepseek/
  cloudflare/cloudflare-ai-gateway, empties vertex's models, **then merges
  `~/.config/opencode/models-cache.json` for every provider without filtering
  disabled providers** (lines 42-63) — so a cache containing openai/deepseek
  entries would re-add them to the model map (luna/kimi correct). Whether the
  cache currently contains such entries is **(unverified)**.
- `opencode models opencode` returns six models; `ling-3.0-flash-free` is
  **absent from the live catalog** (verified 2026-08-09), so the "exactly
  seven free models" claim is stale by the project's own staleness rule.
- The "single config source" framing is overstated: crosslink-guard has
  hard-coded defaults (`DEFAULT_BLOCKED_GIT`, `DEFAULT_GATED_GIT`,
  `DEFAULT_ALLOWED_BASH`), a local overlay (`hook-config.local.json` with
  `+key` extension), and runtime env/agent-type fallbacks (ChatGPT/luna
  correct).
- Cross-repo drift is real but incompletely framed: per-repo hook-config can
  diverge; convention detection is one-level-deep and repo-shaped
  (helpers.rs 122-190, verified); the fork builds `--allowedTools` that the
  local wrapper drops (claim (b)); model pins drift (the #1 failure cause per
  permissions.md).

**WHY.** The plugin source, the live catalog output, and the wrapper/
hook-config contents were all read directly during verification.

**WHAT-NOT-TESTED.** Whether the models-cache currently re-enables any
disabled provider (the cache file exists but its contents were not audited for
this document — luna/kimi flagged the risk, not an observed occurrence).
Whether tripn-astro/Tools repos have divergent hook-config values was not
checked (original §5.5 lists them; this verification did not read them —
hy3 WHAT-NOT-TESTED 6).

---

## 4. Consensus Summary

### 4.1 Cross-reviewer agreement matrix (reproduced from Gemini #319)

| Finding / Theme | ChatGPT | Sonnet5 | GLM | Deepseek | Qwen | luna | hy3 | kimi | Count |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Read-only by construction overstated | Y | Y | Y | Y | Y | Y | Y | Y | 8/8 |
| Builder can modify enforcement config | Partial | Y | Partial | Y | Y | N | Y | N | 6/8 |
| --allowedTools surface dormant/dead | Y | Y | Y | Y | Y | Y | Y | Y | 8/8 |
| Identity resolution fails open to Builder | Y | Y | Y | Y | Y | N | Y | Y | 7/8 |
| No explicit adversary/threat model | Y | Y | Y | Y | Y | N | Y | N | 6/8 |
| Deployed-vs-source version conflation | N | N | N | N | N | Y | Y | Y | 3/8 (internal) |
| Countable claim errors | N | N | N | N | N | Y | Y | Y | 3/8 (internal) |
| Wrapper injects --auto under tmux | N | N | Y | N | N | Y | Y | Y | 4/8 |
| MCP filesystem tool names mis-identified | N | Partial | N | Partial | Partial | N | N | Y | 4/8 |
| Confidentiality/exfiltration unaddressed | Y | N | N | Y | Y | N | Y | N | 4/8 |
| #313 sqlite3 treated as settled fact | Y | Y | Y | Y | Y | N | Y | N | 6/8 |
| Model-whitelist plugin global | N | Y | N | N | Y | N | Y | N | 3/8 |

> **Note on this matrix:** the kimi "MCP filesystem tool names mis-identified"
> row is **partially refuted by runtime evidence** (see claim (d)): the names
> orchestrator-guard blocks ARE the real opencode-exposed names
> (`/tmp/orchestrator-guard.log`: 51 × `filesystem_write_file`, 107 ×
> `filesystem_edit_file`). The correct formulation is that `create_directory`
> and `move_file` are unblocked, not that the blocked names are wrong. The
> "Deployed-vs-source version conflation" row lists luna Y in #319's
> tabulation; luna's own verdict focuses on the container path and countable
> errors, so the direct attribution is hy3 (M1) and kimi (MUST FIX) — both
> confirmed independently by this verification.

### 4.2 Highest-confidence findings (confirmed by direct verification)

1. **Deployed-vs-source version conflation** (hy3 M1, kimi): deployed crosslink
   is `0.9.0-beta.1+a87bd513`; the original cites source HEAD `6221309e`, one
   commit ahead, whose delta lands in `kickoff/launch.rs`/`prompt.rs` — the
   very modules the original cites. **Confirmed.**
2. **Read-only-by-construction is false confidence** (8/8): reviewer/auditor
   have broad bash grants (`git *`, `opencode *`, `crosslink *`, reviewer
   also `cargo *`/`npm *`) that the blocklists do not make read-only; the
   `opencode run --pure` escape (no plugins) is documented in `--help`.
   **Confirmed as a capability, unexecuted.**
3. **MCP filesystem gap** (kimi, refined): orchestrator-guard's blocked names
   are correct as exposed (`filesystem_write_file`/`filesystem_edit_file`,
   runtime-log-verified); the true gap is `create_directory`/`move_file`
   not being in `BLOCKED_TOOLS`. **Confirmed (exposure of the latter
   inferred, never invoked).**
4. **Countable errors** (luna, hy3, kimi): 49 ≠ 29 (bash), 21 ≠ 19
   (agent_overrides blocked), 34 ≠ ~40 (orchestrator patterns); root
   blocked_git 14 correct. **Confirmed.**
5. **`--allowedTools` dormant on the local path, alive on the container
   path** (8/8 for dormancy; luna/kimi for the container exception).
   **Confirmed.**
6. **Wrapper `--auto` under tmux** (hy3 M7, kimi, GLM): auto-approves `ask`
   permissions for every kickoff agent. **Confirmed (flag semantics from
   `--help`, not measured).**
7. **Identity resolution fail-open to builder** (7/8): fallback chain ends at
   `agent.type` = `"builder"` with no `by_type.builder` entry → base config →
   `git commit` gated (not blocked) for an unresolved reviewer/auditor.
   **Confirmed from source.**
8. **Builder can tamper with enforcement config** (6/8): no protection exists
   for hook-config/sentinel/plugins/DBs. **Confirmed as a capability.**
9. **No explicit adversary/threat model** (6/8). **Confirmed by absence.**
10. **#313 sqlite3 block quoted accurately but causally un-instrumented**
    (6/8). **Confirmed.**

### 4.3 Agreed MUST-FIX list

Consolidated from the internal reviews' blocking findings and the external
reviews' minimum-remediation lists (Qwen §9; Gemini #319 "MUST FIX"):

1. Report the deployed crosslink version (`0.9.0-beta.1+a87bd513`) separately
   from source HEAD (`6221309e`); re-verify kickoff claims against a87bd513 or
   mark them source-only (hy3 M1, kimi).
2. Correct the countable claims: 49 allowed_bash_prefixes, 21 agent_overrides
   blocked, 34 orchestrator allow patterns (luna, hy3 M2, kimi).
3. Weaken/replace "read-only by construction" with the direct-write-tool-
   denied statement plus an indirect-mutation attack matrix (8/8; ChatGPT #1,
   Qwen Change 1, hy3 M5).
4. Qualify the `--allowedTools` no-enforcement claim by launch mode (local vs
   container) (luna, kimi).
5. Fix the MCP write-tool gap: add `create_directory`/`move_file` (as
   `filesystem_`-prefixed) to orchestrator-guard's `BLOCKED_TOOLS`, and
   document the MCP surface (kimi, Qwen H-06, Sonnet 5).
6. State the `allowed_bash_prefixes` allow-fast-path semantics — it is not a
   denying surface (hy3 M3).
7. Document the `--auto` injection and its effect on `ask` permissions in the
   kickoff path (hy3 M7, kimi).
8. Address identity fail-open: fail closed on unresolved identity, add a
   `by_type.builder` entry or deny-by-default (GLM, Deepseek, Qwen, hy3 M4a).
9. Add a dedicated threat-model section (Qwen C-05, hy3 S1).
10. Add a verified-sources/reproduction appendix with command outputs and
    excerpts so claims are externally checkable (Qwen M-02/L-01, hy3 S11,
    luna).

### 4.4 Agreed SHOULD-CONSIDER list

- Document the `isAgentContext` precondition and its consequence for the main
  repo (role: driver → agent_overrides skipped → `git merge` not blocked for
  builder there) (hy3 M4b).
- Correct the Reviewer/Auditor "same bash shape" description — auditor lacks
  `cargo *`/`npm *` (hy3 N2, Qwen L-02).
- Document `signing_enforcement: "audit"` semantics (Sonnet 5) and the
  sentinel block's purpose + latent config rot at hook-config.json:229
  (hy3 S3, kimi).
- Clarify the free-tier model policy vs the whitelist's six-live-model
  reality (Qwen L-05, hy3 S2).
- Add confidentiality/exfiltration scoping (`cat *` + `webfetch: allow` +
  env keys) (Qwen H-05, hy3 S6, ChatGPT).
- Document the `.claude/` exemption as trusted out-of-band state or an
  intentional control surface (ChatGPT #5, Qwen M-08).
- Explain the `mode: primary` vs `mode: subagent` contradiction between
  opencode.json and the agent .md files (hy3 M6).
- Separate "Failure it prevents" from "Failure it targets" in the §4 table
  (hy3 S7).
- Add automated tests for the guard plugins; fuzz the shell-parsing logic;
  empirically measure hook ordering and throw short-circuiting (ChatGPT,
  Qwen, GLM, hy3 S10, Deepseek #8).
- Protect the sentinel: verify active issue via Crosslink for sensitive
  operations, or make the sentinel read-only/signed (Qwen M-04, Deepseek #1).

---

## 5. Security-Property Invariants Proposed by Reviewers

The reviewers converged on a set of forward-looking invariants — a proposed
security argument for the system. These are **recommendations**, not current
properties; none is satisfied today except where noted.

### 5.1 ChatGPT's ten invariants (from the "Security properties and
adversarial test obligations" section)

1. **Reviewer/auditor direct-write invariant** — they cannot invoke any
   native or MCP filesystem mutation primitive. *Status: satisfied for the
   five blocked tool names (runtime-log-verified), NOT for
   create_directory/move_file (claim (d)).*
2. **Reviewer/auditor indirect-write invariant** — no command they are
   authorized to invoke can mutate project state. *Status: not satisfied*
   (`git *`, `cargo *`, `npm *`, `opencode *` families; claim (a)).
3. **Delegation invariant** — reviewer/auditor cannot cause a higher-authority
   role to mutate project state. *Status: not examined* (`crosslink kickoff`
   / `swarm` are in their `crosslink *` grant; the confused-deputy question
   is untested — ChatGPT #6, Qwen Scenario 2).
4. **Role-identity invariant** — a subagent cannot cause guard hooks to
   resolve its identity as a more privileged role. *Status: not satisfied*
   (claim (f): fail-open to builder; #204 history).
5. **Git integrity invariant** — non-builder roles cannot create commits,
   modify refs, rewrite history, or alter repository configuration. *Status:
   partially satisfied in agent contexts* (by_type blocks git commit for
   reviewer/auditor, and the configured destructive list); *not satisfied for*
   `git config`, `git update-ref`, `git checkout <path>` variants, and
   **not satisfied in the main repo context** where agent_overrides are
   skipped (claim (e)/(f); luna, hy3 M4b).
6. **Guard fail-closed invariant** — failure to determine agent identity
   blocks security-sensitive operations rather than merely logging. *Status:
   not satisfied* — the FAIL-CLOSED label describes logging, not posture
   (claim (f)).
7. **Configuration invariant** — every advertised security restriction has
   exactly one authoritative implementation path. *Status: not satisfied* —
   config lives in nine places (claim (l); ChatGPT #14).
8. **Dead-control invariant** — disabled/dormant security mechanisms cannot
   be mistaken for active enforcement. *Status: not satisfied* —
   `--allowedTools` is a dead control on the local path (claim (b)).
9. **Optimization independence invariant** — removing RTK changes
   performance/token consumption but never permissions. *Status: satisfied
   by design* (rtk-guard is fail-open and non-authoritative; rtk-guard.ts
   constants verified).
10. **Delegation-chain invariant** — a read-only role cannot obtain write
    authority transitively through Crosslink, opencode, shell commands, MCP,
    or another agent. *Status: not satisfied / untested* (claims (a), (d),
    (g); ChatGPT's "biggest conceptual issue").

### 5.2 Qwen's threat-model and control requirements

Qwen's §9 minimum remediation list, as forward-looking requirements:
1. Remove or qualify "read-only by construction".
2. Add an explicit threat model (10 classes listed in claim (k)).
3. Enumerate exact effective permissions for each role.
4. Replace broad `git *`/`opencode *`/`crosslink *`/`cargo *`/`npm *` grants
   for read-only roles with narrow, testable allowlists or sandboxed
   equivalents.
5. Protect enforcement config/plugins/sentinel/DB from Builder.
6. Make agent identity resolution fail closed.
7. Make the wrapper fail loudly when security flags are unsupported.
8. Add automated adversarial tests for each guard.
9. Add confidentiality and exfiltration controls.
10. Document and test the MCP surface.

### 5.3 Other reviewer-proposed invariants

- **RTK non-authoritative property (ChatGPT #4):** "Removing RTK entirely
  must not change the set of commands an agent is permitted to execute" —
  testable, and currently satisfied.
- **`git -C` normalization invariant (ChatGPT #11):**
  `git -C <arbitrary-repository> <blocked-command>` must be blocked exactly as
  `git <blocked-command>` is; shell parsing/quoting/newline-injection deserve
  a test matrix.
- **Hook-composition invariants (ChatGPT P1, hy3 S10):** empirically
  establish ordering between rtk-guard, crosslink-guard, and orchestrator-
  guard; test both orders; determine whether a `throw` in one handler
  short-circuits the others; determine behavior if a plugin fails to load or
  throws at import.
- **Sentinel trust invariant (Qwen M-04):** include issue ID, timestamp,
  session ID, and signature if a fast-path sentinel is used; verify against
  Crosslink for security-sensitive operations.
- **Log-integrity invariant (Qwen M-06):** security logs should move from
  `/tmp/*.log` (world-writable, deletable, non-durable) to a persistent,
  append-only or tamper-evident location with structured fields.
- **Tool/path integrity (Deepseek #6):** pin rtk by absolute path/checksum,
  re-verify binary identity, add startup integrity checks for wrapper,
  opencode fork, crosslink, rtk, and the global plugin.
- **Confidentiality scoping (Qwen H-05, hy3 S6):** treat "read-only" as an
  integrity property, not a confidentiality property; redact secrets from
  agent environments; deny webfetch for sensitive roles or add egress
  controls.

---

## 6. What-Not-Tested (all reviewers consolidated) and Open Questions

### 6.1 Consolidated WHAT-NOT-TESTED

**Runtime/bypass (no reviewer executed any bypass):**
1. `opencode run --pure --agent builder` writing a scratch file — the
   discriminating test for the plugin-bypass claim — not run (hy3 WNT 1;
   kimi WNT; original §6.4).
2. `cargo run`, `npm run <script>`, `git config core.hooksPath`,
   `git checkout -- <file>`, `git worktree add`, `git rm`, `git mv` — all
   read-from-source/CLI-help claims, not demonstrations (hy3 WNT 1).
3. Whether `--auto` actually converts an `ask` permission to allow vs only
   auto-consenting (hy3 WNT 5; kimi WNT).
4. Whether `task`-spawned subagents go through the `claude` wrapper (GLM 3B).

**Hook/plugin behavior:**
5. Runtime hook ordering between rtk-guard, crosslink-guard, orchestrator-
   guard; whether a `throw` short-circuits other handlers; plugin-load
   failure behavior (hy3 S10, WNT 2; original §6.3; ChatGPT P1).
6. Guard logs under `/tmp` not read for historical sessions (hy3 WNT 3).
7. No in-repo unit/integration test suite for any guard plugin (original
   §6.2; Deepseek #8; Qwen H-03 chaos tests).

**Deployment/version:**
8. Whether the deployed binary (a87bd513) differs behaviorally from source
   HEAD (6221309e) in `build_allowed_tools`/`build_agent_command` — only
   file-granularity confirmed (hy3 WNT 4).
9. Container image's `claude` binary / `--allowedTools` forwarding — not
   inspected (kimi WNT).
10. Live kickoff launch in any mode (original §6.4; kimi WNT).

**Identity:**
11. Forced removal/corruption of `chat.params`, `CROSSLINK_AGENT_TYPE`, and
    hook-config agent.type — not tested; whether the fallback path has ever
    fired in production — not observed (hy3 WNT 3; Qwen Scenario 5).
12. Whether opencode exposes `apply_patch` under that exact name (kimi WNT).

**MCP / config:**
13. Whether `create_directory`/`move_file` are exposed as `filesystem_`-
    prefixed tools (0 log entries; inferred, never invoked — this
    verification's WNT for claim (d)).
14. Whether enabling the MCP `sqlite` server would unblock the #313 auditor
    (hy3 S4).
15. Whether `models-cache.json` currently re-enables any disabled provider
    (luna/kimi flagged the risk; not audited).
16. Whether the 34/33 orchestrator-pattern discrepancy changes any behavior
    (count-only documentation error).

**Process/history:**
17. Whether the opencode fork's `98dfe4a`/`llm.ts` fix is externally
    confirmed (Sonnet 5; hy3 WNT 6 — fork source not reviewed).
18. tripn-astro / Tools repo hook-config drift not checked (hy3 WNT 6).
19. Workflow Topology Design record not read in full by kimi (kimi WNT).

**Epistemic boundaries (luna, hy3, ChatGPT):**
20. Luna did not launch a live kickoff, inspect installed binary internals,
    run plugin hooks, or test unlisted git mutators; did not independently
    verify deployment version/DB sizes/#313 comments/user-level timeout
    config.
21. hy3 confirmed quotes verbatim but not truth (P4: "confirmed the comment
    exists" vs "confirmed the comment is true").

### 6.2 Open questions

1. **What is the intended threat model?** Mistaken agent vs misaligned agent
   (hy3 S1; Qwen C-05) — a policy decision the operator must make; every
   security claim's severity depends on it.
2. **Which mode wins at runtime — opencode.json `subagent` or .md `primary`?**
   (hy3 M6).
3. **Should reviewer/auditor git be deny-by-default?** The bounded-blocklist
   guarantee vs a deny-by-default git policy (luna MUST FIX).
4. **Should the auditor get read-only sqlite3?** How, safely? (Qwen M-03;
   #313 recommendation).
5. **Should the enforcement config be protected from the builder?** Via
   read-only mounts, separate users, or a trusted computing base (Sonnet 5,
   Deepseek, Qwen C-02).
6. **Should the wrapper fail loudly on unsupported security flags?** (Qwen
   C-04; ChatGPT #9's dead-control concern).
7. **Is `--allowedTools` worth completing end-to-end?** If enforced, it must
   be per-role and least-privilege; as-is it is a false-assurance surface
   (ChatGPT #9/#10; Deepseek #3).
8. **Should model enforcement move inside opencode/crosslink-guard** instead
   of the bypassable wrapper (Qwen H-04)?
9. **What is the operator's risk tolerance for confidentiality?** Read +
   egress (webfetch) is unaddressed (Qwen H-05, hy3 S6).

---

## 7. Verified-Sources Appendix

All claims in this document were verified on 2026-08-09 against:

### 7.1 Repository files (this worktree unless noted)

1. `.opencode/opencode.json` — agent map (`mode` values: orchestrator
   `primary`, builder/reviewer/auditor `subagent`), plugin list (lines 4-8),
   MCP config (lines 27-45: filesystem enabled, rooted at
   `/home/claude-code/projects/ASES`; sqlite/github/playwright/cloudflare
   disabled).
2. `.opencode/agents/{orchestrator,builder,reviewer,auditor}.md` — permission
   frontmatter; counts (34 orchestrator allow patterns), bash grants
   (reviewer incl. cargo/npm; auditor without), `mode: primary` in all four.
3. `.opencode/plugins/orchestrator-guard.ts` — `BLOCKED_TOOLS` (5 names),
   `ALLOWED_AGENTS`, per-session agent map, no env fallback.
4. `.opencode/plugins/crosslink-guard.ts` (1220 lines) — steps 1-10 control
   flow (lines 967-1216), `isAgentContext` (239-258), `loadConfigMerged`
   + `hook-config.local.json` overlay (283-331), `agent_overrides` gate
   (395), `resolveAgentType` default builder (453-465), runtime resolution
   + FAIL-CLOSED logs (859-925), allow-fast-path (1141-1147), relaxed allow
   (1152-1155), sentinel allow (1170-1181), kill/pause fail-open (605).
5. `.opencode/plugins/rtk-guard.ts` (415 lines) — constants
   (V1_VALIDATED, 200/15ms/500, 0.40.0, RTK_DISABLED), fail-open gates.
6. `.crosslink/hook-config.json` — 49 allowed_bash_prefixes (127-177), 21
   agent_overrides blocked (15-37), by_type (41-124; no builder entry), 14
   root blocked (179-194), gated `git commit` (197-199), tracking modes
   (125/232), comment_discipline (195), kickoff_verification (201),
   signing_enforcement (230), sentinel block (203-228, enabled:false),
   stray `sentinel.default_agent.model` (229), `agent.type: builder` (8).
7. `.crosslink/agent.json` (this worktree) — `role: "agent"`.
8. `/home/claude-code/projects/ASES/.crosslink/agent.json` (main repo) —
   `role: "driver"` (hy3 M4b precondition verified).
9. `.crosslink/.active-issue` — sentinel, content "320" (both worktree and
   main repo).
10. `.opencode/permissions.md` — STALE snapshot (says OpenCode 1.18.11,
    omits sleep/ps/tmux grants); NOT source of truth.
11. `docs/research/Workflow Topology Design and Reasoning Record.md` —
    referenced as design context (not re-read in full by this verification;
    kimi WNT 19).
12. `.crosslink/knowledge/model-discipline.md` — model rules.
13. `docs/research/agent-tooling-and-permission-enforcement.md` @
    `4cbae854` — the original, unmodified.
14. `docs/research/review-inbox/agent-tooling-and-permission-enforcement-reviews.md`
    @ `368cb6c6` — the 5 external reviews, verbatim.

### 7.2 External binaries, configs, and runtime evidence

15. `crosslink --version` → `crosslink 0.9.0-beta.1+a87bd513` (deployed).
16. `/home/claude-code/projects/crosslink` source — `git describe --tags` →
    `v0.9.0-beta.1-59-g6221309e`; `git show --stat 6221309e` (delta in
    launch.rs +59, prompt.rs +12, plus others).
17. `/home/claude-code/projects/crosslink/crosslink/src/commands/kickoff/prompt.rs`
    — `build_allowed_tools` (lines 429-473; 22-entry base list; no
    agent_type param).
18. `/home/claude-code/projects/crosslink/crosslink/src/commands/kickoff/helpers.rs`
    — `read_kickoff_allowed_tools` (returns empty, no `kickoff` key),
    `detect_conventions`/`has_manifest` (one-level-deep, skip list).
19. `/home/claude-code/projects/crosslink/crosslink/src/commands/kickoff/launch.rs`
    — `build_agent_command` (255-330: `--allowedTools`,
    `--permission-mode`/`--dangerously-skip-permissions`, `CLAUDE_CONFIG_DIR`),
    local tmux requirement (353-366), container path (1000-1035: passes
    `--allowedTools` directly).
20. `~/.local/bin/claude` — wrapper: model enforcement (42-57), `--allowedTools`
    dropped (28-30), `--auto` under tmux (66-67),
    `--dangerously-skip-permissions` → `--auto` (21-24), systemd-run memory
    scope, `CROSSLINK_AGENT_TYPE` export.
21. `opencode --version` → `1.18.13-pp3g-fork`.
22. `opencode run --help` — `--pure` (run without external plugins), `--auto`
    (auto-approve permissions not explicitly denied — dangerous!); **no**
    `--allowedTools` flag.
23. `opencode models opencode` — 6 models: big-pickle,
    deepseek-v4-flash-free, laguna-s-2.1-free, mimo-v2.5-free,
    nemotron-3-ultra-free, north-mini-code-free (ling-3.0-flash-free absent).
24. `~/.config/opencode/plugins/plugin.ts` — freeZenModels (7 incl.
    ling-3.0-flash-free), disabled/hidden providers, vertex emptied,
    models-cache merge (42-63, no disabled filter).
25. `rtk --version` → `0.40.0`; `~/.cargo/bin/rtk`.
26. `~/.local/share/opencode/*.db` — fork 1,213,251,584 B, main
    2,598,903,808 B, local 1,081,344 B (2026-08-09).
27. `/tmp/orchestrator-guard.log` — runtime tool-name evidence:
    `filesystem_write_file` (51), `filesystem_edit_file` (107), `edit`
    (1213), `write` (372), `apply_patch` (1); zero create_directory/move_file
    entries.
28. Issue #313 comment stream — verbatim auditor quotes (15:01 [PROGRESS],
    15:02 [result], 15:03 [handoff]); builder inventory plan (14:29);
    free-tier 401 failure (14:56).
29. Issue #315 (luna), #316 (hy3), #317 (kimi), #319 (Gemini synthesis),
    #314 (original task) — review records as cited.

### 7.3 What was NOT re-verified for this document

- The opencode fork source (`98dfe4a`/`llm.ts`) — second-hand via #156
  (hy3 WNT 6; Sonnet 5's single-incident concern stands).
- tripn-astro / Tools repository hook-config values (hy3 WNT 6).
- The contents of `~/.config/opencode/models-cache.json` (cache-re-enable
  risk flagged, not audited).
- Historical plugin logs for the #313 session (which layer blocked sqlite3).
- Any live bypass demonstration (all bypass claims are capability
  inferences).

---

## Appendix: How to check the key claims in under five minutes

```bash
# 1. Deployed vs source version (claim c)
crosslink --version                       # 0.9.0-beta.1+a87bd513
git -C /home/claude-code/projects/crosslink describe --tags   # v0.9.0-beta.1-59-g6221309e

# 2. Countable claims (claim i)
python3 -c "import json;print(len(json.load(open('.crosslink/hook-config.json'))['allowed_bash_prefixes']))"   # 49
python3 -c "import json;print(len(json.load(open('.crosslink/hook-config.json'))['agent_overrides']['blocked_git_commands']))"  # 21
# bash allow patterns only (excludes the 3 task: allow lines):
awk '/^  bash:/{f=1;next} /^  task:/{f=0} f && /: "allow"/{c++} END{print c}' .opencode/agents/orchestrator.md  # 34

# 3. MCP tool names (claim d)
grep -c 'filesystem_write_file' /tmp/orchestrator-guard.log    # 51
grep -c 'filesystem_edit_file'  /tmp/orchestrator-guard.log    # 107
grep -c 'create_directory\|move_file' /tmp/orchestrator-guard.log  # 0

# 4. Wrapper behavior (claims b, h)
grep -n 'allowedTools' ~/.local/bin/claude                     # shift 2 (drop)
grep -n '\-\-auto' ~/.local/bin/claude                         # tmux injection

# 5. Identity fallback (claim f)
grep -n '"type": "builder"' .crosslink/hook-config.json       # agent.type default
grep -n 'by_type' .crosslink/hook-config.json                  # no builder key

# 6. Native bash grants (claim a)
grep -nE 'git \*|opencode \*|cargo \*|npm \*' .opencode/agents/reviewer.md .opencode/agents/auditor.md

# 7. isAgentContext precondition (claim e/f)
grep -n '"role"' /home/claude-code/projects/ASES/.crosslink/agent.json   # "driver"
```
