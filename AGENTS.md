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

# Goal

The objective is not to maximise document production.

The objective is to improve the reliability, traceability and correctness of AI-assisted software engineering through disciplined research, methodology and implementation.