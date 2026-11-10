# Compact continuation view without inventing liveness or authority

Frozen 2026-11-10. Existing Rust launch-intent runtime `34be0f8e` (PR #20).
Grounding: Engine roadmap's durable work/disposable execution, AGENTS startup
rule that RUNNING/status flags are not liveness, and campaign Priority 5 compact
persistent context/recovery. Router jobs are not thereby promoted to Work Units.

## Smallest new slice

Add a read-only typed `resume_view(job)` to the existing Store. It projects one
coherent SQLite read view: stable job/account/project/environment identity,
recorded state/profile, job versus current catalog revisions, exact launch ID,
and a bounded pointer to retained intent/outcome evidence (event ID/kind/time and
payload digest). Do not include full transcript, forecast_context, event payload
or unbounded historical arrays. Keep encoded view under 2 KiB for valid IDs.
No new durable table or cache. Snapshot serialization is evidence/context, not
a dispatch grant and is never accepted as bootstrap/recovery input.

Derive a clearly advisory next-step enum: authorized work may ask begin_launch;
LAUNCHING must observe/reconcile existing outcome; intent-backed RUNNING needs
process/completion observation, not relaunch; mock RUNNING is explicitly mock;
terminal state has no new dispatch. An unsupported/inconsistent interpretation
refuses rather than inventing a summary. The view itself grants nothing; only
the existing authoritative begin_launch transition can produce DispatchGranted.

Every view distinguishes **recorded state** from **present process liveness**.
Even a retained Started observation does not establish that the process is
still alive now. Do not inspect or signal arbitrary PIDs, infer completion from
an absent process, auto-finalize, release reservations or auto-retry. Observation
truth, current store custody and the trusted adapter remain explicit premises.

## Deciding tests

- Existing actual controller-kill pending history cold-reopens with the same
  continuing job identity, pending-observation advice, no new event/write or
  dispatch grant, and retained reservations. Repeated projection is pure.
- Actual fixed worker starts and exits; retained state remains RUNNING but the
  compact view labels present liveness unknown, preserving exact evidence pointer
  instead of calling the worker healthy/live. Explicit trusted finalization is
  still a separate operation.
- Mock running versus intent-backed running are distinguishable; conflicting or
  missing intent/outcome interpretation refuses.
- A later catalog change appears in current revision while job revision and
  evidence remain preserved. The old serialized view cannot authorize new work;
  begin_launch still performs its own current guard and rejects stale admission.
- Large retained forecast_context does not enlarge the compact view beyond the
  bound; required original evidence remains in the existing event/store.

Use existing Rust types/transactions and no new dependency. Compile with the
already installed user-owned toolchain and committed lockfile. Target new native
and semantic tests; preserve raw process/state/view observations and exact
commands. No new observer daemon, generic orchestrator, provider/model workload,
production transport, canonical policy, CI or independent review campaign.
