---
title: "EDASES Topic: Methodology Research"
program: EDASES
layer: Research
document_type: Research Record
status: Active
authority: Experimental
canonical_repository: edases

depends_on:
  - Documentation Standard
  - EDASES Phase 4 Retrospective

related_documents:
  - EDASES-topic-Git-Based-Engineering-Systems.md
  - EDASES-Methodology-Feedback-and-Enforcement.md

consumed_by:
  - ASES methodology development

supersedes: []

superseded_by: []

last_updated: 2026-08-10
---

# EDASES Methodology Research

**Status:** Research branch proposal

## 1. Purpose

ASES is being developed as a methodology for agentic software engineering, while EDASES is the research program through which that methodology is discovered and refined.

EDASES should not develop this methodology in isolation.

Software engineering, systems engineering, quality engineering, operations, and other engineering disciplines have accumulated substantial prior art around problems that overlap with EDASES:

* coordinating complex work;
* representing processes;
* preserving decisions and rationale;
* controlling change;
* detecting deviations;
* handling incidents;
* verifying results;
* learning from failures;
* improving processes;
* measuring process behavior;
* maintaining reproducibility;
* and converting experience into reusable practice.

This research branch exists to investigate that prior art systematically.

The objective is **not** to select an existing methodology and adopt it as ASES.

Instead, research should determine:

1. what existing approaches already solve;
2. how they solve it;
3. what assumptions their solutions depend upon;
4. which mechanisms are transferable to ASES;
5. which mechanisms require modification;
6. which mechanisms conflict with EDASES's goals;
7. where ASES is independently converging with established practice;
8. and where EDASES appears to require genuinely different mechanisms.

## 2. Scope and level of abstraction

This branch is specifically an **EDASES research activity**.

It concerns methodologies, process systems, quality systems, decision systems, and other bodies of engineering practice that can inform the development of ASES methodology.

It does **not** investigate the operational implementation of ASES.

In particular, agentic harnesses, orchestration systems, execution environments, model capabilities, tool systems, and similar technologies belong to research at the ASES or Execution levels rather than this branch.

The distinction is:

```
EDASES
  │
  │ researches
  ▼
ASES methodology
  │
  │ is operationalized by
  ▼
Execution
  │
  │ operates through
  ▼
tools / harnesses / environments
```

A subject may therefore provide useful information to multiple levels, but it should be researched at the level where its primary question belongs.

## 3. Research philosophy

The research should be **mechanism-oriented rather than label-oriented**.

"Methodology" is too broad a category to make direct comparisons between all subjects meaningful.

For example:

* SEMAT Essence is a framework for describing software-engineering methods;
* RUP is a software-development process;
* BPMN is a process-modeling notation;
* ADR is a decision-recording practice;
* CAPA is a corrective/preventive quality process;
* FMEA is a failure-analysis method;
* OODA is an operational decision loop;
* DORA is an empirical software-engineering research program.

These should not be treated as equivalent methodologies.

Instead, each should be studied for the **engineering mechanisms it embodies**.

## 4. Primary research subjects

### 4.1 SEMAT Essence

**Priority: Very high**

SEMAT Essence is particularly important because it addresses the meta-level problem of representing software-engineering methods themselves.

Research should examine:

* how methods are decomposed into common elements;
* how practices are represented;
* how activities and states are modeled;
* how different methods can be compared;
* what constitutes a reusable methodological element;
* whether Essence provides useful vocabulary or structure for ASES.

The central EDASES question is:

> Can a methodology such as ASES be represented as a composable set of practices, states, activities, constraints, and competencies rather than as a monolithic process document?

This should be one of the earliest investigations in the branch.

### 4.2 Rational Unified Process (RUP)

**Priority: High**

RUP provides prior art for a structured, iterative engineering process with explicit:

* disciplines;
* roles;
* activities;
* artifacts;
* workflows;
* lifecycle phases;
* milestones;
* and iterative development.

Research should focus on what happens when a complex engineering process is explicitly decomposed into interacting activities and artifacts.

The important comparison is not whether ASES should resemble RUP, but whether RUP contains useful mechanisms for representing the relationship between methodology, work state, artifacts, roles, and verification.

### 4.3 Team Software Process (TSP)

**Priority: High**

TSP is relevant because it treats software engineering as a disciplined, measurable process rather than merely a collection of programming practices.

Research should examine:

* planning;
* process measurement;
* quality management;
* team coordination;
* estimation;
* defect prevention;
* process discipline;
* and feedback.

Particular attention should be given to which assumptions of TSP depend on human teams and which mechanisms may remain useful for ASES.

### 4.4 Agile, Scrum, Kanban, and Extreme Programming

**Priority: High**

These should be studied primarily as families of mechanisms rather than as competing doctrines.

Research should examine:

* iterative development;
* work decomposition;
* prioritization;
* feedback cycles;
* work-in-progress control;
* incremental delivery;
* planning;
* coordination;
* customer feedback;
* retrospectives;
* and engineering practices.

The research should distinguish mechanisms that remain useful to ASES from mechanisms whose assumptions depend on conventional human-team structures.

