---
title: Kernel-0 Multi-Domain Composition
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
consumed_by:
  - Kernel-0 generalization and re-minimization
---

# Phase 3 result: A3, bounded composition model

The smallest useful witness has two continuing domains A and B, each with its own
local work bit and old/replacement authority observation. These are consumer
partitions of `σ`, not Work Unit primitives. A separate reservation field in each
domain represents one shared resource; `reservationA + reservationB ≤ 1`.

Local bit flips read only their own authority and work. Reservation reads both
reservation fields and writes one; it needs local write authority but a coherent
view of the coupled invariant. Transfer reads both authorities and both
reservations, requires authority in both domains, and moves the resource in one
whole effect. Management authority is a trusted per-domain initial assumption;
replacement does not affect the other domain. Evidence scope is a trustworthy
ingress observation, not a caller-provided domain assertion.

`kernel0_composition_model.py` exhausts **432 states / 17,280 edges** with no path-
length cutoff. Crash/recovery can repeat arbitrarily within this finite state
space: availability changes while the whole authoritative projection survives.
There are **48 enabled unordered parallel steps** for the two independent local
flips. Their disjoint read/write footprints, unchanged admission in either order,
and equal simultaneous/AB/BA successor are checked separately from serial BFS.
Thus the evidence for independence is not merely an arbitrarily chosen global
serialization. A local operation on B also succeeds while A is down.

The finite result is in `Kernel-0-Composition-results.json`, including source
digest and concrete counterexamples. Reproduce with Python 3.10+ without `-O`:
`python3 docs/research/kernel-0/kernel0_composition_model.py --output PATH`.

## Removal attacks

| Removed obligation / added overconstraint | Confirmed result |
| --- | --- |
| Coherent joint admission | A and B each read empty reservations, then independently reserve their own row. Final `(1,1)` violates the shared invariant. Both local histories were individually valid. |
| Domain-scoped authority observation | Numerically identical evidence for B is incorrectly usable in A when the scope distinction is erased. Correct scoped admission denies. |
| Local independence | Requiring both domains to be up blocks a permitted B-local flip while A is down. This is an unnecessary availability dependency, not a new safety violation. |
| Whole joint commitment | Transfer `(1,0)→(0,1)` split into clear-A / set-B recovers `(0,0)` after failure between halves. The exclusion invariant still holds, but the declared whole effect and resource continuity fail. |
| Compatible recovered cut for a joint effect | Recover A from pre-transfer and B from post-transfer yields `(1,1)`. Individually authentic local views do not constitute a valid joint cut. |

A non-vacuous history reserves A, transfers to B, loses A's availability, changes
B-local work, recovers A, replaces A authority, rejects its old evidence, and
accepts its replacement. Recovery supplies only declared surviving authoritative
state, not a new grant. The model assumes that state is retained; this phase does
not prove a physically split persistence protocol.

## What composes, and what does not

For operations whose guards/effects/invariants have disjoint dependency footprints,
local coherent orders may be combined without an order between unrelated events.
Sharing a numeric authority label does not collapse domain scope. A cross-domain
proposal includes the relevant union of dependencies in its authoritative view;
it cannot ignore the other domain merely because the final write is local.
Acyclicity is required across all interacting commitments, not just separately in
each domain. The earlier three-way cycle finding remains applicable.

An atomic joint transfer couples its participants' recoverable cut. A domain can
recover independently only while preserving compatibility with completed joint
commitments. That is an additional obligation on the failure projection already
required by Phase 1, not a global coordinator object or universal total order.
An implementation can serialize all domains, but this evidence does not make that
necessary. Conversely, independently durable rows cannot silently promise joint
whole-effect recovery without an additional realization contract.

The existing `σ` already ranges over the combined authoritative dependencies.
No new semantic primitive is required. What changes is which facts belong in the
view and which commitments interact. Consumer declaration alone is insufficient:
actual read/write/authority/invariant dependencies determine the claimed locality.

## Adequacy, realization decision and gate

The graph's abstract `step` is atomic; satisfaction of its invariant alone cannot
establish concrete atomicity. Separate weakening code intentionally evaluates two
cross-domain guards against the same old state and combines their independent
writes. The transfer attack then checks a state that passes the invariant but is
neither permitted endpoint. These are attacks on refinement and model adequacy,
not just a restatement of the reference transition.

Bounds: two domains, two work bits, one shared reservation, at most two authority
observations per domain, no arbitrary delegation or higher-order conflict graph.
There is no cutoff theorem or general distributed-recovery protocol. The relation
retains state atomically across domain unavailability by assumption; physically
independent media, split failures during joint publication and network partitions
are not verified.

**A3 is a stable bounded semantic/model result, not a new concrete distributed
realization.** No additional toy implementation was selected: putting both domains
in the Phase 1 store would only restate its stronger serialization; a two-lock
volatile demo would leave the actual joint-recovery gap untouched. Establishing
independent persistent holders would require a new joint commitment/recovery
realization whose necessity and trust tradeoff have not been selected. Preserve
that gap rather than importing a coordinator under the name of composition.
This does not block the Phase 4 locality argument or re-minimization.

**WHY:** independent footprints commute while coupled admission/recovery produces
specific failures when weakened. **WHAT:** exhaustive bounded graph, unordered
step checks and explicit mutant counterexamples. **HOW CERTAIN:** evidence-based
**A3 (model only)**. **WHAT-NOT-TESTED:** general locality proof, physical multi-holder
recovery, global cutoff, independent review. Canonical Kernel-0 semantics unchanged.
