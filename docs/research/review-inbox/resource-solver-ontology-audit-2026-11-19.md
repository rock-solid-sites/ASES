---
title: Resource Solver Ontology and Tool-Routing Boundary Audit — 2026-11-19
program: EDASES
layer: Research
document_type: Research Finding
status: Draft
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/research/Resource Solver Specification Reconciliation 2026-11-02.md
  - docs/research/Provider Registry Control Plane and Usage Reconciliation 2026-11-01.md
  - docs/research/Identifier-First Tool Calling.md
  - research/capability-schema-validation/report.md
  - docs/architecture/Execution Engine Vision.md
related_documents:
  - docs/research/Resource Solver Admission Gate and Exact Reference Audit 2026-11-01.md
  - docs/research/Provisional Environment Configuration and Shared Resource Model 2026-11-01.md
  - docs/research/Task Execution Evidence and Model Quality Index Integration 2026-11-01.md
  - docs/research/registry/AI Capability Registry Specification.md
  - docs/roles/Ontology-Reviewer.md
  - docs/research/review-inbox/resource-solver-ontology-independent-review-brief-2026-11-19.md
consumed_by:
  - independent exploratory architecture/ontology review
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-19
---

# Resource Solver ontology and tool-routing boundary audit

**Status:** Research finding / reviewer input, not an amended ontology, approved Engine architecture, tool migration plan, or production admission claim.

