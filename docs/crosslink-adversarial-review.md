# Adversarial Review Workflow

**Crosslink knowledge page — workflow/review**

---

## Overview

Adversarial review is a structured, multi-agent code auditing workflow built into crosslink's swarm subsystem. It launches parallel LLM-based review agents, each assigned a distinct partition of the codebase and a specific mandate focus. Findings are consolidated, de-duplicated, optionally filed as crosslink issues, and can be automatically dispatched to fix agents.

Use adversarial review when:

- You need a systematic audit before a release or merge.
- You want multiple specialised perspectives on the same codebase (security, robustness, correctness).
- You need to surface issues that a single pass would miss — heterogeneous agents find different classes of bugs.
- You want an auditable, pipeline-driven review-to-fix cycle with human checkpoints.

---

## The Four Mandates

Each review agent is assigned one of four mandate prompts. The mandate shapes the agent's attention and what it considers a "finding." All four share the rule: *find real problems, not style nits.*

### Adversarial (`--mandate adversarial`)

> *"You are the ha-satan, the loyal accuser. Find real problems that would cause failures in production. Ignore style nits, focus on correctness, safety, and robustness."*

The default mandate. Broad-spectrum review looking for anything that would break in production — crashes, logic errors, resource leaks, concurrency bugs, unsafe operations. Best **first pass** because it casts the widest net.

**What it catches:** crash paths, logic errors, resource leaks, concurrency bugs, unsafe operations, production-failing edge cases.

### Security (`--mandate security`)

> *"Review for trust boundary violations, injection vectors, data integrity issues, and unsafe operations."*

Narrow focus on attack surface. Best used after a codebase has been stabilised to find the vulnerabilities that survive normal development.

**What it catches:** SQL/command injection, privilege escalation paths, unvalidated input at trust boundaries, data integrity violations, unsafe `unsafe` blocks, cryptographic misuse.

### Robustness (`--mandate robustness`)

> *"Find crash paths, resource leaks, error handling gaps, and unhandled edge cases."*

Focuses on what happens when things go wrong. Best used when the codebase handles complex failure states, retries, or degraded operation.

**What it catches:** unhandled `Result::Err` paths, missing `?` propagation, resource handle leaks (file descriptors, connections), panic/unwrap in production paths, incomplete match arms, timeout gaps.

### Correctness (`--mandate correctness`)

> *"Find logic errors, race conditions, invariant violations, and incorrect algorithm implementations."*

Focuses on whether the code does what it is supposed to do. Best used when business logic or algorithmic complexity is high.

**What it catches:** off-by-one errors, race conditions in shared state, violated invariants, incorrect sort/compare implementations, wrong branching logic, deadlock cycles.

---

## The Pipeline

The adversarial review workflow is a staged pipeline:

```
Partition → Review → AwaitReview → Consolidate → HumanCheckpoint → FileIssues → Fix → AwaitFix → Merge → PR → Done
```

| Stage | What happens |
|---|---|
| **Partition** | The codebase is split into seam-based partitions (logical modules), distributed round-robin across agents. |
| **Review** | Agents are launched in parallel, each with one partition and one mandate prompt. |
| **AwaitReview** | Pipeline pauses. Agents run asynchronously. Check progress with `crosslink swarm status`; resume with `crosslink swarm review-continue`. |
| **Consolidate** | Agent reports are merged, duplicates are deduplicated, and a consolidated report is written (JSON + Markdown). Trust-model filtering is applied (findings can be triaged as "by-design" or downgraded). |
| **HumanCheckpoint** | Pipeline pauses for manual review of findings. |
| **FileIssues** | Surviving findings are cross-referenced against existing GitHub issues (to avoid duplicates), then filed as crosslink issues labelled `review-finding`. |
| **Fix** | Fix agents are launched, one per filed finding, with scoped prompts and worktree isolation. |
| **AwaitFix** | Pipeline pauses for fix agents to complete. |
| **Merge** | Completed fixes are merged into the target branch. |

---

## Usage

### Launch a review

```bash
# Default: 4 agents, adversarial mandate
crosslink swarm review

# Security review with 6 agents, file issues automatically
crosslink swarm review --mandate security --agents 6 --file-issues

# Full pipeline: review + auto-file + auto-fix
crosslink swarm review --mandate robustness --agents 4 --fix
```

### Check status

```bash
crosslink swarm review-status
# Shows: current pipeline stage, agent progress, next steps
```

### Monitor running agents

```bash
crosslink swarm status
```

### Review findings as crosslink issues

After auto-filing, findings become crosslink issues with the `review-finding` label:

```bash
crosslink issue list --label review-finding
crosslink issue show <id>          # full details of a finding
crosslink issue tree               # hierarchy view
```

### Continue a paused pipeline

```bash
crosslink swarm review-continue
```

### Launch fix agents independently

