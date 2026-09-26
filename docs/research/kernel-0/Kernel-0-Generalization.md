---
title: Kernel-0 Generalization Beyond the Finite Witness
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Derived
canonical_repository: ASES
crosslink_issue: 567
depends_on:
  - Kernel-0-Abstract-Semantics.md
  - Kernel-0-Crash-Recovery.md
  - Kernel-0-External-Effects.md
  - Kernel-0-Composition.md
consumed_by:
  - Kernel-0 refinement assurance and re-minimization
---

# Phase 4: conditional parametric arguments and negative results

The following are hand-derived mathematical arguments over explicit abstract
rules. They are independent of the particular field/context counts, but their
premises are not established for every concrete realization. None is an inferred
cutoff theorem, machine-checked proof, or independent reviewer verdict.

## P1: old-grant non-resurrection, any authority population

Let U be the set of all admission observations ever issued in a domain and A the
current eligible relation. Distinguish this relation from physical principals.
Assume initially A⊆U; a grant introduces only an observation outside U and adds it
to U; invalidation removes it from A; other work transitions cannot add authority;
and recovery reconstructs the current committed A and U or an observationally
equivalent representation. All guard checks use current A. Domain scope is part
of the trustworthy observation when permissions are domain-local.

For any observation e invalidated at event j, induction over subsequent events
shows e remains outside A. Work cannot add it. Invalidation cannot add it. A grant
cannot add it because e∈U and U never shrinks. Correct recovery preserves the
relation and exclusion. Therefore old e cannot admit a later commitment, for any
finite number of contexts, replacements, work fields or crashes. This proof does
not require a stored U set: an alternative representation/mediator must establish
the same non-confusability premise. Deliberately granting the same *principal* a
fresh observation is different from resurrecting e.

The recovery premise is substantive, not derived from a label inside a snapshot:
Phase 1's same-root rollback violates it. A claim that excludes the old physical
producer after it receives fresh evidence also requires source binding, absent
here. An implementation that reuses the same admission observation while old
attempts can survive cannot use this theorem.

**Finite-representation limit.** If infinitely many replacements require a current
producer to be accepted, every old producer may retain and replay its evidence,
and only M distinguishable admission observations exist, the (M+1)th issuance
reuses an old observation. When the new holder is eligible, the old retained
observation is indistinguishable and must receive the same decision. This is a
pigeonhole contradiction, not a timing bug fixed by more bits. Indefinite progress
requires additional fresh distinguishing information, trusted source/lifetime
separation, proof that old attempts are gone, or a weaker claim. Safe exhaustion
by denial is permitted by the existing kernel. Restart increases opportunities
for lost no-reuse information; it does not create a new primitive.

## P2: whole effect, independent of field count

Let F be any finite set of fields and let encoding e and decoding d preserve the
entire claimed authoritative view: d(e(σ)) is observationally equivalent to σ,
including required bytes and authority distinctions. Suppose a substrate operation
atomically replaces e(σ) by e(σ′), recovery selects a current whole committed
value, and no authoritative read/success exposes the tentative successor. Suppose
also the proposal's G/E/I checks and replacement share one coherent current view.

Every normal commitment then decodes to the one declared successor σ′. A crash
before replacement leaves σ; after replacement leaves σ′; interruption of the
substrate operation admits only those endpoints. Induction over operations gives
a predecessor-closed sequence of whole effects. The argument quantifies over F;
it never reasons separately about the number of fields. Content indirection is
valid only if d can actually recover the required content within the same failure
claim. A digest of absent bytes fails the decoding premise.

This is a **conditional refinement lemma**, not a proof that SQLite supplies the
premise for every storage device, payload size, error or interrupted I/O. Atomic
replacement of the entire authoritative view is a sufficient realization, not
the unique one: field-level mechanisms can refine the same relation if their
observations/recovery are equivalent. Critical-state invariants alone cannot
substitute for E; Phase 3's partial transfer demonstrates that distinction.

## P3: a parametric ordering formulation

For an arbitrary finite history, include every dependency that can affect a
commitment's guard, effect or invariant: authority, work, outside facts, sink
acceptance where claimed, and real-time completion-before-initiation edges.
For a concrete versioned observation history, include read-from edges, relevant
write order, and anti-dependencies from a reader to writes that would invalidate
its observed version. Predicate/absence/aggregate reads count; ordinary field
write collisions alone are insufficient. Each event must have locally valid G/E/I
against its declared complete observed view.

