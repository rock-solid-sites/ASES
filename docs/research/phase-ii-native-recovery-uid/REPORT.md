# UID-custodied native recovery

This capture joins the actual strict reconciliation and explicit local
observation commands to the existing UID-2000 manager / UID-2001 worker route.
It is limited to two actual native histories: a locally recorded event after
append, and a complete event at the fsync-before-owner-callback boundary.

## Experimental status

The one-shot UID-2001 audit worker and initial raw checker are in place. The
container runner and UID-2000 native fixture are being integrated. No successful
native recovery result is claimed until the bounded runner completes both
fixtures and the raw checker passes. Failed captures must remain in their own
new evidence directories; a later attempt uses a different directory.

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
