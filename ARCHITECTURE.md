---
title: Conceptual Architecture
program: EDASES
layer: Research
document_type: Architecture
status: Active
authority: Canonical
canonical_repository: edases
supersedes: ARCHITECTURE.md (previous version)
---
# ARCHITECTURE

This document describes the conceptual architecture of the EDASES project and the relationship between its research, methodology and implementation activities.

It does **not** describe the implementation architecture of the execution engine. That vision is documented separately.

---

# Purpose

EDASES is organised as a layered architecture.

Each layer has a distinct responsibility and produces outputs that become inputs to the next layer.

Maintaining these boundaries ensures that research, methodology and implementation can evolve independently while remaining traceable.

---

# Architectural Overview

The project consists of three primary layers.

```text
EDASES
Research Programme
        │
        ▼
ASES
Methodology
        │
        ▼
Execution Engine
Implementation
```

Each layer answers a different question.

| Layer            | Primary Question                                  |
| ---------------- | ------------------------------------------------- |
| EDASES           | What have we learned?                             |
| ASES             | How should software engineering be performed?     |
| Execution Engine | How can the methodology be executed mechanically? |

No layer should redefine the responsibilities of another.

---

# Layer Responsibilities

## EDASES

EDASES is the research programme.

Its responsibilities include:

* conducting experiments
* evaluating AI capabilities
* developing engineering concepts
* validating findings
* refining software engineering methodology

Outputs include:

* research findings
* conceptual models
* evaluation frameworks
* capability assessments

EDASES does not define implementation architecture.

---

## ASES

ASES is the software engineering methodology produced by EDASES.

Its responsibilities include:

* defining engineering workflows
* specifying methodological rules
* describing engineering processes
* translating research into practice

Outputs include:

* methodology specifications
* orchestration guidance
* implementation requirements

ASES is intentionally independent of implementation technologies.

---

## Execution Engine

The execution engine is a software implementation of ASES.

Its responsibilities include:

* executing methodology
* maintaining engineering state
* preserving reasoning
* coordinating AI capabilities
* enforcing methodological correctness

Implementation decisions should always trace back to methodological requirements.

---

# Architectural Flow

Knowledge flows in one direction.

```text
Research
      │
      ▼
Methodology
      │
      ▼
Requirements
      │
      ▼
Architecture
      │
      ▼
Implementation
```

Validation flows in the opposite direction.

Implementation provides evidence regarding methodology.

Methodology provides evidence regarding research.

This creates a continuous improvement cycle.

---

# Canonical Documentation

The project is organised around canonical documents.

These documents define the current understanding of the project.

Derived documentation should reference canonical documents rather than duplicate them.

Current canonical documents include:

* Documentation Standard
* Concept: Levels of Abstraction
* Evaluation Framework
* AI Evaluation Protocol
* AI Capability Registry
* AI Orchestration Guide
* Methodology → Requirements Specification
* Execution Engine Vision

---

# Repository Organisation

The repository is organised according to abstraction rather than technology.

A representative structure is:

```text
README.md
ORIENTATION.md
AGENTS.md
ARCHITECTURE.md

docs/
    standards/
    research/
    methodology/
    requirements/
    architecture/
```

As the project matures, these areas may be separated into dedicated repositories.

The conceptual architecture should remain unchanged regardless of physical repository structure.

---

# Dependency Rules

Higher abstraction layers may not depend upon lower abstraction layers.

Research must remain independent of implementation.

Methodology must remain independent of implementation.

Implementation must derive from methodology.

This dependency direction preserves conceptual integrity.

---

# The Object of Interest

Traditional software projects organise work around source code.

EDASES organises work around engineering reasoning.

Reasoning produces methodology.

Methodology produces requirements.

Requirements produce software.

The architecture therefore preserves reasoning as the project's primary asset.

---

# Knowledge Architecture

Knowledge within the project is represented through explicit relationships.

Examples include:

* observations
* assumptions
* findings
* decisions
* challenges
* validations

These epistemic relationships form the basis of engineering knowledge.

Source code is one output of this knowledge rather than its primary representation.

---

# Evolution

Each layer evolves independently.

Research may introduce new findings.

Validated findings may revise the methodology.

Methodology revisions may change implementation requirements.

Implementation experience may generate new research questions.

This feedback loop enables continuous improvement while preserving traceability.

---

# Future Repository Structure

The project architecture does not require a single repository.

As the project matures, it may naturally separate into repositories such as:

```text
edases/
    Research Programme

ases/
    Methodology
    Requirements
    Execution Engine Vision

ases-engine/
    Software Implementation
```

This separation is an implementation detail rather than an architectural requirement.

The conceptual relationships between the layers remain unchanged.

---

# Architectural Principles

The architecture is guided by the following principles:

* research before methodology
* methodology before implementation
* explicit abstraction boundaries
* evidence-driven evolution
* traceable reasoning
* implementation independence
* mechanical enforcement where practical

These principles apply throughout the project regardless of future implementation choices.

---

# Relationship to Other Documents

`README.md` introduces the project.

`ORIENTATION.md` explains how to navigate the repository.

`AGENTS.md` defines operational guidance for AI contributors.

This document explains why the repository is structured as it is.

The canonical documents define the concepts, methodology and architectural vision that the repository exists to develop.