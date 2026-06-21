# Architecture Assumption Register v1

## Evidence-Driven Autonomous Software Engineering System (EDASES)

### Purpose

This document tracks all known architectural assumptions.

Assumptions are treated as unresolved risks until tested.

Each assumption receives:

* Unique ID
* Confidence Level
* Validation Priority
* Planned Experiment
* Current Status

Statuses:

* Unexamined
* Plausible
* Tested
* Verified
* Retired

Confidence Levels:

* Low
* Medium
* High

Validation Priorities:

* Critical
* High
* Medium
* Low

---

# Section A: Foundation Strategy

## A-001

Assumption:

A single existing harness should serve as the project foundation.

Confidence:

Low

Priority:

Critical

Status:

Unexamined

Validation:

Foundation comparison program.

---

## A-002

Assumption:

OpenClaudia is architecturally closer to the desired end state than OpenCode.

Confidence:

Medium

Priority:

Critical

Status:

Plausible

Validation:

Feature and architecture audit.

---

## A-003

Assumption:

CodeWhale governance primitives are superior to alternatives.

Confidence:

Medium

Priority:

Critical

Status:

Plausible

Validation:

Governance benchmark suite.

---

## A-004

Assumption:

Greenfield architecture produces lower long-term complexity.

Confidence:

Low

Priority:

Critical

Status:

Plausible

Validation:

Architecture modeling exercise.

---

## A-005

Assumption:

The long-term maintenance burden of greenfield development is acceptable.

Confidence:

Low

Priority:

Critical

Status:

Unexamined

Validation:

Maintenance projection study.

---

# Section B: Governance

## B-001

Assumption:

Constitution-based governance improves agent behavior.

Confidence:

Medium

Priority:

Critical

Status:

Plausible

---

## B-002

Assumption:

Runtime enforcement is more effective than prompt-based compliance.

Confidence:

High

Priority:

Critical

Status:

Plausible

---

## B-003

Assumption:

Authority hierarchies reduce unsafe actions.

Confidence:

Medium

Priority:

High

Status:

Plausible

---

## B-004

Assumption:

Sandboxing should be mandatory by default.

Confidence:

Medium

Priority:

High

Status:

Plausible

---

## B-005

Assumption:

Permission systems should be capability-driven rather than tool-driven.

Confidence:

Low

Priority:

Medium

Status:

Unexamined

---

# Section C: Behavioral Systems

## C-001

Assumption:

Behavioral roles outperform generic agents.

Confidence:

Medium

Priority:

Critical

Status:

Plausible

---

## C-002

Assumption:

Claude Code Modes-derived role systems transfer successfully to other models.

Confidence:

Low

Priority:

Critical

Status:

Unexamined

---

## C-003

Assumption:

Role specialization improves verification quality.

Confidence:

Medium

Priority:

High

Status:

Plausible

---

## C-004

Assumption:

Behavior should be enforced through runtime mechanisms rather than prompts alone.

Confidence:

Medium

Priority:

High

Status:

Plausible

---

## C-005

Assumption:

Agent roles should be project assets rather than session settings.

Confidence:

Low

Priority:

Medium

Status:

Unexamined

---

# Section D: Capability Intelligence

## D-001

Assumption:

Capability-aware routing reduces overall costs.

Confidence:

Medium

Priority:

Critical

Status:

Plausible

---

## D-002

Assumption:

Capability scores can be measured reliably.

Confidence:

Low

Priority:

Critical

Status:

Unexamined

---

## D-003

Assumption:

Operational telemetry improves capability assessment.

Confidence:

Medium

Priority:

High

Status:

Plausible

---

## D-004

Assumption:

Projects should never reference specific model names.

Confidence:

Medium

Priority:

High

Status:

Plausible

---

## D-005

Assumption:

Role requirements can be mapped effectively to measurable capabilities.

Confidence:

Low

Priority:

Critical

Status:

Unexamined

---

## D-006

Assumption:

Capability intelligence remains predictive despite model updates.

Confidence:

Low

Priority:

Critical

Status:

Unexamined

---

# Section E: Verification

## E-001

Assumption:

VDD improves software quality.

Confidence:

Medium

Priority:

Critical

Status:

Plausible

---

## E-002

Assumption:

VSDD improves outcomes beyond VDD alone.

Confidence:

Low

Priority:

Critical

Status:

Unexamined

---

## E-003

Assumption:

Mutation testing provides unique value.

Confidence:

Medium

Priority:

High

Status:

Plausible

---

## E-004

Assumption:

Conformance testing catches defects missed by adversarial review.

Confidence:

Low

Priority:

High

Status:

Unexamined

---

## E-005

Assumption:

