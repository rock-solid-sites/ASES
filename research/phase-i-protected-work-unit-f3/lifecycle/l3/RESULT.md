# L3 result — actual authority loss, continued worker, sealed cold readback

Status: **L3 PASS for the selected H=M local read-only mediator and live-host process-death profile.** This is not a machine-crash, power-loss, rollback-resistance, D3/quiescence bound, or F3 closure result.

## Run and exact observations

- F3 HEAD before this gate: `5ae2e2fef63ee05beae7e21b8b26291ba8db358b`.
- Frozen packet @ `415a03fe660f902cfffed6662d1a5982416ee9da`; F1/F2 read-only pins remain `d227a22b9bbc0732881bf58f6933ce46fddc08fa` / `5fb690d4ba7544a4a7eb5fce9ca1e54485543d64`.
- Host: Linux `5.15.0-184-generic`, Python `3.10.12`, Landlock ABI 1, handled rights mask 8190.
- Compile: `python3 -m py_compile research/phase-i-protected-work-unit-f3/lifecycle/l3/l3.py` — PASS.
- Run: `timeout 20s bash -c 'ulimit -v 524288; python3 research/phase-i-protected-work-unit-f3/lifecycle/l3/l3.py > research/phase-i-protected-work-unit-f3/lifecycle/l3/raw-run.json'` — exit 0; one workload at a time.
- Source SHA-256 `c398ea3875791e60ead44e204d1c97bdc37b47c215e23d2091aade7de6c3aac3`; raw run SHA-256 `b75844a0675745638a519eae9a2764acd3fbd89469883c457c5063b8aedf9976`.
- Disposable root: `lifecycle/l3/lab/`; initial argv-index failure root: `lab-failure-001/`; failure traceback is preserved in `raw-failure.json`.

H=M PID 201159 established empty inactive P/C, denied W's initial read with a state-derived missing-full-path-grant response, then committed explicit P and C read grants and activation. W PID 201160 read and accepted x before loss. The accepted bytes are `b'F3-lifecycle-x-v1\n'`, SHA-256 `1462070e6b10a8baf625a31791cd0f4e95af638b42b1767c2aaaf8c79cdef061`, identity `C-content-1462070e6b10a8ba`, stored in the immutable object referenced by `record-000004.json`.

The supervisor requested SIGKILL for H at monotonic ns `210687540282144`; `wait()` reaped H with return code `-9` at `210687541476531`. W was independently observed still alive after H reap. Only then it received the CPU trigger, performed 378,873 arithmetic iterations (`cpu_start_ns=210687541593496`, `cpu_end_ns=210687621598320`), and attempted a new read over its retained socket. The peer was gone: `IOERROR`, errno 32 (`Broken pipe`), with no bytes. Direct source and one symlink read opens, plus an O_WRONLY open, were denied `EACCES`/errno 13. W exited 0 after reporting.

A fresh reader process PID 201161 then received only the disposable root path. It independently opened current selector `record-000004.json`, parsed the supported policy, followed the accepted object reference, checked size and SHA-256, and reconstructed P/C inactive and sealed with no execution ingress. It returned exact x bytes/hash and accepted identity/provenance before any fresh activation/use. The recovery process received no expected x, hash, grants, accepted content, or runner-maintained state. Its independently computed hash equals the fixed test expectation.

Failure class is **authority-process SIGKILL/reap while kernel and filesystem remain live**. Selector publication used same-filesystem `os.replace`; no `fsync`/power-loss inference. Recovery was read-only; it did not prove rollback/corruption resistance. Incomplete/malformed current material handling is coded as refusal, but that negative mutation was not exercised here.

## D1/D2/D3 and concrete route boundary

- **D1 admission:** after H death the only selected request-serving holder was gone; retained W request returned EPIPE. Tested direct source and symlink route opens also denied.
- **D2 protected effect:** no new accepted/read effect occurred after H death in the selected fixture. Effect denial is at the now-closed H-owned local socket plus Landlock path policy; this is only the tested read-only route set.
- **D3 execution:** disproven as instantaneous termination for this realization: W performed CPU work after H reap. The observed CPU interval is about 80 ms, but no quiescence bound `δ` is asserted. Strong sealed-execution/Q1 conformance remains unverified; the interval is not confused with D1/D2.

Route inventory is the same declared local profile as L1, with these L3 outcomes: H-owned protected source/records; worker source and alias reads denied after loss; retained local socket returned EPIPE after H reap; no target FD passed; `close_fds=True`, `pass_fds` limited to the socket. L1 separately tested direct access to `CURRENT`; L3 did not retest a record-path alias. SCM_RIGHTS is absent from the worker code but adversarial descriptor passing was not attempted. No child is spawned by the worker trace; hostile descendants are not prevented by Landlock. No network endpoint is supplied and network is not isolated. No real credentials are used; worker shares the test UID/environment. Other paths, bind mounts, mmap/shared memory, caches and host administrative policy changes remain untested/outside claim. Landlock ABI-1/NPP was applied before exec; failed setup aborts spawn. Live mediator policy resides in H and terminates with it; persisted records survive the observed process death.

## Gate and restart cursor

L3 is passed for the profile above. Next is L4: after cold sealed reconstruction, separately and explicitly authorize a fresh execution ingress, read x, accept distinct y, and verify the current whole record plus both exact accepted contents. Do not count the CPU continuation as evidence that execution was disabled. L5–L7 remain untested.