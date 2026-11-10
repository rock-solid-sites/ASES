# Priority 5 — bounded launch intent and unknown outcome

Frozen 2026-11-10. Source runtime `1fd05d896dde11f185610a4718c1245cfad1ffca`
on `feature/resource-control-runtime-2026-11-02`. The existing runtime is
experimental and supports mock launch only. Original Phase I branches unchanged.

## Grounding and target

Engine Vision and Phase I roadmap preserve work independently of execution;
Closure §4/H10 distinguishes launch commitment from observed outcome. Main's
Resource Router Cross-Conversation Integration Ledger (2026-11-03) explicitly
requires a one-use bounded launch interface and forbids retrying uncertain
external launch before reconciliation. Work Notes contains no more specific
foundation implementation beyond ASES-2; archived stop-button code is not an
active design and will not be revived.

The existing Rust/SQLite resource runtime implements `launch_mock` atomically
in one local database. It cannot establish exactly-once process creation by
wrapping an external spawn in that transaction. This new slice adds a narrow
durable **launch intent**, not a scheduler, provider adapter or new Kernel
primitive. Exercise only fixed harmless local test processes; no paid resource,
external provider, model call or general shell API.

## Frozen behavior

Reuse current Rust types, catalog/account/freshness checks, quote/reservation,
SQLite immediate transactions and event log. Existing mock behavior remains
available unchanged for its named profile. Add a typed `begin_launch` result:

- First currently authorized, still-fresh bounded launch consumes the permission
  into durable LAUNCHING and records exact job/launch identity before dispatch.
  Only this first return grants dispatch. Record reservation and launch-intent
  in the same existing store; no second ledger.
- Identical job/launch replay in LAUNCHING returns **PendingObservation**, never
  another dispatch permit. Different identity conflicts. Crash after intent but
  before actual spawn may therefore require reconciliation; availability is
  not bought by guessing that launch did not happen.
- Matching replay of a known RUNNING launch returns an observation, not dispatch.
- LAUNCHING holds its physical slot and remaining meter reservations, does not
  expire as an unlaunched authorization and cannot be finalized/cancelled to
  silently release capacity while its process outcome is unknown.
- A trusted adapter may record exact-ID positive started observation, transitioning
  LAUNCHING→RUNNING, or definite non-creation observation, transitioning to CLOSED
  failed. Observation truth/source binding are declared trusted local-adapter
  inputs, not established by arbitrary caller labels. Duplicate identical
  observations are idempotent; contradictory observations conflict.
- New useful work succeeds after positively observed termination/finalization,
  or definite non-creation. Process identity is evidence, not authority merely
  because a PID string was supplied. Do not implement takeover using PID guesses.

State is PRIMARY: RESERVED→AUTHORIZED→LAUNCHING→RUNNING→CLOSED, with unresolved
LAUNCHING preventing blind redispatch. Terminal absence is distinct from unknown.
Rust is retained from the existing bounded runtime; avoid rewriting it or adding
dependencies except those strictly needed for targeted native tests.

## Required tests

Valid reserve/ack/first begin and confirmation; identical and conflicting replay;
stale authority/catalog rejection; independent contender race yields one dispatch;
actual controller-process kill after durable intent before spawn and after actual
fixed-worker spawn before observation; cold reopen returns pending with no second
spawn; reservations/slots remain held even after ordinary expiry/finalize attempts;
matching positive observation permits normal completion and later useful launch;
definite spawn failure can release capacity; contradictory observations reject.
Keep baseline mock tests and run relevant existing tests once after changes.
Preserve raw subprocess/gate/SQLite results, source pins and exact commands.

No production transport, authentication scheme, provider resource creation,
independent review, CI engineering, backup administration, merge or deployment.
If Rust toolchain setup is unavailable, record exact blocker and preserve source
candidate; do not consume the campaign on repeated setup attempts.
