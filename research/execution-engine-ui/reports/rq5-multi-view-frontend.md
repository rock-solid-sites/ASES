# RQ5 — Multi-view frontend

## Question

Can one frontend expose four distinct views over the same underlying data without the views fighting each other architecturally? The four views are: (1) an **execution view** showing workflow/execution state (what is running, what is pending); (2) a **state view** showing artefact lifecycle states derived from statecharts; (3) an **evidence view** showing observations, findings, and decisions linked to artefacts; and (4) a **version history view** showing version chains, supersession, and provenance.

## Scope

**Investigated:**
- Whether all four views can read from a single shared data model without each requiring a different query shape or data representation, drawing on the storage options assessed in RQ4 (Neo4j, Memgraph, Kuzu, SQLite+edge tables, PostgreSQL+pgvector) and the graph-rendering frameworks assessed in RQ1 (React Flow, Cytoscape, AntV X6, JointJS).
- Whether the views architecturally conflict — in particular the tension between the execution view's need for real-time, mutable updates and the version history view's need for immutable snapshots.
- Established multi-view frontend architectures (CQRS, event sourcing, materialized views) and their trade-offs, with authoritative sources.
- How statechart-driven state (XState, per RQ2; SCXML, per RQ2) would flow into the views, and whether each view needs its own state management.
- Whether serving four views from one data layer creates query contention, and whether each view needs its own optimized read model.

**Excluded:**
- Hands-on prototyping or benchmarking of a multi-view frontend (this is a literature/evidence review; no frontend code was executed).
- Choosing or recommending a specific RQ1 graph framework, RQ4 storage engine, or RQ3 execution engine (those are the remit of sibling reports; this report treats them as evidence only).
- Any implementation proposal (forbidden by research constraints).
- Detailed quantification of projection-rebuild cost or eventual-consistency lag for the EDASES workload (no EDASES workload shape is specified).

## Evidence

### 1. Shared data layer — one graph model serves all four views

- **Observation (RQ4):** All five storage candidates can represent artefacts, versions, evidence, provenance, and supersession as first-class graph constructs. Neo4j and Memgraph use the property graph model where artefacts are labelled nodes, versions are `State` nodes hung off an immutable entity (entity–state pattern), evidence is a node linked by typed edges, provenance is a chain of typed relationships, and supersession is a typed edge (rq4-neo4j.md §2–§6; rq4-memgraph.md §2–§6). Kuzu, SQLite+edge tables, and PostgreSQL+pgvector represent the same five concerns via node/rel tables, edge tables, and recursive CTEs (rq4-kuzu.md F1–F5; rq4-sqlite.md F1–F5; rq4-pgvector.md §2–§6).
- **Observation (RQ4):** The version-history concern is modelled as *immutable, append-only* version nodes in the property-graph candidates — the entity–state pattern keeps the entity immutable and adds one `State` node per version, maintaining a `LATEST`/chain pointer; history is not overwritten when state advances (rq4-neo4j.md §2; rq4-memgraph.md §2).
- **Interpretation:** Because the shared store already holds artefacts, their versions, their evidence links, their provenance, and their supersession as one connected graph, each of the four views is a *projection* (a filtered query or traversal) over that same graph rather than a separate data store. The execution view reads running/pending execution state; the state view reads each artefact's current lifecycle-state property; the evidence view traverses artefact→evidence edges; the version view traverses version/supersession/provenance edges. All four are expressible against the single RQ4 graph model. **No separate data shape is required per view** — the graph is shape-agnostic and each view selects its subgraph.
- **Observation (RQ1):** All four graph-rendering candidates are *view layers* that consume `nodes`/`edges` props and explicitly compose with an external state store rather than owning the data model. React Flow documents composition with Zustand/Redux/Recoil/Jotai and is feasible with XState (rq1-react-flow.md §7); Cytoscape.js is a library the host syncs via `add`/`remove`/`json` (rq1-cytoscape.md §7); AntV X6 carries its own MVC model but requires explicit glue to an external store (rq1-antv-x6.md §7); JointJS separates model (`dia.Graph`) from view (`dia.Paper`) and can be driven externally via `@joint/react` (rq1-jointjs.md §7).
- **Interpretation:** The choice of RQ1 renderer is *orthogonal* to the multi-view question. Any of the four can render any of the four views as a projection, because none of them imposes its own data model on the application. The multi-view architecture therefore does not depend on, or conflict with, the RQ1 framework choice.

