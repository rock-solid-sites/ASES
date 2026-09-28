---
title: EDASES Phase I Core Substrate Closure
program: EDASES
layer: Architecture
document_type: Design and Reasoning Record
status: Draft
authority: Derived
canonical_repository: edases
crosslink_issue: 571
baseline_commit: 4e800957a673c8bd07eeea3c3c909349cdae76ac
depends_on:
  - EDASES Execution Engine Roadmap
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
  - Work Unit-0 Foundational Reduction
  - EDASES Work Unit Component Design
  - EDASES Currentness and Recovery Assurance
  - EDASES Bounded Structural Transitions
consumed_by:
  - Work Unit Formal Specification
  - Work Unit Prototype Testing
  - Phase I architectural closure review
related_documents:
  - Phase I Information Boundary and Processorless Core
  - Phase I Contract and Verification
  - Phase I Synthesis
  - Kernel-0 Assurance Continuation
  - Kernel-0 Re-Minimization After Stronger Profiles
  - Kernel-0 Protected External Effects
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-28
---

# Phase I — core substrate closure

## Investigation boundary and restart point

This investigation addresses [roadmap Phase I](../EDASES-Execution-Engine-Roadmap.md)
on `codex/execution-engine-roadmap`. The initial evidence tree is the exact
baseline above. Crosslink #571 is the active investigation under #566. New
histories here are reasoned counterexamples, not executed experiments. Earlier
model counts and crash experiments are inherited evidence within their original
bounds; this investigation does not reclassify them as Work Unit implementation
assurance. Canonical Work Unit A–L controls substantive Work Unit requirements.
The obsolete design beneath A–L does not restore Execution or Attachment Point
primitives.

This is a derived architectural candidate, not a canonical methodology revision.
The intended freeze concerns what downstream builders must implement or verify
for this candidate. It is not a declaration that a deployed core already exists.

Documents in this directory split by the roadmap's own core targets:

| Document | Roadmap target |
| --- | --- |
| this file | A — concrete realization, trusted base, closure |
| [Information Boundary and Processorless Core](./Phase-I-Information-Boundary-and-Processorless-Core.md) | D — authoritative-information boundary; E — processorless-core hypothesis |
| [Contract and Verification](./Phase-I-Contract-and-Verification.md) | B — durable state and recovery; C — replaceable execution; F — assurance and downstream work |
| [Synthesis](./Phase-I-Synthesis.md) | the Phase I result in one place |

**Checkpoint 1 (superseded by this revision):** baseline and coupled failure
boundary established. It contained one incorrect claim, corrected in §3.3 below.

**Checkpoint 2 (this revision):** the closure obligation is stated, its two
admissible realization families are separated, and a host-capability limit is
recorded that changes one Work Unit reading and one Kernel clause. Continue with
the information boundary and the processorless falsification program, then the
frozen contract and downstream work.

## Evidence used and why

| Evidence | Question it constrains |
| --- | --- |
| [Kernel semantics](../../research/kernel-0/Kernel-0-Abstract-Semantics.md) and [verification obligations](../../research/kernel-0/Kernel-0-Verification-Obligations.md) | What counts as an admissible whole commitment, current authority, continuity, and a sufficient realization? |
| [Work Unit A–L](../EDASES%20Work%20Unit%20Component%20Design.md) and [foundational reduction](../../research/work-unit-0/Work-Unit-0-Foundational-Reduction.md) | Which confinement, metadata, containment, loss, and disposition guarantees actually have to survive? |
| [Assurance continuation](../../research/kernel-0/Kernel-0-Assurance-Continuation.md), [re-minimization](../../research/kernel-0/Kernel-0-Re-Minimization.md), and [crash/recovery](../../research/kernel-0/Kernel-0-Crash-Recovery.md) | Which mechanisms already have bounded evidence, and where does it stop? |
| [Currentness assurance](../../research/currentness/EDASES-Currentness-Recovery-Assurance.md), especially §3 | Which indistinguishable histories require withholding a claim, and which still permit common safe continuation? |
| [Protected external effects](../../research/kernel-0/Kernel-0-External-Effects.md) | Why decision, irreversible acceptance, later visibility, and knowledge of outcome must be distinguished. |
| [Bounded structural transitions](../../research/structural-change/EDASES-Bounded-Structural-Transitions.md) | Whole disposition, no latent widening, and compatible recovery cuts already reduce to the existing semantics. |
| Linux `capabilities(7)`, `unix(7)`, `seccomp_unotify(2)`, `landlock(7)` (man-pages 6.19) | Whether Work Unit boundary closure is realizable on a mainstream host, and by which mechanism. |

