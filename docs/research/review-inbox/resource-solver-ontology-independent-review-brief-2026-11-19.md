---
title: Independent Review Brief — Resource Solver Ontology and Tool Pathways — 2026-11-19
program: EDASES
layer: Research
document_type: Review Brief
status: Draft
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/research/Resource Solver Specification Reconciliation 2026-11-02.md
  - docs/research/Identifier-First Tool Calling.md
  - docs/architecture/Execution Engine Vision.md
related_documents:
  - docs/research/Provider Registry Control Plane and Usage Reconciliation 2026-11-01.md
  - research/capability-schema-validation/report.md
consumed_by:
  - independently isolated, read-only exploratory ontology reviewers
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-19
---

# Independent ontology review: Resource Solver, tool pathways, and whole-workflow economics

**Review type:** Exploratory, *pre-build* conceptual review. Not a code implementation request, optimizer benchmark, conformance test on a finished artifact, or method-policy change.

**Source revision to inspect:** [`rock-solid-sites/ASES@cb27e4de21142c36c634f9130c9591b7912c3dec`](https://github.com/rock-solid-sites/ASES/commit/cb27e4de21142c36c634f9130c9591b7912c3dec).

**Do not use:** later review drafts/findings, this review packet's companion audit, reviewer peers' reports, hidden expected answers, other reviewers' verdicts, P7 private scoring data or any raw private account information. A separate orchestration controller should distribute this brief and the pinned source documents without placing the companion audit into reviewer context.

## Objective

Critically evaluate whether the resource-control and surrounding ASES/EDASES ontology can describe, constrain and reason about how agentic software-engineering work is executed across models, harnesses, environments, GitHub Actions, cloud compute, scripts, CLI, MCP, direct API, browser and connected service routes. Consider both their resource economics and the fidelity/security of the work achieved.

The purpose is to discover category errors, contradictory definitions, missing relationships, unnecessary entities, incorrect ownership, unjustified assumptions and latent safety failures. A verdict that the ontology is already sufficient is valid if supported by evidence and counterexamples.

## Baseline documents to read, in order

1. [AGENTS.md — authoritative repository boundaries](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/AGENTS.md); [ORIENTATION.md](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/ORIENTATION.md); [Documentation Standard](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/standards/Documentation%20Standard.md).
2. [Resource Solver Specification Reconciliation](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Resource%20Solver%20Specification%20Reconciliation%202026-11-02.md) — provisional baseline and exclusions.
3. [Provider Registry Control Plane](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Provider%20Registry%20Control%20Plane%20and%20Usage%20Reconciliation%202026-11-01.md); [Provisional Environment / Shared CPU](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Provisional%20Environment%20Configuration%20and%20Shared%20Resource%20Model%202026-11-01.md); [Admission Gate Audit](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Resource%20Solver%20Admission%20Gate%20and%20Exact%20Reference%20Audit%202026-11-01.md).
4. [Identifier-First Tool Calling](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Identifier-First%20Tool%20Calling.md) and [Capability/Schema Validation synthesis](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/research/capability-schema-validation/report.md).
5. [Execution Engine Vision](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/architecture/Execution%20Engine%20Vision.md); [AI Capability Registry Specification](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/registry/AI%20Capability%20Registry%20Specification.md); [Task Execution Evidence / MQI](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Task%20Execution%20Evidence%20and%20Model%20Quality%20Index%20Integration%202026-11-01.md).
6. External motivation only: [Gitea CLI 2.0 announcement (2026-11-18)](https://blog.gitea.com/release-of-gitea-cli-2.0.0/). Treat all vendor token measurements as scoped claims, not proof of a universal replacement architecture.

You may search more **pinned** repository sources as necessary, but cite each addition and distinguish canonical authority from research/proposals/prototypes. P7's ontology-review roles are not adopted merely because a proposed role file exists.

## Questions to investigate independently

- Does the existing ontology have clear, non-overlapping identities for tasks/work graphs, semantic operations, agent-visible capabilities, tools/clients, transports, access routes, model, inference provider, harness, compute environment, trigger, account, credential, quota and evidence?
- Can a job's multiple simultaneous resource charges be described without conflating billing reports, consumption estimates, reservation rights and settlement, especially across subscription allowances, promotional credits, changing rate limits and time boundaries?
- Can it compare GitHub-hosted Actions, external Actions runners, on-demand VMs, long-lived servers and autonomous cloud environments without mistaking a trigger/reporting service for the location in which code actually executes?
- Can it represent how information is retrieved, transformed, shown to a model, cached, reused, stored and verified? Which system should own each responsibility?
- Would a common semantic operation interface across CLI/MCP/API/browser be sound, unnecessary, or harmful? Which parts belong to resource planning, capability selection, runtime validation, authorization, or external-tool integrations?
- Does optimizing on token use, advertised price, apparent free allowance, invocation counts or shortest latency miss important forms of cost or reduce final correctness? Are there important objectives that should not be monetized?
- Does the proposal preserve permissions, isolation, confidentiality, account/payer boundaries, task authority, and independent launch admission even if a cheaper route exists?
- Are repeated, combined, long-running, cancelled, interrupted, or partially successful workflows correctly represented?
- What are the smallest sufficient concepts, relations and invariants? Which apparent ontology additions are actually attributes or policies of existing objects?

These are *domains to inspect*, not preferred findings. Reject flawed premises and propose alternatives when warranted.

## Output contract

Provide a concise, source-linked report with:

1. **Verdict and scope:** Is the existing conceptual model sufficient for the stated goal, sufficient with extensions, or materially mis-specified? Give confidence and WHAT-NOT-TESTED.
2. **Ontology map:** Objects and typed relations as currently defined, each tied to a baseline source and authority.
3. **Falsifiable findings:** Severity, exact conflicting/absent definitions, counterexample, affected invariant, and one minimal correction or open decision. Distinguish a documentary omission from an actual implemented defect.
4. **Redundancy audit:** List tempting new components/terms that overlap existing research or blur Engine/Kernel/Solver/registry boundaries.
5. **Two or more clean neighboring cases** where the current ontology should remain valid, to avoid over-rejection.
6. **Decision requests, not unilateral changes:** Identify only the decisions that need operator approval. Do not rewrite canonical method, propose a new engine module as a foregone conclusion, or implement an adapter.
7. **Evidence discipline:** For every material claim include WHY, WHAT, HOW CERTAIN, WHAT-NOT-TESTED and source/commit. Unknown data remains unknown.

## Review independence and execution constraints

Use a different model family than the artifact-producing family where provenance permits. Isolate each reviewer and withhold peer outputs and the companion audit until all raw reports are preserved. Read-only permission must be enforced by actual execution capabilities, not only prompt instructions. If a reviewer lacks source access, record which documents were not inspected rather than reconstructing their contents. Bound runtime and any paid model consumption before launch; no automatic provider/model substitution or retries. Capture source commit, model identity as established by the launcher, prompt/context digest, usage **if observed**, output and limitation notes; report provider token/cost values as unknown otherwise.

**Review preparation only:** this file does not launch any review and does not authorize spending, repository mutation or methodology promotion.
