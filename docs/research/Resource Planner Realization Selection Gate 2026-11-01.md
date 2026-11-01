---
title: Resource Planner Realization Selection Gate — 2026-11-01
program: EDASES
layer: Research
document_type: Research Finding
status: Draft
authority: Experimental
canonical_repository: edases
depends_on:
  - docs/methodology/Implementation Realization and Assurance Selection Method.md
  - docs/methodology/ASES Bounded Project Build Method.md
  - docs/methodology/State-Model Applicability and Reuse Method.md
related_documents:
  - docs/research/Paseo Resource Planner Parallel Track and Identity Domains 2026-11-01.md
  - docs/research/Paseo Conversation-First Integration Roadmap 2026-10-31.md
  - tools/resource-planner/README.md
last_updated: 2026-11-01
---

# Realization selection gate: ASES resource planner

## Decision status: UNRESOLVED (hold maintained implementation)

The 2026-11-01 experimental calculator was coded in Node.js and strict TypeScript **before** the required language/realization selection procedure. The operator explicitly called out this methodological error. The prototype's language and runtime are **not approved** as the implementation for the future maintained calculator, its persistent ledger, its provider adapters or its security/authority boundary.

Keep \`tools/resource-planner/\` as a **disposable, offline, read-only behavioral experiment** with synthetic inputs and regression examples; it may supply evidence about desired observable behavior but is not the reference architecture, chosen language, production package or authorized execution service. Green unit tests do not waive a realization gate. Do not deploy or extend it into a live account integration until the method below is satisfied.

## Governing canonical methodology

- \`docs/methodology/Implementation Realization and Assurance Selection Method.md\` (2026-10-30): first define falsifiable safety, correctness, security, resource, performance, reliability, recovery and maintainability requirements, then eliminate evidenced failures. **Level A** permits shortest disposable experiments or a bounded small integration/connector using a safety-oriented language set; strict TypeScript is especially appropriate for integration into an existing JavaScript/TypeScript codebase. **Level B** applies to substantive, standalone or multi-component products, persistent state/authority, complex concurrency and novel claims; begin without an approved architecture or language shortlist, conduct an open mechanism search, classify alternatives EXCLUDED/UNRESOLVED/VIABLE from evidence, then choose.
- \`docs/methodology/ASES Bounded Project Build Method.md\` (2026-09-22): establish target/acceptance; search before invention; inspect reuse; necessity-pass every new component; specify behavior and state; select realization; only then implement and verify.
- \`docs/methodology/State-Model Applicability and Reuse Method.md\` (2026-10-30): assess PRIMARY, SUPPLEMENTARY, NOT APPLICABLE or UNRESOLVED state-model value before technology selection. A useful abstract state model is not proof that a real provider stopped billing or isolated credentials.
- \`AGENTS.md\`: policy excludes C, C++, Objective-C, Zig, PHP and other unsafe/manual-memory new standalone code; a narrowly bounded upstream-reuse exception must be justified and cannot remove security guarantees.

## Scope classification

- **Current v0:** A pure, offline assignment evaluator with local JSON fixtures and no cloud credentials, launches or persisted account ledger. It is eligible to remain a **disposable behavioral experiment**, provided its role is explicitly limited to exploratory tests and is not promoted into maintained production code without review.
- **Target system:** a persistent, provider-independent, identity/quotas/credits-aware planner with live observations, versioned plans, multi-stage work graphs and potential Paseo adapters. Identity rights, shared accounts, production data classification, trusted-boundary interfaces, concurrency and durable financial/resource records make this **Level B**, not merely a small JavaScript/TypeScript plugin because it might display inside Paseo.
- **Possible thin Paseo client/plugin adapter:** may independently qualify for **Level A** because it must integrate with Paseo's existing JS/TS interface. That does not constrain the calculator core's language.

## Requirements to derive and validate before selection

The following are preliminary requirements; thresholds are not yet frozen, and proposals must not invent evidence of compliance.

| Property to establish | Discriminating failure case / evidence |
| --- | --- |
| **Identity isolation** | ASES resource cannot consume HMS or \`tripn-chill-zone\` quotas/tokens even through a shared interface. Cross-domain grants must be explicit, auditable, revocable and never inferred from common platform ownership. |
| **No implicit execution or spending** | A placement query cannot launch compute, activate a billed sandbox, modify GitHub, move credentials or deploy. Distinguish provider rates, quota balance, usage events and actual bills. |
| **Correct work-graph proposals** | Reject cycles, impossible resource requirements and unsafe dependency ordering; compare downstream setup/cache/transfer, time and spend, not greedy first-stage price. Replanning must preserve immutable completed evidence. |
| **Valid external data** | Malformed or misleading provider API data, JSON, resets or quota units cannot bypass invariants; type checking alone is not input validation. |
| **Durability and concurrency** | Define atomicity, source-of-truth boundaries, reconciled measurements, competing observers, interrupted writes and stale account reports before choosing persistence or runtime. |
| **Measured small-host cost** | Set concrete resident-memory, idle CPU, maximum response-time and startup constraints from actual representative loads on the chosen VPS, not from assumptions about runtimes. |
| **Security / least authority** | An untrusted provider host, compromised API response or compromised worker cannot cross project identity or acquire production launch/deploy rights. Minimize TCB and privileged credentials. |
| **Observability without duplicate tooling** | Ingest actual Paseo/OpenCode token/TPS/cost signals with provenance and confidence; avoid duplicating mature existing telemetry or re-deriving already measured usage. |
| **Interoperability and replaceability** | Stable, versioned input/output contracts, human-readable alternative plans, no coupling of core semantics to a single model/orchestrator, CLI or Paseo runtime. |

A necessity/reuse pass must first decide whether the system actually needs a standalone always-on process or whether a pure library + on-demand query + small persistent state is enough. The operator requires a persistent calculator *capability*, not necessarily a second daemon.

## State-model applicability assessment (preliminary)

- **Pure proposal evaluation:** potentially NOT APPLICABLE for a separate state machine if simple DAG and invariant checks are sufficient; retain explicit graph semantics.
- **Plan revision / observations:** SUPPLEMENTARY candidate — distinguish proposed, accepted, observed, superseded, failed and reconciled states while never rewriting observed results.
- **Account grants, credits, reservations and external execution lifecycles:** SUPPLEMENTARY or PRIMARY candidate where authority/settlement matters. Current v0 does **not** implement those authorities. Before adopting a state model define guards, forbidden transitions, failure/recovery and physical-provider settlement checks.

Do not choose a state-machine library before demonstrating the modeling value.

## Current prototype review: why tests are not enough

Present \`tools/resource-planner/planner.ts\` uses \`strict: true\` and \`noUncheckedIndexedAccess: true\` in \`tsconfig.json\`, which are sensible **if** TypeScript is selected. It also uses non-null assertions (\`!\`) and its CLI parses arbitrary JSON before passing it into the planner without full schema decoding. The library has hand-written runtime checks but those are not complete proof of trusted external-data handling. Numeric cost and included-minute units are simplistic; actual providers expose incompatible reset, GB-hour, CPU-hour, model-token and monetary units.

These are **examples of unmet/untested realization guarantees**, not claims of an exploitable production vulnerability (the prototype has no production credentials or deploy access). The current Node.js/npm dependency chain, memory footprint, availability on constrained VPS and effects on the trusted computing base have not been compared with alternative mechanisms.

The previously reported 10 passing local tests cover the example's behavior only; no independent broad realization survey, adversarial security review, actual provider quota observations, performance benchmark, deployment or trustworthy E2E trial has been completed.

## Required next sequence (no preselected implementation)

1. Derive and freeze the planner's observable core behavior, trust/authority bounds, data ownership, failure cases, persistence needs and representative workload/resource thresholds **without requiring a language, DB, runtime or library**.
2. Perform the scoped state-model applicability evaluation and build cheapest forbidden-trace tests.
3. Search mechanisms that meet the constraints, including reducing or eliminating components, reusing existing Paseo/OpenCode capabilities, and approaches not restricted to the existing prototype. Do not instruct independent evaluators to choose from a favored language shortlist.
4. Apply hard exclusion criteria, recording **EXCLUDED / UNRESOLVED / VIABLE** with evidence for each candidate.
5. Select only among demonstrated viable realizations, accounting for total trusted base, VPS RAM/CPU, integration cost, correctness, portability and future identity separation. The thin Paseo UI adapter may be considered separately.
6. Preserve and adapt the behavioral tests from the disposable prototype as needed, then rebuild/retain/retire its implementation in accordance with the selected realization. Verify red-to-green and independent review before adoption.

**Current outcome:** No realization selected. Do not present Node.js/TypeScript as the decision, do not promote the prototype to the management plane, and do not use the code to authorize real provider activity until the ASES gate is satisfied.

## Initial requirements-first survey completed (2026-11-01)

The operator clarified that **Paseo compatibility is only a current integration requirement; speculative long-term interoperability must not influence realization choice**. The research now includes:

- [Resource Planner Requirements and Behavioral Model](Resource%20Planner%20Requirements%20and%20Behavioral%20Model%202026-11-01.md), including falsifiable invariants, scoped state-model applicability and an **observed 52-minute vs proven optimal 32-minute synthetic counterexample** against the existing assignment-only v0.
- [Resource Planner Mechanism and Realization Survey](Resource%20Planner%20Mechanism%20and%20Realization%20Survey%202026-11-01.md), comparing exact small-graph search, constraint programming/CP-SAT, MiniZinc with multiple backends, MILP, SMT, incremental heuristics and weaker graph/rule-only methods, with source links and test plan.

The initial broad research pass is complete, **but the realization gate remains UNRESOLVED**. No candidate has passed current-machine footprint, complete-fixture semantics, measured optimizer performance and operational trust checks. The next work is small solver-neutral fixtures and direct comparative experiments, not expansion of the initial Node/TypeScript prototype into a live service. A separate adapter specific to current Paseo is permissible when actual APIs are verified; it is not a selection constraint for the core.

## Historical evidence and WHAT NOT TESTED

- Evidence: source code and ten local regression tests from the 2026-11-01 feature branch; three canonical methodology documents above.
- Interpretation: current v0 can inform behavioral requirements; it does **not** satisfy or replace the language-selection procedure.
- Not tested: full exclusion-first search, model-specific assurance, external JSON schema validation, exhaustive graph optimization, live model/provider API integration, persisted quota reconciliation, recovery, concurrency, production data/credential boundaries, benchmarked memory/CPU use on target host.