The roadmap names *EDASES Boundary-Composed Authority*, but no separately titled
file was found in this tree. The substantive boundary rule is available in the
foundational reduction §4. No missing separate document is treated as evidence.
The earlier UI synthesis was consulted as required by AGENTS.md; its graph,
statechart, and scheduling proposals do not decide any Phase I mechanism here.

## 1. A concrete baseline without a new primitive

Retain Kernel-0's six semantic distinctions, with Work Unit's particular policy:
authoritative meaning versus candidates; proposal versus whole commitment;
current versus past permission; trustworthy discrimination between attempts that
require different outcomes; a coherent view/common acyclic order for interacting
commitments; and continuing information independent of executor lifetime.

The least demanding useful realization target is one **logical authoritative
commitment boundary**, retained accepted contents, and boundary-mediated
selected attachments. A single serialized holder is a sufficient comparator;
multiple holders are not needed to demonstrate the core. This is not a
requirement for one physical process, a database product, or one global clock.
Storage, protection and external mediators actually relied upon count in the
trusted boundary wherever placed.

The baseline supports finite, explicitly represented Work Units, a well-founded
containment forest, explicit local grants plus full-path restrictions, bounded
resource quantities, immutable accepted content, cold recovery, and explicit
replacement. It must admit useful create/grant/accept/replace/recover/continue
histories, not merely an empty object and universal denial. A finite-capacity
implementation may refuse new work before exceeding its declared limits; it
cannot erase required accepted work to make room.

### 1.1 First coupled removal tests

**H1 — a seal bit does not revoke a route.** Grant an executor a direct handle to
accepted bytes. Replace it or lose the engine. The old process writes through the
handle while a record says sealed. Kernel records remain valid; authoritative
meaning and confinement do not. Required repair: the concrete route must be
mediated at its claimed authorization event, revoked by a trusted substrate, or
restricted to candidate/private material whose mutation changes no accepted
meaning. Adding a durable Execution record, heartbeat or Processor does not close
the route. This sharpens realization, not Kernel semantics.

**H2 — a new engine is not a new authority by assertion.** Engine A loses contact
with storage but remains alive. B loads a saved grant table and serves replacement
execution; A resumes with old handles. A shared root or generation label does not
prevent both from acting unless the actual acceptance boundary discriminates
current authority. The single-holder baseline permits B to activate only after
trusted exclusion of A from every protected ingress. A surviving host can supply
that exclusion; distributed takeover would require additional realization
assumptions. No lease or election is introduced to hide a missing exclusion proof.

**H3 — cold recovery fixes bearers, not missing work.** Accept x, then accept y;
restore an authentic image containing x and drop all old endpoints. New endpoints
cannot reconstruct y. The currentness obligation covers accepted contents and
coupled relationships as well as authority. Cold recovery reduces bearer
reconstruction requirements but does not remove current-storage trust.

**H4 — already-authorized consequence.** Commit a precise external obligation;
replace its producer; the sink accepts it afterward. This is valid only under an
explicit decision-authorized obligation whose authorization survives replacement.
It violates a different promise requiring current producer authority at sink
acceptance. A raw network capability is not an immutable exact obligation. The
profile must identify the authorization event and cancellation behavior before
such an attachment can be granted. A later denial or compensation cannot undo an
unauthorized irreversible consequence.

**H5 — the orphaned child is outside the revocation model.** An executor inside
`W` starts a background process `b` and then dies. `b` holds a network socket and
read access to `W`'s contents. A guarded revocation of `W`'s network attachment
changes authoritative records, and `b` is not named in any of them. `b` then
sends `W`'s accepted content out. Required repair: either every process that can
act inside `W` is reachable by the boundary's revocation model, or `W`'s
interior holds nothing whose loss or egress is claimed. This is H1 with a
concrete holder that the boundary does not track. It is not repaired by a
Work Unit record, a heartbeat, or a Processor.