### 2. View isolation — the real-time/immutable tension is resolvable, not inherent

- **Observation:** The execution view needs real-time, mutable state (what is running/pending now), whereas the version history view needs immutable snapshots (rq5 task brief). These pull in opposite directions on mutability.
- **Observation (RQ4):** The property-graph versioning pattern already separates *immutable history* (append-only `State` nodes) from *current state* (a derived `LATEST` pointer) — history is never overwritten when state advances (rq4-neo4j.md §2; rq4-memgraph.md §2).
- **Observation (authoritative, CQRS):** CQRS separates the model that updates information from the model used to read it; "for many problems... having the same conceptual model for commands and queries leads to a more complex model that does neither well" (martinfowler.com/bliki/CQRS.html). A single write store can project into *multiple* read models, each optimized for a different query pattern (sysdesai.com, "CQRS Read Models").
- **Observation (authoritative, event sourcing):** Event sourcing captures "all changes to an application state as a sequence of events" stored append-only; current state is *derived* by replaying the event log, so the log is the immutable record and current state is a computed projection (martinfowler.com/eaaDev/EventSourcing.html; arc42 Quality Model, "Event Sourcing").
- **Interpretation:** The four views do **not** inherently fight if the data layer is structured as a shared *write model* (the graph / event log) with *separate read-model projections* per view (CQRS), and the real-time-vs-immutable tension is resolved by event sourcing: the underlying store is append-only, the version view reads the immutable history, and the execution/state views read the *derived current* projection. Because the version view reads history that is never mutated, the execution view's frequent mutations cannot corrupt it. The conflict is a modelling choice, not a law of the architecture.
- **Interpretation (labelled assumption):** Whether EDASES should adopt full event sourcing (an explicit event log as system of record) versus rely on the lighter "graph with immutable version nodes" already present in the RQ4 candidates is an open design decision; both satisfy the "immutable history + mutable current" requirement. Treated as an assumption because the EDASES write-path is not specified in this review.

### 3. Existing multi-view architectures — CQRS, event sourcing, materialized views

- **Observation (authoritative, Materialized View):** The Materialized View pattern "generate[s] prepopulated views over the data in one or more data stores when the data isn't ideally formatted for required query operations"; the read model of a CQRS implementation "can contain materialized views of the write model data" (learn.microsoft.com/azure/architecture/patterns/materialized-view; learn.microsoft.com/azure/architecture/patterns/cqrs).
- **Observation (authoritative, CQRS + Event Sourcing combined):** Microsoft's CQRS guidance states that combining CQRS with event sourcing makes "the event store... the write model and the single source of truth" and "the read model generates materialized views from these events... in a highly denormalized form," with the trade-off of *eventual consistency* (updates to the read store may lag) and *increased complexity* (learn.microsoft.com/azure/architecture/patterns/cqrs, "Combining event sourcing and CQRS").
- **Observation (CQRS read models):** A single write store can project into multiple read models — "an order detail model, an orders-by-customer model, a product sales model, and an Elasticsearch index" — each kept up to date by subscribing to the same domain events; read models are *derivable* and "can always be rebuilt by replaying events from the beginning" (sysdesai.com, "CQRS Read Models").
- **Interpretation:** The four-view requirement maps directly onto the CQRS + materialized-view pattern: one write model (the graph / event log) projects into four read models (execution, state, evidence, version), each shaped for its access pattern. This is a well-established, documented architecture, not a novel construct. The documented trade-offs (eventual consistency, projection-rebuild cost, added complexity) are the costs EDASES would pay for view isolation.

