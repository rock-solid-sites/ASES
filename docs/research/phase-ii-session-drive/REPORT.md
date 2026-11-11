# Native session-driver evidence

`resource-control/tests/native_session_drive.rs` exercises the `resource-drive` binary through its fixed sibling `resource-session`, the actual optional Unix gateway, and one fixed test worker per independent Store. Each worker is this integration-test binary in a bounded helper mode; cleanup uses only a release file or the retained gateway child handle. No persisted PID is adopted.

## Observations

The native history passed 1/1. It records five independent histories:

- A natural code-0 child exit was observed exactly before the driver sent the caller-selected `completed` outcome to finalize. Launch intent, start, exit, and finalization appeared once; one worker ran and finalization released capacity.
- A natural exit code 7 was retained as process evidence. The driver finalized only the caller-selected `failed` outcome; it did not infer outcome from the exit code.
- A 150 ms polling budget expired with the child still running. The driver reported `budget_exhausted`; the event snapshot had no stop or finalize, and the reservation remained held. The test then used a separate explicit release/poll/finalize sequence for bounded cleanup.
- After gateway loss, a fresh driver invocation returned recovery-needed with unknown custody. It did not append events, create another child, stop, or finalize; reserved capacity remained. The orphaned helper exited through its own release file.
- A transport proxy relayed launch and poll to the actual gateway and paused before forwarding finalize. The test observed exact exit evidence and held capacity before forwarding. The actual gateway committed finalize and returned success; the proxy discarded that response. The driver returned recovery-needed for `last_action: finalize`, made no further proxy connection, and did not claim capacity remained held. A fresh client resume read the durable `CLOSED` state and `FINALIZED` pointer.

The actual driver stdout/stderr, nested client replies/statuses, gateway replies at the finalization proxy, durable event/balance snapshots, worker launch identity/counters, exact command, source hashes, and test result are retained under `evidence/`.

**WHY:** A bounded consumer must use the existing Store transitions without inferring semantic outcomes, stopping on budget exhaustion, or retrying an uncertain effect.

**WHAT:** Actual driver/client/gateway/worker histories, Store events and balances, plus a transport-only proxy that discards a committed finalization reply. The proxy has no Store access or lifecycle authority and runs as the same test UID allowed by the actual gateway policy.

**HOW CERTAIN:** Experimental; the focused native history passed and retained records agree with assertions.

**WHAT NOT TESTED:** Remote providers, hostile same-UID code, whole-host loss, arbitrary programs, hard wall-time quiescence, generalized methodology automation, or automatic repair of unknown outcomes.

The exact focused command, test count, source hashes and history hash are in `evidence/manifest.json`.
