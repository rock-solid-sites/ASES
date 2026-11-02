---
title: ASES Resource Solver Specification Reconciliation — 2026-11-02
program: ASES
layer: Research
document_type: Design Document
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on: []
consumed_by:
  - proposed resource-control API and lifecycle specification
  - proposed account-scoped resource registry
related_documents:
  - docs/research/Provider Registry Control Plane and Usage Reconciliation 2026-11-01.md
  - docs/research/Provider Onboarding and Reality Model Audit 2026-11-01.md
  - docs/research/Independent Feasibility Gate Requirements 2026-11-01.md
  - docs/research/Resource Solver Admission Gate and Exact Reference Audit 2026-11-01.md
  - docs/research/Provider Funding Liability and Language Policy Correction 2026-11-01.md
  - docs/research/Provisional Environment Configuration and Shared Resource Model 2026-11-01.md
  - docs/research/Task Execution Evidence and Model Quality Index Integration 2026-11-01.md
  - docs/proposals/2026-11-02-testing-debugging-ontology/ases-account-enumeration-chat-2026-11-02.md
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-02
---

# ASES Resource Solver — Specification Reconciliation

**Status: provisional cross-conversation synthesis, not a new canonical specification, production gate, approved implementation, or policy promotion.** This record reconciles operator-directed decisions in the *ASES Account Enumeration* discussion (November 1–2, 2026) with existing ASES resource-solver, provider-registry, execution-management, and EDASES testing research. Earlier source documents remain available and retain their own authority. No model capability harness, future Observer, or actual Execution Engine is assumed to exist as part of this implementation.

## 1. Outcome and scope

The resource-management subsystem has **four cooperating, separately testable responsibilities**:

1. **Discovery and account-scoped resource state:** provider/product/model catalogs, known registrations and entitlements, actual account observations, prices, limits, policy and data freshness.
2. **Advisory planning:** estimate resource needs across a work graph; compare model/harness/environment alternatives; recommend feasible, revisable allocations. Planning does **not** launch.
3. **Independent validation and mandatory admission for controlled launch paths:** recheck proposed schedules and current account/host constraints; durably reserve all required meters; issue bounded, revision-bound authorization; launch only via controlled adapters.
4. **Operational accounting and evidence:** collect lifecycle timestamps and usage directly; reconcile forecast/reservations/observed consumption/provider reports; preserve sessions and corrections for future research and future Engine consumers.

These responsibilities may initially share one small implementation and database. The separation is conceptual and at the API/event boundary, not an instruction to deploy four services. The orchestration client consumes compact, structured state rather than other agents' conversation histories. The planned Engine's Work Unit, Kernel and Observer retain distinct identities.

**Non-goals for the next bounded slice:** an optimizer choice or global auto-dispatcher, new universal ontology-review gates, a general model-intelligence benchmark, broad provider authentication, production-billing claims, or replacing Paseo's live-conversation and coordination roadmap.

## 2. Authority, sources and supersession

### Authority rule

Canonical ASES documents govern existing method and operator authority. This document records later operator decisions about the *resource-solver research direction* and flags conflicts with earlier provisional design notes; a later chat or research note does not silently amend unrelated canonical policy. Completed experiments establish only their tested claims. Draft testing/ontology proposals and divergent research branches do not become active requirements by being referenced.

