# Executed flat-root inventory and logical disposition subset

One primary execution at14706d7 completed four cases/eight owned children, max overlap1.
Source/executable identities, exact SQL traces, process/gate observations, caller JSON
lines and actual catalog/directory/byte snapshots are in `raw.json`; `check.json` passes.
Both stderr files are empty. Reproduce with `timeout 45 python3
research/phase-i-protected-work-unit-f3/lifecycle/l6-inventory/probe.py > /tmp/l6.json`
then `python3 research/phase-i-protected-work-unit-f3/lifecycle/l6-inventory/check.py /tmp/l6.json`.

Two actual candidate writers fsynced z, inserted its catalog row inside an uncommitted
transaction, then were killed/reaped at the retained gate. Independent catalog readers
saw zero committed rows before/after termination; exact z bytes survived in the owned
unit directory. Thus even an all-dependency catalog, not just an accepted list, can
omit durable preparation debris. Fresh management reconstruction reports unresolved
unregistered material, not successful empty recovery. The directory-inventory guard
denies removal without changing bytes or current unit. The explicit catalog-only
mutation records logical removal while z survives: a policy/admission counterexample.
It does not demonstrate native host exposure or a defect in the preexisting L5 API.

Actual accepted x/candidate z COMMITs and replies precede a successful exact x read.
Disposing x commits the logical disposition, then a pre-unlink/pre-reply gate is killed.
Fresh root-only management reconstructs sealed x-disposed/z-live; exact x bytes remain
private debris, old logical x read denies without content, and z read retains exact
bytes. Premature removal denies; explicit disposed-x cleanup preserves z, removal still
denies, explicit z disposition followed by complete empty-directory check permits
logical removal and actual rmdir. Independently empty removal is a positive control.

Missing recovery observation is INCOMPLETE; contradictory directory/catalog inventory
is VIOLATION. Source hashes match execution git objects and all serving sources match
their recorded hash. This is executed bounded evidence, without independent reproduction
at publication. Native confinement remains blocked; no Landlock attempt occurred.

Limits: one flat enclosing root, trusted management/all cooperative creators under the
same SQLite write lock; no descendants, hostile source/UID/namespace/descriptor bypass,
arbitrary directory mutation or complete F3/L6/T13/T23 acceptance. Logical access denial
does not revoke raw same-UID descriptors/backups or establish physical erasure. The
postcommit gate records no success response observed, with source waiting for input;
this harness does not separately drain/capture remaining stdout at EOF after termination.
That missing transport metadata is not claimed as an independent universal absence proof.
Final SQL removal and rmdir are separate steps; interruptions there and general failure
atomicity are untested. File fsync/process death do not establish machine power loss.
Unknown debris is preserved; no automatic cleanup/reset is presented as recovery.

Next: actual T15 new-dependent creation overlapping the current empty scan/removal,
with write serialization versus a detached scan. First capture/drain EOF transport
metadata for that new harness; do not rerun these cases solely for prettier logs.
