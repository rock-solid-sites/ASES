---
title: Historical idea recovery — initial derived register
program: ASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# Initial idea register

Read with [assignment](README.md) and [coverage](COVERAGE.md). This is a selective, incremental public-safe navigation record, not a complete backlog, adopted architecture, or authorization to execute. Restricted historical discoveries, exact passages, and private owner records are retained in the authorized private execution record; absence from this public view says nothing about existence or relevance. Keep research and implementation status separate.

## Git-based engineering — residual comparative experiments (HIR-008)

**Public evidence:** [EDASES Git-Based Engineering Systems](../retrospectives/topics/EDASES-topic-Git-Based-Engineering-Systems.md), §§6–12 (blob `930b38a5b638d68f6054a8cc3c2ea9752a88dfdc`, read 2026-11-27); dated research record 2026-08-10.

The record proposes a series of experiments on recoverability, observability, and the boundary between Git-native and external state, based on real prior engineering work. Distinct empirical questions include:

- Whether meaningful incremental checkpoints improve interruption recovery versus monolithic delivery; measure what survives, takeover cost and false liveness signals.
- Whether stacked changes improve decomposition, independent review, intervention and error localization versus ordinary branches, rather than merely making diffs smaller.
- Where isolated worktree use still requires external coordination, and whether combinations of otherwise useful practices add value or redundant process.

**Research:** concrete prior proposals; comparative outcome not established in the sources inspected. **Implementation:** operational use of individual mechanisms is documented, but that does not establish the proposed comparative results. **Candidate owner:** existing EDASES Git-based engineering research.

**Reconciliation:** current [task-scoped method](../../methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md) explicitly makes branches disposable, distinguishes progress from durable final delivery and does not require preservation of Git history. The older workflow must not be reinstated as a default. The residual question is empirical benefit under the current deliverable/recovery constraints, not another architecture decision about mandatory history. Reuse the [failure investigation](../../../research/agent-information-topology/greenfield-task-context/field-trial/RECURRING-COORDINATION-FAILURES-2026-11-26.md) and [comparative implementation research proposal](../Comparative%20Implementation%20Research%20and%20Upstream%20Contribution%20Proposal%202026-11-25.md) where applicable. First reconcile later evidence; no new lab or experiment launched.

## Knowledge index — existing partial realization, not rediscovery (HIR-009)

**Public evidence:** [design](../Cross-Project%20Knowledge%20Index%20-%20Minimal%20Schema%20and%20Integration%20Boundaries.md), [historical prototype test record](../Knowledge%20Index%20Prototype%20-%20Real%20Repository%20Test%20Record%202026-11-19.md), [merged PR #61](https://github.com/rock-solid-sites/ASES/pull/61), [pilot charter](../../proposals/knowledge-index/Experimental%20Pilot%20Charter%20and%20Handoff%202026-11-19.md). The older test record still says the PR is draft; the actual PR is closed and merged, and the subsequent charter governs the research-only baseline.

**Research:** experimental pilot constructed; comparative retrieval evaluation remains a distinct question (check its existing owner record). **Implementation:** disposable index, not a maintained authorization service; the recorded real-source tests and red/green repairs do not establish cross-workspace ACL or revocation correctness. **Owner:** existing knowledge-index investigation. No parallel index or automatic archive ingestion proposed.

This is a negative deduplication result: a historical proposal that sounds unimplemented can have a real, limited implementation and a separate unexecuted evaluation. Preserve that distinction rather than creating a new work item.

## Relationship and disposition rules

Both topics relate to recoverable information and evidence, but the Git workflow experiments measure engineering behavior and the index pilot measures retrieval. Neither subsumes the other; no dependency inferred. Link later verified outcomes rather than promote a proposed experiment to an accepted result. Existing current policy and owner-specific decisions take precedence over historical implementation suggestions.