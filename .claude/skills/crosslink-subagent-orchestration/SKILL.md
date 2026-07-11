---
name: crosslink-subagent-orchestration
description: Use when the user says "/kickoff", "/swarm", "use subagents", "spawn an agent", "launch agents", "kick off an agent", "swarm this", "parallelize this", "delegate to agents", "background agent", or asks for multi-agent orchestration via Crosslink. Covers single-agent kickoff, multi-agent swarm, and autonomous sentinel. Does NOT trigger on opencode's built-in subagent feature (Task tool, @mention agents).
---

# Crosslink Subagent Orchestration

You are about to orchestrate background agents via crosslink. There are three tiers depending on scope.

## Decision: Which tier?

| User says | Tier | Tool |
|-----------|------|------|
| "kick off an agent for X" | Single agent | `crosslink kickoff run` |
| "swarm this" / "parallelize this" / multi-feature work | Multi-agent swarm | `crosslink swarm launch` |
| "set up autonomous maintenance" / "auto-fix issues" | Autonomous daemon | `crosslink sentinel` |

## Not this skill

- OpenCode's built-in subagents (Task tool, `@explore`, `@general`) — those are for read-only research, not feature implementation
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
