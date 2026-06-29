---

title: Canonical Terminology
programme: EDASES
layer: Research
document_type: Reference
status: Active
authority: Canonical
canonical_repository: edases

depends_on:

* Documentation Standard
* Concept: Levels of Abstraction

consumed_by:

* Evaluation Framework
* AI Evaluation Protocol
* AI Capability Registry
* AI Orchestration Guide
* Methodology → Requirements Specification
* Execution Engine Vision
* README.md
* ORIENTATION.md
* AGENTS.md
* ARCHITECTURE.md

related_documents:

* Documentation Standard

supersedes: []

## last_updated:

# Canonical Terminology

## Purpose

This document defines the canonical meaning of terms used throughout the EDASES ecosystem.

These definitions provide a shared vocabulary for researchers, contributors, reviewers and AI agents.

Where terminology conflicts arise, the definitions in this document take precedence unless explicitly superseded.

---

# Project Terms

## EDASES

**Epistemically-Driven Agentic Software Engineering System.**

The research programme investigating improved approaches to AI-assisted software engineering.

Its outputs are research findings, conceptual models and validated methodology.

---

## ASES

**Agentic Software Engineering System.**

The software engineering methodology developed through EDASES research.

ASES defines how software engineering should be performed independently of any implementation technology.

---

## Execution Engine

A software system that executes the ASES methodology.

The execution engine implements the methodology but does not define it.

---

# Conceptual Terms

## Research

The systematic investigation of software engineering questions through observation, experimentation and evaluation.

Research produces findings.

---

## Methodology

A validated set of engineering principles, processes and rules derived from research.

Methodology produces implementation requirements.

---

## Requirement

A capability or behaviour required of an implementation to correctly execute the methodology.

Requirements derive from methodology rather than implementation preference.

---

## Architecture

The organisation of a system satisfying a set of requirements.

Architecture derives from requirements.

---

## Implementation

A concrete software realisation of an architectural design.

Implementations may vary while remaining compliant with the same methodology.

---

# Knowledge Terms

## Observation

A recorded fact obtained through experimentation, evaluation or engineering activity.

Observations form the evidential basis of findings.

---

## Finding

A conclusion supported by one or more observations.

Findings should remain traceable to supporting evidence.

---

## Assumption

A proposition accepted provisionally pending validation or refutation.

Assumptions should remain explicit and challengeable.

---

## Decision

A recorded engineering choice made using available evidence.

Decisions should reference the findings and assumptions that informed them.

---

## Challenge

A reasoned objection to an observation, finding, assumption or decision.

Challenges are an expected component of methodological validation.

---

## Validation

The process of determining whether a claim, finding or artefact satisfies defined criteria.

Validation increases confidence but does not establish absolute truth.

---

## Evidence

The observations, experiments and reasoning supporting a finding or decision.

Evidence should remain accessible and traceable.

---

## Epistemic Relationship

An explicit relationship describing how knowledge elements depend upon, support or challenge one another.

Examples include:

* observation supports finding
* finding challenges assumption
* decision depends upon evidence
* validation approves promotion

Epistemic relationships are the primary object of interest within EDASES.

---

# Engineering Terms

## Capability

A demonstrable ability of an AI system, tool or participant to perform a defined engineering task.

Capabilities are determined through evaluation rather than assumption.

---

## Orchestration

The coordination of humans, AI systems and tools to perform software engineering according to the ASES methodology.

---

## State

The current methodological condition of an engineering activity.

State is managed explicitly by the execution engine.

---

## Promotion

The advancement of an artefact or reasoning step to the next methodological stage following successful validation.

---

## Traceability

The ability to determine how an engineering artefact, decision or conclusion was derived.

Traceability should extend from implementation back to research where practical.

---

# Architectural Terms

## Abstraction Layer

A conceptual level within the project architecture.

The primary layers are:

1. Research
2. Methodology
3. Requirements
4. Architecture
5. Implementation

Dependencies should flow only from lower abstraction to higher abstraction.

---

## Canonical Document

A document designated as the authoritative source for a concept within the project.

Derived documentation should reference rather than duplicate canonical documents.

---

## Derived Document

Documentation that explains, applies or summarises canonical knowledge without redefining it.

---

# Governance

Changes to canonical terminology should occur only when:

* new research introduces a genuinely new concept;
* an existing definition is demonstrated to be inadequate; or
* terminology is refined to improve conceptual clarity.

Terminology should evolve cautiously to preserve consistency across the project.