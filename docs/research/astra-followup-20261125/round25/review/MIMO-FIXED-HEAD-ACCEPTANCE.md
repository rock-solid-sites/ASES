**All four closed** (corroborated by reported exit 0/PASS):

1. **Seal cause** — `verify_probe.py:113-118` requires `result==DENY`, `error=="OperationalError"`, `reason=="database is locked"`, `owner_selection_changed`/`durable_phase_changed` `is False`. JSON `cases.A1-A3.a1.lifecycle_at_gate.refusal.reply`.
2. **Full cut** — `lifecycle_readback`/`immutable_lifecycle_cut` (`:60-87`) compare owner state (incl. CURRENT)/selector/generation/inventory subset, owner_tree, F1 `store.sqlite`, L6 `protected/`, journal blob, witness status/current/revision. JSON `...lifecycle_at_gate.{before,after}`.
3. **Null key** — `:178-179` asserts key present and value JSON null. JSON `cases.A1-A3.same_A_retry.refreshed_response.response.body.local_control_committed`.
4. **Distinct envelope** — `:167-170` asserts envelope inequality, `request_id==aid` both sides, `l5` selector change. JSON `...same_A_retry.{exact,refreshed}_envelope`. Refreshed reason now exact full-string (`:176-177`), stricter than prior substring.

**Limits:** claim stays gate-time serialization against one in-flight `seal` (`:106`) — no generalized denial. Exact `database is locked` text is SQLite-message brittle; same-A retries still use narrower `immutable_cut` (`:51-57`), not L6/inventory; single contender/run. SHAs not re-hashed (read-only).
