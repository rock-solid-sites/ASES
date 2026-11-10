# Expired work cannot be finalized into a different history

The unchanged experimental runtime accepted `finalize` from EXPIRED for all
four supported labels: completed, failed, cancelled and interrupted. Each
independently expired fixture became CLOSED with both EXPIRED and FINALIZED
events. Its existing read-only resume interpreter then refused the conflicting
evidence. The regression's before run failed as expected (exit 101), after
preserving all four histories and the valid cancellation neighbor.

The repair is a three-line source-state whitelist after the existing CLOSED
replay and LAUNCHING guards. Finalization can proceed only from RESERVED,
AUTHORIZED or RUNNING, subject to the existing per-state checks. EXPIRED and
unrecognized states refuse. No expiry timing or accounting rule changes.

After repair, all four attempts refuse with EXPIRED intact. Job state, event
history and compact resume view remain byte-equivalent as JSON values;
available capacity remains 100 and repeated expiry changes nothing. A valid
still-reserved cancellation and exact CLOSED replay continue to succeed. All
48 control tests and five resume-view tests passed, offline and locked, on
the existing user-owned Rust toolchain. These targeted suites cover the
changed transition and its interpretation; no native worker or external
service is involved.

The [before histories](evidence/before/expiry-histories.json),
[after histories](evidence/after/expiry-histories.json), complete test logs and
[source hashes and exact commands](evidence/source-and-commands.json) retain
the comparison against PR #25 commit
`9fb8a525c32b56b9191d3f33df9925939636dc9a`. Test clocks use explicit logical
Unix-second inputs; this is not a wall-clock or power-loss experiment.

This establishes the observed transition correction for the experimental local
store. It does not establish storage custody, a universal recovered-database
validator, process termination, a provider adapter or an integration with the
separate termination-evidence branch. No canonical policy, main, deployment,
CI or independent review was changed or run.
