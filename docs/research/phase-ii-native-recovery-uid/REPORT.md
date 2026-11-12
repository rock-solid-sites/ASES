# UID-custodied native recovery

This capture joins the actual strict reconciliation and explicit local
observation commands to the existing UID-2000 manager / UID-2001 worker route.
It is limited to two actual native histories: a locally recorded event after
append, and a complete event at the fsync-before-owner-callback boundary.

## Experimental status

The bounded UID-separated experiment passed in [run-04 raw evidence](evidence/run-04/raw.json),
and the focused checker passed in [run-04 checker output](evidence/run-04/check.json).
Source files were verified against commit `59c446205260578b60b7008dea8805c79af9120c`.
The run used the pinned 119614344-byte VFS image, one networkless constrained
container, and removed that exact labeled container after exit 0. The checker
also rejected both negative controls: a worker management result changed to
allowed, and a success-shaped recovery result with the owner still pending.

The local history reached the actual after-append gate with owner status local
at sequence 4. Strict reconciliation published with one witness CAS and settled
that same event without adding journal bytes. The reserved history reached the
real post-fsync/pre-owner-callback gate with a complete RetryState-indexed event
at sequence 4 and owner status reserved with no sequence. Explicit local
observation then published with one CAS and settled the same event without
adding journal bytes. Both actual cold restarts accepted the full published
cut.

In both fixtures the UID-2001 worker and fork/exec descendant had observed
real/effective/saved/filesystem UID and GID 2001, no supplementary groups,
zero permitted/effective capabilities, and `NoNewPrivs=1`. `CapBnd` was
recorded as the observed value rather than presumed empty. `fstat` and
`F_GETFL` on existing descriptors found no writable regular authority FD. Both
real recovery CLIs reached the protected owner store and returned structured
`PermissionError`; protected `CURRENT`, sink, and witness access attempts got
EACCES. The mediated management operation was denied before forwarding, and
the owner/F1/material/journal/witness state was unchanged across those denied
attempts.

After recovery, manager-owned F4 replacement/activation reached version 2 and
the native owner sealed, moved, and activated the source. A new worker ID with
an envelope derived from the current epoch/selector reached the native path
denial (`native-current-path-denied`) and appended no bytes. The old accepted
ID returned `already-accepted` using the exact original event payload from the
RetryState index, with no new journal bytes.

The earlier failed captures remain preserved: [run-01](evidence/run-01/raw.json)
records the manager case-directory ownership mistake; [run-02](evidence/run-02/raw.json)
records the worker `Path` connection argument and wrong wrapper path; and
[run-03](evidence/run-03/raw.json) records the initial FD audit's invalid
`/proc/self/fd` reopen method. Each failure was fixed before a fresh, separate
capture. The checker passes only run-04.

## Evidence

The capture retains the raw source hashes, container identity/invocations,
worker and manager `/proc` facts, protected-store/socket denials,
owner/F1/journal/witness snapshots, recovery CLI results, cold restart,
post-move current denial, and exact historical replay. The checker includes
controls for an allowed worker management result and a success-shaped recovery
frame that leaves the owner pending.

## Scope

The evidence does not test hostile same-UID/root actors, deliberate writable FD
leaks, host loss, arbitrary programs, general confinement, or deployment.