### 4. State synchronization — XState state flows into views as a persisted projection

- **Observation (RQ2):** XState is actor-based: each artefact maps to one `createActor(machine)` instance with its own isolated state; `actor.getSnapshot()` returns `state.value` (active state) and `state.context`; `getPersistedSnapshot()` returns a JSON-serializable object storable in any backend; the Inspect API streams `@xstate.snapshot` and `@xstate.event` for every actor (rq2-xstate.md §1, §2, §5).
- **Observation (RQ2):** XState persistence is storage-agnostic (localStorage, IndexedDB, MongoDB, PostgreSQL, Redis listed) and the snapshot is a plain object (rq2-xstate.md §5). SCXML interpreters are likewise instantiated per-document with independent state, though full-state persistence is partial/implementation-specific (rq2-scxml.md §1, §5).
- **Observation (RQ1):** React Flow's state-management guide shows composition with Zustand/Redux/Recoil/Jotai; a single shared store feeding multiple view components is the documented React pattern (rq1-react-flow.md §7). JointJS's `@joint/react` uses `useSyncExternalStore` so "diagram state is React state" (rq1-jointjs.md §7).
- **Interpretation:** The state view reads each artefact's XState snapshot (persisted into the shared graph as a lifecycle-state property, or exposed via the Inspect API). The execution view reads execution-engine state (RQ3). Both are *projections* of external state into the shared store; the views do **not** each need their own state-management system. A single shared store (holding the graph plus live execution/lifecycle state) can feed all four view components, each rendering a selector/projection — the Flux/Redux "one store, many views" pattern. The execution view's real-time need is met by the store updating from an event stream (see §5), not by a separate state system.
- **Interpretation (labelled assumption):** That XState actor snapshots are persisted into the same shared graph store (rather than a separate XState store) is the natural integration, but the exact persistence wiring (XState snapshot → graph node property) is an integration detail not evidenced in a concrete EDASES example; treated as an assumption.

### 5. Performance and contention — separate read models remove the contention

- **Observation (RQ4):** Graph stores handle the relevant traversals well — Neo4j's index-free adjacency gives O(k) local traversal (rq4-neo4j.md §7); Memgraph's in-memory architecture makes multi-hop traversal cheap (rq4-memgraph.md §7); Kuzu's columnar/vectorized engine is fast on analytical traversals (rq4-kuzu.md E5). Relational candidates handle shallow traversals adequately but degrade on deep recursive CTEs (rq4-pgvector.md §9; rq4-sqlite.md E4).
- **Observation (authoritative, CQRS scaling):** CQRS lets reads and writes "scale independently — you can add read replicas without touching the write path"; read models are not a cache but a source of truth for reads, rebuilt from events (sysdesai.com, "CQRS Read Models"). The cost is eventual consistency (milliseconds-to-seconds lag) and projection-rebuild effort (learn.microsoft.com/azure/architecture/patterns/cqrs).
- **Observation (RQ3, real-time source):** The execution engines emit state that can drive real-time views — Temporal exposes Signals/Queries and an event history that is the source of truth for execution state (rq3-temporal.md §3); Burr ships a tracking server modelling projects/applications/steps with a UI (rq3-burr.md E6). XState's Inspect API streams snapshot/event updates (rq2-xstate.md §2).
- **Interpretation:** Serving four views from one data layer *would* create contention only if all four queried the same single model with conflicting access patterns (high-frequency execution writes vs read-only version reads). CQRS removes this by giving each view its own read model (materialized projection) updated from the event stream; the write model is updated once and projections update asynchronously, isolating the execution view's churn from the version view's stable reads. **Each view benefits from its own optimized read model for performance**, at the cost of eventual consistency and rebuild complexity — a documented trade-off, not a blocker.
- **Interpretation (labelled assumption):** Real-time push to the execution/state views can be satisfied by an *application-level event bus* (the execution engine and XState emit events → WebSocket to the frontend) independent of the storage engine's own change-feed capability. This decouples the real-time requirement from storage choice. Embedded stores (Kuzu, SQLite) lack a built-in change feed per RQ4 (rq4-kuzu.md E3; rq4-sqlite.md E8), so an application-level event stream is the more portable real-time mechanism; whether a specific storage engine's CDC/streaming (e.g., Neo4j/Memgraph streaming) is used instead is a deployment choice, not an architectural necessity.