### 1.2 The closure obligation

H1, H2 and H5 have the same shape: a Kernel record is correct while a path around
it remains. The prior work states the required outcome (Work Unit A–L K3, K5, K13,
H) but not the substrate obligation that would actually produce it. Phase I
states it, because an implementation cannot be tested for conformance without it.

> **CP — Closure Property.** For a bounded object `W`, let `X(W)` be the set of
> capabilities and channels through which activity inside `W` can affect anything
> outside `W`, or through which anything outside can acquire actionable access
> inside `W`. For every `x ∈ X(W)`: (i) `x` is exercisable only while a current
> Kernel-authorized relation covering it is in force; (ii) revoking that relation
> makes `x` non-exercisable, by a mechanism that acts on the **holder** of `x`,
> not only on the record; and (iii) the mechanism is inside the declared trusted
> boundary and fails closed on its own loss.

CP is a Work Unit external-effect claim expressed through Kernel-0's existing
"boundary of external action claims" clause: Work Unit claims that *no* actionable
crossing is permitted, so *every* crossing is a claimed protected external action,
and each needs a named authorization point and revocation enforcement point. CP
adds no Kernel primitive. It does change what a Work Unit realization must
evidence.

**CP′ — the narrowed form that makes CP reachable.** Requiring every internal
write to be mediated is a cost requirement, not a guarantee requirement. The
guarantee is about *accepted meaning* and *egress*:

> **CP′.** Every crossing that changes accepted authoritative meaning, and every
> crossing that carries anything out of the boundary, satisfies CP. Writes
> confined to a **declared candidate area** inside the boundary need not be
> mediated, provided no authoritative record designates that area as accepted
> content and no separate guarded acceptance is implied by the write itself.

Removal witnesses: drop the accepted-meaning clause and a stale executor
overwrites accepted content while every record stays valid; drop the egress clause
and a sealed object's bytes leave while every record stays valid; drop the
candidate-area allowance and the only defence is mediating every keystroke, which
no required guarantee asked for. This is Kernel-0's existing
"candidate material versus accepted meaning" distinction applied to a filesystem
layout, and it is what makes the property realizable at acceptable cost.

### 1.3 What CP is not

CP does not require a capability system, a sandbox, a namespace, a specific
language, or a mediator process. It requires that the *chosen* realization name
the holder of each route and the enforcement point for its revocation, and that
the name be testable. It is also not satisfied by an access-control *decision*:
a decision made at `open` time does not bind a descriptor already held.

## 2. Two admissible realization families

CP cannot be realized on a mainstream host by any single mechanism, and the
tempting candidates each fail for a specific recorded reason. This was checked
against primary sources rather than assumed.

| Candidate mechanism | What it actually guarantees | Why it is not CP |
| --- | --- | --- |
| Linux capabilities, irreversible bounding-set drop (`capabilities(7)`, `prctl(PR_CAPBSET_DROP)`) | A thread's bounding set can only be narrowed, never restored, and ambient capabilities fall with permitted/inheritable sets. | `prctl` acts on the **calling** thread. No outside process can narrow a live executor's set, and capabilities gate privileged operations, not ordinary file or socket use. |
| Landlock (`landlock(7)`, Linux 5.13+, ABI-gated, boot-time LSM) | Unprivileged, stackable, self-applied, inherited by children, irreversible; access is denied unless every enforced layer grants it. | Restriction is set by the process on itself and "there is no way to remove its security policy". "Files or directories opened before the sandboxing are not subject to these restrictions", so an already-held descriptor is unaffected. Certain calls (`chdir`, `stat`, `chmod`, `chown`, `setxattr`, `utime`, `fcntl`, `access`) are not restrictable at all. |
| seccomp user-space notification (`seccomp_unotify(2)`) | A user-space supervisor sees and can veto or emulate individual syscalls. | The kernel states it "must not be used to make security policy decisions about the system call": a notifier is bypassable if a filter of higher precedence is installable, and `SECCOMP_USER_NOTIF_FLAG_CONTINUE` has a time-of-check/time-of-use race on the arguments. This is exactly the detached-validation-then-use failure the currentness result already names, reproduced in the operating system. |
| `SO_PEERCRED` / `SCM_CREDENTIALS` (`unix(7)`) | The kernel checks and returns the connecting peer's pid, uid and gid; an unprivileged peer cannot forge them. | Excellent for *admission discrimination* (below), and useless for revocation: it tells you who is calling, and gives no lever over what they already hold. `SCM_RIGHTS` also lets a peer hand its descriptor to another process, so a descriptor is not a per-attempt bearer. |
| Process termination (cgroup, `pidfd`, signals) | Removes everything the process holds. | Destroys the executor's volatile work with it, so it is a replacement mechanism, not a sealing mechanism, unless the work is already in the boundary's custody. |

