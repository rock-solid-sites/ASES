---
title: ASES Repository Agent Entry Adapter
version: 1.0.2
program: ASES
layer: Methodology
document_type: Guide
status: Active
authority: Derived
canonical_repository: ases
depends_on:
  - docs/methodology/ASES Task-Scoped Information and Handoff Method.md
  - docs/standards/Documentation Standard.md
related_documents:
  - skills/current/README.md
  - docs/methodology/AI Orchestration Guide.md
last_updated: 2026-11-24
---

# ASES repository agent entry adapter

**This file is a compatibility entrypoint for agent harnesses that automatically load root `AGENTS.md`, not a required ASES startup ritual or a second canonical policy.** The [canonical task-scoped information method](docs/methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md) defines how task context is selected. Current specialized instructions are retrieved selectively from the [ASES current skills index](skills/current/README.md) over read-only HTTPS in ChatGPT; other harnesses must verify their actual load mechanisms. Do not load every skill for every task.

For general evidence-based reasoning and role boundaries, see the [AI Orchestration Guide](docs/methodology/AI%20Orchestration%20Guide.md) only as relevant. For each task, identify its actual objective, current source owner/revision, applicable operator/project rules, needed evidence and completion criteria. Distinguish verified source facts from experimental research and stale working notes. Where sources conflict, record the unresolved choice rather than using last-read-wins. A project-approved complete override excludes replaced rule content from the effective task view while retaining provenance.

**Execution boundary:** Obtain task-specific authority before destructive changes, production deployment, secret access or paid model use. Previously granted approval applies only within its stated scope. Agent workers may carry out authorized repository edits, tests and normal branch checkpoints without requiring the operator to execute shell commands. Avoid presenting multi-step shell/admin work to the operator; human identity/consent actions may remain necessary. Ask for genuine strategy/permission decisions, not routine execution.

**Model and billing:** Use [current agent-launch instructions](skills/current/agent-launch/SKILL.md) to select the exact approved provider, model ID, account, endpoint and funding route. Subscription allowances, purchased API credits, promotional/free credits and free model tiers are distinct. No silent provider/model substitution, auto-overage or paid fallback. The receiving agent does not select its own execution model. ChatGPT Plus/Codex Luna and independent Phoenix Grove routes retain their separately defined authorizations.

**Secrets and privacy:** Never request or publish secret values in a task packet, log or public document; use approved secret stores/credentials and verify access at the actual host. Do not put private project or chat source bodies in public ASES derived views.

**Evidence and handoff:** For retained work, apply the [destination-first execution and recovery section](docs/methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md#destination-first-execution-and-recovery); distinguish disposable branches, verified remote checkpoints during work, and final artifact delivery. Perform the cheapest meaningful falsifying checks before claiming completion. Preserve remote source commits/PRs, observed tests, what was not tested, blockers and current work position in Git and the existing agent Work Notes issue. Projektor records human planning/architectural decisions. Do not invent a session-end file or an always-running monitoring service.

**Retired routes are not current:** The previous root instructions contained Crosslink/VPS kickoff and monitoring, dated model routes and environment-specific claims. They must **not** be executed or cited as current requirements. For historical provenance only, see [the previous revision](https://github.com/rock-solid-sites/ASES/blob/2235d237044d6cb850f827d65baadd1fe3da5b34/AGENTS.md). ASES now uses task-scoped information selection; an agent should stop if the relevant current method or authorized route cannot be verified. The retired repository-local harness bundle is preserved in [the historical harness record](docs/historical/Harness%20Setup%20and%20Permission%20Design%20History.md), not as a runnable default. Archiving it does not grant permissions to a replacement launcher; verify confinement separately.