**Source baseline:** `rock-solid-sites/ASES` main at commit [`cb27e4de21142c36c634f9130c9591b7912c3dec`](https://github.com/rock-solid-sites/ASES/commit/cb27e4de21142c36c634f9130c9591b7912c3dec), read 2026-11-19. The separately retained P7 research branch is pinned to [`f40da189237896a146ad5913ddbd1aca13e488ed`](https://github.com/rock-solid-sites/ASES/commit/f40da189237896a146ad5913ddbd1aca13e488ed). Gitea CLI 2.0 is a new **vendor-reported motivation**, not validation of an ASES design. No repository tests or live provider executions were run for this document.

## 1. Question and scope

Does the existing ASES Resource Solver ontology represent all important entities, relationships, constraints and costs involved in selecting (a) hosted versus independent execution; (b) model, harness and environment; and (c) CLI, MCP, direct API, browser or deterministic script pathways for the same Work Unit outcome?

This audit compares documented *concepts*, not a claim of deployed control. Explicitly separate: existing canonical methodology/vision; provisional solver specification; evidence from limited prototypes; and hypotheses requiring review.

## 2. What already exists — do not reinvent it

| Area | Source-backed coverage | Qualification |
| --- | --- | --- |
| Provider/product/account/payer/principal | Solver Spec §§2–4, Provider Registry Control Plane | Published contract, entitlement and live observation are different planes; no implicit cross-account quota borrowing |
| Model/harness/environment | Solver Spec D04, glossary | A job may consume multiple independently billed products/meters; a harness is not a model or compute entitlement |
| Forecast/reservation/authorization/usage/settlement | Solver Spec §§3, 5–7 | Distinct identity, authority and time; no single overloaded spent/success field |
| Independent admission and revision-bound launch | Solver Spec §5, Admission Gate Audit | Controlled adapter requirement is design intent, not deployed proof; Python gate is process-local, lacks durable CAS, and rejects zero-claim/free-only plans |
| Shared CPU and machine configuration | Provisional Environment Configuration | CPU contention influences speed rather than implying exclusive reservation; RAM/storage and genuine provider caps remain hard safety checks |
| Context as resource | Execution Engine Vision, Context Management | The Engine owns context construction/recovery at methodology level; solver may quote resource implications but must not silently appropriate Engine ownership |
| Capability evidence | AI Capability Registry Specification | EDASES describes observed capabilities, independent from recommendations and allocations |
| Minimal model-visible tool description | Identifier-First Tool Calling; Capability/Schema Validation | Stable IDs, short parameter shapes, runtime validation and a preselected surface already studied |
| Tool authority and role restrictions | Paseo Role Capability Matrix; agent-tooling-and-permission-enforcement-reviewed; capability-schema Test D | Role/capability grants differ from validation, connector authentication, and runtime permission enforcement |
| Distinct evidence streams | Task Execution Evidence/MQI; Solver Spec §6 | Resource usage, verified work quality, capability research and future Observer must not be equated |

**Contradiction warning:** Solver Spec explicitly says the Observer does not yet exist, the named Engine Work Unit is future-facing, and the current solver uses work graph/stage/job/attempt. Do not describe any of these as implemented control-plane services. The ontology-review specialist role is `Proposed` (Ontology-Reviewer.md v0.2-draft); P7 prepared clean packets but did **not** run the proposed independent-model benchmark.

## 3. Gaps and integration questions (hypotheses, not new canonical entities)

### F1 — Tool pathway is inadequately connected to resource planning (high priority; evidence-based documentary gap)

Current solver glossary has `credential/route` for access and separates model/harness/environment, but does not give a worked, typed relation among **requested semantic operation**, **capability**, **agent-visible interface/description**, **transport** (CLI/MCP/API/browser), **connector/client process**, **underlying provider operation**, and **account-authorized credentials**. The identifier-first research already introduces operation IDs and authoritative schemas; it may supply the missing interface instead of a new component. **Reviewer task:** identify minimal cross-references/contracts; reject any unnecessary duplicate gateway or universal abstraction.

### F2 — Information movement and context costs are not specified as multi-stage meters (high; evidence-based documentary gap)

Solver records tokens and cost observations, while Engine Vision owns context management and Identifier-First explores schema-token overhead. Missing end-to-end accounting relationships: tool-definition exposure, operation arguments, raw result size, filtered result, tokens actually admitted to context, cached input, repeated retrieval, external storage, evidence retention, and quality loss/retry. These are **not interchangeable quantities**. A 73.3% reduction in a description block is not 73.3% cheaper Work Units. Distinguish the source payload from what the model saw and from what billing measured.

### F3 — Objective function and constrained choice are underspecified for mixed resource units (high; candidate extension)

Cash liability, subscription allowance scarcity, rate limits, time-to-result, latency distribution, reliability, quality, human intervention, context occupancy, operator risk and privacy cannot all be converted into a single reliable dollar amount. Distinguish (i) hard feasibility; (ii) vector of observed/estimated costs and service-quality measures; (iii) operator-specified priority/constraints; (iv) uncertain opportunity cost as a modeling assumption, not provider fact. Account reset/expiration means the value of unused capacity is time-dependent. Propose no fixed shadow price without evidence.

### F4 — Workflow economics require relationships across operations (medium-high; gap in combined model)

Per-call selection is not necessarily globally optimal. Batching and reusable environment startup can reduce cost; bundling can increase blast radius, latency or rework. An Actions trigger, hosted Actions runner, external runner, Codespace, disposable VM, scheduled service and agent inference route are **different components of a workflow**, not mutually exclusive provider labels. Record triggering/reporting separately from the actual placement of each stage; model setup/teardown, queue, cold-start, network and data locality. Solver need not decide every routine command: deterministic policy may be cheaper than replanning.

### F5 — Capability correctness and information sufficiency require separate assurance (high; research gap)

The capability-schema report's **description-only** simulation used 14 operations, a fixed 22-task corpus, 63 valid calls per variant. Full-scheme description 7,023 tokens; smallest 1,873 (73.3% reduction), 63/63 selection, 62/63 initial argument correctness; it explicitly called **no live LLM**. Test C found output-schema validation necessary; Test D validated separate absent/denied/invalid-argument pathways in the harness. Need distinguish operation routing correctness, result validity, sufficiency of compact evidence, adversarial/prompt-injected tool outputs, and final Work Unit quality. Gitea CLI 2.0 vendor estimates (failed logs ~46,800 to ~11,600 tokens; piped commits ~2,140 to ~1,244) are different scope/baselines; do not compare them as controlled MCP-versus-CLI evidence.

### F6 — Security and data-placement constraints must survive optimization (critical; established invariant + new route audit)

The same semantic capability through a cheaper CLI is not equivalent if it changes privilege, principal, network trust, secret exposure, auditability or data residency. An authenticated connection does not imply authorization to cross project/account boundaries. Enforce independent authority at an execution boundary, not via a model-selected route, a tool description or a prompt. Keep public ASES research and private MbD-Record material separated; never copy private account inventory or secret-bearing raw outputs into public review artifacts. Shared server plus privileged runner can turn a compute optimization into a repository/credential compromise.

### F7 — Operational readiness, freshness and failure-path cost remain underdetermined (medium-high)

Provider catalog availability, currently callable capability, quota balance, reported usage, funding liability and observed request success must remain separate. A dormant stdio MCP process, a long-lived HTTP connector, an on-demand CLI, a browser session and a resident VM have different lifetime costs. Failure/retry may trigger repeated tool calls, model tokens and billable resources; stale output schemas or hidden rate limiting can make an ostensibly cheap route more expensive. Define `unknown`, `stale`, `unavailable`, `denied` and `zero` distinctly.

### F8 — No evidence yet that replacing MCPs is advantageous across our current surfaces (high; explicit non-finding)

Earlier identifier-first research found both tool-description overhead and connector lifecycle overhead but treated them separately; later capability-schema work intentionally retired broader lazy-MCP lifecycle experiments from its scope. There is no verified, whole-workload comparison of the user's connected ChatGPT connectors, autonomous cloud CLIs, and direct service APIs under equivalent identity/permissions. Some host connections cannot be reproduced in an agent sandbox simply by exposing a CLI. **Candidate direction:** unify the model-facing semantic operation contract where possible, retain MCP/CLI/API/browser adapters as underlying routes, and let authorized planner policy choose only among functionally/security-equivalent paths. This is a question to review, not a mandate to build a gateway.

## 4. Candidate minimal ontology crosswalk (request for falsification, not adopted schema)

- **Intent / Work graph / Stage / Job / Attempt:** what outcome must be produced, what dependencies hold, what is authorized; do not rename future Engine Work Unit.
- **Semantic operation / Capability / Versioned schema:** what a task can request, what inputs and outputs are valid; capability's observed competence remains in the evidence registry.
- **Tool presentation / Adapter / Transport / Session:** what the model sees, what executes the operation, how it communicates and what process/session lifetime it incurs.
- **Provider / Product / Configuration / Account / Principal / Credential / Entitlement / Meter:** whose rights and costs apply to each underlying call or runtime interval.
- **Resource observation / Forecast / Reservation / Authorization / Actual usage / Provider report / Settlement:** separate measurement and permission stages.
- **Information artifact / Transformation / Retrieval / Context inclusion / Evidence reference:** distinguish stored original, filtered data, exposed data, cached/reused data and verified result.
- **Policy / Role / Permission / Risk / Trust boundary:** authorization must be validated independently of optimizer preference and transport.
- **Outcome / Validation / Quality evidence / Failure / Retry:** distinguish successful API call, successful job and verified useful engineering result.

**Question to reviewers:** Which are already existing identities to reference, which should be attributes/relationships rather than objects, and what is missing? Reject redundant entities aggressively.

## 5. Threat and counterexample catalogue for adversarial evaluation

1. `gh` lists a GitHub Actions job, while a self-hosted runner performs the work and an external API bills model tokens: does the model charge the right separate accounts and meters?
2. A free-only task has zero allowance claims but requires safe RAM and credentials: is it still eligible for admission? Current Python prototype rejects it.
3. Two independent job controllers race against the same free storage and paid model allowance: can either reuse a stale reservation/revision?
4. CLI filtering hides the actual failure line; model retries three times, increasing total token and compute expense despite a smaller first result.
5. A compact schema exposes an operation name but omits a required nested enum; runtime rejects it and output schema changes after a provider upgrade.
6. Source repository is public, retrieved records and model account are private: cheapest execution route would disclose source/prompt/data across boundary.
7. Prepaid credit expires tomorrow; a low-priority job might consume it now, while a high-priority job is expected later; compare immediate cash with opportunity cost without inventing probabilities.
8. A provider usage report arrives late and aggregates several accounts/jobs; internal usage must not be subtracted again or falsely attributed.
9. A cloud VM remains billable after the agent exits; Actions workflow has already finished; reconcile environment lifetime and job outcome independently.
10. A task can be done by a single deterministic batch call or several model-guided MCP calls; determine which quantities are actually comparable and what correctness evidence is necessary.

## 6. Preliminary judgment and safe next action

**Judgment:** No wholesale replacement of the Resource Solver ontology is warranted from the documents inspected. The most plausible missing layer is an explicit **crosswalk between semantic operations/tool pathways and existing resource, account, context and evidence models**. We should prefer reuse of Identifier-First and Capability/Schema research over a novel generic gateway. Neither alternative warrants implementation before review.

**Not established:** deployed universal capability API, robust multi-process admission, verified real provider billing, automatic model-grade token accounting, live-model reduction in end-to-end cost, a functional Observer, or proven MCP replacement.

**For independent review:** Send the separate neutral reviewer brief `resource-solver-ontology-independent-review-brief-2026-11-19.md` *without* this diagnosis; pin the source commit, isolate model-family outputs, enforce read-only scope, capture falsifiers and corrections. Do not present this audit's suspected gaps or P7 scoring material as prior reviewer conclusions.

## 7. Source index

Main branch at pinned `cb27e4de` (all under `rock-solid-sites/ASES`):
- [Solver reconciliation](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Resource%20Solver%20Specification%20Reconciliation%202026-11-02.md)
- [Provider control plane](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Provider%20Registry%20Control%20Plane%20and%20Usage%20Reconciliation%202026-11-01.md)
- [Admission gate audit](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Resource%20Solver%20Admission%20Gate%20and%20Exact%20Reference%20Audit%202026-11-01.md)
- [Shared resource correction](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Provisional%20Environment%20Configuration%20and%20Shared%20Resource%20Model%202026-11-01.md)
- [Identifier-first tool calling](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Identifier-First%20Tool%20Calling.md)
- [Capability/schema report](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/research/capability-schema-validation/report.md)
- [Capability registry](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/registry/AI%20Capability%20Registry%20Specification.md)
- [Execution Engine Vision](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/architecture/Execution%20Engine%20Vision.md)
- [Ontology Reviewer role (proposed)](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/roles/Ontology-Reviewer.md)
- [Task execution evidence](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Task%20Execution%20Evidence%20and%20Model%20Quality%20Index%20Integration%202026-11-01.md)
- [P7 actual status (separate research branch)](https://github.com/rock-solid-sites/ASES/blob/f40da189237896a146ad5913ddbd1aca13e488ed/research/testing-assurance-pilot/P7-RESULTS-2026-11-02.md)
- [Gitea CLI 2.0 vendor claims](https://blog.gitea.com/release-of-gitea-cli-2.0.0/)
