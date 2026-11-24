---
name: crosslink-subagent-orchestration
description: Use when the user says "/kickoff", "/swarm", "use subagents", "spawn an agent", "launch agents", "kick off an agent", "swarm this", "parallelize this", "delegate to agents", "background agent", or asks for multi-agent orchestration via Crosslink. Covers single-agent kickoff, multi-agent swarm, and autonomous sentinel. Does NOT trigger on opencode's built-in subagent feature (Task tool, @mention agents) — the Task tool is an IN-SESSION, SYNCHRONOUS, BLOCKING subagent call for read/research/quick-answer ONLY, NEVER implementation: it locks the calling session until it returns, and gives the subagent no worktree, no crosslink issue/identity/tracking, and no commit trail. Any implementation request routes to `crosslink kickoff run` / `crosslink swarm launch` / `crosslink sentinel`, never the Task tool.
---

# Crosslink Subagent Orchestration

You are about to orchestrate background agents via crosslink. There are three tiers depending on scope — plus the opencode **Task tool**, which is **not** a delegation tier (see the Decision Matrix below).

## Decision: Which tier?

| User says | Tier | Tool |
|-----------|------|------|
| "kick off an agent for X" | Single agent | `crosslink kickoff run` |
| "swarm this" / "parallelize this" / multi-feature work | Multi-agent swarm | `crosslink swarm launch` |
| "set up autonomous maintenance" / "auto-fix issues" | Autonomous daemon | `crosslink sentinel` |

## Decision Matrix — Task tool vs kickoff vs swarm vs sentinel

| Need | Tool | Execution model | Locking |
|------|------|-----------------|---------|
| In-session read / research / quick-answer — small file reads, summarization, bounded analysis | **opencode Task tool** (or `@explore` / `@general`) | In-session subagent call | **Synchronous, BLOCKING** — the calling session locks until the subagent returns |
| Single implementation ticket | **`crosslink kickoff run`** | Background tmux/container + own worktree + feature branch + crosslink issue | **Non-blocking** — session stays live |
| Multi-phase parallel feature | **`crosslink swarm launch`** | Multiple worktrees, hub-branch coordination, phase gates | Non-blocking — session stays live |
| Autonomous maintenance daemon | **`crosslink sentinel`** | Persistent daemon, poll-triage-dispatch loop | Non-blocking — session stays live |

**The Task tool is NOT an implementation tier.** It is an in-session,
synchronous subagent call: the calling session is **blocked until it
returns** — it cannot converse with the operator, cannot dispatch other
agents, and the subagent gets **no worktree isolation, no crosslink
issue/identity/tracking, no durable commit trail, and no checkpoint
contract**. It is for read/research/quick-answer ONLY:

- **NEVER use the Task tool for implementation.**
- **NEVER use the Task tool to record review verdicts for the record.**
- **NEVER use the Task tool for anything requiring a durable
  worktree/commit/tracking trail.**

**Failure evidence (2026-08-06):** agents repeatedly used the Task tool for
actual implementation, which LOCKED the orchestrator session while the
subagent ran — a blocking failure mode kickoff does not have. Any
implementation request routes to `crosslink kickoff run` (or swarm/sentinel
for multi-phase/autonomous work), never to the Task tool.

## Not this skill

- OpenCode's built-in subagents (Task tool, `@explore`, `@general`) — in-session read/research/quick-answer ONLY, NEVER implementation (see the Decision Matrix above: Task tool calls are synchronous and block the calling session)
- Asking the current agent to do work directly — no kickoff needed

## Tier 1: Single Agent (`crosslink kickoff`)

Launch one background agent for a single feature:

```bash
crosslink kickoff run "<feature description>" [--verify local|ci|thorough] [--timeout 1h] [--container docker|podman]
```

Key flags:
- `--verify local` (default): self-review checklist
- `--verify ci`: push branch, open PR, wait for CI
- `--verify thorough`: CI + adversarial self-review
- `--timeout`: max runtime (default: 1h)
- `--container`: use docker/podman instead of local tmux
- `--doc <path>`: base work on a design document
- `--dry-run`: print the agent prompt without launching
- `--issue <id>`: use existing crosslink issue

After launch:
```bash
crosslink kickoff status <agent-slug>   # check status
tmux attach -t <agent-slug>             # attach to agent session
crosslink kickoff logs <agent-slug>     # view logs
crosslink kickoff stop <agent-slug>     # stop agent
```

The agent creates its own git worktree and branch. Monitor with `crosslink kickoff list --status running`.

## Tier 2: Multi-Agent Swarm (`crosslink swarm`)

Decompose a plan into phases, launch agents per phase, with gates between:

```bash
crosslink swarm init <design-doc.md>     # decompose plan into phases
crosslink swarm status                   # view phase pipeline
crosslink swarm launch <phase>           # launch agents for a phase
crosslink swarm gate <phase>             # review phase outputs before next phase
crosslink swarm checkpoint               # checkpoint current state
crosslink swarm resume                   # resume from checkpoint
```

Budget-aware planning is built in (`crosslink swarm estimate`). Each phase can have multiple parallel agents. Gates ensure the operator reviews outputs before the next phase launches.

## Tier 3: Autonomous Sentinel (`crosslink sentinel`)

Persistent daemon that monitors GitHub labels and auto-dispatches agents:

```bash
crosslink sentinel run                  # one-shot check
crosslink sentinel watch                # persistent daemon
crosslink sentinel status               # check what it's doing
```

Monitors labels like `agent-todo:replicate` and `agent-todo:fix`. Auto-escalates from faster models to Opus on failure. Configurable via `.crosslink/hook-config.json`.

## Execution Model

All agents run via `crosslink kickoff run` under the hood. Each gets:
- An isolated git worktree (`.worktrees/<slug>/`)
- A generated KICKOFF.md prompt
- A tmux session (or container) running `claude` (wrapped to `opencode run`)

Agents sync state via the `crosslink/hub` branch. Run `crosslink sync` before and after agent work to coordinate.

## Verification Pipeline

After agents complete:
```bash
# In the ASES project only:
scripts/crosslink-verify.sh --worktree <path>
scripts/crosslink-cleanup.sh --worktree <path>
```

## Reference

For comprehensive documentation: `crosslink knowledge show subagent-orchestration`
