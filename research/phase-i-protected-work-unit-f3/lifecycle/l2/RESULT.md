# L2 result — replace ingress and reject retained W1

Status: **L2 PASS for the declared one-holder, one-host, read-only mediated profile.** This does not establish physical source binding, process-loss recovery, or complete route exclusion.

## Run and observations

- F3 starting HEAD: `5eb216f86f0eaee4ef288a3263b7612e900ab1a6`.
- Frozen packet: `origin/planning/ases-phase-i-work-unit-lifecycle-20261030` @ `415a03fe660f902cfffed6662d1a5982416ee9da`.
- L1 Landlock setup reused from `lifecycle/l1/l1.py`; H=M owns the only selected protected pathname and worker requests are serialized through the one authority process.
- Environment: Linux `5.15.0-184-generic`, Python `3.10.12`, Landlock ABI 1.
- Command: `timeout 20s bash -c 'ulimit -v 524288; python3 research/phase-i-protected-work-unit-f3/lifecycle/l2/l2.py > research/phase-i-protected-work-unit-f3/lifecycle/l2/raw-run.json'`; exit 0, raw `pass=true`, W1/W2 exit 0. No overlapping workload.
- L2 source SHA-256: `ff2d3e4bb3bbd7582a64528269bb7886c4449bb1cd25acec71bbe3223eb0aa13`.
- Raw run SHA-256: `10dee5328a8d22a1efed2418d5c5d5e402c43f8e1bc03c406d1c5cb38c2b70e1`.
- Disposable root: `lifecycle/l2/lab/`; retained failed syntax/setup root: `lab-failure-001/`.

The W1 process (PID 200445) first observed an empty P/C and received the missing-full-path-grant denial. After separate P and C read grants and activation were committed, that same W1 process read and accepted exact x (`b'F3-lifecycle-x-v1\n'`, SHA-256 `1462070e6b10a8baf625a31791cd0f4e95af638b42b1767c2aaaf8c79cdef061`). It remained alive with its original Unix socket endpoint retained. H then atomically published the replacement record `record-000005.json` with current ingress `W2` and acknowledged replacement. W1 used its retained socket after that acknowledgement; H returned `DENY stale-ingress`, zero bytes. A separately launched W2 process (PID 200446) used its newly established endpoint and read the exact accepted object x with the same hash. H PID 200444 serialized both requests and the replacement. The raw observations, endpoint events, record identifiers, hashes, PIDs and exit codes are in `raw-run.json`; the current record and accepted object are in `lab/`.

## Effect and route boundary

H is the sole authority/commitment holder. The initial manager control socket is a trusted explicit-management route. W1 and W2 each receive a distinct socketpair endpoint from the supervisor; H's endpoint-to-ingress association is the current-source distinction in this fixture. Replacement is one state-image update whose selector is atomically renamed before its acknowledgement. W1's later request is checked against the newly read current ingress at H before any source/object read. W2 reads the retained object only after the replacement record becomes current. No target FD crosses to either worker; `close_fds=True` and `pass_fds` supply only each worker's socket endpoint. The same Landlock ABI-1 policy used at L1 blocks worker filesystem access to the fixture and protects the H-owned pathname; L1 contains the explicit direct/source/symlink denials. No SCM_RIGHTS path is used; it was not adversarially tested here.

This establishes denial for the tested retained W1 socket route, not all possible old physical producers. A copied/transferred descriptor remains an old W1 route and should still be rejected by H's association, but descriptor passing/hostile peers were not attempted. No process credential or peer-credential source binding is claimed. H's routing table/process is the enforcer; process-memory state plus published current-ingress record are relied on. No independent holder replacement or survival across H death is tested.

Remaining inventory is as at L1: one local IPC route mediated; no network endpoint provided (network isolation not claimed); no real credentials, environment isolation, shared-memory or mapping controls; worker code does not spawn children but hostile descendants are not prevented by Landlock; one candidate source path and one symlink are tested, all alternate aliases/mounts untested. Landlock policy setup failure prevents worker spawn; partial host-policy change and administrative mutation are not tested. Supported effect is read-only; write access is neither granted nor claimed.

## Preserved harness failure and restart cursor

The first disposable harness attempt created `lab-failure-001/` but the embedded authority source had an indentation error and emitted no ready record; no acceptance or replacement effect occurred. A separate initial import-path error occurred before fixture creation. Both were harness defects, not behavior attributed to the mechanism. They are not counted as negative controls. The successful current run is `raw-run.json`.

L2 is passed. Next is L3: terminate the selected live H, independently establish worker CPU-only continuation and denial over its retained route, then reconstruct from the current protected records without runner state and remain sealed before any fresh explicit activation. Process death only; no host crash/power-loss assertion.