```bash
# Launch fix agents for all review-finding issues
crosslink swarm fix --from-label review-finding

# Launch fix agents for specific issues
crosslink swarm fix --issues 326,327,328

# Limit concurrency
crosslink swarm fix --from-label review-finding --max-agents 3
```

### Full pipeline shortcut

```bash
# One command: partition → review → consolidate → file issues → fix → merge
crosslink swarm pipeline --mandate adversarial --auto-fix --auto-file-issues

# Control agent count
crosslink swarm pipeline --agents 6 --mandate security --auto-fix
```

This runs the complete pipeline with no human checkpoints (unless a stage fails).

---

## Trust Model Filtering

Before findings are filed, they pass through the trust model. This triages findings into:

- **Valid** — accepted as actionable findings.
- **By-design** — the behaviour is intentional (e.g., a performance trade-off).
- **Downgraded** — severity is reduced based on context.

Configure with:

```bash
crosslink swarm trust-init --model opus
```

This writes a `swarm.toml` config with ignore patterns and trust boundaries.

---

## Model Recommendations for Review Agents

Empirical results from five rounds of adversarial reviews across the ASES project show that heterogeneous multi-model auditing catches significantly more vulnerabilities than any single model. Each model has a distinct strength profile:

| Dimension | Best-suited model | Strength |
|---|---|---|
| VCS & Git hook lifecycles | **Gemini / Claude** | 98% — catches file-system edge cases, hook timing, path resolution bugs |
| POSIX concurrency & locking | **Deepseek** | 90% — catches deadlocks, lock-ordering violations, process-level races |
| Token economics & latency | **Zhipu GLM 5.1** | 98% — catches context-window bloat, unnecessary ceremony, lock-holding latency |
| Database & schema design | **ChatGPT** | 95% — catches over-engineering, schema anti-patterns, transactionality gaps |
| Code hygiene & syntax bugs | **Gemini / Claude** | 95% — catches shell injection, fragile parsing, import resolution failures |
| Transactionality & crash recovery | **ChatGPT** | 95% — catches missing rollback paths, orphan data scenarios |

**Routing guidance:**

- Route **Git, shell scripting, and local environment** reviews to **Gemini/Claude** or **Deepseek**.
- Route **performance-critical, token-capped, and telemetry** reviews to **GLM**.
- Route **macro-architectural, database layout, and schema** reviews to **ChatGPT**.
- For a **general first pass**, the default `adversarial` mandate with any capable model works well — the mandate prompt drives attention more than the model choice.

> **Key finding:** No single model caught even 50% of critical vulnerabilities in any review round. Use multiple agents with different models for production-grade coverage.

---

## Common Anti-Patterns

Based on past review cycles, these patterns recur across projects:

| Anti-pattern | What it looks like | Mandate that catches it |
|---|---|---|
| **Orphan data paths** | Files moved to a processing directory but never consumed if a process crashes mid-way. | adversarial, robustness |
| **Staging-area leakage** | Pre-commit processes that read from the working tree instead of the Git index, leaking unstaged changes. | adversarial, correctness |
| **Synchronous lock-holding across IO** | Holding a file lock during a slow network LLM call, freezing local dev. | robustness, adversarial |
| **Premature commit-time operations** | Trying to read the commit SHA during `pre-commit` when the commit object doesn't exist yet. | correctness |
| **Shell-injection in git commands** | Passing raw JSON strings to `git notes add -m` without escaping. | security |
| **Non-reentrant lock nesting** | Calling a function that internally acquires a lock from within an already-locked context. | robustness, correctness |
| **Database impersonator** | Implementing transactions and crash recovery with loose JSON/JSONL/lock files instead of SQLite. | correctness |
| **Wall-clock timeouts for lease expiry** | Using file-mtime age instead of PID-based lease/heartbeat for ownership. | robustness |
| **Historical archive timestamp confusion** | Using the insertion timestamp instead of the eviction timestamp for archive filenames. | correctness |
| **Unbounded context-window bloat** | Append-only accumulation of natural-language metadata that degrades inference speed. | adversarial, robustness |

---

## Pipeline lifecycle commands

| Command | Purpose |
|---|---|
| `crosslink swarm review` | Launch review agents (with mandate, agent count, options) |
| `crosslink swarm review-status` | Show current pipeline state |
| `crosslink swarm review-continue` | Resume a paused pipeline |
| `crosslink swarm pipeline` | Run full review→fix pipeline in one command |
| `crosslink swarm fix` | Launch fix agents for findings |
| `crosslink swarm status` | Monitor all agents in the swarm |
| `crosslink swarm gate` | Run test suite as a phase gate |
| `crosslink swarm merge` | Merge completed fix worktrees |
| `crosslink swarm trust-init` | Configure trust model for filtering findings |

---

## See also

- [Subagent Orchestration](crosslink-subagent-orchestration.md) — how agents are launched, isolated, and coordinated
- Knowledge page: `crosslink knowledge show crosslink-subagent-orchestration`
- Crosslink CLI: `crosslink swarm review --help`
