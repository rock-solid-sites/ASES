---
title: Frontier round 2 — independent minimal Kernel-0 derivations
version: 0.1.0
status: Experimental
authority: Derived
last_updated: 2026-11-25
---

# Round 2 comparative result

Input: [independent derivation prompt](https://github.com/rock-solid-sites/ASES/blob/01484c5d1148586e2db8c8cff6df7019959f1498/docs/research/astra-followup-20261125/frontier-comparison/MINIMAL-KERNEL-DERIVATION.md); neutral Kernel-0 requirements at a02df749b4b3da88d3f88c1712623cec6ad5d963. Previous candidate designs withheld by prompt. Operator supplied two text attachments in Astra, Sol order; preserved complete extracted text in [Astra](responses/round2-astra-high.md) and [Sol](responses/round2-sol-high.md), remote readback matched. Model labels follow upload order/operator report; session independence, elapsed time, context counts and allowance deltas not independently established. This is unblinded coordinator analysis, not formal verification or cross-family review.

## Findings

Both proposals are realization-neutral guarded authoritative-state candidates, not selected architecture. Both preserve persistent identity, distinguish authority from ordinary data, require current scoped authority and atomic admission at the authoritative effect boundary, protect against grant resurrection, separate external occurrence from evidence and recognize external exactly-once limits.

Astra: deliberately narrow provisioned protected data addresses and grant positions, direct tenure-specific grants, separate configuration authority, single-entry Bind/Replace plus mediated Read. Conditional revisions are optional when the conflict contract does not require them. No general autonomous delegation or multi-entry transactions assumed. Explicit counterexamples for indirect commands, shared resource aliases, confidentiality/information flow, rollback and author/reviewer split where a co-located record would destroy separation of authority. A gap during cross-position transfer can be permitted.

Sol: versioned fixed-kind addresses, Commit(expected, changes, proofs) with closed Put/Bind/Clear vocabulary, guarded multi-entry atomicity, live parent-incarnation lineage and attenuation via distinct use/pass rights. Slot management and supplying rights separately checked; pre-state proofs, newly installed parent must remain live in post-state. Exact attachment dependence may need to be conjunctive where independent issuers exist. Distinguishes revoking a grant, all authority of an execution and access to a resource. Directory/phantom and cross-record conflicts recognized. Acknowledges governor-only direct grants are smaller if autonomous delegation not required.

## Discriminators and limits

Astra is a useful narrower baseline; Sol is a conditional richer candidate, not proved irreducible. Do not infer overall model superiority from one question. Test dynamic creation/disposal and resource identity; governance/bootstrap and recovery; derived permission and confused-deputy pathways; split-authority cross-record invariants (single-entry layout vs guarded atomic batch); omission of relevant caller-supplied guards (an invariant is not enforced merely because a request can express it); effect boundaries and information-flow contracts. Sol's phrase 'admitted before revocation can commit' must mean an already-authoritative decision, not a prior non-atomic check; surrounding rule checks authority at commit, so this is a specification ambiguity to clarify, not a demonstrated defect. Neither candidate proves general invariant enforcement or implementation conformance. Do not infer intrinsic full historical ledger requirement from continuation alone.

## Relation to previous kernel research

The historical ISOLATE/CONNECT/ORDER vocabulary is kernel-specific, not a general ASES methodology. The current neutral requirements and Execution Engine Vision do not prescribe it. Recovered prior-conversation summaries suggest August triad work used isolation/domain boundaries, authority relationships and transition ordering, while September guarded authoritative commitment work may have superseded that framing; exact historical semantic definitions and disposition are not yet checked against original source. Treat these summaries as research leads, not canonical evidence. There is conceptual overlap with both new candidates, but no proved equivalence, sufficiency or requirement to retain three primitives. Before an anchored sufficiency test retrieve exact source and reconcile its status; do not infer definitions from names.

## Next action

Cross-family adversarial assessment of the two candidates, using exact prompt/requirements, without model labels or previous verdict. Determine actual necessity of the additional delegation and batch machinery by counterexample, and identify whether a strictly smaller semantic model suffices. Keep constructive independent derivation separate from subsequent anchored primitive analysis. No implementation, runtime tests, new model launches or architecture adoption in this turn.
