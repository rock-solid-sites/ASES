# SQL isolation does not hide an actual native prepared reservation

Source2d9ffda (exact SHA/raw hashes in commit-failure.raw.json). Reproduce
`python3 docs/research/phase-i-f1/resource-occupancy/commit_failure_probe.py > /tmp/native-commit.json`, then
`python3 docs/research/phase-i-f1/resource-occupancy/check_commit_failure.py /tmp/native-commit.json`.

WHY: native resource backing at successful ACK did not establish failure atomicity or
invisibility of tentative native effects. WHAT: owned ephemeral loopback bind/listen,
actual independent SQLite shared-reader transaction, B IMMEDIATE/INSERT/prepared gate,
parent native bind probe while reader snapshot empty,100ms real COMMIT wait, actual
SQLITE_BUSY/error code/transaction state, rollback/close or ACK, process/recovery evidence.
Certainty: bounded executed cases with coordinator read-only checker; no independent
review of this extension. Original native occupancy review covers parentce7515b only.

Held reader: native listener exists and independent parent bind getsEADDRINUSE while
SQL reader sees empty ledger and B's claim is uncommitted. Actual COMMIT returns
SQLITE_BUSY/code5 with active transaction; native same inode/address is still listening
before cleanup. Explicit ROLLBACK then socket close, structured commit-error result,
no successful acquisition ACK/claim; final native bind succeeds and ledger empty.
Rollback restores database state but does not erase the observed earlier reservation.

Released-reader positive: same prepared native effect observed, then actual reader
ROLLBACK before continuation; B COMMIT/ACK succeeds and native remains busy until B
termination. Durable B row remains after native release. Killed-prepared control:
actual B SIGKILL/reap before COMMIT, no acquisition ACK, current database recovery has
no claim and native is free. Prepared instrument frame is not a success ACK. Three
actual owned B children/max1, all reaped, stderr/unparsed frames empty. Supervisor SQL
reader/native probes are separately recorded parent observations.

First checker control repeated parsed-field omission while retaining real wire field;
raw frame consistency correctly reportedVIOLATION. Initial failure stderr preserved.
Shared coherent-omission helper now constructs genuine missing-evidence controls,
which reportINCOMPLETE; inconsistent frame remains explicitVIOLATION control. Both this
raw and parent raw re-audited with helper, no physical rerun to prettify logs. This
control-fixture error did not invalidate the successful actual three-case execution.

Interpretation: selected ACK ordering remains supported, but a stronger contract that
forbids any precommit native reservation is not established by this adapter. A policy
permitting tentative resource holds must disclose them. No universal denial/failure
semantics, all-or-nothing distributed effect or production defect is invented. No
application traffic, external endpoints, host confinement, credentials, power loss,
independent currentness, durable native restoration or generic C1/C3/C5/F1/PhaseI proof.
Parent source defaults unchanged except structured SQL-error telemetry/cleanup; no
canonical/main changes. Earlier manifests remain historical; new manifest binds this
extension. Next target actual declared preparation/visibility contract or a different
strong open obligation, not more cosmetic schema examples/broad-budget doubling.