| ID | Decision or correction | Earlier position | Reconciled position / authority |
| --- | --- | --- | --- |
| D01 | Planning versus dispatch | October 31 Paseo roadmap describes an **advisory** calculator, no automatic launches | Preserve advisory planner; add separate mandatory authorization/admission interface for **supported controlled launch routes** (later operator direction, Nov 2). Neither planner nor API autonomously launches unrelated work. |
| D02 | Startup/refresh cadence | Broad initial daily catalog refresh, then every orchestrator startup considered | Mechanical provider-specific polling with TTLs and event triggers. First session of a day establishes or validates shared baseline as necessary; later sessions use shared state plus actual usage and targeted refresh. **Not a universal once/day cap or mandatory full sweep per session.** |
| D03 | Accounting authority | Simple estimated-versus-spent ledger | Forecast, reservation, execution, local observation, provider report, billing liability and final settlement are separate. Actual overrun **must be recorded even if it exceeds authorization**; overrun is a violation/exposure, not an observation to reject. |
| D04 | Model/resource separation | Early provider surveys sometimes coupled CLI/model access and compute | Models and inference allowances, harnesses, environments, storage, and their independently billed meters are distinct. Real job may debit several products/accounts concurrently. |
| D05 | Uncertain free services | Published free listing sometimes treated as guaranteed capacity | Registered account, published free tier, verified credential, remaining entitlement, and *current availability* are distinct. NVIDIA/AI Studio free model capacity may be opaque; OpenCode catalog and claimed unlimited models must not imply guaranteed throughput or no throttling. |
| D06 | Free storage baseline | TeraBox 1 TB headline previously counted as enduring free capacity | Treat advertised 1 TB as temporary; 10 GB documented baseline in current account-enumeration discussion, subject to account confirmation and changed terms. Promotional capacity separately expires. |
| D07 | CPU and environment constraints | Some older schedulers treat per-job CPU demand as exclusive hard per-tick reservation | Shared CPU contention can be permitted and affects predicted speed; enforce actual memory/storage safety, supported configurations, genuine concurrency limits and provider hard caps. Earlier 60 green SQLite tests of additive CPU do not validate the corrected model. |
| D08 | Technology selection | Some earlier sequencing suggested Pumpkin-first or Python reference gate | No optimizer selected (see Solver Selection Correction). Production safety-critical logic should prefer memory-safe/type-safe code, Rust being the research recommendation; Python prototypes are references, not admitted controllers. |
| D09 | Observer ownership | Some research docs refer to future Observer telemetry | **Observer does not exist.** Solver collects its own usage/timestamps/lifecycle events now, through modules whose streams can later move to or be read by Observer. |
| D10 | Evidence scope | Testing proposal emphasizes CI results | Preserve **all controlled sessions, launch failures, provider checks and reconciliation runs**. CI is one specialization. Archive upload, hash verification and successful recovery are different claims. |
| D11 | Model capability research | Allocation may benefit from model quality observations | Capability harness/MQI is an **independent EDASES branch**; the solver may consume qualified capability findings, and work sessions may emit incidental evidence to it, but the solver does not benchmark model intelligence. |
| D12 | Work Unit semantics | Some informal discussions use “work unit” for an arbitrary task | Reserve **Work Unit** for its named future Engine component; solver uses work graph, stage, job, attempt, agent session and provider resource with explicit links. |
| D13 | Shared resource ownership | Free tiers considered by provider name | Every entitlement/claim is bound to an account, payer, product, meter, unit, period, region/plan where material and authorized project scope. No implicit cross-account borrowing or quota substitution. |
| D14 | Assurance adoption | Testing, debugging and two ontology reviewer roles proposed | Reuse claim/evidence distinction and cheap discriminating tests. Specialist reviews are selective **experimental** operations; no new automatic global reviewer gate adopted. |

**Historical rationale to retain:** The VPS shopping problem evolved into whole-work-graph planning because nominal vCPU/RAM price omitted CPU usage policy, recoverability, cold-start, concurrent agent interference, quotas and external execution options. Paseo remains a provisional management/coordination surface; neither account discovery nor admission semantics should depend on its implementation.

## 3. Minimal conceptual glossary / identity boundaries

