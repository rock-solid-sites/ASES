# Evidence-Driven Autonomous Software Engineering System (EDASES)

## Vision, Architecture, and Validation Roadmap

### Version 0.1 (Research Draft)

---

# 1. Executive Summary

The goal of this project is not to build another coding assistant.

The goal is to build an autonomous software engineering system capable of producing high-quality software under the direction of a non-programmer principal through a combination of:

* Specification-driven development
* Multi-agent execution
* Evidence-based verification
* Continuous learning
* Capability-aware model routing
* Cost-aware orchestration
* Persistent project knowledge

The primary optimization target is:

## Software Quality × Verifiability × Autonomy × Knowledge Retention

```
              Human Effort × Token Cost
```

Traditional coding assistants optimize developer productivity.

EDASES optimizes for trustworthy software production with minimal dependence on the principal's ability to read or write code.

---

# 2. Core Design Principles

## Principle 1: Trust Comes From Evidence

The system should never require the principal to trust code solely because an agent generated it.

Confidence must be derived from evidence:

* Specifications
* Tests
* Verification artifacts
* Adversarial review
* Conformance suites
* Formal proofs (future)

Every significant decision should leave an audit trail.

---

## Principle 2: Roles Are More Important Than Models

Projects should never depend on specific model names.

Instead:

Role → Capability Requirements → Model Selection

Examples:

* Architect
* Planner
* Implementer
* Reviewer
* Verifier
* Researcher
* Knowledge Curator

Models become replaceable resources.

---

## Principle 3: Knowledge Must Outlive Sessions

Learning must persist across:

* Agent sessions
* Model changes
* Project lifetimes

Knowledge should become an accumulating asset rather than transient context.

---

## Principle 4: Verification Is A Pipeline

Software should pass through multiple verification stages.

Specification
→ Tests
→ Implementation
→ Adversarial Review
→ Mutation Testing
→ Conformance Testing
→ Formal Verification (future)

---

## Principle 5: Continuous Improvement

Every project contributes to:

* Capability intelligence
* Process improvement
* Better routing
* Better verification

The system should become more effective over time.

---

# 3. High-Level Architecture

Specification Layer
↓
Task Graph Layer
↓
Coordination Layer
↓
Role Layer
↓
Execution Layer
↓
Verification Layer
↓
Knowledge Layer
↓
Learning Layer

---

# 4. Architectural Components

## 4.1 Governance Layer

Inspired by:

* CodeWhale Constitution
* Runtime authority systems

Responsibilities:

* Authority hierarchy
* Tool permissions
* Policy enforcement
* Approval gates
* Sandbox controls

Key principle:

Every action must be authorized before execution.

---

## 4.2 Specification Layer

Source of truth.

Artifacts:

* Requirements
* Acceptance criteria
* Constraints
* Non-functional requirements
* Security requirements

Future:

* Formal specifications
* Thermite contracts

Output:

Task Graphs

---

## 4.3 Task Graph Layer

Inspired by:

* Crosslink
* OpenClaudia task systems

Responsibilities:

* Dependency management
* Ownership tracking
* Progress tracking
* Agent assignment
* Worktree coordination

Tasks become first-class objects.

Agents become temporary workers.

---

## 4.4 Coordination Layer

Responsibilities:

* Swarm orchestration
* Distributed locking
* Checkpointing
* Resume support
* Resource allocation
* Budget management

This layer manages projects rather than code.

---

## 4.5 Role Layer

Inspired by:

* Claude Code Modes
* OpenClaudia behavioral tuning

Roles are behavioral contracts.

Examples:

Architect:

* High scrutiny
* Moderate agency
* Long-horizon thinking

Implementer:

* High agency
* Moderate scrutiny

Reviewer:

* Low trust
* Adversarial mindset

Verifier:

* Maximum skepticism

Roles define behavior independently of models.

---

## 4.6 Execution Layer

Inspired by:

* OpenCode
* CodeWhale routing

Responsibilities:

* Provider integration
* Tool execution
* LSP feedback
* Editing
* Shell operations
* Routing

This layer should remain replaceable.

---

## 4.7 Verification Layer

Inspired by:

* VDD
* VSDD
* Thermite

Verification stages:

1. Static analysis
2. Test execution
3. Mutation testing
4. Adversarial review
5. Conformance testing
6. Formal verification (future)

Verification produces evidence artifacts.

---

## 4.8 Knowledge Layer