The resulting limit is a real architectural constraint, not an implementation
difficulty:

> **L1 — live revocation limit.** On a mainstream host, effective filesystem and
> network restriction of a process is fixed when that process is created, is
> self-applied and irreversible thereafter, and binds path resolution rather than
> already-open descriptors. A separate authority process can therefore narrow a
> live executor only by terminating it.
> **Consequence:** any Work Unit claim of the form "revoking attachment `x`
> immediately removes `x`'s exercisability by a live executor" is realizable only
> if `x` was never held by that executor in the first place.

This has a direct reading consequence. Work Unit A–L B states that "removing an
attachment removes that internally available avenue of external influence". Under
L1 the operational reading must be fixed as:

> Removing an attachment (i) prevents any **new** acquisition of that avenue, and
> (ii) stops **boundary-mediated** exercisability of it, and (iii) terminates any
> holder for which removal is claimed as immediate. It does **not** retroactively
> remove a capability the executor already holds.

This is the concrete realization constraint the roadmap's Core target A asks
about, and it forces a change to Work Unit semantics. It is a narrowing of an
ambiguous sentence, not a new obligation.

### 2.1 The two families

Given L1, exactly two families remain, and they are distinguished by who holds
the route.

**R-A — capability-request.** Nothing inside the boundary holds a host capability
that outlives a request. Every effect is a request to the boundary, which holds
the capability and can stop serving. Revocation is immediate and complete; engine
loss destroys every route because the routes are the engine's. CP holds directly.
The cost is that executors cannot act on the host directly: no real shell, no
direct file editing, no pipes. The boundary needs a rich, well-specified effect
vocabulary or useful work becomes impossible.

**R-B — host-sandboxed executor.** Executors are created inside a host
confinement chosen at creation (namespace, Landlock, seccomp-BPF, `chroot`,
resource limits), holding real host capabilities. Revocation is: never grant it,
or terminate the holder. Under R-B "sealed" means *no new grant, and no
boundary-mediated exercisability* — not *existing host access removed*. CP holds
only for the routes the boundary itself holds.

R-B becomes workable through one design move, and this move is a real Work Unit
obligation rather than an implementation hint:

> **Custody rule.** For a Work Unit that claims accepted content, the boundary
> holds the accepted-content paths and the egress channels. The executor's
> confinement is scoped to what it needs, and its outbound access, if any, is a
> boundary proxy rather than a raw host capability.

With custody, R-B satisfies CP for everything a Work Unit actually claims: egress
is a boundary route that can be stopped, and accepted content is boundary-held so
that losing or killing the executor loses no required content. What R-B cannot
deliver, and must not claim, is *immediate* removal of a raw filesystem or
network capability from a live executor. Where a consumer needs that, it must
select R-A or add a stronger host mechanism.

**Neither family is selected here.** The core semantics are identical in both;
only the trusted boundary and the excluded claims differ. Phase I freezes the
contract each family must satisfy and the tests each must pass, and leaves the
choice to the realization, with §2.3 recording the evidence a choice needs.

### 2.2 Why this is a Kernel-0 change and not only a Work Unit change

