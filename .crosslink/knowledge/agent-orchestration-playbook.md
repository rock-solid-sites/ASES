---
title: "Agent Orchestration Playbook"
tags: ["orchestration", "kickoff", "swarm", "workflow"]
sources: []
contributors: ["ASES"]
created: 2026-08-01
updated: 2026-08-01
---

# Agent Orchestration Playbook

**Scope:** Model-agnostic operational rules for orchestrating multi-agent
sessions via Crosslink kickoff and swarm. Applies to every orchestrator
session regardless of which LLM is driving. This is the **canonical** copy;
project repos may carry a duplicate, but the ASES copy wins on conflict.

This playbook covers **both** tiers of delegation. Read it once — it tells you
which tier applies, the shared rules, and the tier-specific procedures.

---

## 1. Division of Labor — Non-Negotiable

| Role | Responsibility | Forbidden |
|------|---------------|-----------|
| **Operator (Human)** | Directs, decides, approves architecture, holds production secrets | Never handed code to read/write |
| **Orchestrator (Main Session)** | Plans, delegates via kickoff/swarm, reviews at gates, handles structural tasks | Never implements, reviews own work, or silently takes over failed agents |
| **Workers (Kickoff/Swarm Agents)** | Execute specific implementation tickets in isolated worktrees | Never plan, review, or merge to master |

**The core constraint:** The orchestrator never wears the implementer hat.
Implementation is delegated. Reviewing your own work is rubber-stamping by
default.

---

## 2. Choose Your Tier — Kickoff vs Swarm

Pick the tier **before** dispatching. The boundary is feature size and shape:

| Situation | Tier |
|-----------|------|
| One well-defined ticket, fits a single session (≤ ~1h) | **Kickoff** (`crosslink kickoff run`) |
| A multi-phase feature that decomposes into parallel or sequential work | **Swarm** (`crosslink swarm init` → `launch` → `gate` → `checkpoint`) |
| Long-running autonomous maintenance | **Sentinel** (separate; see `crosslink-subagent-orchestration.md`) |

**Rules for choosing:**
- Do not swarm what a single kickoff can do — swarm overhead (plan, phases,
  gates, budgets) is not free.
- Do not kickoff a genuinely multi-phase feature serially — you lose the
  parallel fan-out swarm exists for.
- **Prove serially, then fan out.** The first instance of a pattern must be
  completed end-to-end before parallelizing. Six agents fanning out on an
  unproven pattern each invent a different (often wrong) approach.

---

## 3. Model Selection — Mandatory Explicit Pin

**Every kickoff or swarm command MUST include `--model`.**

There is no safe default. The orchestrator must never assume a model is
available. Before dispatching any agent:

1. **Verify the model against the live catalog** — you CAN run `opencode
   models` yourself (it is an allowed command). Run `opencode models opencode`
   (Zen free) and `opencode models opencode-go` (paid Go) and confirm the
   exact model ID is listed. Do not rely on static files (e.g.
   `.opencode/permissions.md` is a snapshot that goes stale).
2. Pass `--model <provider/model-name>` explicitly on every `crosslink
   kickoff run` and `crosslink swarm launch`.
3. If the model is unreachable or not listed, HALT and report to the operator
   — do not fall back silently.

```
# CORRECT
crosslink kickoff run "feature description" --model opencode-go/deepseek-v4-flash

# WRONG — omitted --model, will use stale or wrong default
crosslink kickoff run "feature description"
```

**Hard invariant:** `--model opus` / `sonnet` / `haiku` (or omitting
`--model`) will HARD-FAIL — the `claude` wrapper enforces strict model
validation and aborts on implicit or default Anthropic model names.

**Free Zen caution:** free Zen models are rate-limited and their limits are
opaque. They can be exhausted for hours with no way to predict recovery; a
launch may hang, loop, or fail mid-task. Prefer paid Go models
(`opencode-go/*`) for agent work. If you must use a free model, verify it
launches and completes promptly, and fall back to paid Go on any rate-limit
symptom.

**Legacy command forms are blocked:**
- `claude-mode director -- --model opus` — `claude-mode` CLI wrappers are
  deprecated. Use `crosslink kickoff run` or `crosslink swarm launch`.

---

## 4. Pre-Flight Checklist (Before Every Dispatch)

