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
  - EDASES Authority Ontology
  - EDASES Execution Engine Roadmap
  - Phase I Processorless Core Falsification

consumed_by:
  - Future Observer research
  - Future Processor research
  - Future Orchestrator research
  - Execution Engine implementation planning
  - Astra architecture investigation packet

related_documents:
  - Phase I Core Substrate Closure
  - Phase I Core Substrate Verification Work
  - Concepts and Topics Registry
  - Execution Engine Vision

implements: []
implemented_by: []
supersedes: []
superseded_by: []

last_updated: 2026-09-28
---

# EDASES Efficiency Architecture

## 1. Status and purpose

This document consolidates the **current efficiency architecture baseline** for
EDASES. It is intentionally **Experimental** and **Derived**.

Efficiency is not considered solved. Significant research remains in deterministic
reuse, event-driven observation, incremental computation, partial evaluation,
approximation, context management, scheduling, model routing, caching, topology,
and system-level measurement. The purpose of this document is narrower: collect
the principles already established strongly enough to constrain future work and
prevent higher-level convenience features from unnecessarily expanding the core.

The working thesis is:

> **Keep the authoritative substrate small. Represent durable necessity directly.
> Recompute, derive, observe, or render everything else when that is cheaper and
> correctness permits it. Promote machinery into durable state only when a required
> guarantee or measured efficiency result justifies the added complexity.**

This is an architectural bias to be tested, not a universal theorem.

---

## 2. Minimal substrate, rich derived system

The current core hypothesis is deliberately small:

```text
Kernel
  └── Work Units
       ├── bounded durable state
       ├── resource grants
       ├── capability attachments
       ├── optional nested Work Units
       └── arbitrary internal computation
```

The core need not contain a chat application, agent tree, issue board, scheduler,
dependency graph, persistent cache, semantic work tracker, or autonomous
Orchestrator.

Those systems may be valuable. Their value does not by itself make them part of
the minimal correctness substrate.

The expected product can still be rich:

```text
chat UI      status panes      issue tracker      topology view
   \              |                |                 /
    \             |                |                /
     +--------- derived / reconstructed views ------+
                          |
                          v
          authoritative state + observations
                          |
                          v
                 Kernel + Work Units
```

A rich user experience and a minimal substrate are therefore complementary rather
than competing goals.

---

## 3. Work Units as cheap execution cells

A Work Unit is not intrinsically an LLM session, process, VM, container, worktree,
issue, or workflow.

This has an important efficiency consequence:

> **Representing a Work Unit should not require paying for active execution.**

An inactive Work Unit may eventually be realizable as little more than the durable
state required to preserve its identity, containment, grants, accepted contents,
and recovery obligations.

When execution is desired, the Work Unit may host an agent, a shell, a compiler, a
test process, a deterministic program, or arbitrary user-selected code.

At the low-level operating surface, a collection of active Work Units may therefore
behave analogously to a set of `tmux` panes or CLI-agent sessions, but with explicit
Kernel-governed boundaries and authority.

For example, a user may deliberately grant a Work Unit broad filesystem, shell,
network, or other capabilities and run arbitrary code inside it. EDASES does not
need to replace the flexibility of ordinary CLI computing with a rigid workflow
language. Its contribution is that those powers are **explicit bounded grants**
rather than ambient consequences of the host process.

This analogy does not imply that Work Units must be implemented using `tmux`,
processes, containers, or any other specific mechanism.

---

## 4. Cost should track active work, not represented work

The architecture should aim for a system in which:

- a large number of dormant Work Units does not imply a large number of resident
  agents or processes;
- durable project structure is cheap to retain;
- active execution consumes resources only while actual work is occurring;
- expensive model reasoning is used only where residual uncertainty justifies it;
- derived state does not remain live merely because a UI once displayed it.

These are design targets, not measured performance claims.

A project may eventually contain hundreds or thousands of historical, dormant, or
waiting Work Units. That should not imply hundreds or thousands of active model
contexts, containers, supervisors, or polling loops unless a concrete requirement
demands them.

---

## 5. Derived views should normally be disposable

Many useful product surfaces are interpretations of underlying state rather than
authority-bearing objects.

Examples include:

- chat transcripts or conversational projections;
- current-subagent status panes;
- visual issue trackers;
- agent trees;
- workflow graphs;
- dependency visualizations;
- dashboards;
- activity feeds;
- scheduling views;
- summaries;
- search indexes;
- cached navigation structures.

The working rule is:

> **If a view can be reconstructed from retained authoritative state and adequate
> observations without changing required semantics, the view should not become
> authoritative merely because it is useful.**

A UI crash should not normally threaten correctness. The UI should rebuild.

Likewise, a status dashboard should not become a second state owner. A visual issue
tracker may be the normal way a user understands work while remaining a projection
over lower-level state.

