---
title: Phase I Revocation Verification and Q1 Reduction
program: EDASES
layer: Architecture
document_type: Research Finding
status: Draft
authority: Derived
canonical_repository: edases
crosslink_issue: 571
baseline_commit: 4e800957a673c8bd07eeea3c3c909349cdae76ac
depends_on:
  - EDASES Phase I Core Substrate Closure
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
  - EDASES Work Unit Component Design
consumed_by:
  - Phase I architectural closure review
  - Work Unit Formal Specification
  - Work Unit Prototype Testing
  - real protected-boundary implementation
related_documents:
  - Phase I Core Substrate Verification Work
  - Phase I Concurrent Realization Proposal
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-28
---

# Phase I — revocation verification and the Q1 reduction

## 0. Why this document exists

[Phase I Core Substrate Closure](./Phase-I-Closure.md) closed with two items it
could not settle: a rejected inference recorded in its §10, and the open temporal
contract Q1 in its §8. This document does two things and nothing else:

1. independently verifies the source-level counterexample that rejects the
   rejected inference, and extracts the architectural requirement that the
   counterexample actually implies; and
2. reduces Q1 from an open semantic question to a named disclosure, a named
   enforcement point, and one bounded measurement.

Neither part proposes a new primitive, a new subsystem, or a change to the six
retained Kernel distinctions.

---

# Part A — the revocation question, settled against my own claim

## A1. What was claimed and what was rejected

A concurrent proposal (`76a38fb7`, preserved as
[Phase I Concurrent Realization Proposal](./Phase-I-Closure-Realization-Boundary.md))
advanced **L1**: on a mainstream host, effective filesystem and network
restriction of a process is fixed when the process is created, is self-applied
and irreversible thereafter, and binds path resolution rather than already-open
descriptors; therefore a separate authority process can narrow a live executor
only by terminating it.

The closure record §10 rejected the universal inference and named a countermechanism
in Linux v6.12's `selinux_file_permission`. I have now read that source directly.
**The rejection is correct and the proposal's L1 was wrong in its universal form.**
I record that plainly because the correction runs against my own conclusion, and
because a false "rejected inference" left in the tree would mislead a builder in
the same way the false claim would have.

## A2. Verified source behaviour

`security/selinux/hooks.c`, Linux v6.12, `selinux_file_permission`:

```c
static int selinux_file_permission(struct file *file, int mask)
{
        struct inode *inode = file_inode(file);
        struct file_security_struct *fsec = selinux_file(file);
        struct inode_security_struct *isec;
        u32 sid = current_sid();

        if (!mask)
                return 0;

        isec = inode_security(inode);
        if (sid == fsec->sid && fsec->isid == isec->sid &&
            fsec->pseqno == avc_policy_seqno())
                /* No change since file_open check. */
                return 0;

        return selinux_revalidate_file_permission(file, mask);
}
```

Three facts follow directly, and only these three:

- The fast path that skips revalidation requires **all three** of: unchanged
  subject security context, unchanged inode context, and unchanged **policy
  sequence number** relative to what was recorded at `file_open`.
- Otherwise the kernel calls `selinux_revalidate_file_permission`, which computes
  the access vector and calls `file_has_perm`. That function first requires
  `FD__USE` permission when the current subject context differs from the one
  recorded on the open file, and then calls `inode_has_perm` for the requested
  access — i.e. it re-evaluates the **inode** permission at the moment of use.
- `selinux_file_alloc_security` records the subject context, inode context and
  policy sequence number when the file is opened.

**Therefore an already-open file descriptor is re-checked against current policy
whenever the policy sequence number changes.** Revocation of an already-held
descriptor is achievable by changing policy, not only by terminating the holder.
Landlock's documented open-at-time behaviour is a property of Landlock, not a
property of hosts: the same kernel composes Landlock with other layers, and this
hook is one of them.

## A3. What the verification does and does not establish