Before launching any background agent, the orchestrator MUST complete:

| Step | Check | Action on Failure |
|------|-------|-------------------|
| 1 | HEAD is clean and on expected branch | Report to operator, wait |
| 2 | Target model is accessible (`opencode models <provider>`) | Halt, report unavailable model |
| 3 | Crosslink issue exists and is claimed (`crosslink session work <id>`) | Create/claim issue first |
| 4 | Worktree directory is clean (no orphan `.kickoff-status` from crashed agents) | Run `crosslink kickoff cleanup --force` |
| 5 | Feature branch does not already exist | Delete stale branch or pick new name |
| 6 | Prompt includes acceptance criteria, scope boundaries, and commit convention | Rewrite prompt before dispatch |

---

## 5. Dispatch Protocol

### 5.1 Single-Agent Kickoff

```
crosslink kickoff run "<feature description>" \
  --model <provider/model-name> \
  --issue <id> \
  --verify local \
  --timeout 1h
```

After dispatch:
1. Print the tmux attach command for the operator.
2. Record the dispatch breadcrumb: `crosslink session action "Dispatched <agent-id> for issue #<N>"`.
3. Do NOT poll obsessively — check status at reasonable intervals (every 5-10 minutes).

### 5.2 Multi-Agent Swarm

```
crosslink swarm init --doc <design-doc.md>
crosslink swarm config --budget-window 2h --model <provider/model-name>
crosslink swarm launch
```

Swarm rules:
- **One phase at a time.** Run `crosslink swarm gate` between phases. Never
  skip gates.
- **Budget windows are hard limits.** Agents exceeding the budget are
  terminated. Set realistic windows.
- **Phases depend on each other.** Encode `blocked_by` edges so `issue ready`
  reflects real ordering (edges are documentation, not machine-gated at
  launch — verify them as a process gate).

---

## 6. Monitoring and Verification

### 6.1 Status Checks

- **Never trust status flags alone.** `RUNNING` persists on dead processes.
  `DONE` may be missing from agents that committed successfully but exited
  before writing the flag.
- **The commit is ground truth.** Monitor by tracking expected commits
  (`[#N]` references), not `.kickoff-status` flags.
- **Distinguish STALLED from WORKING:** Read `ps -o pid,etime,time,stat -p
  <pid>`. TIME climbing = computing; frozen + old heartbeat = stalled.

### 6.2 Output Verification

After every agent completes:
1. **Verify output is non-empty.** A blank or empty review is a CRITICAL
   CRASH, not a pass.
2. **Run deterministic verification** — never LLM-based sampling for
   safety-critical gates.
3. **Build from the main checkout** — worktree artifacts may look committed
   but were never rendered (path resolution issues).

### 6.3 The Micro-Gate (Per-Issue)

Each issue worked by a background agent is independently verified before the
agent moves on:

1. Agent implements changes in worktree.
2. Agent runs review against the issue's original instructions.
3. PASS with zero findings → agent closes the issue.
4. FAIL or any finding → agent fixes and re-reviews.
5. Empty/silent review → CRASH protocol (halt, report, await human).

---

## 7. Failure Protocol — MANDATORY HALT

If ANY delegation fails — for ANY reason (task denial, provider error, rate
limit, timeout, crash, network error, agent returns error):

1. **STOP IMMEDIATELY.** Do not retry. Do not substitute another agent. Do not
   attempt the work yourself.
2. Report the failure clearly: which agent, what it was trying to do,
   suspected reason.
3. **REMAIN HALTED** until the operator responds with explicit direction.

**This is not a guideline — it is a hard constraint.** Violating it is a role
breach. The orchestrator must never silently take over a failed agent's work.

### 7.1 Crash Recovery

1. `ps aux | grep -E 'claude|crosslink'` — confirm what's alive.
2. Let running workers FINISH — they commit and write DONE autonomously.
   Don't kill mid-commit.
3. After workers land: `kill <pid>` (or `kill -9 <pid>` if SIGTERM ignored).
   Confirm with `ps -p <pid>`.
4. Re-assert the signing key for the project's driver identity.
5. Run `crosslink kickoff cleanup --force` to release orphan locks and
   worktrees.
6. Relaunch fresh with state reconstruction from hub + git log — never trust
   prior in-context memory.