## Findings

1. **A single shared data layer can serve all four views.** The RQ4 graph model holds artefacts, versions, evidence, provenance, and supersession as one connected graph; each view is a projection/traversal over that same graph, not a separate store (Evidence §1). No per-view data shape is required.
2. **The views do not inherently fight.** The real-time/immutable tension is resolved by separating immutable history (append-only version nodes, already present in the RQ4 candidates) from a derived current-state projection, exactly the event-sourcing/CQRS separation (Evidence §2, §3).
3. **The multi-view requirement is a known, documented architecture.** CQRS + materialized views + event sourcing directly support "one write model, N read models," with documented trade-offs (eventual consistency, projection-rebuild cost, added complexity) (Evidence §3).
4. **Statechart state flows into views as a persisted projection, not a separate state system.** XState actor snapshots are JSON-serializable and storage-agnostic; a single shared store can feed all four view components via per-view selectors (Evidence §4). The RQ1 renderers all compose with an external store, so the multi-view architecture is orthogonal to the RQ1 framework choice.
5. **Contention is avoidable via per-view read models.** CQRS isolates the execution view's high-frequency updates from the version view's stable reads by giving each view its own materialized projection updated from the event stream (Evidence §5). Real-time push is portable via an application-level event bus, independent of storage choice.
6. **The RQ1 framework choice is orthogonal to the multi-view question.** All four RQ1 candidates are view layers that consume nodes/edges and compose with external state; none imposes a data model that would conflict with the four-view projection approach (Evidence §1).

## Rejected options

- **One monolithic shared read model serving all four views directly (as the only mechanism).** Rejected because it concentrates the execution view's high-frequency mutable reads/writes and the version view's immutable reads on the same model, creating the exact contention the question asks about; CQRS read models are the documented mitigation (Evidence §3, §5). This is a finding about the architecture, not a prohibition on a shared model during early/simple phases.
- **Treating the real-time requirement as forcing a specific storage engine.** Rejected: an application-level event bus (execution engine + XState emit events → WebSocket) satisfies real-time push independent of storage; embedded stores (Kuzu, SQLite) lack built-in change feeds yet remain viable via the event bus (Evidence §5). Storage choice is therefore not dictated by the multi-view requirement.
- **Assuming each view needs its own state-management system.** Rejected: the RQ1 evidence shows renderers compose with a single external store, and XState snapshots are persistable into the shared graph; one store with per-view selectors suffices (Evidence §4).
- **Assuming the four views require four different data stores.** Rejected: the RQ4 evidence shows one graph store holds all five concerns; the views are projections, not separate databases (Evidence §1).

## Unknowns

- **U1.** Whether EDASES adopts full event sourcing (explicit event log as system of record) or relies on the "graph with immutable version nodes" already present in the RQ4 candidates. Both satisfy immutable-history + mutable-current, but the write-path and projection-rebuild story differ. Open design decision (Evidence §2, assumption).
- **U2.** The exact persistence wiring that projects XState actor snapshots into the shared graph store (snapshot → artefact lifecycle-state property). No concrete EDASES example was found; treated as an assumption (Evidence §4).
- **U3.** Eventual-consistency lag tolerance of the EDASES UI — CQRS read models lag the write model by milliseconds-to-seconds (learn.microsoft.com/azure/architecture/patterns/cqrs); whether the execution view can tolerate that lag, or needs read-your-own-writes/optimistic-UI handling, is a workload question not answerable here.
- **U4.** Projection-rebuild cost and frequency for four views over the EDASES artefact graph — depends on graph size and update rate, neither specified (Evidence §3, §5).
- **U5.** Whether the execution engine (RQ3) and XState (RQ2) emit events in a form that a single unified event bus can carry to all four views, or whether two separate streams (execution + lifecycle) are needed. The RQ3/RQ2 evidence shows both emit state, but a unified bus design is not evidenced.
- **U6.** The precise contention behaviour if a *single* shared model (no separate read models) is used at EDASES scale — depends on artefact count and execution-update frequency, both unspecified.