| Concept | Meaning and critical exclusion |
| --- | --- |
| Provider / product / execution surface | Company and specific billed or offered capability; a Codespace, Actions runner, managed coding task, Worker and storage bucket are not interchangeable machines. |
| Account / payer / principal | The particular registered identity and billing owner with access/role; **not** merely an API key or a general provider name. Project permissions and permitted borrowing are explicit. |
| Credential / route | Authenticated means of accessing an API/model/launcher, with scopes and account binding; a working key does not prove remaining allowance or model capacity. |
| Published contract / entitlement / observation | Advertised offer; account-applicable rights; and time-stamped actual reported balance/usage/capacity. Each has separate provenance and freshness. |
| Meter / funding | Non-fungible dimension such as core-hours, GB-month, token requests, CPU milliseconds or currency, with product, account, period, reset/expiry and prepaid/postpaid/free/subscription semantics. |
| Model / harness / environment | Inference endpoint and capabilities; agent CLI/framework; physical/managed execution location. Some products bundle dimensions; model them explicitly rather than merging categories. |
| Work graph / stage / job / attempt | Planned dependency graph; bounded placement step; authorized job; specific launch/retry execution. Attempts can be multiple per job and need stable correlation IDs. |
| Agent session / provider resource | Actual conversation/process or provisioned runtime; neither necessarily maps one-to-one onto jobs. They can outlive or be shared across them. |
| Forecast | **Pre-execution** prediction with estimator, assumptions, unit, uncertainty and snapshot revision; never backfilled from actual results without a retrospective label. |
| Reservation / authorization / acknowledgement | Transactionally allocated capacity; bounded permission for specified launch and risk; orchestrator's acknowledgement of the specific revision. None proves execution occurred or provider billing settled. |
| Lifecycle observation / usage | Instrumented timestamps or quantities, source and confidence; distinguish environment allocated/running/billable time, agent active time, waiting time and multiple concurrent activities. |
| Provider report / final settlement | Provider's usage or balance statement versus definitive charge/credit movement where reported. Reports can be aggregate, delayed, revised or unmatched to a job. |
| Reconciliation / correction / decision | Numerical attribution and discrepancy; appended evidence-backed amendment; separate authorized action on allocation or spending. Never rewrite original observations. |
| Archive evidence | Original safe-to-retain outputs, hashes, manifest, storage location, verification and recovery outcomes, separate from job success. |

**No universal `success` or `spent` status.** Represent admission state, execution status, individual observation/claim qualification, billing/settlement status, archive state and authorized decision as *different typed dimensions*. The P6 evidence vocabulary is a relevant **experimental comparator**, not the final solver schema.

## 4. Registry and refresh model

### Three independently sourced planes

1. **Provider terms and catalog:** models, hardware SKUs/configurations, published prices and limits, expiry/reset/overage behavior, official source URL, retrieval time, digest and parser revision.
2. **Account-specific observations:** account tier, enabled product, credential working status, subscription state, actual visible quota/balance, billing owner, reporting period, freshness and API authority.
3. **Execution and reconciliation:** job/attempt/provider-resource IDs, forecasts, reservations, real lifecycle events, local measurements, provider usage/settlement, external unattributed consumption, corrections and evidence.

Never record a research candidate that might be registered by Google SSO as an *existing account*. Operator-reported registrations are evidence of registration, not proof that each product is activated or has unused free credit. Store personally identifying login addresses, credentials, private billing details and live account inventory in an appropriately restricted registry; public ASES documentation should contain only redacted/symbolic account IDs and architectural rules.

### Monitoring policy

- **Passive scheduled discovery:** model catalogs, published terms, prices and promotional changes, using provider-supported endpoints/changelogs; OpenCode free-model catalog is a motivating example.
- **Session preflight:** make the latest sufficiently fresh scoped snapshot accessible mechanically; when needed, first session establishes a shared baseline with bounded, concurrent provider probes. Later sessions consume and update the same state; a session is never allowed to assume an earlier reservation remains available.
- **Account reconciliation:** where provider APIs support it, poll usage/balance/activity at a provider-specific economic interval; catch usage outside ASES. When only aggregate/delayed reporting exists, label unattributed changes and avoid fabricated per-job allocation.
- **Event-driven refresh:** quota exhaustion, stale contract, model withdrawn, unexpected price/usage, reset/expiry, provider outage, material snapshot revision or new external work may trigger narrower checks.
- **Opaque limits:** record actual successful/failed requests and any rate-limit hints. Missing quota headers do not prove unlimited usage or reveal reset times. An unlimited-advertised free model still may be unavailable.
- **Failure semantics:** failed catalog fetch marks old catalog stale; never turn it into an empty provider. No-provider-data is unknown, never zero. Unverified potentially paid usage is blocked unless an explicit bounded spending authorization applies. Conditional free-only routes are governed by demonstrated non-chargeability and risk policy, not invented quotas.

