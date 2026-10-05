---
title: Kernel-0 Ingress Reduction Independent Review
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Derived
canonical_repository: ASES
depends_on:
  - Kernel-0-Direct-RTL-Independent-Review.md
consumed_by:
  - Kernel-0 timing-reduction research
last_updated: 2026-10-05
---

# Kernel-0 Ingress Reduction Independent Review

## Reviewed artifact

The frozen ingress-reduction artifact is commit
`ac9d128e984dddecbbf08c810a9cfc53e9754ac9`, derived from the frozen direct-RTL
baseline `c03bf1c470e54f51c299cb3347c547eeeae0e5ce`.

This record preserves the independent post-build assessment of whether the
fixed protected-lane interface both preserves the declared bounded behavior and
constitutes a genuine reduction of the dynamic ingress-classification premise.

Exact prompts and raw verdicts are preserved under
[`reviews/ingress-reduction/`](./reviews/ingress-reduction/).

## Claim 1 — bounded behavioral preservation

> The fixed protected-lane realization preserves the bounded Kernel-0 transition
> behavior of the frozen direct-RTL baseline while removing the caller-supplied
> actor label and authenticity verdict, under the stated protected-lane and
> synchronous realization assumptions.

**Final status: SUPPORTED.**

The independent reviewer established the declared domain of all
invariant-satisfying legal states in the three profiles paired with all 148
authentic catalog proposals:

| Profile | Legal states | Comparisons | Mismatches |
| --- | ---: | ---: | ---: |
| independent | 8,449 | 1,250,452 | 0 |
| coupled | 6,337 | 937,876 | 0 |
| exclusive | 1,921 | 284,308 | 0 |
| **total** | **16,707** | **2,472,636** | **0** |

The domain includes 19 legal but unreachable states. Supporting evidence also
covered the all-input mapping over `2^60` lane/payload combinations, the raw
stale-lane attack domain, 618 clocked cycles, three boundary proofs, three
synthesis-equivalence proofs and five detected ingress mutants. The unchanged
direct-RTL baseline rerun retained its 4,945,272-vector PASS.

The new interface has no caller-supplied actor field or authenticity verdict.
Actor identity is determined by the selected protected lane and authenticity is
fixed inside the selector.

## Claim 2 — genuine structural reduction

> The realization eliminates the dynamic caller-carried actor/authenticity
> classification rather than relocating an equivalent runtime classifier, while
> retaining the bounded behavior; the residual ingress requirement is protected
> non-confusable source lanes, with synchronous timing retained separately.

**Final status: SUPPORTED.**

The second independent reviewer reproduced the frozen suite and then constructed
independent SAT, synthesis and differential checks.

The fixed selector synthesized standalone to ten combinational cells, with no
flip-flops, memories, processes, routing table or runtime configuration. Independent
all-input checks established that:

- submission occurs exactly for one-hot lane selection;
- the selected lane determines the actor value;
- the authenticity bit is always true on submitted proposals;
- the manager actor requires the manager lane;
- unselected payload slices do not affect the proposal; and
- the 148 authentic templates map injectively to 148 lane/payload pairs.

A stronger independent refinement check covered all `2^22` raw state words and
all raw lane inputs for all four parameter combinations. Sequential differential
testing against the unchanged baseline and frozen oracle also found no
reduction-induced divergence and no stale-a0 commits.

No hidden runtime classifier was identified. The surviving ingress assumption is
therefore the one stated by the artifact: sources that must receive different
authority treatment must remain non-confusable at the protected lane boundary.
The experiment does not prove the physical enforcement of that boundary.

## Interface narrowing

The former 148 false-authenticity proposal variants have no representation on the
new interface because authenticity is no longer caller data. Their baseline
outcome was denial, and the frozen baseline regression retains coverage of them.

This is an intentional interface reduction, not an omitted new-interface case.

## Inherited out-of-domain discrepancy

The second reviewer found a pre-existing discrepancy outside the declared catalog
comparison domain. For some raw non-catalog proposal encodings, the frozen Python
reference can accept combinations that the frozen RTL `wellformed` gate denies.
Examples reported include nonzero unused `other` fields for operations such as
`restrict`, `resume`, `pair`, `set`, and `flip`.

Independent differential testing showed that the ingress composition remains
identical to the frozen RTL on these raw words. The discrepancy therefore predates
and is not introduced by the ingress reduction.

This finding does **not** change the supported verdicts because the established
claims quantify over the declared catalog/compared proposal domain. It does forbid
silently strengthening the result to a claim that the RTL and Python reference
agree for every raw 15-bit proposal word.

The discrepancy should remain a separate follow-up question: either malformed/raw
wire encodings are explicitly outside the abstract proposal relation, or the
reference/wellformed relationship requires a future clarification. No correction
is made as part of this review record.

## Other reproducibility observation

The reviewer reported that synthesized netlist JSON hashes were not byte-stable
across independent reruns despite matching cell counts/types. This is evidence
hygiene only; no behavioral discrepancy was reported.

## Result boundary

The independent evidence supports the following bounded conclusion:

**Fixed protected source lanes replace the dynamic caller-carried actor/authenticity
classification without changing the declared bounded Kernel-0 behavior and without
introducing runtime classification, routing state, sequencing state or general
programmability.**

This is not elimination of trusted ingress. Protected/non-confusable source access
remains part of the realization boundary.

Synchronous timing is also unchanged. In particular, the current realization
still relies on a trustworthy whole-event boundary, coherent observation of the
current authoritative state and coherent publication of the completed successor.
The review makes no claim about asynchronous ingress, metastability, skew,
physical lane ownership, hostile reset, power loss or unbounded contexts.

## Next research gate

The next research task is to reduce the synchronous-timing assumption without
changing the already-reviewed Kernel semantics or treating the current clock as
intrinsic.

The research question is not merely whether a periodic clock can be removed. It
is to determine the weakest realization contract that still guarantees:

1. capture of one whole proposal rather than a torn or mixed proposal;
2. coherent observation of one current authoritative state;
3. publication of one whole successor rather than an intermediate state; and
4. only the ordering actually required between interacting commitments.

A future implementation experiment should follow only after that contract has
been derived and challenged independently.
