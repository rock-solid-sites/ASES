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

> **Active derived failure-evidence register; local interpretation reviewed 2026-11-24.** This matrix accumulates observed workflow failures and the semantics that could prevent or detect them. Retain the cumulative judgments and supporting observations, including counterexamples and uncertainty. Its August–November historical body below is preserved, including contemporaneous confidence assessments and proposed mechanisms. This does not verify the current EDASES upstream revision. The original [source snapshot](https://github.com/rock-solid-sites/ASES/blob/5984862111f721b058943282227c0aff73d19acd/docs/research/registry/Failure-Matrix.md) remains available. The former Hookability Matrix and hook implementation priorities are historical only. They are not current requirements, deployment claims, or an active maintenance schedule.

## Current interpretation and use

Use failure classes to inform task preparation, design reviews, discriminating tests, and evidence-based requirements proposals. Do not infer a current rule, implementation, or priority from an old hook classification. Current authority lives in the [AI Orchestration Guide](../../methodology/AI%20Orchestration%20Guide.md), [Task-Scoped Information and Handoff Method](../../methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md), [Methodology-to-Requirements Mapping](../../requirements/Methodology%20to%20Requirements%20Mapping%20Specification.md), [Execution Engine Vision](../../architecture/Execution%20Engine%20Vision.md), [Kernel-0 Evidence Packet](../kernel-0/Kernel-0-Evidence-Packet.md), and applicable [current skills](../../../skills/current/README.md). Each has a different scope; this research register does not supersede any of them.

### Transferable failure semantics

The following is a crosswalk of existing observations and candidate protective semantics, not a new mandatory pipeline or claim of runtime enforcement.

| Failure family in the earlier matrix | Transferable question or semantic | Evidence and limits |
| --- | --- | --- |
| Repeated actions without progress; expected duration exceeded; legitimately long work | Observe task-specific progress independently of process liveness; distinguish a deadline or budget being reached from a diagnosis of stall; escalate, re-scope or stop within authorized limits. | Repeated historical observations. Legitimate duration overruns remain distinct; historical fixed timeouts and watchdog mechanisms are not current defaults. |
| Worker loss; claimed relaunch never occurs | Separate launch intent, observed execution, loss, completion and accepted effects. Verify identity and actual transition before reporting or repeating a launch. | Historical incidents and architectural motivation; a normally exited worker with missing finalization is not a crash. |
| Engine restart; partial progress; vanished worktree; orchestrator context loss | Durable work and recoverable position independent of an executor or temporary workspace; preserve substantive decisions and verified remote checkpoints as work proceeds. | Historical partial work, handoff and context failures support the goal. A lost worktree is a proposed failure case in the original matrix, not an observed incident there. Current destination-first recovery is defined by the task-scoped method. |
| Duplicate execution after retry; conflicting workers | Preserve effect identity and outcomes; resolve uncertain effects before repeating them; enforce actual authority/ownership, isolate conflicting work and exclude superseded execution authority. | Historical duplicate-work and review-contamination evidence is useful but does not prove a particular lock, idempotency implementation, or atomic replacement mechanism. Kernel-0 defines the substrate constraints separately. |
| Lost scheduled work or timer | If the chosen realization requires persistent scheduling/timers, test the loss and recovery semantics of those responsibilities. | Explicitly unobserved architectural hypotheses in this matrix; not established Kernel primitives or a requirement to build a scheduler. |
| Work completed but finalization fails | Distinguish substantive output, permission to report, publication, independent readback, terminal status and acceptance. Allow separately authorized durable reporting without granting mutation of the target. | Repeated historical role-permission and reporting failures (including absent comments and stale running status); preserve distinctions between mechanisms and actual outcomes. |
| Stale model catalog; quota/credential mismatch; tier-associated stalls | Verify exact model/route/account and current entitlement independently; detect mismatch and classify failures at observed boundaries. Capability evidence informs selection but cannot authorize fallback, spend, credential changes or retries. | Dated multi-session routing evidence and a verified historical key-store divergence; neither old costs, catalog counts, key locations nor remediation commands establish the current configuration. See [Model Routing Matrix](Model-Routing-Matrix.md), [current launch skill](../../../skills/current/agent-launch/SKILL.md), and [capability/failure history](../../historical/Capability%20Observation%20and%20Failure%20Attribution%20History.md). |
| Disk-pressure/environmental crashes | Distinguish infrastructure health, process failure and artifact durability; verify resources relevant to the actual task. | Listed in historical incidents/priorities, without a dedicated original row. Do not infer that a particular crash was caused by disk or memory pressure without evidence. |
| Plugin exists but tools are absent; authentication drift | Separate package, registration, discovery, authentication, execution and independently verified side effects. Check the earliest discriminating boundary before changing infrastructure. | [November 6 case](../Projektor%20MCP%20Registration%20Failure%20Case%202026-11-06.md), single incident, not a universal connector implementation rule. |

### Evidence accumulation and attribution

Continue to use the original evidence hierarchy. Record dated observations with their actual system, route, task, outcome, source and limitations. Repeated symptoms can justify a strong failure-pattern assessment even when their root causes differ. Distinguish confidence in the observed pattern from confidence in the causal explanation or effectiveness of a proposed prevention mechanism. Retain earlier assessments; add qualifications rather than silently rewriting them. New findings should be added at their verified scope, with a reference to the original evidence; no fixed session-end ritual or compulsory review cadence is created here.

For example, the [November streaming diagnostic history](../../historical/Capability%20Observation%20and%20Failure%20Attribution%20History.md#november-diagnostic-evidence) records an authenticated run with sustained wire bytes but no CLI answer text, contradicting idle transport for that run only. That observation refines the earlier no-output and free-tier stall classes; it does not negate their cumulative evidence or establish a common provider/model cause. Keep request delivery, headers, byte progress, decoded events, persisted output and termination distinct. The ongoing diagnostic investigation retains its own evidence and ownership.

Use the [historical Hookability Matrix](Hookability-Matrix.md) and [harness design history](../../historical/Harness%20Setup%20and%20Permission%20Design%20History.md) to understand why particular intervention points and mechanisms were investigated. Do not revive their old hook backlog or assume mechanical protection from a historical hook, prompt convention or named role.

## Preserved original register and implementation history

The material from this point onward is the earlier register, retained verbatim for provenance. Its old playbook, hookability column, implementation priorities and maintenance section are historical, not operating instructions. The cumulative observations remain useful research evidence.

**Date:** 2026-08-18
**Source:** Recurring workflow failures observed across EDASES orchestration sessions, including HMS research session post-mortem (#519), #506 regression-stall report, #522 doc-navigation probe, multiple agent timeouts, and historical Claude Code project documentation. Updated 2026-08-18 with evidence from today's session: pre-positioned auditor loops (#506 regression agents, pp3g-tU4X), 10+ agent timeouts across models, finalization gaps (#398/#355), model-catalog staleness (Tools #4), free-model stall patterns, and disk-pressure crashes. Post-407 evidence pass: added 6+ finalization-gap instances (pp3g-Fsyf, pp3g-gUUV, pp3g-qO5v, pp3g-Jo2n, pp3g-ATNS, pp3g-cCNd context), big-pickle startup stall (pp3g-cCNd), qO5v/ATNS timeout evidence.
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
| **Agent infinite loop** — agent repeats the same action indefinitely without progress | **Liveness observation + escalation** — external watchdog detects lack of state change and escalates (kill, operator alert) | HMS post-mortem §9: pathological monitoring loops; orchestrator repeatedly issued same check command against same agent pane in tight succession without advancing work (#519); playbook §5.3 documents "no new commit for >2x budget = likely stalled"; 2026-08-18: pre-positioned auditor (pp3g-tU4X) looped on 'rtk git status --short' (denied, repeated, zero progress); #506 regression agents looped; HMS post-mortem documented loops — multiple independent recurrences confirm pattern | Well Established | Yes — watchdog timer on session activity; escalation hook on repeated identical tool calls |
| **Agent exceeds expected duration** — agent runs longer than task-matched timeout | **Deadline/attention state** — agent maintains explicit deadline awareness; external monitor enforces timeout | HMS post-mortem: orchestrator failed to bound monitoring cadence; playbook §5.3 documents task-matched timeouts (trivial <=10m, doc 15-20m, review 15-20m, port 30m, complex 45m+); 2026-08-18: ~10+ agents timed out across models (big-pickle, deepseek-flash-free, laguna all timed out; only paid Mimo-v2.5 consistently completed) — consistent pattern across sessions; ADDITIONAL: pp3g-qO5v (#410) exceeded 30m timeout at finalization (work delivered but process exited without finalizing .kickoff-status); pp3g-ATNS (#407) timed out at 30m (failure-matrix diff work recovered by orchestrator) | Well Established | Yes — timeout enforcement in crosslink-guard; agent deadline injection via kickoff template |
| **Agent legitimately exceeds duration** — task genuinely requires more time than estimated | **No automatic termination** — system distinguishes legitimate work from stalls; allows human override | Playbook §5.3: "A shorter timeout bounds blind waiting; exceeding it is actionable" — but legitimate work should be re-scoped, not killed; playbook documents "if timeout exceeded = likely stalled" but acknowledges legitimate work exists | Moderate | Partial — requires human judgment to distinguish stall from legitimate work; hook can alert but not auto-terminate |
| **Worker dies** — agent process crashes or is killed externally | **Worker-loss detection** — system detects process death and reports to orchestrator | Handoff-failure-analysis.md: agent session degraded into generation loop; playbook §5.3 documents "timeout exceeded = likely stalled" — process death is a subclass of stall; NOTE: pp3g-qO5v (#410) is NOT a worker-die — process exited normally after posting comment but never wrote .kickoff-status (still 'RUNNING'). This is a finalization-contract miss (see 'Agent completes work but fails to finalize'), not a crash or kill | High | Yes — process monitoring via systemd/tmux; crosslink session status detection |
| **Relaunch claimed but didn't happen** — orchestrator believes agent was relaunched but launch failed | **Authoritative worker lifecycle** — single source of truth for worker state; launch verification required | HMS post-mortem §4: orchestrator dispatched unrequested builder to change config; playbook §4 pre-flight checklist requires "crosslink issue exists and is claimed" before dispatch | Moderate | Yes — launch verification in crosslink-guard; pre-flight checklist enforcement |
| **Engine restarts** — execution engine or orchestration layer restarts unexpectedly | **Durable state recovery** — all workflow state survives restarts; position store is authoritative | Playbook §5.8: "position store... durable store — the Crosslink hub, posted as structured comments on the working issue, surviving agent restarts" | High | Yes — durable state via crosslink hub; checkpoint contract ensures recoverable state |
| **Queue item disappears** — scheduled work item vanishes from queue without completion | **Durable scheduling** — work items persisted to durable storage; loss detection | Not directly observed in current sessions; identified as architectural requirement in workflow topology design | Emerging | Partial — crosslink issue tracking provides durability; but queue mechanics are not yet implemented |
| **Timer disappears** — scheduled timer or alarm vanishes without firing | **Durable timer** — timers persisted to durable storage; loss detection | Not directly observed in current sessions; identified as architectural requirement for execution engine | Preliminary | Partial — crosslink checkpoint contract provides some durability; but explicit timer persistence not yet implemented |
| **Agent repeats work after retry** — agent performs same work that was already completed | **Idempotency** — operations are idempotent; duplicate detection prevents re-execution | Handoff-failure-analysis.md: fresh model instance reconstructed plausible project model while lacking validation mechanisms; playbook §2.1 documents Task tool misuse causing blocking | Moderate | Yes — git-based idempotency checks; crosslink issue state tracking prevents duplicate work |
| **Agent makes partial progress** — agent completes some work but fails before finishing | **Checkpoint/recovery** — work checkpointed incrementally; recovery from last checkpoint possible | Playbook §5.4: "builders commit incrementally every ~5 minutes of work — small, resume-friendly commits, so a death loses at most one commit's worth" | High | Yes — incremental commits; crosslink checkpoint contract; worktree isolation |
| **Worktree disappears** — isolated work environment vanishes | **Environment reconstruction** — worktree state persisted; can be reconstructed from durable state | Not directly observed; worktree isolation is architectural assumption in kickoff/swarm design | Preliminary | No — worktrees are filesystem-based; reconstruction requires manual intervention |
| **Multiple workers collide** — agents attempt to modify same resources simultaneously | **Reservation/ownership** — resource locking prevents concurrent modification | Playbook §5.6: reviewer independence via isolated sub-issues; contamination incident documented where second reviewer read first reviewer's verdict | Moderate | Yes — crosslink lock system; issue-level resource ownership; worktree isolation |
| **Orchestrator loses context** — orchestrator session loses understanding of project state | **Queryable execution history** — all decisions and state changes are recorded and queryable | HMS post-mortem §3: orchestrator theorized from source code instead of reading documentation; playbook §5.7: "the orchestrator's context is the scarcest resource in the stack" | High | Partial — crosslink issue comments provide history; but context window limits are inherent to LLM architecture |
| **Agent completes work but fails to finalize** — agent performs the substantive work but cannot post result comments, write .kickoff-status, or complete handoff procedures | **Finalization permission/verification** — system verifies that post-work artifacts (result comments, status files) are written; escalation on finalization failure | 2026-08-18: all 5 auditor agents completed analysis but failed to finalize — auditor role blocks echo/file-write tools; tracked as #398 + #355; agents finish substantive work but cannot close the loop due to permission model gaps; ADDITIONAL: pp3g-Fsyf (#408 inventory completed, 39-entry across 10 repos, comment never landed — recovered by orchestrator); pp3g-gUUV (#404 verdict agent BELIEVED it posted and verified, comment was absent — recovered from pane); pp3g-qO5v (#410 — process exited after posting, .kickoff-status never written, still 'RUNNING'); pp3g-Jo2n (#404 first verification, sandbox restrictions blocked posting); pp3g-ATNS (#407 failure-matrix update, timed out at finalization, work recovered) — 6+ instances today; root cause is role-permission gap (auditor role blocks session start/comment posting), not model-specific | High (6+ instances today, role-permission root cause identified) | Partial — hook can verify finalization artifacts exist; but role-permission gaps require architectural fix |
| **Model catalog stale / whitelist blocks new models** — local model catalog (models.dev cache) lags the live API; whitelist in plugin.ts/dynamic-models.ts blocks newly-added free models | **Authoritative model catalog + whitelist sync** — plugin whitelist must sync with live model registry; stale cache must be detected and refreshed | 2026-08-18: local 'opencode models' cache showed 5 models vs Zen API's 62; whitelist in plugin.ts/dynamic-models.ts blocked hy3-free and muse-spark-1.2; tracked as Tools #4 | Moderate | Yes — cache invalidation on model list fetch; dynamic whitelist update from live catalog |
| **Free-model stall pattern** — free-tier Zen models (big-pickle, deepseek-flash-free, laguna) repeatedly stall or time out on substantial tasks while paid models (Mimo-v2.5) complete consistently | **Model-routing awareness** — system must factor model tier/capability into dispatch decisions; free-model failures should trigger routing adjustment | 2026-08-18: big-pickle, deepseek-flash-free, laguna all timed out on substantial tasks; only paid Mimo-v2.5 consistently completed; free Zen models are rate-limited with opaque limits; evidence supports tier-aware routing decisions; ADDITIONAL: big-pickle startup stall (pp3g-cCNd, #404 progress-check, 2.2% CPU, blank pane since launch, no heartbeat, killed at 17m — never produced output) | High (multiple free models stall; big-pickle adds startup-stall pattern to timeout pattern) | Partial — routing matrix already exists but not enforced; hook could auto-downgrade on stall pattern |
| **Go API key stale (auth.json vs env)** — operator rotates `OPENCODE_GO_API_KEY` in the shell but builders read `~/.local/share/opencode/auth.json` (`opencode-go.key`), so the fresh key is never consumed and builders park on the exhausted workspace | **Key-store pre-flight + sync** — before any kickoff, verify `auth.json` key prefix equals env key prefix and that `opencode.log` has no `Monthly usage limit reached` for the active workspace; one-command sync `auth.json ← env` (or re-export if DB is fresher); cheapest-test `curl …/zen/go/v1/chat/completions` streams SSE not `Monthly usage limit` | 2026-08-27 #510/#512: workspace `wrk_01KZF2ZCX2J3H5S248MFCWH3CE` monthly-limit at 13:06:52 parked two durable builders on #510 (`AI_APICallError: Monthly usage limit reached. Resets in 11 days…` + `AI_RetryError: Failed after 3 attempts…` + `retry nextDelay=982…000`); env held a fresh key at 1.9% but `auth.json` still held the exhausted predecessor for `wrk_01KZF…`; fixed 13:38 by updating `auth.json` to `sk-yvUg9…` (now streams SSE); verified 15:33 `ses_fbc24c189ffeH3um1r564nlFAW` (`opencode-go/muse-spark-1.2-contributor`) streams with zero monthly-limit errors and direct `curl` SSE succeeds | High (parked fleet; reproduced via direct API call; fix verified live) | Yes — pre-kickoff hook: compare `auth.json` vs env key prefix, grep `opencode.log` for `Monthly usage limit.*wrk_01KZF`, refuse launch on mismatch or recent park; sync command in `model-discipline.md` |

| **ChatGPT MCP package accepted as live connection / fix-first authentication drift** — Projektor plugin package existed, tools absent; debugging initially changed Cloudflare before checking client MCP registration; a separate Access app introduced a mismatched JWT audience | **Separate package, registration, auth, discovery, execution, and side-effect acceptance; cheapest client-visible discriminating test; verify existing auth audience before changes** | EDASES-MCP-PROJEKTOR-2026-11-06: package-only vs connected-app paired control, exact unauthorized HTTP 401 metadata, audience comparison, registration in the **same ChatGPT conversation**, five-project read and ASES-4 comment with independent activity verification. Single-incident observational evidence; no replicated controlled benchmark. [Case](../Projektor%20MCP%20Registration%20Failure%20Case%202026-11-06.md) | Preliminary (single case, live acceptance) | Partial — project-local MCP registration/release gate and status reporting; platform-owned connection step may require user consent |

---

## Evidence Sources

### Primary Evidence (Today's Incidents)

1. **HMS Research Session Post-Mortem (#519)** — documented pathological monitoring loops, role-boundary breaches, over-conclusion from transient errors, and unapproved configuration changes. Key failure classes: agent infinite loop, orchestrator loses context, relaunch claimed but didn't happen.

2. **#506 Regression-Stall Report** — agent stalled without progress detection. Key failure classes: agent exceeds expected duration, worker dies.

3. **#522 Doc-Navigation Probe** — agent failed to navigate documentation correctly. Key failure classes: agent makes partial progress, orchestrator loses context.

4. **Multiple Agent Timeouts** — agents exceeding task-matched timeouts across sessions. Key failure classes: agent exceeds expected duration, agent infinite loop.

5. **2026-08-18 Session (issue #407)** — comprehensive failure observation session. Pre-positioned auditor (pp3g-tU4X) looped on denied 'rtk git status --short'; #506 regression agents looped; ~10+ agents timed out across models (big-pickle, deepseek-flash-free, laguna); only paid Mimo-v2.5 consistently completed; all 5 auditor agents hit finalization gap (#398/#355); model catalog staleness blocked new free models (Tools #4); disk hit 100% causing crashes. Key failure classes: agent infinite loop, agent exceeds expected duration, agent completes work but fails to finalize, model catalog stale, free-model stall pattern, disk-pressure crashes. **Post-407 pass**: added 6+ finalization instances (pp3g-Fsyf, pp3g-gUUV, pp3g-qO5v, pp3g-Jo2n, pp3g-ATNS — role-permission root cause, not model-specific); big-pickle startup stall (pp3g-cCNd, 2.2% CPU, no heartbeat, killed at 17m); qO5v/ATNS timeout evidence.

### Secondary Evidence (Historical)

5. **Handoff Failure Analysis** — fresh model instance reconstructed plausible project model while lacking validation mechanisms; session degraded into generation loop. Key failure classes: orchestrator loses context, agent infinite loop, agent repeats work after retry.

6. **Playbook Documentation** — §5.3 task-matched timeouts, §5.4 checkpoint contract, §5.6 reviewer independence, §5.8 workflow topology. Provides architectural requirements for preventing multiple failure classes.

7. **Historical Claude Code Project Documentation** — `docs/historical/` and `docs/methodology/` contain process knowledge from earlier project phases. Key patterns: role-boundary breaches, autonomous fallback behaviors, context corruption.

---

### 2026-11-06 Projektor MCP registration recovery (single-case evidence)

- [EDASES-MCP-PROJEKTOR-2026-11-06](../Projektor%20MCP%20Registration%20Failure%20Case%202026-11-06.md) — a real ChatGPT MCP connector was missing from tool inventory despite valid plugin packaging. Separating ChatGPT registration/scanning from OAuth/Worker health exposed the missing boundary; a new Cloudflare Access application also introduced a distinct JWT audience and was reverted. Actual registration/authentication made tools visible in the existing conversation and passed read, bounded write and independent activity verification. Evidence class: single-project direct observation; comparative speed reported by operator, not benchmarked. Adoption is **only** into the project-owned `ases-plugins` workflow so far, not a global methodology change.

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
9. **Model catalog stale / whitelist blocks new models** — cache invalidation on model list fetch; dynamic whitelist update from live catalog
10. **Agent completes work but fails to finalize** — hook can verify finalization artifacts exist; but role-permission gaps require architectural fix
11. **Free-model stall pattern** — routing matrix already exists but not enforced; hook could auto-downgrade on stall pattern

### High Priority (Go key cold path)

12. **Go API key stale (auth.json vs env)** — pre-kickoff key-store check + log grep + one-command sync; cheapest-test `curl` SSE before dispatch

### Lower Priority (Emerging/Preliminary/Single-Observation Confidence)

13. **Queue item disappears** — crosslink issue tracking provides some durability
14. **Timer disappears** — crosslink checkpoint contract provides some durability
15. **Agent legitimately exceeds duration** — requires human judgment
16. **Worktree disappears** — requires manual intervention
17. **Orchestrator loses context** — inherent LLM limitation; partial mitigation via history
18. **Disk-pressure environmental crashes** — disk monitoring can alert; but cleanup is manual and project-specific

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
| 2026-08-18 | Post-407 evidence pass: added 6+ finalization-gap instances (pp3g-Fsyf, pp3g-gUUV, pp3g-qO5v, pp3g-Jo2n, pp3g-ATNS, pp3g-cCNd context), big-pickle startup stall (pp3g-cCNd), qO5v/ATNS timeout evidence, Worker-die subclass note (qO5v is finalization-miss not crash) | pp3g-w8pi builder agent |
| 2026-08-27 | Added Go API key stale row: `wrk_01KZF2ZCX2J3H5S248MFCWH3CE` monthly-limit park 13:06:52, `auth.json` vs env divergence, one-command sync, log signatures, verification via live `muse-spark` session + `curl` SSE | auth-verify builder (#512) |

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
