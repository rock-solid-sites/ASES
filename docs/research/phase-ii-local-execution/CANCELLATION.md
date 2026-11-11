# Native local launch and generic cancellation composition

`native_local_cancellation.rs` verifies the original living-child/capacity invariant through two actual Unix gateways sharing one SQLite database. The first gateway has the trusted local profile and administrator peer. The second has the existing collector grant, so generic `{"op":"finalize","job_id":"…","outcome":"cancelled"}` is authorized and forwarded through the gateway's one-shot `ases-resource-control DB request -` CLI path.

The test covers three histories:

1. **Cancellation first:** generic finalize commits `CLOSED/cancelled` and releases the reservation. A later `local_launch` fails, records no launch intent, and creates no worker.
2. **Launch first:** the native gateway launches one fixed worker and records start evidence. Generic finalize is rejected with no event change, the worker remains alive, and capacity remains held. Only after the owning gateway performs actual stop/wait and explicit native finalize does capacity release.
3. **Concurrent calls:** native launch and generic cancellation start together over separate real sockets. Store transaction ordering must yield one safe result: either cancellation closes the job before any child exists, or launch creates one retained child while cancellation is blocked. The test explicitly cleans up a launch-winning child through its owning gateway.

The fixed test-binary worker records its PID/start token as evidence and waits on a release file with a bounded timeout. The test never signals a process using that saved identity. `ASES_LOCAL_CANCELLATION_EVIDENCE_DIR` captures actual requests, replies, event logs, worker counts, capacity, and source hashes. The focused run is retained under `evidence/cancellation/`.

WHY: A generic cancellation must not release a reservation while the local adapter owns a living child. WHAT: Actual gateway requests, one-shot CLI forwarding, durable event histories, worker marker/liveness, and remaining capacity. HOW CERTAIN: Experimental; the focused native target passed 2/2 entries. The recorded simultaneous history linearized launch first, while the explicit first-wins histories cover both safe branches. WHAT NOT TESTED: hostile same-UID processes, process-tree containment, whole-host failure, remote providers, or arbitrary configured executables.
