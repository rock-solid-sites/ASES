# Selected durable-dependency inventory/disposition discriminator

Freeze fromcc7574fc057755863fd0f0bab227e77e535d0eaf before implementation/execution.
Governing current same-ref Phase-I-Verification T13/T23 and Closure H14/section7:
accepted-list emptiness is insufficient; unaccepted durable candidates need disposition;
interrupted disposition must preserve remaining dependents and block final removal.
L1-L5 do not implement this gate. No unavailable Landlock retry: native F3 confinement
and real credentials remain blocked/untested. This is a concrete store/policy subset,
not whole L6 or an extension falsely attributed to the fixed four-unit L5 graph.

Small independent disposable candidate store: one sealed unit, SQLite current unit/
dependency records outside its flat owned data directory. All cooperative mutations
obtain BEGIN IMMEDIATE before touching objects. Files hold exact accepted/candidate
bytes; SQLite synchronous FULL, DELETE journal. Trusted management commands only,
no untrusted execution ingress or source/credential authentication claim. Every new
durable object must remain within this enclosing directory, including unregistered
preparation debris. No imported model state/oracle expectations supplied to recovery.

Tests fixed before implementation:
1. Real writer creates/fsyncs unaccepted z, INSERTs dependency inside uncommitted SQL
   transaction, emits prepared gate, then is SIGKILLed/reaped. Catalog rollback leaves
   accepted and all-dependency counts zero but real z survives. Separate actual roots
   compare accepted/catalog-only removal mutation (records logical removal while z
   survives) against current-directory inventory guard (deny unchanged, retain unresolved
   bytes/sealed unit). This is a logical removal/admission counterexample, NOT native
   access exposure or existing L5 production defect. Do not delete unknown debris.
2. Actual accepted x and unaccepted z commits/ACKs, exact x read. Disposition x COMMIT
   followed by pre-unlink/pre-reply gate, kill/reap. Fresh process receives root only,
   reconstructs sealed x-disposed/z-live, refuses old x read, retains exact live z.
   Guarded removal denies. Explicit disposed-x cleanup retains z; explicit z disposition
   then empty-directory check/removal positive. This is declared logical disposition,
   not secure erasure of old raw descriptors/backups or all failure atomicity.
3. Independently empty sealed unit removal positive (prevents universal-denial pass).

Final removal guard checks complete actual directory while cooperative write lock held,
not only catalog or accepted list. Logical unit deletion plus rmdir are separate native
steps; no untested interruption across those steps is claimed atomic. Retained logical
references query current disposition; raw same-UID files/handles are outside this
mediated access profile and do not establish host protection. Unknown/missing/inconsistent
material remains unresolved, no empty bootstrap/discard manufactured as recovery.

Capture source/executable identity, exact DB queries/statements, actual process/gate/
ACK/bytes/hash/exit and fresh reconstruction, positive/weak/missing-evidence controls.
<=256MiB per process, finite<=3s IPC waits, no more2 child processes active (prefer1),
whole<=45s. Commit source before run; preserve harness failures separately. No canonical
schema/policy/host/production mutation, physical power loss or generic L6/F3/F4 closure.
Next: T15 actual new-dependent race with removal, if this inventory mechanism survives;
otherwise smallest failing discriminator repair. Never claim inventory complete beyond
declared enclosing-root/all-writer premise.
