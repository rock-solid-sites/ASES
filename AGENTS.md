---
title: Agent Operational Rules
program: EDASES
layer: Research
document_type: Standard
status: Active
authority: Canonical
canonical_repository: edases
supersedes: AGENTS.md (previous version)
---
# AGENTS

This document defines the operational rules for AI agents contributing to the EDASES ecosystem.

Its purpose is to ensure that AI contributions remain consistent with the project's research, methodology and implementation goals.

This document complements `ORIENTATION.md`.

Agents should read both documents before making significant repository changes.

---

# Core Principles

When working within this repository, agents should recognise the distinction between the three project layers.

* **EDASES** develops research.
* **ASES** defines methodology.
* **The Execution Engine** implements methodology.

Agents should avoid introducing concepts from lower abstraction layers into higher abstraction layers.

---

# Canonical Documents

Canonical documents are the authoritative source of project knowledge.

When conflicts arise:

1. Prefer canonical documents.
2. Prefer higher abstraction layers.
3. Prefer explicit evidence over inference.
4. Ask for clarification rather than inventing missing methodology.

Agents should not redefine canonical concepts without explicit human direction.

---

# Abstraction Boundaries

Before modifying a document, determine its abstraction layer.

Research should not depend upon implementation.

Methodology should derive from research.

Implementation should derive from methodology.

If uncertainty exists, move upward through the abstraction hierarchy rather than introducing implementation assumptions.

---

# Reasoning Before Artefacts

The primary object of interest is engineering reasoning.

Source code, documentation and commits are outputs of reasoning rather than the primary artefacts themselves.

Agents should preserve:

* observations
* assumptions
* findings
* decisions
* challenges
* validations

Where practical, reasoning should remain explicit.

---

# Evidence

Agents should distinguish clearly between:

* observations
* interpretations
* findings
* recommendations

Evidence should not be presented as methodology.

Methodology should not be presented as implementation.

---

# Reasoning Certainty

Claims that cross a role boundary — a producer emitting a claim that a
consumer will act on — must state:

* **WHY** — the reasoning behind the claim;
* **WHAT** — the claim's basis (what it is based on);
* **HOW CERTAIN** — the certainty level (guess / evidence-based / proven);
* **WHAT-NOT-TESTED** — what was explicitly not tested.

The WHAT-NOT-TESTED clause is the sharpest element: negative-space disclosure
targets the cheapest class of false-confidence failure. A claim that states
its untested assumptions is checkable by a thin consumer; a claim that hides
them is not.

---

# Cheapest-Test-First

Assumptions that gate decisions must be tested with the quickest cheapest
**discriminating** test — the test that can falsify the core premise, run
before the expensive work is committed. The obligation sits with the
producer (the side that can verify cheaply); the consumer-side check is a
presence/structure audit, not a re-run.

---

# Workflow Topology

The full workflow-topology design — the two principles above, the
information-asymmetry boundary finding, position-emitting agents, the
durable store, the cheap staleness trigger, the AUDITOR as a one-role /
two-phase in-flight divergence verifier, and the reviewer as a
pre-consumption readiness audit — is recorded at
`docs/research/Workflow Topology Design and Reasoning Record.md`.

The operational procedure derived from that design is in
`docs/ORCHESTRATOR.md`; the dispatch-level mechanics are in
`.crosslink/knowledge/agent-orchestration-playbook.md` (§5.8).

---

# Multi-Agent Work

Independent reasoning is preferred where independent judgement is required.

Agents should avoid being influenced by previous conclusions before completing their own analysis unless the task explicitly requires synthesis.

Constructive disagreement is valuable.

Consensus should emerge through evidence rather than repetition.

---

# Zero-Context Sessions

When the user explicitly requests a fresh, isolated or clean-room review, the integrity of that isolation takes precedence.

If an isolated execution cannot be performed:

* report the failure
* explain why it occurred
* wait for further instruction

Do not silently substitute the current conversational context.

---

# Tool Independence

Methodology should remain independent of implementation tooling.

Agents should avoid introducing assumptions tied to specific:

* AI providers
* APIs
* programming languages
* databases
* frameworks

Implementation proposals belong in implementation documents.

---

# Model Discipline

Model names must be verified before use. Never assume a model ID.

* Run `opencode models <provider>` before using any model in a command or configuration.
* Copy model IDs exactly — do not guess, shorten, or modify them.
* Ask the operator which provider to use. Do not choose on your own.
* Do not use free-tier (Zen) models for kickoff or swarm agents — rate limits will cause failures.
* The `opencode-go/` prefix indicates paid models. Free models have different, provider-specific prefixes.
* The mandatory model list for this project is documented at `.crosslink/knowledge/model-discipline.md`.

**Operator override (2026-08-23):** free-tier models are permitted within swarms under auditor supervision; hy3-class serves as primary reviewer; luna is reserved for complex phases; peer-review between agents is permitted.

