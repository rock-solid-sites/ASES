# Cooperative stop native histories

**WHY:** Cooperative stop adds orderly child cleanup while retaining the
gateway's existing ownership, exact stop-plan replay, and explicit-finalize
requirements. The native histories exercise those boundaries with actual
fixed workers and the real local gateway/client path.

**WHAT:** `native_cooperative_stop` covers three histories. A worker handles
SIGTERM, records cleanup, and exits normally; the gateway observes that exact
exit while capacity remains reserved until explicit finalization. A worker
that ignores SIGTERM is escalated after the configured grace and is observed
exiting from signal 9; capacity likewise remains reserved through explicit
finalization. In a third history, the gateway is killed after TERM while a
worker is in bounded cleanup. The client reports an unknown outcome, and a
cold gateway can replay the durable plan but reports unknown liveness without
inventing in-memory TERM/KILL attempt state, signaling or adopting the child,
adding events, or releasing capacity. The worker completes its own cleanup
and exits on its bounded path. The test also checks exact-plan replay,
conflicting grace/mode rejection, resume evidence, viewer-policy denial, and
rejection of forged PID/unknown request fields without event changes.

**HOW CERTAIN:** The fixed helper runs through `resource-session` and the real
Unix gateway. Captures retain actual requests and replies, event snapshots,
worker PID/start token and marker timestamps, exit status, and balances. The
initial focused run passed 1/1 at `aab258485b282c3b665e53623fe808dba048ea08`
and is retained at [`evidence/native`](evidence/native). After a narrow fix
changed graceful exit recording to timestamp the actual wait observation, the
same focused test passed 1/1 again at
`50e2e06baad13efd2c4c585517a47d89ddb3ac28`; that capture is separate at
[`evidence/native-after-wait-fix`](evidence/native-after-wait-fix). The focused
command, result, source hashes, and evidence hash are in each directory's
manifest. Separately, five named legacy native targets passed 14/14 at the
initial cooperative source commit; details are in
[`REGRESSION.md`](REGRESSION.md).

**WHAT NOT TESTED:** This is not independent CI or a full-suite run. It does
not test hostile same-UID/root callers, remote providers, whole-host loss,
arbitrary programs, descendant termination, hard wall-time stopping, or
canonical disposal semantics. The cold worker is a controlled fixture and
does not establish behavior for arbitrary processes after host failure.
