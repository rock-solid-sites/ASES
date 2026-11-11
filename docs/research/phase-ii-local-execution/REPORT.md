# Native local gateway evidence report

## Finding

The optional local profile connects the existing lifecycle Store to an actual
Unix gateway and one trusted native child. In the captured histories, launch
replay did not create a second child; requests containing caller-supplied
command, PID, identity or environment fields were rejected; a peer with the
actual Unix-socket UID but viewer policy was denied; and a mismatched trusted
profile could not resume, stop or finalize a live job. A wrong launch selector
and a conflicting stop ID left the stop event history and capacity unchanged.

The valid stop history recorded one launch-bound `LOCAL_STOP_REQUESTED`,
waited on the gateway-owned child, and recorded its exact PID/start token and
signal-9 exit observation. The job remained RUNNING and its reservation stayed
held until a separate explicit `local_finalize`; only then did the job close
and capacity become available. A fixed absolute profile program that could not
be spawned left exactly one launch intent in LAUNCHING, with no started or
not-created observation. Replay returned unknown without another child, and
finalization remained blocked. These histories exercise the gateway socket,
SO_PEERCRED policy, resource Store and real child process together.

## Evidence and validation

The final native gateway run passed **4/4 test entries**: three active gateway
histories plus the fixed worker helper entry point. The parent regression run
passed **68/68 tests** across control (48), resume view (5), termination (3),
native launch (4) and native termination (8). The focused and regression logs
and JSON observations are retained under
[`evidence/native-gateway-final`](evidence/native-gateway-final). JSON records
include exact requests and responses, worker marker data, event snapshots,
capacity balances and source SHA-256 values. The gateway-loss and cold-resume
histories are recorded separately in [COLD.md](COLD.md) and
[`evidence/cold`](evidence/cold).

The commands ran from `resource-control/` with the configured toolchain/cache,
offline locked dependency resolution, disabled incremental compilation and
debug info. Their stdout and stderr are retained in the evidence directory:

```text
ASES_LOCAL_GATEWAY_EVIDENCE_DIR=/workspace/ases-local-execution/docs/research/phase-ii-local-execution/evidence/native-gateway-final CARGO_HOME=/workspace/.toolchains/ases-launch-rust/cargo RUSTUP_HOME=/workspace/.toolchains/ases-launch-rust/rustup CARGO_INCREMENTAL=0 CARGO_PROFILE_DEV_DEBUG=0 CARGO_PROFILE_TEST_DEBUG=0 /workspace/.toolchains/ases-launch-rust/cargo/bin/cargo test --locked --offline --test native_local_gateway -- --nocapture > /workspace/ases-local-execution/docs/research/phase-ii-local-execution/evidence/native-gateway-final/test.log 2>&1
CARGO_HOME=/workspace/.toolchains/ases-launch-rust/cargo RUSTUP_HOME=/workspace/.toolchains/ases-launch-rust/rustup CARGO_INCREMENTAL=0 CARGO_PROFILE_DEV_DEBUG=0 CARGO_PROFILE_TEST_DEBUG=0 /workspace/.toolchains/ases-launch-rust/cargo/bin/cargo test --locked --offline --test control --test resume_view --test termination --test native_launch --test native_termination -- --nocapture > /workspace/ases-local-execution/docs/research/phase-ii-local-execution/evidence/native-gateway-final/parent-regressions.log 2>&1
```

**WHY:** The existing lifecycle APIs had native process and exit evidence
coverage, but did not establish that the real peer-authenticated gateway uses
those APIs without accepting caller process authority or releasing a live
reservation. **WHAT:** These tests use the actual gateway binary and Unix
socket, current process UID credentials, the parent SQLite Store, a fixed test
binary as the trusted worker, and raw event/balance snapshots. **HOW CERTAIN:**
Evidence-based for the captured Linux build and tested histories; the focused
and regression suites passed. **WHAT NOT TESTED:** This does not prove profile
file ownership or immutability, containment of hostile same-UID code, arbitrary
workload isolation, behavior on other operating systems, remote-provider
cancellation or accounting, hard wall-clock termination, or whole-machine
power-loss behavior. The process and profile owner remain trusted premises.

The captured build emitted two unused-import warnings in `src/local.rs`; they
did not affect these passing tests. After capture, the adapter removed only
those unused imports. The captured `src/local.rs` SHA-256 is
`0a9655d11bf90f6fcd9bbc157e5a9128d3fb399033756fae4f095ef9bafe1833`; the
current file is `4b57ef5d40cefe97ebaa88b44398d5190fa163438f3d50677e1b83e4e0b9006e`.
That import-only cleanup was not retested in this task. No independent review,
CI run, merge or deployment was performed here.
