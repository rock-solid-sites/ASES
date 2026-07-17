# Research Synthesis: Execution-Engine UI

## Executive summary

Eighteen research reports were reviewed across seven research questions (RQ1–RQ7) bearing on seven hypotheses (H1–H7). The evidence supports the following overall picture:

**Well-supported:** Graph databases naturally represent artefacts, versions, evidence, provenance, and supersession (H7). Existing graph UI libraries can render engineering artefacts with low-to-moderate customization (H5). Existing statechart libraries, particularly XState, can model independent artefact lifecycles with full hierarchy, persistence, and inspection (H6). Explicit provenance is supported as a recovery substrate by adjacent-domain evidence (H3). A single graph can serve multiple views via CQRS/event-sourcing patterns (H4).

**Weakly-supported:** Artefacts as a better primary abstraction than repositories (H1) — the evidence shows artefacts are representable and align with existing methodology vocabularies, but no report directly compares artefact-centric vs repository-centric architectures. Versioned artefacts reducing context requirements for zero-context agents (H2) — strong analogy from workflow systems and HCI research, but direct LLM-agent evidence is absent.

**Key uncertainty:** The gap between "can represent" and "is sufficient at scale" persists across H5, H6, and H7 — no report provides independent benchmarks at the 5,000-node/artefact target with realistic complexity.

---

## Hypothesis assessment

### H1: Artefacts as primary abstraction

**Confidence: Medium**

**Evidence for:**
- All four RQ1 reports (rq1-react-flow.md, rq1-cytoscape.md, rq1-antv-x6.md, rq1-jointjs.md) confirm that graph frameworks can represent engineering artefacts (nodes with rich content, metadata, status indicators) with low-to-moderate customization. Nodes are arbitrary components (React Flow), SVG/HTML overlays (Cytoscape), or custom shapes (AntV X6, JointJS).
- All five RQ4 reports (rq4-neo4j.md, rq4-memgraph.md, rq4-kuzu.md, rq4-pgvector.md, rq4-sqlite.md) demonstrate that artefacts map naturally to graph nodes with properties, without excessive schema complexity.
- RQ7 (rq7-existing-methodologies.md) shows that all five existing methodologies examined — SEMAT Essence, SPEM, ArchiMate, OpenProject, Jira — already model persistent "things we produce/track" as first-class entities (alphas, work products, elements, work packages, issues). EDASES's artefact concept is not novel at the type level; it aligns with established vocabulary (rq7-existing-methodologies.md F1, F2).

**Evidence against / gaps:**
- No report directly compares artefact-centric vs repository-centric architectures. The hypothesis asserts artefacts are *better* than repositories, but the evidence only shows artefacts are *representable* and *aligned with existing practice*.
- RQ3 reports (rq3-temporal.md, rq3-camunda.md, rq3-langgraph.md, rq3-burr.md) reveal that execution engines (Temporal, Camunda, LangGraph, Burr) all impose their own lifecycle/state models, suggesting that "artefact as primary abstraction" must contend with engines that want to own the lifecycle frame.

**Verdict:** The hypothesis is plausible and consistent with existing practice, but the comparative claim ("better than repositories") is unsupported. The evidence supports "artefacts are a viable and well-precedented primary abstraction."

---

### H2: Versioned artefacts and context requirements for zero-context agents

**Confidence: Medium**

**Evidence for:**
- RQ6 (rq6-artefact-recovery.md) provides the strongest evidence. Workflow provenance systems recover from structured state/checkpoints without replay, yielding "much shorter re-execution times" (rq6-artefact-recovery.md E1). Mylyn's field study with 99 developers demonstrated that persisting artefact-level context supports interrupted-task resumption (rq6-artefact-recovery.md E2). HCI research shows external cues reduce resumption lag (rq6-artefact-recovery.md E3).
- RQ6 E6 documents the failure mode where context compaction drops the premise of a rejected decision, causing agents to re-propose the same rejected option. Externalised artefact/decision state prevents this (rq6-artefact-recovery.md E6).
- RQ2 (rq2-xstate.md) confirms versioned definitions can coexist at runtime: v1 and v2 actors run simultaneously from different machine definitions (rq2-xstate.md §3). RQ4 reports show entity-state versioning patterns are natural in graph databases (rq4-neo4j.md §2, rq4-memgraph.md §2).

