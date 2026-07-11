# Subagent Orchestration

**Crosslink knowledge page — workflow/orchestration**

---

## Overview

Crosslink provides three tiers of subagent orchestration, each suited to a different scale of work:

| Tier | Name | When to use | Max agents | Execution model |
|---|---|---|---|---|
| **1** | Kickoff | Single, well-defined task | 1 | Isolated worktree, tmux or container |
| **2** | Swarm | Multi-phase feature with parallel agents | Unlimited (phased) | Multiple worktrees, hub branch coordination, budget-aware |
| **3** | Sentinel | Autonomous maintenance (poll-and-dispatch) | Configurable (default 3) | Persistent daemon, poll-triage-dispatch loop |

Choose kickoff when the task fits in one agent session (typically ≤1 hour). Choose swarm when the work decomposes into phases with parallel components. Choose sentinel when you want long-running autonomous responses to external signals (GitHub labels, CI failures, stale issues).

---

## Tier 1: Kickoff (Single Agent)

### When to use

- A single, well-scoped feature or fix.
- You have a design document or a clear description.
- The estimated effort fits a single agent session (≤1 hour by default).
- You want isolation: the agent works in its own branch and worktree.

### Core CLI

```bash
# Launch an agent from a description
crosslink kickoff run "Add user authentication module"
crosslink kickoff run "Add user auth" --issue 42

# Launch from a design document
crosslink kickoff run "..." --doc DESIGN-AUTH.md

# Specify model, timeout, verification level
crosslink kickoff run "..." --model opus --timeout 2h --verify ci

# Dry-run: print the prompt without launching
crosslink kickoff run "..." --dry-run
```

### Key flags

| Flag | Purpose | Default |
|---|---|---|
| `--model` | LLM model for the agent | `opus` |
| `--timeout` | Max runtime (e.g. `1h`, `30m`) | `1h` |
| `--verify` | Verification tier: `local`, `ci`, `thorough` | `local` |
| `--container` | Container runtime: `none`, `docker`, `podman` | `none` |
| `--issue` | Existing crosslink issue to work on | auto-creates |
| `--branch` | Branch name | auto-creates feature branch |
| `--doc` | Path to a design document | none |
| `--dry-run` | Print prompt without launching | false |
| `--skip-permissions` | Bypass Claude permission prompts | false |
| `--permission-mode` | Finer control than `--skip-permissions` | none |

### Lifecycle

```bash
# Launch
crosslink kickoff run "..." --model opus

# Check status
crosslink kickoff status                      # pipeline overview
crosslink kickoff logs <agent-id>              # tail event log
crosslink kickoff list                         # all agents (worktree/tmux/docker)

# Stop
crosslink kickoff stop <agent-id>

# View spec validation report
crosslink kickoff report <agent-id>

# Clean up completed/stale agents
crosslink kickoff cleanup
```

### Execution model

Kickoff creates an **isolated worktree** under `.worktrees/<slug>/`. The agent:

1. Gets its own branch (auto-created as `feature/<slug>`).
2. Gets a crosslink issue and agent identity (ED25519 signing key).
3. Runs in its own tmux session (or container, if `--container docker|podman`).
4. Reports progress via `.kickoff-status` sentinel files and crosslink comments.
5. When done, the worktree is ready for review or merge.

---

## Tier 2: Swarm (Multi-Agent Coordination)

### When to use

- A feature is too large for a single agent.
- Work naturally decomposes into phases (e.g., "database migrations" then "API endpoints").
- Multiple components within a phase can be developed in parallel.
- You need budget-aware planning and quality gates between phases.

### Core CLI

```bash
# Initialize from a design document
crosslink swarm init --doc DESIGN-AUTH-SYSTEM.md

# Review the plan
crosslink swarm plan-show

# Set budget parameters
crosslink swarm config --budget-window 3h --model opus

# Estimate cost for a phase
crosslink swarm estimate 1

# Launch all agents for phase 1
crosslink swarm launch 1

# Monitor progress
crosslink swarm status

# Run quality gate (full test suite)
crosslink swarm gate 1

# Checkpoint and advance
crosslink swarm checkpoint 1 --notes "Auth models and DB migrations done"

# Launch next phase (with budget check)
crosslink swarm launch 2 --budget-aware

# If interrupted, resume later
crosslink swarm resume

# Harvest cost data for better future estimates
crosslink swarm harvest

# Merge completed worktrees
crosslink swarm merge
```

### Design-driven decomposition

Swarm reads the design document and auto-decomposes it into phases. You can also specify phases explicitly with H2 headers:

```markdown
## Phase: Database Migrations
- Add user table schema
- Add session table schema

## Phase: API Endpoints
- Add registration endpoint
- Add login endpoint
```

When these headers are present, `swarm init` uses them directly instead of auto-decomposing. Each bullet becomes an agent work unit within that phase.

### Budget-aware planning

