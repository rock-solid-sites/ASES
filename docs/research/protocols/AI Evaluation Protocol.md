---
title: AI Evaluation Protocol
programme: EDASES
layer: Research
document_type: Research Protocol
status: Active
authority: Canonical
canonical_repository: edases

depends_on:
  - Concept: Levels of Abstraction
  - Evaluation Framework

consumed_by:
  - AI Capability Registry

related_documents:
  - Evaluation Framework

supersedes: []

review_frequency: Quarterly

last_reviewed:

---

# AI Evaluation Protocol

## Status

**Research Protocol**

This document defines the procedures by which EDASES evaluates AI systems, AI-assisted tools, and related technologies.

Its purpose is to ensure that capability assessments are reproducible, comparable and evidence-based.

---

# Purpose

The AI Capability Registry records observations.

This protocol defines how those observations are produced.

Without a common evaluation protocol, capability assessments become anecdotal and cannot reliably support methodological development.

This protocol therefore establishes the minimum requirements for generating evidence suitable for inclusion within the AI Capability Registry.

---

# Objectives

The protocol aims to:

- produce repeatable evaluations
- minimise evaluator bias
- support comparison between capabilities
- distinguish observations from conclusions
- generate evidence suitable for methodology development

---

# Evaluation Principles

## Repeatability

Equivalent evaluations should produce comparable results when repeated under similar conditions.

---

## Transparency

All evaluations should record sufficient metadata for another researcher to understand how the observation was produced.

---

## Comparability

Different systems should be evaluated against identical tasks wherever practical.

Differences in prompts, context or constraints should be documented explicitly.

---

## Independence

Evaluations should assess observed behaviour rather than expected behaviour.

Vendor documentation and marketing claims should not be treated as evidence.

---

## Continuous Revision

Evaluations represent observations at a particular point in time.

They should be repeated when significant model or tool updates occur.

---

# Evaluation Lifecycle

```text
Research Question
        ↓
Experiment Design
        ↓
Execution
        ↓
Observation
        ↓
Analysis
        ↓
Capability Assessment
        ↓
Registry Update
```

---

# Evaluation Metadata

Every evaluation should record:

- evaluation identifier
- evaluator
- date
- system evaluated
- version
- provider
- access method
- configuration
- temperature or equivalent parameters
- tools available
- context size
- elapsed time
- token consumption (where applicable)

---

# Task Definition

Each evaluation should define:

- objective
- expected outcome
- available information
- constraints
- success criteria

Tasks should reflect realistic software engineering activities.

---

# Task Categories

Evaluations should be classified according to one or more categories.

Examples include:

- requirements engineering
- software architecture
- debugging
- refactoring
- testing
- code review
- documentation
- planning
- synthesis
- orchestration
- implementation
- repository navigation
- adversarial review

Additional categories may be introduced as the methodology evolves.

---

# Experimental Controls

Where comparison is intended, evaluations should attempt to control:

- identical task definitions
- equivalent context
- equivalent supporting information
- equivalent external tools
- equivalent time constraints

Known differences should be recorded.

---

# Observation Recording

Observations should describe behaviour rather than interpretation.

Examples include:

- required clarification
- omitted requirements
- hallucinated APIs
- architectural inconsistencies
- successful decomposition
- effective reasoning
- unnecessary complexity

Observations should avoid conclusions such as "excellent" or "poor" without supporting evidence.

---

# Assessment Dimensions

Evaluations may assess characteristics including:

## Correctness

Did the result satisfy the task?

---

## Completeness

Were important aspects omitted?

---

## Consistency

Did reasoning remain internally coherent?

---

## Robustness

How well did performance remain stable under increasing complexity?

---

## Explainability

Was reasoning understandable and traceable?

---

## Efficiency

Resources consumed during completion.

Examples include:

- elapsed time
- token usage
- interaction count

---

## Collaboration

Where multiple systems are involved:

- ability to accept critique
- ability to build upon previous work
- consistency across hand-offs
- recovery from conflicting information

---

# Failure Recording

Failures should be classified where possible.

Examples include:

- hallucination
- logical inconsistency
- missing requirements
- unsupported assumptions
- context degradation
- excessive verbosity
- premature optimisation
- incomplete reasoning

Repeated failure patterns should inform future methodology development.

---

# Comparative Evaluations

When comparing systems:

Each system should receive:

- identical objectives
- equivalent context
- equivalent constraints
- equivalent opportunities for clarification

Results should be assessed independently before comparison.

---

# Longitudinal Evaluation

Capabilities change over time.

Important evaluations should be repeated:

- after significant model updates
- after methodology revisions
- after workflow changes
- after tooling changes

Previous observations should remain available for comparison.

---

# Confidence Assessment

Confidence should reflect the quantity and quality of supporting evidence.

Suggested levels:

- Preliminary
- Emerging
- Moderate
- High
- Well Established

Confidence applies to the observation rather than the evaluated system.

---

# Registry Integration

Completed evaluations may generate:

- new capability entries
- revised strengths
- revised weaknesses
- updated failure modes
- revised confidence assessments

Registry updates should reference the supporting evaluations.

---

# Relationship to ASES

This protocol is maintained by EDASES.

It exists to generate trustworthy evidence.

ASES consumes the resulting evidence when defining:

- orchestration strategies
- methodology revisions
- implementation guidance

ASES does not define how evaluations are conducted.

---

# Future Evolution

As the execution engine matures, portions of this protocol may become partially or fully automated.

Automation may assist with:

- experiment execution
- metadata collection
- result comparison
- statistical analysis
- confidence updates

Final capability assessments remain subject to methodological review.