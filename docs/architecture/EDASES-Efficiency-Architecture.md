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
  - Efficiency Architecture Investigation Record

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
  - Efficiency Architecture Evidence Ledger
  - Efficiency Architecture Discriminating Experiments

implements: []
implemented_by: []
supersedes: []
superseded_by: []

last_updated: 2026-09-29
---

# EDASES Efficiency Architecture

## Current research baseline — 2026-09-29

**Experimental / Derived.** This revision transforms the frozen Stage-1 baseline into a set of discriminating architecture choices. It recommends research and evaluation conditions; it does not establish new methodology, change the Kernel/Work Unit core, or authorize a full efficiency subsystem.

The central objective remains:

> Minimize total computation, inference, state, coordination, observation, reconstruction and maintenance cost while retaining the smallest trustworthy authoritative substrate.

The useful reduction is **contract-constrained elimination of total work**. First identify the information and successful behavior that must survive; then compare complete lifecycle costs of the simplest admissible alternatives. The best mechanism depends on demand, change, applicability, retention and failure patterns. “Recompute first”, “cache”, “event-driven” and “cheap-model first” are candidate choices, not a universal ordering.

### Reading and provenance

This pass starts exactly at commit `8d158e3e82d5811e420c80cc6c9664d3ae4a6088`, with Efficiency Architecture blob `349eee3b51171a9365201eff5d2bd10d8cbfa719`. It uses the directly governing frozen Work Unit A–L, Roadmap and Phase-I Processorless Falsification. The pending authority/recovery reconciliation `ad24f856a` was not consulted or imported as accepted evidence. Currentness-dependent efficiency proposals remain conditional.