```bash
# Plan across a 3-hour budget window
crosslink swarm plan --budget-window 3h

# Configure budget parameters
crosslink swarm config --budget-window 3h --model opus

# Estimate wall-clock cost for phase 1
crosslink swarm estimate 1
```

The swarm scheduler distributes phases across the available budget window. Cost estimates improve as completed phases feed data into the cost history (`crosslink swarm harvest`).

### Worktree isolation and hub branch

Every agent in a swarm gets its own **isolated worktree** (same as kickoff). Coordination happens through the **`crosslink/hub` branch**:

- The hub branch stores phase plans, agent assignments, checkpoints, and consolidated reports as JSON blobs under `swarm/`.
- Agents share state through the hub branch without directly accessing each other's worktrees.
- The hub branch is a git branch — it syncs naturally with remotes, enabling CI integration and human review.

```
Feature branch A (worktree)          Feature branch B (worktree)
        │                                     │
        │  push changes                        │  push changes
        ▼                                     ▼
   crosslink/hub branch (JSON state + coordination data)
        │
        ▼
   crosslink/hub cache (local SQLite snapshot)
```

### Phase gates

Before advancing between phases, the gate runs the **full project test suite**:

```bash
crosslink swarm gate 1
```

All tests must pass before the phase is considered complete. Use `--force` to checkpoint without a passing gate (for partial progress):

```bash
crosslink swarm checkpoint 1 --force --notes "3 of 4 agents done, one blocked"
```

### Editing the plan

You can restructure the plan between phases:

```bash
# Move an agent to a different phase
crosslink swarm move <agent> --to-phase 2

# Merge two phases
crosslink swarm merge 2 3

# Split a phase after a specific agent
crosslink swarm split 1 --after <agent>

# Remove an agent
crosslink swarm remove <agent>

# Reorder an agent within a phase
crosslink swarm reorder <agent> --position 1

# Rename a phase
crosslink swarm rename 1 --name "Database migrations"
```

### Managing multiple swarms

```bash
# Create a new swarm (assigned a UUID)
crosslink swarm create

# List all swarms
crosslink swarm list

# Switch active context
crosslink swarm switch <uuid>

# Archive a completed swarm
crosslink swarm archive

# Reset active swarm
crosslink swarm reset
```

---

## Tier 3: Sentinel (Autonomous Maintenance)

### When to use

- You want long-running autonomous responses to external signals.
- Issues labelled `agent-todo: replicate` or `agent-todo: fix` should be automatically handled.
- You want periodic maintenance sweeps (CI failures, stale issues, dependency audits).
- Human approval is gated by the `agent-todo:*` label convention — sentinel only acts on labels humans have applied.

### Architecture

The sentinel is a **persistent daemon** (or one-shot command) that follows a poll-triage-dispatch-collect loop:

```
External Source (GitHub, CI, internal)
        │
        ▼
   Poll → Dedup (SeenSet + DB) → Triage → Dispatch → Collect → Post Results
        │                              │
        ▼                              ▼
   Skip if seen              Kickoff agent in worktree
```

### Core CLI

```bash
# One-shot sweep
crosslink sentinel run
crosslink sentinel run --dry-run           # preview without acting
crosslink sentinel run --label "agent-todo: fix"   # filter by label

# Persistent daemon
crosslink sentinel watch                    # default 10min interval
crosslink sentinel watch --interval 5       # custom interval (minutes)

# Status and history
crosslink sentinel status                   # daemon state, in-flight agents
crosslink sentinel history                  # past runs and outcomes
crosslink sentinel history --limit 20 --json

# Stop the daemon
crosslink sentinel stop
```

### Signal types and dispatch rules

| Signal | Label | Agent scope | Verification | Action |
|---|---|---|---|---|
| Bug replication | `agent-todo: replicate` | `tests/` only | Local | Write failing test, do NOT fix |
| Bug fix | `agent-todo: fix` | `src/` + `tests/` | CI | Fix bug, push branch, open draft PR |

### Deduplication

Sentinel uses a four-layer dedup system to prevent duplicate work:

1. **Source-level**: Only polls issues that currently have the label at poll time.
2. **SeenSet**: In-memory cache of past dispatches from the database.
3. **Database constraint**: Index on `(gh_issue_number, label)` prevents duplicate inserts.
4. **GH comment dedup**: Checks for an existing sentinel comment marker before posting.

### Model escalation

First attempt uses **Sonnet** (fast, cheap). On failure, retry with **Opus** (more capable, more expensive) after a cooldown (default 30 minutes). Maximum 2 attempts per signal.

```
Attempt 1: Sonnet, 30min timeout
  ├── Success → done (outcome: "success")
  └── Failure → cooldown 30min
                └── Attempt 2: Opus, 45min timeout
                    ├── Success → done (outcome: "success")
                    └── Failure → exhausted (outcome: "exhausted")
```

