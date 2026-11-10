---
title: L5 single-writer custody boundary — Cloud environment probe
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - PLAN.md
  - docs/research/phase-i-f1-recovery-repair/L5-PLAN.md
  - docs/research/phase-i-f1-recovery-repair/REPORT.md
  - docs/methodology/Agent Model Launch Routes.md
related_documents:
  - evidence/environment-probes.txt
  - evidence/posix-owner-bypass.json
  - evidence/original-l5-probe/raw.json
---

# Result

The requested L5 launcher boundary could not be prototyped in this Codex Cloud
Linux environment. The cheapest discriminator, a Landlock ABI query, returned
`ENOSYS` (`Function not implemented`) for x86_64 syscall 444
(`landlock_create_ruleset`). Both available namespace helpers also failed
before child setup because `/proc/self/uid_map` is read-only. The exact raw
outputs are retained in [environment-probes.txt](evidence/environment-probes.txt).

This establishes that the required controls were unavailable through the
observed interfaces in this environment. It does **not** distinguish a kernel
built without Landlock from a seccomp filter deliberately returning `ENOSYS`;
`/proc/self/status` reports seccomp mode 2 with one filter. No Landlock ruleset
was installed, so there is no confinement claim and no confined-child
inherited-FD test result. No fallback based on `flock`, file mode bits, or a
cooperative wrapper was implemented.

# Observations and limits

- Runtime: Linux `6.18.57`, x86_64; Python `3.12.14`.
- Identity: uid/gid `1000(agent)`, no supplementary groups; effective,
  permitted and bounding capabilities are zero; `NoNewPrivs: 1`.
- Landlock: ABI version query on syscall 444 returned `-1`, errno 38.
- User namespace probe: `unshare --user --map-root-user --mount true` failed
  with `cannot open /proc/self/uid_map: Read-only file system` (exit 1).
- Bubblewrap probe: `bwrap --unshare-all --ro-bind / / -- true` failed with
  `setting up uid map: Read-only file system` (exit 1).

# Demonstrated outside-boundary controls

Two negative/control experiments were run in disposable roots. The full L5
probe reused the pinned original #11 harness and its independent checker. All
11 histories passed the checker. In `exclusive-bypass`, the original
unguarded manager entered while the cooperative exclusive-lock owner was
paused; both management operations returned COMMITTED, but cold state retained
parent P instead of the acknowledged move to Q. The same wrong-move ACK was
reproduced by the generation guard's unguarded-writer bypass and the original
overlap comparator. The exclusive owner was actually killed and reaped at both
pre-selector and post-selector gates; fresh processes started only after reap
and successfully progressed from cold state. The raw capture is at
[original-l5-probe/raw.json](evidence/original-l5-probe/raw.json); checker
output is retained at [original-l5-check.json](evidence/original-l5-check.json).

A separate POSIX control used a temporary directory mode `0700`, a lock file
mode `0600`, and data files mode `0600`, all owned by uid/gid `1000`. While the
parent held `flock(LOCK_EX|LOCK_NB)`, a separate same-UID child ignored that
lock and wrote `unguarded-child` successfully (no error/errno). The file owner
also changed a file from mode `0444` back to `0600` and wrote it successfully.
A child inherited an already-open writable descriptor through `pass_fds`;
after the parent changed that file to `0444`, the child wrote through the
descriptor successfully. Exact resulting bytes, identities, modes and return
statuses are retained in [posix-owner-bypass.json](evidence/posix-owner-bypass.json).

These are demonstrated **outside-boundary bypasses**: cooperative `flock` and
owner-controlled mode bits do not create a custody boundary against the same
UID. They do not test an OS-confined child, because Landlock/user namespaces
could not be enabled here. In particular, the inherited-descriptor control
shows why a future restricted child must not receive a writable store FD; it
does not show a Landlock escape.

WHY: a trusted launcher must be able to install an OS-enforced policy before
starting the mutable L5 child; cooperative lock participation does not enforce
that boundary. WHAT: direct ABI and namespace probes in this disposable Cloud
runner. HOW CERTAIN: evidence-based that these tested mechanisms are unavailable
here; not proof of kernel-wide absence. WHAT-NOT-TESTED: actual Landlock path
rules, worker fork/exec under confinement, whether Landlock would block an
inherited writable descriptor, lock inode replacement, and entrypoint
completeness. Same-UID unguarded L5 and POSIX bypasses plus selected owner
kill/reap histories are tested below, but only outside an OS-confined child.
Further confined tests depend on an enforceable restriction and trusted custody
boundary.

# Minimum additional trust/process separation

A follow-on needs a host/runtime that allows a trusted launcher to install
Landlock before `exec`, or an OS-managed separate service identity that owns
the mutable store. The latter is the minimum trust/process separation if this
runner's confinement restrictions persist: the launcher and broker run as the
store-owning UID, and the L5 worker runs as a distinct unprivileged UID. The
worker must lack store-path permissions and receive no writable store
descriptors; a narrow broker must validate and serialize every mutation. All
management entrypoints must route through that trusted launcher/broker. The
broker's storage directory and lock inode must be owned and replaceable only
by the broker identity, so the worker cannot unlink/recreate a lock or change a
path between validation and publication.

The boundary must explicitly cover inherited descriptors, fork/exec
descendants, `/proc`-based access, every launcher/entrypoint, and the deliberate
unguarded same-UID writer outside the boundary. The last remains an expected
bypass unless OS identity or host policy excludes it. Broker crash/restart
must release process-held locks only after actual death/reap and recover from
the L5 old/new whole-state publication point without guessing at stale lock
ownership. These are future proof obligations, not findings from this run.

No confined-child native test or implementation was run because the required
confinement primitive failed its initial availability gate. The unguarded L5
bypass, owner-kill/reap, and same-UID POSIX controls above are native negative
and lifecycle evidence, not evidence that a hostile same-UID writer is
confined. This is the exact blocker requested by the frozen packet; no
stronger claim is made.
