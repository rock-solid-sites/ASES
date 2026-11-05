# Native preparation visibility across actual SQLite COMMIT failure

Frozen fromce7515b before code/execution. Prior profile proves native bind/listen at
successful acquisition ACK while descriptor lives; it does not prove failure atomicity
or invisibility of precommit resource reservation. Selected discriminator: SQLite
isolation may hide uncommitted claim while native prepared bind is externally visible.
Do not silently broaden the promise or call prior SQL-only/profile evidence defective.

Cheapest three histories: an owned ephemeral port is released by parent before B begins;
parent independent SQLite connection holds a real read transaction on empty ledger.
B original guarded path begins IMMEDIATE, binds/listens and INSERTs, emits exact prepared
gate before COMMIT. Parent bind probe must getEADDRINUSE while its SQL snapshot is empty.
1. Reader remains: release prepared gate, actual COMMIT with100ms busy timeout must
failSQLITE_BUSY; record native/transaction state, explicit ROLLBACK/socket close, no
successful acquisition ACK, final ledger empty/native free.
2. Reader explicitly releases before gate continuation: same native prepare, COMMIT
succeeds then acquisition ACK, native occupied until B killed; durable B row remains.
3. B actually killed/reaped at prepared gate before COMMIT: current DB recovery has no
claim/native free, no acquisition ACK. Keep no-ACK/failed outcome and positive distinct.

Interpretation: transient native reservation is a real observed effect, even when no
durable claim/success ACK follows. A stronger profile forbidding all such precommit
effects is not established by this adapter; a profile permitting declared tentative
reservation must say so. No universal denial/failure semantics invented, no generic
repair by pretending rollback undid external history. Any exception beyond confirmed
BUSY+active transaction/rollback remains explicitly uncertain, not fabricated denial.

Same owned loopback resource/disposable SQLite only, no application/external traffic,
no host/credential/config change. One owned B child at once (supervisor has SQL reader),
256MiB, bounded pipe gates/100ms COMMIT waits/kill-reap. Preserve exact sources/frames/
SQLite error code, native probes, reader hold/release, SQL trace, process times and
actual cleanup. Missing gate/error/reply metadata INCOMPLETE. No physical power loss,
independent currentness, native durable restoration, atomic distributed effect, generic
C1/C3/C5/F1/PhaseI closure. Next choose lifecycle/acceptance contract or another genuinely
open obligation; avoid repeating larger broad-model/field/example batteries.
