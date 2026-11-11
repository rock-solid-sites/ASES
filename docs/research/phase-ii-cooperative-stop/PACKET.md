# Cooperative stop inside the existing owned-child authority

ASES-4 priority D continuation, parent draft32 at0643b3a9. Existing local_stop
is explicitly force-kill. Add one bounded cooperative alternative through the
same actual client/gateway/Store/owned-Child path, preserving old stop semantics.
The goal is orderly local worker cleanup before forced termination, not a new
Kernel primitive or a canonical requirement to stop CPU at logical disposal.

## Interface and durable decision

New operation `local_stop_graceful` takes exactly job_id, launch_id, stop_id,
grace_ms (1..2000), plus op. Existing SO_PEERCRED administrator and exact trusted
profile scope checks apply. No caller PID, signal choice, executable, clock,
identity or observation. Existing local_stop request and behavior are unchanged.
Client adds `resource-session SOCKET stop-graceful JOB LAUNCH STOP_ID GRACE_MS`;
all transport uncertainty/no-retry rules remain unchanged. Driver never stops
a worker automatically and needs no change.

Reuse the exact existing `local-stop:{job}` / LOCAL_STOP_REQUESTED event owner.
Legacy payload `{launch_id,stop_id}` remains force-kill, byte-semantically
unchanged for replay. Graceful payload has exactly `{launch_id,stop_id,
mode:"term_then_kill",grace_ms}`. Strictly decode only these two supported
shapes, validate selectors/bounds and reject unknown material. Exact replay
requires same stop_id and same plan; changing mode/grace or mixing a legacy
stop with a graceful plan conflicts without another signal or event. No new
journal, table or authority registry. Resume returns the exact selected plan
and selector with its existing event hash, still within4KiB.

## Runtime authority and observations

Commit the stop request before any signal. Only the retained Child for that
exact job/launch may be signaled; never reconstruct from persisted PID. For
that still-owned, unreaped child only, send SIGTERM, poll actual Child.try_wait
until the monotonic grace interval, then if necessary Child.kill (SIGKILL) and
wait/reap. A known Child ID can be used for SIGTERM; arbitrary PID adoption is
forbidden. If already exited, record its actual wait result without a signal.

Retain in-memory progress for each owned stop (term/kill attempted and initial
monotonic deadline) so a same-process replay cannot send SIGTERM again or reset
the grace interval after an interrupted attempt. This progress is not durable
process ownership. On gateway loss no Child/progress survives; cold replay is
unknown and cannot signal or fabricate exit. Stop intent is not completion.
Use existing exact observe_launch_exit and require separate explicit finalize;
capacity stays held until finalization. A lost reply remains uncertain.

This is a bounded grace interval, not a hard wall-clock termination guarantee:
wait/reap after SIGKILL and filesystem operations retain the same local kernel
premises as the original adapter. No process-group or descendant stop claim.

## Native histories

Use actual new client action -> gateway -> fixed owned worker: cooperative
SIGTERM handling produces retained cleanup marker then known exit code; an
ignoring worker escalates after the selected grace and yields actual signal9;
capacity is held before explicit finalize in both cases. Verify exact replay
and conflicting mode/grace cannot repeat signal or create a second stop event;
resume supplies the exact plan; legacy force-kill tests still pass. A gateway
loss during the worker's bounded cooperative delay yields cold unknown/no
adoption/no release. Test actual viewer peer refusal and caller-selected PID
or unknown fields without mutation. Use an async-signal-safe test handler
(atomic flag only, filesystem cleanup in normal worker code), fixed self-timeout
and retained test Child/release-file cleanup rather than arbitrary PID cleanup.
Preserve raw requests/replies/events/worker markers/wait status/commands.

WHY: integrate orderly cancellation without weakening existing custody or exit
requirements. WHAT: same native runtime and transactional stop owner. HOW
CERTAIN: experimental until actual histories pass. WHAT NOT TESTED: hostile
same-UID/root, remote providers, whole-host loss, arbitrary programs, descendants,
hard wall-time stop, or changes to canonical Work Unit/F3 disposal semantics.
