# Native launch preflight — implementation evidence

This record covers the frozen packet's native gateway, client, driver, and
identity-lifetime acceptance checks. Raw request/response and Store snapshots
are retained under [`evidence/`](evidence/).

## Observations

- The real gateway rejected missing program, non-executable regular program,
  missing cwd, and non-directory cwd before writing `LAUNCH_INTENT`. Each
  durable job remained `AUTHORIZED`; repairing the fixed profile path and
  retrying the same job and launch identity produced one intent and one start
  observation. Exact retry did not create a second intent. Per-case raw records:
  `native-gateway-preflight-*.json`.
- The actual `resource-session` client received a missing-program rejection,
  with the job still `AUTHORIZED` and its event history unchanged. After the
  executable was installed at the same trusted path, a fresh invocation of the
  same launch command succeeded. See
  `session-client-preflight-repair.json`.
- A copied `/bin/sleep` child was started and then its executable path was
  unlinked. Exact replay, poll, resume, stop, and finalize all succeeded through
  the still-owned `Child`; the event history contains one launch intent. See
  `native-gateway-unlinked-executable.json`.
- An executable script with an absolute interpreter path that does not exist
  passed metadata and `X_OK` preflight, then failed during spawn. The Store
  retained `LAUNCHING`, no started or not-created observation was written,
  replay reported unknown, capacity stayed reserved, and finalize was rejected.
  This is the post-intent loader-error discriminator in
  `native-gateway-post-intent-spawn-failure.json` and
  `session-client-history.json`.

These observations support the bounded preflight behavior on this Linux host.
The filesystem snapshot and spawn are not atomic: changes between the check and
spawn can still fail after intent. A returned error is evidence about that
request path, not global proof that no effect occurred. Host compromise,
power loss, universal confinement, loader failure classes beyond the absent
interpreter case, and other platforms were not tested.

## Commands and results

The focused native targets were run with the pinned offline toolchain and the
shared target directory:

```text
CARGO_HOME=/workspace/.toolchains/ases-launch-rust/cargo
RUSTUP_HOME=/workspace/.toolchains/ases-launch-rust/rustup
CARGO_TARGET_DIR=/workspace/ases-native-identity-lifetime/resource-control/target
CARGO_INCREMENTAL=0 CARGO_PROFILE_DEV_DEBUG=0 CARGO_PROFILE_TEST_DEBUG=0
cargo test --offline --locked --manifest-path resource-control/Cargo.toml \
  --test native_local_gateway --test native_session_client --test native_session_drive
```

Result: `native_local_gateway` 6 passed, `native_session_client` 4 passed,
`native_session_drive` 2 passed; no failures. The five #39 identity-lifetime
regression tests were run separately, without running the broader Store suite:

```text
cargo test --offline --locked --manifest-path resource-control/Cargo.toml \
  --lib identity_lifetime_tests
```

Result: 5 passed, 0 failed. They cover stale identity after reap, exact replay,
force stop, graceful stop, and resume behavior.

Cargo stdout/exit logs were not saved as files. The counts above are the
report-only test-process result recorded from the completed focused runs; the
retained JSON files contain the raw native requests, replies, and Store
observations, not Cargo console output. No tests were rerun to produce this
documentation note.

During test development an assertion compared the entire event snapshot after
replaying an immediately exiting `/bin/true`; the gateway can legitimately add
exit observation asynchronously. The assertion was narrowed to the relevant
one-intent/one-start invariant, and the focused targets then passed.

## Source hashes at evidence capture

SHA-256:

| Source | SHA-256 |
| --- | --- |
| `resource-control/src/local.rs` | `98bfbc35f37313b1f98b5b69487f06be2301f9ad4100f9c15ea3e8ed69a14ae6` |
| `resource-control/src/lib.rs` | `4eee660beb26d330ffe5f4f13c3ae941692f9197ca4a6f73788aafbe57583b23` |
| `resource-control/src/local/identity_lifetime_tests.rs` | `facb1075a5424b41eba2d45cca3dc125df0145314b74ff92e3b74cf1cdc3d92a` |
| `resource-control/tests/native_local_gateway.rs` | `b9021b635c846fe0124a8c84105c7eeb51565d4e5e209b2f03c9fe521977e382` |
| `resource-control/tests/native_session_client.rs` | `02a81a39db9721da3fa4af9d1fde299aad250d317bd7263686e37098ef962171` |
| `resource-control/tests/native_session_drive.rs` | `c1c378a25dacdb87c042edaa880686b0856f6efc1d3101e41ded082885259ec7` |

Raw JSON evidence includes source hashes per record and the actual requests,
responses, and durable event snapshots.
