# Managed eligibility replay discriminator

Frozen after primary managed evidence7ed639c, before replay implementation/execution.
Research extension, no canonical adoption. Competing hypotheses: replaying only issued
generation is sufficient; or acknowledged grant/activation/revocation history must be
reconstructed before serving. Equal token1 after revoke must not regain eligibility
at restart. Existing implementation explicitly refuses restart, so its behavior is an
availability limit, not already a stale-acceptance defect.

Cheapest test: retain actual journal from create/grant/activate/positive/revoke ACK,
kill/reap serving child, request explicit managed recovery on that same file. Before
ready, validate complete bounded typed managed event history, monotonic sequence,
C/p/profile identity, transition/currentness and exact payload commitments. Rebuild
eligibility, holder, generation, obligations/effects; unknown/invalid/truncated history
refuses before ready without writing. Fresh mode keeps refusing existing journals.
After recovery token1 remains denied although lastissued1; explicit grant2 then
activation2 enables current2 while old1 denied; kill and recover again retaining both
ACKed positive effects. Separate replacement history retains exact m/x and inactive2.
One replay-only mutant restores granted/active after reconstructing a revoked state;
same actual source history must expose post-restart token1 acceptance. This mutant is
not the baseline product and must be reported as a new weakened representation.

Controls: empty/truncated/unknown event, duplicate keys, Boolean sequence/generation,
illegal activation/regrant, missing revoke after genuine ACK are distinct cases.
The last is a LIMIT control: a syntactically valid older prefix can be accepted without
an external currentness witness; do not claim journal replay supplies rollback proof.
No power-cut simulation. Bound one child at a time/256MiB/local HTTP and synchronous
refusal subprocesses. Preserve exact hashes/raw calls/journal/process timing, fresh and
recovery statuses, all ACK inclusion, two checker missing-evidence controls. No prior
ACK/oracle state is passed to runtime recovery, only actual path and explicit mode.

Completion: durable branch/source/raw/checker plus qualified result. Selected
same-host trusted-current-root/journal and manager premise only. No native confinement,
credential/source authentication, arbitrary corruption repair, concurrent manager,
exactly-once, fsync failure coverage, general F2/F4 or PhaseI completion. Next discriminator
is an independent authority/witness or bounded manager concurrency, not more identical
restarts. Freeze exact obligation cancellation semantics separately before claiming it.
