# Acknowledged revocation survives selected managed replay

Execution source5fa2dbc (full SHA in replay.raw.json), same authorized disposable
Cloud host. Reproduce `python3 research/phase-i-t18-sink-order-20261103/managed-revocation/replay_probe.py > /tmp/managed-replay.json`, then
`python3 research/phase-i-t18-sink-order-20261103/managed-revocation/check_replay.py /tmp/managed-replay.json`.
The later read-only checker additionally verifies20 nonoverlapping owned-process
intervals/PIDs; no behavioral rerun was needed for this raw-metadata check.

WHY: selected live eligibility must survive an ACKed revoke/process-death boundary.
WHAT: actual same-file writer/recovery/cold histories, no ACK oracle passed to runtime,
strict bounded transition parser before ready, all requests/status/effects/journal
bytes plus process/time/source/executable hashes. Certainty: executed selected evidence,
coordinator checker; independent primary review covers earlier7ed639c only, not replay.

Reference retains prior positive ACK plus revoked/grant=false/active=false/gen1 at
ready. Token1 denies even though still equal to last-issued1. Regrant2 without activate
denies, activate2/current2 ACKs, old1 denies. Second real restart retains both ACKed
payloads and state. Separate committed exact m/x remains available after replacement
and actual restart at inactive2, while ordinary current2 use denies; delivered x then
survives another restart. Diagnostic sequence gaps are allowed, not invented events.

Replay-resurrection mutation restores grant/active after parsing a revoked history;
actual token1 then accepts201/x. Checker first detects grant-state divergence at ready,
and raw independently shows unsafe acceptance. Subsequent strict baseline recovery
refuses that mutant-generated unlicensed effect, rather than pretending it was valid.
This is a deliberately weakened representation, not a pre-existing baseline defect.

10 invalid histories (empty, truncated, unknown event, duplicate key, Boolean seq,
Boolean generation, wrong unit/profile, illegal activation and stale regrant) all
refuse before ready without changing bytes. Missing ACK and recovery-byte controls
are INCOMPLETE.20 actual owned children have distinct PIDs, disjoint observed intervals
and exit/reap observations; maximum1 active. Fresh-mode original T18 controls/regression
still support selected intended behavior; raw and checker output retained.

Limit counterexample: an actual older authentic pre-revoke ACKed prefix, deliberately
installed into a separate rollback-control root, passes syntax/transition replay and
accepts old1. Thus replay supplies no external freshness/rollback guarantee. Reference
histories do not copy fixture bytes into runtime; rollback control explicitly violates
the trusted-current-journal premise. Correct current journal/root and trusted supervisor
remain external premises. Original SHA256SUMS applies to initial7ed639c source; new
REPLAY-SHA256SUMS binds current replay source/new evidence, preserving chronology.

WHAT NOT TESTED: authenticated/independent manager, native host enforcement or genuine
credential revocation, durable root authentication, independent nonrollback witness,
physical power loss, this profile's injected fsync faults, hierarchy, concurrent writers,
exactly-once. No general F2/F4/F1-F5 completion. Cancellation of exact obligations by
revocation remains a separately unfrozen contract, not inferred from replacement.

Next cheapest discriminator: an external live witness that only remembers issued
generation versus one that also binds revocation/eligibility changes; couple its actual
reply to sink acceptance. Gen1 is unchanged at revoke, so generation-only freshness may
fail even with a genuinely live nonrolled witness. This extends earlier F1 admission-only
witness evidence into the actual sink path under explicit local source/ordering premises.
