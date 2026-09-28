---
title: EDASES Execution Engine Roadmap
program: EDASES
layer: Architecture
document_type: Roadmap
status: Active
authority: Derived
canonical_repository: edases

depends_on:
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
  - Kernel-0 Assurance Continuation
  - Work Unit Component Design
  - Work Unit-0 Foundational Reduction
  - EDASES Currentness and Recovery Assurance
  - EDASES Authority Ontology
  - EDASES Bounded Structural Transitions

consumed_by:
  - Execution Engine research planning
  - Execution Engine architecture work
  - Work Unit Formal Specification
  - Work Unit Prototype Testing

related_documents:
  - Concepts and Topics Registry
  - EDASES Future Topics Register
  - Execution Engine Vision
  - EDASES Efficiency Architecture

implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-28
---

# EDASES Execution Engine Roadmap

## 1. Purpose

This document records the current roadmap for developing the EDASES execution
engine.

It is a planning document, not a canonical architecture specification. The roadmap
is expected to change when research, formalization, implementation, or adversarial
testing produces new evidence.

The sequencing principle is:

> **Close the minimal execution substrate first. Evaluate optional system units
> against that working core. Defer higher-level coordination and optimization
> mechanisms until the full system has begun to take shape.**

The roadmap therefore distinguishes:

1. the execution **core**, whose guarantees must be trustworthy without optional
   higher-level systems;
2. the major optional/system-defining units that can be attached to and evaluated
   against that core;
3. higher-level coordination, optimization, and workflow mechanisms that should
   be investigated only once the underlying system exists.

This is not a commitment to implement every named component. A later component
must justify itself against the simpler system available before it.

## 2. Current architectural baseline

The current minimal-substrate hypothesis is:

- the **user/operator** is the root source of authority within EDASES;
- **Kernel** owns authoritative state-transition, represents user-derived grants,
  and mechanically enforces authority at protected boundaries;
- **Work Unit** is the durable bounded unit of work governed by the Kernel;
- execution activity is replaceable and is not the durable center of the system;
- the core must remain correct without Observer, Processor, an Orchestrator agent,
  work-topology machinery, or a generalized coordination system, even though the
  intended normal product experience uses an Orchestrator agent as the primary
  user-facing interface.

The recent Kernel-0 and Work Unit-0 investigations have strengthened rather than
expanded this baseline:

- Work Unit semantics have not justified a new Kernel primitive;
- currentness and recovery are scoped assurance obligations rather than a new
  global freshness service;
- boundary-composed authority reduces to existing Kernel semantics plus consumer
  policy and conformance;
- bounded structural transitions reduce to existing guarded whole effects,
  authority, ordering, continuity, recovery, and Work Unit-specific policy.

Accordingly, the next work should test whether this minimal model can be realized
and closed, rather than adding surrounding architecture prematurely.

## 3. Research rule: falsify before expanding

Every proposed core component or new primitive should face the same necessity
test:

> **What required guarantee cannot be expressed or realized without this
> addition?**

Convenience, performance, developer ergonomics, or expected future usefulness do
not by themselves justify promotion into the core.

A stronger addition is justified only when a concrete required history,
implementation constraint, or assurance obligation shows that the simpler model
cannot meet an accepted requirement.

This rule applies especially to the Processorless-core hypothesis described
below. A Processor may later prove highly valuable without becoming necessary to
the correctness of the minimal execution substrate.

---

# Phase I — Core substrate closure

Phase I is the current priority.

The [Phase I closure investigation](./core-substrate/Phase-I-Closure.md) records a
scoped architectural candidate, fifteen Processor falsification attempts, and
[bounded verification work](./core-substrate/Phase-I-Verification.md). No new
Kernel primitive or persistent Processor is currently justified. The former Q1
wording ambiguity is now resolved by the canonical Work Unit clarification:
engine loss must deactivate protected capability attachments but does not itself
require interior computation using still-valid resources to stop. Bounded
quiescence remains an optional stronger profile documented in
[the Q1 reasoning record](./core-substrate/Phase-I-Revocation-and-Q1.md). This is
architectural readiness for implementation and verification, not completion of the
prototype, formal assurance or hostile-test exit evidence below.

Its purpose is to turn the abstract Kernel + Work Unit model into a trustworthy,
bounded execution substrate and then attempt to falsify its sufficiency.

Frontier reasoning should be concentrated here where a mistake can alter the
entire architecture. Formalization, model construction, implementation, and
bounded empirical testing should be delegated to cheaper methods when the
architectural question is already settled.

## 4. Core target A — Concrete realization and trusted base

### Question

Can the abstract Kernel and Work Unit guarantees be realized by a sufficiently
small and explicit trusted computing base?

### Research targets

Determine:

- the smallest trusted realization boundary required to enforce Kernel decisions;
- which components may mediate filesystem, process, network, credential,
  resource, and external-service effects;
