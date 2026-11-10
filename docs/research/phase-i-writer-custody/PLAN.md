---
title: L5 single-writer custody boundary probe — frozen packet
program: EDASES
layer: Research
document_type: Research Protocol
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/research/phase-i-f1-recovery-repair/L5-PLAN.md
  - docs/research/phase-i-f1-recovery-repair/REPORT.md
  - docs/methodology/Agent Model Launch Routes.md
related_documents:
  - REPORT.md
---

# Frozen question and boundary

**Question.** Can this Codex Cloud Linux environment enforce a small trusted L5
launcher boundary that gives one authorized child exclusive mutation authority
for one disposable store, beyond a cooperative `flock`, while allowing an
unguarded writer outside that boundary to remain an explicit bypass?

**Threat boundary.** The trusted launcher/broker and its store custody are in
scope. A restricted descendant must not regain store mutation through normal
path opens, inherited directory/file descriptors, or a fork/exec descendant.
An independently launched unguarded same-UID process remains outside the
boundary and is expected to bypass it. This experiment must not claim
confinement of arbitrary hostile same-UID processes. A stronger claim requires
separate OS identity/permissions or a trusted broker whose store is inaccessible
to the worker, plus complete launcher/entrypoint ownership.

**Smallest candidate.** Test whether kernel Landlock can be installed by a
trusted launcher with `no_new_privs`, before starting the L5 worker, to deny
store writes to that worker and its descendants. The store remains under the
trusted launcher's control. If unavailable, stop without implementing a
cooperative substitute or claiming a custody guarantee.

# Fixed checks

1. Record kernel/runtime identity, effective capabilities, seccomp and
   `no_new_privs` state.
2. Query Landlock ABI using `landlock_create_ruleset(...,
   LANDLOCK_CREATE_RULESET_VERSION)`.
3. Check existing namespace helpers only with disposable no-op invocations;
   do not modify host configuration or install packages.
4. If an enforceable boundary is available, freeze a follow-on packet before
   code and test: authorized mutation, denied path mutation, inherited writable
   FD, fork/exec inheritance, independent unguarded same-UID bypass, broker and
   worker crash/reap, lock inode replacement/custody, and every management
   entrypoint. Use disposable roots and retain raw traces.
5. If the boundary cannot be installed, record the exact result and stop. State
   the minimum additional process/identity separation needed. Do not create an
   unconfined approximation.

# Stop and success conditions

Success is a demonstrated OS-enforced restriction inherited by worker
fork/exec, with the bypass and lifecycle limits above kept explicit. A
Landlock availability failure, blocked namespace setup, or inability to place
mutable storage behind a distinct trust boundary is a blocker, not a pass.
No production, CI, host configuration, package installation, credential use,
external publication, or billable resources are in scope.