**Evidence against / gaps:**
- RQ6 explicitly states: "No large-scale study was found that gives an LLM agent *artefact history with provenance and no conversation* and measures resume success vs. a conversation-history control" (rq6-artefact-recovery.md Unknowns). The claim is supported by analogy, not direct evidence.
- Current LLM-agent recovery systems (LangGraph, Temporal) bundle conversation history into persisted state — they test state-replay, not the artefact-vs-conversation contrast (rq6-artefact-recovery.md E4, F4).
- The optimal provenance granularity for recovery is unknown: too little yields shallow recovery; too much rivals conversation token cost (rq6-artefact-recovery.md Unknowns).

**Verdict:** Well-motivated by workflow/HCI analogy. The predicted efficiency gain (fewer tokens, faster resume) is plausible but unvalidated for LLM agents specifically. RQ6's designed experiment (Appendix) would convert this from Medium to High confidence if executed.

---

### H3: Explicit provenance improves interruption recovery

**Confidence: Medium-High**

**Evidence for:**
- RQ6 (rq6-artefact-recovery.md) is the primary source. Workflow provenance-based recovery is an established, evaluated technique yielding shorter re-execution times than replay (rq6-artefact-recovery.md E1). The Mylyn field study demonstrates artefact-context-based resumption for human engineers (rq6-artefact-recovery.md E2). HCI research confirms external cues aid recovery while internal/conversational memory is fragile (rq6-artefact-recovery.md E3).
- RQ6 E5 (Vispute & Kadam, 2026) formalises the distinction between computational state and reasoning provenance, arguing provenance "cannot in general be faithfully reconstructed from computational state" (rq6-artefact-recovery.md E5). This means provenance is a distinct, non-reconstructable layer — if absent, it is lost.
- RQ6 E8 ("Workflow as Knowledge," 2026) argues for retaining typed objects and relations beyond execution, consistent with EDASES's "reasoning as primary artefact" stance (rq6-artefact-recovery.md E8).
- RQ7 (rq7-existing-methodologies.md) independently confirms the gap: none of the five existing methodologies provides first-class PROV-style provenance, identifying this as EDASES's primary novel contribution (rq7-existing-methodologies.md F4).

**Evidence against / gaps:**
- The provenance community's core assumption (provenance aids trust/reuse) is "under-studied" empirically (rq6-artefact-recovery.md E7, citing Nguyen et al. 2011).
- Direct LLM-agent validation of artefact-only recovery (conversation excluded) is still emerging (rq6-artefact-recovery.md F4).
- Dynamic-environment recovery — whether static artefact snapshots suffice when the environment evolves during interruption — is untested (rq6-artefact-recovery.md Unknowns).

**Verdict:** Strong support from adjacent domains (workflow systems, HCI, emerging reasoning-provenance research). The gap identified in RQ7 (no existing methodology provides this) strengthens the case that provenance is a genuine, unmet need rather than a reinvention. Direct agent-level validation is the remaining gap.

---

### H4: One graph for execution, reasoning, version history

**Confidence: Medium-High**

**Evidence for:**
- RQ5 (rq5-multi-view-frontend.md) directly addresses this. All five RQ4 storage candidates can represent artefacts, versions, evidence, provenance, and supersession as one connected graph; each view is a projection over that graph, not a separate store (rq5-multi-view-frontend.md §1, Finding 1).
- RQ5 shows the real-time/immutable tension is resolvable via CQRS + event sourcing: immutable history (append-only version nodes) is separated from derived current-state projections (rq5-multi-view-frontend.md §2, §3). Martin Fowler's CQRS and event sourcing patterns are cited as authoritative support.
- RQ5 Finding 6 confirms the RQ1 framework choice is orthogonal — all four graph renderers (React Flow, Cytoscape, AntV X6, JointJS) are view layers that compose with external state (rq5-multi-view-frontend.md §1).
- RQ4 reports confirm graph databases handle the relevant traversals: Neo4j's index-free adjacency gives O(k) local traversal (rq4-neo4j.md §7); Memgraph's in-memory architecture makes multi-hop traversal cheap (rq4-memgraph.md §7).

