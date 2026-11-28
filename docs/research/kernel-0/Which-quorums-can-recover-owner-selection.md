---
title: Which quorums can recover a selected owner cut?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Recoverable-owner-selection.md
  - docs/research/kernel-0/How-independent-are-authority-checks.md
  - docs/research/kernel-0/Custody-at-an-admission-closed-cut.md
last_updated: 2026-11-28
---

# Which quorums can recover a selected owner cut?

Multiple replicas can keep a protected selection readable through loss. The required intersections depend on whether recovery needs to find an already certified decision, whether replicas decide the commitment themselves, and whether the recovery set comes from a different membership. A quorum of genuine preparation statements cannot attest a final selection. [Selection witness](Recoverable-owner-selection.md)

## Recovering an already certified and retained decision

Assume a trusted non-forking issuer of authenticated selection certificates. A certificate binds scope, ordered generation, selected candidate and phase. At a recovery cut, either the selector is quiescent or a separately proved protocol defines the appropriate ordered cut. Every selection the contract requires recovering has its certificate retained in a write set W. A sufficiently late truthful reply by an honest member of W returns that certificate or a newer authentic one certified under the same semantics. Newer candidates merely staged or voted upon are distinguishable from selections. Recovery sees a response set R. Let F be the actual failed domains, with replica identity mapped to those domains.

**Exact support condition.** The one-shot result is determined by the returned certificates if every allowed (W,R,F) has an honest retained member in W∩R. Then the latest required certificate is present or superseded by a genuinely selected certificate. Use the highest certified generation under the declared cut. Authenticity and generation order are load-bearing. A relay that can return an older certificate forever violates an honest responder premise. Complete content and dependency custody are separate from knowing the name of the cut.

If an allowed triple has no honest witness in W∩R, consider one history with only the previous selection and one with a newer selection completed exactly to W. Let the newer candidate bytes be staged in both. Honest responders outside W need not yet learn the outcome. Failed overlapping responders can omit it. The same returned older certificates now require choosing different cuts. This establishes necessity in the specified black-box model where other information cannot distinguish the selections. The support condition does not define a protocol for electing the trusted issuer or publishing the certificate. In particular an issuer must keep a decision recoverable before others can use it as authoritative. If a signed candidate can escape before the promised retention is established, the proof does not cover that exposure.

## Fixed membership and distinct failure domains

Let all write sets of size w and response sets of size r be allowed among n independently faultable named replicas. Any two sets intersect in at least max(0,w+r−n) members. The bound is attained by using disjoint members until the universe is exhausted.

- **Crash/omission with R drawn from live responders.** Ordinary intersection is sufficient and necessary, so w+r>n. If each phase must be able to finish with f unavailable replicas, require w,r≤n−f. This has a solution exactly when n≥2f+1.
- **Up to f misleading responses.** A member of R may claim old state despite having participated in W. At least one honest shared member is guaranteed when w+r>n+f. When any f replicas can also withhold their responses or storage participation, the other inequalities still apply. A solution exists exactly when n≥3f+1. Authentic issuer certificates prevent false selection fabrication. This result addresses retrieval of an existing decision under these assumptions. [Authenticated data and Byzantine quorums, Malkhi and Reiter](https://malkhi.com/files/byzquorums-STOC1997.pdf)

Replica names with a shared fate cannot simply be counted as independently retained evidence. Replace f names with the actual allowed sets of failed domains, then apply the support condition directly. Similarly these counting rules do not establish a linearizable concurrent register. An implementation spanning reads and writes needs a protocol that deals with their timing, versions and partial propagation. [Atomic registers in message passing, Attiya, Bar-Noy and Dolev](https://groups.csail.mit.edu/tds/papers/Attiya/JACM95.pdf)

If independent replicas **decide** competing values for the same slot, retention alone does not prevent them from creating conflicting certificates. With equal certificate threshold t and an honest durable single vote per scope and slot, every pair of threshold sets must meet in an honest replica to rule out conflicting certificates by intersection. The intersection assurance is 2t>n+f. Validation of a single proposed effect by t checkers has a different threshold, t>f, if every honest checker rejects that invalid effect. Authentication, common policy revision, per-effect completeness and the actual effect boundary remain obligations in both cases.

## Direct reads across membership changes

Let U be the old replica universe and V the new one. Allow any old write quorum of size w drawn from U and new recovery quorum of size r drawn from V. The minimum overlap is

```text
max(0, w + r − |U union V|).
```

For necessity count members in the union. For attainability each set first uses as many members exclusive to its own universe as it can. Within U∩V, choose the required remaining members as disjointly as possible. This realizes the stated value. Consequently the same old decision can be unreadable from the new membership even with no fault, despite each membership separately satisfying a majority rule.

This condition constrains **direct** reads from the new roster, without additional transfer evidence. Another protocol can establish an authoritative new base by securely copying the old selected cut and its proof, binding that transfer to a decision that closes old issuances before installing the new configuration. A recoverable certified transfer can allow disjoint administrative memberships. If the old set can continue issuing acknowledged selections after the copied cut, the copy is only a prefix and the direct-read impossibility reappears for the later decisions. Even a correct selection transfer does not carry missing material by implication. [Final extent and custody](Custody-at-an-admission-closed-cut.md) · [Admission and membership](Fencing-after-membership-rollback.md)

**Disposition.** The current native witness's in-memory F4 CAS supplies none of the newly assumed retention quorums or F3 selection certificates. A stronger realization can reuse established register/consensus mechanisms under their applicability assumptions. The research decision to qualify is which failure and progress contract the protected owner selection needs. Exact minimal supports above permit a known special-purpose placement without requiring a general quorum service. No runtime or configuration change follows.
