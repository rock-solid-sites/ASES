# Architecture Validation Plan v1

## Evidence-Driven Autonomous Software Engineering System (EDASES)

### Purpose

This document defines the process by which architectural assumptions are transformed into evidence-backed conclusions.

The objective is not to prove that any particular design is correct.

The objective is to systematically reduce uncertainty and replace assumptions with measured outcomes.

---

# 1. Validation Philosophy

Every major design decision begins as a hypothesis.

Hypothesis
→ Experiment
→ Measurement
→ Analysis
→ Decision

No architectural component is considered foundational until evidence supports its inclusion.

---

# 2. Evidence Classification

All assumptions receive one of five statuses.

## Unexamined

No meaningful investigation has occurred.

Confidence: Unknown

---

## Plausible

Supported by documentation, discussion, or theory.

Confidence: Low

---

## Tested

Experiment completed.

Confidence: Moderate

---

## Verified

Repeatedly demonstrated across multiple scenarios.

Confidence: High

---

## Retired

Proven ineffective, unnecessary, or superseded.

Confidence: High

---

# 3. Architectural Decision Registry

Every major architectural belief should be recorded.

Template:

Decision ID

Hypothesis

Expected Benefits

Expected Costs

Experiment Design

Success Criteria

Failure Criteria

Evidence Collected

Decision Status

Notes

---

# 4. Evaluation Categories

The system will evaluate assumptions across nine domains.

## Governance

Authority systems

Constitution models

Permission systems

Sandboxing

---

## Coordination

Task graphs

Swarm orchestration

Checkpointing

Worktrees

---

## Verification

VDD

VSDD

Mutation testing

Conformance testing

Formal verification

---

## Knowledge

Memory systems

Knowledge graphs

Lesson capture

Context retrieval

---

## Capability Intelligence

Model routing

Capability measurement

Benchmarking

Adaptation

---

## Behavioral Systems

Role definitions

Agent modes

Specialization

Prompt architectures

---

## Economics

Token efficiency

Model utilization

Verification cost

Coordination overhead

---

## Extensibility

Plugin architecture

API stability

Maintenance burden

Integration complexity

---

## Human Oversight

Principal workload

Decision fatigue

Review burden

Operational complexity

---

# 5. Foundation Selection Program

One of the earliest goals is determining the optimal architectural starting point.

Candidates:

OpenCode-first

OpenClaudia-first

CodeWhale-first

Greenfield

---

## Hypothesis F-001

OpenCode is the easiest platform to extend.

Status:
Unexamined

Metrics:

Files modified

Engineer effort

Architectural friction

Maintenance burden

---

## Hypothesis F-002

OpenClaudia is closest to the desired long-horizon workflow architecture.

Status:
Plausible

Metrics:

Native support for:

Task systems

Verification

Memory

Knowledge

Behavioral roles

Worktrees

---

## Hypothesis F-003

CodeWhale contains the strongest governance primitives.

Status:
Plausible

Metrics:

Authority enforcement

Policy consistency

Sandboxing

Routing integration

---

## Hypothesis F-004

Greenfield architecture produces a cleaner long-term design.

Status:
Plausible

Metrics:

Architectural coherence

Implementation effort

Long-term flexibility

Maintenance burden

---

# 6. Capability Intelligence Research Program

The capability registry is considered a first-class subsystem.

---

## Hypothesis C-001

Role-based capability routing reduces cost without reducing quality.

Experiment:

Compare:

Fixed model assignment

vs

Capability-aware routing

Measure:

Token cost

Completion quality

Verification findings

Success:

20%+ cost reduction

No quality degradation

---

## Hypothesis C-002

Capability scores remain predictive across projects.

Experiment:

Train routing decisions on Project A

Apply to Project B

Measure:

Prediction accuracy

Success:

Maintain predictive power above threshold

---

## Hypothesis C-003

Operational telemetry improves capability assessment.

Experiment:

Synthetic benchmarks only

vs

Synthetic + production telemetry

Measure:

Prediction accuracy

---

# 7. Behavioral Systems Research

---

## Hypothesis B-001

Role specialization improves outcomes.

Experiment:

Generic agent

vs

Architect + Implementer + Reviewer

Measure:

Defect rate

Verification findings

Cost

Success:

Lower defects at acceptable cost increase

---

## Hypothesis B-002

