---
title: What makes authority checks independent under a common fault model?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Kernel-0-Evidence-Packet.md
  - docs/research/kernel-0/Recoverable-owner-selection.md
  - docs/research/kernel-0/Fencing-after-membership-rollback.md
last_updated: 2026-11-28
---

# What makes authority checks independent under a common fault model?

Two checks on one effect improve resistance to a fault only for a claim both actually enforce and a fault neither shares. A schema validator, a scope validator and a custody check can be valuable together while leaving a particular forbidden effect dependent on just one of them. Two implementations of the same check may also rely on the same broken currentness source. This note makes the historical assurance-diversity question precise for a fixed effect and fault envelope. [Historical realization reduction, §6 and T6](https://github.com/rock-solid-sites/ASES/blob/d30679c3aaeb0a57f7ca160140a7c3174496ff04/docs/research/kernel-0/Kernel-0-Machine-Realization-Family-Reduction.md)

## Enumerate failure supports at the effect, not at the API

For a specified forbidden effect e, enumerate a complete finite family of physical or mediated paths that could cause it under the declared environment. An omitted write, import or disposal alias can invalidate the whole analysis. Along each path list the guards that would independently prevent **e**, including their observation of the exact resource, scope, authority and selected cut. A check that honestly accepts e because e violates a different property is absent from this list.

Let D be the available fault domains. In a fixed abstract snapshot, assume each relevant guard has a monotone predicate of failed domains under which the path can go through it. A failure can represent authority corruption, loss of currentness evidence, fail-open recovery, or another explicitly modeled premise. Mere unavailability that reliably closes the guard does not make it pass. The exactness result also assumes jointly possible faults and that the path can pass its listed guards together when the predicates hold. Where the predicates or paths are only upper bounds, the resulting analysis is a conservative assurance argument.

For any allowed fault set F, the forbidden effect can occur exactly when some path has all its relevant guards passable under F. An empty guard list is a path the claim does not protect. A guard that cannot pass under any declared F closes its path for this claim. The property is a familiar fault-tree construction. Writing it per actual effect keeps the temporal and identity questions from disappearing behind component names. [NRC, *Fault Tree Handbook*](https://www.nrc.gov/regulations-legislation/nureg-series-publications/publications-prepared-by-nrc-staff/sr0492)

When the domains can fail independently, one can compute the minimal fault supports by:

1. For each guard, represent the upward-closed passable sets by their inclusion-minimal members.
2. For one path, take every union of one minimal support for each relevant guard, then remove supersets.
3. Take the union of those families over all paths and again remove supersets.

For step 2, any F allowing the whole path contains a member of every guard's support family, hence one of the stated unions. Every such union permits the path by monotonicity and the joint-pass premise. Step 3 follows from the existential choice of path. This describes an exact certificate vocabulary. A minimum support by size or cost need not be efficiently computable. Even for a fixed single chain of guards, let each guard g be subvertible by any single domain in S(g). Finding the fewest domains meeting every S(g) is set cover on the guards. The reduction does not depend on dynamic path discovery. One concrete low-cost support supplies a falsifier. A successful proof against every allowed support still needs completeness of the guard and path model.

## Illustrative consequences

- Two required copies of the same check in disjoint fault domains yield a minimum of two failures for the covered effect, if either healthy copy independently forbids it. Two checks that both use one corruptible selected-authority record can have a one-domain support even if their implementations and reviewers differ.
- If one check enforces provenance and another an allowance cap, compromising the cap check alone can allow a correctly attributed but over-limit effect. Redundancy has to be stated per effect. Keeping both checks remains necessary for different claims.
- Two independent vetoes on the declared path do not help an alias that bypasses both. Two separate paths each guarded by a different single veto also do not require two failures. Fault resistance depends on how hostile choices and required checks compose, not on a count of repositories, processes or authors.
- Availability needs its own predicates. A guard can reliably prevent an unauthorized write under any fault and still be unavailable to a valid caller after one failure. A safety implementation that fails closed cannot claim fault-tolerant progress from the absence of an unsafe support.

No probability of independent failures is inferred from naming separate domains. Correlated failures such as a common policy revision, shared verification runtime, logical identity service, or shared loss domain must be represented when they are allowed. Static verdict independence also must persist through handover: an escaped old approval used after a grant expires can be a distinct pass condition at the actual effect, even if every check was honest at issuance.

## Reuse in assurance qualification

For one proposed elimination, ask which path, guard or premise actually disappears while required valid histories and the same allowed faults remain. A physically impossible alias can eliminate a path obligation. Proving a lower-level execution premise can discharge a guard's assumed behavior without changing the path. Adding a second checker that depends on the same external currentness source may leave all minimal fault supports unchanged. These are different outcomes.

**Disposition.** The native fixtures and the Lean statements in this directory can discharge bounded behavior or abstract logical implications. No joint physical fault-domain census is available to turn them into an independence claim. For a real candidate the cheapest next step is a source crosswalk of effect paths, exact checks and shared dependencies. A physical fault campaign or independent review comparison would require its own authorization. This argument can advance before choosing a native selector or granting new execution authority.