Formal verification should be targeted rather than universal.

Confidence:

Medium

Priority:

Medium

Status:

Plausible

---

## E-006

Assumption:

Verification artifacts can substitute for direct code inspection.

Confidence:

Medium

Priority:

Critical

Status:

Plausible

---

# Section F: Knowledge Systems

## F-001

Assumption:

Persistent knowledge reduces repeated mistakes.

Confidence:

High

Priority:

Critical

Status:

Plausible

---

## F-002

Assumption:

Cross-project learning provides measurable value.

Confidence:

Medium

Priority:

Critical

Status:

Plausible

---

## F-003

Assumption:

Structured knowledge retrieval outperforms raw documentation.

Confidence:

Medium

Priority:

High

Status:

Plausible

---

## F-004

Assumption:

Knowledge should be separated into project and global layers.

Confidence:

Medium

Priority:

High

Status:

Plausible

---

## F-005

Assumption:

Knowledge graphs provide value beyond semantic retrieval.

Confidence:

Low

Priority:

Low

Status:

Unexamined

---

# Section G: Coordination

## G-001

Assumption:

Task graphs should be first-class objects.

Confidence:

Medium

Priority:

Critical

Status:

Plausible

---

## G-002

Assumption:

Worktree-per-agent is superior to shared repositories.

Confidence:

Medium

Priority:

High

Status:

Plausible

---

## G-003

Assumption:

Checkpoint and resume functionality significantly improves reliability.

Confidence:

Medium

Priority:

High

Status:

Plausible

---

## G-004

Assumption:

Multi-agent coordination produces net gains.

Confidence:

Low

Priority:

Critical

Status:

Unexamined

---

## G-005

Assumption:

Crosslink-style coordination should be central rather than optional.

Confidence:

Low

Priority:

High

Status:

Unexamined

---

# Section H: Economics

## H-001

Assumption:

Verification costs less than defect correction.

Confidence:

Medium

Priority:

Critical

Status:

Plausible

---

## H-002

Assumption:

Capability routing improves quality-per-dollar.

Confidence:

Medium

Priority:

Critical

Status:

Plausible

---

## H-003

Assumption:

Knowledge systems reduce token consumption.

Confidence:

Medium

Priority:

High

Status:

Plausible

---

## H-004

Assumption:

Human attention is the primary scarce resource.

Confidence:

High

Priority:

Critical

Status:

Plausible

---

## H-005

Assumption:

Most engineering costs can be shifted from humans to agents.

Confidence:

Medium

Priority:

Critical

Status:

Plausible

---

# Section I: Human Oversight

## I-001

Assumption:

A non-programmer principal can effectively direct software development through specifications and evidence.

Confidence:

Low

Priority:

Critical

Status:

Unexamined

---

## I-002

Assumption:

Verification evidence can be presented in a form understandable to non-programmers.

Confidence:

Low

Priority:

Critical

Status:

Unexamined

---

## I-003

Assumption:

Decision fatigue can be reduced through role specialization.

Confidence:

Low

Priority:

Medium

Status:

Unexamined

---

## I-004

Assumption:

The system can continuously improve while remaining understandable to its operator.

Confidence:

Low

Priority:

Critical

Status:

Unexamined

---

# Section J: Meta-Assumptions

## J-001

Assumption:

Architectural decisions can be evidence-driven.

Confidence:

High

Priority:

Critical

Status:

Plausible

---

## J-002

Assumption:

The validation framework itself is capable of identifying poor assumptions.

Confidence:

Medium

Priority:

Critical

Status:

Unexamined

---

## J-003

Assumption:

The project can evolve faster than the AI ecosystem changes.

Confidence:

Low

Priority:

Critical

Status:

Unexamined

---

## J-004

Assumption:

Long-term learning compounds rather than creating complexity.

Confidence:

Low

Priority:

Critical

Status:

Unexamined

---

# Initial Validation Order

Tier 0 — Foundational Questions

A-001
A-002
A-003
A-004
I-001
I-002

These determine whether the overall project direction is viable.

---

Tier 1 — Core Mechanics

B-001
C-001
D-001
D-002
E-001
F-001
G-001
G-004

These validate the primary architecture.

---

Tier 2 — Optimization

D-003
E-003
F-003
G-003
H-002

These improve efficiency.

---

Tier 3 — Long-Term Research

D-006
E-005
F-005
J-003
J-004

These shape the future evolution of the system.

---

Current Register Summary

Total Assumptions: 54

Critical: 24

High: 19

Medium: 9

Low: 2

Verified: 0

Retired: 0

Primary Goal:

Reduce the number of unexamined critical assumptions to zero as quickly as possible.
