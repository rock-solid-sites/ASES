# Guarded bookkeeping versus native exclusive resource occupancy

Frozen frome035dec before code/execution. Prior SQLite capacity experiments establish
serialized record conservation; abstract active-use/reassignment tests stipulated
surviving activity. They did NOT claim an allocation record alone proves a usable
native resource. New selected profile promises a usable exclusive owned loopback TCP
listener at successful acquisition ACK, while its owner/retained descriptor lives.
This is a disposable resource, not host confinement or a persistent-port guarantee.

Hypotheses: guarded free ledger suffices for native acquisition after release/process
death; or independently surviving native occupancy must be included before ACK.
Cheapest three actual histories, capacity1/disposable SQLite:
1. Owned A listener remains alive after actual ledger release COMMIT/ACK. Deliberate
ledger-only B path ACKs its claim before bind; actual bind must fail EADDRINUSE although
SQL conservation holds. Record failure, then explicit fixture cleanup of B's unbacked
row (no hidden repair). Native-bind-before-COMMIT/ACK path denies and ROLLBACKs while A
still holds listener. Actual A close then B native acquisition succeeds.
2. A release then actual kill/reap without retained reference; B native acquisition
succeeds. Process death is a positive sufficient release control only in this case.
3. A transfers actual listener fd over Unix SCM_RIGHTS to owned keeper; A releases
ledger and is killed/reaped, keeper survives. B native path denies/EADDRINUSE. Explicit
keeper fd close/exit then B succeeds. No parent listener copy remains. This separates
original process death from actual resource reference lifetime.

A/native guarded B processes only operate on owned ephemeral 127.0.0.1 listener; no
external connections/scanning/configuration. Stdlib socket/SQLite, <=2 owned children
at once,256MiB inherited, finite pipe/socket waits. Capture exact fd/port identity and
transfer, native errno/getsockname/SO_ACCEPTCONN, durable claim/release/native attempts/
ACK ordering, real process exits, independent parent bind probe and ledger reads.
After successful B ACK, actual B termination should free native listener while its
durable claim row remains; qualify this as ephemeral-resource lifetime/reconciliation
limit, not durable resource restoration or unqualified allocator defect.

Keep SQL admission, actual acquisition, active reference, release and durable recovery
distinct. Only selected new whole-resource ACK adapter discriminated, not proof old
record-only tests failed their scope. No actual credential revocation/confinement,
Landlock retry, physical power loss, cross-host binding, arbitrary resources, fairness,
maximal liveness, generic C3/C5/F1 or PhaseI closure. Every child/descriptor belongs to
this disposable test root. Source/executable hashes/raw and exact reproduction retained;
missing native/transfer/process metadata INCOMPLETE. Next independent check or actual
resource persistence/reconciliation discriminator only if new uncertainty remains.