If the resulting **complete** dependency graph is acyclic and its edges faithfully
encode those observations, take a topological order. Induct through that order.
For each event, every writer supplying an observed value precedes it, and a writer
that would invalidate that value follows it by the relevant dependency edge.
Consequently its admission/effect uses the same current view; its local G/E/I
validation remains applicable. This constructs a common coherent order of the
interacting set. Unrelated events need not be ordered in the declared graph.
Conversely, a required directed cycle admits no such order.

The completeness of the graph is a large proof obligation. Merely drawing an
acyclic graph or observing independently valid local histories does not establish
it. External facts whose order cannot be reconstructed must be trusted with an
explicit contract or excluded. This formulation is sufficient for each finite
prefix; infinite execution progress, finite predecessor assumptions and fair
scheduling do not follow. No count bound is used in the acyclicity argument.

**No small-cycle cutoff.** A directed cycle of length four has no cyclic proper
three-vertex induced subgraph. Checking every pair/triple therefore cannot establish
acyclicity of arbitrary populations. `kernel0_generalization_checks.py` preserves
that negative witness. The original three-event exploration remains bounded.

## P4: locality by non-interference

Let two initially admissible transitions t and u have declared read supports R and write supports W,
including all semantic invariant/authority dependencies. Assume a transition's
admissibility and written values depend only on its read support and it changes
only its write support. If Wt∩(Ru∪Wu)=∅ and Wu∩(Rt∪Wt)=∅, then t leaves u's admission
and computed writes unchanged, and conversely. Their writes are disjoint, so
componentwise t(u(σ)) = u(t(σ)). Both remain admissible in either order. Other
domains' state is untouched. This is a direct commutation proof for any number
of domains; it justifies leaving such events unordered.

This is a sufficient locality condition, not a complete test of commutativity:
some overlapping operations also commute. A shared conservation predicate creates
a read dependency even when implementation code forgot to read it. A cross-domain
operation enlarges the relevant support and may require a common view; it does
not introduce a global total order among everything else. Recovery projections
also have footprints: a completed joint effect forbids combining incompatible
local cuts. The theorem does not make independent media atomic.

## P5: delegation depth is an unproved consumer extension

The witness's one-edge cascading policy does not imply arbitrary-depth delegation
safety. If an eager invalidation algorithm revokes only immediate children, a
three-node chain root→child→grandchild leaves the grandchild active after root
revocation. If admission checks only the leaf's stored active flag, its credential still
admits. Checking every parent edge could instead reject the incomplete revocation;
that also fails to supply the intended successful transitive invalidation. The
executable negative witness confirms this simple extension failure;
it is not a failure of the actual depth-one implementation.

For a finite rooted acyclic delegation structure, effective permission can instead
be defined as the intersection of rights along a still-valid path from a trusted
root. Invalidation removing that path then removes effective permission at any
depth by induction on path length. Eager transitive cascade and guarded path
validation are possible mechanisms. Multiple parents, cycles, independently
revocable paths and reconvergence require an explicit consumer policy before
extending that argument. Kernel-0 does not select one.

## Assurance decision

The four narrow conditional arguments above materially clarify what must be
proved: current recovery, complete dependency observation, whole encoding, and
trusted non-confusable admission. A new formal language would not establish those
concrete premises merely by encoding them as axioms. Phase 5 should instead attack
**complete implementation histories crossing holder loss**, where pointwise cut
checks can miss incompatible ordering of several pending/acknowledged operations.
A separate whole-trace refinement checker can decide a concrete finite proposition
not already settled by isolated endpoint tests. Storage-internal crash consistency
remains the largest substrate gap and is kept explicit for the realization decision.

Run `kernel0_generalization_checks.py --output PATH` for the negative witnesses.
It also checks disjoint-flip commutation through five Boolean fields as a sanity
check; that finite enumeration is not the proof of P4. The hand arguments, their
premises, and their limitations are the Phase 4 result.

**WHY:** replacing tested bounds with explicit inductive/commutation hypotheses
separates semantic arguments from implementation evidence. **WHAT:** P1–P4 hand
arguments, P5 limitation, and executable negative witnesses. **HOW CERTAIN:**
conditional mathematical derivations, not machine-verified or independently
reviewed. **WHAT-NOT-TESTED:** premise satisfaction by arbitrary implementations,
cutoffs, arbitrary delegation policies, storage internals and infinite progress.
No semantic changes. Proceed to Phase 5's implementation-history discriminator.
