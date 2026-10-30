# L1 result — empty boundary, denied missing grant, accepted x

Status: **L1 PASS for the declared local read-only mediated attachment profile.** This is one concrete bounded witness, not F3 closure or a claim of broader confinement.

## Source and run

- F3 branch HEAD at test start: `fd36abffb6cd04733cd65841355a651ca55de509`.
- Frozen packet: `origin/planning/ases-phase-i-work-unit-lifecycle-20261030` @ `415a03fe660f902cfffed6662d1a5982416ee9da`.
- F1/F2 read-only pins: `d227a22b9bbc0732881bf58f6933ce46fddc08fa` / `5fb690d4ba7544a4a7eb5fce9ca1e54485543d64`.
- Host: Linux `5.15.0-184-generic`, x86_64; Python `3.10.12`; Landlock ABI 1; handled filesystem rights mask `8190`.
- Syntax: `python3 -m py_compile research/phase-i-protected-work-unit-f3/lifecycle/l1/l1.py` — PASS.
- Exact bounded run: `timeout 20s bash -c 'ulimit -v 524288; python3 research/phase-i-protected-work-unit-f3/lifecycle/l1/l1.py > research/phase-i-protected-work-unit-f3/lifecycle/l1/raw-run.json'` — exit 0, report `pass=true`; no concurrent test process.
- Final source SHA-256: `000359c5f40a6d560940c356f3e4b08d8ce88e88e45cdf8ba7af9e8afe8d46f2`.
- Raw run SHA-256: `37305b2c00f96d5e0abb78528955871dac2d188e62b3bc6a19e0d5aebd161513`.

## Concrete observations

The disposable root is `lifecycle/l1/lab/`. H=M is a separate authority/mediator process (PID 199477). It wrote the initial protected record `record-000001.json` with P and C empty, inactive, without grants, and without accepted data. Before manager intervention, W (PID 199478) requested the selected read route. H read its current record, computed the effective ancestor-and-child read predicate, and denied with `missing-full-path-grant`, zero bytes. The returned observation contains both P/C inactive, empty grant arrays and null accepted content; this denial is policy-derived, not hard-coded in the successful run.

W's attempts to open the protected selector, candidate source and one symlink alias each failed with `EACCES` (errno 13) under Landlock. W then held only its retained local socket route to H for the supported operation. The explicit initial manager granted `read` separately at P and C and then activated them as two ordered management commitments (`record-000002.json`, `record-000003.json`). W's mediated source read succeeded with exact bytes `46332d6c6966656379636c652d782d76310a` (`b'F3-lifecycle-x-v1\n'`), SHA-256 `1462070e6b10a8baf625a31791cd0f4e95af638b42b1767c2aaaf8c79cdef061`. W presented those returned bytes for acceptance. H compared the submitted hash with the hash of the bytes it had just read and accepted, then stored the immutable content object plus accepted identity/provenance in `record-000004.json` and only then atomically replaced `CURRENT` and acknowledged `ACCEPTED`.

The independent reader was a different process (PID 199479), launched after H exited; it read the published `CURRENT`, record and object from disk without receiving expected x or accepted state from the runner. It returned the exact 18 bytes, same SHA-256, identity `C-content-1462070e6b10a8ba`, source `candidate-x.bin`, actor `worker-ingress-W1`, and matching presented hash. The worker exited 0. The source-level fixed expectation and the independent readback agree.

The selected commit boundary is the same-filesystem `os.replace` of `CURRENT` after object and full record preparation. The mediator sends an acceptance acknowledgement after that replacement. This demonstrates process ordering/publication in the live host process profile only. No `fsync`, OS crash, power-loss, rollback or corruption durability inference is made. Private object/record preparation before selector replacement is not the accepted state; unreferenced preparation debris is not automatically disposed in this experiment. No failed-write or lost-reply injection was run.

## Route inventory and claim limits

| Route | L1 disposition |
|---|---|
| Protected state/object paths | Worker direct opens of `CURRENT`, source and one symlink alias tested and denied by Landlock; H is the only intended path reader/writer. Other aliases, mount/bind paths and rename races are untested. |
| Open/inherited descriptors | `Popen(close_fds=True)` passes only W's socket endpoint; no protected FD is deliberately passed. No `/proc/<pid>/fd` snapshot or hostile preopened-FD mutation was captured, so complete FD exclusion is not claimed. |
| SCM_RIGHTS | No descriptor passing code or route in the successful worker; no hostile `sendmsg` bypass attempt. Treat as disabled by this fixture's code, not host-wide exclusion evidence. |
| Child processes | Worker does not spawn children in this trace. Landlock does not block fork/exec; a hostile descendant route is outside this claim and not tested. |
| Local IPC | One retained `AF_UNIX` socketpair is the only supported attachment route and is mediated per request by H. No hostile peer or duplicate endpoint mutation was attempted. |
| Network | No network endpoint or network operation is part of the test. No network namespace/seccomp isolation; host network access is not claimed disabled and is outside the supported attachment profile. |
| Credentials/environment | No real credentials/secrets were provisioned. W runs as the same Unix identity and inherited environment as the harness; credential/env isolation is outside the claim. |
| Shared files/mappings | One fixture source and protected record/object directory; the tested pathname aliases are denied. Other files, mappings, shared memory, caches and alternate roots are untested/outside claim. |
| Live policy | Landlock ABI-1 ruleset with filesystem read/write/create/remove rights handled, installed with `PR_SET_NO_NEW_PRIVS` before W exec. Setup failure aborts spawn. H's current grant/activation state is its in-memory view persisted by current selector. Partial Landlock application, host administrative changes and general ACL behavior are not tested. |

Supported effect is read-only mediated candidate retrieval and one accepted immutable content publication. There is no write attachment or external sink. Initial management is an explicit trusted test-runner control route; manager identity authentication is assumed, not established by this fixture. Physical producer/source binding, hostile peer exclusion, full filesystem confinement and all unlisted routes remain unproven. H is the single serialized current authority/commitment holder; W's socket is a bearer endpoint and no stronger physical-source claim is made.

## Preserved non-passing harness runs

The first argv-indexing failure, the shutdown-response harness failure, and the trailing `PY` submode typo are retained with their disposable roots as `lab-failure-001/`, `lab-failure-002/`, and `lab-failure-003/`; the earlier run that accepted x but had an unconditional initial denial is retained as `lab-initial-vacuous-control/` plus `raw-initial-vacuous-control.json`. The unconditional-denial observation was explicitly rejected as vacuous and is not counted as L1 evidence. Their console diagnostics are the command-session raw outputs; the final successful run is preserved verbatim in `raw-run.json`. These failed attempts produced no observed surviving worker/authority processes after each run.

## Gate and restart cursor

L1 is passed only for this local, process-live, read-only mediated profile. Next gate is L2, and must independently show W1 succeeds, a replacement commit creates current W2 ingress that reads accepted x, and retained W1 ingress is denied after replacement. Do not infer any L3 authority-loss/cold-recovery result from this L1 run.