# Independent T18 managed-revocation check

## First verdict, recorded before the probe

**Provisional verdict: supported for the selected flat C/p sink, conditional on the trusted-local-manager boundary.** The frozen T18 current-use fixture requires an acknowledged revoke to precede a rejected post-revoke sink acceptance; the exact-obligation fixture requires a previously committed obligation to remain deliverable after position replacement. Source inspection predicts both: the manager mutates authority under the same sink lock used by submission, records/fsyncs revocation before replying, and exact delivery checks the committed obligation instead of current authority. This is a prediction from source and fixtures, not execution evidence; the bounded primary run below may change it.

The main hidden premise is that callers cannot invoke the manager's `/create`, `/grant`, `/activate`, `/revoke`, and `/replace` routes as untrusted principals. These are unauthenticated loopback HTTP routes in one process; this experiment gives them trusted-manager semantics. It therefore does not establish principal isolation, a generic C/p enforcement boundary, or use by an arbitrary sink. Exact-obligation delivery also presumes the obligation was durably committed before replacement and that its identity-to-payload mapping remains authoritative. The probe uses one fixed obligation and one replacement.

The fixture does not specify a cryptographic ACK, crash recovery, rollback resistance, process confinement, multiple sinks, or concurrent revoke/regrant histories. No such claim is inferred here. The abstract exact-obligation fixture is marked executed, while current-use is prepared-only because f2lib has no sink-side current-authority ordering event.

## Pre-verdict isolation and inputs

