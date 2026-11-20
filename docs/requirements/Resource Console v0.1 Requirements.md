---
title: Resource Console v0.1 — Requirements
program: Tooling
layer: Requirements
document_type: Requirements Specification
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/methodology/ASES Bounded Project Build Method.md
  - docs/methodology/State-Model Applicability and Reuse Method.md
  - docs/standards/Documentation Standard.md
consumed_by:
  - docs/architecture/Resource Console v0.1 Design and Contracts.md
  - docs/research/resource-console/verification-matrix.md
related_documents:
  - docs/research/Provider Registry Control Plane and Usage Reconciliation 2026-11-01.md
  - docs/research/Resource Solver Specification Reconciliation 2026-11-02.md
  - docs/research/kernel-0/Kernel-0-Evidence-Packet.md
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-06
---

# Resource Console v0.1 — Requirements

## Purpose and authority

A lightweight, visually interactive resource-observation console for one Ubuntu VPS and heterogeneous provider accounts, usable by a human on laptop/phone and by agents through machine-readable **read-only** interfaces. It provides derived projections, not an authority substrate, execution engine, scheduler, deployment platform, provider entitlement source, or credential vault. This experimental project cannot establish, reinterpret or override Kernel-0 semantics, Work Unit guarantees, methodological rules, or resource-admission policy. Upward transmission of evidence does not confer upward authority.

## Settled operator constraints

- Host the console on the existing VPS where practical, reusing its already authorized private access route and ingress. No additional always-running application or monitoring process when inactive. A systemd socket unit is not an application process.
- Loading the static page must not start monitoring or provider queries. An explicit **Start dashboard** action activates a monitoring session; a visible Stop ends it.
- Closing the last browser session must terminate **dashboard-owned** monitoring processes (never the agents/services being observed), with a bounded disconnect/heartbeat fallback. Multiple active clients do not cancel each other.
- Presentation should be visual and live during an active session, not a text-only report; a machine-readable equivalent must be available to agents.
- Include local VPS usage, running services/agents, remote execution environments, model/provider allowances, storage capacity and observed usage where access is authorized.
- Historical snapshots should remain accessible after the console is stopped. SQLite is a candidate for local projections, not a new accounting authority.
- Provider accounts, entitlements and usage have distinct scopes and freshness; unknown is never silently treated as zero or unlimited.
- No real provider provisioning/spending, arbitrary shell control, agent termination, resource-solver dispatch or kernel simulation in v0.1.

## Functional requirements

| ID | Required externally observable behavior |
|---|---|
| RC-F01 | Serve a usable static landing page with Start control and zero automatic monitoring requests on ordinary page load. |
| RC-F02 | After authenticated explicit Start, show CPU, memory, swap, disk, and relevant systemd/process/cgroup metrics from the VPS with timestamp, collection source and units. |
| RC-F03 | Render known providers, account/product identities, access routes, offerings, limits, reset/expiry metadata, and usage observations; never present published claims as verified account balance. |
| RC-F04 | Present clearly distinct **measured**, **provider-reported**, **estimated**, **user-reported**, **unknown**, **stale**, and **disputed** information; retain source, time and scope. |
| RC-F05 | Update the active dashboard with recent local observations; query remote provider APIs only according to provider-specific TTL/rate/cost policy and explicitly show reporting delay. |
| RC-F06 | Record selected safe historical observations and session lifecycle in append-oriented form, with reproducible stable IDs; reopening shows history even if no collector is active. |
| RC-F07 | Closing/stopping one tab ends its lease; monitoring remains while any authorized tab remains active. Last lease termination causes collectors and child processes to exit within the specified bound. |
| RC-F08 | An abrupt browser/network loss expires the abandoned lease without requiring reliable page-unload notification; no abandoned child process remains. |
| RC-F09 | Expose versioned, authenticated read-only resource and observation queries usable by agents; the UI must consume the same projections. |
| RC-F10 | Permit only transient monitoring-session control (start, heartbeat, stop) in v0.1; no endpoint changes provider state, scheduler reservations, agent processes or authoritative registers. |
| RC-F11 | Show inaccessible providers and unavailable interfaces as **unavailable/unknown** with reason, rather than a zero or empty record. |
| RC-F12 | Keep secrets, live private account identifiers, billing PII, and unredacted process command-line contents out of browser responses, logs and the public ASES repository. |
| RC-F13 | Existing static site and monitoring can be reopened from laptop and phone through the authorized private ingress, with no added public management socket. |
| RC-F14 | Resource observations can be correlated to projects/jobs/agents when verified IDs exist, with an explicit **unattributed** category otherwise. Never equate Work Units with current jobs. |

## Safety, lifecycle and measurable acceptance

- **No authority:** attempted writes to registry/solver/kernel/provider targets through console routes are rejected; public files are read-only inputs; application database contains only derived data, monitor leases and evidence references.
- **Lazy activation:** after a page-only GET and after the last lease expires, there is no dashboard-owned collector, watcher, service worker with monitoring capability, Node dev server, or other resident console application process. Existing ingress/tunnel processes are not new dashboard overhead.
- **Termination:** target within 5 seconds on clean last-session disconnect; fail-safe expiry and process-group termination within 30 seconds of last observed heartbeat in an abrupt-loss test. These are provisional acceptance targets to verify against actual network and host behavior.
- **Overhead:** measure baseline versus active using CPU, PSS/RSS, disk I/O and provider request count. Initial *target*, not an asserted fact: active non-browser backend PSS <= 100 MiB, idle resident console application PSS = 0, without significant CPU spikes at 1 Hz local polling; revise only using recorded measurements and an explicit design decision.
- **Data integrity:** null/unknown/expired remain distinguishable from zeros; stale snapshots cannot authorize spending. Rendering or refresh may not rewrite historical source evidence.
- **Security:** authenticate before any private data returns; enforce origin/CSRF protection on session-mutating requests; bind local API to protected transport; never expose a raw resource-controller socket, token, or database.
- **Failure isolation:** a failed provider probe or broken browser must not affect monitored services, alter a global accounting ledger, or start remote resources.

## Scope and deferred capabilities

v0.1: local live resource monitoring, cached provider inventory and a few read-only provider probes after verification, read-only agent API, explicit session lifecycle, history and small dashboard. Deferred: deployment, resource launch, automatic routing, cost enforcement, model capability benchmarking, independent Observer, Work Unit lifecycle, and Kernel implementation.

## Evidence classification

Proposed UI and specifications are design claims only. Existing ASES experimental Rust/SQLite controller is unmerged and mock-adapter scoped; its successful tests are **not** evidence that this dashboard or real billing/admission works. Future observations may support research revisions but cannot directly become upstream authority.
