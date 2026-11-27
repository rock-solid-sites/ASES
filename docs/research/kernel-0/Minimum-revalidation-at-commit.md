---
title: Which observations must be revalidated at commitment?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# Which observations must be revalidated at commitment?

A caller-supplied guard can omit a dependency and still pass every comparison it names. Conversely, rechecking every field consulted during preparation can repeat work whose answer cannot change. For a finite admission policy one can calculate what a trusted verifier needs to distinguish after interference. The answer depends on the requested effect, the observed preflight evidence, the transitions possible before commitment, and what the consumer was promised. [Candidate comparison and omission concern](../astra-followup-20261125/frontier-comparison/ROUND2-COMPARISON.md)

## A complete check for a proposed set of observations

Fix a request and trustworthy preflight evidence. Let T contain all authoritative states consistent with that evidence and subsequent permitted interference up to the commit cut. Let D(s) be the required decision, including every difference in authoritative action or response that the checker must resolve. Each available field is an authenticated observation of state at that cut. For every pair s,t with different decisions, form the set of fields whose values differ between them. A fixed selection S suffices for an exact decision **if and only if** it hits every such difference set.

A missed set supplies an indistinguishable pair requiring different decisions. If all sets are hit, every reachable observation tuple on S has a single decision, furnishing the decoder. An empty difference set means even all available observations are insufficient. No differing pairs means preflight evidence alone determines this decision class. An overapproximation of T can give sufficient observation sets and spurious lower bounds. A claimed necessary field needs actual reachable histories or an exact model.

This is the decision-table discernibility construction applied to *post-interference* states. Distinguishability as a technique predates ASES. The contribution here is choosing the comparison domain, contrasting fixed and adaptive reads, and checking the consequences for fresh admission versus replay. A worker may propose the field set or a cached decision table. The owner must establish coverage against the correct transition and observation contract, including freshness. A verified dependency set cannot make a non-atomic read coherent. [Skowron and Rauszer, *The Discernibility Matrices and Functions in Information Systems*](https://doi.org/10.1007/978-94-015-7975-9_21)

For a particular commit-time view, the owner can also act when all states with that view agree, and defer in mixed cases if the interface allows deferral. A definitive refusal or assertion of staleness is itself a decision. For example two grant bits can move atomically from (1,0) to (0,1). A reader observing the first bit before that transition and the second afterward can assemble (1,1) although no admitted state had that value. Selecting both necessary fields without a coherent view can admit an effect that their conjunction never authorized.

## A Work Unit example

Consider one request from X to a continuing local owner. Its preflight evidence binds the request identity, payload and W/P. Between preflight and commitment, another exact or conflicting use of the nonce may commit, and X may be replaced irreversibly. Accepted nonce records are immutable. The observable decision class is one of append, replay the stored outcome, conflict or stale. Fix scope and resource validity. The two available fields are X's currentness and the nonce record classified as absent, exact, or conflicting.

- With X current and the record absent at preflight, all six combined states are reachable. "Current versus retired with no outcome" makes checking currentness necessary. "Current with no outcome versus current with an outcome" makes checking the nonce necessary. Inspecting only an expected current grant supplied by the caller loses the latter pair.
- With an exact or conflicting outcome already observed, retirement cannot change the relevant record. The decision class needs zero new field reads. Serving the exact ordinal without another lookup requires retaining the trustworthy original ordinal and its binding. An effect that writes new state still owes a whole commitment.
- With X retired and no outcome at preflight, no permitted action can add a record for X. Stale is stable. A delayed finalization of an earlier authorized obligation, garbage collection, grant resurrection or owner rollback would change T and requires recomputation of that conclusion.

The implemented local experiment still serializes its reads. These are semantic computations that *could* be eliminated given stronger evidence about a preflight. They are independent of the cost of obtaining or storing that evidence. [Local owner](Local-owner-admission-and-replay.md) · [Receipt release changes the contract](Receipt-retention-after-replacement.md)

## Fixed and adaptive costs can differ exponentially

Suppose k bits select one of 2^k bindings, each with its own independent eligibility bit. The required answer is the selected bit. A fixed field set needs every eligibility bit, since any one can be selected, and every address bit, since neighboring addresses can differ. An adaptive verifier on one snapshot can read the address and then the selected bit, k+1 reads. This is tight with unit-cost binary field observations. Choose an input with selected data bit 0 and all other data bits 1. Flipping any one address bit or the selected bit changes the result. A decision path skipping one of those k+1 fields cannot distinguish the corresponding neighbor. This separation concerns available raw fields. A trusted precomputed aggregate or a change in the cost of taking one coherent snapshot changes the comparison.

`python3 docs/research/kernel-0/decision_revalidation.py` compares the hitting test with direct grouping by projected observations on all nonempty partial binary decision tables over three binary fields. Across 52,480 table/field-set pairs, 17,150 were sufficient and 35,330 insufficient. The script constructs the interference closure from each preflight state in the nonce example and checks its minimal sets. An independent minimax decision-tree search gives fixed/adaptive read counts of 3/2 for two bindings and 6/3 for four. [Executable calculations](decision_revalidation.py)

**Assurance boundary.** The theorem determines sufficiency relative to a request, observation vocabulary, decision function and interference model. It cannot establish completeness of an interface catalogue, prevent omitted writable aliases, infer which output differences matter to the user, or supply snapshot consistency. A silent change to any of these invalidates the reusable evidence. It supports a concrete verification obligation for ISOLATE, CONNECT and ORDER without requiring a particular primitive representation.
