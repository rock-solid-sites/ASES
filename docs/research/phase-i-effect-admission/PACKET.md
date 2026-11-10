# Commit-point effect admission — frozen bounded experiment

Research only, 2026-11-10. Parent: PR #11 `1970abe2f5d2016c8fb773474601e02d8f02c1d8`.
No frozen policy or original component is modified. This is a disposable Python
integration experiment reusing the pinned Python services, not a maintained runtime.
Rewriting their processes/storage would add untested boundaries without resolving
the missing native identity interface. Validate input at runtime and retain native
transaction, journal, publication and crash observations as compensating controls.

## Requirement and interpretation

Comparator: Phase-I-Closure §§2–5, §7 C1/C2/C3/C7/C8/C9/C10/C11/C12 and
Phase-I-Verification F4 at F1 pin `29ec3960c4c60dfb5d5f76d1c5dba7d2ea32d38a`.
Kernel-0 Abstract Semantics requires a coherent current view at commitment.
The protected effect is a new **use-current descendant D write**, whose local
irreversibility point is the inherited F4 journal append/fsync. Remote cut
publication and caller acknowledgement remain later, distinct observations.
This does not change F4's original flat contract or promise cancellation at remote
visibility. A separately authorized audit event is a different operation; this
port refuses it and does not reinterpret a denied D effect as an audit record.

## Smallest candidate and alternatives excluded

PR #10's detached adapter/same hash fails: native F4 publishes after native L5
denial. A preflight check alone also permits invalidation before append. A new
universal identity database or distributed transaction is not justified here.
Use an isolated subclass/hook at `emit_locked(effect_accepted)`, retaining real
F4 HTTP, flat authority, append/fsync, witness CAS, reply suppression and replay.
Acquire, in fixed order: F1 `BEGIN IMMEDIATE`, #11 L5 management-writer `flock`,
L6 `BEGIN IMMEDIATE`. Reread under these guards; hold them through local append
and fsync. No durable admission token or second authority store is added.

State representation is PRIMARY: proposal → guarded view → local commitment →
remote publication → known reply. Denial changes none of the journal bytes;
crash may retain a whole committed local effect without a reply/publication.

## Import, issuer, verifier and custody

The trusted test supervisor creates a fixed, local `experimental-import-v1`
configuration binding F1 store/root/profile, L5 C/object, L6 root/x and F4 C/p.
It records device/inode identity for roots, databases and L5 guard, plus an
explicit import epoch. The client cannot choose storage paths or invent aliases.
The request presents the exact accepted content and four opaque F1 observations,
the fixed import ID/epoch and expected L5 selector+record hash. These are
comparison inputs, never capabilities. Guarded current readback is the verifier.

The F1 pair must be selected and retained by #11's wrapper. The L5 selected
metadata must bind that exact pair and actual bytes; validate full graph, current
ingress, ancestor activation/sealing, grants and all latent ceilings. Expected
generation equality prevents an old selector being presented as current. L6
must be live, have a non-disposed accepted x matching actual bytes and catalog,
and have no unknown physical material. Fail closed on malformed/missing/changed
roots, wrong worlds with equal bytes, stale generation, denied path or disposed
inventory. Receipt binds the resulting exact journal, not truth of external facts.

**This issuer/import is test-only and untrusted as native ASES authority.** Native
F1→F3 acceptance does not issue a protected import binding; L6 has no native
owning-domain identity linking its x to L5's retained object. Configuration
authenticity, opaque observation truth, current storage and cooperative all-writer
participation are explicit premises. Same-UID unguarded L5 writers bypass flock.
Device/inode checks detect tested retargets, not hostile host/custody attacks.
No expiry policy is invented for immutable evidence; current mutable authority
is recomputed. Stable lock inode and the supervisor-owned root are part of TCB.

## Acceptance and live assumptions

Preserve original denied+published and allowed+published neighbors. Prototype:
allowed append/publication; attenuated denial with zero journal change; stale
preflight after native L5 move/activation; changed same-byte opaque evidence;
wrong subject/epoch/root; disposed/removed inventory; physical unknown debris;
failed F1 bundle. Demonstrate relevant writers cannot commit while guards are
held, and correct work resumes after release. Include actual kill before append,
after fsync before publication, cold recovery, and publication receipt loss.
Do not turn 503 into denial. Live guard bypass is a negative control, not a
passing native integration result. Preserve exact source pins and raw frames.

Finish this slice when these discriminators establish the bounded result or a
concrete blocker. Then continue the campaign queue; no independent review/CI,
main merge, production use or deployment is part of this packet.