| Establishes | Does not establish |
| --- | --- |
| Filesystem access to an already-open file is not universally fixed at open time; a policy-sequence change forces revalidation. | That revocation of already-open access is available on an arbitrary host, or that SELinux is configured or enabled on the host an implementation actually uses. |
| The universal form of L1 is false, so the Work Unit closure obligation is not host-impossible in principle. | That *all* access paths are covered. `file_permission` does not govern already-mapped memory, device `ioctl`, or asynchronous completion. |
| The claim "applying a new rule cannot be assumed to revoke existing handles" remains correct **for Landlock and capability mechanisms specifically**, and must be stated per mechanism. | That the administrative action used to revoke actually increments the policy sequence number. That is a separate, checkable fact about the chosen policy-management path. |

The narrower warning survives and is worth keeping: a builder may not assume that
*because a route is mediated*, revoking the Kernel-side record revokes the
holder. Whether it does depends on the specific enforcement point, and must be
tested per mechanism. That was the useful part of the proposal and the closure
record adopted it.

## A4. The requirement the counterexample actually implies

Correcting L1 does not remove the obligation; it relocates it, and the relocated
version is stronger than the original.

> **AC — access-control policy is an authoritative resource.** For a bounded
> object `W`, the concrete access-control policy that decides what already-running
> work inside `W` may do is part of the trusted boundary for every claim about
> `W`'s confinement. Therefore:
>
> 1. A change to that policy is a change to what previously authorized work may
>    do. It must be **ordered with** the Kernel's authority change, on the same
>    footing as a sink's acceptance point: a revocation completed and acknowledged
>    before a later use cannot be justified by the earlier permission.
> 2. It must **fail closed**. A rejected, partial, or half-applied policy change
>    must not leave previously-permitted access in force while the Kernel records
>    the relationship as revoked.
> 3. The realization must **disclose which policy changes are inside the trust
>    boundary and which are host-administered outside it**, and must state what
>    the Kernel's "revoked" claim is worth when the enforcing policy is mutable by
>    something the Kernel does not control.

Clause 3 is the part that is easy to miss and it is a genuine route into a
false revocation. If a host administrator can broaden policy, then a stale
producer whose Kernel-side grant was correctly revoked can have its access
restored by a policy change the Kernel never authorised and never observed. Every
Kernel record remains valid; the revocation is a record, not an exclusion. This
is the same shape as H2 and H4 — authority hidden in a mediator outside the
Kernel — and it must be in the route inventory for any realization that relies on
host access control rather than on boundary-held custody.

AC is not a new Kernel primitive. It is an instantiation of the existing
external-action clause applied to the enforcement point, plus the existing
ordering requirement applied to a second class of protected change. It belongs in
the effect-correspondence rules of the closure record, and it adds a **route class**
that §2 currently does not list.

## A5. A second source claim, also over-stated: "sealed does not mean frozen"

A concurrent [Authority Ontology](../../EDASES-Authority-Ontology.md) (commit
`2bcad274`) asserts at §11, flatly:

> **Sealed does not mean frozen.** A Work Unit may be sealed from protected
> external effects while computation continues internally.

and its `Execution-neutral invariant` generalizes this: "internal computation is
not itself an authority-bearing act unless it crosses a protected boundary or
changes authoritative meaning".

The authority half of that is right, and is the position the closure record already
took: D1 and D2 concern admission and protected effects, and `Execution-neutral` is
a fair restatement. The difficulty is that "sealed" in the canonical Work Unit
glossary is defined as "the durable bounded object remains, but **active
execution**/outward capability use is disabled", so the ontology asserts the
opposite of that phrase for the same word. A Work Unit cannot satisfy both, and
the ontology's §1 declares itself a working base that "should constrain future
reasoning".

This is the one place where the **specification** and the **derived** records now
disagree. It is a wording conflict, not a design conflict: `Execution-neutral` is
the stronger and more defensible formulation, because "internal computation" and
"active execution" are different things and only the second is what the glossary
names. The recommended repair is to qualify the ontology rather than the glossary:

