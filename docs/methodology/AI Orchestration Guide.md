---
title: AI Orchestration Guide
version: 2026-11-24.1
program: ASES
layer: Methodology
document_type: Methodology Specification
status: Active
authority: Canonical
canonical_repository: ases

depends_on:
  - Concept: Levels of Abstraction
  - AI Capability Registry

consumed_by:
  - Methodology to Requirements Mapping Specification
  - Execution Engine Vision

related_documents:
  - Evaluation Framework
  - docs/methodology/ASES Task-Scoped Information and Handoff Method.md
  - docs/historical/Harness Setup and Permission Design History.md

supersedes: []
last_updated: 2026-11-24
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

Specific implementation mechanisms are outside the scope of this document. This is the current general orchestration methodology, not a harness configuration or universal startup prompt. For task preparation and operational routing, use the [task-scoped handoff method](ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md) and select only applicable [current skills](../../skills/current/README.md).

## Current reasoning principles

The earlier EDASES core prompt iterations are consolidated here as methodological principles, not instructions that must be injected into every session. Distinguish observation, inference, hypothesis and unknown. Prefer measured, verified outcomes to plausible explanations; state confidence limits, missing evidence and plausible alternative explanations. Test important assumptions with the cheapest meaningful falsifier. Evaluate proposals against risks, dependencies, trade-offs and operational implications; do not defend a particular tool, technology, model or method by default. Explain material reasoning clearly to technical and nontechnical participants. Learn from successful and failed work, including recurring operator corrections; retain the evidence and rationale for later reuse.

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

Automation should reduce opportunities for predictable error rather than simply reducing effort. Verify permissions at the actual effect boundary, including indirect shell, filesystem and connector paths. A prompt convention, model-picker label, or accumulation of guards is not proof of containment; distinguish accidental-error prevention from protection against an adversarial agent. In particular, read-only review means no mutation of the target under review, not an inability to preserve a verdict through a separately authorized durable reporting channel. Select controls for the actual host and role; test denied effects and necessary allowed effects. Do not infer present enforcement from a historical harness configuration.

**Rationale:** Earlier OpenCode/Crosslink experiments exposed write-path bypasses, conflicting allowlists, drift across configuration layers, reviewer relay bottlenecks, and repeated instruction violations. Those results justify verifying actual boundaries, not reviving the obsolete guards. See the [historical harness decision and evidence guide](../historical/Harness%20Setup%20and%20Permission%20Design%20History.md) for source snapshots, review disagreements, rejected approaches and limits.

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

The following progression illustrates separable engineering functions; it is not a mandatory pipeline. Choose the smallest relevant evidence-to-decision loop, repeat stages when evidence requires it, and omit stages that add no value for a bounded task.

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

Evidence preservation enables future review, learning and methodology improvement. Official current documents state the selected rule or decision, its concise rationale and the evidence limits; historical records retain the fuller reasoning, alternatives rejected by discussion or tests, source revisions and results. Do not treat those earlier alternatives as governing instructions. Follow the task-scoped method for final artifact homes and verified remote checkpoints.

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