## Confidence

**Medium-High.**

- **High** for the structural claims: (a) the RQ4 graph model holds all five concerns as one graph, so the four views are projections, not separate stores (directly from RQ4 sibling reports); (b) the RQ1 renderers are view layers that compose with external state and do not impose a data model (directly from RQ1 sibling reports); (c) XState actor snapshots are JSON-serializable and persistable (directly from RQ2); (d) CQRS/event-sourcing/materialized-view support "one write model, N read models" and resolve the real-time/immutable tension (authoritative sources: Martin Fowler, Microsoft Azure, arc42).
- **Medium** for the operational claims: (a) the exact persistence wiring of XState→graph and the choice between full event sourcing vs immutable-version-nodes is an open design decision (U1, U2); (b) eventual-consistency lag tolerance and projection-rebuild cost are workload-dependent and unquantified (U3, U4); (c) the unified-event-bus design is inferred from RQ2/RQ3 emit patterns, not evidenced as a concrete EDASES integration (U5).

The core research question — *can one frontend expose four distinct views over the same data without the views fighting each other architecturally?* — is answered with reasonable confidence: **yes**, provided the data layer is structured as a shared write model with per-view read-model projections (CQRS) and the real-time/immutable tension is resolved by separating immutable history from a derived current-state projection (event sourcing). The four views are projections over the single RQ4 graph, the RQ1 renderers are compatible with this, and XState state flows in as a persisted projection. The residual uncertainty is operational (consistency lag, rebuild cost, integration wiring), not architectural.

## References

Sibling reports (in this directory):
- rq1-react-flow.md — React Flow composition with external state (§7)
- rq1-cytoscape.md — Cytoscape.js as a syncable library (§7)
- rq1-antv-x6.md — AntV X6 MVC model + external store glue (§7)
- rq1-jointjs.md — JointJS model/view separation, `@joint/react` (§7)
- rq2-xstate.md — XState actors, getSnapshot, getPersistedSnapshot, Inspect API (§1, §2, §5)
- rq2-scxml.md — SCXML per-document interpreters, persistence limitation (§1, §5)
- rq3-temporal.md — Temporal event history as execution-state source of truth (§3)
- rq3-burr.md — Burr tracking server (projects/applications/steps) + UI (E6)
- rq4-neo4j.md — property graph, entity–state versioning, immutable version nodes (§2–§6)
- rq4-memgraph.md — property graph, entity–state versioning (§2–§6)
- rq4-kuzu.md — structured property graph, embedded / no change feed (E3, F1–F5)
- rq4-sqlite.md — edge tables + recursive CTEs, embedded / no change feed (E8, F1–F5)
- rq4-pgvector.md — relational graph simulation, recursive CTEs (§2–§9)

External / authoritative:
- Martin Fowler, "CQRS" — https://martinfowler.com/bliki/CQRS.html
- Martin Fowler, "Command Query Separation" — https://martinfowler.com/bliki/CommandQuerySeparation.html
- Martin Fowler, "Event Sourcing" — https://martinfowler.com/eaaDev/EventSourcing.html
- arc42 Quality Model, "Event Sourcing" — https://quality.arc42.org/approaches/event-sourcing
- Microsoft Azure Architecture Center, "CQRS pattern" (incl. combining with event sourcing) — https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs
- Microsoft Azure Architecture Center, "Materialized View pattern" — https://learn.microsoft.com/en-us/azure/architecture/patterns/materialized-view
- SysDesAi, "CQRS Read Models for Performance" (single write store → multiple read models, eventual consistency) — https://www.sysdesai.com/learn/performance-scalability/cqrs-read-models
