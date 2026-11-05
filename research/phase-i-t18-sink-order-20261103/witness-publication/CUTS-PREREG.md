# Actual pre-reply revocation process cuts

Frozen after854b008, before gates/runner execution. Governing C12 in
Phase-I-Closure: successful ACK follows recoverable commitment; lost reply preserves
uncertainty about a definite local outcome. C11 concerns identity/provenance/project/
consumer evidence, not an invented requirement for management request identifiers.

Competing hypotheses: absent revoke response implies no revoke; or identical no-reply
caller observations can accompany uncommitted, locally committed, or locally plus
witness committed control changes. Cheapest discriminator: actual held HTTP revoke
request, exact retained gate evidence, SIGKILL/reap before local mutation, after local
append/fsync/state publication but before witness publish, and after validated witness
publish before reply. No fabricated ACK, source revision and gate/PID/time evidence.
Runtime recovery receives only same actual journal plus explicit mode, not gate/oracle.

Expected: all3 callers observe no success response. Before-local cut current journal
and live witness stay eligible; current-journal recovery and real current request
succeed. After-local cut current journal/recovery revoked but witness still eligible;
old token locally denied. After-witness cut both revoked, still no caller ACK, old token
denied. Second current-journal restart retains actual positive/negative effect evidence.
Each point has different definite local/remote outcome despite same caller no-reply.
Uninterrupted control returns200 after witness publication. No retry/distributed
atomicity/operation-identity semantics inferred. Do not auto-publish at recovery.

Retain actual journal lineage (no fixture restoration in these histories), gate file
point/PID/monotonic/source binding, request completion/error, raw witness transcript,
actual process kill/reap and fresh recovery. Bound <=2 owned children at once,
256MiB inherited, bounded HTTP/gate waits. Missing reply/gate/journal are INCOMPLETE,
not successful absence claims. Gate file is a test instrument, not durable authority
or a premise passed into recovery. Process termination is not physical power loss.
Next discriminator depends on result: explicit handling of a locally committed but
unpublished management action, or return to strongest remaining F1/C11 obligation.