The [original body is preserved below](#historical-baseline--2026-09-28) without alteration. Where the two differ, use the current research conclusions as this document's **experimental** position; historical statements retain their provenance, not automatic present endorsement.

| Record | Purpose |
| --- | --- |
| [Investigation and reasoning](efficiency/Efficiency-Investigation.md) | Frozen blob manifest; findings F01–F10; cost models; 14 mechanism cards; hypothesis dispositions; six boundary decision points |
| [Evidence ledger](efficiency/Efficiency-Evidence.md) | 21 selected primary sources, exact supporting loci, transfer limits and excluded evidence |
| [Discriminating experiments](efficiency/Efficiency-Experiments.md) | Eight executed finite countermodels and 12 ranked proposed empirical comparisons |

The split keeps the architecture readable while preserving substantial reasoning and experimental instructions. It introduces no new component. All records remain Experimental / Derived.

## A. The retained boundary

The frozen Work Unit is a bounded Kernel-governed object; it does not intrinsically require a model, runtime process, issue, scheduler, Observer, Processor, Orchestrator or visual work graph. Its containment lifetime is independent of execution. **Sealed does not mean dormant:** internal computation may continue under surviving grants.

The efficiency design should distinguish three axes:

| Axis | Distinctions that matter |
| --- | --- |
| Information role | Authoritative state; accepted historical content; observation; reproducible derivation; proposed judgment |
| Retention | Ephemeral; bounded cache; durable materialization; information retained because a contract requires it |
| Trust | Untrusted production; checked result; scoped attestation; trusted computation |

Derived origin does not imply disposable lifetime or untrusted consumption. A computed result accepted for future reading may need retention even after its inputs disappear. A disposable cache may still be in the trusted path if its results are used unchecked. These distinctions refine the efficiency boundary without adding Kernel object types.

“Smallest” is relative to required future observations. If two histories require different future answers, collapsing them into the same surviving representation loses information. A source hash is not the source; an interpreter version name is not an available interpreter. Retain the distinctions needed by the promised contract, not automatically the full event log and not automatically only the latest snapshot. See F01/F02 and boundary B04.

## B. Proposed efficiency principles after challenge

These are evaluation principles for this experimental architecture, not Canonical invariants.

1. **Separate admissibility from economics.** Savings cannot buy a weakened authority, retention or required-progress guarantee. Compare mechanisms under the same contract.
2. **Measure marginal dormant cost.** Eliminate unnecessary per-object activity; still count retained bytes, maintenance, observation and recovery. Measure dormant population with active work held fixed.
3. **Price applicability, not just lookup.** A reused answer needs the right meaning, complete relevant inputs, checked production, required currency and authorized consumption. Establish each only to the extent the consumer requires.
4. **Exploit demand before maintaining every intermediate result.** Event dirtying, recomputation on demand, incremental repair, materialization and scheduling are independent decisions.
5. **Retain only with a stated reason and lifecycle.** Include transitive source/witness retention, invalidation, recovery, migration and reclamation. Never dispose accepted evidence merely by labeling it a cache.
6. **Test absence and wrongness separately.** Remove, corrupt, stale, restart and overload an optimization. A safe useful fallback must meet the actual successful-continuation contract.
7. **Make information reduction consumer-relative.** Exact compression, indexing, evidence selection and semantic summarization have different obligations. Preserve access to required source evidence when a packet is disposable.
8. **Keep computation identity separate from authority.** Shared bytes or proof of a fact do not grant permission to access them or act on them. Topology for scheduling is not containment authority.
9. **Budget optimization itself.** Planning, retrieval, measurement, proof checking and adaptive tuning must earn their costs. A simple threshold or direct computation remains a competitor.
10. **Evaluate correlated failure and required progress.** Many simultaneous cold reconstructions can change economics; advisory filters can suppress necessary work. Safety alone is insufficient where continuation is promised.

The strongest baseline principles survive in this qualified form. The investigation explicitly rejects stronger readings such as zero-cost dormancy, automatically cheap incremental repair, removal proving untrusted operation, or cheap-first always saving work.

## C. Economic decision model

Use a cost vector containing compute, inference, memory-time, durable-byte-time, network, energy, latency distribution, human attention and engineering/maintenance effort. Track trusted-base complexity and assurance obligations separately. Hard guarantees constrain the feasible set; a single weighted price is appropriate only for declared tradeoffs. Latency percentiles cannot be added as though they were work counts.

For a chosen additive cost dimension and a homogeneous workload:

```text
Direct: N R
Reuse:  N(L + V) + (N - H)R + B + U m + S(T) + F r + O

Reuse is cheaper only when:
H R > N(L + V) + B + U m + S(T) + F r + O
```

N counts requests; H counts truly applicable accepted hits; R is recomputation; L/V are average lookup and applicability/check cost per request; B is setup; U m is update maintenance; S(T) is retention over the horizon; F r is failure repair; O is added observation, coordination, engineering and review. Heterogeneous or shared work needs explicit per-request/shared accounting rather than this simple formula. See F03 for derivation and limits.

An executed illustrative model with the same 80% hit rate makes reuse either cheaper (570 versus 1000) or more expensive (1270 versus 1000) solely by changing validation cost. These are invented cost units. **No EDASES performance benefit is claimed.**

The first empirical question is therefore whether a real repeated result has a cheap, sound applicability boundary. A precise dependency graph that costs more than recomputation fails this test; so can a coarse snapshot key with excessive invalidation.

## D. Mechanism families and simpler competitors

The [mechanism portfolio M01–M14](efficiency/Efficiency-Investigation.md#8-candidate-mechanism-portfolio) gives necessity, economic conditions, state burden, applicability, disposability, incremental entry and falsifiers for each candidate.

| Family | Distinction / first comparison |
| --- | --- |
| Reuse and incremental computation | Direct recomputation → scoped memoization → dirty/full rebuild on demand → selected delta repair. A cache, graph and scheduler need not arrive together. |
| Durable derived state | Compare ephemeral reuse with selected materialization/checkpoints across failures and retention lifetime; test source availability and accepted-output obligations. |
| Negative results | Exact absence, formal contradiction, bounded search miss, transient failure and semantic rejection have different scope and invalidation. Compare rescan/retry before automatic pruning. |
| Computation compilation | Extract specified mechanics or specialize a specified program. Inducing a rule from repeated judgments is a separate policy/learning proposal. Compare an existing tool/table first. |
| Context and discovery | Compare direct retrieval and exact fragments with task-specific projections before semantic compression or a global tool registry. Measure evidence/tool recall and repair. |
| Observation | Compare polling, event hints, demand and hybrid reconciliation at matched observation quality. Lost irreplaceable events cannot be reconstructed from a current snapshot. |
| Placement and sharing | Compare local compute with transfer + remote lookup/check/fallback; establish permitted scope separately from computation identity. |
| Approximation and routing | Separate sound conservative abstraction, statistical estimation and heuristics. Compare risk/coverage and complete cascade cost with direct execution. |
| Scheduling and topology | Compare bounded concurrency and simple priority before a planner. Data dependencies, resource conflicts, organization and authority are different edge meanings. |
| Retention, measurement and adaptation | Begin with bounded caches, coarse counters and fixed budgets; count reclamation, pinned ancestry and optimizer overhead before generalizing. |

Established correspondences go beyond the original list: build-system rebuilder/scheduler separation; demand-driven incremental computation; database materialization/adaptive indexing; lineage and checkpointing; formal negative knowledge; proof-producing/checking separation; selective prediction; abstract interpretation; online investment; and metareasoning. Their exact limits are in the evidence ledger. None supplies an EDASES implementation or a transferable performance multiplier by analogy alone.

## E. Corrections that materially constrain future design

**Applicability is not one freshness bit.** Complete positive and negative domains, interpretation, production correctness, currency and authorized use are different. Hashing all included records does not prove that no additional record exists. Revalidation must meet the selected consumption/commitment contract; this pass does not invent that contract.

**Event-driven is not reconciliation-free.** Demand determines whether a result is needed; notifications indicate change; direct reads or reconciliation may establish a current view. If every historical event is required, coalescing may be invalid. If only the final output matters, repairing every event can be wasteful.

**Reconstructible is not economically free to lose.** Simultaneous misses after shared failure can overload sources and trigger duplicate work. Durable materialization, coalesced/throttled rebuild, selective warming and additional capacity compete. Only a genuine required deadline plus a defensible lower bound creates a potential correctness crossing.

**A rich UI can remain derived, but its unique inputs cannot vanish.** User acceptances, commitments and irreplaceable observations captured through that UI need retained representation under the governing contract. Display projections remain rebuildable when their required sources survive.

**Approximation can affect progress without authorizing effects.** A heuristic that hides the only successful path may violate a continuation guarantee even when the exact guard rejects every unsafe effect. Coverage and meaningful fallback matter.

## F. Processorless result and stop conditions

No new necessity for a persistent first-class Processor was established under the frozen Phase-I comparator. Trusted calculation or sound checking, complete relevant inputs, accepted information and the declared currentness/recovery mechanism remain necessary. This pass neither eliminates those obligations nor proves all future consumers reducible.

Six [boundary cases B01–B06](efficiency/Efficiency-Investigation.md#10-architectural-decision-points-stop-these-branches-here) stop speculative design:

- stale or rolled-back authority/currentness evidence;
- an unknown external effect after a lost reply;
- a mandatory cold-recovery deadline incompatible with a defensible resource/work bound;
- irreplaceable history or accepted content lost through compaction/disposition;
- nominal telemetry required for exact quota/billing enforcement;
- a required successful path suppressed by heuristic routing.

These cases require a governing contract or a separate architectural decision. None by itself entails a Processor, a new Kernel primitive, a global freshness service or a replacement core. Immutable derivation economics can be investigated while those dependencies remain isolated.

## G. Prioritized next investigations and intentionally unbuilt machinery

Begin with **X01 workload/observer-cost inventory**, **X02 applicability versus recomputation**, **X03 demand/full rebuild versus incrementality**, and **X04 cold recovery/retention closure**. These test whether a generalized efficiency subsystem is justified at all. X05 task-relative context/tool discovery is useful once defensible cases exist. X06–X12 cover negative reuse, specialization, observation, sharing, routing, scheduling and adaptation as their repeated costs become evident.

The [protocol](efficiency/Efficiency-Experiments.md) fixes comparators, mutations, measurements, confounds, falsifiers and stopping conditions. Eight small countermodels ran in this pass; all real-system experiments remain proposed.

Keep a universal semantic cache, comprehensive dependency engine, global tool registry, learned scheduler/router, generalized context compressor and large telemetry system intentionally unbuilt until simpler comparisons justify them. Candidate missing topics for existing roadmap phases are applicability economics, retention/reclamation, correlated reconstruction, bounded optimization effort, and progress/coverage under heuristics. They add research questions, not components or a changed phase order.

## H. Confidence and review handoff

**WHY:** the baseline now distinguishes information, retention and trust; challenges its strongest hypotheses; specifies complete cost comparisons; and offers bounded next investigations. **WHAT:** the frozen packet, 21 primary-source entries, F01–F10, M01–M14, B01–B06 and eight reproducible finite countermodels. **HOW CERTAIN:** evidence-based architecture synthesis with conditional toy proofs, not validated implementation economics. **WHAT-NOT-TESTED:** production workloads, actual model routing, real fault injection, independent adversarial review, implementation refinement, or the pending authority/recovery reconciliation. Separate review is required before experimental conclusions become Canonical direction.

---

# Historical baseline — 2026-09-28

The following body is retained verbatim from blob `349eee3b51171a9365201eff5d2bd10d8cbfa719`. Its original metadata identified it as Experimental / Derived; that authority level is unchanged. Consult the current sections above for the present experimental position.



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