### 4.5 Lean Software Development

**Priority: High**

Lean is relevant because of its emphasis on:

* flow;
* feedback;
* waste reduction;
* limiting unnecessary work;
* shortening feedback loops;
* and continuous improvement.

The investigation should focus particularly on whether Lean's process-improvement principles provide useful prior art for EDASES's goal of learning continuously from live projects.

### 4.6 Six Sigma and DMAIC

**Priority: High**

Six Sigma provides prior art for measurement-oriented process improvement.

Research should examine:

* Define;
* Measure;
* Analyze;
* Improve;
* Control;
* process variation;
* defect analysis;
* evidence-based improvement;
* and maintaining improvements after intervention.

The key EDASES question is whether methodology development can benefit from a comparable separation between identifying a problem, gathering evidence, analyzing it, changing the system, and verifying that the improvement persists.

### 4.7 DORA

**Priority: High**

DORA provides important prior art for empirical software-engineering research and the translation of research findings into engineering guidance.

Research should examine:

* measurement;
* empirical research;
* capability models;
* research-to-practice translation;
* feedback;
* and the relationship between engineering practices and outcomes.

DORA is particularly relevant because EDASES is itself intended to learn from evidence generated by live engineering work.

### 4.8 ITIL

**Priority: Medium–High**

ITIL provides prior art for operational management rather than software development itself.

Relevant mechanisms include:

* incident management;
* problem management;
* change management;
* configuration management;
* service continuity;
* controlled evolution;
* and operational feedback.

This is directly relevant to the distinction between:

```
immediate execution fix
      versus
later methodological investigation
```

Research should determine whether ITIL's separation of incidents, underlying problems, and controlled changes provides useful mechanisms for EDASES.

### 4.9 Business Process Model and Notation (BPMN)

**Priority: High**

BPMN is not a methodology but provides prior art for explicitly representing processes.

Research should examine:

* process states;
* activities;
* events;
* gateways;
* parallelism;
* exceptions;
* responsibilities;
* and process transitions.

The investigation should ask whether process-modeling concepts could provide useful representation mechanisms for EDASES/ASES methodology and workflow models.

### 4.10 OODA Loop

**Priority: Medium–High**

OODA provides a compact model of operational adaptation:

* Observe;
* Orient;
* Decide;
* Act.

It is relevant because live engineering produces a continuous sequence of observations, interpretation, decisions, interventions, and new observations.

Research should determine whether OODA provides useful conceptual machinery for describing EDASES feedback loops without assuming that EDASES should simply be modeled as OODA.

## 5. Decision and knowledge systems

### 5.1 Architecture Decision Records (ADR)

**Priority: High**

ADR provides prior art for preserving decisions and their rationale.

Research should examine:

* decision capture;
* rationale;
* alternatives;
* consequences;
* supersession;
* traceability;
* and durable engineering knowledge.

### 5.2 Generalized Architecture Decision Records (GADR)

**Priority: Very high**

GADR is particularly relevant because it addresses the transformation from project-specific decision knowledge into reusable generalized guidance.

This closely resembles a central EDASES problem:

```
project experience
      ↓
generalized finding
      ↓
reusable methodology
```

Research should determine how GADR handles generalization and whether its mechanisms can inform the EDASES distinction between project-specific evidence and ASES methodology.

## 6. Quality, failure, and verification systems

### 6.1 Cleanroom Software Engineering

**Priority: High**

Cleanroom provides prior art for defect prevention, formal specification, statistical quality control, and independent verification.

Research should examine its assumptions about:

* correctness;
* specification;
* verification;
* quality control;
* statistical process measurement;
* and defect prevention.

### 6.2 Test-Driven Development and Behavior-Driven Development

**Priority: Medium**

These provide prior art for expressing desired behavior before or alongside implementation and using executable verification to constrain development.

Research should focus on the general mechanism:

```
desired behavior
      ↓
executable specification
      ↓
implementation
      ↓
verification
```

This may be relevant to the broader EDASES concept of turning methodology requirements into executable constraints.

### 6.3 Continuous Integration

**Priority: Medium**

CI provides prior art for automatically evaluating changes as they enter a shared engineering system.

Relevant mechanisms include:

* automated verification;
* change-triggered evaluation;
* fast feedback;
* integration;
* and preventing known failures from propagating.

### 6.4 Independent Verification and Validation / Formal Verification

**Priority: High**

These should be investigated for their treatment of independence, evidence, correctness, and confidence.

The key EDASES question is:

> Which claims about an engineering process can be independently verified rather than accepted from the same process that produced them?

## 7. Corrective and failure-management systems

### 7.1 CAPA — Corrective and Preventive Action

**Priority: Very high**

CAPA is particularly relevant to the emerging EDASES feedback architecture.

Its distinction between:

* correcting an observed problem; and
* changing the system to prevent recurrence

closely resembles the distinction between:

```
immediate project intervention
      versus
methodological learning
```

Research should determine whether CAPA provides useful prior art for representing:

* incidents;
* immediate corrections;
* root-cause investigation;
* systemic corrective actions;
* preventive actions;
* verification of effectiveness;
* and closure.