- how an abstract guarded whole commitment corresponds to a concrete effect;
- which facts or effects, if any, can exist outside the authoritative Kernel view;
- when a requested restriction cannot be represented and the system must fail
  closed;
- what physical or software assumptions remain below the verified model;
- whether any realization constraint forces a change to Kernel or Work Unit
  semantics.

### Success condition

The realization boundary is explicit enough that a later implementation can be
tested for refinement/conformance without treating ambient host behavior as
implicitly trusted.

A difficult implementation is not evidence for another Kernel primitive unless
the required guarantee itself cannot be represented by the existing model.

## 5. Core target B — Durable authoritative state and recovery

### Question

What state must survive failure, what may be reconstructed, and what is required
before recovered material can again be treated as current authoritative state?

### Research targets

Define:

- the minimum authoritative state that must persist;
- state that may be reconstructed deterministically;
- the declared failure classes covered by the core;
- process loss, executor loss, machine restart, storage failure, rollback,
  corruption, and other failure assumptions that materially change the contract;
- the trusted basis for currentness after recovery;
- the distinction between preserved historical material and recovered current
  authority;
- sealed/restricted behavior when currentness cannot be established;
- preservation of accepted work without resurrection of stale authority;
- compatible recovery of coupled commitments where required.

### Constraint

Storage mechanisms are downstream choices. Databases, logs, snapshots, counters,
replication, or other persistence mechanisms should be selected only after the
required recovery contract is explicit.

## 6. Core target C — Replaceable execution and stale-executor exclusion

### Question

What semantics are required for execution to be genuinely disposable while the
Work Unit remains authoritative and durable?

### Research targets

Determine:

- how the currently authorized execution attempt is identified;
- how superseded execution is mechanically prevented from changing authoritative
  state;
- what happens to already-authorized effects when execution is replaced;
- how lost replies are reconciled with committed, uncommitted, or
  externally-accepted effects;
- crash and partition behavior at the execution boundary;
- what must survive replacement;
- whether generation identity alone is sufficient under the selected failure
  model;
- whether leases, heartbeats, fencing tokens, or similar mechanisms are actually
  required.

### Constraint

Generation numbers, leases, heartbeats, and fencing tokens are implementation
candidates, not assumed primitives. They should enter the design only when a
specific required failure history needs them.

## 7. Core target D — Authoritative-information boundary

### Question

What kinds of information exist in EDASES, and which of them may participate in
authoritative decisions?

### Required distinctions

Formalize the roles of:

- authoritative state;
- trusted observations;
- deterministic derived facts;
- candidate proposals;
- evidence and provenance;
- bounded probabilistic judgments;
- open semantic reasoning;
- unknown or unresolved state.

### Research targets

Determine:

- which categories may directly participate in a Kernel guard;
- how an external observation becomes trustworthy enough to matter;
- when deterministic derived information becomes an authoritative dependency
  rather than advisory output;
- how semantic judgment enters the system without acquiring authority implicitly;
- what "unknown" means mechanically;
- which actions are allowed when several histories remain compatible;
- when uncertainty requires restriction, refusal, reconciliation, or escalation.

### Importance

This boundary is intended to prevent derived information, model confidence,
historical evidence, or convenient cached state from silently acquiring the same
status as current authoritative state.

It should also make later Observer, Processor, and Orchestrator research easier:
those systems can be defined in terms of what information they produce or consume
without making them part of the trusted core by default.

## 8. Core target E — Processorless-core hypothesis

### Hypothesis

> **Kernel + Work Unit + their required trusted, recovery, and execution
> mechanisms are sufficient for correctness. A persistent Processor subsystem is
> not required by the minimal execution model.**

Deterministic derivation may initially be performed externally, transiently,
manually, or recomputed when needed.

### Purpose

The project should deliberately try to invalidate this hypothesis before treating
Processor as architecturally necessary.

### Valid falsification candidates

A concrete counterexample would need to show that correctness, not merely
efficiency, requires a first-class deterministic derivation component. Examples
to test include:

- legal continuation cannot be determined from authoritative state without
  separately durable derived state;
- safe recovery requires dependency or invalidation knowledge that cannot be
  recomputed from retained authoritative inputs;
- a Kernel guard necessarily depends on derived information whose trustworthy
  computation cannot remain outside the substrate;
- correct continuation requires preservation of a derived state machine rather
  than preservation of its authoritative inputs;
- removing Processor destroys a required semantic distinction rather than merely
  increasing cost or latency.

### Non-falsifications

The following do **not** by themselves invalidate a processorless core:

- Processor makes a calculation faster;
- Processor avoids repeated model calls;
- Processor provides better caching;
- Processor derives graphs or AST information conveniently;
- Processor reduces context or token use;
- Processor makes later system features easier to implement.