**Evidence against / gaps:**
- The "without becoming unusable" clause is not directly benchmarked. No report measures query performance or UI responsiveness with all four views active simultaneously over a realistic artefact graph.
- CQRS adds eventual-consistency lag (milliseconds to seconds) and projection-rebuild cost; whether the execution view can tolerate this lag is unknown (rq5-multi-view-frontend.md U3).
- Whether EDASES adopts full event sourcing vs the lighter "graph with immutable version nodes" is an open design decision (rq5-multi-view-frontend.md U1).

**Verdict:** The architectural claim (one graph can serve all four views) is well-supported by the CQRS/event-sourcing evidence and by the RQ4 modelling findings. The "without becoming unusable" performance claim is plausible but unbenchmarked.

---

### H5: Existing graph UI libraries are sufficient

**Confidence: Medium-High**

**Evidence for:**
- **React Flow** (rq1-react-flow.md): 37.6k GitHub stars, 8.59M weekly npm installs, MIT licence. Nodes are arbitrary React components — rich artefact content requires only ordinary component authoring. Virtualization via `onlyRenderVisibleElements` is a built-in first-class prop. Sub Flows provide hierarchical support. Strong composition with external state (Zustand/Redux/XState documented or feasible) (rq1-react-flow.md Findings).
- **AntV X6** (rq1-antv-x6.md): SVG/HTML/React/Vue/Angular nodes, native virtual rendering (`virtual: true`), native compound/hierarchical graphs with expand/collapse. Documented ~2k-node benchmark at 60fps with virtualization. Corporate backing (Ant Group), active releases (v3.1.7, March 2026) (rq1-antv-x6.md Findings).
- **JointJS** (rq1-jointjs.md): SVG/foreignObject/HTML-overlay nodes, first-class embedding/hierarchy, viewport virtualization in open-source core (`viewport()`, `viewManagement`), turnkey `virtualRendering` in commercial JointJS+. Documented 11k DOM nodes smooth untuned, 100k with virtualization. `@joint/react` integration with `useSyncExternalStore` (rq1-jointjs.md Findings).
- **Cytoscape.js** (rq1-cytoscape.md): ~11.1k stars, actively maintained (v3.34.0). Compound nodes for hierarchy. HTML-overlay extensions for rich content. WebGL renderer preview. Tested at 6k–20k elements (rq1-cytoscape.md Findings).

**Evidence against / gaps:**
- No report provides an independent benchmark at 5,000+ nodes with realistic (complex React/HTML) artefact node content. The closest figures: AntV X6 at ~2k nodes (simple cells); JointJS at 11k nodes (light cards); Cytoscape.js at 6k (biology datasets); React Flow has no official 5k+ benchmark (rq1-antv-x6.md, rq1-jointjs.md, rq1-cytoscape.md, rq1-react-flow.md).
- Cytoscape.js lacks native viewport virtualization — it must be built at the application layer (rq1-cytoscape.md Finding 3).
- Rich interactive node content in Cytoscape.js requires HTML-overlay extensions with ongoing canvas↔DOM synchronisation — not zero-effort (rq1-cytoscape.md Finding 1).

**Verdict:** The four libraries collectively demonstrate that existing graph UI libraries can represent engineering artefacts and their relationships. React Flow and AntV X6 are the strongest candidates (native virtualization, flexible node content, active maintenance). The gap is quantitative: no independent benchmark at the target scale with realistic node complexity.

---

### H6: Existing statechart libraries are sufficient

**Confidence: High**

**Evidence for:**
- **XState v5** (rq2-xstate.md): Actor-based model maps directly to "one actor per artefact." Full hierarchy (nested/compound, parallel, history states). Strong inspection via `getSnapshot()`, Inspect API, XState DevTools (time-travel), Stately Studio (visual, collaborative, no-code editor). Built-in persistence (`getPersistedSnapshot()` → JSON → any store). Deep persistence of invoked/spawned actors in v5. Clean composition: XState is a library, not a lifecycle-owning framework; it composes with separate workflow engines via the actor model (rq2-xstate.md Findings).
- **SCXML** (rq2-scxml.md): W3C standard with native hierarchy (compound, parallel, history states). Per-document interpreter model supports independent artefact lifecycles. Runtime inspection available in all major engines. However: the ecosystem is "stable-but-stale" — fragmented, mostly unmaintained implementations, overshadowed by XState for new web work (rq2-scxml.md Finding 7).

