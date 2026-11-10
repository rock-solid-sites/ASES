# Observed termination before releasing an intent-backed execution

Frozen 2026-11-10. Parent source: resume-view draft PR #25,
`9fb8a525c32b56b9191d3f33df9925939636dc9a`, retaining launch-intent PR #20.
Grounding: campaign P5 observer evidence, bounded launches, stop-button semantics;
Engine Vision explicit recoverable state; AGENTS rule that a recorded RUNNING
flag is not liveness. This is a narrow continuation of the existing Rust runtime,
not a new scheduler, termination service or Kernel policy.

## Gap and cheapest discriminator

Current `observe_launch(Started)` sets RUNNING. Generic `finalize(cancelled)` or
`finalize(completed)` can then close this intent-backed job and release its slot
and reservation while the actual fixed child is still alive. There is no
termination observation interface. First demonstrate this with a fixed owned
child and its actual Child handle, live process/start evidence, store state and
capacity before/after; retain the pre-change comparator. Mock behavior is its
separate existing profile and remains unchanged.

## Smallest repair

Add a typed trusted-adapter exit observation for an exact job, launch ID and
previously recorded Started process identity. Retain normal exit code versus
signal distinctly using bounded platform-valid values. Record one deterministic
LAUNCH_EXIT_OBSERVED event in an immediate SQLite transaction. Identical replays
are observations even after finalization; conflicting launch/process/status
observations reject without changing history. It cannot stand in for a pending
launch's unknown creation result or for DefinitelyNotCreated.

The store cannot establish observation truth from a typed value. Trusted adapter
truth and store custody remain explicit premises, exactly as with Started.
Only the native test adapter's actual Child wait/reap supplies test evidence.
Do not inspect/signal arbitrary PIDs, adopt unknown processes, infer exit from
absence, or introduce an arbitrary command interface.

For intent-backed RUNNING, finalization requires matching Started plus matching
exit evidence. A mere cancellation request or terminal outcome label does not
release resources. Observing exit itself leaves RUNNING/reservations held until
the separate existing finalization operation commits; finalization then permits
the existing outcome labels. Unknown/unsupported profile evidence refuses.
LAUNCHING still refuses finalization. DefinitelyNotCreated retains its existing
failed-closed behavior. Existing mock/unlaunched profiles keep their semantics.

Extend the existing compact resume interpretation to validate exit evidence,
select the exit pointer as RUNNING outcome evidence when available and give
FinalizeObservedExit advice only then. Do not add an unbounded history or more
than the existing two compact pointers. Keep the serialized view under 2 KiB,
Serialize-only and read-only. Intent-backed CLOSED after actual start must have
exit evidence; older experimental CLOSED rows without it refuse interpretation
rather than claim a newly established fact. Present liveness remains unknown;
retained observations never become a current dispatch or signaling grant.

## Deciding tests

1. Pre-change native live-worker finalization releases capacity; repaired version
   rejects all terminal labels while child is live, leaves events/reservations
   unchanged, and prevents another job from obtaining that occupied slot.
2. Actual fixed child release and Child wait/reap produce exact exit evidence;
   observe leaves capacity held, cold reopen retains evidence, finalization
   releases it and a valid next launch can progress. Include actual nonzero
   exit or signal with exact owned child handle and status.
3. Wrong launch, wrong PID/start token, conflicting status, pending/no-start and
   mock observations reject. Exact repeated exit and finalization replay without
   duplicate events. No dispatch can arise from any observation or view.
4. Actual controller kill after wait but before recording the exit leaves no
   durable exit evidence: cold finalization refuses until trusted observation
   is explicitly supplied. Do not infer absence proves an exit.
5. Resume view stays pure and bounded, retains correct pointers/advice, refuses
   missing/conflicting exit histories, and makes no present-liveness assertion.

Use existing toolchain, dependencies and locked offline build. Preserve source
hashes, raw process/status/SQLite observations, failed instrument attempts and
exact verification commands. Run affected control/native/resume suites once
after integration. No paid/provider/model workload, daemon, generic stop API,
canonical policy edits, CI, independent review, merge or deployment.
