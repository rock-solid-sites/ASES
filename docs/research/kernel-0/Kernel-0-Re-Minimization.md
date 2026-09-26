---
title: Kernel-0 Re-Minimization After Stronger Profiles
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
  - Kernel-0-Generalization.md
  - Kernel-0-Refinement-Assurance.md
consumed_by:
  - Kernel-0 stronger realization direction
---

# Phase 6 result: stronger profiles do not justify a new kernel primitive

The original six distinctions remain the presently justified semantic candidate.
This is a stronger **reduction finding** from the new counterexamples, not a new
canonical definition or a proof that every possible kernel has one unique minimal
representation. The conditional generalization arguments do not remove the
implementation/refinement obligations.

## Removal audit

| Retained distinction or mechanism | Classification | Removal result / reduction |
| --- | --- | --- |
| Accepted authoritative meaning versus candidate material | Intrinsic to the base claim | Without it, speculative or stale material can change accepted meaning outside the guard. Durable preparation remains candidate material until commitment. |
| Proposed whole effect versus commitment | Intrinsic | Phase 1 torn image and Phase 3 half-transfer fail the declared effect; an invariant can still hold. Existing E already expresses the obligation. |
| Current eligibility versus past permission | Intrinsic | Stale-decision and old-ingress attacks fail it. No separate permission service primitive follows. |
| Trustworthy different observations for differently treated attempts | Intrinsic | Producer/position or domain-scope confusion admits old/wrong authority. A principal, context, endpoint or generation is a representation choice. |
| One coherent validity view and common acyclic order of interacting commitments | Intrinsic | Detached joint guards and incompatible whole-history snapshots fail. Ordering unrelated events remains unnecessary. |
| Continuing information independent of executor lifetime | Intrinsic to the declared base failure class | Required content cannot disappear with the producer. Its location/format is not intrinsic. |
| Recoverable commitment versus volatile publication | Optional holder-recovery profile | Removing it loses acknowledged work. It strengthens the existing commit/failure/observation contract, not the proposal alphabet. |
| Current recoverable cut versus authentic obsolete snapshot | Optional recovery profile, supplied by trusted substrate/mediation | Same-root restore after revocation demonstrably resurrects authority. A stored label alone cannot supply currentness. |
| Retained complete content across holder loss | Optional stronger failure projection of intrinsic continuity | Durable digest without recoverable bytes fails. Inline string, external immutable holder or other complete representation can supply it. |
| Committed-but-unacknowledged versus uncommitted | Existing commitment/observation distinction | Lost acknowledgement cannot undo commitment. Request IDs, deduplication and exactly-once do not follow. |
| Trusted recovery root, policy and initial management | Trusted initialization/recovery substrate facts | Removing them confuses unrelated work/bootstrap with authority. Root ID is one representation; it is not a freshness proof. |
| Reconstruction of concrete bearer | Optional continuing-recovery profile | Cold recovery can discard bearers. Continuing mode needs a trustworthy surviving binding; current rights alone cannot identify the bearer. |
| Supervisor's immutable endpoint/context association | Realization of trusted mediation | Necessary for this continuing implementation; not universally necessary. Its presence outside the erased service memory is explicitly in the trust boundary. |
| Consumed-context bitset / non-reused labels | Realization of authority non-confusability | Dropping the information in this witness permits reuse; another trustworthy distinction could replace the bitset. Finite exhaustion safely denies. |
| Durable effect obligation | Selected external-effect policy | Without it, a required consequence can be lost after source crash. Other external profiles may choose different authorization/cancellation semantics. It is accepted information within σ. |
| Immutable one-slot intent | Bounded consumer/realization choice | Monotonicity makes a prior committed-intent read safe for later delivery here. Mutable/cancellable obligations require a different ordering contract. |
| Trusted sink mediation and exact payload association | Trusted boundary for the selected external claim | Removing it permits irreversible effects without corresponding commitment. Sink descriptor ownership is one mechanism, not a kernel API. |
| Sink acceptance versus later observation | External-profile event/observation distinction | Accepted-before-revoke can be visible afterward. It parameterizes authorization meaning; it is not a new universal lifecycle object. |
| No cancellation after decision | Selected consumer policy | Removing it changes the selected guarantee. Cancellation is legitimate in another explicitly modeled profile. |
| Delivery acknowledgements / retry metadata | Not required by selected safety claim | Intent can remain indefinitely in this finite experiment. Duplicate effects are allowed. Safe reclamation would be additional work. |
| Idempotence, deduplication, compensation | Not retained | None is needed for this selected contract. They may be required by stronger consumer claims; compensation never retroactively authorizes an invalid effect. |
| Two domains / domain-scoped evidence | Consumer partition of σ and authority validity | Domain name is part of a trustworthy observation where labels otherwise collide. No Work Unit primitive follows. |
| Cross-domain whole view and compatible recovery cut | Existing guard/order/whole-effect obligations over a larger dependency support | Removing them admits double reservation, half-transfer or incompatible recovered cuts. No global coordinator object follows. |
| Global total order / global availability gate | Not retained semantically | Independent steps commute and B works with A down. A single lock is a stronger realization choice. |
| SQL transaction, rollback journal, FULL synchronization, serialized row | Trusted substrate plus selected realization | One sufficient implementation of whole recoverable commitment; not methodology or kernel ontology. Actual I/O refinement remains unproved by API-cut tests. |
| JSON, Python, SQLite, Unix sockets/processes, descriptor passing | Realization/runtime trust | Necessary to account for this experiment's evidence, replaceable in another realization. |
| Two content atoms, four contexts, one shared reservation, one delegation edge | Bounds/consumer policy | They are neither kernel objects nor cutoff theorems. Generalization limits are preserved in Phase 4. |
| Test gates, ghost histories, model state counters, result files | Assurance apparatus | No enforcement authority. They must never supply recovered implementation state. |

