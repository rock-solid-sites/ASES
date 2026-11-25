---
title: LLM Agents and Distributed Systems - Research Topic
program: EDASES
layer: Research
document_type: Research Framework
status: Experimental
authority: Experimental
canonical_repository: edases
depends_on:
  - docs/standards/Documentation Standard.md
related_documents:
  - docs/research/Workflow Topology Design and Reasoning Record.md
last_updated: 2026-11-19
---

# LLM agents and distributed systems

## Local reconciliation: prior work and transferable foundations (2026-11-25)

The literature programme below remains open under Projektor ASES-18. Its initial bibliography is abstract-level candidate triage, not a verified systematic review, a novelty claim or evidence of replication. Preserve the original external-source questions; no primary-paper rereading, citation sweep or new comparative experiment was undertaken in this reconciliation.

| Research question | Related existing evidence and applicability |
| --- | --- |
| Scheduling, heterogeneous resources, DAGs and critical paths | [Resource Solver specification reconciliation](Resource%20Solver%20Specification%20Reconciliation%202026-11-02.md) sections on feasibility, optimization and admission preserve exact-reference, bounded local-search and heterogeneous synthetic evidence. The Python/Rust/Haskell comparisons and local transactional experiments are not distributed scheduling, real-agent scaling or provider-enforcement results. No optimizer or implementation language selected. |
| Resource admission, shared state and recovery | The same Solver record covers local SQLite reservations, replay, cancellation, overrun/settlement and report overlap. Distinguish exact admission, effect identity, provider-side lifecycle and actual liability; local serializing transactions and bounded crash tests do not establish distributed transactions, partition tolerance or complete provider admission. |
| Authority, fencing and continuing work | The [Kernel-0 evidence packet](kernel-0/Kernel-0-Evidence-Packet.md) and [Execution Engine Vision](../architecture/Execution%20Engine%20Vision.md) specify bounded authoritative change and durable work versus disposable execution. [PR #83](https://github.com/rock-solid-sites/ASES/pull/83) reports W5–W6 not represented by the Rust resource-control API. [PR #84](https://github.com/rock-solid-sites/ASES/pull/84) and [existing hosted replay #86](https://github.com/rock-solid-sites/ASES/pull/86) support the scoped native pending-admission repair, not a complete Kernel or cross-host proof; [PR #85](https://github.com/rock-solid-sites/ASES/pull/85) remained blocked before container creation on its exact environment. Preserve source-specific boundaries in the [engine history](../historical/Engine%20Architecture%20and%20Experiment%20History.md). Leases, fencing and consensus are comparison mechanisms, not imposed Kernel representations. |
| Coordination topology, information asymmetry and context | The [historical topology record](Workflow%20Topology%20Design%20and%20Reasoning%20Record.md) preserves earlier observations and rejected paths. The [task-scoped architecture decision](../architecture/Task-Scoped%20Information%20Architecture%20Decision%202026-11-21.md) governs information sufficiency, provenance and scoped authority without a mandatory graph, resolver, topology or centralized context service. Its adoption is not evidence that one information topology or coordination pattern outperforms all others. Knowledge-index and context-view experiments retain their separate acceptance questions. |
| Failures, stragglers, recovery and measurement | Reuse the Solver observation/MQI reconciliation and its pinned model-stream results: byte activity, useful progress, terminal output, independently qualified work, resource consumption and settlement differ. Existing local interruption/replay controls and historical stream experiments inform candidate measures; none establishes general distributed liveness or fault tolerance. Do not conflate an unreliable semantic answer with a transport fault or an adversarial/Byzantine process. |
| Assurance and comparative implementation research | The [cross-project property/stateful pilot](https://github.com/rock-solid-sites/ASES/blob/2affc493a0296dcf80efc598a99e64631c333569/docs/research/Generated%20Property%20and%20Stateful%20Testing%20Cross-Project%20Pilot%202026-11-19.md) distinguishes synthetic stale-execution witnesses from bounded generated histories on actual HMS and Rust resource-control code. Use existing controls and independent oracles; do not infer production assurance or framework superiority. The [comparative implementation and upstream contribution discussion](Comparative%20Implementation%20Research%20and%20Upstream%20Contribution%20Proposal%202026-11-25.md) proposes source-pinned comparisons, reciprocal method improvement and eventual reusable free testing tooling. It remains a proposal, not an approved laboratory, universal suite, or scheduled research run. Reuse existing WNASES-10/14 and ASES-7 work rather than duplicate it. |

### Scope and remaining questions

The general correspondence between LLM-agent coordination and distributed computing, including information asymmetry, task dependency and communication overhead, remains independently valuable EDASES/shared research. ASES is a relevant case study and consumer, not the owner of distributed-systems mechanisms generally. Work Unit/Kernel authority and adequacy, Engine realization, Solver placement/admission and independently useful assurance instruments have distinct questions, evidence and owners. Findings may transfer only under matching semantics and assumptions.

The original literature candidates and sweep tracks are retained. A later approved investigation should first establish bibliographic identity, primary-source evidence quality and exact claim/setting, compare against dated ASES sources and prioritize genuinely discriminating residual questions. Matched single-agent/self-assignment/centralized/solver-governed DAG comparisons, formal safety/liveness conditions, communication and enforcement costs, and fault-injection under applicable distributed boundaries remain proposals. Distinguish mechanism applicability, empirical benefit and formal guarantees. No duplication of existing tests, novelty attribution, production design choice, research launch or methodology promotion is implied.

**Disposition:** documentation crosswalk complete; ASES-18 literature sweep, deduplicated bibliography, primary-paper claim matrix and prioritized research plan remain outstanding. Do not close the research issue on this basis. Source cutoff [c9c948d2](https://github.com/rock-solid-sites/ASES/tree/c9c948d23f5df7c58a86ba1af18d5c2163fcd415); original research topic retained below. Documentation only, no Actions/CI, new experiments, model calls or implementation.

## Research question
Which established distributed-systems principles and recent empirical findings apply to coordinating heterogeneous LLM agents, and which ASES Resource Solver, Work Unit, Kernel-Zero and Execution Engine hypotheses can be independently falsified?

This is a research topic, not an architecture decision or a declaration of novelty. Distinguish previously developed ASES ideas from external precedents; do not infer chronological priority or independent novelty without dated evidence.

## Initial trigger
- PNAS DOI: https://www.pnas.org/doi/10.1073/pnas.2612825123
- Evaluate the paper's experimental methods, coordination conditions, task dependency structures, scaling, speedup, conflict and straggler measurements; verify all numerical claims against the paper itself.

## Initial literature candidates (abstract-level triage; not yet reproduced)
- SILO-BENCH (ACL 2026): https://aclanthology.org/2026.acl-long.1354/ — distributed information, communication/reasoning gap.
- HiddenBench (ICML 2026): https://proceedings.mlr.press/v306/li26ej.html — information asymmetry and premature convergence.
- Dynamic Context Allocation (EMNLP 2026): https://aclanthology.org/2026.emnlp-main.1785/ — bounded context and information exposure.
- MultiAgentBench (ACL 2025): https://aclanthology.org/2025.acl-long.421/ — coordination topologies and milestone measures.
- Agora (ICML 2026): https://proceedings.mlr.press/v306/liu26dw.html — state-space testing of distributed consensus protocol invariants using agents.
- Group size effects and collective misalignment (PNAS 2026): https://pmc.ncbi.nlm.nih.gov/articles/PMC13505991/ — nonlinear group effects.
- Coordination Overhead and Governance Readiness (SSRN 2026; preprint): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6781620 — architecture overhead and governance instrumentation; interpret benchmark limits.

## Sweep tracks
1. Classical distributed systems: scheduling, queueing, DAGs, critical paths, resource allocation, admission control, leases/fencing, failure detectors, idempotency, consistency, isolation, consensus and distributed transactions.
2. LLM-agent systems: orchestration vs self-organization, task allocation, shared memory/blackboards, communication topology, context propagation, information asymmetry, heterogeneity, failure recovery and cost.
3. Assurance: machine-enforced authority, state-machine safety/liveness, model checking, property-based and fault-injection tests, Byzantine or semantically unreliable workers.
4. Comparative implementations and benchmarks: reproducible code, workloads, measurement instruments and external baselines.

## ASES comparison protocol
For each source record: bibliographic identity and date; empirical vs theoretical vs opinion; exact claim; study setting and limitations; mechanism; analogous ASES component; whether ASES already documents the idea; dated provenance; support/conflict/unknown; falsifiable test; implementation implications (if any); and confidence/untested surface.

Keep research separate from methodology and architecture changes. Do not treat source agreement as proof of correctness. Compare against the current canonical ASES documents before asserting a gap.

## Candidate experiments
- Compare single-agent, decentralized self-assignment, static central assignment and solver-governed assignment under identical task DAGs and budgets.
- Inject slow workers, crashes, duplicate completion, late writes, stale leases and partial information.
- Measure verified success, cost, wall time, critical-path delay, idle resources, communications, conflicts, recoverability, and invariant violations.
- Separate empirical performance benefits from formally specified guarantees; measure overhead introduced by enforcement.

## Next steps
Conduct a systematic bibliography sweep and deduplicate by DOI; read primary papers and linked code; map claims to existing Resource Solver and Execution Engine specifications; produce an evidence matrix and a prioritized cheapest-test-first experimental plan. No implementation or policy change is authorized by this topic record.
