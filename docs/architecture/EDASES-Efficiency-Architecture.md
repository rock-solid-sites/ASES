---
title: EDASES Efficiency Architecture
program: EDASES
layer: Architecture
document_type: Architecture Vision
status: Experimental
authority: Derived
canonical_repository: edases

depends_on:
  - EDASES Work Unit Component Design
  - EDASES Execution Engine Roadmap
  - Phase I Processorless Core Falsification

consumed_by:
  - Future Observer research
  - Future Processor research
  - Future Orchestrator research
  - Work Unit realization
  - EDASES architecture review

related_documents:
  - EDASES Authority Ontology
  - Concepts and Topics Registry
  - Execution Engine Vision

implements: []
implemented_by: []
supersedes: []
superseded_by: []

last_updated: 2026-09-28
---

# EDASES Efficiency Architecture

## 1. Status

This document consolidates the **current efficiency architecture research baseline**.

It is intentionally **Experimental / Derived**. Efficiency remains a major open research area in EDASES. The purpose here is not to freeze mechanisms, but to gather the principles and correspondences already established well enough to constrain future exploration and prevent repeated rediscovery.

A later finding may invalidate, narrow, or relocate any mechanism described here.

The core discipline is:

> **Keep authoritative machinery small. Prefer reconstruction, derivation, and demand-driven work over persistent machinery unless measurement or a required guarantee demonstrates otherwise.**

Efficiency is treated as an architectural constraint rather than a late optimization phase, while specific optimizations remain evidence-driven.

---

## 2. Minimal substrate, rich derived system

The working execution substrate should remain small enough that higher-level behavior can be constructed above it without forcing that behavior into the trusted core.

At the lowest level:

~~~text
Kernel
  └── Work Units
       ├── bounded durable identity/state
       ├── resource grants
       ├── capability attachments
       ├── accepted contents
       ├── optional nested Work Units
       └── arbitrary computation while active
~~~

A Work Unit does not intrinsically require:

- an LLM agent;
- a resident process;
- a VM or container;
- an issue;
- a scheduler;
- a conversation;
- an Observer;
- a Processor;
- an Orchestrator;
- a dashboard;
- a work graph.

In deliberately simple use, a Work Unit may act analogously to a more strongly bounded and durable tmux pane. The user may run arbitrary code of their choice within the authority and resource boundaries granted to that Work Unit.

The richer system is layered above this substrate.

---

## 3. Derived views are the default

User interfaces and coordination representations should normally be **derived views** over smaller authoritative state and observations.

Examples include:

- chat interfaces;
- current-agent and subagent status panes;
- issue and work trackers;
- topology or dependency graphs;
- dashboards;
- progress summaries;
- cost views;
- history browsers;
- scheduling views;
- project maps.

A visual representation should not become authoritative merely because users depend on it operationally.

The default design test is:

> **If this view disappears, can it be reconstructed from retained authoritative state, accepted contents, and observations without changing the meaning of the work?**

If yes, persistence of the view is an optimization or UX choice rather than a correctness requirement.

This does not forbid caching or materialization. It means the derived representation should not silently become a second source of truth.

---

## 4. Logical scale should be cheap

A durable Work Unit should be cheap when inactive.

The intended direction is that an inactive Work Unit approaches:

- a small set of durable authoritative records;
- references to bounded contents or storage;
- relationship metadata;
- no resident model or execution runtime unless needed.

It should not inherently require:

- a permanent process;
- one daemon per Work Unit;
- one scheduler per Work Unit;
- one VM/container per Work Unit;
- a resident LLM context;
- continuous polling.

The scaling principle is:

> **Resource consumption should scale primarily with actual active computation and required observation, not with the number of logical objects represented.**

A system may therefore retain large numbers of dormant or historical Work Units while only a small subset consume meaningful CPU, RAM, network, model, or tool resources.

---

## 5. Processorless-by-default

Phase I currently supports a processorless correctness core:

> Kernel + Work Unit and their required trusted realization/recovery mechanisms should remain sufficient for correctness unless a concrete counterexample proves that separately persistent deterministic derivation state is required.

This does **not** mean deterministic computation is undesirable.

It means that caches, dependency graphs, incremental state, AST indexes, derived topology, reusable results, and similar structures do not become correctness primitives merely because they save work.

The burden of proof differs:

