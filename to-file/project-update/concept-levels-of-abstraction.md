---
title: Concept: Levels of Abstraction
programme: EDASES
layer: Research
document_type: Research Finding
status: Active
authority: Canonical
canonical_repository: edases

depends_on: []

consumed_by:
  - Evaluation Framework
  - AI Evaluation Protocol
  - AI Capability Registry
  - AI Orchestration Guide
  - Methodology → Requirements Mapping
  - Execution Engine Vision
  - Documentation Standard

related_documents:
  - Evaluation Framework
  - Documentation Standard

supersedes: []

review_frequency: On Release

last_reviewed:
---

Levels of Abstraction
Status

Research Finding

This document records a validated finding from the EDASES research programme and forms part of the conceptual foundation of ASES.

Purpose

One of the earliest architectural deadlocks within EDASES arose because questions were being asked and answered at incompatible levels of abstraction. Independent analyses repeatedly escaped these deadlocks by reframing the question at a higher level before returning to the implementation.

This document defines the abstraction hierarchy used throughout the project and establishes where different kinds of questions belong.

The purpose of the hierarchy is to ensure that research, methodology, architecture and implementation remain conceptually distinct while maintaining clear relationships between them.

The Abstraction Hierarchy

The project consists of five distinct abstraction levels.

Research
    ↓
Methodology
    ↓
Requirements
    ↓
Architecture
    ↓
Implementation

Each level constrains the levels below it without being constrained by implementation details.

Level 1 — Research (EDASES)
Purpose

To investigate how non-programmers can safely and effectively direct heterogeneous AI systems to engineer software.

Produces
research questions
observations
experiments
findings
hypotheses
validated principles
Answers questions such as
What problems exist?
Which approaches appear effective?
What evidence supports a conclusion?
Which assumptions have been falsified?
Which methodology changes are justified?

Research does not prescribe implementation.

Level 2 — Methodology (ASES)
Purpose

To capture the current best-supported practices derived from EDASES.

Produces
workflows
artifact types
review processes
validation procedures
promotion rules
orchestration patterns
Answers questions such as
How should work progress?
How should evidence be evaluated?
When is a decision justified?
How should multiple AI systems collaborate?

ASES is implementation-independent.

It defines what should happen rather than how software performs it.

Level 3 — Requirements
Purpose

Translate methodological rules into capabilities that software must provide.

Produces
functional requirements
behavioural requirements
validation requirements
orchestration requirements
Answers questions such as
What must an implementation support?
What must be prevented?
What information must remain traceable?
What state transitions require validation?

Requirements describe behaviour, not technology.

Level 4 — Architecture
Purpose

Determine how software satisfies the requirements.

Produces
component boundaries
execution models
persistence strategies
communication mechanisms
deployment models
Answers questions such as
Should operational state be graph-based?
How should orchestration be implemented?
How should derived state be maintained?
How should services communicate?

Architecture chooses solutions without changing methodology.

Level 5 — Implementation
Purpose

Construct working software.

Produces
source code
schemas
interfaces
tests
deployment artefacts
Answers questions such as
Which database?
Which language?
Which framework?
Which API?

Implementation should never define methodology.

Direction of Influence

Influence flows downward.

Research
      ↓

Methodology

      ↓

Requirements

      ↓

Architecture

      ↓

Implementation

Evidence flows upward.

Implementation

      ↓

Operational Evidence

      ↓

Research

      ↓

Methodology Revision

This creates the continuous research cycle used throughout EDASES.

Solving Problems at the Correct Level

Questions should be answered at the highest abstraction level capable of determining the lower levels.

For example:

Incorrect

Should Findings be stored in YAML?

This is an implementation question asked before the methodological purpose of Findings has been established.

Correct sequence

Why do Findings exist? (Research)
How should Findings behave? (Methodology)
What capabilities are required? (Requirements)
How should those capabilities be realised? (Architecture)
How should they be implemented? (Implementation)

The implementation follows naturally once the higher-level questions have been answered.

Lessons from the Provenance Deadlock

The original provenance discussions focused primarily on implementation questions:

Git commits
storage formats
provenance mechanisms
databases

Independent reasoning repeatedly converged on a higher-level question:

What is the object of interest?

The answer was not commits.

It was reasoning.

Once the question moved from implementation to methodology, the architectural deadlock dissolved.

This established an important methodological principle:

Architectural uncertainty often indicates that the underlying methodological question has not yet been answered.

Relationship to EDASES and ASES

EDASES operates primarily at the Research level.

ASES occupies the Methodology level.

Software implementations operate at the Architecture and Implementation levels.

The Requirements layer forms the contract between ASES and its implementations.

This separation allows:

multiple implementations of ASES
independent evolution of methodology
evidence-driven refinement of the research
replacement of technologies without changing the methodology
Research Finding

EDASES has identified that many apparently technical disagreements are actually abstraction mismatches.

Attempting to resolve implementation questions before establishing the corresponding research, methodological or requirements-level principles leads to unnecessary architectural deadlock.

Conversely, establishing the correct abstraction level first frequently causes lower-level decisions to become straightforward consequences rather than independent design problems.

Visualization
Levels of Abstraction
        │
        ├──────────────┐
        ▼              ▼
Evaluation      Capability Registry
Framework              │
        │              ▼
        │      Orchestration Guide
        │              │
        └──────┬───────┘
               ▼
Methodology → Requirements
               │
               ▼
Execution Engine Vision