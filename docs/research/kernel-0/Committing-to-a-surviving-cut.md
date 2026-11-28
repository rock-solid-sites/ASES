---
title: Where can a Work Unit acknowledge an append that must survive rollback?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Maintaining-a-recovery-stamp-online.md
  - docs/research/kernel-0/Reconstructing-a-cut-from-prepared-updates.md
  - docs/research/kernel-0/Transferring-the-accepted-prefix.md
related_documents:
  - docs/research/kernel-0/When-handover-order-must-be-fixed.md
  - docs/research/kernel-0/Fencing-after-membership-rollback.md
last_updated: 2026-11-28
---

# Where can a Work Unit acknowledge an append that must survive rollback?

A compact stamp can check an authentic offered cut, but it cannot help if the only trace distinguishing an acknowledged append is erased by owner rollback. Moving the stamp before acknowledgment prevents that gap only if the stamp identifies the accepted update and its material survives. This study tests a candidate with an explicit authority point between durable staging and optional local materialization. It advances the earlier updater-ordering obligation, without assuming the updater is a reliable recipient of notifications sent after commitment. [Online stamp boundary](Maintaining-a-recovery-stamp-online.md) · [Prepared-cut ambiguity](Reconstructing-a-cut-from-prepared-updates.md)

## Two independently necessary agreements

Fix the failure projection: a named owner image can roll back to a genuine earlier cut. The caller may disappear or lose its reply. Recovery has access to a protected witness and a declared surviving content holder. An accepted append must be visible to the successor, and a stable retry must resolve its outcome without introducing another accepted append. For this contract two checks cannot be collapsed.

1. **Decision before acknowledgment.** Suppose an append can acknowledge while all facts that distinguish its outcome from one merely staged append are still in the rollback domain or in a lost reply. Take a second history in which the same payload was staged without acceptance. Roll both owner images back, losing the differing evidence. Recovery receives identical data and must make incompatible decisions. The same argument applies to a completed observation that promised the write was authoritative. If the owner's actual effect and authoritative decision always survive, a separate witness can lag as a derivative projection. That is a different failure contract.
2. **Surviving content before a decision that relies on it.** A protected current decision that names a payload cannot reconstruct missing arbitrary payload bytes. Staging only on the rollback-prone owner leaves a gap between accepting the reference and making its target recoverable. Either the content needs a surviving prior placement, or acceptance must itself atomically preserve it.

These arguments do not require the two obligations to live in different components. They permit a protected append journal with embedded bytes, or an immutable holder plus a protected manifest. A count-only witness can be enough with a separately guaranteed immutable publication order. The test here permits request-specific acceptance and exact replay, so the witness selects the particular bytes instead of incrementing an undifferentiated count. [Prepared-cut result](Reconstructing-a-cut-from-prepared-updates.md) · [Lee et al., *Implementing Linearizability at Large Scale and Low Latency*, §4.1](https://sigops.org/s/conferences/sosp/2015/current/2015-Monterey/printable/126-lee.pdf)

## Candidate and proof boundary

Stage immutable content at a holder that outlives the owner rollback and guarantees retention for the duration of the promise. Staging may fail or be repeated. It gives no authority to publish. At one protected decision, check the current tenure and the original request identity, record accepted references in order, and record the exact retry receipt. A matching request for a committed identity may replay the historical receipt even after replacement. Reusing its identity with changed material returns a conflict. A fresh request from that old tenure is stale. Replacement is serialized with fresh acceptance in the same protected state. Reads use the accepted references as their authority. A local copy can be materialized or rebuilt from that prefix, and cannot independently announce admission.

**Induction.** Initially the accepted prefix is empty. Staging changes only the set of available candidates. Fresh acceptance extends the prefix with one already retained payload and one durable receipt. Replay, rejection and replacement preserve the prefix. Materialization and rollback of the local projection preserve the prefix and the placement promises. At each cut the ordered accepted payloads are recoverable from the protected references, and each recorded accepted identity corresponds to exactly one extension. The induction assumes complete mediation, non-forking serialized witness decisions, unique tenure incarnations, reliable custody and a stable binding between a reference and immutable bytes. Content digests in the fixture assume collision resistance. They prove neither custody nor authorization by themselves. The same shape supports a cut event for the prefix-preserving handover checker when that event really denotes the protected decision. [Prefix-preserving handover study](When-handover-order-must-be-fixed.md)

## Executed process-loss checks

Run `python3 docs/research/kernel-0/acknowledged_cut_witness.py`. The fixture uses SQLite 3.53.1 in three separate files on one host. A subprocess stages bytes, writes a protected acceptance, optionally materializes the local cache and returns a reply. The harness kills the subprocess at five barriers and explicitly restores the owner file to its saved initial bytes. It then replaces tenure 1 with 2 in the surviving witness. The resulting three checks are preservation of the pre-cut accepted prefix, exact retry under the old identity, and eligibility of the successor. It also exercises repeated old retries, a fresh stale append and a same-identity changed-payload refusal.

| Cut | Old value after recovery | Exact old retry | Visible original reply |
| --- | --- | --- | --- |
| After staging | Absent | Stale | None |
| After writing the decision, before SQLite commit | Absent | Stale | None |
| After witness commit | Present once | Original receipt | None |
| After writing the local cache | Present once | Original receipt | None |
| After success reply | Present once | Original receipt | Accepted |

Two negative controls fail at different links. The owner-first variant acknowledges after a rollback-prone write without committing the witness. After restoring the owner file, all three complete database files compare byte-for-byte equal to those of the history that stopped after staging. The replies differ. The unstaged variant acknowledges from the protected witness while the selected bytes were never persisted. Recovery rejects its dangling reference. The control establishes a missing-content failure, even though the authoritative reference and receipt still exist. [Fixture and controls](acknowledged_cut_witness.py)

**Outstanding.** The harness assumes protection of the witness and staged content rather than implementing physically independent failure domains. It models local subprocess kills, simulated rollback of one file and trusted fixture callers. It does not establish native engine conformance, real host or power loss, distributed witness and content agreement, concurrent staging or reclamation, external effects, or a complete authentication interface. Garbage collection is especially load-bearing: it must be impossible for a staging attempt or outgoing tenure to release bytes that a committed reference still requires. The current model resolves the ordering discriminator under explicit custody and effect-boundary premises. [Repeated retention results](Retaining-immutable-content-across-attempts.md)
