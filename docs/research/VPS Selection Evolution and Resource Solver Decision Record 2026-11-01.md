---
title: VPS selection evolution and provisional resource allocation — 2026-11-01
program: EDASES
layer: Research
document_type: Decision and Reasoning Record
status: Provisional
authority: Operator-directed research; not implementation approval
last_updated: 2026-11-01
related_documents:
  - docs/research/Paseo Live Conversations and Resource Planning 2026-10-31.md
  - docs/research/Paseo Cloud Execution Environment Registry 2026-10-31.md
---

# From VPS shopping to work-graph resource planning

## Why the selection criteria changed

1. **Replace or renew the VPS.** Initial objective: compare annual price, advertised vCPU/RAM/storage, renewal cost, location and reliability against the HOSTKEY IT3812 baseline (4 shared vCPU, 8 GB RAM, approximately 120 GB NVMe; $61.91 annual renewal around November 11). Resource pressure, sustained CPU/IO policies and recovery access made nominal specification insufficient.
2. **Compare effective capacity and recoverability.** CPU share/limits, random IO, rescue console, performance under concurrent agents, migration risk and operating overhead became more important than advertised vCPU count. TNA Hybrid-8/12 emerged as low-price candidates, but cached HDD, older Xeon, Chicago latency and actual checkout/CPU behavior remain unverified.
3. **Question the assumption of one permanent machine.** Codespaces, GitHub Actions, Codex Cloud, Mistral cloud, Modal and ephemeral sandboxes could supply bounded compute. A small persistent Linux host remains useful for coordination, durable lightweight services and recovery, while bursts move elsewhere when demonstrably feasible.
4. **Separate three scarce resources.** Model/provider allowances, coding harnesses and physical execution environments are different constraints. OpenCode Go or a model subscription is not free CPU/RAM; Codex Cloud managed tasks are not automatically a general-purpose external-agent workspace.
5. **Move from provider ranking to whole-work-graph allocation.** Dependency ordering, parallel stages, cache warmth, startup and transfer overhead, quota resets, security and evidence retention can make the cheapest individual job placement a worse overall plan.
6. **Prioritize conversation provenance and coordination before automation.** Paseo is the selected management plane, with original live ChatGPT/DeepSeek conversations first, related sessions second, advisory resource planning third, and selectively verified execution adapters fourth. Imported transcripts do not satisfy live-conversation access.

These are changes in the *decision problem*, not retroactive claims that earlier candidate providers were wrong. Preserve dated assumptions and superseding rationale rather than deleting old comparisons.

## Provisional allocation policy (not reserved capacity)

| Workload | Preferred investigation / allocation | Fallback or constraint | Confidence |
| --- | --- | --- | --- |
| Always-on coordination, lightweight tools, recovery | Affordable persistent Linux VPS running Paseo and necessary services | HOSTKEY renewal vs TNA or other replacement after measured footprint, checkout, CPU/IO and rescue verification | Direction selected; host undecided |
| Strategy conversation grouping | Original live ChatGPT and DeepSeek sessions opened and grouped through Paseo | No import-only substitution; account-wide agent search not verified | Requirement confirmed; integration unverified |
| Ordinary repository CI, tests, deploy checks | GitHub Actions where legitimately eligible | Respect account/billing and repository-specific terms | Existing workflow; incremental capacity unmeasured |
| Interactive bounded development | GitHub Codespaces when plan quota and lifecycle fit | VPS or portable sandbox | Documented quota; integration untested |
| Burst compilation, tests and browser automation | Modal Functions/Sandboxes using reported recurring $30/month credit | PAYG hourly VM with cap, or sandbox trials | Strong candidate; live balance and workload fit unverified |
| Managed cloud coding tasks | Codex Cloud under existing ChatGPT allowance; Mistral Vibe Web exploratory | Do not assume ability to run arbitrary OpenCode child agents | Existing access; cross-harness launch unverified |
| Portable OpenCode sandbox experiments | Daytona ($200 introductory credit) then E2B ($100 introductory credit) | Credits are one-time, not monthly | Candidate; terms and actual balances unverified |
| High-memory/CPU short bursts | Compare hourly OVH/Hetzner or other PAYG only when free/included options infeasible | Hard cash cap, teardown and delete evidence | Candidate |
| Durable source, decisions, test evidence | GitHub for source; independent R2/B2 or suitable object storage for worker artifacts | Do not rely on disposable worker disks or indefinite CI artifact retention | Architectural preference |
| Discontinued or policy-incompatible services | Exclude Jules, Ona/Gitpod Cloud, Codeanywhere; restrict Vercel Hobby for commercial workloads | Retain research history without routing jobs | Exclusion documented |

