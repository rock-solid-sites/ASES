# Atomic unlaunched cancellation — native evidence

The pre-implementation route discriminator is recorded in
[`BASELINE.md`](BASELINE.md) with its original source snapshot. Final test
histories and their source/binary hashes are under
[`evidence/pass2/`](evidence/pass2/).

## Observations

- The baseline showed a real missing-program preflight rejection leaves the
  job `AUTHORIZED`, writes no launch intent, and retains the reservation. The
  previous `local_finalize` request with an arbitrary launch selector refused
  without changing events or balances.
- After the new route, the actual `resource-session cancel-unlaunched JOB`
  command closed that same authorized job as `cancelled`, with no launch intent
  or worker and with reserved capacity released. An exact replay returned
  `CLOSED_REPLAY`; later launch was refused without changing the event log.
- `RESERVED` jobs cancel and replay successfully. Live launched, exited-but-not-
  finalized, already-closed launched, and `EXPIRED` jobs refused the new route
  with their events, state, and balances unchanged.
- Wrong role, mismatched trusted profile scope, extra request fields, invalid
  ID, and unknown job ID were rejected without mutation.
- The lost-reply test forwarded one real client request to the gateway, let the
  gateway commit cancellation, then dropped its reply. The client returned
  `outcome_unknown` (exit 4). The Store showed `CLOSED/cancelled`, no launch
  intent, one finalization, and released capacity. A fresh exact client command
  returned `CLOSED_REPLAY` without a new event. The client made no automatic
  retry, and a later launch was refused. This history does not treat a lost
  response as proof of no effect.
- Separate gateway processes produced deterministic cancel-first and
  launch-first histories. In the actual concurrent race, the launch reply
  succeeded and cancellation was refused; one worker and one observed launch
  were present, and capacity stayed reserved until bounded stop/finalize
  cleanup. The saved history labels only the observed replies and durable
  effects, not an unobserved scheduler ordering.

Raw requests, replies, events, balances, worker markers, and test/source/binary
hashes are in each per-case JSON file in `evidence/pass2/`. Scope limits match
the packet: this does not test compromised host/database, power loss, external
dispatch bypassing Store, unknown future lifecycle kinds, arbitrary providers,
or termination of already launched work.

## Cargo runs

The baseline-only command passed one exact test on the old route; see
[`BASELINE.md`](BASELINE.md). The implementation regression run used:

```text
set -o pipefail
CARGO_HOME=/workspace/.toolchains/ases-launch-rust/cargo
RUSTUP_HOME=/workspace/.toolchains/ases-launch-rust/rustup
CARGO_TARGET_DIR=/workspace/ases-native-identity-lifetime/resource-control/target
CARGO_INCREMENTAL=0 CARGO_PROFILE_DEV_DEBUG=0 CARGO_PROFILE_TEST_DEBUG=0
ASES_UNLAUNCHED_CANCEL_EVIDENCE_DIR=/workspace/ases-native-unlaunched-cancel/docs/research/phase-ii-native-unlaunched-cancel/evidence/pass2
/workspace/.toolchains/ases-launch-rust/cargo/bin/cargo test --offline --locked \
  --manifest-path resource-control/Cargo.toml \
  --test native_unlaunched_cancel --test control --test native_termination \
  --test native_local_gateway --test native_session_client --test native_session_drive \
  --test native_local_cancellation
```

The first full attempt is preserved at
[`cargo-native-regressions-pass1.txt`](evidence/cargo-native-regressions-pass1.txt)
with exit code 101. Seven new native cases and the other selected targets
passed; the concurrent launch case sampled the worker marker immediately after
the launch response, before the child had written it. The test was corrected to
wait for that bounded marker before asserting worker count. No implementation
change was made for this timing observation.

The final command output and numeric exit code are preserved verbatim at
[`cargo-native-regressions-pass2.txt`](evidence/cargo-native-regressions-pass2.txt)
(`CARGO_EXIT_CODE=0`). Results: native cancellation 8/8, control 48/48,
termination 8/8, existing cancellation 2/2, gateway 6/6, session client 4/4,
and session drive 2/2; 78 tests passed, 0 failed.

## Source and binary hashes at final run

SHA-256:

| File | SHA-256 |
| --- | --- |
| `resource-control/src/main.rs` | `f92f0bfa773a0088dac95d229a5a2cb0790d58170131a22c35d160495b87213b` |
| `resource-control/src/lib.rs` | `03dec127c00f14112318b86ce25aa7fa3a330aa7367d1f777ea32aa068ddcd5b` |
| `resource-control/src/local.rs` | `98bfbc35f37313b1f98b5b69487f06be2301f9ad4100f9c15ea3e8ed69a14ae6` |
| `resource-control/src/bin/resource-gateway.rs` | `e80d45e29a6f7dbeb3a7317c77e480b3ba1e235ea5a66fa2851d858e68ae5c18` |
| `resource-control/src/bin/resource-session.rs` | `1d92bf136a053c807aeda499d632a4b1adb6239c6f02d085c3ad3db8353b331e` |
| `resource-control/tests/native_unlaunched_cancel.rs` | `40dddea16340df50bb37b80395e87c42d6f595dd5eb6f4ecfd8cebe8731412d0` |

The `lost-cancel-reply-history.json` record includes SHA-256 hashes for the
compiled gateway, client, controller, and integration-test executable.