---

# Repository Changes

Before introducing new documents:

* determine whether an existing canonical document already covers the concept
* avoid duplication
* maintain explicit dependency relationships
* update documentation where conceptual changes occur

Repository organisation should reflect conceptual organisation.

---

# Adversarial Review

Adversarial findings are research outputs.

They do not become project direction automatically.

Agents should:

* preserve findings accurately
* distinguish evidence from recommendation
* avoid treating consensus as authority
* defer strategic decisions to the human orchestrator

---

# Failure Handling

If required tools fail:

* report the failure accurately
* preserve intermediate work where possible
* request further instruction

Do not substitute fundamentally different execution strategies without explicit approval.

---

# Continuous Improvement

If repository work reveals missing concepts, inconsistent terminology or structural gaps:

* identify the issue
* explain the reasoning
* propose an improvement

Do not silently redefine project concepts.

---

# Research Programme

The execution-engine UI research programme has completed its first cycle.

The synthesis is at `research/execution-engine-ui/synthesis/execution-engine-ui-synthesis.md`.

Key findings for agents working on the execution engine:

* Property graph databases naturally represent artefacts, versions, evidence, provenance, and supersession (High confidence).
* XState v5 can model independent artefact lifecycles with full hierarchy, persistence, and inspection (High confidence).
* Existing graph UI libraries can render engineering artefacts with low-to-moderate customization (Medium-High confidence).
* Explicit provenance is the novel contribution — no existing methodology provides it (Medium-High confidence).
* The central architectural tension is lifecycle-ownership: execution engines claim state that EDASES reserves for statecharts.
* The reversed composition (statechart owns lifecycle, engine only schedules) is unevidenced.

Open items are tracked as Crosslink issues #14–#21.

Agents should read the synthesis before making implementation decisions that affect the execution engine.

---

# Working With the Operator

The operator is not a programmer and does not assess shell commands.

## Execution Boundary (Doctrine, issue #462 — binding)

* **[D1]** Any action executable in a shell, a config file, an admin UI, or over SSH is **agent work by default**. The orchestrator delegates it; the operator never performs it. The operator never runs shell commands, admin consoles, SSH sessions, or vendor consoles (cloud dashboards, OAuth wizards, rclone-style config menus).
* **[D2]** The operator surface is exactly: decisions, priorities, approvals, reviewing results, and — where a task irreducibly requires a human identity action (e.g. clicking a Google consent button) — that ONE action, presented as a single step.
* **[D3]** If a task in flight discovers it needs more than one such operator action, the workflow is WRONG: stop, re-plan for agent delegation, and re-present. Never escalate operator involvement to compensate for delegation failure.
* **[D4]** Multi-step terminal sequences, menu navigation, port flags, and config-file editing are never given to the operator, even as copy-paste blocks.

Raw pasted output blocks are the expected response format; parsing them is the agent's job. Explain significance in plain language. Never delegate command-safety assessment to the operator.

Where an irreducible operator action exists (e.g. a `git push` that triggers deploys, or a consent click), present it as ONE single step — nothing more.

## Secrets Handling

Agents NEVER ask the operator for codes, keys, tokens, or any secret inside the conversation. The operator-preferred pattern: the operator copies the secret into a shell command or file ON THE MACHINE themselves (so it is available to agents at runtime) without it entering chat context; agents are told only WHERE to find it (a path or variable name), never its value. Dispatch specs must name a secret-placement location (e.g. a file under `/tmp/opencode/secrets/` or an env var set by the operator) whenever external credentials are involved.

## Startup Verification

No agent launch may be reported as healthy at t=0. Mandatory sequence for every launch:

1. launch;
2. sleep 30 seconds;
3. check the opencode.log tail for the session — creation line present, no `AI_APICallError` / retry-after / consent-gate signature, tracking heartbeats advancing — AND check `.kickoff-status`;
4. only then report status.

Evidence from the 2026-08-24 forensics shows agent death signatures appear in opencode.log within seconds of launch (consent-gate fatal ~6s; rate-limit parking within one cycle). Seconds-scale log evidence is therefore authoritative for launch-window checks; staleness thresholds referencing 45–90 minute budgets are SUPERSEDED for this purpose (interim procedure until Observer F2 fast-path is live).

---

Agents proactively propose git push moments: after merge clusters, before cleanup or migration operations, and at session end.

When building automation or repair work, consult: AI Orchestration Guide (coordination principles), Methodology to Requirements Mapping Specification (preservation requirements), Execution Engine Vision (long-term direction), Documentation Standard (any new document), Canonical Terminology and Concept: Levels of Abstraction (naming and layering).

---

# Goal

The objective is not to maximise document production.

The objective is to improve the reliability, traceability and correctness of AI-assisted software engineering through disciplined research, methodology and implementation.