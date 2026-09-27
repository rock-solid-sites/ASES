---
title: Kernel-0 Stronger Realization Direction
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Derived
canonical_repository: ASES
crosslink_issue: 567
depends_on:
  - Kernel-0-Re-Minimization.md
  - Kernel-0-Refinement-Assurance.md
consumed_by:
  - Future bounded Kernel-0 substrate assurance
---

# Phase 7 decision: retain the small transactional reference and attack storage cuts

The evidence does not justify rewriting the transition core in a lower-level
language or building a production authority service. A verified-source core would
not establish the still-assumed storage currentness and crash-consistency contract.
The still-live implementation remains appropriate to its original executor-loss
claim; the transactional variant is the reference for the stronger process-loss
profile. Neither is a production architecture endorsement.

The next discriminating bounded experiment is **actual holder termination at
observed storage-call boundaries**. Earlier `prepared`/`durable` API gates can miss
journal/database writes inside SQLite. Interpose only in a test child process,
trace actual positional writes, synchronization, truncation and journal removal
for the private experiment directory, and pause before/after each observed call.
The supervisor kills the holder there and restarts an uninstrumented holder from
the surviving files. No model snapshot supplies recovery state.

First require a successful uncut trace showing database and journal writes,
synchronization, and journal removal. Only then replay each observed cut and
compare recovered state against the original abstract whole endpoints. Test a
composite work effect, content acceptance and authority replacement. A following
old-evidence attempt must agree with the recovered relation. A single successful
whole-state round trip is insufficient evidence for coverage.

The test library uses Linux dynamic-linker interposition with `RTLD_NEXT`; this
wraps, rather than replaces, actual calls. Positional writes and synchronization
have their documented Unix meanings. References:
[dlsym](https://man7.org/linux/man-pages/man3/dlsym.3.html),
[pwrite](https://man7.org/linux/man-pages/man2/pwrite.2.html),
[fsync](https://man7.org/linux/man-pages/man2/fsync.2.html).
Only test-generated paths and descriptors are instrumented; the parent process and
normal recovery service do not load the library. Source/runtime/compiler/library
hashes and call-level evidence must be retained, not the disposable compiled file.

The failure class remains process SIGKILL with a live OS/filesystem. Before/after
call cuts do not inject torn sectors, lost successful flushes, reordered device
writes, ENOSPC/EIO, malicious rollback or failure during recovery itself. No
power-loss or universal SQLite proof can follow. If the observed sequence is
platform-specific, report the platform and exact covered sequence rather than
claiming coverage of all VFS paths.

## Result: bounded storage-call and partial-write experiment survives

`kernel0_io_interposer.c` is a test-only library compiled with the installed C
compiler. `kernel0_io_check.py` first verifies that the library sees the actual
private database/journal I/O during an acknowledged request. It then replays the
same exact observed prefix at each cut, terminates the holder with SIGKILL, and
starts the ordinary uninstrumented service. No production source or global loader
configuration is modified. The interpreter, SQLite and OS remain trusted.

For each of composite work update, content acceptance, and authority replacement,
the control trace contains **30 before/after points** at positional writes,
`fdatasync` and journal `unlink`. All **90 targeted process kills** recover one
whole permitted endpoint. For each operation, 29 cuts recover old state and the
post-journal-removal cut recovers new state. Every following old-evidence replay
agrees with the recovered authority relation. Recovery after actual main-database
writes rolls back correctly; these are not only tentative memory-image cuts.

The additional partial-write discriminator splits each of the two observed
4096-byte main-database writes at 2048 and 4080 bytes, pauses after the real prefix
write, and actually kills the process before the suffix. All **12 deliberate
partial-write cases** recover old whole state. Raw-file digests confirm **10 of
12** intermediate images differ from both uncut endpoint images; the other two
are not claimed to be physically mixed just because a prefix write occurred.
The partial-write cases are explicitly induced by the test library, not reported
as naturally observed torn device sectors or interruption inside one kernel call.

Evidence is `Kernel-0-Storage-Cuts-results.json`: exact event sequences and prefixes,
cut descriptions, restored state, replay result, process IDs, physical-image
hashes, source/library hashes and runtime/compiler versions. The successful run
used Linux x86-64/glibc 2.35, Python 3.10.12, SQLite 3.37.2 and GCC 11.4.0. Reproduce
as an agent with installed `cc`, without Python `-O`:
`python3 docs/research/kernel-0/kernel0_io_check.py --output PATH`.
The checker builds only a temporary library and database files. It requires local
Unix sockets, inherited descriptors, process termination and dynamic interposition.

### Adversarial interpretation and remaining gap

The preliminary cheapest test demonstrated real intercepted calls before the
coverage run; zero hooks would have failed, not passed vacuously. Every replay
checks the complete prefix against its control trace, not merely a target counter.
Each operation has both old and new recoveries. Every case restarts the normal
service from disk, and control runs verify an acknowledged operation survives.
A separate negative test in Phase 1 still restores a stale same-root image and
resurrects authority: this experiment does not repair or erase that boundary.

Interposition itself is trusted measurement apparatus. It does not enumerate
unintercepted APIs, alternative SQLite VFS implementations, write errors, failed
flushes, recovery interrupted again, arbitrary content size or all schedules.
Actual synchronization is performed, but the machine is never powered off.
The partial-write injection extends the tested write pattern while preserving a
live OS; it does not simulate a controller lying about durability or corrupting
unrelated bytes. No adversarial rollback resistance, media-loss recovery or
unbounded implementation proof is claimed.

## Final direction and stop

Keep the small transactional holder as the reference for this recovery profile.
The test-only low-level library is not a proposed lower-level kernel. A verified
transition core would address a different uncertainty; a replacement storage
engine, replication, general coordinator or production service is not justified
by these results. The ordered seven-phase program is complete within its declared
bounds, so no further implementation expansion is selected in this run.

The next recorded research action is independent adversarial review of the frozen
final source/evidence tree, focused on recovery currentness, bearer reconstruction,
whole-trace checker soundness and instrumentation adequacy. If a stronger failure
claim is later selected, first choose one explicit storage-fault model (for example
failed writes or interrupted recovery); design its smallest discriminator before
changing architecture. Host power loss and arbitrary hardware correctness remain
unestablished, not silently converted into obligations on the operator.

**WHY:** actual write/synchronization/removal cuts attack a previous concrete
coverage gap without adding production machinery. **WHAT:** 90 natural call-boundary
kills plus 12 deliberately partial writes, exact event prefixes and normal recovery.
**HOW CERTAIN:** bounded realization evidence; no independent review or storage
proof. **WHAT-NOT-TESTED:** exclusions above. No new Kernel-0 primitive or canonical
semantic change. No earlier in-profile result was falsified; all negative results
remain recorded with their dispositions.