---

## 8. Signing Key Discipline

Hub commits are signed with the project's driver key. The key drifts when:
- Workers rewrite signing config on hub commits.
- Deleting a worktree that holds the signing key orphans it, breaking ALL hub
  commits.

**Procedure:** Re-assert the driver key before every kickoff/worktree cleanup,
and after every crash. Verify with `git config --worktree --get
user.signingkey`.

---

## 9. Worktree and Branch Management

- Workers commit to **feature branches only**. Never merge to master or push
  from a worker.
- **Push is operator-gated.** The orchestrator commits and stops; the operator
  pushes.
- **Worktree overlap → merge order:** When workers touch shared files, merge
  the branch that ESTABLISHES a shared file before the one that consumes it.
- **One scope per session.** Never mix unrelated scope in a single worker.

---

## 10. Gate Discipline for Unmonitored Waves

When the operator can't watch:
- Workers commit to feature branches; the orchestrator does NOT merge or push.
- Operator reviews branches on return.
- **The one rule that protects master:** nothing merges unreviewed.
- Skeletons/structure can run unattended (no fidelity judgment);
  fidelity-sensitive work is HELD at a gate.

---

## 11. Verification Asymmetry

**Committed ≠ verified.** Workers run in git worktrees. If a worktree can't
resolve a dependency (e.g., a `file:../../` path at the wrong depth), the
worker may hand-port an artifact that looks committed but was NEVER built or
rendered.

Before trusting such work:
1. BUILD/RENDER it from the main checkout where paths resolve.
2. Run the project's deterministic verification.
3. Only then consider the work verified.

---

## 12. Documentation and Handoff

- **End every session** with `crosslink session end --notes "..."` including:
  what was done, what's pending, any agent crashes, state of branches.
- **Record breadcrumbs** during work: `crosslink session action "..."`.
- **Reference issues in commits:** `feat: description [#N]`.
- **Never edit STATUS.md directly** — it's auto-generated by hooks.
- **Design prompts so a fresh orchestrator can rebuild fully** from the hub
  state + git log. Never rely on in-context memory as source of truth.

---

## 13. Anti-Patterns (Do Not Do These)

| Anti-Pattern | Why It's Dangerous | Correct Behavior |
|-------------|-------------------|------------------|
| Omitting `--model` on kickoff | Silently uses wrong/unavailable model | Always pin explicitly |
| Using `claude-mode` CLI wrappers | Deprecated, inconsistent with Crosslink | Use `crosslink kickoff run` / `crosslink swarm launch` |
| Accepting empty review output | Crash disguised as pass | Halt immediately, report to operator |
| Orchestrator implementing directly | Role breach, rubber-stamp review risk | Delegate to Builder agent |
| Parallelizing unproven patterns | Six agents invent six wrong approaches | Prove serially on one case, then fan out |
| Trusting `.kickoff-status` flags | Flags persist on dead processes | Verify against actual git commits |
| Merging to master from worktree | Unreviewed code reaches production | Operator reviews and merges |
| Retrying a failed delegation | Masks systemic issues, wastes resources | Halt, report, await human direction |
| LLM-based sampling for safety gates | Misses edge cases, not reproducible | Use deterministic verification scripts |
| Pushing from orchestrator | Triggers deploys without operator review | Surface push command for operator |
| Trusting a static permission/model doc | Goes stale; names dead models | Verify against live `opencode models` |

---

## Quick Reference — Commands

```bash
# Choose tier
#   one ticket  -> kickoff
#   multi-phase -> swarm
#   autonomous  -> sentinel (see crosslink-subagent-orchestration.md)

# Single agent dispatch
crosslink kickoff run "feature description" --model <model> --issue <id>

# Swarm setup and launch
crosslink swarm init --doc <design-doc.md>
crosslink swarm config --budget-window 2h --model <model>
crosslink swarm launch

# Status and monitoring
crosslink kickoff status <agent-id>
crosslink swarm status

# Cleanup after crashes
crosslink kickoff cleanup --force

# Session lifecycle
crosslink session start
crosslink session work <id>
crosslink session action "breadcrumb"
crosslink session end --notes "handoff notes"

# Model verification (you can run this yourself)
opencode models opencode
opencode models opencode-go
```