Persistent project memory.

Stores:

* Decisions
* Lessons learned
* Architectural knowledge
* Known pitfalls
* Research

May eventually support graph-based retrieval.

---

## 4.9 Learning Layer

Responsibilities:

* Session analysis
* Failure analysis
* Routing improvements
* Capability updates
* Process evolution

Output:

Recommendations and process changes.

---

# 5. Capability Intelligence System

## Purpose

Models evolve continuously.

Hardcoded assumptions become stale.

Projects should depend on capabilities, not model names.

---

## Capability Registry

Stores:

* Capability scores
* Latency
* Cost
* Reliability
* Context behavior
* Historical trends

Example:

Model X:

Planning: 0.92
Reviewing: 0.84
Bug Detection: 0.88
Cost: $Y
Latency: Z

---

## Capability Categories

Planning

Specification Analysis

Implementation

Refactoring

Review

Security Analysis

Test Generation

Tool Discipline

Context Retention

Knowledge Extraction

Adversarial Reasoning

Constitution Compliance

Cost Efficiency

Latency

Reliability

---

## Continuous Evaluation

Triggers:

* New model release
* Model update
* Pricing change
* Scheduled re-evaluation

Sources:

* Synthetic benchmarks
* Real-world project outcomes

---

## Global vs Project Knowledge

Global:

Cross-project model intelligence.

Project:

Local performance observations.

These should remain distinct.

---

# 6. Learning System

Every project generates telemetry.

Inputs:

* Session traces
* Human interventions
* Verification failures
* Routing outcomes
* Cost data

Outputs:

* Better routing
* Better role definitions
* Better constitutions
* Better specifications

---

# 7. Research Program

Current assumptions must be converted into evidence.

No assumption should remain permanent without testing.

---

# 8. Validation Framework

Every major claim receives:

Hypothesis
→ Experiment
→ Measurement
→ Conclusion

---

# 9. Architecture Validation Matrix

Question:

Which foundation best aligns with the target architecture?

Candidates:

A. OpenCode-first

B. OpenClaudia-first

C. CodeWhale-first

D. Greenfield

Evaluation Categories:

* Governance
* Verification
* Memory
* Routing
* Coordination
* Task Systems
* Learning
* Extensibility
* Community Health
* Maintenance Cost

Each scored independently.

---

# 10. Foundational Assumptions To Test

## Assumption A

OpenClaudia architecture aligns better with long-horizon autonomous engineering.

Test:

Implement identical workflow.

Measure:

* Human interventions
* Verification quality
* Recovery after interruption

---

## Assumption B

CodeWhale Constitution is a superior governance model.

Test:

Simulated policy conflicts.

Measure:

* Correct decisions
* Safety violations
* Override behavior

---

## Assumption C

Behavioral roles improve output quality.

Test:

Role-based vs generic agents.

Measure:

* Defect rate
* Verification findings
* Cost

---

## Assumption D

Capability routing reduces cost.

Test:

Fixed model vs capability-aware routing.

Measure:

* Quality
* Cost
* Completion time

---

## Assumption E

Persistent knowledge improves outcomes.

Test:

Fresh project vs knowledge-enabled project.

Measure:

* Repeat mistakes
* Token consumption
* Human interventions

---

# 11. Benchmark Program

## Tier 1: Cheap Tests

Duration:

Minutes

Purpose:

Validate assumptions quickly.

Examples:

* Planning quality
* Review quality
* Context retention
* Specification adherence

---

## Tier 2: Workflow Tests

Duration:

Hours

Purpose:

Validate architecture.

Examples:

* Multi-agent feature delivery
* Verification pipelines
* Checkpoint recovery

---

## Tier 3: Project Benchmarks

Duration:

Days

Purpose:

Validate real-world effectiveness.

Example:

Build complete application.

Measure:

* Cost
* Quality
* Intervention rate
* Verification evidence

---

# 12. Success Metrics

Primary Metrics

Human Supervision Hours

Verification Coverage

Defect Escape Rate

Token Cost

Knowledge Reuse Rate

Capability Prediction Accuracy

Learning Improvement Rate

---

# 13. Long-Term Vision

The final system should function as:

A persistent software engineering organization composed of specialized agents operating under explicit governance, continuously improving through evidence and learning, and producing software whose quality can be justified through verification artifacts rather than trust in any individual model.

Code generation is not the product.

Verified software production is the product.
