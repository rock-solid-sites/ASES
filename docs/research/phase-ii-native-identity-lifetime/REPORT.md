# Native identity lifetime fault histories

## Scope

This bounded test checks whether a `LocalSupervisor` can turn a later process
identity lookup into exact start and exit evidence after its actual owned
`Child` has exited and been reaped. It uses the real catalog, reservation,
acknowledgement, launch-intent, supervisor launch, and SQLite event store. The
only launched executable is fixed `/bin/true`.

The test-only, per-supervisor identity reader first fails, then offers a
synthetic stale token after the test observes an actual `Child::try_wait` reap.
That token is injected metadata. It is not an OS identity read, an actual
second process, or evidence that numeric PID reuse occurred.

## Pre-fix observation

Against seam-only source commit `36acdf8f6f280e40c86d3dad94a99c372e8b7558`,
all five fault histories failed their durable-behavior assertions. The actual
`/bin/true` child exited with code 0. When the test reader then returned the
synthetic stale token, poll, exact launch replay, force stop, and graceful stop
returned `exit_observed`; the Store recorded `LAUNCH_STARTED_OBSERVED` and
`LAUNCH_EXIT_OBSERVED`, and moved the job from `LAUNCHING` to `RUNNING`. The
resume history also reported `exit_observed` from the cached wait result before
the stale token was offered, although no identity had been captured.

Raw output, exact command metadata, and the seam-only source patch are under
[`evidence/pre-fix/`](evidence/pre-fix/). The output shows `0 passed; 5 failed`
and includes the durable event kinds, job state, and resume projection in each
failure diagnostic.

## Post-fix verification

The post-fix source is pinned to commit `e1148e883102b880125380e55f08dd22ad63ea58`.
The five focused fault histories passed (5 passed, 0 failed). They assert
unknown outcomes; absence of start and exit evidence events; retained
`LAUNCHING` state and reservation; refusal to finalize; no dispatch grant on
replay; no second owned child; and resume that does not call an unidentified
cached wait an observed exit. The force and graceful stop histories use fresh
fixtures because their durable stop plans are mutually exclusive.

The requested existing targets passed once each in a single Cargo invocation:
`native_local_gateway` passed 4 tests and `native_cooperative_stop` passed 2
tests. Full output and SHA-256 pins are in
[`evidence/post-fix/meta.json`](evidence/post-fix/meta.json).

## Evidence limits

WHY: a process identity refresh after reap is no longer tied to that owned
child's unreaped lifetime.

WHAT: the test observes real wait/reap status and Store effects, then injects a
synthetic identity through a private test-only reader.

HOW CERTAIN: the pre-fix source behavior is reproduced by five failing tests;
fixed behavior is evidence-based only after the recorded post-fix runs pass.

WHAT NOT TESTED: actual PID reuse; real `/proc` staleness or tampering; hostile
same-UID/root behavior; host loss; remote providers; process adoption; automatic
repair of unknown identity; or any claim that the injected token described a
second process.
