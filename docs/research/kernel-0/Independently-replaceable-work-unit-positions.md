---
title: When does a Work Unit need independently recoverable executor positions?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/architecture/Execution Engine Vision.md
  - docs/research/kernel-0/Kernel-0-Evidence-Packet.md
  - docs/research/kernel-0/Tenure-reuse-and-delayed-admission.md
last_updated: 2026-11-28
---

# When does a Work Unit need independently recoverable executor positions?

The current architecture asks for durable executor-facing continuity under replacement, without prescribing a kernel state variable or API for positions. September's bounded-object design explicitly superseded its own earlier strict executor-position hierarchy and used “attachment” for an exposed grant. Its foundational reduction allowed the continuity projection to omit a distinct Attachment Point object. November's evidence packet and engine vision retain the continuing position as a consumer requirement. These statements support separating three questions: whether there is continuing work, whether its executor-facing positions have independent replacement semantics, and whether a primitive type or stored object is necessary. [September bounded-object specification](https://github.com/rock-solid-sites/ASES/blob/741abfb905a270a90cab62213cf74fcda257b223/docs/architecture/EDASES%20Work%20Unit%20Component%20Design.md#a-current-canonical-definition) · [September foundational reduction](https://github.com/rock-solid-sites/ASES/blob/741abfb905a270a90cab62213cf74fcda257b223/docs/research/work-unit-0/Work-Unit-0-Foundational-Reduction.md) · [November engine vision](../../architecture/Execution%20Engine%20Vision.md#established-authority-and-continuity-requirements)

## A contract that distinguishes positions

Fix one continuing Work Unit with k addressable, occupied positions. Initially each position i has an eligible authority bearer Xᵢ. For every subset of positions, there is a legal history replacing exactly that subset, without changing the accepted work contents or retiring the other positions. Assume replacement invalidates old Xᵢ for a fresh protected effect at i and, absent independent later invalidation, preserves that effect eligibility of each untouched Xⱼ. The effect is otherwise valid. Ask for the fresh effect under the frozen original evidence after a declared failure. The positive case requires continuation at the steady recovery cut after environment prerequisites hold. An exact retry of an old accepted effect is a different observation. It can legitimately return historical success after replacing the bearer.

Let B be the set of replaced positions. An observer doing a counterfactual fresh probe for old Xᵢ must get allow exactly for i outside B. Two distinct B differ at some position and require different outcomes with identical original request evidence. If every trusted input at the protected boundary is equal after recovery, denial versus an eventual successful protected effect cannot differ in the required way. A nondeterministic implementation has the same set of possible behaviors on the equal inputs, so it cannot satisfy both universal guarantees. Therefore the reachable combined trusted evidence configurations must distinguish at least 2ᵏ profiles. Under these premises the information bound is k bits for this frozen cohort of old bearers. For a constrained family of replaceable subsets it is the ceiling of the base-two logarithm of the number of distinct reachable eligibility profiles. Interpreting protected effect eligibility by a terminal reply further requires reply-to-effect correspondence.

A bitmap indexed by the k stable positions meets the encoding bound for exactly this frozen cohort. It says nothing about the information needed to select new bearers, overlapping cohorts, non-reuse, live restrictions or previously accepted outcomes. For repeated replacement, per-position current-incarnation evidence is a sufficient construction under non-confusability and the declared currentness rules. Encoding the bitmap or an incarnation tuple into a single scalar changes its representation. It still preserves distinct independently observable authority decisions. [Currentness under reused tenures](Tenure-reuse-and-delayed-admission.md)

## The smallest discriminating pair

Take two positions of the same Work Unit. Replace X₁ with Y₁. Holding physical effect assumptions fixed, a fresh old X₁ effect must be refused while a fresh old X₂ effect must still be accepted at its own boundary. A single uniform decision that accepts only credentials in the one current Work Unit generation cannot do both with the original credentials. Bumping that generation denies both; leaving it unchanged accepts both. Reissuing X₂'s credential may implement a contract that permits interruption or mandatory refresh at all positions. A mediator that transparently leaves X₂'s old evidence usable can satisfy the stronger contract if it retains the differentiating state somewhere trusted. Restoring the same Work Unit tuple or serving an earlier replay does not prove that result.

The bound weakens when the contract weakens. A Work Unit with one executor-facing position can use a constant position label, paired with continuing Work Unit identity. Whole-unit replacement that always invalidates all original bearers needs only the initial and superseded profiles for this observation, even with many visible positions. Independent recovery of per-position outcome custody or restrictions may create other profiles. Merely assigning different roles or naming different positions supplies no reachability proof for independent replacements.

## Separating continuity from realization

A durable consumer reference can be decoded from stable scope and a position key instead of a separate stored record, when all required queries preserve that decoded identity across failure. If a human-facing label may be repurposed while old references still matter, the decoder must use a surviving distinction, an explicit retirement rule, or fresh scoped evidence. Aliases into the same authority relation can share the relation when all affected operations allow joint replacement. Exposed grants and allowing valid fresh appends are separate from whether the Work Unit exists sealed, empty, or inactive. None of this requires a resident executor.

The Rust adequacy audit at the fixed November pin fails to represent even the one-position W5/W6 seam. It says nothing about a two-position implementation. If independence is a chosen profile, first prove single-position replacement at the authoritative owner, then discriminate whole-unit revocation from selective replacement using the pair above, including rollback and the unaffected positive control. The profile choice, true owner seam, failure schedule and new run admission remain unsettled. [Pinned W5/W6 audit](https://github.com/rock-solid-sites/ASES/commit/8de559c78272bf639a82d284572e218a14cc1269)

**Disposition.** Preserve the architecture's consumer distinction where the selected profile can observe it. A case for a separate kernel position primitive still needs an enforcement or assurance advantage over equivalent guarded relationships with the same observations. The proof supplies a representation-independent information requirement under explicitly independent, non-disruptive replacement. It does not decide whether that stronger contract belongs in Kernel-0 or which owner should implement it.

## Mechanized obligations

The [Lean proof](proofs/IndependentContinuity.lean) verifies representation injectivity for reachable eligibility profiles, exact selective replacement of any list of positions, commutation of the profile updates, and impossibility of preserving two differently affected positions with a uniform revocation outcome. Run `lean docs/research/kernel-0/proofs/IndependentContinuity.lean` on Lean 4.19.0. The check exited 0 using standard axioms. Profile reachability and concrete evidence adequacy are premises of the application.
