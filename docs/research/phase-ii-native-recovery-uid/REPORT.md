# UID-custodied native recovery

This capture joins the actual strict reconciliation and explicit local
observation commands to the existing UID-2000 manager / UID-2001 worker route.
It is limited to two actual native histories: a locally recorded event after
append, and a complete event at the fsync-before-owner-callback boundary.

## Experimental status

The implementation owner's native source smoke exercised the local and
reserved gates, both recovery CLIs, cold restart, transition, and exact-old
response. That smoke did not run the UID-separated container route. The
one-shot UID-2001 audit worker and raw checker are in place; the bounded
container capture is still pending. The first actual UID-container attempt is
preserved in [run-01 raw evidence](evidence/run-01/raw.json). The pinned image,
source hashes, bounded Docker settings, and exact container cleanup all
verified. Fixture setup then failed because UID 2000 could not create its
`native/` directory under the root-owned case root (`PermissionError: EACCES`).
The driver now transfers that case root to UID 2000 before launching the
manager.

The second actual attempt is preserved in [run-02 raw evidence](evidence/run-02/raw.json).
The corrected local case reached the real after-append gate, published exactly
one journal event through strict reconciliation, confirmed the full witness
cut, cold-started, moved/sealed the source, denied a fresh current ID at the
native path check without append, and returned the exact historical result for
the original ID. The one-shot worker audit exposed a probe bug: `socket.connect`
received a `Path` instead of a string and exited before its protected-store and
CLI checks. The reserved case then failed because the controller pointed at a
nonexistent fixture-local gate wrapper instead of the existing staged
local-observation wrapper. Both issues are fixed in source; this capture remains
failed and was not overwritten. No successful UID-custody result is claimed
until a new capture completes both UID-separated cases and the raw checker
passes. Any retry uses a separate evidence directory.

The third actual attempt is preserved in [run-03 raw evidence](evidence/run-03/raw.json).
The bounded container completed both local and reserved cases, and the outer
runner verified and cleaned up its unique task container. The one-shot worker
completed both direct CLI attempts, protected path/socket attempts, and its
fork/exec descendant; each protected route returned an actual EACCES or
structured `PermissionError`. The checker rejected this capture because the FD
audit reopened `/proc/self/fd/N` instead of inspecting the inherited descriptor
with `fstat`/`F_GETFL`. That produced permission errors on legitimate pipes and
made the FD evidence inconclusive. The worker now inspects the existing FDs
directly; run-03 remains unchanged and does not count as a complete pass.

## Evidence

The finalized capture will link the exact raw JSON, source hashes, container
identity/invocations, worker and manager `/proc` facts, protected-store/socket
denials, owner/F1/journal/witness snapshots, recovery CLI results, cold restart,
post-move current denial, and exact historical replay. The checker includes
controls for an allowed worker management result and a success-shaped recovery
frame that leaves the owner pending.

## Scope

The evidence does not test hostile same-UID/root actors, deliberate writable FD
leaks, host loss, arbitrary programs, general confinement, or deployment.