Polling frequencies, TTLs, jitter and reporting latency are **per-provider facts/decisions**. A full provider sweep on every session is not required, but a versioned acknowledgement and immediate dispatch-time admission are.

## 5. Planning, admission and execution lifecycle (contract candidate)

The existing three gates remain distinct:

1. **Input preflight:** validate typed work graph, provider/account/entitlement snapshots, units, policy, forecast and source revisions.
2. **Independent candidate acceptance:** accept/reject a proposed plan using authoritative input and independent feasibility checks, not the optimizer's own assertions. The planner remains advisory.
3. **Dispatch-time admission:** atomically recheck current hard constraints and all dependent meters/reservations, then durably record authorization before the controlled launch.

The lifecycle has **orthogonal states**, not one overloaded linear state:

- **Planning:** proposed -> quoted -> candidate validated/rejected -> selected; preserve rejected alternatives when useful.
- **Admission:** requested -> reserved + durable authorization (or blocked) -> acknowledged specific version -> launch permitted/expired/revoked. A meaningful subsequent change requires revalidation; acknowledgement cannot override a failed admission.
- **Execution:** launch requested -> provisioning -> running/blocked/interrupted -> completed/failed/cancelled/unknown; provider resource may continue billing after agent work ends.
- **Accounting:** estimated -> observed partially -> provider reported (possibly delayed/aggregate) -> reconciled/disputed/unknown; later adjustments append corrections.
- **Evidence:** captured -> uploaded -> digest verified -> restore verified; each step independently observable.

For retries, cancellations and crashes, keep `job_id`, `attempt_id`, `reservation_id`, `authorization_id`, external provider operation ID and idempotency key distinct. **ACK must follow durable commit**, and crash/replay recovery must query or reconcile an uncertain external launch instead of blindly launching a duplicate. Independent controllers must not be able to allocate the same reservation. Existing reservations and active work need explicit policy when a catalog/entitlement changes.

Enforcement can be claimed **only** for supported launch adapters whose credentials/permissions prevent a bypass. Orchestrators should hold read access and limited launch tokens, not unrestricted account provisioning or spending credentials. Unsupported routes remain external observations, not falsely controlled jobs.

### Thin API, deliberately independent of Paseo

| Operation (illustrative) | Contract purpose |
| --- | --- |
| `resources.snapshot` | Read scoped provider/account/meter facts, validity, source and revision, with a compact changed-since view |
| `plan.quote` | Register pre-run estimates and proposed work graph; offer alternative eligible plans without dispatch |
| `plan.validate` | Independent feasibility result and falsifiable reason codes |
| `allocation.reserve` | Atomic multi-meter reservation against pinned current revisions, budget and account policy; idempotent request |
| `execution.authorize` | Bind an acknowledged resource-state revision to a specific approved attempt/launcher, expiry and hard bounds |
| `execution.launch` | Controlled adapter initiates **only** the authorized attempt and returns correlation/provider IDs |
| `execution.status` | Compact state, known progress, incurred/pending usage and exceptions; no agent-chat replay |
| `events.ingest` / `execution.finalize` | Authenticated lifecycle/usage observations and terminal attempt result; event idempotency |
| `resources.reconcile` | Pull provider balance/usage/settlement if possible; attribute deltas, update availability and flag unexplained usage |
| `reconciliation.correct` | Append evidenced/manual correction; separate elevated authority for spending-cap or safety override |
| `evidence.references` | Return source/derived archive manifests, hashes, access class and recovery status |

This is a logical contract, not an assertion that a particular transport or executable API exists. Avoid an always-on LLM agent or unnecessary daemon to operate it.

