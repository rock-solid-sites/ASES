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