> Sealing disables admission and protected effects (D1, D2). Whether it must also
> stop interior execution is a separate claim (D3) with its own path-dependent
> realization, and is not settled by the fact that interior computation is not
> itself authority-bearing.

Read as written, the ontology forecloses a question that remains open, and would
let a builder report "sealed" against closure's Q1 without having measured
anything. Recorded rather than applied, because the ontology is a provisional
working document on a different issue and the operator may prefer to keep it
unqualified. The safest interim rule for any downstream builder is: report D1 and
D2 as verified, and report D3 as unverified unless the enforcement point and
quiescence window have been measured.

---

# Part B — Q1 reduced to a disclosure and a measurement

## B1. The question

Q1 asks when engine loss must disable still-running computation. The tension is
between Work Unit E, which says that while the engine is not running durable Work
Units "remain sealed bounded objects", and the H glossary, which defines sealed as
"the durable bounded object remains, but **active execution**/outward capability
use is disabled".

## B2. The reduction: "disabled" is three claims, not one

The ambiguity dissolves once the word is split. Sealing and revocation can each
assert three different things, and the repository's text supports them very
differently:

| Claim | Meaning | Repository support | Realizability |
| --- | --- | --- | --- |
| **D1 — admission disabled** | No new authorized work for `W` is admitted or started. | Unambiguous in E and H. | Always. The boundary simply stops admitting. No host support. |
| **D2 — effect disabled** | No new protected effect for `W` occurs: no crossing changes accepted meaning and nothing egresses. | Unambiguous in E and H. | Always, given the closure obligation of Part A and the effect contracts of §4. |
| **D3 — execution stopped** | No process inside `W` continues to execute or consume granted resources. | Only the single H glossary phrase, inside a bullet that is explicitly a **taxonomy of boundary facts** ("The words `sealed`, `revoked`, and `destroyed` describe different facts"), not a process-management specification. | Path-dependent. See B3. |

The reduction is therefore: **D1 and D2 are claimed and achievable on every path.
D3 is a separate claim whose support is one glossary phrase, and it is achievable
on some paths and not others.**

This already narrows the question. E is about the *engine* not running and about
*recovery*; it says the durable objects and their relationships are not treated as
current and are not reactivated. It does not say their processes were stopped. C
reinforces this: the stated concern is that loss "must not implicitly destroy the
Work Unit or release its contents" — destruction and release, not cessation.

## B3. D3 on the two paths

**The authorized-seal path (revocation, narrowing, ancestor restriction).** H's
own frame is "when a Work Unit **loses the authority** necessary for continued
external effects". Authority loss is a guarded transition, so the boundary is
alive when it happens, and it can terminate the holder in the same commitment.
**D3 holds with no interval and no timer on this path.** Nothing here is open.

**The engine-death path.** The boundary is gone, so it cannot terminate anything.
Whether D3 holds, and after what delay, is entirely a property of the selected
substrate. Define

> **Δ — quiescence window.** The interval between the authority holder ceasing to
> serve and the last process inside any sealed or revoked Work Unit ceasing to
> execute.

Then D3 on this path is exactly the claim `Δ = 0`, or `Δ ≤ δ` for a declared
`δ`. Nothing else is at stake, and there is no third possibility. Δ is a property
of a named substrate mechanism, not of the semantic contract.

## B4. What producing a bound on Δ requires

Producing `Δ ≤ δ` on the engine-death path requires two things the selected
profile does not otherwise need:

1. **An engine-independent enforcement point** — a component outside the engine
   that can terminate or freeze interior execution. Candidates are a surviving
   supervisor, a cgroup or namespace whose teardown is triggered without the
   engine, or a shared-fate arrangement. Its survival is a trust assumption and
   must be named, not assumed.
2. **A trusted liveness signal and a timer** acting on that point, because the
   trigger is the *absence* of the engine rather than an authorized transition.

