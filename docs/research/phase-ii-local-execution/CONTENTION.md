# Native gateway contention and lost-reply histories

These native Unix-socket histories extend the bounded local-execution vertical. They use two real gateway processes sharing one SQLite Store and a trusted profile selecting this test binary's fixed harmless worker. No request carries a command or process identity.

`native_local_contention.rs` exercises two discriminating histories:

1. Two gateways concurrently submit the same job, launch ID, and catalog revision. The existing atomic `Store.begin_launch` transition must grant exactly one dispatch. The winning gateway owns the child handle; the other reports unknown custody. A caller-supplied PID is rejected, the losing gateway cannot signal or finalize without exact exit evidence, and the owning gateway resumes the exact retained `launch_id` and `stop_id`, replays that same durable stop request, waits for its child, records exact exit evidence, and explicitly finalizes.
2. A client sends a complete launch request and closes the Unix socket without reading its reply. The durable started event and worker marker must still appear. Reconnecting with the exact launch identity must observe the existing child without redispatching it; the history then uses the explicit stop and finalize operations.

The test persists `contention-history.json` and `lost-reply-history.json` under `ASES_LOCAL_CONTENTION_EVIDENCE_DIR` when that variable is set. Each record includes source SHA-256 values, requests, responses, event snapshots, worker count, and capacity before and after finalization. The hot owner obtains its replay selectors from `local_resume`, which validates and returns only the exact stop payload fields while retaining the event digest. The worker has a 20-second bounded release gate and cleanup releases it.

WHY: the existing store transition and retained-child owner need verification through actual concurrent gateway connections and a lost response. WHAT: two real SO_PEERCRED gateways, one SQLite database, a fixed trusted worker, durable events, and observed capacity. HOW CERTAIN: experimental until the native test passes on the built binaries. WHAT NOT TESTED: hostile same-UID code, process containment beyond the configured child limits, whole-host failure, and arbitrary or remote providers.
