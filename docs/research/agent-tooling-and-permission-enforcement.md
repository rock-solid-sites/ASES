---
title: Agent Tooling and Permission Enforcement — Current State
program: EDASES
layer: Research
document_type: Report
status: Active
authority: Experimental
canonical_repository: edases

related_documents:
  - docs/research/Workflow Topology Design and Reasoning Record.md
  - .opencode/permissions.md
  - .crosslink/knowledge/model-discipline.md
  - .crosslink/knowledge/crosslink-fork.md
  - docs/ORCHESTRATOR.md

supersedes: []

last_updated: 2026-08-09
---

# Agent Tooling and Permission Enforcement — Current State

> **Purpose.** This document is a self-contained, current-state write-up of the
> agent tooling and permission-enforcement system used in the ASES repository.
> It is written for **external review** — a reader with zero prior context of
> this repository must be able to understand: the software stack, what the
> system is trying to achieve, why each tool and plugin exists, and the
> problem areas that have been identified.
>
> **Sources.** Every claim below was verified against the live sources listed
> in §7. Issue and PR numbers refer to the Crosslink issue tracker (see §2.2).
> Where a fact is an observation about a live deployment rather than a
> guaranteed invariant, it is marked as such. What was explicitly **not**
> tested is collected in §6.

---

## 1. Purpose

### 1.1 The problem this system addresses

ASES runs a multi-agent software-engineering workflow in which an **operator**
(a human) supervises a small set of AI agents with distinct roles. The roles
are separated by **authority**: only one role may modify project files; the
other roles exist to verify, review, and coordinate. For this separation to be
meaningful, the enforcement must be **structural** — permissions enforced by
the tooling — rather than merely requested in prose. An agent that is told
"you are read-only" but is physically able to write files is not read-only.

The system therefore layers several independent enforcement mechanisms on top
of an AI-agent harness. Understanding the system means understanding each
layer, why it exists, and how the layers interact (and sometimes fail to
interact).

### 1.2 The four-role permission model

Four agent roles are defined (`.opencode/opencode.json`, `.opencode/agents/*.md`):

| Role | Mode | Writes files? | Git write | Job |
|------|------|---------------|-----------|-----|
| **Orchestrator** | primary | **No** (edit deny) | `git commit` + `git merge` gated on an active issue; push/rebase/reset/clean/checkout/restore/stash/tag blocked | Plans, delegates via `crosslink kickoff`/`swarm`, coordinates the other three, maintains tracking state. Never implements, reviews, or audits. |
| **Builder** | subagent | Yes | `git commit` gated on an active issue; everything destructive blocked | Implements approved work, modifies project files. |
| **Reviewer** | subagent | **No** (edit deny) | all git writes blocked (read-only) | Deep read-only review of implementation output; produces findings. |
| **Auditor** | subagent | **No** (edit deny) | all git writes blocked (read-only) | Project-level evaluation of outcome **and** process; independent of implementation and review. |

The asymmetry is deliberate: **reviewer and auditor are read-only by
construction**, and the enforcement is intended to make that a property of the
tooling, not a suggestion. The orchestrator's write path is also blocked at
the tool level (not just by instruction) so it cannot silently become an
implementer.

### 1.3 Workflow-topology design context: the pre-positioned auditor

The role topology is not arbitrary; it is the operationalization of a
research design recorded in
`docs/research/Workflow Topology Design and Reasoning Record.md`. Key elements:

- **Position-emitting agents + durable store.** Every agent emits structured
  position updates (`step`, `completed`, `next`, `blocker`) as comments on its
  Crosslink issue. The store is durable (it survives agent restarts) so that
  the auditor can check claims *after* the producer is gone.
- **Cheap staleness trigger.** A position/heartbeat stale for >2× its expected
  interval triggers investigation.
- **AUDITOR as one-role/two-phase divergence verifier.** The auditor is
  re-positioned from a post-hoc final gate to an **in-flight divergence
  verifier**: trigger-invoked, read-only, joining position claims against
  artifact evidence, and flagging divergence to the orchestrator. Phase 1 is
  the in-flight monitor ("is work on track *as claimed*?"); Phase 2 is the
  post-hoc audit ("did outcome *and* process hold up?").
- **Reviewer as pre-consumption readiness audit.** The reviewer verifies the
  artifact *admits verification* and carries the required calibration
  (WHY / WHAT / HOW-CERTAIN / WHAT-NOT-TESTED), rather than "verifying the
  truth" of the work.
- **Orchestrator as single integration point.** The operator supervises the
  orchestrator, which owns the bounded action set (investigate/nudge/
  stop-resume) and surfaces only decisions to the operator.