This settles the roadmap's standing question about leases and heartbeats with a
complete conditional answer:

| Claim | Lease/heartbeat/fence class mechanism |
| --- | --- |
| Safety of the core: no unauthorized effect, no stale admission, continuity across executor loss | **Not required.** Automatic revocation on unexplained death would seal a Work Unit on executor loss, which is safe but reduces availability and is not a claimed guarantee. Prior work reached this; it is now stated with its complete boundary. |
| D3 on the authorized-seal path | **Not required.** The boundary is alive and the trigger is an explicit transition. |
| D3 with a bound on the engine-death path | **Required**, and it is a realization component in the TCB, not a Kernel primitive. A watchdog that acts on expiry must fail closed, and killing is only safe for accepted content when the custody obligation of §2 is met. |
| Physical exclusion of an old producer that has acquired genuinely new evidence | **Required**, but that is a different claim: Kernel already separates an invalidated old grant from a genuinely new authorized grant, and this is a source-binding premise, not a timing mechanism. |

A watchdog that only *proposes* a replacement transition after noticing death is a
convenience and inherits no safety property; only one that *enforces* fail-closed
termination discharges Δ. The distinction is worth stating because the two are easy
to conflate in an implementation.

## B5. The residual, stated precisely

Q1 is therefore not an open architectural question. What remains is listed below,
with one added blocker: the first item is now gated on reconciling two records that
currently assert opposite things about the same word, not on new evidence (A5).

| Residual | Why reasoning cannot settle it | What settles it |
| --- | --- | --- |
| Which reading the Work Unit specification intends for D3 on the engine-death path | It is a canonical wording decision about one glossary phrase, not a derivable result. Two readings are defensible. | An explicit canonical clarification of the H glossary and E, stating whether D3 is claimed on engine death. Until then, report the profile as meeting D1+D2 and leave D3 **unverified** on that path. This decision is now additionally blocked on reconciling two records, since the concurrent Authority Ontology asserts the opposite of the glossary (A5). |
| The achievable value of Δ on a chosen substrate | A property of a specific host, kernel, LSM configuration and watchdog design. | Measure it: kill the engine with an interior CPU-only activity running, and record the interval until last execution stops, with the enforcement point named. |
| Whether the enforcement point is in the trust boundary and who can change it | Same class as A4 clause 3. | Disclose it, and apply AC. |

The discriminating test for the first residual is concrete: an implementation that
claims the strong reading must show that the *engine itself* is the sole execution
supervisor and that its death is synchronous with the death of everything it
supervised. No ordinary substrate provides that, so the strong reading reduces in
practice to "there is always a surviving enforcement point", which is a claim about
architecture, not about the specification. An implementation that claims the weak
reading must show only D1 and D2 and must not describe a still-running interior as
"sealed" in prose.

## B6. Why this closes Phase I's frontier work

Q1 was the only item the closure record described as an unresolved *core* contract.
It reduces to: one canonical wording decision, one disclosure parameter, one trust
disclosure, and one measurement. None of these can be settled by further frontier
reasoning about the architecture, and none of them can require a new primitive
unless the strong reading is adopted — in which case the consequence is a named
surviving enforcement component, which is a realization obligation already
implied by the closure property.

**WHY:** the source read is decisive against my own claim and implies a stricter
ordering obligation; the D1/D2/D3 split is exhaustive and its support in the
repository text is asymmetric. **WHAT:** the pinned `selinux_file_permission`
source, the Work Unit C/E/H/K and glossary text, and the closure record's own
§2/§4/§8/§10. **HOW CERTAIN:** A2 is verified primary source; B2–B4 are
evidence-based reductions over the pinned contracts; the residual is one canonical
decision and one empirical measurement. **WHAT-NOT-TESTED:** no host, kernel, LSM
configuration, policy sequence change, watchdog or process-teardown experiment was
run; whether a given administrative action increments the policy sequence number is
unverified here; mappings, device `ioctl` and asynchronous completion are outside
the hook that was read.
