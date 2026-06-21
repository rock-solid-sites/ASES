# EDASES Assumption-to-Decision Register (A-D Register)

## Purpose

The Assumption-to-Decision Register (A-D Register) records how research assumptions influence practical project decisions and provides a mechanism for evaluating whether those assumptions produce beneficial outcomes.

The register exists to create traceability between:

```text
Research Assumption
    ↓
Project Decision
    ↓
Observed Outcome
    ↓
Evidence
```

Without such traceability it becomes difficult to determine which assumptions contributed to successful outcomes, which had no meaningful effect, and which produced unintended consequences.

The register is not intended to validate assumptions. Validation is the responsibility of the Evidence Register and related research activities.

Its purpose is to document influence.

---

# Register Structure

Each entry shall contain:

### Assumption

The originating research assumption.

### Decision

The project decision influenced by the assumption.

### Expected Outcome

The anticipated effect of the decision.

### Project Impact

The specific area of the project affected.

### Status

One of:

* Proposed
* Active
* Under Review
* Supported
* Unsupported
* Superseded

### Evidence

References to observations, metrics, reviews, or findings.

---

# Active Entries

---

## AD-001

### Assumption

Capability-first planning produces better outcomes than feature-first planning.

### Decision

Hospitality Suite requirements shall be organized around operational capabilities and workflows rather than feature lists.

### Expected Outcome

* Reduced scope drift.
* Improved requirement clarity.
* Stronger alignment with operational needs.
* Easier prioritization.

### Project Impact

* Product Specification
* Module Specifications
* Planning Process

### Status

Active

### Evidence

Pending

---

## AD-002

### Assumption

Knowledge externalization improves continuity and project outcomes.

### Decision

Major project knowledge shall be maintained in structured documents rather than conversational history alone.

### Expected Outcome

* Improved continuity.
* Reduced context loss.
* Easier onboarding.
* Improved project resilience.

### Project Impact

* Specifications
* Architecture Documentation
* Research Documentation

### Status

Active

### Evidence

Pending

---

## AD-003

### Assumption

Adversarial review improves decision quality and reduces implementation defects.

### Decision

Major architectural, workflow, and specification documents shall undergo adversarial review prior to implementation.

### Expected Outcome

* Earlier identification of flaws.
* Reduced rework.
* Improved design quality.
* More explicit assumptions.

### Project Impact

* Product Design
* Architecture
* Workflow Definition

### Status

Active

### Evidence

Pending

---

## AD-004

### Assumption

Verification quality is more important than implementation generation quality.

### Decision

Capabilities shall include explicit acceptance criteria and verification requirements before implementation begins.

### Expected Outcome

* Clear success conditions.
* Improved testing.
* Easier oversight.
* Reduced ambiguity.

### Project Impact

* Issue Definitions
* Testing
* Release Process

### Status

Active

### Evidence

Pending

---

## AD-005

### Assumption

Human oversight is most valuable during problem definition and verification.

### Decision

Human review shall be concentrated on:

* Requirements
* Capability definition
* Architecture
* Verification

rather than direct implementation activity.

### Expected Outcome

* Better use of human attention.
* Reduced bottlenecks.
* Improved strategic decisions.

### Project Impact

* Workflow Design
* Agent Orchestration
* Review Process

### Status

Active

### Evidence

Pending

---

## AD-006

### Assumption

Role specialization improves performance as project complexity increases.

### Decision

Project responsibilities shall be separated into distinct functions where practical, including:

* Specification
* Review
* Implementation
* Verification

### Expected Outcome

* Improved output quality.
* Reduced context overload.
* Better scalability.

### Project Impact

* Team Structure
* Agent Structure
* Review Process

### Status

Active

### Evidence

Pending

---

## AD-007

### Assumption

Persistent project state is more valuable than conversation state alone.

### Decision

Project decisions, specifications, and rationale shall be recorded in durable project artifacts.

### Expected Outcome

* Improved project memory.
* Better decision continuity.
* Reduced repetition.

### Project Impact

* Documentation Strategy
* Knowledge Systems

### Status

Active

### Evidence

Pending

---

## AD-008

### Assumption

Operational workflows are a more reliable source of requirements than speculative feature requests.

### Decision

Observed operational tasks shall take precedence over hypothetical future requirements when defining Version 1 scope.

### Expected Outcome

* Faster adoption.
* Reduced unnecessary complexity.
* Stronger operational value.

### Project Impact

* Product Scope
* Prioritization

### Status

Active

### Evidence

Pending

---

## AD-009

### Assumption

Incremental deployment provides higher-quality feedback than large releases.

### Decision

Modules shall be deployed independently where practical and evaluated through operational use before wider rollout.

### Expected Outcome

* Faster learning cycles.
* Earlier issue detection.
* Reduced deployment risk.

### Project Impact

* Rollout Strategy
* Release Planning

### Status

Active

### Evidence

Pending

---

## AD-010

### Assumption

Explicitly defining what will not be built improves project outcomes.

### Decision

Major specifications shall include explicit Out-of-Scope sections.

### Expected Outcome

* Reduced scope creep.
* Improved decision consistency.
* Better prioritization.

### Project Impact

* Product Specification
* Architecture Reviews
* Planning

### Status

Active

### Evidence

Pending

---

# Evaluation Process

The purpose of this register is not merely to record assumptions and decisions.

The purpose is to evaluate influence.

As evidence accumulates, each entry should be reviewed and updated.

Possible outcomes include:

### Supported

Evidence suggests the assumption contributed positively to outcomes.

### Unsupported

Evidence suggests the assumption did not produce the expected effect.

### Superseded

The assumption was replaced by a more accurate model.

### Under Review

Evidence remains inconclusive.

---

# Success Criteria

The A-D Register is considered successful if it enables future researchers to answer:

* Which assumptions influenced project decisions?
* Which assumptions improved outcomes?
* Which assumptions failed?
* Which assumptions produced unintended effects?
* Which assumptions are transferable to other projects?

The register exists to transform assumptions from abstract ideas into observable, evaluable project influences.
