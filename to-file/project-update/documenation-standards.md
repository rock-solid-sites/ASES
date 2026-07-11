# Documentation Standard

## Document Classification

**Program:** EDASES

**Layer:** Research

**Document Type:** Standard

**Status:** Active

**Authority:** Canonical

**Canonical Repository:** edases

**Depends On:**

- Concept: Levels of Abstraction

**Consumed By:**

- All project documentation

---

# Purpose

This document defines the standards governing documentation within the EDASES ecosystem.

The objective is not stylistic consistency but structural consistency.

Every document should clearly identify its purpose, ownership, relationships and authority so that both humans and software can reason about the repository without relying upon implicit knowledge.

These standards apply regardless of storage format or implementation technology.

---

# Design Principles

Project documentation should be:

- explicit rather than implicit
- mechanically inspectable
- traceable
- implementation-independent
- minimally ambiguous
- suitable for automated processing

Documentation should expose its relationships to other documentation rather than relying upon repository structure alone.

---

# Required Metadata

Every canonical document should begin with structured metadata.

The metadata defines the document's identity within the project.

Example:

```yaml
---
title:
program:
layer:
document_type:
status:
authority:
canonical_repository:

depends_on:

consumed_by:

related_documents:

implements:

implemented_by:

supersedes:

superseded_by:

last_update:
---
```

Metadata should remain concise.

Narrative descriptions belong within the document body.

---

# Metadata Definitions

## title

The canonical document title.

Titles should remain stable.

---

## program

Defines ownership.

Permitted values:

- EDASES
- ASES
- Tooling

---

## layer

Defines the abstraction level.

Permitted values:

- Research
- Methodology
- Requirements
- Architecture
- Implementation

Every document belongs primarily to one layer.

---

## document_type

Examples include:

- Research Finding
- Research Framework
- Research Protocol
- Standard
- Registry
- Methodology Specification
- Requirements Specification
- Architecture Vision
- Design Document
- API Specification
- ADR
- User Guide

Additional types may be introduced as required.

---

## status

Lifecycle state.

Suggested values:

- Draft
- Active
- Experimental
- Validated
- Deprecated
- Archived

---

## authority

Defines whether the document is considered authoritative.

Suggested values:

- Canonical
- Derived
- Generated
- Experimental

Canonical documents are the primary source of truth.

Generated documents should never be edited directly.

---

## canonical_repository

Identifies the authoritative repository.

Examples:

- edases
- ases
- ases-engine

---

## depends_on

Documents required before this document can be understood or maintained.

Dependencies should point only toward equal or higher abstraction levels.

---

## consumed_by

Documents or systems which depend upon this document.

This relationship assists impact analysis.

---

## related_documents

Non-hierarchical relationships.

Related documents provide context without implying dependency.

---

## implements

For implementation documents.

Identifies methodology or requirements implemented by the document.

Research documents should normally leave this empty.

---

## implemented_by

For methodology and requirements documents.

Identifies downstream implementations.

---

## supersedes

Identifies documents replaced by this document.

---

## superseded_by

Identifies replacement documents.

---

## last_updated

Date of most recent update.

---

# Dependency Rules

Dependencies should follow the abstraction hierarchy.

Valid direction:

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

Lower abstraction levels may depend upon higher levels.

Higher abstraction levels should not depend upon lower levels.

This preserves conceptual independence.

---

# Authority Rules

Canonical documents define project knowledge.

Derived documents summarise canonical documents.

Generated documents are produced automatically.

Experimental documents represent work under evaluation.

Only canonical documents should establish project policy or methodology.

---

# Repository Independence

Repository location should not determine document identity.

A document's metadata should remain sufficient to determine:

- ownership
- abstraction level
- dependencies
- authority
- lifecycle

Repositories may therefore be reorganised without changing document meaning.

---

# Relationship Graph

Documentation should form a directed dependency graph rather than a collection of isolated files.

Each document should explicitly identify:

- upstream dependencies
- downstream consumers
- related concepts

The resulting graph should permit automated validation.

---

# Validation

Documentation should be mechanically verifiable.

Examples include:

- required metadata present
- dependency cycles absent
- abstraction rules satisfied
- invalid references detected
- missing canonical documents reported

Validation should become part of future tooling.

---

# Evolution

This standard is expected to evolve alongside EDASES.

New metadata fields should be introduced only where they provide measurable value for repository management, methodology execution or automated tooling.

The objective is to minimise manual repository maintenance while maximising structural clarity.

---

# Relationship to Other Documents

The Concept: Levels of Abstraction defines the conceptual hierarchy used by this standard.

The Evaluation Framework defines how methodological changes to the standard should be evaluated.

All documentation within EDASES, ASES and associated tooling should conform to this standard unless explicitly exempted.

Tooling is the current placeholder name for the technology layer of the project and will be replaced in all documentation once the final naming scheme has been developed.