Kernel-0's external-action clause already says an outside action is protected when
its occurrence changes the authoritative view, and otherwise only when an
instantiation expressly claims it. CP is an instance of that clause, so no
semantic change is required. What *is* required is a sharpening of one sentence:
CP (i) binds the *holder* of a route, not only the record of the relation. The
existing clause says revocation must be enforced "at the effect sink or an
equivalent cancellation contract", which is a temporal statement and can be read
as satisfied by refusing to act. It cannot be read as satisfied by refusing to
act when the effect is already in the holder's hands. Phase I's freeze therefore
adds the holder-binding requirement to the Kernel verification obligations, not to
the abstract semantics.

### 2.3 What a family choice still needs

| Question | Why reasoning cannot settle it | Cheapest discriminating evidence |
| --- | --- | --- |
| Is R-A's effect vocabulary expressive enough for real agent work (build, test, patch, inspect)? | It is an empirical property of a future effect set, not a semantic one. | Implement one real work item end to end through R-A; count the effects that cannot be expressed and the latency of those that can. |
| Does R-B's confinement plus custody actually hold on the target host and kernel? | Landlock, namespace and cgroup availability and semantics are platform facts; `landlock(7)` records boot-time LSM enablement and ABI gating, and OverlayFS layering is a known gap for lower-layer rules. | One executor inside the chosen confinement: attempt each excluded access, then attempt it again after the boundary stopped serving, then kill the executor and attempt once more. Record the host, kernel version and Landlock ABI. |
| Can a route be made revocable without terminating a live executor on this host? | Determines whether a third family exists. | Probe for any mechanism that narrows a *running* process's already-held filesystem or network access, other than termination. Landlock and `prctl` are self-directed; `seccomp_unotify` is documented as unsuitable. Record the result either way. |

**WHY:** H1/H2/H5 distinguish valid records from valid behaviour, and L1 shows
that the distinction is not closable by record-keeping or by any single host
mechanism. **WHAT:** Work Unit A–L B/C/H/K, Kernel-0's external-action clause, and
the four primary sources named above, read for the specific mechanism each
provides. **HOW CERTAIN:** the requirement analysis and the mechanism limits are
evidence-based against primary documentation; no kernel or host was exercised and
no C code was written. **WHAT-NOT-TESTED:** real confinement, engine-death
teardown, partitioned takeover, R-A effect expressiveness, and whether some other
host mechanism provides live revocation.

## 3. Coupled failure boundary, corrected

The prior checkpoint's failure table is retained except for the second row, which
is wrong as stated. It claimed that when the engine/authority process stops, the
system can "disable active routes ... recover cold and sealed". Under L1 an engine
cannot disable routes it does not hold, so under R-B engine loss terminates
nothing, and "recover sealed" asserts a route property from a record property. The
corrected table separates the two families.

| Event | R-A required result | R-B required result | Assumption or boundary |
| --- | --- | --- | --- |
| Executor or attachment process disappears | Preserve the Work Unit, accepted contents and current authoritative relationships; replacement is a guarded event. | Same. | Neither executor-local bytes nor executor assertions are a trusted continuation store. |
| Engine/authority process stops | All routes die with it; nothing is exercisable. Recover cold and sealed. | Routes held by surviving executors persist. The Work Unit is *inactive*, not *sealed*, until custody is confirmed or holders are terminated. | Under R-B, custody is the only thing making "sealed" true. Verify it; do not infer it from a record. |
| Loss during commitment, including lost reply | Recover a permitted whole endpoint; preserve irrevocably committed effects even if unacknowledged. | Same. | Current retained storage supplies a coherent recoverable cut. No automatic retry or exactly-once promise follows. |
| Transient loss of contact with authority | Withhold affected new commitments; an isolated executor cannot confer authority on itself. | Same. | No partitioned multi-writer availability guarantee, timeout election, or takeover by suspicion. |
| Missing, unreadable, or detected-inconsistent recovery material | Keep affected objects bounded and inactive; do not silently bootstrap an empty replacement. | Same. | Preservation/availability may be lost. Refusal is not successful recovery. |
| Machine restart, power loss, failed writes, rollback, media corruption | Do not inherit a positive recovery guarantee from the process-loss experiments. | Same. | A stronger profile needs its own storage/protection evidence. Silent rollback or corruption cannot be promised detectable under the baseline. |

