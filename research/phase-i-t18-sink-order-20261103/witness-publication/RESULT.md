# Selected revoke publication barrier evidence

Execution source4c0efe0 (full SHA raw.json). Reproduce `python3 research/phase-i-t18-sink-order-20261103/witness-publication/probe.py > /tmp/witness-publication.json`, then
`python3 research/phase-i-t18-sink-order-20261103/witness-publication/check.py /tmp/witness-publication.json`.

WHY: previous full-state witness depended on trusted supervisor synchronization.
WHAT: actual management/use HTTP, local durable revoke, live witness publication/check
transcripts, genuine old journal prefix, actual restart/cold replay, process/source/
executable hashes. Certainty: bounded executed evidence, coordinator read-only checker;
independent review of earlier witness projection does not cover this barrier extension.

Delayed update: actual successful revoke ACK precedes restart/rollback/send, but external
full-state witness still has old eligible state. Its fresh nonce-bound reply permits
actual x201/durable effect/cold retention. Later genuine witness publication of retained
revoked state denies further use. This falsifies unqualified sufficiency of a live full
eligibility witness, while preserving the earlier explicitly synchronized result.

Candidate barrier, revoke only: local append/fsync returns, grant/active clear, trusted
witness receives exact revoked tuple, publication reply root/nonce/state validated
inside local sink lock, then success200. Actual older-prefix restart/send afterward
gets409/no x. Startup never republishes possibly stale local state. Other management
transitions still use trusted supervisor initialization; no general distributed manager
protocol or canonical adoption is claimed.

Three publication controls all return503 with local_control_committed=true and a real
persisted managed_revoked event, not a success revoke ACK. Rejected publication leaves
witness active/old. Wrong-nonce reply follows real witness update to revoked: both
committed but publication ACK unusable to caller. Actual witness kill/reap before
revoke causes request failure: local revoked, remote unavailable. Current-journal cold
restart retains revoked state and denies old token in all three, even with witness dead.
17 actual owned distinct children/max2, all reaped; missing publication/local journal
controls INCOMPLETE. Prior guard projection/nonce/missing-endpoint regressions preserved
with compatible extended publication response protocol.

WHAT NOT TESTED: source authentication, independent trust/nonrollback, arbitrary root
rollback prevention, physical power loss, concurrent manager/global linearization,
all other control transitions, durable retry identifiers/completion of unfinished
management operations, exactly-once or aggregate F1/F4/PhaseI acceptance. Failed/unknown
revoke can leave local or both states committed; no rollback hiding that outcome. The
barrier does not make two stores atomically durable, nor establish liveness under
unavailable witness. Trusted manager must not publish rolled old state on recovery.
Historical parent SHA256SUMS belongs to7ee4837; local publication manifest pins extended
protocol/new artifacts. No original canonical policy or main changes.

Next discriminator: actual process cuts after local commit and after witness publication
before management reply; current-journal restart, honest no-ACK classification and
reconstruction of unfinished management provenance. Consult governing consumer/C11
criteria before inventing request metadata or claiming operation completion semantics.