- **correctness machinery** must justify why the system cannot safely function without it;
- **efficiency machinery** must justify itself through measured savings, responsiveness, cost, throughput, or another declared operational objective.

A Processor may eventually be highly valuable without becoming part of the trusted execution core.

---

## 6. Recompute before persisting derived machinery

For a derived value D = f(B, P), recomputation is preferred when:

- the authoritative base B and relevant policy/interpretation P are retained;
- f is sufficiently bounded and reproducible for the required use;
- recomputation preserves required observations;
- no correctness deadline makes recomputation impossible;
- maintaining D, dependencies, invalidation and recovery would cost as much or more than recomputation.

Persistent derived state becomes attractive when measurement shows repeated recomputation dominates cost or latency, or when a real guarantee cannot otherwise be met.

This yields a recurring comparison:

~~~text
cost(recompute)
    versus
cost(store + index + invalidate + recover + verify-current)
~~~

The cheaper architecture may vary by workload.

---

## 7. Formal correspondences already identified

Several EDASES ideas correspond directly to established computing techniques.

These correspondences are research anchors, not claims that EDASES has already implemented the mature form of each technique.

| EDASES concern | Established correspondence | Current architectural interpretation |
| --- | --- | --- |
| react only when something relevant changes | Event-driven computation | Prefer events/notifications to continuous polling where trustworthy observation permits |
| update only consequences affected by change | Incremental computation | Candidate Processor optimization once dependency/value economics justify it |
| reuse a previous deterministic answer | Memoization | Reuse only with sound applicability/currentness checks |
| specialize repeated computation using known inputs | Partial evaluation | Candidate way to eliminate repeated reasoning/tool composition |
| trade precision for cost under explicit bounds | Approximate computing | Future research; simulation/System-1 mechanisms may provide bounded approximations where correctness policy allows |
| make invalid states or effects impossible structurally | Constraint by construction | Kernel/Work Unit authority and confinement are the primary current example |
| put minimum semantics in trusted core | Minimal kernels | Kernel-0 and the Work Unit reduction follow this direction |
| keep views outside source-of-truth state | Materialized/derived views | UI, graph, dashboard and tracker representations should normally rebuild from smaller sources |
| compute only when requested or useful | Demand/lazy computation | Avoid permanent subsystem activity without a consumer |
| turn repeated semantic work into cheaper deterministic work | Computation compilation / reuse | Processor research should seek proven repeated reasoning that can be safely mechanized |

Each item needs deeper research before implementation policy is frozen.

---

## 8. Event-driven over polling where possible

Continuous polling creates work proportional to elapsed time even when nothing changes.

Where a trustworthy source can expose events or changed-state indicators, the architecture should investigate event-driven observation first.

However, event delivery itself may be incomplete, delayed, lossy, duplicated, or outside the trusted boundary. Therefore:

> **Event-driven is an efficiency preference, not an excuse to weaken observation correctness.**

The Observer phase must determine which facts require polling, event subscription, direct query, or some combination.

---

## 9. Incremental computation and memoization are optional layers

Incremental computation, memoization, indexes and dependency graphs are useful only when their maintenance burden is justified.

They introduce costs of their own:

- dependency discovery;
- invalidation;
- provenance;
- currentness checks;
- storage;
- recovery;
- cache misses;
- drift prevention;
- version/interpretation binding.

A cached answer that cannot prove applicability may be cheaper to store but more expensive to trust.

Therefore the Processor phase should measure complete workload economics rather than benchmark only cache-hit latency.

---

## 10. Approximation belongs behind explicit policy

Approximate computation can be useful when exact work is unnecessarily expensive and the consumer can tolerate bounded uncertainty.

Potential future EDASES uses include:

- cheap System-1 classification before expensive reasoning;
- simulation or sampling;
- approximate search;
- probabilistic routing;
- heuristic prioritization;
- bounded summarization.

Approximate results must not silently satisfy exact Kernel premises.

The architecture should distinguish:

- an approximation used to decide what to inspect next;
- a bounded judgment explicitly authorized by policy;
- an authoritative fact requiring exact or otherwise trusted evidence.

This topic remains substantially open.

---

## 11. Arbitrary computation remains possible

Efficiency does not require restricting EDASES to a specialized workflow language.

The system should be able to operate similarly to existing CLI coding agents when the user desires:

~~~text
user
  ↓
