---
title: "Agent Orchestration Playbook"
tags: ["orchestration", "kickoff", "swarm", "workflow"]
sources: []
contributors: ["ASES"]
created: 2026-08-01
updated: 2026-08-08
---

# Agent Orchestration Playbook

**Scope:** Model-agnostic operational rules for orchestrating multi-agent
sessions via Crosslink kickoff and swarm. Applies to every orchestrator
session regardless of which LLM is driving. This is the **canonical** copy;
project repos may carry a duplicate, but the ASES copy wins on conflict.

This playbook covers **both** tiers of delegation. Read it once — it tells you
which tier applies, the shared rules, and the tier-specific procedures.

**ASES permission note (gh#121):** the mechanical git rules for the four ASES
agent roles are enforced by `.crosslink/hook-config.json`
(`agent_overrides.by_type.*`) via the `crosslink-guard` plugin and snapshotted in
`.opencode/permissions.md`. The Orchestrator's `git commit` and `git merge` are
**gated** on an active Crosslink issue; `git push` is blocked for every role.
Where this playbook says "the orchestrator does NOT merge", read that as process
discipline ("nothing merges unreviewed") — the mechanical gate is
active-issue-gated, not a hard block. Pushing remains operator-only everywhere.

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
| One well-defined ticket that fits a single session (task-matched timeout, see §5.3) | **Kickoff** (`crosslink kickoff run`) |
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

### 2.1 The Task Tool Is Not a Tier — In-Session Read/Research Only

The opencode **Task tool** (and `@explore` / `@general` subagents) is **NOT**
an orchestration tier. It is an in-session, synchronous subagent call. It must
never be used where kickoff/swarm/sentinel apply. The full decision matrix:

| Need | Tool | Execution model | Locking |
|------|------|-----------------|---------|
| In-session read / research / quick-answer — small file reads, summarization, bounded analysis | **opencode Task tool** (or `@explore` / `@general`) | In-session subagent call | **Synchronous, BLOCKING** — the calling session locks until the subagent returns |
| Single implementation ticket | **Kickoff** (`crosslink kickoff run`) | Background tmux/container + own worktree + feature branch + crosslink issue + checkpoint contract | **Non-blocking** — session stays live |
| Multi-phase parallel feature | **Swarm** (`crosslink swarm init` → `launch` → `gate` → `checkpoint`) | Multiple worktrees, hub-branch coordination, budget windows, phase gates | Non-blocking — session stays live |
| Long-running autonomous maintenance | **Sentinel** (separate; see `crosslink-subagent-orchestration.md`) | Persistent daemon, poll-triage-dispatch loop | Non-blocking — session stays live |

**Locking mechanism, stated explicitly:** the Task tool runs **in-session and
synchronously** — the calling orchestrator session is **blocked until the
subagent returns**. While it runs the orchestrator cannot converse with the
operator and cannot dispatch other agents. Kickoff/swarm/sentinel run
**out-of-session** (own tmux/container, own worktree, own crosslink issue and
identity, hub sync, checkpoint contract) — the orchestrator session stays
live and responsive.

**Task-tool constraints (hard):**
- **NEVER use the Task tool for implementation.** It has no worktree
  isolation, no crosslink issue/identity/tracking, no durable commit trail,
  and no checkpoint contract — it cannot produce tracked, verifiable work.
- **NEVER use the Task tool to record review verdicts for the record.**
  Verdicts belong on a crosslink issue via a tracked reviewer session.
- **NEVER use the Task tool for anything requiring a durable
  worktree/commit/tracking trail.**

**Failure evidence (2026-08-06):** agents repeatedly used the Task tool for
actual implementation, which LOCKED the orchestrator session while the
subagent ran — a blocking failure mode kickoff does not have. Any
implementation request routes to kickoff (single ticket), swarm (multi-phase
parallel), or sentinel (autonomous), never to the Task tool.

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
  --timeout <task-matched timeout — see §5.3, never a blanket 1h>
```

After dispatch:
1. Print the tmux attach command for the operator.
2. Record the dispatch breadcrumb: `crosslink session action "Dispatched <agent-id> for issue #<N>"`.
3. Do NOT poll obsessively — check status at reasonable intervals (every 5-10 minutes).
4. Watch for checkpoint comments on the issue (see §5.4) — a missing expected
   checkpoint is a stalled-agent signal, not something to wait out to timeout.

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

### 5.3 Task-Matched Timeout Guidance

**Timeout length is the PRIMARY problem, not merely a feedback problem.**
Evidence: #120 completed a four-file fix in ~3 minutes of real work on a 40m
timeout; review/doc/port tasks all landed in <=30m. The old 45m/40m/1h
defaults overcommit and starve the operator of feedback — a 40m timeout on a
3-minute task means the operator cannot distinguish *working slowly* from
*dead agent* for 37 minutes.

**Timeouts MUST be task-matched. Never use a blanket 1h default.**

| Task type | Realistic ceiling | Rationale |
|-----------|-------------------|-----------|
| Trivial (1-2 files, small change) | **<= 10m** | #120: 4-file fix took ~3 min actual |
| Documentation / simple change | **15-20m** | doc/port tasks observed <=30m, leave headroom |
| Review / audit (read-only) | **15-20m** | setup + verdict fits easily |
| Port / multi-file change | **30m** | 9-file port took ~11 min actual |
| Complex / multi-phase feature | **45m+ — use swarm, not kickoff** | genuinely larger work belongs in swarm with gates and budget windows |

Setup and verification headroom is included in these ceilings. If the task is
estimated to need more than ~45m of sequential single-agent work, that is a
signal to decompose into a swarm rather than to raise the timeout.

**Two-signal stalled detection (checkpoints are the SECONDARY signal):**
1. **Timeout exceeded = likely stalled.** A shorter timeout bounds blind
   waiting; exceeding it is actionable.
2. **No checkpoint for >2x the expected interval = likely stalled.** The
   expected interval is the task ceiling (from the table above) divided by
   the number of milestone checkpoints (~4, see §5.4). A silent agent past
   that window warrants investigation via `ps` and session status — do not
   wait for the timeout.

**Checkpoints do NOT justify retaining a long timeout.** They are a
complement to task-matched ceilings, not a replacement for them.

### 5.4 Progress-Feedback Contract — Mandatory Checkpoint Comments

Every delegated agent MUST report progress to the operator through **milestone
checkpoint comments** on its issue. This is the durable, operator-facing
channel — the operator never waits blind until timeout.

**Checkpoint rules (enforced by the KICKOFF template — see
`kickoff-custom-template.md` and the `Progress Check-Ins` section of the
template):**

- **Post `--kind observation` checkpoint comments at milestones, max ~4 per
  session**: (a) POST-PLAN — immediately after the plan comment; (b) MIDPOINT
  — after the first meaningful completion unit; (c) BLOCKER-OR-VERIFY — a
  blocker report, or verification results; (d) FINAL — the `--kind result`
  comment before session end.
- **Use a scannable prefix and structured fields**: `[PROGRESS] state=working
  completed=<one-line> next=<one-line> blocker=none`, or `[BLOCKED]` /
  `[VERIFY]` / `[DONE]` as appropriate. Required fields: `state`
  (working/blocked/verifying), `completed`, `next`, `blocker`.
- **Sync after posting.** `crosslink issue comment <id> "..." --kind
  observation` followed by `crosslink sync`. Worktree-local comments do NOT
  reach the hub until sync — without it a checkpoint is invisible to the
  operator and cannot distinguish silent work from a dead agent.
- **Missed check-in escalation:** if an expected checkpoint has not arrived by
  the expected interval (see §5.3), investigate: `ps -o pid,etime,time,stat
  -p <pid>` (TIME climbing = working; frozen = stalled), check session status,
  then report to the operator. Do not wait silently for the timeout.
- **Task-awareness:** a <=10m trivial task posts the mandatory start and final
  checkpoints; the midpoint is optional. A >30m task must not post more than
  ~4 comments — milestone-based, never per-action.

**Session-action breadcrumbs are SUPPLEMENTARY telemetry only.** Use
`crosslink session action "..."` for high-frequency internal breadcrumbs
(agent identity, timestamps, process continuity). They are NOT a substitute
for checkpoint comments: session actions are local session metadata, not hub
issue records, and have zero failure-detection value for the operator without
explicit polling of the agent's session state.

**Workflow-topology formalization.** The checkpoint contract above is the
position-emitting agent mechanism of the workflow-topology design; the
durable-store semantics, staleness trigger, pre-positioned AUDITOR, and
review-before-consume gate are in §5.8.

### 5.5 Two-Repo Sync Requirement

The ASES and tripn-astro orchestrator roles are **one process** — the
orchestration contract is shared between the two repos and MUST be updated
together. The following are kept identical across both repos:

- `.crosslink/knowledge/agent-orchestration-playbook.md` (canonical copy:
  ASES wins on conflict; tripn-astro mirrors it)
- `.claude/skills/kickoff/SKILL.md`
- `SESSION-START.md`
- The KICKOFF template (`~/.crosslink/rules/kickoff.md` global + project
  copies) including the `Progress Check-Ins` section
- Orchestrator role definitions (ASES: `docs/ORCHESTRATOR.md`, tripn-astro:
  `.opencode/agents/orchestrator.md`)

**Rule:** any change to these files in one repo MUST be applied to the other
in the same process — never in a follow-up issue. Document the change in the
same place as the timeout guidance so it cannot be missed.

### 5.6 Reviewer Independence — Isolated Sub-Issues

When dispatching MULTIPLE reviewers on the same question, each reviewer MUST
post its verdict to its **OWN isolated sub-issue**. Never dispatch multiple
reviewers onto the same issue thread.

- Create one sub-issue per reviewer (e.g. `#123-r1`, `#123-r2`), each with
  only that reviewer's access/assignment.
- Each reviewer reads only its own sub-issue and posts its verdict there.
- The orchestrator synthesizes after ALL verdicts land, and posts the
  synthesis to the parent issue.
- **Rationale (contamination incident, 2026-08-03):** the second of two
  reviewers on issue #123 read the first reviewer's posted verdict via
  `crosslink issue show 123` before writing its own — its verdict was NOT
  fully independent. Shared-thread dispatch makes later reviewers inherit
  earlier conclusions. This rule makes contamination impossible by
  construction.

This rule applies to every multi-reviewer dispatch: adversarial review
swarms, design reviews, verification reviews — anywhere the same question is
asked of more than one independent reviewer.

### 5.7 Thin-Orchestrator Rule — Bounded Signals Only

The orchestrator consumes **bounded signals only**. Any read requiring large
volume (whole files, full diffs, log analysis) is **delegated to a subagent**
which returns a summary. Never paste large raw output into the orchestrator
context or a shared channel.

**Rationale:** the orchestrator's context is the scarcest resource in the
stack — every token it spends on raw dumps is a token it cannot spend on
planning and coordination. This is the same principle as `webfetch: deny` on
the orchestrator while subagents have fetch: the orchestrator reads at
command/prefix granularity (the allowlist is intentionally scoped, e.g.
`ps -o`, `tail -50`, `git log --oneline`) and receives **summaries**, not
bulk. When a read is unbounded (whole files, full diffs, log analysis),
delegate to a Builder/Reviewer/Auditor subagent and have it return the
summary.

### 5.8 Workflow Topology — Position Store, Staleness, Auditor, Review-Before-Consume

The workflow-topology design (canonical record:
`docs/research/Workflow Topology Design and Reasoning Record.md`, ASES repo;
do not modify the design record) operationalizes how claims, positions,
verification, and consumption interact across role boundaries. Its
dispatch-level mechanics are:

**Position store.** Every delegated agent emits **structured position
updates** to a **durable store** — the Crosslink hub, posted as structured
comments on the working issue, surviving agent restarts:

```
step=<current step>
completed=<what just completed, one line>
next=<what's next>
blocker=<detail or none>
evidence=<link to artifact/evidence>
```

This is §5.4's checkpoint contract formalized as a durable, structured,
queryable stream. Cadence is **task-adaptive** (from the dispatch spec, or the
default: every state transition + every Nth idle minute + at any blocker) — a
5-minute task does not emit 5 checkpoints. Claims inside positions that cross a
role boundary carry the certainty disclosure (WHY / WHAT / HOW-CERTAIN /
WHAT-NOT-TESTED) per AGENTS.md.

### 5.8.1 Validated cadence + two-phase-auditor dispatch defaults (TENTATIVE)

**TENTATIVE — n=1 lifecycle (session #20, hydration epic closeout,
2026-08-08); 3 silent-hangs caught with zero artifact loss; limited evidence —
adjustments within scope IF failure modes are encountered.**

1. **Validated cadence defaults.** First position within ~2 min of session
   start; position at every state transition AND at least every ~10 min even
   during silent exploration (post `step=exploring`, `completed=<files read>`,
   `evidence=<file refs>`). `completed` claims MUST carry an
   artifact/commit/test-log link — a claim without evidence IS a divergence
   flag.
2. **Phase-1 auditor dispatch.** Launch the in-flight auditor ALONGSIDE the
   builder at dispatch (pre-positioned, per the existing §5.8 rule); give it
   the trigger set + the builder's expected cadence explicitly in the prompt.
   It reports divergence to the orchestrator only, never acts.
3. **Phase-2 auditor.** Post-hoc, model-varied from Phase 1; verifies outcome
   (architectural consistency) + process (tracking/commit hygiene/claim
   discipline) + systemic issues. CONDITIONAL verdicts with named
   preconditions are the expected output shape.
4. **Verification-tail pattern.** When a builder silent-hangs post-commit
   (committed but no final verification), dispatch a verification-only builder
   to complete the tail: tests re-run, binary rebuild, sha==commit check, live
   sanity, per-item evidence result.

**The stops.** Two gates control the producer-consumer edges:

1. **Review-before-consume** — the REVIEWER is the **pre-consumption readiness
   audit**: verify the artifact is *ready to be consumed* (testability,
   acceptance criteria, evidence presence, certainty labels present,
   cheapest-test evidence present). It is **not** "verify the truth"; it is
   "verify the artifact admits verification and carries the required
   calibration." Untestable claims are declared untestable with stated residual
   risk — a first-class, non-penalized outcome.
2. **Pre-positioned AUDITOR** — the AUDITOR is the **in-flight divergence
   verifier**, **one role with two phases** (Phase 1 in-flight monitor: "Is
   work on track as claimed?"; Phase 2 post-hoc audit: "Did outcome and process
   hold up?"), **pre-positioned** (launched alongside the Builder at dispatch
   as a continuous in-flight monitor — the trigger set does NOT summon it; a
   trigger causes the already-present AUDITOR to act), read-only, flag-only.
   **No duplicate Verifier role** — a separate Verifier would duplicate the
   AUDITOR's read-only verification point without guarding a distinct failure
   class. Models may vary across phases (Phase 1 cheap/bounded, model-varied
   from the Builder; Phase 2 heavier/rarer). It flags to the orchestrator,
   which owns the bounded action set (investigate/nudge/stop-resume).

**Cheap staleness trigger.** A position/heartbeat **stale >2x its expected
interval** triggers investigation — a cheap clock comparison against the
durable store, and the *primary* trigger that causes the pre-positioned
AUDITOR to act. Logical trigger set:

1. position/heartbeat staleness (>2x expected interval);
2. position-vs-artifact claim mismatch (text claims "tests pass" but no test
   run in the evidence);
3. reviewer disagreement (split verdicts);
4. evidence-accuracy flags from the REVIEWER;
5. orchestrator-explicit request.

**Orchestrator as single integration point.** All agent surfaces (positions,
AUDITOR flags, reviewer verdicts) flow through the orchestrator; the
orchestrator owns the action set and **surfaces only decisions** to the
operator. The operator supervises the **orchestrator**, not the swarm. The
orchestrator itself emits a position/heartbeat (staleness applies to it too).

---

## 6. Monitoring and Verification

### 6.1 Status Checks

- **Never trust status flags alone.** `RUNNING` persists on dead processes.
  `DONE` may be missing from agents that committed successfully but exited
  before writing the flag.
- **The commit is ground truth.** Monitor by tracking expected commits
  (`[#N]` references), not `.kickoff-status` flags.
- **Checkpoint comments are the progress signal.** A synced `--kind
  observation` checkpoint (see §5.4) proves the agent is alive and working. A
  missing checkpoint past the expected interval is a stalled-agent signal —
  investigate before the timeout.
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
4. **Verify against the hub agent refs, not the local DB** — see §6.5.
   Agent output (reviews, results, checkpoints) lives in
   `refs/heads/crosslink/agents/<id>/events.log` and is readable via git
   without any sync.

### 6.3 The Micro-Gate (Per-Issue)

Each issue worked by a background agent is independently verified before the
agent moves on:

1. Agent implements changes in worktree.
2. Agent runs review against the issue's original instructions.
3. PASS with zero findings → agent closes the issue.
4. FAIL or any finding → agent fixes and re-reviews.
5. Empty/silent review → CRASH protocol (halt, report, await human).

### 6.4 Agent Lifecycle Watcher — Phase 1 (monitor + notify)

A systemd user timer (`ases-kickoff-notify.timer` → `ases-kickoff-notify.service`)
runs `tools/kickoff-notify.py` every 15s against `~/.worktrees/*/` (all repos
using this playbook). Phase 1 is strictly **monitor + notify**: it observes
kickoff agents and alerts the operator on lifecycle transitions. It performs
**no** destructive action (no kill, no relaunch, no commit).

**Signals read per agent:**
- `.kickoff-status` — LAUNCHING / RUNNING / DONE / FAILED / CI_FAILED.
- `.kickoff-metadata.json` — `started_at` + `timeout_secs` (per-model stall
  scaling).
- `.crosslink/.cache/last-heartbeat` — **PRIMARY liveness signal** (mtime;
  written by the PostToolUse heartbeat hook, throttled 120s).

**State machine:** LAUNCHING → RUNNING → DONE | FAILED | CI_FAILED, plus a
derived STALLED state (heartbeat stale past threshold, on **2 consecutive
detections**, outside the LAUNCHING grace period). STALLED → notify only.

**Notifications:** COMPLETED / FAILED / CI_FAILED / STALLED → `notify-send`
(desktop) + optional webhook POST (`KICKOFF_NOTIFY_WEBHOOK`). `notify-send`
is absent on this host (libnotify-bin missing — #133 verdict); the watcher
degrades gracefully to webhook + logs. Install with
`sudo apt install libnotify-bin`.

**Known Phase 1 limitations (Phase 2/3 pending):**
- **Heartbeat hook gap:** worktrees currently do NOT carry
  `.claude/hooks/heartbeat.py` (only the main checkout does), so the heartbeat
  file is often absent. The watcher handles absence conservatively (no
  false-positive STALLED from a missing file; falls back to timeout-overrun
  detection). Installing the hook into worktrees is a Phase 2 item.
- **No completion-edge detection yet:** a finished-but-flagless agent (commit
  present, DONE missing — §6.1) is not yet classified as COMPLETED; that is
  Phase 2 hardening.
- **No watchdog fix / no kill / no relaunch:** the inert crosslink watchdog
  (launch.rs exit-condition bug) and all destructive recovery are Phase 2/3.

**Two-repo sync (§5.5):** this section is mirrored to tripn-astro's
`.crosslink/knowledge/agent-orchestration-playbook.md` in the same process,
and the `tools/kickoff-notify.py` + systemd units belong in both repos'
landing points per §5.5.

### 6.5 Hub Refs Are Ground Truth — Agent Output

**Hub agent refs are the ground truth for agent output — NOT the local
main-repo SQLite DB.** Each kickoff/swarm agent's output (reviews, results,
checkpoint comments) is recorded as `CommentAdded` events on its hub agent
ref: `refs/heads/crosslink/agents/<id>/events.log`. The local SQLite DB is a
hydrated cache and can lag, be stale, or (worst case) roll back to an older
hub checkpoint.

Operational rules:

1. **To verify agent output, read the hub agent refs** — NOT the local DB:
   ```
   git show refs/heads/crosslink/agents/<id>/events.log
   git log --oneline refs/heads/crosslink/agents/<id>
   ```
   This works WITHOUT any sync and is the safe way to confirm what an agent
   actually produced.
2. **NEVER run `crosslink sync` in the main repo to 'refresh' visibility.**
   `sync.fetch()` rehydrates the local SQLite from hub state — when the hub
   checkpoint is stale, this DROPS local-only issues and comments. This is
   the exact command that caused the June rollback (tripn-astro
   #338/#342/#370-376) and the repeated '#N not found' drops this session
   (ASES #123/#124/#137). To recover visibility, re-hydrate safely or run
   `crosslink compact` — never blind-sync.
3. **Liveness and data-visibility are separate failures** — a dead agent and
   an un-synced comment trail are different problems with different
   remedies (see #125, and §6.4 for the watcher).

**Durable root-cause fix (2026-08-06):** the unguarded `maybe_auto_hydrate`
v2 wipe path is fixed in the crosslink fork (commit `ade6146b` — fail-closed
gate on v3-ref presence, binary rebuilt and live); `crosslink compact` remains
the interim recovery for older binaries.

### 6.6 Standing Workflow — Agent Status Notes + Wave Cleanup

While any kickoff/swarm agent is running, the orchestrator follows a
standing workflow every turn:

1. **Every orchestrator turn ends with a brief Agent Status note** — state,
   time-in, last signal — even if unchanged. This is a standing turn-ending
   discipline, not an occasional update. A silent turn is indistinguishable
   from a dead session; the note keeps the operator able to distinguish
   *working slowly* from *stalled* without polling.
2. **Run `crosslink kickoff cleanup` after each dispatch wave.** Assess STALE
   agents with `--dry-run --force` first; preserve work before removing —
   never destroy an agent's commits or worktree without confirming the work
   is captured elsewhere.
3. **The Phase 1 lifecycle watcher (§6.4) is a supplement, not a
   substitute** for the standing Agent Status note. The watcher monitors
   heartbeat/lifecycle automatically (monitor + notify only); the turn-ending
   note is the orchestrator's own liveness contract with the operator.

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
  pushes. In ASES the orchestrator may also `git merge` (gated on an active
  issue — see `.opencode/permissions.md`), but push stays operator-only.
- **Worktree overlap → merge order:** When workers touch shared files, merge
  the branch that ESTABLISHES a shared file before the one that consumes it.
- **One scope per session.** Never mix unrelated scope in a single worker.

### 9.1 Operator Git Convention — No Interactive Editors (repo-agnostic)

**OPERATOR GIT CONVENTION:** the operator does not want to interact with
interactive editors (vim/nano). Every operator-gated git command that would
open an editor MUST include `--no-edit` (e.g. `git merge --no-ff <branch>
--no-edit`, `git commit --no-edit`, `git cherry-pick --continue --no-edit`).
As a safety net the operator may set: `git config --global core.editor true`
(or `export GIT_EDITOR=true`) so no git command ever opens an editor.

---

## 10. Gate Discipline for Unmonitored Waves

When the operator can't watch:
- Workers commit to feature branches; the orchestrator does NOT push. In ASES the
  orchestrator's `git merge` is gated on an active issue, so a merge is only
  possible while an issue is in flight — never treat a gated merge as a licence
  to merge unreviewed work.
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
- **Post milestone checkpoint comments** during work (see §5.4): `crosslink
  issue comment <id> "[PROGRESS] state=... completed=... next=... blocker=..."`
  `--kind observation`, then `crosslink sync`. Max ~4 per session.
- **Record breadcrumbs** as supplementary telemetry: `crosslink session action
  "..."`. They are not a substitute for checkpoint comments.
- **Reference issues in commits:** `feat: description [#N]`.
- **Never edit STATUS.md directly** — it's auto-generated by hooks.
- **Design prompts so a fresh orchestrator can rebuild fully** from the hub
  state + git log. Never rely on in-context memory as source of truth.

---

## 13. Anti-Patterns (Do Not Do These)

| Anti-Pattern | Why It's Dangerous | Correct Behavior |
|-------------|-------------------|------------------|
| Using the opencode Task tool for implementation | Synchronous in-session subagent BLOCKS the calling session; no worktree, no crosslink issue/tracking, no commit trail (repeated incidents, 2026-08-06) | Task tool = in-session read/research/quick-answer ONLY; implementation → kickoff/swarm/sentinel (§2.1) |
| Omitting `--model` on kickoff | Silently uses wrong/unavailable model | Always pin explicitly |
| Blanket `--timeout 1h` on every kickoff | Overcommits, starves operator of feedback, hides dead agents | Task-match the timeout (§5.3) |
| Using `claude-mode` CLI wrappers | Deprecated, inconsistent with Crosslink | Use `crosslink kickoff run` / `crosslink swarm launch` |
| Accepting empty review output | Crash disguised as pass | Halt immediately, report to operator |
| Orchestrator implementing directly | Role breach, rubber-stamp review risk | Delegate to Builder agent |
| Parallelizing unproven patterns | Six agents invent six wrong approaches | Prove serially on one case, then fan out |
| Trusting `.kickoff-status` flags | Flags persist on dead processes | Verify against actual git commits |
| Waiting silently until timeout for progress | Wastes operator time, hides stalls | Watch checkpoint comments; escalate on missed check-ins (§5.4) |
| Relying on session actions for operator visibility | Local metadata, invisible at hub | Use synced checkpoint comments; actions are supplementary |
| Dispatching multiple reviewers on one thread | Later reviewers inherit earlier verdicts | Per-reviewer isolated sub-issues (§5.6) |
| Merging to master from worktree | Unreviewed code reaches production | Operator reviews and merges |
| Retrying a failed delegation | Masks systemic issues, wastes resources | Halt, report, await human direction |
| LLM-based sampling for safety gates | Misses edge cases, not reproducible | Use deterministic verification scripts |
| Pushing from orchestrator | Triggers deploys without operator review | Surface push command for operator |
| Trusting a static permission/model doc | Goes stale; names dead models | Verify against live `opencode models` |
| Reading agent output from the local SQLite DB | DB is a hydrated cache; can be stale or rolled back | Read hub agent refs (`git show refs/heads/crosslink/agents/<id>/events.log`, §6.5) |
| Running `crosslink sync` in the main repo to 'refresh' visibility | Rehydrates from stale hub state; drops local-only issues (June rollback) | Re-hydrate safely or `crosslink compact`; never blind-sync (§6.5) |
| Ending orchestrator turns silently while agents run | Silent turns are indistinguishable from dead sessions | End every turn with a brief Agent Status note (§6.6) |
| Skipping `crosslink kickoff cleanup` between waves | Orphaned STALE agents and locks accumulate | Assess STALE with `--dry-run --force`, preserve work, then remove (§6.6) |

---

## Quick Reference — Commands

```bash
# Choose tier
#   in-session read/research/quick-answer -> opencode Task tool (BLOCKS session — NEVER implementation)
#   one ticket  -> kickoff
#   multi-phase -> swarm
#   autonomous  -> sentinel (see crosslink-subagent-orchestration.md)

# Single agent dispatch
#   --timeout: task-matched per §5.3 (trivial <=10m, doc/simple/review 15-20m,
#              port/multi-file 30m, complex multi-phase 45m+ -> swarm)
crosslink kickoff run "feature description" --model <model> --issue <id> --timeout 20m

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
crosslink session action "breadcrumb"          # supplementary telemetry only
crosslink issue comment <id> "[PROGRESS] state=working completed=... next=... blocker=none" --kind observation
crosslink sync                                  # ALWAYS sync after posting a checkpoint
crosslink session end --notes "handoff notes"

# Model verification (you can run this yourself)
opencode models opencode
opencode models opencode-go
```
