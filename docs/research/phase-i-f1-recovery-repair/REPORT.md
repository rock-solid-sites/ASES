---
title: F1 Recovery Repair and L5 Writer Exclusion
program: EDASES
layer: Research
document_type: Investigation
status: Experimental
authority: Derived
last_updated: 2026-11-06
---

# Confirmed defect and repair

The F1 counterexample is reproduced independently of PR #10's harness. The fault is
in the experimental C11 wrapper's configuration/write semantics: a missing tuple lets
the core content UPDATE commit alone, while a supplied tuple is rewritten on **every**
state write, including unrelated restrictions. The inherited finite authorization core
and SQLite do not enforce that wrapper's extra accepted-evidence contract.

An isolated [repaired_service.py](repaired_service.py) reuses the original core,
transaction, query, reader and kill gates. It admits changed content only with an
explicit subject-bound, structurally valid acceptance bundle. A new same-byte opaque
world requires an explicit acceptance; a configuration change or unrelated operation
never rewrites existing observations. Unchanged-content reacceptance without a new
bundle preserves its valid existing pair.

From explicit variant preparation onward, all actually accepted pairs remain in one
insert-only retention table. Preparation seeds the currently available original pair;
it cannot reconstruct observations already discarded by the original implementation.
This
small additional representation meets the instruction not to discard old observations;
it is not a new authority rule or general event log. Exact duplicates share a row.
An explicit preparation step validates and retains an existing original pair, or
prepares a trusted empty initial store. Ordinary recovery performs no schema creation,
state reset or evidence reconstruction from an oracle.

The linearization point remains the **inherited SQLite COMMIT**. The core content,
selected observation pair and newly retained pair are written in its existing
BEGIN IMMEDIATE transaction. Missing/malformed/mismatched bundle denial preserves all
rows; failed INSERTs roll everything back. A prepared SIGKILL recovers the old pair;
a post-COMMIT/pre-ACK SIGKILL recovers the new pair with the old observations retained.

The derivation, exact rules and scope are frozen in
[REPAIR-CONTRACT.md](REPAIR-CONTRACT.md). The comparator is pinned Phase-I-Closure
§3/§7 C1/C7/C9/C11/C12, not PR #10's interpretation. Original C11 explicitly excluded
general immutable-content/consumer assurance; this investigation extends its wrapper's
tested behavior, rather than retroactively claiming its five original cases failed.
The [exact added-service diff](evidence/analysis/repair.diff) and Git history preserve
the implementation change. Original source/evidence and existing branches are intact.

## Independent verification and before/after disposition

[probe.py](probe.py) is a fresh socket/process/SQLite harness. [check.py](check.py) imports
no acceptance logic, old checker or old harness. It decodes hashed raw rows, compares
actual read-only SQLite files, checks bundle meaning and retention, inspects real
transaction/gate/process evidence, and distinguishes instrument errors from defects.
It is a separately derived checker by the same investigator, **not clean-room or
cross-family review**.

| Property / discriminator | Original pinned source | Isolated repair |
| --- | --- | --- |
| Cold changed-content accept without a new bundle | COMMIT, incompatible old observations | Whole denial; old pair and archive unchanged |
| Cold changed-content accept with valid new evidence | Valid current pair | Valid pair; previous observations also retained |
| Recovery reads without original observation input | Useful reads | Useful reads, no evidence rewrite |
| Unchanged-content reaccept without new bundle | Useful COMMIT | Useful COMMIT preserving the existing pair |
| Unrelated restrict with a configured future bundle | Accepted evidence unexpectedly replaced | Restriction commits; evidence remains exact |
| Invalid acceptance then valid acceptance | Valid later operation observed | Intermediate readback unchanged; valid later operation succeeds |
| Null/list/wrong subject/non-string subject/missing or extra field/non-string field | Not claimed from original experiment | Whole denial without data mutation |
| Stale-subject bundle after accepting B | No general binding guard | A-subject bundle cannot be used for B, including unchanged B reacceptance |
| Different opaque evidence worlds with identical bytes | Distinct current worlds possible, no retained-pair archive | Both required worlds retained; explicit acceptance selects the new world |
| Duplicate requests and repeated recovery | No exactly-once claim | Existing pair/history unchanged; no new authority or duplicated retained pair |
| Failure in current-pair INSERT or retained-pair INSERT | Additional archive not present | SQL rollback preserves complete old state; fresh-holder valid operation succeeds |
| Process kill before / after COMMIT | Inherited selected evidence only | Old/new whole pair plus required retained observations, no ACK fabrication |
| Incompatible original state / missing variant schema | Original query can expose incompatibility | Explicit preparation/refusal changes no old rows; recovery cannot silently bootstrap |

Six original histories completed. The independent checker rejects exactly the
missing-bundle and non-accept rewrite histories. **24 repaired histories satisfy the
tested contract**, including valid neighboring cases, and five altered-evidence controls
are rejected. A live implementation mutant removes only the missing-bundle admission
protection; it executes a real incompatible COMMIT and the checker rejects it.
Raw runs and verdicts are under [evidence](evidence/analysis/repaired.json).