Working directory: `/workspace/ases-t18-revocation-check`; branch `review/autonomy-20261105-t18-revocation`; HEAD before evidence creation: `7ed639cd0fc8c938dbc68eb8ca1892e54900713c`. Initial worktree was clean. I read `AGENTS.md`, `ORIENTATION.md`, the two T18 fixture objects in `docs/architecture/core-substrate/fixtures-f2/fixtures.json`, `research/phase-i-t18-sink-order-20261103/managed-revocation/{managed_sink.py,probe.py,check.py}`, and the relevant portions of `research/phase-i-t18-sink-order-20261103/run.py` (sink state persistence, request handlers, and the original experiment's adjacent T18 code). I did not open producer `RESULT.md`, `PREREG.md`, `raw.json`, `check.json`, coordinator ledger, or coordinator index before recording this verdict.

Pre-verdict commands:

```text
pwd && git status --short --branch && ls -la
cat AGENTS.md && cat ORIENTATION.md && git rev-parse HEAD && git status --porcelain=v1
python - <<'PY'  # JSON-load fixtures.json; print only fixture IDs beginning T18-
...
cat managed_sink.py; cat probe.py; cat check.py
rg -n 'T18|managed-revocation|run_t18' research/phase-i-t18-sink-order-20261103/run.py
sed -n '1,230p' research/phase-i-t18-sink-order-20261103/run.py
sed -n '560,635p' research/phase-i-t18-sink-order-20261103/run.py
sed -n '210,355p' research/phase-i-t18-sink-order-20261103/run.py
sha256sum <fixture and four allowed Python inputs>
python3 -V
python3 -c 'import sys,platform;print(sys.executable);print(platform.platform());print(platform.release())'
```

Environment observed before execution: Python 3.12.14 at `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3`, Linux `6.18.57` (`Linux-6.18.57-x86_64-with-glibc2.41`). Pre-verdict SHA-256: fixtures `bdc8cbeb5e917c10f23add99ab8dd88a9d2212d1d9f52be0a7e5c178e1eb6f65`; managed sink `c87f8444b0c3bc8e03d60754d83271348b79e863eab8142ff38da91f7f894a6a`; probe `3b2b47931e9f78e49fee7fefb19b05776792691ca663091781988b8192b036e4`; checker `fcaf60b759783415339b6d0129e8676608a7898c77056e11310fb55bd56d77ec`; imported runner `6b1d759b87b13d32bdc7c5f31a64c15d5a63296d77bc2f16ecc6b0e7795a9d59`.

## Independently derived expected observations

From `T18-use-current-sink-order-after-revocation`: create/grant/activate C; a current write succeeds before revocation; the revoke call returns successfully; a subsequent request carrying the old authority is rejected; the durable/current effect set has zero `x` acceptances after revoke. Source fixture expected observation is `sink=rejected`, `content.x.sink_accept=0`.

From `T18-exact-obligation-delivery-after-replacement`: with p at generation 1 and holder old, commit exact obligation `m -> x` while active; replace p with holder new (advance authority); deliver m after the replacement call returns; observe the exact `x` acceptance. This is separate from current-use: post-replacement current submissions should be inactive/rejected while the explicit committed obligation remains deliverable.

The primary probe's reference run is expected to exercise those two histories, and its `equality_only` mutation is expected to expose stale use if currentness degenerates to equality of the presented token alone. The probe is loopback-only, temporary-directory isolated, and serial at the case level; each sink runs as a disposable child and is killed/reaped. It is not an independent second implementation.

## Observed result and final verdict

**Final verdict: supported within the selected flat C/p trusted-local-manager scope.** The one probe run produced the expected histories. In the reference revocation case, the client received HTTP 200 for revoke; the client-side monotonic end timestamp for that call precedes the next submit's start timestamp. The revoke snapshot has `granted=false`, `active=false`; journal event 7 is `managed_revoked`; the subsequent submit receives 409 and creates no `x` effect. In the `equality_only` mutant, the same post-revoke submit receives 201 and records `x`, so the intended stale-use mutation is detected.

In the exact-obligation case, commit `m -> x` is persisted at event 4 under authority version 1; replacement is acknowledged at event 5 and advances the version to 2 while leaving the unit inactive; a current-use submit is rejected; then the later delivery request is acknowledged at event 7 with payload `x`, obligation `m`, the committed payload hash, `check_mode=committed-exact-obligation`, and `accepted_under_version=2`. The delivery request's start timestamp follows the replacement response's end timestamp. This supports the fixture's distinct obligation semantics.

The independent audit in `audit.py` checks input hashes, response/event identity, journal bytes and sequence order, observed effects against journaled effects, timestamps, process termination and restart refusal, the stale-use mutation, and exact payload/obligation linkage. Its `check.json` has 18 passing checks. The mutation is the built-in mutation in the primary probe; I did not run a second probe.

No implementation failure appeared for these sequential histories. The main harness limitation is that it constructs trusted manager calls and submits after the revoke response; it does not test a hostile caller, an in-flight request racing with revoke, or a separately scheduled manager process. `managed_rejected` is visible in live status but is not appended to the journal; accepted effects and the successful revoke are journaled and fsynced. This limits durable negative-event auditability but did not alter the observed no-effect result. The code and harness both leave the trusted-local-manager assumption external to the mechanism. This is no full F2/F4/native enforcement, crash-recovery, or cross-family independence result.

## Reproduction and artifact identity

Primary execution (run once, loopback-only; empty stderr):

```sh
python3 research/phase-i-t18-sink-order-20261103/managed-revocation/probe.py \
  > evidence/t18-revocation/raw.json \
  2> evidence/t18-revocation/probe.stderr.txt
```

Independent re-audit:

```sh
python3 evidence/t18-revocation/audit.py
```

The captured `raw.json` records Python version and executable path/hash (`fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7`), Linux platform/kernel, a 256 MiB address-space limit, maximum child concurrency 1, source and fixture hashes, and the pre-run execution commit. Evidence hashes: `raw.json` `d1e371b05c64c6ae87c1073ec6de1f8841ceecf5d779a975da98076e15aebbfd`; `check.json` `54c5a5236d44c094f489f4bfa66a57b7f0f7431d537b39a3597f71267560625c`; `audit.py` `cc5697122d6e91be6ef627fda4e5e54b4a3dd04a15abdf72cb2e9e05e431388c`. Probe stderr is empty. The evidence contains no producer result, preregistration, or producer check output.

