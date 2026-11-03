# T18 sink-side currentness discriminator — results

Run date: 2026-11-03 UTC. Source worktree began at `8b3c7e06aaab97122d2fcdaf2ee891e62667154b`; the preregistered hypothesis is commit `a4f1c493d943f4e06d0a8ed5f097ecb9c9265ed2`.

## Observation

The bounded loopback experiment passed all nine preregistered assertions. The sink-ordered run recorded this event order:

1. Current request `live-v1` accepted at authority version 1.
2. Exact obligation `q-1` committed at version 1.
3. Delayed request `stale-v1` arrived and paused.
4. Replacement advanced authority 1 → 2 and acknowledged.
5. Sink-side check rejected the delayed version-1 request; its payload was absent from the accepted-effect log.
6. Current request `live-v2` accepted at version 2.
7. The exact payload in `q-1` was delivered and accepted at version 2.

In the detached-check mutation, version 1 was read and accepted before the pause. Replacement then advanced to version 2. When the request resumed, the sink accepted `x-stale-mutant` with presented version 1 under current version 2. This is the expected failing control for a permission read detached from the sink acceptance event.

The per-scenario raw event sequence, accepted-effect set, append journal, platform values, and individual assertions are in `results.json`. The runner returned exit code 0; exact command and stdout are retained in `run.exit-code.txt` and `run.stdout.txt`.

## Interpretation and correspondence

This supplies one concrete, bounded sink-side ordering witness for the previously prepared-only `T18-use-current-sink-order-after-revocation` fixture. It shows the expected distinction between a delayed uncommitted use-current request, which is denied after replacement, and an already committed exact obligation, which this profile allows to complete later. The detached-check mutation demonstrates fault sensitivity for the intended stale-order defect.

The authority check and sink effect append share one lock in the sink subprocess. The append-only effect, obligation, and replacement journal is flushed and `fsync`ed before the corresponding successful reply. This gives an explicit local event boundary for this probe. The mutation intentionally checks before waiting and accepts after replacement. The experiment concerns those two implementations and schedules only; it does not show that another service provides the same serialization or durability.

**WHY:** current authority must be ordered at the selected sink acceptance event for the use-current profile; permission observed earlier can go stale. A committed exact obligation follows its separately selected decision-time policy. **WHAT:** the pinned abstract T18 controls, the separate loopback sink process, and the complete recorded event order. **HOW CERTAIN:** bounded, executed local witness with positive and destructive controls. **WHAT-NOT-TESTED:** repository F3 code conformance, Linux access-control confinement, process termination at the event boundary, power-loss durability, rollback resistance, remote authentication, multi-sink ordering, and arbitrary sink correctness.

This is not host-confinement evidence. The TCP server listens only on `127.0.0.1` at an ephemeral port; all data is disposable. No Landlock, seccomp, SELinux, production sink, credentials, or external network was used.

## Reproduction

From repository root, on the pinned branch:

```sh
python3 research/phase-i-t18-sink-order-20261103/run.py --output research/phase-i-t18-sink-order-20261103/results.json > research/phase-i-t18-sink-order-20261103/run.stdout.txt 2>&1
```

Observed exit code: `0`. The script launches and terminates its own local sink subprocesses and creates a temporary journal directory per scenario.

## Next discriminator

Exercise the same paused-request schedule against a pinned candidate implementation or real selected sink, using its actual authority replacement and acceptance boundary. Retain both positive paths and the detached-check control. Until that exists, no claim follows about F3, operating-system enforcement, production services, or arbitrary use-current attachments.