**No purchasing decision, live quota balance, provider reservation or automatic routing authorization is implied.** The existing VPS remains the operational baseline pending a verified replacement. Provider credits, discounts, renewal and account permissions must be checked at plan time.

## Resource solver v0: advisory contract

**Inputs:** work graph (stages, dependencies, alternatives, parallelism, CPU/RAM/disk, expected duration, architecture, security sensitivity, artifact size, verification and deadline); model allowances; harness compatibility; environment capacities and concurrency; recurring/one-time credits, remaining balance and reset time; setup/warm-cache and data-transfer costs; observed evidence with timestamp/confidence.

**Hard feasibility gates:** supported launch mode; actual available quota/credit and region; memory/CPU/storage requirements; model/harness compatibility; dependency readiness; acceptable trust and secret scope; deadline/resource window; cancellation/cleanup; independently recoverable results. Unknowns cannot silently pass hard gates: mark plans conditional or demand a discriminating test.

**Planning:** enumerate feasible stage/environment/model/harness combinations; account for shared workspace setup and cache reuse; schedule dependencies and parallelism; evaluate *complete* plans for cash, credits, makespan, risk and evidence quality. Present a small Pareto set such as lowest cash, fastest finish and conservative compatibility, with explicit assumptions. Avoid a single opaque weighted score.

**Replanning:** freeze completed stages and evidence; update measured runtime, quota and failures; recompute only unfinished graph; retain the previous plan, reason for reassignment, and estimate-versus-actual deltas. No always-on autonomous dispatcher.

**Initial cheapest tests:** (1) measure idle and concurrent Paseo/VPS footprint; (2) query current balances and reset dates; (3) run one reproducible small compile/test on existing VPS, Actions, Codespaces and Modal where authorized; (4) compare startup, elapsed time, memory peak, credits and retained evidence; (5) test cancel/delete and artifact recovery. Use existing usage/TPS telemetry before adding monitoring overhead.

## Open decisions and provenance discipline

- **Persistent host:** HOSTKEY renewal versus TNA Hybrid-8/12 or alternatives; price alone is insufficient. Record actual checkout, latency, CPU sustained-load behavior, disk IO, rescue access, migration time and Paseo baseline.
- **Compute economics:** GitHub public/private repo eligibility, Codespaces personal-versus-organization quota, Modal actual balance, Mistral account allowance, Daytona/E2B introductory balances, hourly VM teardown charges.
- **Capability:** Paseo live conversation continuity and restart; authorized cross-chat search; Codex Cloud launching external OpenCode; sandbox lifecycle, cancellation and provenance.
- **Security:** cloud workers are untrusted; use least-privilege short-lived credentials and independently stored evidence.
- **Source discipline:** October 31 environment registry is a dated research snapshot. Every numeric offer is provisional until checked against a live account or order page. Distinguish operator direction, published documentation, direct observation and inference.

## Next implementation boundary

Build a **pure, deterministic solver prototype with synthetic fixture data** before connecting accounts or executing jobs. Start with a small DAG and 3-4 environments, hard feasibility rejection, two or three full-plan alternatives and a partial-stage replan test. Test rejection of expired one-time credits, insufficient RAM, missing harness compatibility, impossible dependency schedules, and incomplete teardown support. Keep solver separate from Paseo integration and the canonical ASES Work Unit engine; expose it later as an advisory query interface only.