Those are important Phase III questions.

## 9. Core target F — Formal assurance, refinement, and core closure

### Question

Once the previous targets are sufficiently specified, is Kernel + Work Unit a
sufficient and non-vacuous execution substrate under its declared assumptions?

### Research targets

Finalize:

- the exact formal invariant set;
- which Work Unit properties belong in the formal target;
- implementation-to-model refinement obligations;
- concrete-effect correspondence;
- trusted-base assumptions;
- failure-profile boundaries;
- non-vacuity requirements and successful witnesses;
- hostile tests for invalid transitions, races, replacement, replay, recovery,
  authority misuse, and concrete-effect bypass;
- the boundary between formal proof, strong mechanical/empirical assurance, and
  semantic/external review.

### Closure review

The final Phase I architectural review should attempt to falsify the claim:

> **Kernel + Work Unit, with the cross-cutting realization, recovery,
> execution-replacement, and information-boundary semantics defined above, are
> sufficient as the execution-engine core.**

A new primitive or core component should be added only if a concrete required
history cannot be represented or realized otherwise.

### Phase I exit condition

Phase I is complete enough to proceed when:

1. the abstract core contract is frozen sufficiently for implementation;
2. the trusted realization and failure assumptions are explicit;
3. replaceable execution is mechanically enforceable under the selected profile;
4. authoritative versus non-authoritative information is unambiguous;
5. the processorless-core hypothesis has survived targeted falsification or has
   been revised by a concrete counterexample;
6. a minimal prototype can be subjected to hostile transition/recovery testing;
7. no unresolved question requires adding a higher-level subsystem merely to hide
   a weakness in the core.

---

# Phase II — Observer

Observer research begins against the working core rather than as part of it.

The starting baseline is deliberately crude observation: logs, direct state
inspection, explicit queries, or a test harness.

The question is not "how should we build an Observer?" but:

> **What does a first-class Observer add that the working core actually needs or
> benefits from?**

## 10. Observer research targets

Investigate:

- continuously observed facts versus explicitly queried facts;
- time, liveness, external change, and environment observations;
- event-driven observation versus polling;
- observation identity and binding to authoritative state;
- delayed, missing, conflicting, or uncertain observations;
- failure isolation and backpressure;
- whether any Observer state must itself be durable;
- how Observer facts are exposed without allowing Observer to define legal state
  transitions.

Preserve the responsibility boundary:

> **Observer: WHAT IS?**

Observer should not acquire:

- Kernel authority;
- semantic decision ownership;
- general deterministic computation merely because it sees current state.

A separate Observer subsystem remains optional unless evidence justifies it.

---

# Phase III — Processor

Processor research begins only after there is a working processorless baseline.

The central evaluation question is:

> **Does a first-class deterministic derivation layer eliminate enough work or
> improve enough guarantees to justify its complexity relative to recomputation
> and the processorless core?**

Preserve the responsibility boundary:

> **Processor: WHAT FOLLOWS?**

## 11. Processor research targets

This phase is the proper home for:

- deterministic computation and derivation;
- computation reuse and memoization;
- content/result identity;
- dependency tracking;
- invalidation;
- incremental computation;
- partial evaluation;
- negative-result/dead-end retention;
- AST and code analysis;
- graph derivation;
- evidence derivation;
- deterministic command composition;
- provenance and versioning of derived results;
- deciding when recomputation is cheaper than cache/dependency maintenance;
- conversion of repeated reasoning into reusable deterministic computation where
  justified.

Research should compare Processor-enabled behavior against the processorless
baseline using real workloads and measurements.

A useful Processor does not retroactively become part of the trusted execution
core unless a later correctness counterexample proves that it must.

The experimental [EDASES Efficiency Architecture](./EDASES-Efficiency-Architecture.md)
collects the current cross-cutting efficiency baseline — derived views, cheap
inactive Work Units, recomputation, deterministic reuse, incremental computation,
partial evaluation, approximation, and persistence tests — without treating those
research directions as settled architecture.

---

# Phase IV — Orchestrator mechanism

Only after the deterministic substrate and derivation layer are sufficiently clear
should the project settle the semantic-control mechanism.

The central question is:

> **What decisions genuinely remain after authoritative state and deterministic
> derivation have done everything they can?**

Preserve the responsibility boundary:

> **Orchestrator: WHAT SHOULD WE DO?**

## 12. Orchestrator research targets

Investigate:

- human versus model orchestration;
- semantic decision ownership;
- bounded probabilistic judgment and System-1/Jev-style mechanisms;
- cheap-model versus frontier-model escalation;
- model routing based on actual residual uncertainty;
- capability/resource/information escalation;
- delegation and review;
- the boundary between semantic intent and system-owned mechanics;
- when repeated semantic decisions should become deterministic machinery;
- promotion and retraction of derived knowledge;
- how Orchestrator proposals are converted into Kernel-authorized transitions
  without giving reasoning itself authority.

