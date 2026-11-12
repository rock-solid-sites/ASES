# Native cancellation driver evidence

The final scoped run used the existing shared target directory and offline locked dependencies. Exact command:

```sh
cargo test --offline --locked --manifest-path /workspace/ases-native-cancel-drive/resource-control/Cargo.toml --test native_cancel_drive --test native_session_drive --test native_cooperative_stop -- --nocapture
```

Tool environment: `CARGO_HOME=/workspace/.toolchains/ases-launch-rust/cargo`, `RUSTUP_HOME=/workspace/.toolchains/ases-launch-rust/rustup`, `CARGO_TARGET_DIR=/workspace/ases-native-identity-lifetime/resource-control/target`, `CARGO_INCREMENTAL=0`, and dev/test debug info disabled.

Final Cargo exit code: **0**. Results: cancellation driver 2/2, existing cooperative stop 2/2, existing session drive 2/2. Raw command output and exit code are in `cargo-native-final.log` and `cargo-native-final.exit`.

The native histories were then emitted by the already-built `native_cancel_drive` test binary with `ASES_CANCEL_DRIVE_EVIDENCE_DIR` set to this directory. That run exited **0**; its raw output is in `native-evidence-run.log` and `native-evidence-run.exit`. `native-cancel-drive.json` contains the exact captured requests/replies, Store events, balances, worker markers, and source hashes.

The first Cargo test attempt exited **101** because the new fixture omitted the existing `Environment.provider` field. Its raw output is retained in `cargo-native-attempt1.log` and `cargo-native-attempt1.exit`. The corresponding intermediate source snapshot SHA-256 is `44e4f543d45f5593bad9f792a77583af2cf8b353e6c3f4ae7e5c9df5c34baa33`; the snapshot is preserved as `native_cancel_drive-attempt1.rs`.

Two later cancellation-history runs also failed on test-fixture assertions before the final passing run. One expected the proxy's literal mutation to be `failed`, while the helper generated `mutated-outcome`. Another expected a cold stop to leave events unchanged and then did not release the orphan worker through the fixture's cleanup file. The corrected assertions account for the durable `LOCAL_STOP_REQUESTED` selector and explicitly release the bounded worker. Their raw Cargo logs were overwritten by subsequent runs and were not retained; these summaries come from the observed tool output, not reconstructed logs. An earlier shell invocation also failed before Cargo started because the toolchain `bin` directory was missing from `PATH`; it was not a test attempt.

Final test source SHA-256: `9c066e85d74dfbe0ee0359cece2faa2db6ac4bbf8822de5470d01e8a96a5da99`. This matches the `tests/native_cancel_drive.rs` hash in the native history JSON.
