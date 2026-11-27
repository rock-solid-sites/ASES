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


## Bounded judgment — surviving Jev experiments (HIR-010)

**Public evidence:** [Phase 1 verdict](https://github.com/rock-solid-sites/ASES/blob/98cab044f4f9db615e5fcd95d099df97daddaf0a/research/jev-bounded-judgment/phase1/PHASE1-VERDICT.md), [Phase 2 design](https://github.com/rock-solid-sites/ASES/blob/98cab044f4f9db615e5fcd95d099df97daddaf0a/research/jev-bounded-judgment/phase2/README.md), [Experiment 2 design](https://github.com/rock-solid-sites/ASES/blob/98cab044f4f9db615e5fcd95d099df97daddaf0a/research/jev-bounded-judgment/phase2/exp2/DESIGN.md), [Experiment 3 independent verification](https://github.com/rock-solid-sites/ASES/blob/98cab044f4f9db615e5fcd95d099df97daddaf0a/research/jev-bounded-judgment/phase2/exp3/verification.md). Source branch verified at the pinned September 28 revision.

Phase 1 demonstrates a scoped advantage over deterministic/lexical baselines but not a capability niche over MiMo V2.6 Flash on its synthetic answerable cases. Intrinsic abstention was not established; operational latency measurements are narrow cross-window observations. Phase 2 uses real code, distinguishes lookup from judgment and tests derivability rather than scoring unavailable evidence as model failure. The surviving Experiment 3 verification reports 9/10 unanswerable cases detected at its preregistered threshold and 0/41 false unknowns; distributions touch, and argmax selection is not the threshold result. Do not extrapolate calibration or universal separation.

**Research:** substantial empirical work exists; Experiment 2 shared-state multi-question comparison is explicitly design-only in the surviving revision. Later state must be reconciled before rerunning. **Implementation:** experimental harness and source-backed test corpus, not an adopted decision service. **Owner:** EDASES decision-model research, with adjacent capability evidence and resource-allocation work; no new architecture adopted. See [formal-computation findings AD-028](../formal-computation-reuse-avoidance/ARCHIVE-FINDINGS.md#ad-028--batched-judgment-must-preserve-the-evidence-semantics-of-each-decision) for the reusable computation question rather than duplicating it. Preserve negative results and original controls; recover the latest verified artifacts first.

## Claim-driven testing on a real implementation (HIR-015)

**Public evidence:** [Guarantee-Driven Testing and Goal-Substitution Resistance](../Guarantee-Driven%20Testing%20and%20Goal-Substitution%20Resistance.md) (source blob `3dee993a4fbedfa688bca03d3722f169d5fd0013`) and [Testing and Assurance Source Map](../Testing%20and%20Assurance%20Source%20Map.md) (source blob `628cce95bae49f4a220d2153baddf1e544070b9a`).

The earlier research proposes a target-specific claim register and a controlled real-implementation experiment, with ATProto Spaces named as the proposed substrate. Study attributable claims and the evidence required to discriminate compliance and violation before choosing techniques. An untestable claim or zero discrepancy is a valid result; defect count is not the research objective. Evaluate the testing method, including the cost and failure modes of the gates themselves.

**Research:** earlier concrete design; later testing pilots establish partial method realization elsewhere, not completion of this original target experiment. **Implementation:** original target execution not established in the public sources inspected. **Owner:** existing empirical testing research, with target-specific ownership distinct. Reconcile later source records before building anything. No target testing or disclosure is authorized by this register.


## Capability evidence versus allocation (HIR-030)

**Public evidence:** [AI Capability Registry Specification](../registry/AI%20Capability%20Registry%20Specification.md), [16-review-wave retrospective](../retrospectives/topics/EDASES-topic-Model-Capability-16-Review-Wave.md), [Model Routing Matrix](../registry/Model-Routing-Matrix.md). The research registry records observed behavior; operational strategy is derived separately. Two eight-model review waves offer actual findings and important access-asymmetry and synthesis-attribution limitations, not a fully controlled capability benchmark.

**Research:** qualitative and observational evidence exists; controlled comparisons and calibration against actual review outcomes remain distinct questions. **Implementation:** descriptive registry exists; it is not a measured resource solver or a provider-routing authority. **Owner:** existing model capability research; retain the current registry and associated work rather than build another. See the [early research disposition](../../../future-research-topics/README.md) for current ownership and overlap.

## Disposition correction: older automatic provenance export (HIR-007)

**Public evidence:** [September 29 archival commit](https://github.com/rock-solid-sites/ASES/commit/dcc34f15d6db7f80958567022c32e28bd759de9e) explicitly archives the undeployed Crosslink auto-export design family. The current task-scoped method governs durable evidence and deliverable homes; Git history is not itself the deliverable.

Do not reopen the archived implementation as an uncompleted obligation. Residual provenance questions concern useful reasoning/evidence preservation and recoverability, not compulsory commit-level telemetry or reintroducing a superseded bridge. The public source proves archival of that family, not a universal resolution of all provenance questions.


## Relationship and disposition rules

Related subjects retain their different evaluation objects: engineering behavior, retrieval, bounded judgment, assurance methodology, conceptual discrimination, capability evidence and reasoning provenance. Link later verified outcomes rather than promote a proposed experiment to an accepted result. Current policy and owner-specific decisions take precedence over historical suggestions. Historical branches are evidence, not new delivery destinations. No dependency inferred solely from topical similarity.


## Deferred coordination mechanisms are not forgotten core requirements (HIR-022)

**Public evidence:** [September execution-engine roadmap](https://github.com/rock-solid-sites/ASES/blob/cff5f57c/docs/architecture/EDASES-Execution-Engine-Roadmap.md), [efficiency architecture research](https://github.com/rock-solid-sites/ASES/blob/85158604d/docs/architecture/EDASES-Efficiency-Architecture.md), [structural-transition study](https://github.com/rock-solid-sites/ASES/blob/3e5abe47a77538adb0dbe795eff8a001050809c5/docs/research/structural-change/EDASES-Bounded-Structural-Transitions.md). Historical roadmap deliberately sequences core closure before evaluation of optional Observer, Processor, Orchestrator and work-tracking units, then full-system coordination. The earlier structural study finds no additional Kernel-0 semantic power in its F4 structural-change histories; Work Unit policy obligations still require concrete instantiation.

**Research:** existing deferred coordination/integration questions and partly investigated efficiency mechanisms, not missing core primitives. **Implementation:** historical source-level designs and research artifacts, not proof that the full roadmap is realized. The later [formal computation research](../formal-computation-reuse-avoidance/README.md) owns computation avoidance/reuse; [Kernel-0 research](../kernel-0/README.md) owns current core experiments. Keep the future-topics scratchpad a source list, not a ranked work queue. Reconcile specific questions with later evidence before commissioning work.

## Conceptual-review discrimination — a benchmark exists, but comparative review is not measured (HIR-023)

**Public evidence:** [P7 redacted machine result](https://github.com/rock-solid-sites/ASES/blob/f40da189237896a146ad5913ddbd1aca13e488ed/research/ontology-benchmark-p7/evidence/p7-machine-result-redacted.json), [independent-review protocol](https://github.com/rock-solid-sites/ASES/blob/f40da189237896a146ad5913ddbd1aca13e488ed/research/testing-assurance-pilot/P7-REVIEW-EXECUTION-PROTOCOL-2026-11-02.md), [draft PR #4](https://github.com/rock-solid-sites/ASES/pull/4), [current testing and assurance source map](../Testing%20and%20Assurance%20Source%20Map.md).

The earlier [Ontology Reviewer proposal](../../roles/Ontology-Reviewer.md) raised an empirical distinction between exploratory and conformance review. The November P7 corpus has six cases, including clean controls; its identity with the earlier proposed corpus is not established. The [validation-brief corpus](../../../evaluation-corpus/validation-brief-corpus/README.md) measures a related but distinct methodology-enforcement question. Its cheap syntax heuristic detected two of four seeded defects without flagging either clean control; this is **not** an ordinary model-review comparator. The record marks independent review routes NOT_RUN and concept ground truth not independently validated. A corrected conformance packet removes trace hints that could reveal planted defects. Preserve this distinction between a qualified instrument and an actual measured capability. Any earlier benchmark asset should be reconciled rather than assumed identical to P7.

**Research:** corpus preparation and deterministic control partly demonstrated; actual comparative capability, restraint, grounding and cost remain unmeasured in the inspected evidence. **Implementation:** experimental packets, not an adopted reviewer-role gate. The current source map uses distinct reasoning modes and rejects reinstating permanent ontology roles. Preserve the comparative question under current assurance research; no new role, duplicate corpus, or dispatch is authorized by this entry.

## Collective correctness beyond individual verification (HIR-031)

**Public evidence:** [historical classification prompt](https://github.com/rock-solid-sites/ASES/blob/ef24547caa8759f6c84e31009714359d66ddcbc4/docs/historical/decisional-provenance/research-level-classification-prompt.md), question D; [Gas Town historical synthesis](https://github.com/rock-solid-sites/ASES/blob/ef24547caa8759f6c84e31009714359d66ddcbc4/syntheses/gas-town-deep-dive-summary.md); [Kernel-0 research](../kernel-0/README.md).

Individually verified changes may fail when combined. The research question is what establishes collective correctness under declared dependency and interaction assumptions, including when review evidence must be invalidated or refreshed. It is not simply which Git merge queue to use. Related to HIR-008 and HIR-022, but distinguish empirical software integration validity from bounded formal Work Unit composition results. Current core research gives concrete compositional safety results under specific assumptions, not general software integration correctness.

**Research:** historical proposal with related formal evidence; original empirical comparative scope remains to be reconciled. **Implementation:** no general integration mechanism inferred. Do not create a mandatory queue or permanent role from this question.

## Historical research-level classification — recovered review corpus (HIR-034)

**Public evidence:** [historical provenance filing commit](https://github.com/rock-solid-sites/ASES/commit/ef24547caa8759f6c84e31009714359d66ddcbc4), [review directory at that revision](https://github.com/rock-solid-sites/ASES/tree/ef24547caa8759f6c84e31009714359d66ddcbc4/docs/historical/decisional-provenance-reviews/research-level-classification).

The research/methodology/runtime distinction was subjected to a multi-model classification exercise. The pinned filing commit preserves one common prompt, eight nominally model-attributed noncorrupt responses, one attribution-mismatch record, and one corrupted output. Preserve the two qualified records as such. The reviews disagree about the count and boundaries of fundamental tracks, whether questions should be partitioned or decomposed across levels, the direction of empirical feedback, and how to treat collective correctness. Model agreement cannot prove that the taxonomy is uniquely correct.

**Research:** review corpus exists; comparative adjudication and downstream lineage remain to be checked, rather than assuming the exercise never happened. **Implementation:** not a new taxonomy. The historical filing commit diverges from current main; this record preserves its evidence without declaring the moves present on main or repeating them. Use the existing topic organization.

## Identifier-first tool calling — existing research, qualified residuals (HIR-035)

**Public evidence:** [identifier-first research](../Identifier-First%20Tool%20Calling.md), [lazy MCP proxy experiment](../../../research/toolregistry-lazy-mcp/report.md), [catalog-scale experiment and November 25 scope qualification](../../../research/toolregistry-lazy-mcp/catalog-scale/report.md).

The project already has substantial validation of a narrow lazy-connector architecture and bounded catalog residency, plus description-compression experiments. The exact identifier-only representation, matched CLI comparison, generalized idle-timeout/pooling policy, multi-transport validation and full costs remain distinct questions in the existing reconciled research record. This is a negative deduplication result: retain current evidence and owners instead of opening a competing Lexicon project. Research result does not authorize adopting the prototype.

## Reconciliation checkpoint — 2026-11-27

The [first present-state reconciliation](RECONCILIATION.md) qualifies these entries against current owners, decisions and surviving artifacts. The [synthesis](SYNTHESIS.md) organizes the residual questions by existing research homes. Later Jev preparation reports were found; the missing measured-result artifacts remain a custody gap, not proven loss. Do not rerun as a substitute for recovery. This selective view does not enumerate the complete private register or authorize work.
