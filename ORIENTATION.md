---
title: Project Orientation
program: EDASES
layer: Research
document_type: Guide
status: Active
authority: Derived
canonical_repository: edases
supersedes: ORIENTATION.md (previous version)
---
# ORIENTATION

Welcome to the EDASES repository.

This document provides the starting point for contributors, reviewers and AI agents. It explains how the project is organised, how knowledge is structured and where to begin reading.

For a high-level overview of the project, see `README.md`.

---

# Purpose

EDASES is a research programme investigating how non-programmers can safely and effectively use AI systems to engineer software.

The project is organised around three distinct but interdependent layers:

1. **EDASES** — the research programme.
2. **ASES** — the methodology produced by that research.
3. **Execution Engine** — software implementing the methodology.

Understanding which layer a document belongs to is essential for interpreting and modifying it correctly.

---

# Project Structure

The repository contains documentation organised by abstraction rather than implementation.

At a high level:

```text
Research
    ↓
Methodology
    ↓
Requirements
    ↓
Architecture
    ↓
Implementation
```

Lower layers may depend upon higher layers.

Higher layers should never depend upon lower layers.

This preserves conceptual independence throughout the project.

---

# Canonical Documents

The following documents define the current state of the project.

## Documentation Standard

Defines how project knowledge is represented.

Read this before creating or modifying canonical documentation.

---

## Concept: Levels of Abstraction

Defines the abstraction hierarchy used throughout the project.

This concept underpins every other canonical document.

---

## Evaluation Framework

Defines how research findings are evaluated.

---

## AI Evaluation Protocol

Defines how AI capabilities are evaluated experimentally.

---

## AI Capability Registry

Records evidence-based observations regarding AI systems and engineering tools.

---

## AI Orchestration Guide

Defines the ASES methodology for coordinating humans, AI systems and supporting tools.

---

## Methodology → Requirements Specification

Translates methodological rules into capabilities that software must provide.

---

## Execution Engine Vision

Describes the architectural vision for software capable of executing the ASES methodology.

---

# Documentation Standard

All canonical documentation follows the Documentation Standard.

Every canonical document includes metadata describing:

* programme
* abstraction layer
* document type
* authority
* dependencies
* downstream consumers

Documentation should expose relationships explicitly rather than relying upon directory structure.

---

# Repository Philosophy

The project is based upon several core principles.

## Research produces methodology.

Methodology is derived from evidence rather than intuition.

---

## Methodology produces requirements.

Implementation requirements should always trace back to methodological principles.

---

## Software implements methodology.

Software should execute the methodology rather than redefine it.

---

## Reasoning is the primary engineering artefact.

Files, commits and source code are outputs of engineering reasoning.

The project therefore focuses on preserving reasoning and the relationships between engineering decisions.

---

## Epistemic relationships are first-class.

Observations, assumptions, findings, decisions, challenges and validations form the knowledge structure of software engineering.

These relationships should remain explicit and traceable.

---

## Mechanical enforcement is preferred.

Whenever methodological correctness can be enforced automatically, automation should replace procedural compliance.

The objective is to reduce predictable human and AI error.

---

# Repository Navigation

A typical reading order is:

1. README.md
2. Documentation Standard
3. Concept: Levels of Abstraction
4. Evaluation Framework
5. AI Evaluation Protocol
6. AI Capability Registry
7. AI Orchestration Guide
8. Methodology → Requirements Specification
9. Execution Engine Vision

The remaining documentation should be interpreted in the context established by these canonical documents.

---

# Contributing

Before making significant changes:

* understand which abstraction layer you are working within
* identify the canonical documents governing that area
* ensure proposed changes remain consistent with upstream concepts
* update dependencies where necessary
* avoid introducing implementation concerns into research or methodology documents

When in doubt, resolve uncertainty by moving upward through the abstraction hierarchy rather than downward.

---

# Guidance for AI Contributors

AI contributors should additionally read `AGENTS.md`.

AI-generated contributions should:

* preserve abstraction boundaries
* avoid introducing unsupported assumptions
* maintain explicit reasoning
* respect canonical documents as the primary source of truth
* avoid duplicating concepts across multiple documents

---

# Current Project Phase

The project is transitioning from exploratory research to methodology execution.

Current priorities are:

* consolidating canonical documentation
* aligning the repository with the current conceptual model
* validating the methodology through adversarial review
* investigating architectures for the execution engine

Implementation work should remain guided by the methodology and research rather than precede them.

---

# Repository Governance

Canonical documents define the project's current understanding.

If conflicts arise:

1. Prefer canonical documents over derived documentation.
2. Prefer higher abstraction levels over lower abstraction levels.
3. Revise methodology only when supported by research.
4. Revise implementation only when required by methodology.

Maintaining these relationships preserves the integrity of the project as it evolves.