---
title: Bounded durable launch intent and unknown outcome
program: EDASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - PACKET.md
related_documents:
  - ../../research/phase-i-sol-integration/REPORT.md
  - ../../methodology/Agent Model Launch Routes.md
---

# Result

The opt-in `Store::begin_launch` path records `AUTHORIZED → LAUNCHING` and a
`LAUNCH_INTENT` event in one SQLite immediate transaction before returning a
typed `DispatchGranted` result. The result is non-cloneable and non-serializable;
only the first call for an authorized job and exact launch ID returns it. An
identical replay in `LAUNCHING` returns `PendingObservation`; a matching
intent-backed `RUNNING` replay returns `RunningObservation`. Conflicting launch
IDs reject. The existing atomic `launch_mock` behavior remains unchanged, and
mock `RUNNING` records cannot be mistaken for intent-backed launches.

The first transition checks the caller's expected catalog revision against the
reserved and current revisions, authorization expiry, current account state and
project grant, environment and meter identity/freshness, forecast coverage, and
whether new observed usage has overconsumed the reservation. Those checks occur
before durable intent. Pending and running replays are observations and do not
re-run current checks or grant another dispatch. This is the packet's
decision-authorized profile: later catalog or authority change does not infer
cancellation of an already committed launch decision. An adapter may therefore
execute after such a later change; no automatic cancellation is implemented.

`observe_launch` accepts typed `Started` or `DefinitelyNotCreated` evidence for
the exact recorded launch. A positive observation changes `LAUNCHING → RUNNING`;
a definite non-creation observation changes it to `CLOSED` with outcome
`failed`. The exact repeated event replays idempotently and a contradictory
observation conflicts. A trusted local adapter is an explicit precondition for
these observations; a typed value or local event does not independently prove
that the claimed process outcome is true.

# Native evidence

The source runtime is pinned to `1fd05d896dde11f185610a4718c1245cfad1ffca`.
Raw gate, process, event-log, job, balance and source-digest evidence is in
[evidence/final](evidence/final). The native process test kills the controller
with signal 9 after durable intent, then verifies a cold reopen returns pending
without dispatch. A second history starts the fixed worker test binary, records
its PID and Linux `/proc` start token, kills the controller while that worker is
still live, reopens to pending, verifies the worker marker has one row, and only
then records the trusted positive observation. A test-owned release file cleans
up the worker without signaling a PID. The pre-spawn history retains the
reservation, slot, and `LAUNCHING` state despite ordinary expiry and finalization
attempts.

The initial inherited-stdin worker gate failed to keep the worker live under the
test harness. That result is retained at
[initial-worker-gate-failure.json](evidence/attempts/initial-worker-gate-failure.json).
The bounded release-file gate replaced it and passed. Final source SHA-256
values are recorded beside both SQLite histories.

Rust was absent from `PATH`. One official rustup setup installed stable Rust
1.99.1 under `/workspace/.toolchains/ases-launch-rust`; no host package,
`HOME`, or security configuration was changed. No crate dependency was added.
The resource-control test suites passed separately: 47 control tests, 3 access
tests and 4 native launch tests. Their complete output is retained in the three
`*-test.log` files under `evidence/final`.

Exact validation commands:

```sh
CARGO_HOME=/workspace/.toolchains/ases-launch-rust/cargo RUSTUP_HOME=/workspace/.toolchains/ases-launch-rust/rustup /workspace/.toolchains/ases-launch-rust/cargo/bin/cargo check --manifest-path resource-control/Cargo.toml --tests
CARGO_HOME=/workspace/.toolchains/ases-launch-rust/cargo RUSTUP_HOME=/workspace/.toolchains/ases-launch-rust/rustup /workspace/.toolchains/ases-launch-rust/cargo/bin/cargo test --manifest-path resource-control/Cargo.toml --test control
CARGO_HOME=/workspace/.toolchains/ases-launch-rust/cargo RUSTUP_HOME=/workspace/.toolchains/ases-launch-rust/rustup /workspace/.toolchains/ases-launch-rust/cargo/bin/cargo test --manifest-path resource-control/Cargo.toml --test access
CARGO_HOME=/workspace/.toolchains/ases-launch-rust/cargo RUSTUP_HOME=/workspace/.toolchains/ases-launch-rust/rustup ASES_LAUNCH_EVIDENCE_DIR=/workspace/ases-launch/docs/research/phase-i-launch-intent/evidence/final /workspace/.toolchains/ases-launch-rust/cargo/bin/cargo test --manifest-path resource-control/Cargo.toml --test native_launch
```

# Boundaries

The grant authorizes the trusted adapter to perform its bounded dispatch
obligation. It does not bind a source binary, command, provider, or external
effect. The native discriminator uses only one fixed harmless local test
worker. This slice does not establish exactly-once process creation or
all-route custody: an unguarded adapter can ignore `PendingObservation` or
launch without using the grant. Generic job and launch IDs are not command
authority.

Process identity is retained as evidence only. The ledger never signals a PID,
adopts an unknown process, or uses a PID guess to permit redispatch. The trusted
adapter boundary and its observation truth remain assumptions. The test covers
local SQLite and Linux child-process gates; it does not cover an external
provider, model launch, production transport, process takeover, crashes inside
the operating system's spawn syscall, or multi-host custody.