### Availability and period semantics

The source account snapshot plus observations, pending reservations and actual executions define available future capacity. **Avoid double counting:** provider reports may already include local jobs; reconcile using reporting windows/watermarks, not blindly subtract both provider-reported consumption and the same internal debits. A single execution can span quota reset boundaries or consume multiple non-fungible units. Model those splits explicitly.

Provider-billed usage is not restricted to the reserved amount. When observed use exceeds reservation, preserve the real observation, mark budget/authorization violation and potential financial liability, restrict further commitments as policy requires, and report the exception. Financial settlement cannot be inferred from a local `finalize` acknowledgement.

A free-only task must still pass authorization even if it has **zero chargeable allowance claims**; earlier Python prototypes reject such plans because they require a positive claim, which is not acceptable as the production abstraction.

## 6. Forecast, consumption and evidence requirements

Capture before launch: task/job/attempt identity; model, harness, environment, selected configuration, account/payer, provider contract revision; forecast runtime, agent work, memory, credits/tokens, budget and assumptions; authorized reservations and snapshot digest.

Capture during/after: timestamps for request, provisioning, availability, agent start/stop, pauses, retries, timeout, environment termination; model response usage, CPU/RAM observations when cheap, provider execution ID, usage and charging windows; provider-account usage deltas; failure classification. Distinguish machine lifetime from billable runtime and from parallel-agent activity. Derive intervals using compatible monotonic/UTC clock sources with uncertainty where necessary.

**Illustrative Codespaces case:** forecast 45 wall minutes; observed environment running 60 minutes; measured agent active 30 minutes. Preserve three separate facts plus any verified provider core-hour meter (machine size and pricing matter). The remaining 30 minutes are **unclassified** unless evidence supports a provider fault, setup delay, idle time or other cause. If allowance consumption exceeds the reservation, do not reject the evidence; restrict availability and reconcile.

Every controlled session (including failed starts, skips, partial/cancelled attempts and provider checks) has a stable indexed record. Preserve raw safe evidence and derived accounts as independent, append-oriented artifacts, compressed where useful (e.g. zstd for text/JSON), with manifests, access controls and hashes. An uploaded archive is not necessarily complete or recoverable. Provider-native CI retention is not the durable archive. Redact secrets/private content and retain private records in restricted storage; do not post full transcripts or personal account credentials in a public repo.

**Separate evidence consumers:** resource allocator uses resource usage and constraints; EDASES capability research may consume appropriately qualified task outcomes; the future Observer may consume or assume selected lifecycle streams. None should silently rewrite another stream's source observations.

## 7. Requirements-to-evidence matrix (existing tests are not production proof)