`original-01` preserves an execution-sandbox Unix-socket EPERM. It is infrastructure
failure, not a product verdict. The first original-checker output is also retained:
the earlier capture lacked a newly added intermediate-reader field. The checker now
uses that earlier denial's actual reply state/observations and distinguishes it from
the newer repair's stronger intermediate SQLite readback. No original data was edited
to manufacture evidence. The independently reproduced original defects remain two.

Intentional compatibility change: a legacy, **unbound** `observations` configuration
cannot authorize a changed-content acceptance in this variant. Callers must explicitly
provide the proposed subject and tuple. Unrelated operations and reads remain functional.
This is not a drop-in production migration or an ASES-wide API decision.

# L5 comparison, after F1 verification

[L5-PLAN.md](L5-PLAN.md) was committed after F1 verification and before L5 changes.
The separate [L5 variant](l5/worker_variant.py) wraps the original pinned worker/manager;
original policy and filesystem commit helpers are unchanged. Initialization remains
the original style of trusted test-only accepted-object fixture, not native F3 ingress.

The original overlap counterexample was reproduced: A prepares moved record2, B
activates old C-under-P into the same record name, and A ACKs its move although cold
state remains under P. A matching receipt hash does not establish the move's meaning.

| Discriminator | Process-lifetime exclusive writer | Atomic generation reservation |
| --- | --- | --- |
| Contender while owner pauses after record preparation | Refused before READY | Starts read-only; mutation denied because old generation reserved |
| Resume owner, then cold selection | Whole move to Q with C/D read ceilings | Same permitted move |
| Uninterrupted move then separate activation | Both operations succeed | Both succeed |
| Owner killed/reaped before selector publication | OS releases lock; fresh writer moves from old whole state | Persisted reservation conservatively blocks progress |
| Owner killed after selector publication | Fresh activation of new whole state succeeds | Next generation can be reserved and activated |
| Competing original unguarded writer | Guard bypassed; wrong move ACK reproduced | Guard bypassed; wrong move ACK reproduced |

Eleven L5 histories were checked from exact record/object bytes and process frames,
including an independently rejected well-formed wrong-parent control. Within the
**cooperative all-writer, stable-root/inode premise**, the lifetime lock is the smaller
tested candidate and provides simpler recovery after actual process death. The
generation approach adds persistent claims and a recovery/progress obligation.

This comparison does **not** implement atomic compare-and-replace of CURRENT. The
generation contender uses an actual O_CREAT|O_EXCL reservation, not a detached
check-and-os.replace mislabeled CAS. Direct CAS remains an alternative specification:
conditional current-state validation, immutable prepared identity, publication and
crash outcomes must have one defined atomic relation. Adding a second independent
generation database would introduce another coupled commitment and is not justified
as the smallest repair here.

Both tested guards fail against a writer that does not participate. Hostile process
exclusion, lock-inode custody and enforcement of the launcher boundary remain open;
the result is not native confinement or a safe claim about arbitrary same-UID writers.

## Reproduction, evidence and remaining obligations

[reproduce.sh](reproduce.sh) sequences original comparison, repaired histories, evidence
controls, expected mutant rejection, and only then L5. It writes a fresh capture.
Source pins: F1 `29ec3960c4c60dfb5d5f76d1c5dba7d2ea32d38a`; L5
`51b34aface9340b7e6821b8c40dc62ca38da15e2`. Exact original dependency files are retained
in the unchanged PR #10 source capture. New sources, hashes, raw SQLite/SQL/process
evidence and short reproduction results are retained on this branch.

WHY: admission now validates the evidence binding before the single local commitment;
unrelated configuration no longer changes accepted evidence. WHAT: before/after native
process runs, independent row readback, rejection controls and an executed mutant.
HOW CERTAIN: supported within the finite local experiment. WHAT-NOT-TESTED:

- Semantic truth, source authentication or external-world freshness of supervisor-supplied
  opaque strings. Stable same-subject evidence is not inherently stale; no timestamp
  expiry/nonce authority policy was invented to claim universal freshness detection.
- Physical power loss, malicious host/storage writers, compaction/capacity, production
  schema migration, multiwriter F1 response linearizability or complete formal refinement.
- Host-protected L5 confinement, arbitrary bypass routes, direct atomic CURRENT CAS,
  cross-component identity/lifecycle repair or changes to Kernel primitives.

Next proof obligations, in order: independently review the exact repair contract and
retention representation; validate the trusted acceptance-input producer's truth and
applicability; specify capacity/disposition and production migration if adopted; prove
F1 response/refinement behavior beyond the finite single-lane profile; enforce L5
writer participation and stable-root custody before promoting that guard. No broader
architecture or global lifecycle change is authorized by these findings.
