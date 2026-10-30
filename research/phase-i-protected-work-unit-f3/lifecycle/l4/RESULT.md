# L4 result — fresh authorization, x continuation and accepted y

Status: **L4 PASS for the selected single-holder/local read-only mediator profile and live-host process-death failure class.** No machine-crash, rollback-resistance, power-loss, arbitrary source-binding, or F3 closure claim.

## Run and observations

- F3 HEAD before L4: `2683908c6e235ea31dfaa4adbd88dfbad2ffe4e6`.
- Packet @ `415a03fe660f902cfffed6662d1a5982416ee9da`; pinned read-only F1/F2 inputs remain `d227a22b9bbc0732881bf58f6933ce46fddc08fa` / `5fb690d4ba7544a4a7eb5fce9ca1e54485543d64`.
- Host Linux `5.15.0-184-generic`, Python `3.10.12`, Landlock ABI 1.
- Command: `timeout 20s bash -c 'ulimit -v 524288; python3 research/phase-i-protected-work-unit-f3/lifecycle/l4/l4.py > research/phase-i-protected-work-unit-f3/lifecycle/l4/raw-run.json'` — exit 0, `pass=true`.
- L4 source SHA-256 `338c8bfed66716c4364d9497e1a49dc4bafb307167ad38db55d9884b07659694`; raw SHA-256 `bd0f28c74005cd9aad29b0b5e514ab553c5430d635b1458510604bcb33cf2860`.
- Fixture `lifecycle/l4/lab/`; outer run <20s, virtual-memory limit 524288 KiB.

H1 PID 201727 was SIGKILLed/reaped with `-9`. W1 PID 201728 remained alive, performed 368,146 CPU-only iterations after H1 reap, then its retained H1 socket produced EPIPE/errno 32 with no bytes. A fresh cold reader validated `record-000004.json`, x bytes/hash and current accepted identity/provenance, constructing sealed inactive P/C and no ingress. H2 PID 201730 independently parsed the same current records and reported `recovered-sealed`, `ingress=null` before any management activation. H2 received a separate explicit manager authorization (`authorized_by=initial-manager` in this trusted harness) and published `record-000005.json` before acknowledging and admitting new W2 PID 201731. No historic endpoint was reused to create W2.

W2 read retained x through H2 after activation: x hex `46332d6c6966656379636c652d782d76310a`, SHA-256 `1462070e6b10a8baf625a31791cd0f4e95af638b42b1767c2aaaf8c79cdef061`. It then read candidate y through the same guarded mediator, presented those bytes for acceptance, and H2 stored/committed exact y plus identity/provenance before `ACCEPTED`; W2 then read accepted y back. y hex `46332d6c6966656379636c652d792d76310a`, SHA-256 `a56c91761fc6a09c69a51a162b4c4f7c7ce5f26cd14371bec50c7fd3a5d8df62`. A separate final reader enumerated both accepted records/objects from current `record-000006.json` and recomputed both exact hashes. The raw run preserves all PIDs, selector record names, identities, events, replies, CPU interval, byte hex and return codes.

After H2 activated W2, W1 used its original retained H1 socket again; it remained disconnected and returned EPIPE/errno 32 with no bytes. No stale W1 route to H2 was installed. This is a process-local socket-lifetime result, not physical identity authentication or arbitrary endpoint-transfer resistance.

H2 recovery is process-independent: it received only the fixture root and its sockets, read current state, validated schema/policy and x object integrity, projected inactive/sealed P/C with no ingress, and did not receive runner-held x/y or reconstructed policy variables. The management activation then separately rebuilt an active W2 route. The recovery and accepted-content selectors use same-filesystem atomic replace; acknowledgements follow current-selector publication. There was no `fsync`, interruption, OS crash, media fault, or power-loss test.

## D1/D2/D3 and routes

D1/D2 are evidenced only for the selected H-owned read mediator/path route: after H1 loss its retained endpoint and tested direct/alias access yielded no new protected bytes; fresh W2 read became effective only after explicit activation. D3 is not immediate: W1 continued CPU work after H1 reap; the observed interval was approximately 80 ms. No upper bound `δ` is claimed and full sealed-execution/Q1 conformance remains unverified.

Route inventory is the L1/L3 inventory for this same fixture: H owns source and protected record/object paths; direct source/alias reads denied under Landlock; W1/W2 receive only their individual socket FDs (`close_fds=True`, `pass_fds` limited to that endpoint); one retained local socket per worker is mediated; no SCM_RIGHTS path is used, but hostile descriptor passing/peer behavior is not tested. Worker code spawns no children, but Landlock does not prevent hostile descendants. No network endpoint is offered and network is not isolated; no real credentials are supplied, and workers inherit the same test UID/environment; shared memory/mappings, other files, bind mounts, alternate aliases/caches and host administrative policy mutation are untested/outside claim. Landlock ABI-1 NNP setup is required before exec; partial host-policy application is not injected. There is no write attachment or external sink.

`candidate-x.bin` and `candidate-y.bin` remain in the disposable source directory as durable candidate dependents. Their presence is deliberate evidence for L6 complete disposition; they are not treated as accepted publications. Logical disposal/removal has not yet been exercised.

## Gate and restart cursor

L4 is passed. Next is L5: explicitly seal C, move it P→Q as a whole selector update while Q is more permissive, activate under a new current ingress, then demonstrate allowed read and continued denial of a formerly prohibited write. L6/L7 remain untested. The supported effect profile remains read-only, so a write denial is a hostile use attempt, not a granted write operation.