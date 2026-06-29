---

title: Documentation Taxonomy
programme: EDASES
layer: Research
document_type: Reference
status: Active
authority: Canonical
canonical_repository: edases

depends_on:

* Documentation Standard
* Concept: Levels of Abstraction
* Canonical Terminology

consumed_by:

* All canonical and derived documentation

related_documents:

* ORIENTATION.md
* ARCHITECTURE.md

supersedes: []

## last_updated:

# Documentation Taxonomy

## Purpose

This document defines the categories of documentation used throughout the EDASES ecosystem.

It provides a common taxonomy for organising project knowledge, ensuring that documents are created at the correct abstraction layer, fulfil a clear purpose, and maintain explicit relationships with one another.

The Documentation Standard defines how documents are written. This document defines what kinds of documents exist.

---

# Principles

Documentation should:

* exist for a single primary purpose;
* occupy a single abstraction layer;
* have a clearly defined audience;
* avoid duplicating canonical knowledge;
* explicitly identify dependencies.

Every document should belong to one category defined in this taxonomy.

---

# Documentation Categories

## Top-Level Repository Documents

**Purpose**

Provide entry points into a repository.

**Examples**

* `README.md`
* `ORIENTATION.md`
* `ARCHITECTURE.md`
* `AGENTS.md`

**Characteristics**

* Repository-specific.
* Human-readable.
* Navigation-oriented.
* Generally not canonical.

---

## Canonical Documents

**Purpose**

Define the authoritative understanding of a concept.

**Characteristics**

* Canonical authority.
* Stable.
* Referenced by other documentation.
* Updated cautiously.

**Examples**

* Documentation Standard
* Concept: Levels of Abstraction
* Evaluation Framework
* Canonical Terminology

---

## Methodology Documents

**Purpose**

Describe validated engineering methods derived from research.

**Characteristics**

* Belong to ASES.
* Independent of implementation.
* Normative.

**Examples**

* AI Orchestration Guide
* Methodology → Requirements Specification

---

## Requirements Documents

**Purpose**

Translate methodology into implementation requirements.

**Characteristics**

* Traceable to methodology.
* Technology-independent.
* Implementation-neutral.

---

## Architecture Documents

**Purpose**

Describe the organisation of systems satisfying implementation requirements.

**Characteristics**

* Derived from requirements.
* Concerned with structure rather than behaviour.
* May evolve independently of implementations.

---

## Reference Documents

**Purpose**

Provide authoritative definitions, classifications or lookup information.

**Characteristics**

* Consulted rather than read sequentially.
* Frequently referenced.
* Minimise ambiguity.

**Examples**

* Canonical Terminology
* Documentation Taxonomy

---

## Standards

**Purpose**

Define mandatory conventions governing project artefacts.

**Characteristics**

* Normative.
* Cross-cutting.
* Applicable across repositories.

**Examples**

* Documentation Standard

---

## Guides

**Purpose**

Explain how to perform an activity.

**Characteristics**

* Instructional.
* Task-oriented.
* May reference multiple canonical documents.

**Examples**

* Clean Room Execution Guide

---

## Checklists

**Purpose**

Promote consistent execution of repeatable tasks.

**Characteristics**

* Operational.
* Concise.
* Complements, but does not replace, methodology.

**Examples**

* Repository Review Checklist

---

## Experimental Documents

**Purpose**

Capture ongoing investigations and provisional ideas.

**Characteristics**

* Not authoritative.
* Subject to revision.
* May become research findings.

---

## Research Records

**Purpose**

Preserve observations, experiments and findings.

**Characteristics**

* Evidence-driven.
* Traceable.
* Inputs to methodology development.

---

## Syntheses

**Purpose**

Combine multiple research outputs into higher-level conclusions.

**Characteristics**

* Derived from research.
* Explicitly cite contributing sources.
* May propose methodological changes.

---

## Historical Documents

**Purpose**

Preserve superseded knowledge for historical reference.

**Characteristics**

* Read-only.
* Not normative.
* Clearly marked as historical.

---

# Relationships

Documentation follows a layered progression.

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

Reference documents, standards and guides support multiple layers without redefining them.

---

# Dependency Rules

Documents should depend only upon documents at the same or higher abstraction level.

Derived documents should reference canonical documents rather than duplicate them.

Repository-level documents should introduce canonical documentation but should not replace it.

Historical documents should never become upstream dependencies.

---

# Choosing the Correct Document Type

Before creating a new document, ask:

1. Is this defining a concept or applying one?
2. Is this authoritative or explanatory?
3. Is this research, methodology, requirements, architecture or implementation?
4. Does an equivalent canonical document already exist?
5. Could this information belong within an existing document instead?

If a document cannot be clearly classified using this taxonomy, its purpose should be reconsidered before creation.

---

# Governance

The documentation taxonomy evolves only when the project introduces genuinely new classes of knowledge.

New document categories should be created sparingly and only when existing categories cannot adequately describe the role of a document.

Maintaining a stable taxonomy improves discoverability, reduces duplication and preserves conceptual consistency across the EDASES ecosystem.