The motivating incident for this design is the **binary-vs-source
misattribution** from the reliability epic (#156): an agent claimed the
compiled binary "lacked" a fix the source had, implying a build defect. The
claim drove a full investigation chain (rebuild, matrix verification, a
dedicated compile-divergence investigation) before the root cause was found:
the binary was byte-faithful and the real defect was a consumption deadlock in
`llm.ts`. The producer could have run the cheapest discriminating test (run
the source, compare hang behavior — the E3 parity test that finally collapsed
the hypothesis in minutes); nobody did until the end. The workflow topology is
the structural response to that failure class.

### 1.4 Git write discipline

All git writes are governed by a single rule set, enforced by the
`crosslink-guard` plugin (see §3.3) with lists configured in
`.crosslink/hook-config.json`:

- **Permanently blocked** for every role: `git push` (incl. `--force`/`-f`),
  `git rebase`, `git cherry-pick`, `git reset`, `git clean`, `git checkout .`,
  `git restore .`, `git stash`, `git tag`, `git am`, `git apply`,
  `git branch -d/-D/-m`. Pushing is the operator's job.
- **Gated on an active Crosslink issue** (strict mode also requires a `--kind
  plan` comment): `git commit` for builder and orchestrator.
- **Orchestrator-only addition**: `git merge` is gated for the orchestrator
  (it coordinates merges); builder may not merge.
- **Read-only git** (`status`, `diff`, `log`, `show`, `branch`, `worktree
  list`) is always allowed.

The rationale: git history is the durable audit trail; the human performs all
remote/destructive git operations. Agents may only create commits that are
traceable to an active issue.

### 1.5 Model discipline

Model selection is treated as a failure-prone decision and governed by hard
rules (`.crosslink/knowledge/model-discipline.md`):

- **Never assume a model ID** — verify with `opencode models <provider>`
  before use; copy IDs exactly.
- **Ask the operator which provider to use**; do not choose a provider
  autonomously.
- **Do not use free-tier (Zen) models for agent/kickoff/swarm work** — they
  are rate-limited and opaque, and a launch may hang or fail mid-task. Paid
  `opencode-go/*` models are the production-grade default for agents.
- **Failure discrimination**: a stalled agent is not assumed to be
  rate-limited; the opencode log is checked for the error signature
  (429/rate-limit vs silent hang = outgoing stream with no response and no
  error).

---

## 2. Software Stack

### 2.1 opencode (forked as `1.18.13-pp3g-fork`)

- **What it is.** opencode is the AI-agent harness/TUI that runs the agents.
  It loads agent definitions from `.opencode/agents/*.md` (via the agent map
  in `.opencode/opencode.json`), enforces each agent's permission frontmatter,
  and provides the tools the agent can call (read/write/edit/bash/glob/grep/
  task/webfetch, MCP servers, etc.).
- **The pp3g fork.** The deployed binary reports version `1.18.13-pp3g-fork`
  (`opencode --version`). The fork exists because of the **silent-hang
  reliability epic** (#156): stock opencode would hang on certain provider
  stream errors (a consumption deadlock in `llm.ts` — an
  `effect Stream.fromAsyncIterable` scope finalizer awaiting `iter.return()`
  that rejects/hangs after a stream error). The fork's durable fix was a
  fire-and-forget `safeIterable()` return in `llm.ts` (commit `98dfe4a`),
  plus the request-timeout configuration described in §2.7.
- **Separate session database.** The fork writes sessions to a **separate
  SQLite database** (`opencode-fork-pp3g.db` in `~/.local/share/opencode/`),
  via a baked-in channel name (`fork-pp3g` → `opencode-<channel>.db`). The
  stock/main history lives in `opencode.db`. This split was characterized in
  #313: the fork binary does not read the main DB (the "sessions gone" report
  after a crash was traced to this), and at inventory time the fork DB was
  ~1.13 GB dominated (~90%) by a single session's event table. A third,
  `opencode-local.db`, also exists.

### 2.2 crosslink fork CLI (Rust)

- **What it is.** crosslink is the issue tracker + agent-orchestration CLI
  used for all tracking in this project. It provides: issues/comments with
  `--kind` semantics (plan/observation/blocker/result/handoff/…), sessions and
  locks, a durable hub for state sync, `kickoff run` (launch a background
  agent in a tmux session or container) and `swarm` (parallel agents), agent
  identity/signing, and the guard-hook configuration consumed by the plugin
  chain.
- **Version.** The deployed binary is built from
  `/home/claude-code/projects/crosslink` (a fork of crosslink),
  `v0.9.0-beta.1-59-g6221309e`.
- **Kickoff surface.** The fork's `kickoff` command builds the launch
  command for each agent; it also builds a `--allowedTools` CLI allowlist
  string (§3.6) and a `KICKOFF.md` prompt file. The three relevant source
  files are `src/commands/kickoff/{prompt.rs,helpers.rs,launch.rs}` (§7).

### 2.3 The `claude` wrapper (bash)

- **What it is.** `claude` on PATH is a ~86-line bash wrapper at
  `~/.local/bin/claude` that translates Anthropic-claude CLI arguments into
  `opencode run` invocations. It is not the real Claude Code binary.
- **Strict model enforcement.** The wrapper rejects launches whose `--model`
  is missing or an implicit/default Anthropic name (`opus`/`sonnet`/`haiku`)
  with a fatal error listing allowed providers. Every agent launch must pass
  an explicit verified model ID.
- **Memory scoping.** Inside tmux (the kickoff case) it wraps the launch in
  `systemd-run --scope --user` with `MemoryMax`/`MemoryHigh` caps to prevent
  a session's subagents from OOMing the box.
- **Agent-type export.** When `--agent <type>` is present it exports
  `CROSSLINK_AGENT_TYPE=<type>` so the `crosslink-guard` plugin can apply
  per-agent-type overrides (§3.3).
- **Observation (verified):** the wrapper currently **drops** `--allowedTools`
  (consumes the argument without forwarding it), and `opencode run --help`
  exposes no `--allowedTools` flag. The fork builds the string (§3.6) but it
  has no enforcement effect through the current wrapper. See §5.1/§6.

### 2.4 rtk (token-saving bash proxy)

- **What it is.** `rtk` (v0.40.0, `~/.cargo/bin/rtk`) is a CLI proxy that
  rewrites bash commands into lower-token forms (`rtk rewrite <cmd>`; `rtk
  read` maps `cat` to filtered reads). Claude Code's native PreToolUse hook
  performed this rewriting; opencode cannot run that hook, so this repository
  restores the behavior with a plugin (§3.4).

### 2.5 sqlite3 (databases)

The harness and tracker store state in SQLite:

- `~/.local/share/opencode/opencode.db` — main opencode session/message store
  (2.42 GiB at #313 inventory).
- `~/.local/share/opencode/opencode-fork-pp3g.db` — the fork's separate
  session store (live; ~1.13 GiB at #313 inventory).
- `~/.local/share/opencode/opencode-local.db` — a smaller local store.
- `.crosslink/issues.db` — crosslink's per-worktree issue/comment/session DB
  (synced to the hub).
- `.crosslink/.hub-cache/issues.db` — hub-side cached issue store.

### 2.6 The three in-repo guard plugins (TypeScript)

`.opencode/opencode.json` loads three plugins from `.opencode/plugins/`
(run inside the Bun runtime opencode provides):

| Plugin | File | Job |
|--------|------|-----|
| **orchestrator-guard** | `.opencode/plugins/orchestrator-guard.ts` | Closes the `edit:deny` gap (opencode issue #33677): blocks native write/edit/`apply_patch` and MCP `filesystem_write_file`/`filesystem_edit_file` at the `tool.execute.before` hook for every agent except the Builder. |
| **crosslink-guard** | `.opencode/plugins/crosslink-guard.ts` | Git discipline (blocked/gated lists), active-issue gating, bash allowlist, issue-comment discipline, operator kill/pause flags, per-agent-type overrides. Config comes from `.crosslink/hook-config.json`. |
| **rtk-guard** | `.opencode/plugins/rtk-guard.ts` | Transparently rewrites eligible bash calls through `rtk rewrite` to save tokens; strictly fail-open (never blocks, never throws). |

### 2.7 The user-level model-whitelist plugin

`~/.config/opencode/plugins/plugin.ts` is a user-level (global) opencode
plugin that mutates the resolved config at startup:

- disables and hides providers `openai`, `deepseek`, `cloudflare`,
  `cloudflare-ai-gateway` (empty their model maps);
- **whitelists** the `opencode` (Zen/free) provider to exactly seven free
  models (`big-pickle`, `deepseek-v4-flash-free`, `laguna-s-2.1-free`,
  `ling-3.0-flash-free`, `mimo-v2.5-free`, `nemotron-3-ultra-free`,
  `north-mini-code-free`);
- empties `vertex`'s model map;
- merges provider metadata from `~/.config/opencode/models-cache.json`.

The rationale is **provider hygiene**: paid Zen models are not exposed because
no Zen credits are used, and the free-model set is deliberately constrained
(the whitelist was introduced for issue #103). Related: per-API-request
timeouts for providers `opencode`/`opencode-go` live in the user-level
`~/.config/opencode/opencode.json` (60 min full-request backstop; 5 min
header/chunk timeouts) — deliberately user-level so they reach every kickoff
agent.

### 2.8 Where the pieces live

```
ASES repo:
  .opencode/opencode.json            agent map, plugin list, MCP config
  .opencode/agents/{orchestrator,builder,reviewer,auditor}.md   permission frontmatter
  .opencode/plugins/{orchestrator-guard,crosslink-guard,rtk-guard}.ts
  .opencode/permissions.md           snapshot of the four role maps (NOT source of truth)
  .crosslink/hook-config.json        guard config: bash allowlist, git lists, by_type overrides
  .crosslink/knowledge/model-discipline.md
  docs/research/Workflow Topology Design and Reasoning Record.md

Outside the repo:
  ~/.local/bin/opencode               the pp3g fork (1.18.13-pp3g-fork)
  ~/.local/bin/claude                 bash wrapper → opencode run
  ~/.local/bin/crosslink              crosslink fork CLI (Rust)
  ~/.cargo/bin/rtk                    rtk 0.40.0
  ~/.config/opencode/plugins/plugin.ts  user-level model whitelist
  ~/.config/opencode/opencode.json   user-level request timeouts
  ~/.local/share/opencode/*.db        opencode session stores
  /home/claude-code/projects/crosslink  crosslink fork source
```

---

## 3. Enforcement Layers

This section describes the full enforcement chain, in the order a tool call
experiences it. The layers are **additive**: a call must survive every layer
that applies to it.

### 3.1 (a) opencode native permission engine (agent `.md` frontmatter)

Each agent definition carries a `permission:` frontmatter block. opencode's
native engine evaluates it before tool execution. Examples (verbatim shapes):

- **Orchestrator** (`orchestrator.md`): `edit: deny`; `bash: {"*": "deny",
  "crosslink *": "allow", "opencode models *": "allow", "git status *":
  "allow", …, "git commit *": "allow", "git merge *": "allow", "ls *":
  "allow", "cat *": "allow", "rtk *": "allow", …}` (~40 explicit allow
  patterns, including scoped read-only tools `ps -o`, `pgrep`, tmux
  list/capture, `stat`, `diff`, `free`, `df`, `uptime`, `curl -I`,
  `curl --head`); `task: {"*": "deny", "builder": "allow", "reviewer":
  "allow", "auditor": "allow"}`; `question: allow`; `webfetch: deny`;
  `websearch: deny`.
- **Builder** (`builder.md`): `edit: allow`; `bash: allow` (unrestricted);
  `external_directory: {"*": "ask", "/tmp/*": "allow"}`; `task: deny`;
  `question: ask`; `webfetch/websearch: allow`.
- **Reviewer** (`reviewer.md`): `edit: deny`; `bash: {"*": "deny",
  "crosslink *": "allow", "opencode *": "allow", "git *": "allow", "ls *":
  "allow", "cat *": "allow", "cargo *": "allow", "npm *": "allow",
  "rtk *": "allow"}`; `task: deny`; `question: deny`; `webfetch: allow`;
  `websearch: deny`.
- **Auditor** (`auditor.md`): same bash shape as reviewer (`crosslink *`,
  `opencode *`, `git *`, `ls *`, `cat *`, `rtk *`); `edit: deny`; `task:
  deny`; `question: deny`; `webfetch: allow`; `websearch: deny`.

**Important limitation (the #33677 gap):** in opencode, `edit: deny` alone
does **not** block the native write/edit/`apply_patch` tools or the MCP
`filesystem_write_file`/`filesystem_edit_file` tools — they succeed
regardless. This is the gap closed by the orchestrator-guard plugin (§3.2).
Also note that the reviewer/auditor bash blocks are **broader than** the
bash-allowlist surfaces described below (§5.3).

### 3.2 (b) orchestrator-guard plugin (write blocking)

Because of the #33677 gap, a second layer exists: `orchestrator-guard.ts`
hooks `tool.execute.before` and throws for the tools
`write`, `edit`, `apply_patch`, `filesystem_write_file`, `filesystem_edit_file`
unless the resolved agent is `builder` (`.opencode/plugins/orchestrator-guard.ts:33-41`).

Implementation detail: the plugin tracks the current agent via `chat.params`
**keyed by sessionID** (`agentBySession` map), because one opencode process
hosts multiple sessions (the interactive session plus Task-tool subagents) and
a shared scalar would be clobbered by the most recent subagent event — the
same defect fixed in crosslink-guard for the #204 git-merge regression.

### 3.3 (c) crosslink-guard plugin (git / bash / issue discipline)

`crosslink-guard.ts` is the native-TypeScript successor of crosslink's Python
`work-check.py` PreToolUse hook. On every `write`/`edit`/`bash` call it
applies, in priority order:

1. **Operator kill/pause flags** — `crosslink agent flags --strict`; exit
   code 2 with `kill`/`paused` state throws a hard block.
2. **`~/.claude/` exemption** for write/edit (Claude Code's own memory path).
3. **Permanently blocked git commands** (from config, normalized — global
   flags like `-C`, `--git-dir` are stripped so `git -C /x push` → `git
   push`; chained commands split on `&&`, `;`, `|`).
4. **Gated git commands** (`git commit`): requires an active issue (fast path
   via the `.active-issue` sentinel file, slow path via `crosslink session
   status`) and, under `required`/`encouraged` comment discipline, a `--kind
   plan` comment on the issue.
5. **Issue-close comment discipline**: closing an issue requires a `--kind
   result` comment.
6. **Allowed bash pass-through**: if every sub-command matches
   `allowed_bash_prefixes`, allow.
7. **Relaxed tracking mode**: no issue-tracking enforcement (this is how
   agent worktrees run; see below).
8. **No crosslink dir**: cannot enforce, allow.
9. **Active-issue enforcement** (strict/normal): sentinel or session-status
   check; strict mode throws the hard block, normal mode reminds.
10. **No active work item**: by tracking mode.

**Config source.** All lists come from `.crosslink/hook-config.json`
(root-level `allowed_bash_prefixes`, `blocked_git_commands`,
`gated_git_commands`, `comment_discipline`, `tracking_mode`) with a
`hook-config.local.json` overlay supporting `+key` array-extension. Root
tracking mode is `strict`; agent contexts switch to `relaxed` via
`agent_overrides.tracking_mode: "relaxed"` (agents are allowed to work
without re-checking issue state on every call because the worktree itself is
tied to an issue).

**Per-agent-type overrides.** `agent_overrides.by_type.<type>` replaces the
blocked/gated lists per role (`orchestrator` gets `git merge` gated;
`reviewer` and `auditor` get `git commit` **blocked** — the read-only
guarantee). The runtime agent is resolved per sessionID from `chat.params` /
`chat.message`, falling back to `CROSSLINK_AGENT_TYPE`, then
`hook-config agent.type` (default `builder`). The plugin logs explicit
FAIL-CLOSED warnings when resolution falls back (no chat hook seen and no
env).

**Runtime agent tracking.** Like orchestrator-guard, agent identity is keyed
by sessionID, not a module scalar — a shared variable was proven to be
clobbered by subagent `chat.params` events (the #204 regression: an
orchestrator merge was hard-blocked at 03:24:15 because a reviewer
subagent's event had overwritten the shared value).

### 3.4 (d) rtk-guard plugin (bash rewrite proxy)

`rtk-guard.ts` hooks `tool.execute.before` for `bash`, and — when safe —
mutates `output.args.command` to prepend `rtk` via `rtk rewrite <command>`.
It is **strictly fail-open**: no path throws or blocks; every error degrades
to passing the original command through. Safety gates in order:

1. Loop guard — skip if already `rtk`-wrapped.
2. Opt-out — `RTK_DISABLED=1` env or command prefix.
3. **Unattestable-construct scan** (quote-aware): rejects commands containing
   `$()`, backticks, `>`, `<`, `sudo`, `env` (bash evaluates `$()`/backticks
   even inside double quotes).
4. **Binary gate** (once per session): resolve `rtk` (PATH first, hardcoded
   fallback only when `which` itself is unavailable), require version
   ≥ 0.40.0, and require `rtk rewrite "git status"` to return output starting
   with `rtk ` (integrity probe). Any failure → no-op mode for the session.
5. **Latency gate**: rolling p95 over the last 200 calls; > 15 ms disables
   live mode, re-checked after 500 calls.
6. **Validated allowlist**: only rewrite commands whose leading token is in
   `V1_VALIDATED = {git, ls, grep, find, diff, wc, cat}`.
7. Mutate the command; audit-log when `RTK_HOOK_AUDIT=1`.

**Interaction with crosslink-guard (§3.3):** crosslink-guard's command
matching strips leading `rtk ` prefixes (`isSingleCommandAllowed`,
`normalizeGitCommand`), so an already-`rtk`-prefixed command is matched
against the git/allowlists as if unprefixed. The exact hook-ordering
behavior of the two plugins in the same process is an open question (§6).

### 3.5 (e) hook-config.json as the single config source

`.crosslink/hook-config.json` is the config source for the guard layers:

- `allowed_bash_prefixes` (29 entries): `crosslink `, `opencode `, read-only
  git, `jj *`, cargo/npm/npx/tsc/node/python toolchains, `ls`, `dir`, `pwd`,
  `echo`, `rtk read`, `ps -o `, `pgrep `, tmux list/capture/display,
  `grep `, `tail `, `head `, `wc `, `stat `, `diff `, `free `, `df `,
  `uptime `, `date `, `which `, `env `, `git worktree list`, `git -C`,
  `curl -I`, `curl --head`.
- `blocked_git_commands` (root, 14 entries) and `agent_overrides`
  (19 entries incl. `git push --force`/`-f`, `git reset --hard`, `git
  checkout .`, `git restore .`).
- `gated_git_commands: ["git commit"]`.
- `agent_overrides`: `agent_lint_commands: ["shellcheck **/*.sh"]`,
  `agent_test_commands: []`, `by_type` per-role blocked/gated lists,
  `tracking_mode: "relaxed"`.
- `comment_discipline: "encouraged"`, `tracking_mode: "strict"` (root),
  `kickoff_verification: "local"`, `signing_enforcement: "audit"`,
  `sentinel` block (default model `opencode-go/deepseek-v4-pro`, escalation
  model `claude-opus-4-6`, currently `enabled: false`).

There is **no `kickoff` key** in this file — `kickoff.allowed_tools` is
unset in ASES (verified in both the worktree and the main repo config),
so `read_kickoff_allowed_tools()` returns an empty list (§3.6).

### 3.6 (f) the KICKOFF path: the fork's `--allowedTools` surface

When the orchestrator launches an agent via `crosslink kickoff run`, the fork
constructs the launch command (`launch.rs::build_agent_command`):

```
timeout <backstop>s env -u CLAUDECODE claude --model <model> --agent <type>
  --allowedTools '<list>' -- "$(cat KICKOFF.md)"
```

(backstop = `max(timeout*24, 24h)` — a destroyer guard, never a task kill).

The `--allowedTools` string is built by `prompt.rs::build_allowed_tools` from
three inputs:

1. **Base list** (always): `Read, Write, Edit, Glob, Grep, Skill, Task,
   WebSearch, WebFetch, Bash(git *), Bash(ls *), Bash(mkdir *), Bash(test *),
   Bash(which *), Bash(touch *), Bash(cat *), Bash(head *), Bash(tail *),
   Bash(wc *), Bash(diff *), Bash(echo *), Bash(crosslink *)`.
2. **CI tools** (`gh *`, `sleep *`) when verification level is `ci`/`thorough`.
3. **Convention-detected project tools** from `helpers.rs::detect_conventions`
   (manifest-based, one directory level deep): Rust → `Bash(cargo *)` +
   clippy/fmt lint commands; Node → `Bash(npm *)`, `Bash(npx *)`; Python →
   `Bash(uv *)`, `Bash(python3 *)`, `Bash(pytest *)`; Go → `Bash(go *)`;
   Just/Make; Shell → `Bash(shellcheck *)`, `Bash(bash *)`, `Bash(bats *)`;
   Elixir → a large `mix *` set — plus any project-supplied
   `kickoff.allowed_tools` entries from hook-config (currently none in ASES).

**Key properties of this surface:**

- It is built **independently of the agent `.md` permission blocks** — a
  separate surface with its own matching semantics (tool-name patterns like
  `Bash(git *)`, the Claude-Code style).
- It is built **identically for all agent types** — `build_allowed_tools`
  takes `(conventions, verify)` and has no `agent_type` parameter. The
  `--agent <type>` flag changes only which `.md` block loads and which
  `by_type` git lists crosslink-guard applies; it does not change the tool
  surface.
- **In the current deployment it is constructed but not enforced**: the
  `claude` wrapper drops `--allowedTools` and `opencode run` has no such
  flag (verified). The effective enforcement surfaces for a kickoff agent are
  therefore the `.md` block (§3.1), orchestrator-guard (§3.2), crosslink-guard
  (§3.3), and rtk-guard (§3.4). See §5.1 and §6.

---

## 4. Why This Set — Each Component's Job and the Failure It Prevents

| Component | Failure it prevents | Evidence |
|-----------|--------------------|----------|
| **pp3g opencode fork** (`1.18.13-pp3g-fork`) | Silent-hang family: provider stream errors that deadlock stock opencode (consumption deadlock in `llm.ts`; fixed by `safeIterable()` fire-and-forget return, commit `98dfe4a`). The reliability epic (#156) drove the durable fix; the separate fork DB isolates fork-verification noise from real history (#313). | Workflow Topology record §2; #313 result (fork DB, baked-in channel split). |
| **crosslink fork CLI** | Issue/session state is the durable store for the workflow topology (§1.3): positions, checkpoints, auditor flags, verdicts all live as comments. Without it, agents have no shared coordination state and no audit trail. | Workflow Topology record §5.1; used by every agent workflow in the repo. |
| **`claude` wrapper (strict model enforcement)** | Implicit/default Anthropic models (`opus`/`sonnet`/`haiku`) or unverified IDs reach the provider; free-tier launches hang/fail mid-task. The wrapper makes an explicit verified model ID a hard launch requirement and memory-caps tmux sessions. | `~/.local/bin/claude` (model check, systemd-run memory scope); model-discipline.md. |
| **user-level model-whitelist plugin** | Provider hygiene: paid Zen models exposed without credits; unwanted providers (`openai`, `deepseek`, `cloudflare`, …) selectable; free-model set unbounded. The plugin disables/hides providers and whitelists exactly seven free Zen models (#103). | `~/.config/opencode/plugins/plugin.ts`; model-discipline.md. |
| **orchestrator-guard plugin** | The #33677 gap: native `edit: deny` does not block write/edit/`apply_patch`/MCP filesystem write tools. Without the plugin, a read-only role (orchestrator/reviewer/auditor) can still write project files, defeating the role separation. | `.opencode/plugins/orchestrator-guard.ts` (BLOCKED_TOOLS, per-session agent map); permissions.md note 1. |
| **crosslink-guard plugin** | Git discipline failures: agents pushing, rebasing, resetting, force-pushing; commits not tied to an issue; issue closes without a result comment; tool use with no tracking at all. Also the operator kill/pause control channel. Replaces the Python `work-check.py` hook natively. | `.opencode/plugins/crosslink-guard.ts` (behaviour list in header comment, steps 1-10); hook-config.json lists; #204 regression note. |
| **rtk-guard plugin** | Token cost: unfiltered `cat`/`git status` output is expensive in long agent sessions. Claude Code's PreToolUse rewriting cannot run in opencode, so the plugin restores transparent rewriting — fail-open so it can never block work. | `.opencode/plugins/rtk-guard.ts` (header, gates); rtk 0.40.0. |
| **hook-config.json** | Config drift between what plugins enforce and what is documented. A single per-repo config file drives the bash allowlist, git blocked/gated lists, per-role `by_type` overrides, comment discipline, and tracking mode. | `.crosslink/hook-config.json`. |
| **git write discipline (blocked/gated lists)** | A mutation-unsafe agent corrupting history (push/rebase/reset/clean/checkout/restore/stash/tag/am/apply/branch-delete). Commit gating ties every commit to an auditable issue; pushes remain the operator's job. | hook-config.json `blocked_git_commands`/`gated_git_commands`; agent `.md` git rules; permissions.md summary table. |
| **model-discipline rules** | Stale/guessed model IDs (the #1 failure cause per permissions.md), free-tier agents hanging under rate limits, and misdiagnosing stalls as rate limits when they are silent hangs. | `.crosslink/knowledge/model-discipline.md`. |
| **workflow-topology design** | The dominant unguarded failure class: decision-gating claims crossing information-asymmetry boundaries (the #156 binary-vs-source misattribution). Positions + staleness trigger + pre-positioned auditor + readiness audit make claims checkable. | Workflow Topology record §2-§5. |
| **`sleep *` orchestrator grant** | Orchestrator unattended monitoring: polling loops (`sleep N` then re-check the auditor's issue) were blocked by the bash allowlist; granted by issue #298 (referencing #156). | #298; orchestrator.md allowlist. |

---

## 5. Identified Problem Areas

> This section is a **write-up of problems**, not solutions. It records what
> is observed to be fragile or inconsistent in the current system.

### 5.1 THREE-SURFACE kickoff enforcement

A kickoff agent is nominally gated by **three separate surfaces** that must be
kept in agreement:

1. **hook-config `allowed_bash_prefixes`** — the bash allowlist enforced by
   crosslink-guard (though under the agent `tracking_mode: "relaxed"` the
   allowlist is not the blocking layer for agents; blocked/gated git still
   are).
2. **`kickoff.allowed_tools`** — merged into the fork's `--allowedTools`
   string (currently unset in ASES; when set it would extend
   `build_allowed_tools`).
3. **the agent `.md` permission block** — enforced by opencode's native
   engine.

Three places to update, with different matching semantics and different
enforcement actors. **Observed deployment wrinkle:** the `--allowedTools`
string is currently **constructed but not enforced** end-to-end — the `claude`
wrapper drops the flag and `opencode run` has no such flag (verified against
the wrapper source and `opencode run --help`, not against a live kickoff).
So the practical surface count today is two (native engine + crosslink-guard)
with a third dormant one waiting in the fork — but the divergence risk is
already present in the *configuration space*: a project owner updating only
one surface (e.g. adding `sqlite3` to hook-config) does not affect the fork's
base list, and vice versa.

### 5.2 PER-TYPE ASYMMETRY in the kickoff surface

`build_allowed_tools(conventions, verify)` produces an **identical tool
surface for builder, reviewer, and auditor** — the function has no
`agent_type` parameter (`prompt.rs:429-473`). `--agent-type` only changes the
git blocked/gated lists inside crosslink-guard via `by_type`
(hook-config.json), not the bash tool surface. Consequently:

- **Auditor-only tool grants are NOT expressible in kickoff mode** without a
  fork change. If the auditor needs a tool the builder must not have (e.g.
  read-only `sqlite3` for DB audits), the shared `--allowedTools` list cannot
  express that distinction; a per-type allowedTools implementation does not
  exist.
- The role asymmetry that exists in the `.md` blocks (builder unrestricted
  bash vs reviewer/auditor allowlisted) is not mirrored in the fork's
  constructed surface.

### 5.3 TWO-SURFACE INCONSISTENCY: `.md` claims vs kickoff grants

The reviewer/auditor `.md` files claim a **broad** bash surface:
`"opencode *": "allow"` and `"git *": "allow"` (all of git), plus
`ls`/`cat`/`rtk`. The fork's `--allowedTools` base list grants **less**:

- no `opencode *` (only `Bash(crosslink *)`, `Bash(git *)`, and the listed
  read tools);
- no `sqlite3`, no `stat`, no `ps`.

**Observed concretely in #313:** the pre-positioned Phase-1 auditor
(agent `pp3g-dZ3X`, opencode-go/mimo-v2.5) was tasked with independently
verifying the builder's read-only SQLite inventory claims. The auditor
reported, in checkpoints and handoff:

> "sqlite3 blocked by bash permission pattern (no allow rule for sqlite3)"
> — #313 [PROGRESS] comment
>
> "LIMITATION: sqlite3 blocked by bash permission pattern, could not
> independently verify SQL headline numbers. Systemic risk: auditor role
> needs sqlite3 read access for DB-audit tasks." — #313 handoff comment

The auditor fell back to file-size/stat-level cross-checks (which passed:
NO DIVERGENCE OBSERVED) but could not run the SQL spot-checks it planned. The
blocking surface as reported ("no allow rule for sqlite3") matches the
agent `.md` allowlist; the kickoff `--allowedTools` surface would also have
excluded it had it been enforced. This is the concrete, observed cost of the
surface disagreement.

### 5.4 The #33677 gap requires a custom plugin

The opencode native permission model does not enforce `edit: deny` for its
own write-path tools — the gap is only closed by the custom
orchestrator-guard plugin. Consequences:

- The plugin is **in-repo code** that can drift from the agent definitions it
  enforces (it hard-codes `ALLOWED_AGENTS = {"builder"}` and a fixed
  `BLOCKED_TOOLS` set).
- A new write-capable tool (native or MCP) is not covered until it is added to
  `BLOCKED_TOOLS`; a new agent role is not covered until `ALLOWED_AGENTS` is
  updated. Both are manual, easy to miss.
- The plugin's per-session agent map is a correctness-critical mechanism (the
  #204-style clobbering regression) that is only as correct as the `chat.params`
  events it receives; crosslink-guard logs explicit FAIL-CLOSED warnings when
  resolution falls back to env/config, and those warnings are observational.

### 5.5 CROSS-REPO DRIFT RISK

The same tooling story spans multiple repositories — ASES, tripn-astro, the
Tools repo, and the crosslink fork itself. Points of drift:

- **Per-repo hook-config**: each repo's `.crosslink/hook-config.json` can
  diverge (allowlist entries, blocked/gated lists, by_type maps, tracking
  mode). The plugin code is shared (in-repo copies); the config is not.
- **Convention detection** (`helpers.rs::detect_conventions`) is
  manifest-based and repo-shaped: a repo whose manifests sit two or more
  levels deep gets no Rust/Python/… tools in `--allowedTools` (the
  `has_manifest` scan is one level deep, with an explicit skip list) — the
  mitigation (`kickoff.allowed_tools`) is per-repo and optional.
- **Fork vs deployment**: the fork builds `--allowedTools` and the deployed
  wrapper drops it — a fork/deployment contract mismatch (see §5.1).
- **Model pins** drift (permissions.md documents stale pins as "#1 failure
  cause"); the model-discipline rule exists precisely because of it.

---

## 6. What-Not-Tested / Open Questions

Following the project's reasoning-certainty principle, the limits of this
write-up are stated explicitly:

1. **Per-type `allowedTools` is not implemented.** There is no
   `agent_type`-dependent tool surface in the fork; adding one requires a
   fork change. Untested: what the correct per-type surface would even be.
2. **Independent testability of each guard is unaudited.** The three plugins
   log to `/tmp/*.log` and are exercised only in live sessions; there is no
   in-repo unit/integration test suite for them. Whether each guard is
   independently testable (and what the cheap discriminating test per guard
   is) is an open question.
3. **rtk-guard × crosslink-guard ordering.** crosslink-guard strips `rtk `
   prefixes in `isSingleCommandAllowed`/`normalizeGitCommand` so an
   already-prefixed command matches the allowlists; rtk-guard mutates
   `output.args.command` to add the prefix. The actual hook-firing order of
   the two `tool.execute.before` handlers in the same process was not
   empirically measured — only the defensive stripping in crosslink-guard was
   verified.
4. **`--allowedTools` enforcement semantics.** It was verified that the
   deployed wrapper drops the flag and `opencode run --help` lists no such
   flag; it was **not** verified against a live kickoff launch, nor whether a
   future wrapper forwarding the flag would enforce Claude-Code-style
   `Bash(pat *)` patterns against opencode's permission engine (the two
   matchers are different).
5. **Relaxed-mode allowlist nuance.** Under `agent_overrides.tracking_mode:
   "relaxed"`, crosslink-guard's bash allowlist is not the blocking layer for
   agents (any non-blocked, non-gated bash passes); the observed #313
   sqlite3 block therefore most plausibly came from the native `.md`
   allowlist, but the precise layer responsible in that session was not
   instrumented.
6. **Free-tier behavior is still being characterized.** #313's first auditor
   attempt (`opencode/north-mini-code-free`) failed with a provider **401**
   (auth), distinct from 429/rate-limit and silent-hang classes; the free-tier
   failure space is documented but not closed.
7. **Kill/pause and FAIL-CLOSED paths.** `checkControlFlags` fails *open*
   when `crosslink` is unavailable; the plugin's FAIL-CLOSED warnings when
   agent-type resolution falls back are observational, and the interactive
   (non-kickoff) orchestrator session path was not re-verified in this
   write-up.

---

## 7. Verified Sources

All claims in this document were verified against these files on 2026-08-09:

1. `.opencode/opencode.json` — agent map, plugin list, MCP config.
2. `.opencode/agents/{orchestrator,builder,reviewer,auditor}.md` — permission
   frontmatter.
3. `.opencode/plugins/{orchestrator-guard,crosslink-guard,rtk-guard}.ts`.
4. `.crosslink/hook-config.json`.
5. `/home/claude-code/projects/crosslink/crosslink/src/commands/kickoff/prompt.rs`
   — `build_allowed_tools()`.
6. `/home/claude-code/projects/crosslink/crosslink/src/commands/kickoff/helpers.rs`
   — `read_kickoff_allowed_tools()`, `detect_conventions()`.
7. `/home/claude-code/projects/crosslink/crosslink/src/commands/kickoff/launch.rs`
   — `build_agent_command()`.
8. `~/.config/opencode/plugins/plugin.ts` — user-level provider hiding +
   free-model whitelist.
9. `docs/research/Workflow Topology Design and Reasoning Record.md` —
   canonical role-topology design record.
10. `.crosslink/knowledge/model-discipline.md`.
11. `.opencode/permissions.md` — four-role permission snapshot (documented as
    possibly stale; agent definitions and live CLI win).
12. Live deployment facts: `opencode --version` (`1.18.13-pp3g-fork`),
    `rtk --version` (`0.40.0`), `~/.local/bin/claude` wrapper source,
    `opencode run --help`, `~/.local/share/opencode/*.db` presence, and the
    #313 auditor comments in `.crosslink/issues.db`.
