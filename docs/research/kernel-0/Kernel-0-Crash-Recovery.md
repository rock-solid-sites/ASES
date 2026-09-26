---
title: Kernel-0 Authority-Service Crash and Recovery
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Derived
canonical_repository: ASES
crosslink_issue: 567
depends_on:
  - Kernel-0-Abstract-Semantics.md
  - Kernel-0-Verification-Obligations.md
related_documents:
  - Kernel-0-Realization-Experiment.md
consumed_by:
  - Kernel-0 external-effect and composition assurance
  - Kernel-0 stronger realization experiments
---

# Phase 1: derivation before mechanism

The baseline protects executor loss while a separate authority holder remains
alive. Here **all service-local volatile state disappears**. A survivor is trusted
only if explicitly outside that failure projection. No particular representation
is presumed. This is a stronger optional profile of the existing contract.

## What must survive, and why

Consider two completed histories with identical post-crash observations: in H0,
old authority is current; in H1, its replacement was completed. Recovery cannot
accept that authority in H0 and deny it in H1 if it observes exactly the same
facts. A hash, signature, old authentic image, or statement that a snapshot was
once committed does not distinguish these histories. Either the failure boundary
must preserve a **current committed whole view** (or information sufficient to
reconstruct an observationally equivalent view), or successful recovery with both
guarantees is impossible. Failing closed avoids stale acceptance but alone does
not establish successful continuation. This is an indistinguishability argument,
not a requirement for a clock, sequence number, log, or particular storage engine.

For this profile the surviving information must denote a cut of a coherent
commitment order, containing every completed commitment and any irrevocably
committed operation whose acknowledgement was lost. For interacting commitments
the cut is predecessor-closed; a whole composite contributes all of its effect
or none. Recovery may not resurrect a state just because it is locally valid.
Already superseded work/content is not required to remain current. No audit log
of every prior value follows from continuity.

| Retained distinction | Exact guarantee lost on removal |
| --- | --- |
| Recoverable commitment versus tentative preparation/publication | A successful acknowledgement followed by crash can lose accepted work. Tentative bytes alone cannot justify a success reply or an authoritative read. |
| Current recoverable cut versus authentic stale image | A completed replacement/revocation can roll back, restoring stale authority. An old valid image is insufficient. |
| Whole coherent cut versus individually valid fragments | Replacement rights and work/content can recover from incompatible times; a composite may recover only one field. |
| Required accepted content versus a surviving name for absent bytes | Continuation cannot consume the accepted content after both producer and service memory disappear. A declared surviving content holder suffices; inline bytes are not mandatory. |
| Current authority relation versus a concrete bearer | An authority table can survive while every endpoint disappears. Reconstructing an endpoint by caller assertion lets old or unrelated producers impersonate current authority. |
| Committed outcome versus knowledge of outcome | Treating no reply as noncommit can roll back a real commitment; blind retry can repeat an effect. No unique processing promise follows. |
| Trusted recovery root/policy versus data asserting its own origin | Wrong-store or fresh-bootstrap confusion can silently substitute unrelated work or reopen old authority. Missing/unreadable state cannot mean authorized creation. |

The first, third and sixth rows refine *one* guarded whole commitment and its
observation/failure projection, not three new kernel primitives. Currentness and
root authenticity are distinct: the right root can still supply an old valid
image. A monotone label inside a rolled-back image cannot establish freshness on
its own. There is no claim against adversarial storage rollback without a
surviving independent trust fact that excludes it.

## Two recovery claims

**Cold recovery:** preserve work, accepted content, consumed authority distinctions
and current relation; drop all old attachments. A trusted management recovery path
can withdraw/replace the orphaned authority and attach fresh execution. No old
endpoint is accepted, and no producer assertion reconstructs it. It is not
necessary to reproduce concrete bearers or revoke automatically on crash.

**Authority-continuing recovery:** surviving producers may reattach to their same
authority observations; the recovered relation judges them. A trustworthy
association outside erased service memory must distinguish old and replacement
observations. It may be a surviving trusted mediator, a retained binding, or other
non-confusable evidence. Restoring rights by position alone is insufficient.
Continuing recovery therefore has an additional observational/availability claim;
it is not equivalent to cold recovery. Both share the same guarded transition
semantics. Physical exclusion after obtaining genuinely new evidence is still a
separate claim.

A submitted pre-crash request is candidate material, not authority. It may be
lost before commitment or resubmitted; every new attempt is admitted against the
recovered current view. No persistent request queue is necessary for this safety
profile. A committed-but-unacknowledged operation is retained, but the client need
not learn its result. Durable request identifiers and deduplication are therefore
not required. Existing accepted bytes and current work are necessary; speculative
candidates are not. Neither epochs nor transaction records are intrinsic.

## Adequacy target before realization