This table covers every retained distinction from Phase 1, every candidate
mechanism considered in Phase 2, the composition dependencies, and the concrete
mechanisms used by the experiments. Repeated rows share semantic obligations;
they do not increase the primitive count.

## Expressing all stronger profiles with the existing parameters

- **Authoritative view σ:** add only the information whose accepted meaning,
  permission, or invariant actually depends on it. Multiple domains and an
  obligation are values/partitions of that view, not new kernel object types.
- **Guarded whole commitment G/E/I:** declare the larger whole effect and check
  all current dependencies. Transfer and durable intent are consumer proposals.
- **Authority validity:** retain trustworthy non-confusable observations across
  the promised failures, scoped to the relevant permission domain.
- **Ordering:** include all interacting dependencies, including a sink boundary
  only when the selected claim requires current authority there. Leave disjoint
  transitions unordered.
- **Failure projection:** say which authoritative information survives or is
  reconstructible, and which observations/attachments are lost. Joint commitments
  constrain compatible recovery cuts.
- **Trusted mediation:** account for bootstrap, current storage, binding and sinks
  wherever they physically reside. Moving a fact outside a named component does
  not remove it from the assurance boundary.

## Minimal trusted boundary actually evidenced

The recovery realization trusts the finite consumer policy and sole guarded
transition path; configured initialization/root; surviving supervisor and endpoint
associations (continuing mode); complete current storage and SQLite's transactional
contract; Python/SQLite/VFS/Unix process, descriptor and filesystem semantics.
Cold mode does not require restoration of old bearers. The effect profile adds the
mediator, configured source/sink association and sink's irreversible acceptance /
retention contract. The two-domain result is model-only and assumes compatible
recovery; it does not shrink physical cross-holder trust by drawing two boxes.

This is the smallest boundary justified **for these realizations**, not an absolute
hardware lower bound. No proof of OS/runtime/storage correctness, protection
against a hostile supervisor, power-loss durability or adversarial rollback was
produced. Neither a verified transition core nor a lower-level rewrite would,
by itself, discharge current-storage or sink-mediation assumptions.

## Re-minimization gate

No tested counterexample requires changing the provisional Abstract Semantics or
adding a new Kernel-0 primitive. The substantial additions are explicitly selected
profile obligations and realization trust. A new persistent reference may be a
useful assurance artifact; it is not a revised methodology or production design.

**WHY:** each failed removal maps to an already retained semantic distinction
under a stronger declared profile. **WHAT:** Phase 1–5 counterexamples, positive
histories and conditional arguments. **HOW CERTAIN:** evidence-based reduction;
no universal uniqueness/minimality proof. **WHAT-NOT-TESTED:** alternative
realizations, unbounded concrete refinement, independent review and storage I/O
interruption internals. Proceed to Phase 7's bounded substrate experiment decision.