Claude Code Modes-derived behaviors improve engineering quality.

Experiment:

Behavioral modes enabled

vs

Behavioral modes disabled

Measure:

Planning quality

Verification quality

Task completion

Human interventions

---

## Hypothesis B-003

Behavioral systems are more effective when tied to governance controls.

Experiment:

Prompt-only behavior

vs

Prompt + runtime enforcement

Measure:

Policy violations

Task success

Verification failures

---

# 8. Verification Research Program

---

## Hypothesis V-001

VDD improves software quality.

Experiment:

Standard workflow

vs

Adversarial review workflow

Measure:

Defect escape rate

Verification findings

Cost

---

## Hypothesis V-002

Mutation testing improves confidence beyond conventional testing.

Experiment:

Standard tests

vs

Standard tests + mutation tests

Measure:

Detected regressions

Surviving mutants

---

## Hypothesis V-003

Conformance suites catch defects missed by VDD.

Experiment:

VDD only

vs

VDD + conformance

Measure:

Behavioral mismatches

---

## Hypothesis V-004

Formal verification should be reserved for selected components.

Experiment:

Measure verification cost and benefit by subsystem type.

Goal:

Determine where Thermite-style verification provides the greatest return.

---

# 9. Knowledge System Research

---

## Hypothesis K-001

Persistent knowledge reduces repeated mistakes.

Experiment:

Knowledge disabled

vs

Knowledge enabled

Measure:

Duplicate failures

Human corrections

---

## Hypothesis K-002

Structured knowledge outperforms raw documentation.

Experiment:

Markdown documents

vs

Structured retrieval

Measure:

Retrieval relevance

Task success

Token cost

---

## Hypothesis K-003

Cross-project learning produces measurable gains.

Experiment:

Fresh project

vs

Project seeded with global knowledge

Measure:

Completion quality

Cost

Oversight effort

---

# 10. Governance Research Program

---

## Hypothesis G-001

Constitution-based authority reduces harmful actions.

Experiment:

Standard permissions

vs

Constitution hierarchy

Measure:

Policy violations

Unsafe actions

---

## Hypothesis G-002

Runtime enforcement is superior to prompt-based compliance.

Experiment:

Prompt rules

vs

Runtime policy engine

Measure:

Violations

Recovery effort

---

## Hypothesis G-003

Sandboxing should be mandatory.

Experiment:

Evaluate risk reduction versus operational friction.

Measure:

Blocked unsafe operations

Developer inconvenience

---

# 11. Economics Research Program

---

## Hypothesis E-001

Verification costs less than defect correction.

Measure:

Verification spend

vs

Post-hoc correction effort

---

## Hypothesis E-002

Capability routing lowers total project cost.

Measure:

Token spend

Completion rate

Quality metrics

---

## Hypothesis E-003

Knowledge systems reduce context costs.

Measure:

Token consumption

Task success

Retrieval efficiency

---

# 12. Benchmark Framework

Three benchmark tiers.

---

## Tier 1

Micro Benchmarks

Duration:
Minutes

Purpose:
Rapid hypothesis testing

Examples:

Planning

Reviewing

Specification adherence

---

## Tier 2

Workflow Benchmarks

Duration:
Hours

Purpose:
System-level evaluation

Examples:

Feature delivery

Multi-agent collaboration

Recovery testing

---

## Tier 3

Project Benchmarks

Duration:
Days

Purpose:
Real-world evaluation

Examples:

Complete application delivery

Migration projects

Refactoring projects

---

# 13. Meta-Hypothesis Program

Some assumptions concern the research process itself.

---

## M-001

Architectural decisions can be evidence-driven.

Measure:

Percentage of major decisions supported by experiments.

Target:

90%+

---

## M-002

Capability intelligence remains useful despite model churn.

Measure:

Prediction accuracy over time.

---

## M-003

Continuous learning improves organizational effectiveness.

Measure:

Trend in:

Quality

Cost

Human effort

Across multiple projects.

---

# 14. Success Criteria

The validation program succeeds when:

Every major architectural assumption has:

A hypothesis

An experiment

A measurement

A recorded outcome

And the system increasingly relies on evidence rather than intuition.

The long-term objective is not merely to build software.

The long-term objective is to build a software engineering organization whose behavior, quality, and decision-making can be continuously measured, improved, and justified through evidence.