| Requirement / falsifier | Existing evidence (scope) | Still unverified / cheapest next discriminating check |
| --- | --- | --- |
| R01 Typed account/meter identity and no unit/account substitution | Allowance ledger v1 and admission v2 local tests; provider manifest v0 committed with 18 tests initially reported **not run** | Clean-checkout registry tests; negative/positive cases for borrower, account, payer, period, unit, reset and explicit free-only admission |
| R02 Independent offline plan acceptance | Snapshot gate local suite (22 specific gate tests) and small synthetic exact-reference runs; broader 104 local test methods across multiple suites | Test authoritative schema with correct shared CPU policy and independent validator; no inference from synthetic feasibility to actual provider balances |
| R03 Multi-meter atomic reservation with no double allocation | Single-process Python locks; P1/P3 targeted controls; P4 in-memory Rust/Haskell contention trials | Cross-process durable transaction with concurrent attempts, real restart, version drift and overlapping meters; preserve valid neighboring admissions |
| R04 Authorize only after durable commit; replay cannot double-launch | P5 Rust/Haskell controlled journal faults detected by checkpoint-qualified SIGKILL; P7 programmatically reconstructed original P5 results | Integrate actual reservation -> ACK -> launch adapter, test kill at each boundary and uncertain external launch; existing tests are **not** live gateway proof |
| R05 Forecast versus actual, including 45/30, 45/60 and 60/30 | Proposed event/accounting contracts; no complete end-to-end provider slice verified | Synthetic provider lifecycle with measured time and explicit overrun, correct release or liability, period crossing, missed stop and idle resource |
| R06 External/out-of-band usage and delayed provider data | Control-plane design proposes idempotent provider reports and cursors | Synthetic aggregate-only and delayed usage plus duplicate/out-of-order provider reports; ensure no double subtraction or fabricated attribution |
| R07 Opaque model limits and changing catalogs | Operator-reported working AI Studio/NVIDIA keys; OpenCode free catalog changes, availability failures | Passive catalog diff; mock throttle/no-headers vs unlimited-advertised; avoid expensive inference probes or inferred reset times |
| R08 Free/prepaid/postpaid/subscription distinctions and no unauthorized paid overage | Funding liability policy; selected P1/P3 paid-authorization mutants | Unknown price, free-to-paid boundary, prepaid depletion, postpaid liability cap, separate model API debit and provider billing uncertainty |
| R09 Existing environment contention and configuration legality | Later shared-CPU correction invalidates older additive-CPU assumption | Co-running CPU jobs accepted where safe, memory-heavy invalid neighbor blocked, supported/unsupported resize boundary |
| R10 Record separate outcome/interpretation/decision and archive claims | P6: three legitimate event cases accepted and 16 invalid controls rejected; P7 prepared ontology packets but **no independent-model reviewer result** | Apply typed event semantics to a real/second execution source; verify actor authority and source provenance separately |
| R11 Preserve and restore evidence even on failed/interrupted jobs | P5/P6 original CI ZIPs retained and hashed; P7 sensitive original archived privately; some P1/P3 evidence partial | Simulated archive write-after-index, corruption, lost upload and recovery; distinguish incomplete archive from job outcome |
| R12 Prevent bypass of authorized launch boundary | Thin API and permission isolation are operator-approved design intent | Mock direct-credential bypass: show refusal/absence of permission, verify controlled adapter honors max liability/stop rights and cannot create extra agents |

**Method discipline:** Freeze requirement, falsifier, and test assumptions before testing. Use the cheapest test that distinguishes a consequential defect, with valid neighboring controls and source-first results. A passing mutation suite does not automatically establish a correct oracle or live-provider guarantee. Keep original FAILED/RED observations and later corrected interpretations separately. The P1–P7 Rust/Haskell/testing-assurance branch is **experimental and unmerged** relative to main as reviewed; P7's independent-model ontology reviewer evaluation is **NOT_RUN** (its mechanical benchmark preparation did run). Do not silently promote its proposed reviewer roles.

## 8. Smallest useful next experiment and acceptance

**Proposed next slice:** a synthetic, Codespaces-like provider with at least two metered dimensions (machine core time and storage), separate optional inference route, symbolic account IDs and a controlled mock launcher. Reuse the existing typed provider registry, independent feasibility gate and allowance research as comparators; do not make live billable calls.

1. Freeze exactly the `quote -> validate -> reserve -> acknowledge/authorize -> launch -> collect -> finalize -> reconcile -> archive` interface and pre-run predictions.
2. Test five core scenarios: **45 estimated / 30 actual**, **45 / 60 overrun**, **60 environment / 30 agent-active**, **two competing reservations**, and **crash/replay between durable commit, ACK and external launch**.
3. Add focused controls for unknown/opaque free entitlement, conflicting account/period, out-of-band provider consumption, delayed aggregate reports, and an archive with missing or corrupted data.
4. Run positive and negative neighbors, and targeted red/green/mutations only where they distinguish selected high-consequence guards. Measure actual time, memory, I/O and storage overhead of the launcher/accounting path separately from model inference.
5. Retain original run artifacts, exact source revisions, pretest plan, instrument qualifications, resulting failures and uncertainty; expose a concise final status through the thin API.