Use the original consumer policy/reducer as an oracle, extending only failure
projection and observation events. Bound concurrent pending requests explicitly;
exercise both orders of replacement/work, invariant-conflicting work, composite
fields, content acceptance, root substitution, repeated recovery, and replay.
Keep the checker's semantic commitment history outside the modeled service; it is
an oracle and may never be recovery input. Explore crash before preparation,
after preparation, after recoverable commitment, and after acknowledgement.
Weaken persistence/currentness/whole-cut/content/binding/root/commit-knowledge and
validation order separately. A passing invariant alone is inadequate: include
successful post-recovery content use in both profiles.

WHY: indistinguishable surviving observations cannot support required different
future permissions. WHAT: current abstract semantics plus the explicit stronger
failure projection and counterhistories above. HOW CERTAIN: conditional semantic
argument; model and concrete evidence pending. WHAT-NOT-TESTED: storage, runtime,
physical source binding, independent review and unbounded refinement.

## Phase 1B result and adequacy attack

The finite projection in `kernel0_recovery_model.py` explores **7,502 states and
12,457 edges to closure in 24 fixtures** (12 scenarios × two recovery profiles,
at most two crashes and three requests). The original finite policy remains
unchanged and supplies a separately implemented transition oracle. Ghost committed
state checks the projection and is never supplied to recovery. All ten weakened
variants fail; BFS retains shortest traces within each fixture, plus explicitly
acknowledged variants where applicable. These are fixture minima, not global
counterexample-minimality or cutoff claims.

The ten removals cover early success, same-root rollback, torn composite, absent
accepted bytes, work/authority mixed cut, producer association confusion,
forgetting unacknowledged commitment, wrong root, detached validation, and loss
of consumed authority distinctions. Non-vacuity now requires content 1 accepted
*before* a crash to be consumed after recovery. The first draft admitted a weaker
witness with all useful work after recovery; self-review repaired that test.
A first no-reuse attack was masked by the consumer's exclusivity guard; changing
its prefix from replacement to revocation exposes reuse for its intended reason.
These harness corrections are not counterexamples to Kernel-0.

Adequacy limits: the model starts from established work and one grant; bootstrap
origin is an external assumption. Fixture closure is not the full product of all
148 original requests. No byte-level storage behavior, arbitrary repeated crashes,
all observer schedules, hostile roots, or arbitrary policy is exhaustively tested.
Two-field coupling and concurrent pending requests expose detached whole-view
validation; original three-way order evidence remains the baseline. No safety
property is inferred from always-deny behavior.

## Phase 1C: realization selection and pre-implementation correspondence