Orchestrator (normally)
  ↓
Work Unit
  ↓
shell / compiler / editor / tests / arbitrary user code
~~~

A user may grant broad capabilities and run general-purpose software inside a Work Unit.

The architectural difference from ambient CLI-agent authority is that external effects remain bounded by explicit current capability relationships.

This preserves generality while allowing lightweight higher-level machinery.

---

## 12. UI and interaction should not inflate the substrate

The expected product may expose a sophisticated experience:

~~~text
chat
agent-status panes
visual issue tracker
topology views
review state
metrics
history
~~~

These should normally be projections over lower-level state.

A UI process should be restartable without changing system truth.

A chat transcript should not need to be the only durable representation of project state.

A visual issue tracker need not imply that every Work Unit is an issue.

An agent-status tree need not imply that every logical Work Unit has a resident agent.

This separation permits UX richness without making the runtime correspondingly heavy.

---

## 13. Orchestrator efficiency role

The Orchestrator is expected to be the normal user-facing LLM agent, but it should not become a universal compute engine.

Efficiency research should test how much work can be discharged before invoking expensive semantic reasoning:

- deterministic state checks;
- direct retrieval;
- cached/reusable results;
- cheap-model routing;
- bounded System-1 decisions;
- ordinary tools;
- user-specified policy;
- Processor derivation where justified.

The residual semantic uncertainty is what should reach the more expensive Orchestrator reasoning path.

This principle does not reduce the Orchestrator's authority by itself. Authority and computational routing are separate concerns.

---

## 14. Failure behavior separates correctness from optimization

An important current distinction is:

- **authority/correctness controls** fail closed where the claimed guarantee requires it;
- **pure optimization layers** should normally be removable or bypassable without changing correctness.

For example, a command-rewriting optimization may safely fail open to the original command if the rewrite only saves tokens or latency. A capability guard cannot safely fail open if its function is to prevent unauthorized effects.

This provides a useful test for later Processor features:

> **If this optimization disappears, does correctness change or only cost/latency?**

If correctness changes, the component may have crossed into the trusted architecture and must be analyzed accordingly.

---

## 15. Measurement before machinery

Optimization should be driven by observed workload costs.

Useful measurements may include:

- model calls;
- tokens;
- latency;
- local CPU/RAM;
- network usage;
- repeated retrieval;
- repeated deterministic computation;
- cache hit/miss rates;
- invalidation frequency;
- time spent reconstructing context;
- idle overhead;
- number of logical versus active Work Units.

The project should avoid building generalized schedulers, dependency engines, caches or topology systems merely because such systems are common.

The question is:

> **Which repeated cost is large enough that eliminating it pays for the mechanism that eliminates it?**

---

## 16. Current constraints for future architecture

Until evidence changes them, future EDASES components should be evaluated against these constraints:

1. **Dormant logical state should be cheap.**
2. **Active cost should follow active work.**
3. **Derived views should normally be reconstructible.**
4. **Persist derived state only when its economics or a required guarantee justify persistence.**
5. **Keep correctness authority independent of optimization machinery where possible.**
6. **Prefer demand/event-driven work to unconditional continuous work where observation semantics allow it.**
7. **Allow arbitrary general-purpose computation inside bounded Work Units.**
8. **Do not force rich UX concepts into Kernel or Work Unit ontology.**
9. **Measure complete maintenance cost, not just fast-path performance.**
10. **Re-minimize after each new subsystem proves useful.**

These are working constraints, not universal theorems.

---

## 17. Open research program

Substantial efficiency research remains, including:

- rigorous workload and cost models;
- event-driven Observer design;
- incremental dependency tracking;
- memoization validity and identity;
- partial evaluation opportunities;
- negative-result reuse;
- cache placement and eviction;
- cross-Work-Unit and cross-project reuse;
- approximate computation and bounded uncertainty;
- System-1 decision routing;
- context reconstruction and compression;
- lazy tool/interface discovery;
- scheduling and resource allocation;
- graph/topology optimization;
- locality and edge operation;
- durable versus ephemeral state economics;
- local versus remote computation;
- subsystem ablation;
- full-system cost attribution.

The current document should therefore be used as an **Astra exploration baseline**, not as a conclusion that efficiency architecture is settled.

A future research result may split this document into more precise architecture and research records once the mechanisms have enough evidence.
