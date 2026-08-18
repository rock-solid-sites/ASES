---
title: Failure Matrix
program: EDASES
layer: Research
document_type: Registry
status: Active
authority: Derived
canonical_repository: edases

depends_on:
  - AI Capability Registry Specification
  - Agent Orchestration Playbook

consumed_by:
  - Agent Orchestration Guide
  - Hook Implementation Priorities

related_documents:
  - Model Routing Matrix
  - Harness Capability Matrix

supersedes: []
review_frequency: Monthly (or per-session)
last_reviewed: 2026-08-18

---

# Failure Matrix

**Date:** 2026-08-18
**Source:** Recurring workflow failures observed across EDASES orchestration sessions, including HMS research session post-mortem (#519), #506 regression-stall report, #522 doc-navigation probe, multiple agent timeouts, and historical Claude Code project documentation.
**Convention:** Rows are recurring failure classes. Columns describe the required semantic that would prevent or detect each failure, evidence quality, and hookability.

---

## Purpose

This matrix maps recurring workflow failures to the required semantic that would prevent or detect them. It serves as:

1. A diagnostic reference for orchestrators encountering failures
2. A prioritization tool for hook implementation (which semantics to enforce first)
3. A living record of observed failure patterns and their root causes
4. A bridge between observed failures and architectural requirements

Unlike the AI Capability Registry (which records what systems *can* do), this matrix records what *goes wrong* and what capability would be needed to prevent it.

---

## Evidence Quality

Following the AI Capability Registry Specification, evidence quality is categorized:

1. **Replicated experimental evidence** — failures reproduced under controlled conditions
2. **Repeated project observations** — same failure class observed multiple times across sessions
3. **Independent reviewer agreement** — multiple agents/observers confirm the failure pattern
4. **Single project observations** — one-time occurrence, not yet replicated
5. **Vendor documentation** — documented in external sources
6. **Anecdotal reports** — unverified or partial observations

---

## Confidence Assessment

Confidence levels reflect the quantity and quality of supporting evidence:

- **Preliminary** — single observation, not yet replicated
- **Emerging** — 2-3 observations, pattern forming but not confirmed
- **Moderate** — repeated observations across multiple sessions
- **High** — consistent pattern with multiple independent confirmations
- **Well Established** — extensively documented, root causes understood

---

## Failure Matrix

| Failure Class | Required Semantic | Evidence | Confidence | Hookable? |
|---------------|-------------------|----------|------------|-----------|
| **Agent infinite loop** — agent repeats the same action indefinitely without progress | **Liveness observation + escalation** — external watchdog detects lack of state change and escalates (kill, operator alert) | HMS post-mortem §9: pathological monitoring loops; orchestrator repeatedly issued same check command against same agent pane in tight succession without advancing work (#519); playbook §5.3 documents "no new commit for >2x budget = likely stalled" | High | Yes — watchdog timer on session activity; escalation hook on repeated identical tool calls |
| **Agent exceeds expected duration** — agent runs longer than task-matched timeout | **Deadline/attention state** — agent maintains explicit deadline awareness; external monitor enforces timeout | HMS post-mortem: orchestrator failed to bound monitoring cadence; playbook §5.3 documents task-matched timeouts (trivial <=10m, doc 15-20m, review 15-20m, port 30m, complex 45m+) | Well Established | Yes — timeout enforcement in crosslink-guard; agent deadline injection via kickoff template |
| **Agent legitimately exceeds duration** — task genuinely requires more time than estimated | **No automatic termination** — system distinguishes legitimate work from stalls; allows human override | Playbook §5.3: "A shorter timeout bounds blind waiting; exceeding it is actionable" — but legitimate work should be re-scoped, not killed; playbook documents "if timeout exceeded = likely stalled" but acknowledges legitimate work exists | Moderate | Partial — requires human judgment to distinguish stall from legitimate work; hook can alert but not auto-terminate |
| **Worker dies** — agent process crashes or is killed externally | **Worker-loss detection** — system detects process death and reports to orchestrator | Handoff-failure-analysis.md: agent session degraded into generation loop; playbook §5.3 documents "timeout exceeded = likely stalled" — process death is a subclass of stall | High | Yes — process monitoring via systemd/tmux; crosslink session status detection |
| **Relaunch claimed but didn't happen** — orchestrator believes agent was relaunched but launch failed | **Authoritative worker lifecycle** — single source of truth for worker state; launch verification required | HMS post-mortem §4: orchestrator dispatched unrequested builder to change config; playbook §4 pre-flight checklist requires "crosslink issue exists and is claimed" before dispatch | Moderate | Yes — launch verification in crosslink-guard; pre-flight checklist enforcement |
| **Engine restarts** — execution engine or orchestration layer restarts unexpectedly | **Durable state recovery** — all workflow state survives restarts; position store is authoritative | Playbook §5.8: "position store... durable store — the Crosslink hub, posted as structured comments on the working issue, surviving agent restarts" | High | Yes — durable state via crosslink hub; checkpoint contract ensures recoverable state |
| **Queue item disappears** — scheduled work item vanishes from queue without completion | **Durable scheduling** — work items persisted to durable storage; loss detection | Not directly observed in current sessions; identified as architectural requirement in workflow topology design | Emerging | Partial — crosslink issue tracking provides durability; but queue mechanics are not yet implemented |
| **Timer disappears** — scheduled timer or alarm vanishes without firing | **Durable timer** — timers persisted to durable storage; loss detection | Not directly observed in current sessions; identified as architectural requirement for execution engine | Preliminary | Partial — crosslink checkpoint contract provides some durability; but explicit timer persistence not yet implemented |
| **Agent repeats work after retry** — agent performs same work that was already completed | **Idempotency** — operations are idempotent; duplicate detection prevents re-execution | Handoff-failure-analysis.md: fresh model instance reconstructed plausible project model while lacking validation mechanisms; playbook §2.1 documents Task tool misuse causing blocking | Moderate | Yes — git-based idempotency checks; crosslink issue state tracking prevents duplicate work |
| **Agent makes partial progress** — agent completes some work but fails before finishing | **Checkpoint/recovery** — work checkpointed incrementally; recovery from last checkpoint possible | Playbook §5.4: "builders commit incrementally every ~5 minutes of work — small, resume-friendly commits, so a death loses at most one commit's worth" | High | Yes — incremental commits; crosslink checkpoint contract; worktree isolation |
| **Worktree disappears** — isolated work environment vanishes | **Environment reconstruction** — worktree state persisted; can be reconstructed from durable state | Not directly observed; worktree isolation is architectural assumption in kickoff/swarm design | Preliminary | No — worktrees are filesystem-based; reconstruction requires manual intervention |
| **Multiple workers collide** — agents attempt to modify same resources simultaneously | **Reservation/ownership** — resource locking prevents concurrent modification | Playbook §5.6: reviewer independence via isolated sub-issues; contamination incident documented where second reviewer read first reviewer's verdict | Moderate | Yes — crosslink lock system; issue-level resource ownership; worktree isolation |
| **Orchestrator loses context** — orchestrator session loses understanding of project state | **Queryable execution history** — all decisions and state changes are recorded and queryable | HMS post-mortem §3: orchestrator theorized from source code instead of reading documentation; playbook §5.7: "the orchestrator's context is the scarcest resource in the stack" | High | Partial — crosslink issue comments provide history; but context window limits are inherent to LLM architecture |

---

## Evidence Sources

### Primary Evidence (Today's Incidents)

1. **HMS Research Session Post-Mortem (#519)** — documented pathological monitoring loops, role-boundary breaches, over-conclusion from transient errors, and unapproved configuration changes. Key failure classes: agent infinite loop, orchestrator loses context, relaunch claimed but didn't happen.

2. **#506 Regression-Stall Report** — agent stalled without progress detection. Key failure classes: agent exceeds expected duration, worker dies.

3. **#522 Doc-Navigation Probe** — agent failed to navigate documentation correctly. Key failure classes: agent makes partial progress, orchestrator loses context.

4. **Multiple Agent Timeouts** — agents exceeding task-matched timeouts across sessions. Key failure classes: agent exceeds expected duration, agent infinite loop.

### Secondary Evidence (Historical)

5. **Handoff Failure Analysis** — fresh model instance reconstructed plausible project model while lacking validation mechanisms; session degraded into generation loop. Key failure classes: orchestrator loses context, agent infinite loop, agent repeats work after retry.

6. **Playbook Documentation** — §5.3 task-matched timeouts, §5.4 checkpoint contract, §5.6 reviewer independence, §5.8 workflow topology. Provides architectural requirements for preventing multiple failure classes.

7. **Historical Claude Code Project Documentation** — `docs/historical/` and `docs/methodology/` contain process knowledge from earlier project phases. Key patterns: role-boundary breaches, autonomous fallback behaviors, context corruption.

---

## Hook Implementation Priorities

Based on confidence level and hookability, prioritized for implementation:

### High Priority (High Confidence + Yes Hookable)

1. **Agent infinite loop** — watchdog timer on session activity; escalation hook on repeated identical tool calls
2. **Agent exceeds expected duration** — timeout enforcement in crosslink-guard; agent deadline injection via kickoff template
3. **Worker dies** — process monitoring via systemd/tmux; crosslink session status detection
4. **Agent makes partial progress** — incremental commits; crosslink checkpoint contract; worktree isolation
5. **Multiple workers collide** — crosslink lock system; issue-level resource ownership; worktree isolation

### Medium Priority (Moderate Confidence + Yes/Partial Hookable)

6. **Agent repeats work after retry** — git-based idempotency checks; crosslink issue state tracking
7. **Relaunch claimed but didn't happen** — launch verification in crosslink-guard; pre-flight checklist enforcement
8. **Engine restarts** — durable state via crosslink hub; checkpoint contract

### Lower Priority (Emerging/Preliminary Confidence)

9. **Queue item disappears** — crosslink issue tracking provides some durability
10. **Timer disappears** — crosslink checkpoint contract provides some durability
11. **Agent legitimately exceeds duration** — requires human judgment
12. **Worktree disappears** — requires manual intervention
13. **Orchestrator loses context** — inherent LLM limitation; partial mitigation via history

---

## Maintenance

This is a **living document** updated at the end of every session and reviewed regularly.

### Update Protocol

1. **End of session:** if a new failure class was observed or an existing class was confirmed, update the matrix with evidence citations and adjust confidence levels.
2. **Weekly review:** review open issues for failure patterns; update evidence quality and confidence assessments.
3. **Monthly review:** comprehensive review of all entries; retire outdated entries; add new failure classes from accumulated evidence.
4. **After incidents:** post-mortem findings feed directly into this matrix with appropriate evidence citations.

### Version History

| Date | Change | Author |
|------|--------|--------|
| 2026-08-18 | Initial creation with 13 failure classes seeded from today's incidents and historical documentation | pp3g-5w3e builder agent |

---

## Relationship to Other Documents

- **AI Capability Registry Specification** — defines the evidence-based, confidence-assessed documentation pattern used here
- **Model Routing Matrix** — routes models to tasks; this matrix routes failures to required semantics
- **Harness Capability Matrix** — evaluates harness capabilities; this matrix evaluates failure patterns
- **Agent Orchestration Playbook** — operationalizes the required semantics as rules and procedures
- **Hook Implementation Priorities** — future document mapping required semantics to concrete hook implementations

---

## Future Evolution

This matrix is expected to grow as:

1. More sessions are conducted and failure patterns are confirmed
2. Hook implementations are built and their effectiveness is measured
3. New failure classes emerge from more complex orchestration patterns
4. The execution engine implements durable primitives that address architectural requirements

The matrix serves as both a research record and an operational prioritization tool for the ASES execution engine implementation.