Only now select a mechanism. A whole-image replace file is small in source but
requires a bespoke contract for write completion, replacement, directory state,
recovery of interrupted preparation, and errors. An append-only record stream
requires valid-prefix recognition and a current-root rule. A single-row embedded
transactional store already supplies the needed all-or-nothing replacement and
restart boundary. Choose **SQLite rollback journal, synchronous FULL, one complete
serialized view per commitment**, with no WAL, replication, delivery IDs or queue.
This is an assurance experiment, not a kernel requirement or a storage proof.
SQLite documents its atomic-commit algorithm and its OS/storage assumptions:
[atomic commit](https://sqlite.org/atomiccommit.html),
[synchronous setting](https://sqlite.org/pragma.html#pragma_synchronous).

- **Commit point:** an actual successful transaction commit, before any success
  reply or authoritative publication. A kill inside the commit call may recover
  old or new whole state; absence of a reply cannot decide which.
- **Currentness:** one protected configured database and its journal remain intact;
  no actor restores an obsolete copy. Root/profile checks reject the wrong store
  but do not authenticate freshness of an old same-root copy.
- **Whole view:** one serialized value contains established work, fields, full
  accepted string, issued-context set, rights and parent relation. Recoverable
  state is always read within the same serialized boundary used for admission.
- **Content:** retain the actual bounded string. No executor-held referent.
- **Continuing binding:** a trusted surviving supervisor knows fixed endpoint-to-
  context associations (not current rights) and hands reconnected descriptors to
  the corresponding surviving producer. That supervisor, its association and
  bootstrap root/profile are explicitly outside service loss. The restarted
  service never reconstructs current rights from the supervisor or producer.
- **Cold binding:** old endpoints close; the supervisor does not reissue them.
  Management replaces the orphaned current context with an unused one and gives
  fresh execution its endpoint. The same stored whole state is recovered first.
- **Recovery:** open an existing store, allow substrate rollback recovery, verify
  root/profile/schema and semantic validity, then admit traffic. Initialization
  is a separate trusted operation; missing/mismatched state fails closed.
- **Ordering:** one in-process lock and one transaction encompass current read,
  validation and replacement. This intentionally serializes more than necessary.
  The supervisor guarantees the old service has terminated before restarting it.
- **Trust:** supervisor/descriptor isolation, source and finite policy, Python,
  SQLite and its VFS, Unix locking/filesystem/process semantics, and the surviving
  storage image. The experiment kills a process with SIGKILL while OS/storage stay
  alive. It does not establish power-loss durability, disk corruption tolerance,
  malicious rollback resistance, or crash consistency of every SQLite I/O path.

Prepared image, commit entry, commit return, publication and acknowledgement will
have separate test-only pause points. Their pipes are never issued to producers.
An independent checker maps recovered concrete state back to the original model;
no test oracle state is used to initialize recovery.

## Result A1: bounded holder crash/recovery realization survives

`kernel0_recovery_service.py` retains the unchanged concrete policy core.
`kernel0_recovery_check.py` independently maps observations to the unchanged
abstract reducer. Source hashes and runtime provenance are in the two generated
`Kernel-0-Crash-Recovery-*-results.json` files. Reproduce with Python 3.10+ without
`-O`, running each checker with `--output PATH`. The process suite needs Unix
socket/process permissions; its initial sandbox run was blocked at socket send,
then rerun with approved permissions. No dependency was installed.

Evidence: 36 deterministic holder SIGKILL cuts (four effect classes × nine points,
including confirmed partial ingress and received, validated, prepared, commit
entry, durable, published, before-ack, acknowledged cuts); both content-retaining
recovery modes; actual surviving worker processes reattached through the trusted
supervisor; stale ingress/replay after completed replacement; conflicting field
requests; a denied whole composite; and lost-reply retry that changes a bit twice.
Eighteen additional timed commit-call races permit only old/new whole outcomes
and require new after a success reply. They do **not** establish kills inside
SQLite's I/O implementation. Deterministic before/after gates discriminate both
sides without relying on timed race coverage. Wrong root, wrong policy, and
missing database all refuse startup; missing state is not recreated.

**Strongest confirmed counterexample:** save an old same-root store; acknowledge
revocation; terminate holder; restore old store; restart; old-authority `flip`
commits. This is a concrete negative result against freshness-by-root-ID, not an
in-profile service-loss failure. It explicitly delimits A1: the surviving storage
must not roll back beneath the declared boundary. A root/hash/version within the
same restored image would not repair it. The minimum response is a stronger
trusted freshness fact or refusal to promise that stronger failure class.

### Adversarial conformance review (same-session, not independent)

| Obligation | Enforcement / remaining assumption |
| --- | --- |
| Every protected change crosses current guard | Sole request ingress uses original strict decoder; endpoint association is outside JSON. `BEGIN IMMEDIATE`, current read, guard, complete serialized update and commit share one lock. |
| No partial committed view | One transaction contains one complete view, including content/authority/no-reuse state. SQLite atomicity is a trusted substrate contract, not proved by these process tests. |
| No volatile success or accepted read | Replies follow commit; reads reload only existing committed state. Gate pipes cannot modify it. Commit uncertainty never returns a fabricated denial. |
| Continuing evidence after restart | Supervisor retains immutable context association only. Rights, consumed labels, work and bytes reload from storage; old evidence is not remapped to current position. |
| Cold continuation | Old workers/endpoints disappear; management replaces the orphaned context, then a fresh worker consumes retained bytes. Automatic authority revocation at crash was unnecessary. |
| No bootstrap confusion | Existing-only open and root/profile/schema checks. The configured location and initial management association remain trusted. Same-root rollback is deliberately demonstrated as unprotected. |
| No hidden oracle recovery | Model truth exists only in the checker; service imports only concrete policy. Restart configuration contains path/root/policy/endpoints, never a state snapshot. |
| Observation versus outcome | Lost-reply whole commit survives; repeat `flip` commits again. No deduplication claim. |

Review repaired non-vacuity, the initially masked reuse attack, and an initial
partial-ingress harness race (parent now waits for the worker's sent marker).
Prepared-image kills do not prove recovery from every partially overwritten disk
page: the small update may still be in SQLite memory. No result about OS crash,
power loss, malicious same-user processes, supervisor loss, independent authority
binding reconstruction without its survivor, unlimited contexts, deadlines or
full-stack correctness is implied.

**WHY:** each retained distinction has a discriminating failure; the mapped
concrete projection survives actual holder loss at declared cuts. **WHAT:** finite
fixture closure, minimized mutant traces, process evidence and the conformance
review above. **HOW CERTAIN:** evidence-based **A1**, bounded and conditional on
explicit trust; not an unbounded or independent formal proof. **WHAT-NOT-TESTED:**
all exclusions above, general external effects and multi-domain composition.
No Kernel-0 semantic primitive or canonical definition changed. Proceed to Phase 2.
