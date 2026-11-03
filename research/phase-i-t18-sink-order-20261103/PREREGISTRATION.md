# T18 sink-side currentness discriminator (preregistered)

Date: 2026-11-03

## Pinned comparison

- F2 fixture source: commit `8b3c7e06aaab97122d2fcdaf2ee891e62667154b`
- Abstract prepared-only fixture: `docs/architecture/core-substrate/fixtures-f2/fixtures.json`, id `T18-use-current-sink-order-after-revocation`
- Abstract exact-obligation positive control: same file, id `T18-exact-obligation-delivery-after-replacement`
- Governing constraint: `docs/architecture/core-substrate/Phase-I-Verification.md` §3 T18 and §4 F4; `Phase-I-Closure.md` §4 external-effect contracts

The abstract use-current fixture is intentionally prepared-only because `f2lib` has no sink-side ordering event. This experiment tests only a disposable loopback sink, not the F2 oracle, F3 implementation, a privileged host policy, or a production service.

## Hypothesis

H1: If revocation/replacement and sink acceptance are serialized at one concrete sink boundary, a request held after arrival with old authority is denied when delivered after replacement. A fresh request under the new authority is accepted. A separately committed exact obligation remains deliverable after replacement under its selected decision-authorized profile.

H0 / destructive control: A sink that validates current authority before a delay, then accepts later without rechecking, will accept the old request after replacement. That failure demonstrates why a detached permission read does not establish sink-current ordering.

## Bounded procedure

Use a local HTTP server in a child process bound to `127.0.0.1` on an ephemeral port. Its only effect is an append-only JSONL entry in a newly created temporary directory; each accepted entry is flushed with `fsync`. No credentials, external network, privileged API, paid resource, or persistent user data is involved.

Run four observations against isolated server state:

1. Current request at authority version 1 accepts.
2. An old-version request pauses after reaching the sink; replace version 1 with version 2; release it. Sink-side atomic check-and-accept rejects it and records no effect.
3. Repeat the delayed old-version request against the detached-check mutation. It must accept after replacement, proving the control is sensitive to the intended ordering fault.
4. Commit an exact payload under version 1, replace the producer/version, then deliver only that committed obligation. It must accept the committed payload after replacement; this is the T18 profile distinction, not use-current authorization.

Acceptance criteria are the exact event order and effect count above. A mismatch fails the experiment; a timeout or server failure is inconclusive and must be recorded as such. The run does not establish host confinement, process-death behavior, machine/power-loss durability, rollback resistance, authentication of remote senders, or arbitrary sink correctness.

## Observation lock

No experiment code or output was present when this preregistration was committed. Record every command and raw result after running; do not edit this hypothesis to fit observations.
