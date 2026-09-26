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
