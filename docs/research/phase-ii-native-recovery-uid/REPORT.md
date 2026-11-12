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
The driver needs to transfer that case root to UID 2000 before launching the
manager. No successful UID-custody result is claimed until a new capture
completes both fixtures and the raw checker passes. Any retry uses a separate
evidence directory.

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
