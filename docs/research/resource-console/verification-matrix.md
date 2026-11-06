---
title: Resource Console v0.1 — Verification Matrix
program: Tooling
layer: Research
document_type: Research Protocol
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/requirements/Resource Console v0.1 Requirements.md
  - docs/architecture/Resource Console v0.1 Design and Contracts.md
  - docs/methodology/State-Model Applicability and Reuse Method.md
related_documents:
  - docs/methodology/ASES Bounded Project Build Method.md
  - docs/research/Guarantee-Driven Testing and Goal-Substitution Resistance.md
consumed_by:
  - docs/research/resource-console/implementation-packet.md
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-06
---

# Resource Console v0.1 — Verification Matrix

All items below are **planned tests**, not executed claims. Follow existing ASES/VSDD evidence and independent review discipline. Do not interpret a mock pass as proof of real VPS shutdown, authentication, or provider accounting.

## Acceptance table

| ID | Claim and falsifying test | Required evidence | Maps to |
|---|---|---|---|
| V01 | Static first-load is inert: open and refresh the page without clicking Start; no collector request, poll, provider call or dashboard-owned backend left running. | Network trace, process tree, baseline PSS/CPU, 60s observation | F01, F13 |
| V02 | Explicit authenticated Start activates one lease and real local metrics within a bounded period; no auto-start from asset requests. | Timestamped process events and metric source/units | F02, F05 |
| V03 | Stop removes lease and last-session collector subprocess; never signals observed agent process. | Process-group logs, liveness checks for unrelated dummy process | F07, F10 |
| V04 | Browser/tab closure ends monitoring promptly when observable; abrupt network loss expires orphan within 30s of final received heartbeat. | Mobile/desktop browser and killed-network tests, process/PID checks | F07, F08 |
| V05 | Two active leases: closing one preserves other's metrics, closing final stops; restarted session does not inherit stale lease. | Parallel clients, unique lease/generation IDs, process trace | F07 |
| V06 | Repeated Start/Stop/heartbeat, delayed old heartbeat, timeout at start, duplicate request ID cannot resurrect expired collector or create duplicate persistent monitor. | Mutation/race fixtures, transition traces, orphan scan | F07, F08 |
| V07 | Unknown, null, expired, and stale provider quota never appear as 0, infinite, verified remaining credit, or spendable allowance. | Known-accounts source mappings, negative JSON fixtures, UI snapshots | F03, F04, F11 |
| V08 | Provider API failures leave prior snapshot marked stale/unavailable rather than deleting history or creating a false zero. | Fault-injected 429/500/timeout tests, historical snapshot comparison | F03–F06 |
| V09 | Provider-specific TTL/rate limits respected, no provider API call when inactive, reporting lag visibly represented. | Mock clock/provider logs, counted requests and timestamps | F05 |
| V10 | SQLite snapshots survive restart, interruption and collector shutdown; repeated source events deduplicate without rewriting evidence. | DB query/digest before/after fault, crash/reopen tests | F06 |
| V11 | Human and agent queries produce matching values, provenance, source revision and evidence-kind, freshness and dispute classifications from one projection. | Golden fixtures for REST and UI view model | F04, F09 |
| V12 | Browser and client cannot call privileged controller/provider mutation, execute shell, view secrets or access unrestricted local sockets. | Auth negative tests, CSRF/cross-origin tests, route/method denial, leak scan | F10, F12, F13 |
| V13 | Metrics distinguish processes, services, sessions, jobs, provider resources and unattributed usage; no fabricated joins or Work Unit claims. | Identity collision fixtures and source reference checks | F14 |
| V14 | Resource-use targets measured on real target host: PSS/RSS, CPU, I/O, startup/shutdown and provider request volume in idle and active states. | Reproducible command output, host version, repetition and baseline | F01, F02, F05 |
| V15 | Browser UI works on phone and laptop behind the existing private access route, with keyboard access, accessible status and chart/table equivalence. | Browser session and accessibility test evidence | F01, F13 |
| V16 | Console data cannot change kernel/Engine/admission/project authority and never issues destructive actions against observed jobs. | Static route audit, negative API tests, credentials/privilege audit | F10, F12 |

## Lifecycle model scope

The **dashboard lease protocol** is SUPPLEMENTARY state modeling under ASES State-Model Applicability and Reuse Method. Test legal starts/stops, timeouts, stale events, concurrent leases and crash/restart. The model contains no authoritative Kernel/Work Unit primitives. Check the physical process state in addition to any modeled terminal-state claim.

Critical counterexample traces:

- Last tab disappears without close message; no heartbeat arrives. A monitor process must be gone by the fallback bound.
- Final tab closes while another tab's Start is in flight. The new explicitly authorized lease, if successfully established, may keep the collector alive; the old lease cannot be revived by a delayed heartbeat.
- A prior process crashes after writing evidence but before sending response. Replaying the event must not double-add usage or delete the previous observation.
- A provider's publicly advertised "free" plan and a null account credit field coexist. No view claims available credits.
- Provider usage and locally observed usage overlap. The UI must not sum them as separate charges without reconciliation evidence.
- A session ends while an unrelated Go service is running. Stopping the dashboard must not terminate that service.

## Resource budget and measurement

Record host/OS architecture, CPU, RAM, background load and network environment. Collect an idle baseline over at least 60 seconds, repeat with dashboard static page open for 60 seconds, then active with local metrics, and finally 60 seconds after last-session shutdown. Capture `ps`, `systemctl` state, cgroup information, PSS via `/proc/<pid>/smaps_rollup` where authorized, CPU-time deltas, I/O and request counts. Exclude the pre-existing ingress explicitly; report measured deltas rather than fictitious absolute zero host usage.

Provisional goals: 0 resident console application PSS at idle, <=100 MiB active non-browser backend PSS, clean disconnect shutdown target <=5s, abrupt loss <=30s after last heartbeat. Set a justified CPU threshold using repeat baseline and 1 Hz local collector; never silently relax a failed goal.

## Environment gates before production

1. Inspect exact existing VPS ingress/auth path, service manager, cgroup version, local socket authorization and available process-level metrics; reject unverified assumptions.
2. Verify static page can be served without waking the collector.
3. Test authenticated socket activation/connection and lifecycle on a disposable or isolated service identity; protect unrelated production processes.
4. Validate v1 projection schema against synthetic fixtures and the known-account mapping. No account credential or private usage in public repository.
5. Run red/green/negative testing, independent post-build review of critical claims, and controlled live acceptance.
6. Require separate approval for any provider API scope expansion or mutation capability; v0.1 need not provide any.

## Evidence record format

Each result should include test ID, fixture/scenario, environment and commit SHA, input/source revision, observation time, outcome (`passed`, `failed`, `not_run`, `blocked`), measured values where relevant, evidence paths/hashes, and explicit limits. Tests performed only on synthetic fixtures do not validate the production VPS.

**Current status: all tests NOT RUN; no live console implementation is claimed in this document.**
