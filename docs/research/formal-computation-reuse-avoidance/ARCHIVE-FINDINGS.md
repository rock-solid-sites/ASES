---
title: Formal Computation — incremental archive findings
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# Archive discovery — incremental findings

Organization and planning only. Read with [research charter](README.md), [source map](SOURCE-MAP.md) and [active discovery assignment](ARCHIVE-DISCOVERY.md). Private exact source identity, coverage and next range are in WNASES-32. Findings are historical evidence or hypotheses, not adopted designs, independent proof or experiments. Opaque finding keys connect to the restricted provenance.

## AD-001 — Handoff sufficiency is a consumer- and operation-relative predicate

**Evidence:** Historical operator-reported incident: an agent that had authored onboarding material asserted that the document and knowledge store were sufficient for a new session. A fresh session recovered approximately the intended vocabulary but recharacterized concepts, gathered information and failed before performing the requested action; a repetitive generation failure also occurred. The operator corrected the description of the underlying project and distinguished application maturity from documentation maturity. The transcript supports the reported discrepancy; the mechanism of the repetition, source admission completeness and causal explanation are unresolved. It is not a measured benchmark.

**Mechanism / question:** A reusable representation is sufficient for a particular authorized operation only if the consumer can reconstruct the relevant semantics, uncertainty, applicable constraints and state. A document can support description without supporting execution. The producer's confidence in a compressed representation is not validation of its use by a fresh consumer. Compare the cost of retaining relevant distinctions or targeted retrieval with the cost of reconstructing them, including erroneous reconstruction, redundant search, and intervention. A cheap discriminator should test operation-relevant fidelity, not merely repetition of vocabulary. Do not assume that a mandatory plan, full reread, or self-report of understanding establishes fidelity; these could themselves add redundant work.

**Domain:** agent cognition, coordination and execution. **Technique:** semantic sufficiency, lossy abstraction, representation validity, negative evidence. Current owner: [task-scoped information and handoff method](../../methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md) distinguishes effective task view, source admission, revision and evidence; [recurring coordination failures](../../../research/agent-information-topology/greenfield-task-context/field-trial/RECURRING-COORDINATION-FAILURES-2026-11-26.md) distinguishes observable failures from unresolved causes. This historical case is a candidate for that existing investigation, not proof of recurrence or a requirement for a new bootstrap artifact.

## AD-002 — Verification must terminate at the obligation, not at universal certainty

**Evidence:** In the same early discussion, an assistant proposed a reconstruction gate, adversarial reality check and evidence-backed execution, and the operator explicitly challenged the recursive regress of verifying verifiers. The operator then asked whether a narrower check could be automated on cheaper hardware, and questioned whether such tooling belonged inside the harness. Historical proposals included checking unsupported claims and assumption/decision traceability separately from generating the project model. No such checker was measured in this exchange; numerical self-confidence, supposed ease of verification and the donor capability descriptions are unverified.

**Mechanism / question:** Distinguish a decision's actual proof/evidence obligation from proving the entire consumer's understanding. Bound the validation by the requested operation, authority, observable acceptance and a finite stopping rule; accept residual uncertainty only where the relevant rule allows it. Reuse accepted scoped evidence rather than recursively revalidating its producer, subject to changed dependencies and trust/authority. Cheap mechanical reference/identity checks can precede semantic review, but a valid reference or unsupported self-reported confidence is not proof of entailment. A specialized reviewer may need less context than the generator; its correctness, false-accept rate, independence and total cost still require evidence. A finite budget alone does not justify execution on failure.

**Domain:** verification, agent cognition, orchestration. **Technique:** bounded obligation, selective validation, separation of generation/checking, proof/evidence custody. The [current task-scoped method](../../methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md) already selects the cheapest relevant falsifier, separates receiver roles, and specifies authority/acceptance. Historical confidence-score and mandatory bootstrap-stage proposals are not current governing procedure. A harness-independent contract/consumer split is a candidate relationship, not a new enforcement design.

## Emerging synthesis (provisional)

Separate representation size from decision sufficiency, and producer-side construction from receiver-side admission and interpretation. A reusable representation may retain facts while losing the authority, applicability, or uncertainty necessary for an operation. This adds a consumer-relative dimension to the identity/validity questions in the source map; it is not a proposal to replace existing task-scoped methods.

A second axis is the cost and termination of verification itself: the operator's early regress objection distinguishes a bounded obligation from an indefinite chain of agent reviews. Candidate specialization should be evaluated by whether the narrower check is adequate for the actual claim, not merely cheaper or easier to express. Keep the domain of operation separate from the technique used to establish sufficiency.
