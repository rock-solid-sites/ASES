# Native occupancy survives record release and a transferred reference survives owner death

Execution source7c2f1a7 (full SHA raw.json). Reproduce
`python3 docs/research/phase-i-f1/resource-occupancy/probe.py > /tmp/resource-occupancy.json`, then
`python3 docs/research/phase-i-f1/resource-occupancy/check.py /tmp/resource-occupancy.json`.

WHY: record conservation alone did not test concrete resource backing or surviving
active references. WHAT: owned ephemeral loopback bind/listen, actual SQLite claims/
release COMMIT, exact child wire frames plus parent receive times, actual native errno,
SCM_RIGHTS inode/address identity, child kill/reap and parent independent bind probes.
Certainty: bounded executed evidence/coordinator checker; no independent review yet.

Live A: release COMMIT/ACK leaves ledger empty while A still listens. Deliberate ledger-
only B adapter commits/ACKs B row before native attempt, then actual bind fails EADDRINUSE;
SQL capacity1 conservation still holds. This falsifies sufficiency for the selected
native-acquisition ACK promise, not earlier SQL-only test scope. Explicit cleanup of
unbacked B row retained. Bind-before-COMMIT native path denies busy/ROLLBACK/no claim.
A closes actual resource while process lives, then B binds/listens/COMMITs/ACKs.

A killed/reaped with no retained reference: actual native acquisition succeeds. Retained
case: exact listener fd transferred to owned keeper (same inode/address/SO_ACCEPTCONN);
A release/kill/reap does not free port, B gets actual EADDRINUSE and ROLLBACKs. Keeper
explicit fd close/normal exit permits B acquisition. Process termination and resource
reference release are distinct observations, not merely synthetic active-state bits.

Each successful guarded B ACK follows bind/listen and returned SQLite COMMIT; independent
parent bind probe confirms occupied port. After actual B termination, port becomes free
while durable B claim row remains. This is ephemeral-resource lifetime/reconciliation
limit, not durable native-resource recovery. Profile covers native bind/listen while
owned descriptor lives; application accept/traffic was not tested.10 actual distinct
owned children/max2, all reaped, empty stderr/unparsed frames, ledger integrity ok.

First checker missing-native control removed decoded field but left its real wire field,
so it correctly reported contradiction/VIOLATION rather than intended INCOMPLETE. Initial
assertion stderr retained. Corrected coherent omission now INCOMPLETE; original conflict
becomes explicit contradictory-evidence control/VIOLATION. Re-audited same raw; no physical
rerun. Failed control is a checker-fixture error, not native/product failure.

WHAT NOT TESTED: host confinement, actual credential revocation, Landlock, external
network, arbitrary resources, simultaneous allocation fairness, durable native backing,
physical power loss, cross-host state or full C3/C5/F1/PhaseI acceptance. No source/policy
or main change. Native acquired effect happens before SQL COMMIT; whole-effect failure
atomicity or invisibility of a tentative reservation is not established. Scope is one
resource-backed ACK adapter and explicit lifetime controls, not universal enforcement.

Next bounded independent audit. A new failure-boundary test could observe native binding
before actual SQL COMMIT failure, distinguishing ACK truth from failure atomicity only
under an explicitly chosen tentative-reservation contract; do not silently broaden claim.
