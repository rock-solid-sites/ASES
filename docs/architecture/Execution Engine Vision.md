---
title: Execution Engine Vision
program: Tooling
layer: Architecture
document_type: Architecture Vision
status: Active
authority: Canonical
canonical_repository: ases-engine
# Mirror/placeholder: this document is canonical to the ases-engine repository;
# it is filed here in edases as a mirror until the ases-engine repository is established.

depends_on:
  - Concept: Levels of Abstraction
  - AI Orchestration Guide
  - Methodology to Requirements Mapping Specification

related_documents:
  - AI Capability Registry
  - Evaluation Framework

supersedes: []
last_updated: 2026-08-10
---

# Execution Engine Vision

## Purpose

This document describes the architectural vision for the software system responsible for executing the ASES methodology.

It defines what the execution engine is intended to achieve rather than how individual implementation decisions should be realised.

Specific technologies, programming languages and implementation details remain outside the scope of this document.

---

# Vision

ASES should eventually be executable rather than procedural.

Instead of relying upon users to remember methodological rules, the execution engine should understand the methodology, manage engineering state and mechanically enforce methodological correctness wherever practical.

The engine exists to reduce cognitive burden while increasing consistency, traceability and engineering quality.

---

# Objectives

The execution engine should:

- execute the ASES methodology
- minimise predictable human error
- minimise predictable AI error
- coordinate heterogeneous AI capabilities
- preserve engineering reasoning
- maintain methodological state
- reduce unnecessary token consumption
- improve engineering throughput
- remain independent of individual AI providers

---

# Core Principle

The execution engine is not a software development environment.

It is a methodology execution system.

Its purpose is to coordinate software engineering rather than perform software engineering itself.

---

# Responsibilities

The execution engine is responsible for:

- maintaining methodological state
- coordinating workflows
- enforcing methodology
- preserving epistemic relationships
- recording engineering evidence
- orchestrating AI capabilities
- supporting human oversight
- validating workflow progression

It is not responsible for determining software architecture or writing software autonomously.

---

# The Object of Management

Traditional development systems primarily manage files, commits or tasks.

The execution engine manages reasoning.

Engineering artefacts remain important, but they derive their meaning from the reasoning that produced them.

Consequently, the execution engine should treat relationships between observations, assumptions, findings, decisions, challenges and validations as first-class entities.

---

# Methodology Execution

The execution engine should understand the current methodological state of every engineering activity.

Examples include:

- awaiting review
- awaiting validation
- blocked by missing evidence
- conflicting findings
- promotion ready

Users should not be required to infer methodological state manually.

---

# Mechanical Enforcement

Methodological rules should be enforced automatically wherever practical.

Examples include:

- preventing unsupported promotion
- detecting incomplete reviews
- identifying missing evidence
- preventing invalid state transitions
- detecting unresolved conflicts
- identifying orphaned reasoning

Mechanical enforcement should replace procedural discipline whenever possible.

---

# Knowledge Model

The execution engine should maintain explicit relationships between engineering concepts.

Examples include:

- observation supports finding
- finding challenges assumption
- decision depends upon evidence
- validation approves promotion
- requirement derives from methodology

Knowledge should remain queryable throughout the project lifecycle.

---

# Orchestration

The execution engine should coordinate heterogeneous capabilities.

Responsibilities include:

- selecting appropriate capabilities
- assigning functional roles
- coordinating independent reasoning
- managing review workflows
- recording collaboration
- supporting escalation

Capability selection should remain evidence-driven through integration with the AI Capability Registry.

---

# Human Interaction

The execution engine exists to augment human decision-making.

Humans remain responsible for:

- defining objectives
- accepting engineering risk
- resolving ambiguity
- approving significant decisions
- evolving the methodology

Automation should increase capability rather than reduce human understanding.

---

# Context Management

Context should become an explicit resource managed by the execution engine.

Responsibilities may include:

- constructing task-specific context
- recovering previous reasoning
- minimising redundant context
- preserving long-term knowledge
- reducing unnecessary token usage

Context management should support both efficiency and reasoning quality.

---

# State Management

The execution engine should maintain a complete representation of project state.

State should be:

- explicit
- recoverable
- auditable
- consistent
- methodology-aware

Projects should resume from state rather than reconstructed conversation history.

---

# Validation

Validation should become a continuous activity.

The execution engine should continuously evaluate:

- methodological compliance
- missing evidence
- unresolved assumptions
- incomplete reviews
- conflicting conclusions
- promotion readiness

Validation should occur throughout engineering rather than only at project completion.

---

# Extensibility

The execution engine should support:

- multiple AI providers
- evolving methodologies
- additional capability types
- new orchestration strategies
- future research findings

Methodological evolution should require minimal architectural change.

---

# Architecture Principles

The implementation architecture should favour:

- explicit state
- composable services
- traceable reasoning
- deterministic workflows
- modular capability integration
- implementation independence

Architectural decisions should support methodology rather than constrain it.

---

# Relationship to EDASES

EDASES investigates improved approaches to AI-assisted software engineering.

Validated findings produced by EDASES inform revisions to ASES.

Those revisions become executable through the execution engine.

The execution engine therefore operationalises current methodological knowledge while remaining capable of evolving alongside future research.

---

# Relationship to ASES

ASES defines how software engineering should proceed.

The execution engine provides the mechanisms through which those methodological rules are executed, enforced and supported.

It is an implementation of the methodology rather than an extension of it.

---

# Long-Term Vision

As EDASES matures, increasing portions of ASES should become mechanically executable.

Ultimately, the execution engine should function as a methodology operating system that:

- understands engineering state
- coordinates specialised capabilities
- preserves engineering knowledge
- enforces methodological correctness
- supports continuous research
- improves through evidence

The methodology remains the source of truth.

The execution engine provides its execution.