**Acceptance to move beyond synthetic slice:** demonstrably no unauthorized controlled launch or silent double reservation; ACK follows durable state; real overruns recorded rather than censored; correct remaining capacity and liability under replay/reporting lag; source/interpretation/decision remain distinct; evidence loss is detectable; an independent validator rejects invalid plans without rejecting valid neighbors. Passing this slice does **not** authorize a production deployment or establish account/provider-specific live guarantees.

## 9. Open questions and next decisions

- Exactly what account-role and cryptographic/credential boundary can make launch bypass infeasible in current Paseo/CLI/VPS routes? Which routes remain outside enforcement?
- Which authoritative actor grants paid-spend caps, cross-account borrowing and manual overrides, and how are approvals authenticated?
- Provider-specific TTL, reporting latency and reset boundary behavior, including a partial-balance report and absent available-balance API.
- How are running jobs drained or cancelled when catalog, price, account permission or quotas change? What stop/teardown evidence confirms billing actually ended?
- What minimal durable state mechanism meets atomicity and recoverability (SQLite WAL is a candidate), without adding an unnecessary resident service?
- Which records belong in public repo vs restricted account/project archive; backup, restore, retention and aggregate storage economics?
- What tests on actual supported provider routes justify advancing from synthetic admission to bounded real execution?
- How should forecast uncertainty and agent activity estimation be calibrated without conflating task capability assessment with resource accounting?

## 10. Source map and explicit limits

**Main branch, research and reference:**
- [Provider registry control plane](Provider%20Registry%20Control%20Plane%20and%20Usage%20Reconciliation%202026-11-01.md), [provider onboarding/reality model](Provider%20Onboarding%20and%20Reality%20Model%20Audit%202026-11-01.md), [provider funding/liability correction](Provider%20Funding%20Liability%20and%20Language%20Policy%20Correction%202026-11-01.md).
- [Independent feasibility gate](Independent%20Feasibility%20Gate%20Requirements%202026-11-01.md), [solver selection correction](Solver%20Selection%20Correction%202026-11-01.md), [admission-gate experimental audit](Resource%20Solver%20Admission%20Gate%20and%20Exact%20Reference%20Audit%202026-11-01.md), [shared CPU/configuration correction](Provisional%20Environment%20Configuration%20and%20Shared%20Resource%20Model%202026-11-01.md).
- [Paseo conversation-first integration](Paseo%20Live%20Conversations%20and%20Resource%20Planning%202026-10-31.md), [task execution/MQI research](Task%20Execution%20Evidence%20and%20Model%20Quality%20Index%20Integration%202026-11-01.md), and [Account Enumeration Chat feedback](../proposals/2026-11-02-testing-debugging-ontology/ases-account-enumeration-chat-2026-11-02.md).
- [Parallel Resource Solver Chat commentary](../proposals/2026-11-02-testing-debugging-ontology/resource-solver-chat-response-2026-11-02.md), for the adjacent P1–P5 discussion.

**Experimental branch, not canonical:** [P1–P7 pilot overview](https://github.com/rock-solid-sites/ASES/blob/research/rust-haskell-admission-2026-11-01/research/testing-assurance-pilot/README.md), [P6 evidence semantics](https://github.com/rock-solid-sites/ASES/blob/research/rust-haskell-admission-2026-11-01/research/testing-assurance-pilot/P6-RESULTS-2026-11-02.md), and [P7 source-first/ontology benchmark preparation](https://github.com/rock-solid-sites/ASES/blob/research/rust-haskell-admission-2026-11-01/research/testing-assurance-pilot/P7-RESULTS-2026-11-02.md).

**Methodology proposals, not adopted:** [November 2 testing/debugging/ontology bundle](https://github.com/rock-solid-sites/ASES/tree/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology).

**Evidence classification:** dated user statements establish design intent and reported account observations; repository documents establish documented research assertions; experimental artifacts establish only executed outcomes within stated scope; no newly executed provider integration, live account reconciliation, code test, artifact-restoration experiment or production authorization is claimed by this reconciliation.
