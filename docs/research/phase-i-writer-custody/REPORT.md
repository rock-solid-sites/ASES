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
was installed, so there is no confinement claim and no inherited-FD test result.
No fallback based on `flock`, file mode bits, or a cooperative wrapper was
implemented.

# Observations and limits

- Runtime: Linux `6.18.57`, x86_64; Python `3.12.14`.
- Identity: uid/gid `1000(agent)`, no supplementary groups; effective,
  permitted and bounding capabilities are zero; `NoNewPrivs: 1`.
- Landlock: ABI version query on syscall 444 returned `-1`, errno 38.
- User namespace probe: `unshare --user --map-root-user --mount true` failed
  with `cannot open /proc/self/uid_map: Read-only file system` (exit 1).
- Bubblewrap probe: `bwrap --unshare-all --ro-bind / / -- true` failed with
  `setting up uid map: Read-only file system` (exit 1).

WHY: a trusted launcher must be able to install an OS-enforced policy before
starting the mutable L5 child; cooperative lock participation does not enforce
that boundary. WHAT: direct ABI and namespace probes in this disposable Cloud
runner. HOW CERTAIN: evidence-based that these tested mechanisms are unavailable
here; not proof of kernel-wide absence. WHAT-NOT-TESTED: actual Landlock path
rules, worker fork/exec, inherited writable descriptors, same-UID bypass,
L5 native adversarial/control/crash histories, lock inode replacement, and
entrypoint completeness. Those depend on first obtaining an enforceable
restriction and a trusted custody boundary.

# Minimum additional trust/process separation

A follow-on needs a host/runtime that allows a trusted launcher to install
Landlock before `exec`, or an OS-managed separate service identity that owns the
mutable store. For the latter, the L5 worker must not have store-path
permissions or receive writable store descriptors; a narrow broker must
validate and serialize every mutation. All management entrypoints must route
through that broker. The broker's storage directory and lock inode must be
owned and replaceable only by the broker identity, so a same-UID worker cannot
unlink/recreate a lock or change a path between validation and publication.

The boundary must explicitly cover inherited descriptors, fork/exec
descendants, `/proc`-based access, every launcher/entrypoint, and the deliberate
unguarded same-UID writer outside the boundary. The last remains an expected
bypass unless OS identity or host policy excludes it. Broker crash/restart
must release process-held locks only after actual death/reap and recover from
the L5 old/new whole-state publication point without guessing at stale lock
ownership. These are future proof obligations, not findings from this run.

No code or native L5 adversarial/control/crash suite was run because the
required confinement primitive failed its initial availability gate. This is
the exact blocker requested by the frozen packet; no stronger claim is made.