These are *selected assurance bounds*, not permission to weaken Work Unit's
abstraction. Engine loss cannot release contents — under either family. Power-loss
durability, rollback-resistant successful recovery, and physical erasure remain
explicit stronger claims. An implementation must disclose which family it
implements and which failures its evidence covers; unsupported failures cannot be
reported as passing this profile.

## 4. The two exclusion obligations

CP and Kernel-0's "trustworthy distinction among attempts" look like one
requirement and are two. Separating them is necessary, because a realization can
satisfy one and fail the other while passing every abstract test.

> **AR — admission discrimination.** When policy requires a replacement attempt to
> proceed while a superseded attempt is excluded, their submissions must differ in
> something admission can trust, and the superseded attempt must be unable to
> acquire new authority. Subject: the *proposal*.
>
> **RR — route revocation.** When a claim says an effect avenue is no longer
> exercisable, the mechanism must act on the *holder* of that avenue. Subject: the
> *capability*.

They are independent. AR without RR is H1/H5: records are right, egress continues.
RR without AR is the reverse: the old avenue is gone, but the old process obtains
fresh authority by position, because "whoever is attached to position `p` may
write" is not a distinction between two live attempts. Neither implies the other,
so both must be tested.

**AR has a realization that needs no durable counter.** The obligation is that an
admission observation is never reissued. Two realizers discharge it:

1. a **monotone issued-observation namespace** kept in the authoritative view, so
   that reissuing a consumed label is impossible; and
2. a **host-attested live attempt**: the boundary owns the endpoint, binds
   authority to the connection object it established, and identifies the peer by
   the kernel-checked credential rather than by a recorded value.

`unix(7)` records that the kernel validates `SCM_CREDENTIALS` claims and rejects
mismatches absent `CAP_SETUID`/`CAP_SETGID`/`CAP_SYS_ADMIN`, and that `SO_PEERCRED`
is available on connected `AF_UNIX` sockets. So on an unprivileged host the
boundary can tell live attempts apart without any persisted generation number.
The same source records `SCM_RIGHTS` descriptor passing, which is why the
boundary must own the endpoint: handing the executor a reusable bearer would let
a different process present the old attempt's evidence. Binding to the connection
rather than to a stored pid also disposes of the identifier-reuse race, because no
recorded identifier is ever consulted after the connection is established.

This retires **generation counters, epochs, leases, heartbeats and fencing tokens
as core candidates** for the selected profile, and records why:

| Candidate | Status | Reason |
| --- | --- | --- |
| Generation / epoch counter in `σ` | Optional realizer of AR | Needed only if the host cannot attest a live attempt, or if a claim must survive the peer's death without re-establishing a connection. |
| Lease | Not required | Nothing in the selected profile requires automatic revocation on unexplained death. Automatic revocation would seal the Work Unit on executor loss, which is safe but reduces availability and is not a claimed guarantee. |
| Heartbeat / liveness monitor | Not required | It would be a *trigger* for the same automatic revocation. A detection delay is an availability question, not a safety one, under this profile. |
| Fencing token | Not required as a separate object | The token's only job is AR's non-reissuability, which a connection binding or a monotone namespace already supplies. |
| Durable request ID / deduplication | Not required | Prior work already separates commitment from knowledge of commitment. Adopt only if a consumer claims at-most-once effects. |

The prior finite-representation limit still binds whichever realizer is chosen: if
only `M` distinguishable observations exist and every superseded holder can still
present one, the `(M+1)`-th issuance must reuse, and the safe outcome is exhaustion
by denial. Host-attested live attempts do not escape this — they escape it by never
relying on a *recorded* value at all, so exhaustion is not reached for live peers.
Both statements should be stated together; either alone invites a builder to
assume indefinite replacement progress.

**WHY:** H5 and its mirror show the record/execution split, and the four sources
show which host mechanisms can actually act on a holder. **WHAT:** the AR/RR
definitions, the mechanism table, and the primary-source limits already cited.
**HOW CERTAIN:** evidence-based requirement analysis; the AR realizer is argued
from documented kernel behaviour and has not been implemented or exercised.
**WHAT-NOT-TESTED:** no fork/exec, socket, namespace, Landlock, cgroup or
revocation experiment was run. In particular, the claim that a live attempt can be
distinguished by kernel-attested peer credentials on an unprivileged host is
documented, not measured.
