---
title: When is a state partition too strong for Kernel-0 minimization?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/How-much-seal-state-survives.md
  - docs/research/kernel-0/Seal-state-under-policy-evolution.md
  - docs/research/kernel-0/Recovery-as-repeated-decisions.md
last_updated: 2026-11-28
---

# When is a state partition too strong for Kernel-0 minimization?

For a deterministic, fully specified interface, reference states can share one implementation state exactly when every future input gives the same observation sequence. That does not always hold for an interface that declares some inputs impossible in some states. A correct implementation can then use two states where every partition of the reference states requires three, by representing the same reference state differently according to how it was reached. This is a distinction about the declared environment and observation contract. If a caller is promised an explicit rejection, that input is specified. [Existing exact seal quotient](How-much-seal-state-survives.md) · [Closed covers in finite-state minimization, Kam et al.](https://www2.eecs.berkeley.edu/Pubs/TechRpts/1996/Archive/ERL-96-17.pdf)

## The fully specified case

Consider a deterministic sequential interface, with a response and successor for every state and input. Include status reads, authoritative grants, diagnostic denials and restart observations where required. Two states are equivalent if every finite input word gives equal response transcripts from both. This relation is a right congruence. Equal first-step replies and equal suffix responses imply that both successors are equivalent. Conversely the equality of all finite replies follows by induction for any relation that preserves a step and relates its successors.

The quotient is an exact representation of the required observations. Any implementation that maps two reference states to one and has no other distinguishing input or state must give the same response to every suffix. A distinguishing suffix therefore rules that merge out. Refining depth-k equality by immediate response and successor depth-(k−1) class computes the finite quotient. In an N-state model there can be at most N−1 strict refinements from the initial one-block partition. Once a refinement is stable it remains stable. Hence any distinguishable pair has a separating word of length at most N−1. A chain of N states that counts one step toward an absorbing state, reporting “done” only on an operation starting at that state, attains the bound. This is a bound in reachable reference states and specified input steps, not a small constant across implementations. [Sequential state observation, Moore](https://www.cs.cmu.edu/~cdm/resources/Moore1956-gedanken-experiments.pdf)

## Partial contracts require a different reduction test

Treat a state/input pair as absent only when the surrounding contract rules it out or truly imposes no response or successor requirement. Deterministic required steps still have one response and one successor. An implementation can use a **cover** C of reference states by compact states. Every relevant initial reference state must have a representative. A reference state may belong to more than one compact state. For each compact state c and input i:

1. Consider the required i-steps from all reference states covered by c.
2. If there are any, their outputs must agree.
3. Some single compact state must cover every required successor in that set. Choose that compact state as the runtime successor for c,i.

These conditions are sufficient by induction on required input sequences from related initial states. They are necessary for any deterministic implementation with a step-preserving relation: take the reference states related to each of its states. A reachable output history may assign multiple compact states to one reference state. Requiring a unique encoding of every reference state is an extra storage or recovery interface requirement. In particular, if recovery must reconstruct the compact state from the current reference snapshot alone, the overlapping cover may need additional evidence or a canonicalization step with its own correctness argument.

Mere pairwise compatibility is weaker than a cover. If some input is specified in a and c with conflicting replies and unrestricted in b, a can be compatible with b and b with c while a and c conflict. Compatibility is not transitive. It also does not say which single target compact state covers all successors of a chosen source group.

## A strict counterexample to partition-only minimization

Here is a three-state reference with two movement commands and one reply check. The dash means an input excluded by the contract. A move's reply is always OK when specified.

| State | Forward | Back | Read |
| --- | --- | --- | --- |
| A | B | — | 0, stay A |
| B | C | A | — |
| C | — | B | 1, stay C |

A and C cannot share a compact state because their read replies differ. Two compact states suffice with overlapping groups L={A,B} and R={B,C}. Forward goes to R from either group that has a required forward step. Back goes to L. Read replies 0 at L and 1 at R, each staying in its group. B tolerates either representation because Read is absent there and the movement transitions are covered. Both representations of B arise from required histories by moving forward from A or back from C.

Every two-class partition fails. If B shares A's class, applying Forward to A and B has successors B and C, which must share a class and do not. If B shares C's class, applying Back to B and C forces A and B to share a class. A full-shape mapping that returns a definitive `blocked` reply for Read on B additionally requires three distinct immediate read responses. The smaller implementation cannot be credited unless the read assumption is actually enforced.

## Application to a kernel elimination claim

A state elimination has to preserve every required future response, including effects that were committed before replacement and statuses consumed by another authority. Record whether an excluded input is physically impossible, denied by an upstream trusted gate, or merely absent from the selected traces. Only the first two can discharge a requirement of untrusted caller tolerance if the contract still admits the caller. Adding a new authority to inspect or migrate an intermediate state can make a formerly absent observation required.

For a proved total interface, a partition and distinguishing suffixes are exact certificates. For an actually partial one, compare closed covers and prove exclusion at the shared boundary. If an implementation relies on different histories leading to different encodings of one reference state, check crash reconstruction as an ordinary required transition. The minimal reachable implementation under that stronger contract may be larger. This is a model-level comparison method. It does not establish that a named Kernel-0 state, primitive or trusted mechanism can be removed in the native prototype.
