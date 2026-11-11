# Fresh-session client transport fault evidence

## Observed behavior

The `resource-session` client sends one literal effect request over one Unix
connection and never retries it automatically. When the fixture accepted a
`local_launch` request and closed without a reply, the client returned exit 4
with `outcome_unknown`; the fixture captured exactly one accepted connection
and the complete raw request. The client did not infer that the launch had no
effect. The server-error fixture returned its received `{ "ok": false,
"error": "..." }` unchanged with exit 3, distinct from transport uncertainty.

An incomplete JSON reply, unsupported `{ "ok": true }` or non-string error
shape, and a 9 KiB reply all produced `outcome_unknown`; the oversized bytes
were not copied to stdout. Invalid selectors, a negative revision, and extra
command/PID arguments produced `invalid_input` with exit 2 and zero accepted
connections. A one-byte response trickle every 600 ms ended at the total
response deadline: the client returned after 3005 ms, the server observed a
broken pipe while writing, and exactly one connection/request was captured.
This discriminates the complete response deadline from a rolling per-read
timeout.

## Evidence and command

The focused transport target passed **7/7 tests**. Raw requests, client
stdout/stderr and status, fixture reply bytes, connection counts and the slow
trickle's broken-pipe observation are retained in
[`evidence/client-transport`](evidence/client-transport). Each JSON record
includes source SHA-256 values for the client, test and packet.

From `resource-control/`, the exact command was:

```text
ASES_SESSION_TRANSPORT_EVIDENCE_DIR=/workspace/ases-local-execution/docs/research/phase-ii-local-execution/evidence/client-transport CARGO_HOME=/workspace/.toolchains/ases-launch-rust/cargo RUSTUP_HOME=/workspace/.toolchains/ases-launch-rust/rustup CARGO_INCREMENTAL=0 CARGO_PROFILE_DEV_DEBUG=0 CARGO_PROFILE_TEST_DEBUG=0 /workspace/.toolchains/ases-launch-rust/cargo/bin/cargo test --locked --offline --test session_client_transport -- --nocapture > /workspace/ases-local-execution/docs/research/phase-ii-local-execution/evidence/client-transport/test.log 2>&1
```

**WHY:** A lost reply after an effect request cannot prove absence of effect;
the client must expose uncertainty and avoid a duplicate request. **WHAT:**
This test uses the actual compiled `resource-session` binary and bounded local
AF_UNIX fault servers that capture every request and return, truncate, drop,
oversize, or slowly trickle replies. **HOW CERTAIN:** Experimental for the
captured Linux binary and these transport histories; all seven focused tests
passed. **WHAT NOT TESTED:** These synthetic servers do not use the resource
Store, gateway policy, native supervisor or worker. They cannot establish
whether any launch actually occurred, prove real gateway role denial, or
replace the separate actual-gateway histories in [CLIENT.md](CLIENT.md). They
also do not test a remote provider or behavior on other operating systems.
