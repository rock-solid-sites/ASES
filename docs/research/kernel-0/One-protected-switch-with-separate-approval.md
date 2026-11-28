---
title: Can a single protected switch preserve independent approval?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/When-separate-checks-prove-one-legal-effect.md
  - docs/research/kernel-0/When-split-authorities-can-publish-separately.md
  - docs/research/astra-followup-20261125/frontier-comparison/ROUND2-COMPARISON.md
last_updated: 2026-11-28
---

# Can a single protected switch preserve independent approval?

The narrower November candidate allows an authorized executor to replace one inert data value. It also recognizes that giving a writer control over a co-located draft and approval would break separation of authority. The richer candidate allows a guarded batch against a coherent pre-state, and explicitly says that rights held by one controller do not establish consent by two independent subjects. These source claims leave room for an intermediate construction. A fixed protected switch can preserve separate authoring and approval while changing only one selected record. Whether it works depends on what has authoritative meaning before and after that switch. [Single-entry candidate, sections 2–3](../astra-followup-20261125/frontier-comparison/responses/round2-astra-high.md) · [Guarded batch candidate, sections 1 and 4](../astra-followup-20261125/frontier-comparison/responses/round2-sol-high.md)

## A profile that needs separate authorization but only one mutable selection

Consider a Work Unit whose consumers require a currently effective artifact that was independently approved for that exact publication. Authors must be able to edit candidates while the already published artifact stays available. Reviewers must be able to approve an exact candidate without acquiring the ability to edit it or select it. Initially either provision a qualified artifact or explicitly allow an inactive empty state. In this profile the publication record promises valid approval **at the publication cut**. A subsequent reviewer withdrawal may prevent future publication. It does not erase the earlier fact or immediately withdraw the already published artifact.

The authority surface can be implemented by the following conditional construction.

1. An authoring path inserts immutable candidates. Identity binds the exact artifact bytes and intended scope. No candidate becomes effective by insertion.
2. Distinct approving roles create authenticated evidence for the same publication proposal. Bind the evidence to the selected predecessor where applicable, the candidate identity, Work Unit and target, action and applicable policy incarnation. If a reviewer may withdraw a still-pending approval, include its live validity in the publication check. Merely holding two rights under one identity is insufficient when genuine independent consent is required.
3. A narrowly constrained owner step checks a coherent view of those facts and changes one protected selector to the chosen artifact and its retained evidence. All effective reads and protected uses resolve that selector or safely defer. An old selection and its evidence remain explainable after later candidate edits. The issuer and guarded sink must prevent bypass. Immutable staging and the selected evidence need custody across the declared losses.

Induction establishes that every effective selection has legitimate evidence for that artifact at its own publication cut. Candidate insertion and approval do not change selection. Every selector transition satisfies the invariant for the new record. Author and reviewer transitions cannot manufacture one another's evidence. If old approvals can be used only with the exact predecessor, a completed publication also invalidates competing old-predecessor attempts without erasing historical proof. This construction permits positive histories with ongoing draft work and two genuinely independent contributors. It does not imply immediate delivery or a fairness guarantee.

The selected record can be one data entry. The check that constrains its value and the binding of staged facts are substantive. An unrestricted replacement of that entry by any role cannot enforce this rule unless an independently justified mediator actually limits every such replacement. The original candidate explicitly leaves payload interpretation out of its kernel `Replace`. A typed fixed switch or a trusted interposed policy would be a specific refinement of the obligation. Conversely, support for arbitrary guarded multi-entry updates does not by itself exclude a proposal that omits one required approval or binds one to a different artifact. [Predicate factorization](When-separate-checks-prove-one-legal-effect.md)

## Where the reduction fails

**Live endorsement of the already effective artifact.** Change the contract so that a currently effective artifact must be backed by approvals that are still current. A withdrawal can now change effective eligibility without changing the selector. Keeping the earlier artifact unconditionally effective on a cached certificate fails. One option is to derive effectiveness from the current approval and withhold it when that check fails. But if independent withdrawal must complete, a qualified effective artifact must always exist, and the withdrawal leaves the entire qualified set empty, those three requirements are inconsistent at that cut. A larger transaction cannot create another party's approval. A live profile must permit a vacancy, have a qualified substitute, or constrain when the withdrawal can take effect. Independently safe continuity and independence of the approval act are then separate proof obligations.

**Independently authoritative publications.** If two owners' raw surfaces both claim independently readable current fields and the requested operation must switch both atomically, staging behind one selector works only if those surfaces honor selection or defer. If both continue exposing independently advancing current values, a read-new followed by read-old can refute the common switch. The solution is about the effect and observation contract. It does not prescribe where bytes or proofs must reside. [Atomic publication counterexample](When-split-authorities-can-publish-separately.md)

## Consequence for choosing a primitive profile

Count independent authority domains, independently observable accepted effects and tested failures before counting writable records. For the publication profile above, a fixed guarded selector makes the batch requirement unnecessary even though separate approvals remain essential. For user-level effects that other owners independently control or expose, the same reduction needs a correspondence proof at each owner. The native F3/F4 bridge would first have to specify whether its consumer wants one common current claim or separately typed historical and live facts. This remains a source and policy qualification question. No alternate architecture was selected or executed.

**Disposition.** Use a three-way discriminator when evaluating candidate transition sets. Ask whether approvals are historical or revocable at effect time, whether unselected material is truly non-authoritative, and whether every effective observer follows the protected selection. The construction demonstrates a conditional middle ground between unrestricted one-entry replacement and general batch mutations. It supplies neither implementation conformance nor a case for weakening independently required authority.
