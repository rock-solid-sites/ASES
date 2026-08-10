---
title: AI Orchestration Guide
program: ASES
layer: Methodology
document_type: Methodology Specification
status: Active
authority: Canonical
canonical_repository: ases
# Mirror/placeholder: this document is canonical to the ASES repository (ases);
# it is filed here in edases as a mirror until the ases repository is established.

depends_on:
  - Concept: Levels of Abstraction
  - AI Capability Registry

consumed_by:
  - Methodology to Requirements Mapping Specification
  - Execution Engine Vision

related_documents:
  - Evaluation Framework

supersedes: []
last_updated: 2026-08-10
---

# AI Orchestration Guide

## Status

**Methodology Specification**

This document defines the principles by which ASES coordinates AI systems, supporting tools and human participants during software engineering.

Unlike the AI Capability Registry, this document is normative rather than descriptive. It defines recommended orchestration practices based upon the current body of evidence produced by EDASES.

---

# Purpose

No individual AI system is expected to excel at every software engineering task.

ASES therefore treats software engineering as a process of orchestrating specialised capabilities rather than relying upon a single general-purpose system.

The purpose of orchestration is to maximise software quality while minimising cost, time and opportunities for human or AI error.

---

# Scope

This document defines:

- orchestration principles
- role assignment
- collaboration patterns
- review structures
- escalation strategies
- validation responsibilities

Specific implementation mechanisms are outside the scope of this document.

---

# Guiding Principles

## Capability-Driven Assignment

Tasks should be assigned according to demonstrated capability rather than model popularity or availability.

Assignments should be supported by evidence recorded within the AI Capability Registry.

---

## Specialisation

Systems should perform the tasks for which they are best suited.

General-purpose use should be considered a fallback rather than the default.

---

## Independent Reasoning

Where independent judgement is required, participating systems should reason independently before viewing the conclusions of others.

Independent reasoning reduces confirmation bias and increases the probability of discovering hidden assumptions.

---

## Constructive Adversarial Review

Review exists to improve engineering outcomes rather than defend previous work.

Challenge should focus on assumptions, evidence and reasoning rather than individuals or systems.

---

## Human Accountability

Responsibility for engineering decisions remains with human participants.

AI systems assist decision-making but do not replace engineering accountability.

---

## Mechanical Verification

Where methodology can be enforced automatically, automation should replace procedural compliance.

Automation should reduce opportunities for predictable error rather than simply reducing effort.

---

# Orchestration Roles

ASES recognises functional roles rather than specific products.

Any capability may fulfil a role provided sufficient evidence exists.

Examples include:

- Requirements Analyst
- Domain Researcher
- Architect
- Planner
- Implementation Specialist
- Reviewer
- Adversarial Reviewer
- Synthesiser
- Validator
- Test Designer
- Documentation Specialist

Multiple capabilities may fulfil the same role.

A single capability may fulfil multiple roles where appropriate.

---

# Human Roles

Humans provide responsibilities that cannot currently be delegated.

These include:

- defining project objectives
- evaluating trade-offs
- accepting engineering risk
- approving methodology changes
- validating research findings
- determining project priorities

ASES augments rather than replaces human judgement.

---

# Core Orchestration Pattern

Most engineering activities should follow a structured progression.

```text
Objective
      ↓
Analysis
      ↓
Generation
      ↓
Independent Review
      ↓
Adversarial Review
      ↓
Synthesis
      ↓
Validation
      ↓
Approval
```

The specific capabilities assigned to each stage depend upon the evidence contained within the AI Capability Registry.

---

# Independent Generation

Where practical, important artefacts should be produced independently before comparison.

Examples include:

- architectural proposals
- implementation strategies
- threat models
- review findings

Independent generation reduces convergence upon shared errors.

---

# Comparative Synthesis

When multiple independent outputs exist:

- identify areas of agreement
- identify areas of disagreement
- investigate unsupported conclusions
- preserve minority viewpoints until resolved

Consensus should emerge through evidence rather than voting.

---

# Adversarial Review

Adversarial review is intended to discover weaknesses before implementation progresses.

Typical review objectives include:

- unsupported assumptions
- hidden dependencies
- architectural inconsistencies
- incomplete reasoning
- specification ambiguity
- unnecessary complexity

Successful adversarial review strengthens rather than delays progress.

---

# Validation

Validation confirms that artefacts satisfy methodological requirements.

Validation should determine:

- evidence completeness
- reasoning traceability
- methodological compliance
- readiness for promotion

Validation differs from review.

Review discovers issues.

Validation determines readiness.

---

# Escalation

When disagreement cannot be resolved:

1. seek additional evidence
2. obtain independent analysis
3. broaden capability diversity
4. involve human review
5. record unresolved uncertainty where necessary

Escalation should increase confidence rather than authority.

---

# Capability Selection

Capability selection should consider:

- demonstrated strengths
- known weaknesses
- failure modes
- context requirements
- cost
- latency
- availability
- interoperability

Selection should remain evidence-based.

---

# Context Management

Capabilities should receive only the information necessary for their assigned task.

Excess context increases cost and may reduce reasoning quality.

Context should therefore be:

- relevant
- sufficient
- traceable
- recoverable

---

# Evidence Preservation

Every significant engineering decision should preserve:

- supporting observations
- findings
- assumptions
- challenges
- validation
- rationale

Evidence preservation enables future review, learning and methodology improvement.

---

# Workflow Evolution

Orchestration patterns are expected to evolve.

Changes should be supported by:

- experimental evidence
- repeated successful application
- measurable improvement

Patterns should not become fixed tradition.

---

# Relationship to Other Documents

The AI Evaluation Protocol defines how capability evidence is generated.

The AI Capability Registry records the resulting observations.

This document translates that evidence into methodological guidance.

The Methodology-to-Requirements Mapping derives implementation requirements from the orchestration principles defined here.

Execution Engine implementations are responsible for enforcing and supporting these orchestration patterns.