This principle applies equally to agent-facing context: a context packet may be
generated for convenience without becoming the durable source of truth for the
facts it summarizes.

---

## 6. Processorless by default

Phase I has so far failed to demonstrate that a persistent Processor subsystem is
required for correctness.

That result does **not** mean computation is absent from the trusted system. Kernel
guards may perform deterministic computation where necessary.

It means that a separately durable derived-state lifecycle has not been shown
necessary.

The baseline preference is therefore:

```text
authoritative inputs
      |
      v
bounded deterministic computation
      |
      v
result used / checked
```

rather than automatically:

```text
authoritative inputs
      |
      v
persistent derivation subsystem
      |
      +-- cache
      +-- queue
      +-- dependency graph
      +-- invalidation state
      +-- incremental state
      +-- scheduler
```

A Processor may later be highly valuable. Processor research should test whether it
eliminates enough repeated work or improves enough guarantees to justify its
persistent machinery relative to recomputation.

The burden is not "prove caching is useful." It is:

> **Show that the chosen persistent derivation machinery provides enough measured
> value, or is required by a correctness guarantee, to justify the state and
> invalidation complexity it introduces.**

---

## 7. Recompute versus retain

A derived value is a candidate for recomputation when:

- its authoritative dependencies are retained;
- its computation terminates within the supported domain;
- the computation or verification is trustworthy enough for its consumer;
- recomputation preserves required observations;
- no correctness deadline requires the value to exist sooner;
- reconstruction does not require information that has legitimately disappeared.

Retention becomes necessary when deleting information would make histories with
different required future observations indistinguishable.

This yields an important distinction:

- **accepted results or irrecoverable observations** may be durable authoritative
  information even if computation produced them;
- **caches, indexes, paths, summaries, and reusable derivations** remain derived
  when their required meaning is reproducible from retained inputs.

Calling something a cache does not make required information disposable.
Calling something state does not make it authoritative.

---

## 8. Efficiency correspondences

Several established computing ideas correspond closely to EDASES mechanisms. The
correspondence is useful for future research, but the formal names should not be
mistaken for requirements to introduce new subsystems.

| Computing concept | Current EDASES correspondence | Research direction |
| --- | --- | --- |
| **Minimal kernels** | Keep authoritative Kernel semantics small; move convenience and policy machinery outward unless correctness forces it inward. | Continue re-minimization after each stronger profile or counterexample. |
| **Event-driven computation** | Observer or host events should trigger work when facts change rather than requiring universal polling. | Compare event delivery, missed events, reconciliation, and polling fallbacks. |
| **Incremental computation** | Recompute only consequences affected by changed authoritative inputs where maintaining dependency information is worthwhile. | Measure dependency-maintenance cost against fresh recomputation. |
| **Memoization / deterministic reuse** | Reuse deterministic results when identity, provenance, applicability, and currentness can be checked cheaply. | Develop applicability/invalidation tests and cross-project reuse evidence. |
| **Partial evaluation** | Precompute stable portions of repeated deterministic work while leaving variable inputs for later. | Identify recurring guards, analyses, or tool flows where specialization pays. |
| **Approximate computing** | Simulation, bounded System-1/Jev-style judgments, or other approximate methods may cheaply narrow search before exact acceptance. | Keep approximation outside authoritative acceptance unless a policy explicitly permits bounded judgment. |
| **Constraint by construction** | Work Unit boundaries and Kernel grants make invalid effect paths unavailable rather than relying on agents to remember rules. | Measure how much procedural checking can be eliminated by stronger construction. |
| **Lazy evaluation / demand-driven work** | Do not derive, fetch, instantiate, or summarize information until a consumer actually needs it. | Apply to context assembly, graph expansion, tool discovery, and observation. |
| **Materialized views** | Cached dashboards, indexes, graphs, or summaries may accelerate queries but remain rebuildable unless a guarantee proves otherwise. | Establish when materialization cost is lower than repeated derivation. |

This table is a research map, not a statement that all listed mechanisms should be
implemented.

---

## 9. Approximation and exact authority remain separate

Approximate methods may be important to efficiency because exact frontier-model
reasoning is expensive.

Examples include:

- cheap-model routing;
- System-1 judgments;
- simulations;
- heuristic search;
- probabilistic ranking;
- approximate static analysis.

The authority rule remains:

> **Approximation may guide what to inspect or propose; it does not silently become
> permission.**

A cheap probabilistic judgment can select a likely next action, but protected
effects still require the authority and verification appropriate to that effect.

This keeps approximate computing useful without forcing it into the Kernel's
authoritative semantics.

---

## 10. Context is a resource, not the system state

Model context has cost in tokens, latency, money, and attention.

The system should therefore avoid treating "everything potentially relevant" as
the default context.

