# Pre-implementation cancellation route baseline

This is the required baseline discriminator, run on the pinned #42 packet
commit `8f20e32a8423f4be52c3f7bd37be15d4f1717b1d` before the new operation
implementation was applied.

## Observation

The real native gateway first rejected a fixed trusted profile whose program
path was missing. The job remained `AUTHORIZED`; its event history contained
only `RESERVED` and `AUTHORIZED`, capacity remained reserved at 50, and the
fixed worker marker was absent. The old native `local_finalize` route, given an
arbitrary launch selector and `cancelled`, returned
`conflict: local operation launch selector does not match stored job`. The
second request left the event history and capacity unchanged. The raw request,
reply, Store event snapshots, capacity snapshot, and source/binary hashes are
in [`evidence/preflight-old-local-finalize-gap.json`](evidence/preflight-old-local-finalize-gap.json).

## Cargo capture

The exact focused command was:

```text
set -o pipefail
CARGO_HOME=/workspace/.toolchains/ases-launch-rust/cargo
RUSTUP_HOME=/workspace/.toolchains/ases-launch-rust/rustup
CARGO_TARGET_DIR=/workspace/ases-native-identity-lifetime/resource-control/target
CARGO_INCREMENTAL=0 CARGO_PROFILE_DEV_DEBUG=0 CARGO_PROFILE_TEST_DEBUG=0
ASES_UNLAUNCHED_CANCEL_EVIDENCE_DIR=/workspace/ases-native-unlaunched-cancel/docs/research/phase-ii-native-unlaunched-cancel/evidence
/workspace/.toolchains/ases-launch-rust/cargo/bin/cargo test --offline --locked \
  --manifest-path resource-control/Cargo.toml --test native_unlaunched_cancel \
  -- --exact preflight_then_old_local_finalize_is_refused_without_mutation --nocapture
```

The Cargo console output is retained verbatim at
[`evidence/baseline-cargo-preflight-old-finalize.txt`](evidence/baseline-cargo-preflight-old-finalize.txt):
the exact test passed (`1 passed`, `0 failed`, `7 filtered out`). The shell exit
code was not separately captured in the log; no test was rerun to reconstruct
it. The native JSON record is the full observed request/reply and Store evidence.

## Source hashes

The native evidence record captures these source hashes for the baseline:

| File | SHA-256 |
| --- | --- |
| `resource-control/src/main.rs` | `f92f0bfa773a0088dac95d229a5a2cb0790d58170131a22c35d160495b87213b` |
| `resource-control/src/lib.rs` | `4eee660beb26d330ffe5f4f13c3ae941692f9197ca4a6f73788aafbe57583b23` |
| `resource-control/src/local.rs` | `98bfbc35f37313b1f98b5b69487f06be2301f9ad4100f9c15ea3e8ed69a14ae6` |
| `resource-control/src/bin/resource-gateway.rs` | `b09e573c06e95be0584884f2e1f70b5362a5e80b7c3fd104199ccc7c5c560b09` |
| `resource-control/tests/native_unlaunched_cancel.rs` | `4e5d7683c1b0ed936ff7c634c81e83fae3f39f557f7c548e6856313aa0f82930` |

The same JSON record contains hashes for the three built runtime binaries and
the integration-test executable.