**Evidence against / gaps:**
- No official benchmark of 5,000+ concurrent XState actors exists; feasibility is inferred from architecture, not measured (rq2-xstate.md Unknowns).
- Persisted-snapshot compatibility across definition changes is a known hazard, mitigated by migrate-on-load (`xstate-migrate`) but not a built-in guarantee (rq2-xstate.md §3).
- SCXML's full-state persistence is not standardized and has documented hard limitations around serializing embedded script-engine datamodels (rq2-scxml.md §5).

**Verdict:** XState v5 is a strong, well-documented answer to the statechart question. It provides independent artefact lifecycles, full hierarchy, inspection, persistence, and clean composition. SCXML adds standards credibility but its ecosystem weakness makes it a secondary option. The hypothesis is well-supported.

---

### H7: Existing graph databases model the relationships naturally

**Confidence: High for the property-graph model; Medium for product viability.** The property-graph model (Neo4j, Memgraph) demonstrably represents all five concerns with low schema complexity. However, one of the five investigated products (Kuzu) is archived with the team acqui-hired, and another (Memgraph) uses BSL source-available licensing — product viability is qualified, not uniform.

**Evidence for:**
- **Neo4j** (rq4-neo4j.md): Property graph model with schema-optional nodes/labels/relationships. Official entity–state versioning pattern documented in Neo4j's own data-modelling guide. Provenance chains via typed relationship traversals in one Cypher clause. Supersession as a typed directed edge. Schema complexity remains low — the only recurring extra structure is the version `State` node + `LATEST` pointer (rq4-neo4j.md Findings).
- **Memgraph** (rq4-memgraph.md): Structurally identical modelling to Neo4j (same property graph model, openCypher). In-memory architecture gives performance advantage for multi-hop traversals. Schema-optional, same entity–state pattern transfers (rq4-memgraph.md Findings).
- **Kuzu** (rq4-kuzu.md): Structured property graph with node/rel tables. Artefacts, versions, evidence, provenance, and supersession all representable with low schema complexity. One label per node and pre-defined schema are modelling constraints but not excessive (rq4-kuzu.md F1–F7). **Critical caveat:** original project archived October 2025 following Apple acqui-hire; continued use depends on community forks (LadybugDB, Vela-Engineering/kuzu) (rq4-kuzu.md E7, F9).
- **PostgreSQL+pgvector** (rq4-pgvector.md): Can represent all five concerns via tables, foreign keys, join tables, and recursive CTEs — but as a *simulated* graph, not a native one. Schema is more verbose; multi-hop traversal requires recursive SQL. pgvector adds genuine semantic search capability orthogonal to graph modelling (rq4-pgvector.md Findings).
- **SQLite+edge tables** (rq4-sqlite.md): Achievable via adjacency-list tables and recursive CTEs. Schema is moderate; traversal queries are hand-written SQL with explicit cycle guards. Strong portability (single-file, git-friendly, public domain). Single-writer limitation constrains concurrent web use (rq4-sqlite.md Findings).

**Evidence against / gaps:**
- The one-label-per-node constraint in Kuzu means an artefact cannot simultaneously carry multiple labels (rq4-kuzu.md F7).
- PostgreSQL and SQLite require recursive CTEs for multi-hop traversal, which degrade at depth — ~100× slower than native Neo4j at 6 hops / 10M nodes (rq4-pgvector.md §9).
- Kuzu's archival means the original project cannot be adopted; only community forks remain (rq4-kuzu.md F9).
- No report benchmarks the specific EDASES artefact-graph query patterns against any database.

**Verdict:** Property graph databases (Neo4j, Memgraph) model artefacts, versions, evidence, provenance, and supersession naturally and with low schema complexity. The entity–state versioning pattern is a well-documented, reusable idiom. Relational databases (PostgreSQL, SQLite) achieve the same representation but with more verbosity and slower multi-hop traversal. The hypothesis is well-supported for native graph databases; qualified for relational alternatives.

---

## Cross-cutting findings

### 1. The lifecycle-ownership conflict is the central architectural tension

