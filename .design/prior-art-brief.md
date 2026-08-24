---
title: Prior Art Brief - EPIC 423 Support Systems
program: EDASES
layer: Implementation
document_type: Research Brief
status: Active
authority: Derived
parent_epic: "#423"
purpose: Operator-conducted external prior-art scan; agents must not duplicate this research via webfetch
---

# Purpose

We run fleets of LLM agents (builders, reviewers, auditors) dispatched from a coordination CLI. On 2026-08-23 five froze silently across four distinct causes. We are building the support system so none of this needs a human noticing. Hard constraints: zero budget; consumers are agents, so outputs must be machine-readable first; one Linux server; every mechanism must survive the question - what if the monitor itself dies?

This brief exists so the OPERATOR can check existing tools before we build, avoiding agent webfetch bursts entirely.

# Component 1 - Semantic liveness detection (the core problem)

Know within one minute whether a long-running agent is healthy, rate-limit-parked with a resume time, stream-dead, or stuck in a repetition spiral - and auto-kill only the spiral case.

Classic supervisors (systemd, monit, pm2) detect process exit. Our failures are processes alive but uselessly waiting - liveness is semantic, signaled only in a shared log file (AI_APICallError lines versus bare silence versus repeated phrases).

Check: log-tail alerting (Loki/Promtail, Vector); LLM-agent observability platforms (LangSmith, Langfuse, AgentOps, Arize Phoenix, OpenTelemetry GenAI conventions) - do any do runtime stall or parking detection rather than post-hoc tracing?

Research question: does any agent framework expose agent-is-quota-parked-resumes-at-T as a first-class state?

# Component 2 - Continuous event-driven ingestion

Replace polling with tail -F on the shared opencode log, attributing lines to agents, feeding a classifier. Check how existing shippers handle rotation plus multi-writer attribution within a single-box stdlib-python constraint.

# Component 3 - Repetition-spiral auto-kill

Detect same-phrase-repeating output streams and terminate within roughly 90 seconds without killing legitimately verbose tasks. Check LLM-framework max-iteration and recursion-limit guards (LangGraph/LangChain) for sophistication level.

# Component 4 - Persistent status panel with lifecycle gates

Side-pane table of every agent (role, model, state, age) updating itself; rows clear only through defined gates (merge clears green rows; frozen rows pin until human decides); click-to-intervene later. Check OpenCode 2 plugin UI capabilities and dashboards-for-agent-fleets prior art.

# Component 5 - Dispatch declarations and plan linter

Every dispatch declares estimate duration, planned units, model provenance; a linter validates plans pre-launch (commit cadence achievable, dependencies exist, atomization granularity sane). Tonight's collator died because its inputs lived on unmerged branches - exactly what a dependency check catches. Check CI-pipeline linting and Terraform-plan validate-before-apply patterns.

# Component 6 - Human transition gates as popups

Git push and risky launches render a native yes/no prompt with context instead of hard-block or free-run. Check opencode permission ask action, GitHub Environment approvals, LangGraph interrupts.

# Component 7 - Session archive and wind-down protocol

Weekly export of session transcripts to compressed JSONL plus index; off-box sync via rclone to an unpinned provider; destination-side read-back verification; only then prune server copies. Check backup ecosystems with automated restore verification (restic, borg communities) and anything exporting LLM session histories to durable readable formats.

# Cross-cutting research questions

1. Has anyone built LLM-session-aware supervision rather than process supervision? Our exact niche may be empty.
2. Prior art for machine-consumable status surfaces - dashboards designed for agent readers with token budgets?
3. Has any retry-library or framework surfaced parked-versus-dead as a monitoring concern?
4. Does the MAST/AdaMAST/ATLAS corpus taxonomize silent-freeze detection already?

Note: component evidence base is the 2026-08-23 incident set documented on issues #417, #419, #423, #429 and the forensics result comments thereon.