### Configuration

Sentinel is configured via the `"sentinel"` key in `.crosslink/hook-config.json`:

```jsonc
{
    "sentinel": {
        "enabled": true,
        "interval_minutes": 10,
        "max_concurrent_agents": 3,
        "sources": {
            "github_labels": {
                "enabled": true,
                "labels": ["agent-todo: replicate", "agent-todo: fix"]
            }
        },
        "default_agent": {
            "model": "claude-sonnet-4-6",
            "timeout_minutes": 30,
            "verify": "local"
        },
        "escalation": {
            "enabled": true,
            "model": "claude-opus-4-6",
            "cooldown_minutes": 30,
            "max_attempts": 2,
            "timeout_multiplier": 1.5
        }
    }
}
```

---

## Verification Pipeline

All three tiers use a shared verification model with three tiers:

| Level | What runs | When to use |
|---|---|---|
| `local` | `cargo check` (or equivalent compile check) | Rapid iteration, reproduction agents |
| `ci` | Full test suite + lint | Before merging, fix agents |
| `thorough` | Full test suite + lint + integration tests + benchmarks | Release gate |

Set with `--verify` on `crosslink kickoff run` or via configuration:

```bash
# Quick local verification
crosslink kickoff run "..." --verify local

# CI-grade verification (default for fix agents)
crosslink kickoff run "..." --verify ci

# Full verification
crosslink kickoff run "..." --verify thorough
```

---

## Lock Mechanics

Crosslink uses optimistic locking so multiple agents don't collide:

```bash
# View active locks
crosslink locks list

# Check if an issue is locked
crosslink locks check <id>

# Manually claim or release
crosslink locks claim <id>
crosslink locks release <id>

# Steal a stale lock
crosslink locks steal <id>
```

Auto-claiming: `crosslink quick` and `crosslink session work` auto-claim locks on the issue. `crosslink issue close` releases them. Swarm agents claim locks on their assigned issues through the hub branch's coordination state.

**Conflict resolution:** If two agents try to modify the same file in different worktrees, the merge step (`crosslink swarm merge`) surfaces conflicts for manual resolution — same as a normal git merge conflict. The hub branch's JSON state files (phase plans, agent assignments) are updated atomically via git commits, so coordination metadata never conflicts.

---

## Agent Identity and Trust

Every agent — whether launched via kickoff, swarm, or sentinel — gets:

1. A dedicated ED25519 signing key.
2. A crosslink agent identity initialized in its worktree.
3. Trust-published key for signing crosslink comments and commits.

```bash
# View agent identity
crosslink agent status

# Manage trust
crosslink trust list
crosslink trust approve <fingerprint>
crosslink trust revoke <fingerprint>
crosslink trust pending
```

---

## Command reference

### Kickoff

| Command | Purpose |
|---|---|
| `crosslink kickoff run <desc>` | Launch a single agent |
| `crosslink kickoff status` | Check running agents |
| `crosslink kickoff logs <id>` | Tail agent event log |
| `crosslink kickoff stop <id>` | Stop a running agent |
| `crosslink kickoff list` | List all agents |
| `crosslink kickoff cleanup` | Remove completed/stale agents |
| `crosslink kickoff plan <doc>` | Gap analysis against design doc |
| `crosslink kickoff graph` | Branch topology |

### Swarm

| Command | Purpose |
|---|---|
| `crosslink swarm init --doc <path>` | Initialize from design document |
| `crosslink swarm status` | Show swarm state and progress |
| `crosslink swarm plan` | Budget-aware multi-phase planning |
| `crosslink swarm plan-show` | Display current plan |
| `crosslink swarm launch <phase>` | Launch all agents for a phase |
| `crosslink swarm gate <phase>` | Run test suite as quality gate |
| `crosslink swarm checkpoint <phase>` | Record phase completion |
| `crosslink swarm resume` | Reconstruct after interruption |
| `crosslink swarm merge` | Merge worktrees into one branch |
| `crosslink swarm harvest` | Update cost history |
| `crosslink swarm list` | List active and archived swarms |
| `crosslink swarm archive` | Archive completed swarm |

### Sentinel

| Command | Purpose |
|---|---|
| `crosslink sentinel run` | One-shot poll-and-dispatch |
| `crosslink sentinel run --dry-run` | Preview without acting |
| `crosslink sentinel watch` | Start persistent daemon |
| `crosslink sentinel status` | Show daemon state |
| `crosslink sentinel history` | Past runs and outcomes |
| `crosslink sentinel stop` | Stop the daemon |

---

## See also

- [Adversarial Review Workflow](crosslink-adversarial-review.md) — review pipeline, mandates, findings
- Knowledge page: `crosslink knowledge show crosslink-adversarial-review`
- Crosslink CLI: `crosslink kickoff run --help`, `crosslink swarm --help`, `crosslink sentinel run --help`
