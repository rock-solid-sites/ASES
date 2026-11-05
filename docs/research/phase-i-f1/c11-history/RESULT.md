# Atomic latest pairing does not retain independently required earlier evidence

Execution sourceaa1c8f7 (full SHA raw.json). Reproduce
`python3 docs/research/phase-i-f1/c11-history/probe.py > /tmp/c11-history.json`, then
`python3 docs/research/phase-i-f1/c11-history/check.py /tmp/c11-history.json`.

WHY: latest-only C11 coupling left required-history/stable-identity gaps. WHAT: actual
single-lane original holder commits, stable opaque identity/genesis/created-by/project
across both acceptances, earlier independent evidence A/B, common later evidence M,
actual durable gate/SIGKILL, fresh holder and separate read-only SQLite process without
original tuples. Certainty: bounded executed evidence/coordinator checker, no independent
review of archive extension.

Latest-A/B: both actually ACK earlier zero/evidence A or B, then commit later one/M
atomically before process death/no reply. Latest pairing recovers correctly, but logical
consumer query/core view/serialized latest observation row are identical across A/B and
contain only later M. Required earlier evidence cannot be answered by that retained
consumer representation. Do not extend this to all physical stale-page bytes or every
possible external authority/source; no such proof was run.

Archive-A/B: experimental content-indexed immutable observation archive writes older/
later record in same existing SQLite transaction as each commitment. Repeated identical
bootstrap write is idempotent. Both actual accepted contents/evidence records recover;
older A/B remain distinguishable, later M and fixed three identity fields agree.
Original latest row stays coupled, not repurposed as historical evidence.16 actual
owned distinct children/max1, all reaped; fresh read-only integrity ok. Missing retained-
record/reply observation controls INCOMPLETE. No recovery observer/oracle tuple supplied.
Conflicting same-content record branch is source-reviewed only, not executed here.

Small parent Holder hook adds extra config/source arguments with original defaults;
no parent service/canonical/main changes. Parent hashes/manifests refer to historical
source29ec396; new manifest binds continuation source/raw. Earlier singleton result
was qualified latest-pair evidence, not rewritten into full C11 history retention.

WHAT NOT TESTED: authoritative/stable intrinsic identity truth (opaque fixed fields are
fixture premises), provenance/source authentication, independent nonrollback, power loss,
arbitrary histories/consumers, same-content differing-evidence contract, invalid archive
validation, concurrent writer, storage minimality/schema mandate, generic C11/F1/PhaseI
acceptance. Retention of accepted observations is distinct from validating their truth.
This implementation stores selected accepted evidence history, not a new required
methodology or full record requirement for all implementations.

Next cheapest discriminator: malformed required observation inputs before a new content
commit, and conflicting same-content observations. Check whether validation occurs
before commitment, rather than only when recovering/querying already-committed bytes.
Keep trusted well-typed input premise of completed runs explicit.