The Orchestrator is expected to be the normal user-facing agent role: in ordinary
use the user directs EDASES through an LLM chat interface whose agent interprets
intent, coordinates work, and exercises the authority the user has delegated to
that role. Its authority may be narrow or broad and can be changed or revoked at
any time.

The Kernel must nevertheless remain correct without an Orchestrator agent. Direct
user control is possible in principle, and Orchestrator identity itself grants no
authority. The Kernel should not depend on a specific model family or autonomous
controller.

---

# Phase V — Work tracker and coordination substrate

This phase addresses organization across multiple Work Units.

It should not redefine the Work Unit primitive or move coordination concerns back
into the Kernel merely because they become convenient at scale.

The exact role of Crosslink or any successor should be assessed here against the
working execution engine.

## 13. Work-tracker research targets

This phase is the correct home for:

- durable work/issue identity beyond one Work Unit;
- dependency relationships;
- parent/child work structure;
- communication and delivery semantics;
- decomposition and assignment;
- multi-Work-Unit coordination;
- integration state;
- work graphs and graph replanning;
- SFC / Scaffold-Fork-Converge;
- waves and derived topology views;
- convergence and integration policy;
- scheduling;
- priority, quotas, concurrency, fairness, cancellation, and speculative work;
- multi-Work-Unit evidence and progress;
- Crosslink decomposition and architectural ownership of its existing functions.

These mechanisms may be important to the final engine while remaining entirely
outside the execution core.

---

# Phase VI — Full-system and future-topic research

Once the core and major units above have begun to compose into a real system, the
project can return to the wider Future Topics Register with concrete architecture
and measurements.

## 14. Deferred topics

Examples include:

- checkpoint products and stacked-diff workflows;
- Git versus runtime durability and integration history;
- graph-execution optimization;
- generalized context reconstruction;
- negative computation across Work Units/projects;
- evidence transfer across integration boundaries;
- generalized communication systems;
- advanced scheduling and resource management;
- agent-facing context-packet optimization;
- harness self-optimization;
- simulation and approximation systems;
- full-system telemetry and cost attribution;
- subsystem ablation;
- broader evaluation methodology;
- automatic interface/tool-surface optimization.

The Future Topics Register remains a useful repository of questions, but it is
not a ranked build list. Topics should be pulled forward only when the working
system makes their dependencies and value concrete.

Some may disappear because earlier architecture makes them unnecessary.

---

# 15. Sequencing summary

The current roadmap is:

```text
I. CORE SUBSTRATE CLOSURE
   Kernel + Work Unit
   ├─ concrete realization / trusted base
   ├─ durable authoritative state / recovery
   ├─ replaceable execution / stale-executor exclusion
   ├─ authoritative-information boundary
   ├─ processorless-core falsification
   └─ formal refinement / adversarial core closure
                 │
                 ▼
II. OBSERVER
   trustworthy facts, liveness, and event observation
                 │
                 ▼
III. PROCESSOR
   deterministic derivation, reuse, invalidation, computation elimination
                 │
                 ▼
IV. ORCHESTRATOR
   semantic judgment, escalation, delegation, and decision control
                 │
                 ▼
V. WORK TRACKER / COORDINATION
   multi-Work-Unit structure, communication, topology, integration, scheduling
                 │
                 ▼
VI. FULL SYSTEM / FUTURE TOPICS
   higher-level mechanisms justified by the composed system
```

The arrows express the default research dependency, not a prohibition on all
parallel work. Small experiments may occur earlier when they provide evidence for
a current architectural question.

## 16. Model and assurance routing

Frontier reasoning should be reserved for questions that may change the
architecture, trusted boundary, primitive set, or fundamental semantic contracts.

Examples:

- a counterexample suggesting Kernel-0 is insufficient;
- a realization constraint that forces a new authoritative distinction;
- a failure history that defeats the processorless-core hypothesis;
- a dispute over the boundary between authoritative state and derived/judgment
  state.

Cheaper models and deterministic methods should normally handle:

- retrieval and provenance;
- documentation propagation;
- formalization after semantics are fixed;
- finite model construction;
- implementation;
- fixture generation;
- property tests;
- fuzzing;
- fault injection;
- trace checking;
- bounded adversarial testing.

Formal independent review should remain cross-family when it is used as review
evidence.

## 17. Change rule

This roadmap is intentionally revisable.

A phase may be:

- narrowed;
- reordered;
- split;
- merged;
- deferred;
- removed entirely

when evidence supports the change.

The governing constraint is not fidelity to this roadmap. It is preservation of
the project's core design discipline:

> **Build the smallest trustworthy execution substrate first. Add later machinery
> only when the working system demonstrates why it is needed.**