Four RQ3 reports independently identify the same structural conflict: execution engines (Temporal, Camunda, LangGraph, Burr) claim ownership of process/execution state and recovery, while EDASES intends statecharts (XState) to own artefact lifecycles. Temporal's design philosophy explicitly positions itself as a *replacement* for state machines (rq3-temporal.md F7). Camunda/BPMN's predefined-model assumption and compensation semantics conflict with immutable artefact versioning (rq3-camunda.md §3, §4). LangGraph owns the durable checkpoint state (rq3-langgraph.md §3). Burr's state machine would overlap XState's lifecycle role (rq3-burr.md F2).

The one demonstrated composition (XState inside a Temporal workflow, rq3-temporal.md §6) inverts the intended authority: Temporal owns durability and recovery; the statechart is a passenger. A reversed composition (statechart owns lifecycle, engine only schedules) is unevidenced across all four reports.

### 2. Provenance is the novel contribution, not artefacts or lifecycles

RQ7 (rq7-existing-methodologies.md) independently confirms what RQ6 (rq6-artefact-recovery.md) argues from the recovery side: all five existing methodologies model artefacts and lifecycles, but none provides first-class, PROV-style provenance or a first-class evidence concept. This is the primary gap EDASES fills (rq7-existing-methodologies.md F4, F5). The W3C PROV family (PROV-DM) is the existing standard EDASES should reference rather than reinvent (rq7-existing-methodologies.md E7).

### 3. The actor model is the shared abstraction across layers

XState's actor model (rq2-xstate.md), the graph-as-projection architecture (rq5-multi-view-frontend.md), and the entity-state versioning pattern (rq4-neo4j.md, rq4-memgraph.md) all converge on the same abstraction: each artefact is an independent, typed entity with its own state, connected to other entities via typed relationships. This is consistent across the statechart layer (one actor per artefact), the storage layer (one node per artefact with version/evidence/provenance edges), and the view layer (one projection per view over the shared graph).

### 4. Virtualization is the performance gate for graph UI at scale

All four RQ1 reports identify viewport-based virtualization as the key scalability mechanism. React Flow has it as a built-in prop (rq1-react-flow.md §5). AntV X6 has it as a first-class feature (rq1-antv-x6.md §5). JointJS has it in core (building blocks) and as a turnkey flag in the commercial tier (rq1-jointjs.md §5). Cytoscape.js lacks it entirely (rq1-cytoscape.md §5). Without virtualization, all candidates degrade when rendering thousands of DOM/SVG elements simultaneously.

### 5. Licensing spans the full spectrum

The reports document every licensing posture: public domain (SQLite, rq4-sqlite.md E9), permissive BSD/MIT (PostgreSQL, pgvector, rq4-pgvector.md §10), MIT (Kuzu, rq4-kuzu.md E6; React Flow, rq1-react-flow.md), Apache-2.0 (Neo4j driver), MPL-2.0 (JointJS, rq1-jointjs.md), GPLv3 (Neo4j Community, rq4-neo4j.md §9), BSL source-available (Memgraph, rq4-memgraph.md §10), and commercial (JointJS+, rq1-jointjs.md; Neo4j Enterprise). The licensing question is not one-size-fits-all and depends on EDASES's redistribution and embedding requirements.

---

## Disagreements and uncertainties

### Disagreements

No report directly contradicts another. The closest to a disagreement is the **performance characterisation of graph-like queries in relational databases**: rq4-pgvector.md cites a vendor-adjacent figure of ~100× slower than Neo4j at 6 hops / 10M nodes, while a Medium author argues recursive CTEs "solve 95% of graph problems" with sub-second response at typical depths (rq4-pgvector.md §9). These are not contradictory — they describe different scales and depths — but they pull in opposite directions on whether relational databases are adequate.

### Remaining uncertainties

1. **Quantitative performance at target scale.** No report benchmarks any candidate at 5,000+ artefacts with realistic complexity. The closest figures are AntV X6 at ~2k nodes, JointJS at 11k light cards, Cytoscape.js at 6k biology nodes, and XState's unstudied 5,000-actor ceiling. This uncertainty cuts across H4, H5, H6, and H7.

2. **Reversed engine/statechart composition.** All four RQ3 reports find that demonstrated compositions place the engine in the dominant role. Whether a viable architecture exists where the statechart owns lifecycle and the engine is a neutral scheduler is an open question across rq3-temporal.md, rq3-camunda.md, rq3-langgraph.md, and rq3-burr.md.

