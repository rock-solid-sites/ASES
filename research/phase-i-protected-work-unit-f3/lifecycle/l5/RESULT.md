# L5 ? mediated latent-write move witness

**Verdict: PASS for this narrow host profile.** This is an L5 discriminator, not F3/F5 completion or a general execution runtime.

## Frozen expectation and source basis

The F3 lifecycle Implementation Packet on `origin/planning/ases-phase-i-work-unit-lifecycle-20261030` ??Move without widening? requires a sealed P?Q whole move, fresh activation, a positive permitted read, and a previously prohibited write that remains denied. The Phase I Closure ?7 requires latent permission comparison across activation, and Phase I Verification ?3 T11 requires C's local read/write grants, P's read-only effective ceiling, a more permissive Q, a post-move read, denied write, and a weakened latent-ceiling mutation that admits write. F1's targeted run marks latent ceilings/sealed move partial. F2 latest verified T11 expectation at `8b3c7e06aaab97122d2fcdaf2ee891e62667154b` reports the abstract AT-05 write-after-move deny and weakened mutation admit, while explicitly noting no concrete structural/ACL route test. The host test below adds only a mediator-routed host effect.

Accepted `x` and `y` remain under the existing L4 immutable-content contract. The test reads x from the L4 accepted object and verifies the same hash/bytes before and after each case. It does not write, replace, delete, or republish accepted content. The new write effect targets a distinct disposable `effects/write-effect.bin` under a temporary lab directory.

## Exact checks and observations

Host: Ubuntu `Linux 5.15.0-184-generic`, Python `3.10.12`, Landlock ABI 1. Authority/mediator PID `205041`; worker PIDs `205042` (positive control), `205043` (preserved restriction), and `205044` (mutation). Worker receives one socket FD only; H and W are separate live processes.

- **Positive write:** P grants `{read,write}`, C local grants `{read,write}`. H checks current `W1`, active/unsealed state, full path, operation-to-effect mapping, and grants. H authorizes W's write, atomically replaces the separate effect file, verifies its bytes, then acknowledges `COMMITTED`. Effect bytes are `authorized-positive` (hex `617574686f72697a65642d706f736974697665`), SHA-256 `8732b8a00f4332a354a08c1713b3f31278436d3c16f2befae9095e47590bbd06`.
- **Move under restriction:** P grants `{read}`; C grants `{read,write}`. H snapshots the old effective path `{read}`, commits one sealed whole transition setting C's parent to Q and retaining `C.latent_ceiling={read}`, then separately commits fresh authorized activation on `W1`. Q grants `{read,write}`. H's post-move read check allows and returns accepted x, hex `46332d6c6966656379636c652d782d76310a`, SHA-256 `1462070e6b10a8baf625a31791cd0f4e95af638b42b1767c2aaaf8c79cdef061`. Its write check denies with `current-effective-permission`; no write effect file exists.
- **Unsafe mutation:** same old P restriction, move, Q, worker and `W1`, but the move weakens `C.latent_ceiling` to `{read,write}`. The same post-move write is authorized and produces `post-move-forbidden`, hex `706f73742d6d6f76652d666f7262696464656e`, SHA-256 `fc614537bf8ddf4be6ccf0797898d6c2f476fea99da0fdec674d084dd9b47b83`. This is a detected unsafe configuration, not a passing policy outcome.

The raw trace records request-specific actor/worker PIDs, ingress, parent, current-record digest, effective permission and decision. Whole move and activation each publish a complete JSON selector by atomic replacement. The effect record reports the effect file visible before the reply. All cases independently preserve x unchanged. The report/verifier expectations are separate from the runner: `verify_l5_write.py` checks raw observations, records, decisions, byte hashes, process identities and the unsafe effect without trusting the runner's `acceptance` booleans.

## Reproduction

From the F3 L5 directory on the VPS:

```sh
python3 -m py_compile l5_write.py verify_l5_write.py
timeout 20s bash -c 'ulimit -v 524288; python3 l5_write.py > l5-write-raw.json'
python3 verify_l5_write.py
sha256sum l5_write.py verify_l5_write.py l5-write-raw.json
```

The bounded run completed with `status=L5-PASS`; independent verifier emitted nine `PASS` checks. Limits: 20 seconds, 524288 KiB virtual memory, three cases, two worker requests per case. Raw environment and all observations are retained in `l5-write-raw.json`.

SHA-256:

- `l5_write.py`: `214771793703ad7d2cce234d166ce8c9909a5a4ada7f872c65a1b13054915015`
- `verify_l5_write.py`: `b1e226b7f100b3749cfbbb9f41852288c23af04e2a1491eb38d079d12031d255`
- `l5-write-raw.json`: `a03521863a6dd5ebce55eadb057467a1479e90d13ca526a4607ac2fb52f5d83b`

## Authority/effect route boundary

**Exercised:** worker?authority request/reply over the one passed Unix socketpair FD; H's per-request policy decision; H-only read of the accepted x object; H-only atomic write to the disposable effect file. The worker receives no target path, accepted-object FD, or effect-file FD. The worker is Landlock-confined using the existing L1 helper; its only tested protected effect route here is the mediator socket. H is the trusted authority and effect point for this witness. This is not SELinux or host-kernel enforcement of mediated writes.

**Excluded or not tested:** additional IPC/SCM_RIGHTS/hostile peers, worker descendants and FD passing, network, credentials, shared memory/mappings, alternate mounts/aliases, other external sinks, mediator survival/loss, crash/power-loss durability, rollback resistance, races/concurrency, partial policy application, Q/C descendants, and all-purpose filesystem confinement. No source binding or general physical-worker identity claim is made. L1/L3/L4 previously record bounded read-only direct-path probes; they do not substitute for the routes excluded here. No L1?L4 regression rerun was needed because this change adds an independent L5 harness and does not alter those sources or fixtures.

## Remaining assumption and next task

The harness trusts one serialized H process to load the committed whole state correctly, map operations to effects correctly, retain latent ceilings, and be the only authority over this disposable sink. The records use atomic replace but do not claim fsync/power-loss durability or resistance to rollback/host administration. This is limited host evidence for one mediator-owned write attachment; it does not establish broader Work Unit semantics or Phase I closure.

**Smallest next task:** perform a focused independent source/route review of this L5 harness and its recorded claims, particularly the one-socket authority assumption, actual full-path guard and whole move/activation publication. Then continue only with separately authorized lifecycle work; do not infer F3/F5 completion from this gate.