This should be compared directly with the proposed EDASES methodology-incident model.

### 7.2 Failure Mode and Effects Analysis (FMEA)

**Priority: High**

FMEA provides prior art for systematically identifying potential failure modes before or during operation.

Research should examine:

* failure-mode identification;
* causes;
* effects;
* detection;
* severity;
* likelihood;
* mitigation;
* and prioritization.

This may be particularly useful for EDASES's work on methodology failure modes, execution safety, and adversarial review.

FMEA should not be assumed to be directly applicable. Its value is primarily as prior art for structured reasoning about how engineering systems can fail.

## 8. Comparative research rubric

Every research subject should eventually be analyzed using a common rubric.

### Purpose

What problem was the system designed to solve?

### Type

Is it a:

* methodology;
* process framework;
* practice;
* decision system;
* quality system;
* research system;
* process notation;
* or other engineering system?

### Unit of work

What does it treat as its fundamental unit?

Examples include:

* task;
* requirement;
* change;
* decision;
* incident;
* artifact;
* iteration;
* experiment;
* deployment.

### State model

What state does the system represent?

### Process model

How does work move between states?

### Knowledge model

What knowledge is considered durable?

### Evidence model

How does the system establish that something is true or successful?

### Decision model

How are decisions made and preserved?

### Feedback model

How does experience modify future behavior?

### Verification model

What is independently checked?

### Enforcement model

Which requirements can be mechanically enforced?

### Human role

What remains dependent on human judgment?

### Change model

How does the system evolve when its current process proves inadequate?

### Failure model

How are failures represented, investigated, and recovered?

### Traceability

Can outcomes be traced back through decisions, assumptions, evidence, and implementation?

### Reproducibility

Can another participant reconstruct how the outcome was produced?

### EDASES applicability

Which mechanisms are:

* directly reusable;
* reusable with modification;
* useful only as conceptual prior art;
* incompatible with EDASES;
* or already independently represented in ASES?

## 9. Convergence and divergence

A major purpose of this research is identifying how ASES relates to established prior art.

### Independent convergence

ASES has independently arrived at a mechanism that resembles an established approach.

This can provide validation, terminology, known limitations, and implementation experience.

### Adapted convergence

ASES has arrived at a related mechanism but under different assumptions.

The differences should be documented explicitly.

### Genuine divergence

Existing approaches do not adequately address a requirement identified by EDASES, or their assumptions conflict with the requirements emerging from EDASES.

This may represent an important research result.

### Rejected prior art

A mechanism was investigated and intentionally rejected.

The reason should be preserved so that the same question does not repeatedly return as though it were unexplored.

## 10. Research artifacts

The branch should eventually use a structure such as:

```
methodology-research/
  README.md
  subjects/
  mechanisms/
  comparative-analysis/
  convergence/
  divergence/
  rejected-approaches/
  synthesis/
  bibliography/
```

Each subject should answer:

> What does this system actually do, what assumptions does it make, and which mechanisms are relevant to EDASES?

Research reports should preserve external evidence separately from EDASES's own conclusions.

## 11. Relationship to EDASES and ASES

Methodology research should not directly modify ASES.

The preferred flow is:

```
external prior art
      ↓
methodology research
      ↓
comparison and evidence
      ↓
EDASES finding
      ↓
ASES synthesis
      ↓
methodology proposal
      ↓
live-project validation
```

This maintains the distinction between:

* what an external methodology claims;
* what EDASES observes;
* what EDASES concludes;
* and what ASES ultimately prescribes.

Research findings may subsequently motivate work in other EDASES or ASES research areas. For example, research into declarative/reconciliation systems such as GitOps belongs primarily to systems/architecture research, even though a finding from that research could eventually influence ASES methodology.

## 12. Initial research priorities

The initial corpus should be prioritized approximately as follows.

### Tier 1 — methodology and meta-methodology

1. SEMAT Essence
2. GADR
3. ADR
4. RUP
5. TSP
6. Lean Software Development
7. Six Sigma / DMAIC
8. DORA

### Tier 2 — process and operational methodology

9. ITIL
10. BPMN
11. OODA
12. Agile
13. Scrum
14. Kanban
15. Extreme Programming

### Tier 3 — quality, verification, and corrective systems

16. CAPA
17. FMEA
18. Cleanroom Software Engineering
19. Independent Verification and Validation
20. Formal Verification
21. TDD
22. BDD
23. Continuous Integration

This ordering is provisional. Research findings should be allowed to change it.

## 13. Desired outcome

The desired outcome is a comparative map of engineering prior art that allows EDASES to answer two questions:

> What have other engineering disciplines already learned that ASES should not rediscover?

and:

> What does the agentic software-engineering problem require that existing engineering methodologies do not adequately provide?

The research branch should therefore become part of EDASES's epistemic infrastructure.

Its purpose is not to make ASES resemble established methodologies.

Its purpose is to make ASES **informed by prior art, explicit about its departures from prior art, and able to distinguish genuinely novel requirements from problems that engineering disciplines have already solved.**