3. **Artefact-only agent recovery.** RQ6 supports H2/H3 by analogy from workflow systems and HCI, but direct LLM-agent evidence with conversation excluded is absent (rq6-artefact-recovery.md F4, Unknowns).

4. **Provenance granularity for recovery.** How much provenance is necessary and sufficient is unknown (rq6-artefact-recovery.md Unknowns).

5. **Eventual-consistency tolerance.** CQRS read models lag the write model; whether the execution view can tolerate this lag is workload-dependent and unquantified (rq5-multi-view-frontend.md U3).

6. **EDASES lifecycle shape.** Several RQ3 findings depend on assumptions about EDASES's own (unspecified) lifecycle model — whether lifecycles are open-ended or predefined, whether versioning is immutable or reversible, whether coordination requires dynamic graphs (rq3-burr.md U1, rq3-camunda.md Unknowns, rq3-temporal.md Unknowns).

---

## Deferred items

The following scope-boundary items were flagged by subagents as requiring separate resolution:

1. **Legal/licensing assessment.** GPLv3 (Neo4j Community), BSL (Memgraph), MPL-2.0 (JointJS), and source-available (Camunda/Zeebe) licensing each carry distinct implications for EDASES distribution and embedding. Multiple reports (rq4-neo4j.md, rq4-memgraph.md, rq3-camunda.md, rq1-jointjs.md) flag this as a question for legal review, not a technical finding.

2. **Empirical validation of RQ6.** RQ6 (rq6-artefact-recovery.md) designs a three-condition experiment (artefact+provenance vs artefact-only vs conversation-history baseline) but does not execute it. Execution is deferred to a validation phase.

3. **EDASES requirements specification.** The severity of the lifecycle-ownership conflict (Cross-cutting Finding 1) depends on EDASES requirements not yet specified: coordination dynamism, artefact-state model, versioning semantics, and write-concurrency profile. These are flagged as unknowns in rq3-burr.md (U1, U2), rq3-camunda.md, rq3-temporal.md, and rq3-langgraph.md.

4. **Kuzu fork governance.** The original Kuzu project is archived (rq4-kuzu.md E7). Long-term health and governance of community forks (LadybugDB, Vela-Engineering/kuzu, Bighorn) requires monitoring, not a one-time assessment.

5. **Graph UI benchmarking at target scale.** All four RQ1 reports require hands-on benchmarking at 5,000+ nodes with realistic artefact-node complexity to resolve the performance uncertainty. This is a testing task, not a literature task.

6. **3-concurrent subagent stability.** The original W-6 3-concurrent test produced an empty result from the Burr subagent. A retry with mid-wave memory polling confirmed 3-concurrent is stable (mid-wave delta ~50 MB, all 3 subagents completed cleanly). The original failure is attributed to an unrelated flake, not a concurrency limit. Peak verified concurrency for this run is 3.

7. **W-9 memory gap.** Wave W-9 (RQ4's last investigator + RQ7) has no `free -h` before/after reading — a missing data point in an otherwise complete memory record across W-1 through W-12.

---

## References

### RQ1 — Graph UI frameworks
- rq1-react-flow.md — React Flow (@xyflow/react)
- rq1-cytoscape.md — Cytoscape.js
- rq1-antv-x6.md — AntV X6
- rq1-jointjs.md — JointJS

### RQ2 — Statechart frameworks
- rq2-xstate.md — XState / Stately
- rq2-scxml.md — SCXML (W3C)

### RQ3 — Execution engines
- rq3-temporal.md — Temporal
- rq3-camunda.md — Camunda / BPMN
- rq3-langgraph.md — LangGraph
- rq3-burr.md — Burr (Apache)
- rq3-burr-retry.md — Burr (retry, 3-concurrent validation)

### RQ4 — Graph databases
- rq4-neo4j.md — Neo4j
- rq4-memgraph.md — Memgraph
- rq4-kuzu.md — Kuzu
- rq4-pgvector.md — PostgreSQL + pgvector
- rq4-sqlite.md — SQLite + edge tables

### RQ5 — Multi-view frontend
- rq5-multi-view-frontend.md

### RQ6 — Artefact recovery
- rq6-artefact-recovery.md

### RQ7 — Existing methodologies
- rq7-existing-methodologies.md
