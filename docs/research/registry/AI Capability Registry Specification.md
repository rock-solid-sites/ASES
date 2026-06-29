---
title: AI Capability Registry Specification
program: EDASES
layer: Research
document_type: Registry
status: Active
authority: Canonical
canonical_repository: edases

depends_on:
  - Concept: Levels of Abstraction
  - Evaluation Framework
  - AI Evaluation Protocol

consumed_by:
  - AI Orchestration Guide

related_documents:
  - AI Evaluation Protocol

supersedes: []

review_frequency: Monthly

last_reviewed:

---

# AI Capability Registry Specification

## Status

**Research Artefact**

This document defines the structure, purpose and maintenance of the AI Capability Registry used by the EDASES research program.

The registry records empirical observations regarding AI systems, tools and related technologies. It is descriptive rather than prescriptive.

The registry does not recommend how capabilities should be used. That responsibility belongs to the ASES AI Orchestration Guide.

---

# Purpose

Successful orchestration depends upon understanding the capabilities and limitations of the systems being orchestrated.

Rather than relying upon anecdotal experience or vendor claims, EDASES maintains a continuously evolving evidence base describing observed behaviour across supported AI systems.

The registry exists to answer questions such as:

- What capabilities has this system demonstrated?
- Under what conditions does it perform well?
- Where does it consistently fail?
- How reliable are these observations?
- Which evidence supports these conclusions?

---

# Scope

The registry may contain entries for any technology relevant to the ASES execution environment, including but not limited to:

- Large Language Models
- Reasoning Models
- Code Generation Models
- Image Generation Models
- Embedding Models
- Search Systems
- Static Analysis Tools
- Testing Frameworks
- Formal Verification Systems
- Build Systems
- Automation Platforms
- Execution Engines
- Supporting AI Services

The registry is intentionally broader than language models.

ASES is concerned with orchestrating capabilities rather than products.

---

# Guiding Principles

## Evidence Before Opinion

Every recorded capability should be supported by one or more observations.

Unsubstantiated opinion should not be recorded as established behaviour.

---

## Behaviour Over Marketing

Entries describe observed behaviour rather than advertised features.

Capabilities should be evaluated through experimentation wherever practical.

---

## Continuous Revision

Capabilities evolve over time.

Registry entries are expected to change as new model versions, tools and workflows emerge.

Historical observations should be retained where they remain useful for understanding behavioural evolution.

---

## Independence

The registry records observations.

It does not recommend workflows, methodologies or implementation decisions.

Those are derived separately.

---

# Registry Structure

Each registry entry should contain the following sections.

---

## Identification

Required fields:

- Name
- Provider
- Version
- Release Date
- Category
- Access Method
- Licensing
- Availability

---

## Summary

A concise description of the capability.

This should describe observed strengths rather than marketing claims.

---

## Primary Capabilities

Examples include:

- software architecture
- implementation
- debugging
- repository analysis
- requirements engineering
- adversarial review
- long-context reasoning
- synthesis
- documentation
- planning
- orchestration
- testing
- code review

Capabilities should be recorded only where supported by evidence.

---

## Observed Strengths

Describe situations in which the system consistently performs well.

Each strength should reference supporting observations where available.

---

## Observed Weaknesses

Describe limitations repeatedly encountered during practical use.

Weaknesses should be recorded objectively.

---

## Failure Modes

Document recurring classes of failure.

Examples include:

- hallucinated APIs
- excessive confidence
- context degradation
- inconsistent reasoning
- omitted edge cases
- unnecessary complexity
- premature optimisation
- specification drift

Failure modes are particularly valuable for methodology design.

---

## Context Behaviour

Record observations relating to:

- large context performance
- context recovery
- instruction retention
- long-term consistency
- conversational stability

---

## Cost Characteristics

Record operational observations such as:

- relative token consumption
- cost efficiency
- context efficiency
- typical interaction overhead

Where possible, measurements should be empirical.

---

## Performance Characteristics

Examples include:

- response latency
- throughput
- reliability
- determinism
- stability across repeated executions

---

## Tool Integration

Record compatibility with:

- external tools
- APIs
- repositories
- execution environments
- development environments

---

## Human Interaction

Document observed interaction characteristics.

Examples include:

- clarification behaviour
- instruction following
- resistance to ambiguity
- responsiveness to critique
- ability to recover from mistakes

---

## Suitable Tasks

Record tasks for which evidence suggests the capability is well suited.

These should remain descriptive.

Recommendations belong elsewhere.

---

## Unsuitable Tasks

Record tasks where consistent limitations have been observed.

---

## Dependencies

Where appropriate, identify capabilities that improve performance when combined.

Examples may include:

- retrieval systems
- specialised reasoning models
- verification tools
- external execution environments

This records observed relationships without prescribing workflows.

---

## Supporting Evidence

Every significant observation should reference supporting evidence.

Evidence may include:

- controlled experiments
- project observations
- benchmark results
- replicated behaviour
- comparative studies

Evidence quality should be clearly indicated.

---

## Confidence Assessment

Every capability assessment should include an explicit confidence level.

Suggested categories:

- Preliminary
- Emerging
- Moderate
- High
- Well Established

Confidence reflects the quantity and quality of supporting evidence rather than subjective certainty.

---

## Last Review

Each entry should record:

- review date
- reviewer
- evidence considered
- significant changes

---

# Evidence Quality

Capability assessments should distinguish between different forms of evidence.

Suggested hierarchy:

1. Replicated experimental evidence
2. Repeated project observations
3. Independent reviewer agreement
4. Single project observations
5. Vendor documentation
6. Anecdotal reports

Higher quality evidence should take precedence when conflicting observations exist.

---

# Versioning

Capability entries are versioned.

Changes in model behaviour should create new observations rather than overwrite historical evidence.

This allows EDASES to study capability evolution over time.

---

# Relationship to ASES

The AI Capability Registry is maintained by EDASES as a research artefact.

ASES derives orchestration strategies from the accumulated evidence contained within the registry.

The registry therefore answers:

> What has been observed?

The AI Orchestration Guide answers:

> Given those observations, how should capabilities be coordinated?

Maintaining this separation ensures that methodology remains evidence-driven rather than opinion-driven.

---

# Future Evolution

The registry is expected to become one of the primary knowledge sources used by future execution engine implementations.

Software should eventually be capable of querying registry data to:

- recommend appropriate capabilities
- identify complementary systems
- avoid known failure modes
- support automated orchestration
- inform methodology evolution

The registry therefore serves both as a research artefact and as a future operational knowledge base.