Expected techniques include:

- retrieve only task-relevant facts;
- use durable state instead of reconstructing long conversations;
- pass identifiers and compact references rather than duplicated payloads;
- summarize only when a consumer needs a summary;
- reuse deterministic computation where applicability is cheap to establish;
- escalate model capability only when the residual uncertainty warrants it.

The durable system should make it possible to rebuild an agent's working context
without requiring the agent's previous conversational context to remain the source
of truth.

---

## 11. Orchestrator efficiency

The Orchestrator is expected to be the normal user-facing agent, but this should
not require the Orchestrator to perform every computation itself.

The intended pattern is:

```text
user intent
    |
    v
Orchestrator
    |
    +-- use already-known authoritative facts
    +-- request deterministic derivation where available
    +-- delegate bounded execution
    +-- call stronger reasoning only where needed
    +-- present a compact derived view back to the user
```

The Orchestrator should ideally spend model reasoning on semantic uncertainty,
tradeoffs, planning, and interaction rather than repeatedly reconstructing facts
that deterministic machinery or retained state can supply more cheaply.

This remains a later research area. The current architecture merely preserves the
separation needed to pursue it.

---

## 12. Authority machinery and optimization machinery have different failure rules

The RTK guard example illustrates a useful distinction.

A transparent output/token optimization may safely **fail open** when its failure
only means "perform the original expensive operation."

An authority boundary generally cannot.

Therefore:

```text
optimization failure
    -> lose efficiency
    -> correctness may remain intact

authority-enforcement failure
    -> potentially permit forbidden effect
    -> must satisfy the declared fail-closed contract
```

This distinction should prevent efficiency features from unnecessarily entering
the trusted computing base.

Caching, compression, command rewriting, UI projection, indexing, and other
optimizations should remain outside correctness-critical authority paths whenever
their loss can be tolerated by falling back to slower correct behavior.

---

## 13. Persistence test for proposed machinery

Before introducing a new durable subsystem or derived state, ask:

1. **What required observation or guarantee fails if this state is deleted?**
2. Can the value be recomputed from retained authoritative inputs?
3. Is recomputation actually too expensive, too slow, or impossible under a real
   requirement rather than a hypothetical preference?
4. What new invalidation, recovery, currentness, and synchronization obligations
   does persistence create?
5. Does the proposed subsystem become a second state owner?
6. Can the same benefit be obtained through a derived view or bounded cache?
7. Is measured workload evidence available?
8. If the mechanism fails, can the system safely fall back to a slower path?

The default answer need not always be "recompute." The purpose of the test is to
make persistence earn its complexity.

---

## 14. Composition levels

The same substrate should support several operating styles.

### Minimal / low-level

```text
user
  -> Kernel
      -> Work Unit
          -> shell / program / arbitrary code
```

Useful for direct control, debugging, experiments, or users who want a CLI-like
surface.

### Typical

```text
user
  <-> Orchestrator chat
          -> Kernel
              -> Work Units
                  -> agents / tools / programs
```

This is the expected ordinary experience.

### Rich

```text
user
  <-> chat + dashboards + issue views + status panes
          -> Orchestrator
          -> Observer / optional Processor / coordination machinery
          -> Kernel
              -> Work Units
```

The richer composition should not require changing the fundamental authority and
containment model of the lower levels.

---

## 15. Research still required

Important unresolved efficiency questions include:

- the measured fixed cost of an inactive Work Unit;
- the cheapest realization of durable Work Unit discovery;
- event-driven Observer design and missed-event recovery;
- polling versus event subscription costs;
- when dependency graphs outperform full recomputation;
- memoization identity, provenance, and invalidation;
- incremental and partial computation across changing repositories;
- reuse across Work Units and projects;
- negative-result and dead-end retention;
- approximate-computing error budgets;
- System-1 versus deterministic Processor boundaries;
- context-packet construction and retrieval;
- graph/topology derivation;
- scheduling and batching;
- resource-aware model routing;
- computation placement;
- backpressure;
- cache locality;
- cost attribution;
- subsystem ablation;
- whether a persistent Processor is justified on real workloads;
- whether any later correctness counterexample invalidates the processorless core.

These belong to later research rather than being silently decided by the present
baseline.

---

## 16. Constraint for future architecture work

Future proposals should distinguish three questions:

1. **Correctness necessity:** what guarantee cannot be expressed or realized without
   this addition?
2. **Efficiency value:** what measured repeated work, latency, cost, or resource use
   does this addition remove?
3. **Product convenience:** what experience does this addition make easier to
   present?

Only the first question can by itself force machinery into the minimal correctness
core.

The second can justify an optional or standard optimization after measurement.

The third can justify a derived user-facing feature without making that feature
authoritative.

This distinction is the main purpose of the efficiency architecture baseline.
