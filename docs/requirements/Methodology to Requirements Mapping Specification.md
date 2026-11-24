---
title: Methodology to Requirements Mapping Specification
version: 2026-11-24.1
program: ASES
layer: Requirements
document_type: Requirements Specification
status: Active
authority: Canonical
canonical_repository: ases

depends_on:
  - Concept: Levels of Abstraction
  - AI Orchestration Guide

consumed_by:
  - Execution Engine Vision

related_documents:
  - Evaluation Framework

supersedes: []
last_updated: 2026-11-24
---

# Methodology → Requirements Mapping

## Purpose

This document defines how the ASES methodology is translated into software requirements.

ASES specifies *what* should occur during software engineering.

Implementations determine *how* those behaviours are realised.

This document forms the high-level requirements boundary between the methodology and its implementations. It is not the complete Kernel specification, a frozen build packet or proof of a deployed engine. The applicable current requirements come from the methodology and explicit accepted decisions, not from old implementation proposals.

---

# Scope

This document derives implementation requirements from validated methodological principles.

It does not prescribe:

- implementation technologies
- software architecture
- programming languages
- storage mechanisms
- user interfaces

Those concerns belong to downstream architecture and implementation documents.

---

# Mapping Principles

Every software requirement should be traceable to one or more methodological principles.

Software requirements should not exist independently of the methodology.

Where new implementation requirements appear necessary, the corresponding methodological justification should first be established within ASES.

This ensures that implementations remain faithful to the methodology rather than evolving independently.

---

# Requirement Categories

Requirements are grouped according to the responsibilities required to execute ASES.

## Methodology Enforcement

The execution system shall enforce applicable, authorized and mechanically expressible rules defined by ASES. Semantic engineering judgment and rule adoption remain with the appropriate participants; a mechanism must not treat a model's assertion or mere successful API call as proof of validity.

Examples include:

- preventing invalid workflow progression
- preventing unsupported state transitions
- requiring mandatory validation before promotion
- enforcing required review stages

Methodological compliance should be achieved mechanically wherever practical.

---

## Workflow Management

The execution system shall support the progression of work through the methodology.

Capabilities may include:

- tracking workflow state
- recording promotion history
- identifying incomplete activities
- managing parallel work
- coordinating dependent activities

Workflow management should reflect methodology rather than implementation convenience.

---

## Knowledge Management

The execution system shall support preservation of material reasoning underlying software engineering activities at authorized durable destinations. Relationships must be traceable where they matter; this does not require a single knowledge database, universal graph, or copying every source into one store.

Capabilities include maintaining relationships between:

- observations
- findings
- assumptions
- decisions
- challenges
- validations

Reasoning should remain traceable throughout the engineering process.

---

## Evidence Management

The execution system shall preserve evidence supporting methodological decisions.

Capabilities include:

- linking evidence to findings
- preserving supporting rationale
- recording validation outcomes
- maintaining auditability

Evidence should remain accessible for future review.

---

## AI Capability Integration

The execution system shall support evidence-based capability selection.

Capabilities include:

- accessing the AI Capability Registry
- exposing capability metadata
- supporting capability comparison
- recording observed performance
- incorporating updated evaluations

Capability selection should remain driven by research rather than static configuration.

---

## Orchestration Support

The execution system shall support coordinated interaction between humans, AI systems and supporting tools.

Capabilities include:

- assigning functional roles
- coordinating task execution
- supporting independent reasoning
- managing review workflows
- recording hand-offs
- supporting escalation

The execution system should coordinate rather than replace participants.

---

## Validation

The execution system shall support methodological validation.

Capabilities include:

- identifying missing evidence
- identifying incomplete reviews
- verifying required relationships
- determining promotion readiness

Validation should be performed consistently regardless of project size.

---

## State Management

The execution system shall maintain or retrieve the current methodological state of the artefacts it is authorized to manage, distinguishing retained authoritative state from derived views and unknown observations.

State should be:

- explicit
- recoverable
- consistent
- traceable

State transitions should only occur when permitted by the methodology and actual granted authority. The [Kernel-0 Evidence Packet](../research/kernel-0/Kernel-0-Evidence-Packet.md) states the established substrate constraints: external bounded authority; durable Work Unit and Attachment Point; disposable Execution; stale-authority exclusion; and separately verified model adequacy and realization correspondence. These constraints do not freeze primitive vocabulary or assign all higher-level concepts to the Kernel.

---

## Traceability

The execution system shall preserve relationships across the engineering process.

Users should be able to determine:

- why a decision was made
- what evidence supported it
- which assumptions influenced it
- which findings justified it
- which reviews challenged it
- which validations approved it

Traceability should extend across the complete engineering lifecycle.

---

## Human Oversight

The execution system shall preserve meaningful human control.

Capabilities include:

- approval workflows
- review visibility
- intervention points
- decision recording
- responsibility attribution

Automation should support human judgement rather than replace it.

---

# Derived Requirements

The following mappings illustrate how methodological principles become implementation requirements.

| Methodological Principle | Derived Requirement |
|---------------------------|---------------------|
| Findings require supporting observations | Prevent unsupported findings from being promoted |
| Assumptions must remain challengeable | Record challenges and their outcomes |
| Independent review reduces confirmation bias | Support isolated review workflows |
| Evidence must remain traceable | Preserve explicit epistemic relationships |
| Capability selection should be evidence-based | Integrate with the AI Capability Registry |
| Validation precedes promotion | Prevent promotion until validation succeeds |
| Workflow should minimise human error | Mechanically enforce required methodology |
| Humans retain accountability | Require explicit human approval where defined |

These mappings are illustrative rather than exhaustive.

---

# Non-Functional Requirements

Implementations should also support:

## Reliability

Methodological state should remain internally consistent.

---

## Recoverability

Projects should recover authoritative work state after interruption. Preserve unknown effect/launch outcomes rather than silently repeating work or fabricating completion. The [task-scoped handoff method](../methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md) defines current durable destinations and evidence obligations; the execution engine need not replace those stores.

---

## Transparency

System behaviour should remain understandable to users.

---

## Extensibility

New methodological rules should be introducible without redesigning the execution system.

---

## Interoperability

The execution system should support heterogeneous AI systems and external engineering tools.

---

## Efficiency

Methodology execution should minimise unnecessary:

- token consumption
- duplicated work
- repeated reasoning
- manual coordination

---

# Requirement Evolution

Requirements evolve as ASES evolves.

Changes to methodology should be reflected in this document before implementation changes are undertaken.

Implementations should therefore derive their behaviour from this specification rather than embedding methodological assumptions directly into software.

---

# Relationship to Other Documents

The Concept: Levels of Abstraction defines the abstraction boundary represented by this document.

The AI Orchestration Guide defines the methodological behaviours from which these requirements are derived.

The [Execution Engine Vision](../architecture/Execution%20Engine%20Vision.md) summarizes the current architectural intent, role boundaries and research status. It does not adopt a particular realization. The [historical architecture and experiment record](../historical/Engine%20Architecture%20and%20Experiment%20History.md) preserves the earlier mappings, proposals and evidence.

Implementations should trace their behaviour back through this document to the underlying methodology.