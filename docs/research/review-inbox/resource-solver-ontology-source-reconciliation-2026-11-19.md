---
title: Resource Solver Ontology — Source-First Reconciliation and Minimal Integration Contract
program: EDASES
layer: Research
document_type: Research Finding
status: Draft
authority: Experimental
canonical_repository: ases
source_baseline: cb27e4de21142c36c634f9130c9591b7912c3dec
review_wave:
  - 44580280375
  - 44582509135
depends_on:
  - docs/research/Resource Solver Specification Reconciliation 2026-11-02.md
  - docs/standards/Canonical Terminology.md
  - docs/research/Provider Registry Control Plane and Usage Reconciliation 2026-11-01.md
  - docs/research/Identifier-First Tool Calling.md
  - docs/research/Task Execution Evidence and Model Quality Index Integration 2026-11-01.md
  - docs/research/review-inbox/resource-solver-ontology-review-wave-2026-11-19.md
related_documents:
  - docs/research/kernel-0/Kernel-0-Evidence-Packet.md
  - docs/research/Paseo Role Capability Matrix.md
  - research/capability-schema-validation/report.md
  - research/capability-schema-validation/corpus-530/report.md
  - docs/architecture/Execution Engine Vision.md
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-19
---

# Source-first reconciliation: Resource Solver ontology + capabilities, tools and information

**Verdict:** The present resource identities should be **retained**. The strongest unsatisfied architectural need is an explicit *relationship contract* joining required engineering capability, callable operation, concrete access path, independently authorized execution, multi-meter charges and qualified result. **No new universal gateway, ontology replacement or MCP migration is authorized or evidenced.**

This document reconciles the three Phoenix Grove exploratory ontology reports against fuller primary sources and known experiments. It is **research and a candidate relation contract**, not an adopted schema, approved implementation, security proof or new Kernel/Engine component. In this document, "missing" means missing from the specified integration relationship, not necessarily absent from every historical branch.

## 1. Scope, source authority and evidence corrections

**Baseline:** [ASES `cb27e4de`](https://github.com/rock-solid-sites/ASES/tree/cb27e4de21142c36c634f9130c9591b7912c3dec). Reviewer source input was bounded and excluded some authoritative and later experimental documents; this *reconciliation* reads those missing sources. Reviewer output remains unchanged; this is a separate, non-blind analysis.

**Reviewer evidence:** [Phoenix Grove original wave](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44580280375) produced DeepSeek and GLM substantive reports; MiMo timed out. [MiMo-only retry](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44582509135) delivered its independent first substantive report using identical input hashes. All three assessed the research ontology conditionally sufficient. Their agreement does not promote a requirement; see separate [review-wave record](resource-solver-ontology-review-wave-2026-11-19.md).

**Authorities and facts the reviewers could not fully inspect:**

- [Canonical Terminology L194–202](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/standards/Canonical%20Terminology.md#L194-L202) **already defines Capability** as a *demonstrable ability of an AI system, tool or participant to perform a defined engineering task*. It is an evaluated ability, not a callable function identifier or an authentication token.
- [Kernel-0 Evidence Packet](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/kernel-0/Kernel-0-Evidence-Packet.md) independently requires bounded authority, external-to-executor authorization, durable Work Unit identity, disposable Execution identity and authority revocation. **Kernel-0 is research; do not claim it currently enforces these boundaries.**
- [Paseo Role Capability Matrix §§4–8](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Paseo%20Role%20Capability%20Matrix.md#L209-L500) already distinguishes semantic role capability, role authority, runtime permissions and provider-native tool settings. This is a temporary harness compatibility study, not a complete Kernel.
- [Task Execution Evidence/MQI L32–69](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Task%20Execution%20Evidence%20and%20Model%20Quality%20Index%20Integration%202026-11-01.md#L32-L69) already distinguishes attempt, forecast, measured resource cost, **verified outcome**, allocation decision and privacy-preserving evidence references. It explicitly rejects success inferred from a successful API response.
- **Important evidence update:** [Corpus 530 live-model report](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/research/capability-schema-validation/corpus-530/report.md) follows the earlier [deterministic 14-op validation study](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/research/capability-schema-validation/report.md). Corpus 530 actually used live `openai/gpt-4o-mini` through OpenRouter (24 tasks × two variants, plus recovery and adversarial cases; one repetition per variant). The description block fell **8,915 → 2,588 tokens** (71.0%); selection was 24/24 each, schema-valid arguments **23/24 full vs 22/24 minimal**, but strict intended arguments **23/24 vs 20/24**. Three minimal strict mismatches include omitted optional intent or wording drift, even when schema passes. First-attempt correction was **8/12 schema-valid** vs **4/12 strict**; output validation was tested separately, not automatically integrated into `Harness.call`. This is stronger evidence than the proxy alone but does **not** establish cross-model, multi-step, transport-independent or whole-Work-Unit cost savings. [Later 3-rep/multi-model plans](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/research/capability-schema-validation/corpus-530/next-wave/measurements/README.md) were scaffolding, not executed data in that document.

**Correction to earlier summary:** It was accurate to call the *original capability-schema report* deterministic; it is inaccurate to imply there has never been a live-model comparison. Corpus 530 is relevant independent research, though it did not test replacing MCPs.

## 2. Reviewer-finding disposition against authoritative sources

| Report claims | Classification | Source-first finding and treatment |
| --- | --- | --- |
| DeepSeek F1/F6; GLM ONT-01; MiMo F1: capability / operation / route | **Retained as narrow cross-system relation gap** | Canonical Capability, Identifier-First `op_id` / ToolRegistry, and Solver credential/route are distinct. The [Solver glossary L71–90](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Resource%20Solver%20Specification%20Reconciliation%202026-11-02.md#L71-L90) lacks their explicit join. This does **not** require a new universal gateway. |
| GLM ONT-02: operation-level meter confusion | **Narrow join gap, not a proven accounting flaw** | [Solver D04/D13 and §5](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Resource%20Solver%20Specification%20Reconciliation%202026-11-02.md#L54-L66) already support multi-account/multi-product claims. A planned or observed sub-operation needs correlation to its job/attempt and charge bucket; no single universal `tool cost` measure is justified. |
| DeepSeek F2; GLM ONT-03; MiMo F2: trigger and lifecycle | **Retained as origin/correlation gap; proposed Trigger entity rejected pending falsifier** | [Solver §5 L121–131](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Resource%20Solver%20Specification%20Reconciliation%202026-11-02.md#L121-L131) already separates job, attempt, reservation, auth, provider operation and retries. A typed *trigger-origin observation* and `controlled/external/observed` classification could suffice. Requirement for independently durable trigger identity is not yet established. |
| GLM ONT-04: duplicate reservations / new “reservation substrate” | **Existing semantic invariant; known implementation limit** | [Solver R03–R04](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Resource%20Solver%20Specification%20Reconciliation%202026-11-02.md#L175-L179) mandates durable atomic multi-meter reservation and distinct launch identities; [Admission Gate Audit L19–55](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Resource%20Solver%20Admission%20Gate%20and%20Exact%20Reference%20Audit%202026-11-01.md#L19-L55) calls current Python locks process-local and lacks durable CAS/settlement protection. Requiring a new ontology entity confuses semantics with implementation. |
| DeepSeek F4: free-only route; unknown quotas | **Explicitly covered; implementation test not done** | [Solver L151–157](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Resource%20Solver%20Specification%20Reconciliation%202026-11-02.md#L151-L157) permits zero chargeable claims while still requiring authorization; earlier Python prototype rejects them. Distinguish unmetered/no-liability, unknown meter and unknown allowance. |
| DeepSeek F3; MiMo F4: context lineage | **Retained as evidence relation gap; ownership already declared** | [Execution Engine Vision L184–198](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/architecture/Execution%20Engine%20Vision.md#L184-L198) assigns context construction/retrieval to Engine. [Solver `evidence.references`](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Resource%20Solver%20Specification%20Reconciliation%202026-11-02.md#L133-L147) and [MQI/evidence reference model](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Task%20Execution%20Evidence%20and%20Model%20Quality%20Index%20Integration%202026-11-01.md#L32-L69) can link original → transformation → model-visible projection without transferring authority to Solver. |
| MiMo F3: resource auth vs capability policy | **Retained conjunction/ownership invariant; pieces exist** | [Capability Test D](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/research/capability-schema-validation/report.md) distinguishes `UnknownOperation`, `ValidationFailed` and `PolicyDenied` from resource admission. [Kernel-0 Evidence Packet](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/kernel-0/Kernel-0-Evidence-Packet.md) governs future authority requirements; current Solver must not grant capability access merely because allocation is feasible. |
| MiMo F5: output conformance vs verified work | **Known test finding; implementation/evidence qualification gap** | [Original Test C3](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/research/capability-schema-validation/report.md) found output-schema drift passes input validation; [Corpus 530 §8–9](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/research/capability-schema-validation/corpus-530/report.md#L166-L210) does manual output validation but not end-to-end call integration. [MQI verified outcome](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Task%20Execution%20Evidence%20and%20Model%20Quality%20Index%20Integration%202026-11-01.md#L32-L43) already disallows “API succeeded ⇒ useful work”. No new universal success flag. |
| DeepSeek F7; GLM general economics | **Already represented; evidence needed** | [Task Execution Evidence/MQI](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Task%20Execution%20Evidence%20and%20Model%20Quality%20Index%20Integration%202026-11-01.md#L26-L69) already requires Pareto alternatives, hard constraints, quality, retry burden, human correction and uncertainty. Corpus 530's schema-valid-but-intent-wrong examples illustrate why cheapest tokens ≠ best verified outcome. |
| GLM ONT-05: silent model substitution | **Policy clarification; no new entity needed** | [Solver D04/D13/§5](https://github.com/rock-solid-sites/ASES/blob/cb27e4de21142c36c634f9130c9591b7912c3dec/docs/research/Resource%20Solver%20Specification%20Reconciliation%202026-11-02.md#L54-L66) binds model/product/account/meter to a forecast and revision. An unapproved material route change cannot inherit another route's authorization; new revision + revalidation required unless explicitly within an authorized alternative set. |
| GLM billing-cycle object; DeepSeek F5 Engine-document mirror | **Reject unnecessary new billing entity / retain metadata question** | Meter period and provider report/settlement are already independent. The Engine Vision explicitly identifies itself as an `ases-engine` mirror/placeholder; this is a *source-authority housekeeping decision*, not reason for the Solver to own Engine state. |

**Severity correction:** Reviewer HIGH flags are hypotheses until mapped to implemented claims and reproducible invariant failures. The source-first classifications above supersede no raw review and make no production defect claims.

## 3. Minimal candidate relation contract (reuse, not ontology expansion)

The aim is to join *existing identities*. Names are **illustrative types/relations** for scrutiny, not new canonical classes, API names or schema definitions.

```text
Proposed work graph / stage / job
  --requires--> evaluated Capability (domain/task competence; evidence-based)
  --requests--> semantic OperationContract(op_id, input/output schema revision, effect)
  --may-use--> OperationBinding(operation_id, client/adapter, transport, scopes)
  --under-policy--> role/grant + task authority + data classification
  --planned-as--> RouteSelection(attempt_id, binding_id, account, product, environment, model/harness)
  --quotes--> Forecast(meter claims, uncertainty, observed basis)
  --admitted-by--> independent ResourceAdmission + capability/action authorization
  --launched-as--> Attempt(idempotency key, origin event/ref, controlled/external/observed)
  --observed-via--> sub-operation event / tool-call refs / provider-resource events
  --consumes--> account/product/meter/period-bound observations
  --produces--> source/derived/model-visible evidence refs + output-validation result
  --qualified-by--> task-level verified outcome and separate accounting/settlement
```

A route must be described precisely enough to **select** it, **authorize** it, **execute** it and **attribute** actual resource use; this does not require a physically unified service. "Same capability" is weaker than "semantically equivalent operation": e.g. an MCP `get_logs` output and a CLI `--log-failed` output might not have the same scope, completeness, error semantics or source fidelity. Equivalence must be established against the requested postcondition, not inferred from names, token count, or transport.

| Contract join | Candidate minimal information | Current conceptual owner |
| --- | --- | --- |
| Requested outcome → capability → operation | Task specification/version, capability evidence reference/confidence, operation ID + required postconditions | Engine/Work graph and Capability Registry research; no Solver-owned model benchmark |
| Operation → concrete binding/transport | Stable binding reference, schema revisions, client/adapter, transport mode, endpoint location, permission scopes, lifecycle costs and expiry | Tool interface/adapter/harness; **no mandatory gateway** |
| Binding → account/placement/meter | Source provider/product/contract revision, account/payer/principal, runtime environment, pre-run meter claims, time windows, trust/data class | Solver registry/planner; existing resource objects |
| Task authority + capability policy + resource admission | Independently checked permissions/grants and resource reservation; bound to exact attempt, route revision and account; reason codes/expiry | Existing role policy/authorization + Solver; future Kernel substrate distinct |
| Trigger → attempt → provider operation | Origin event/reference; admission classification; correlation and idempotency IDs; observed external effects and cancellation/teardown | Launch adapter and execution evidence; might be an attribute, not new Trigger service |
| Information provenance → model view | Original evidence hash/ref and access class; transformations/versions; cached/retrieval provenance; context-inclusion/size; model-visible projection ref | Engine context management and evidence/archive layer; Solver quotes **meter consequences only** |
| Response → qualified outcome | Output schema/version check; result completeness/semantic criteria; validation/test evidence; review finding vs authorized acceptance | Runtime adapter/validation and Engine/EDASES evidence |
| Observed usage → provider report → settlement | Correlation IDs, source, unit, time window, reported/accounted differences and revisions; no false exact attribution | Solver accounting and provider control plane; Observer future |

**Do not fuse:** Capacity authorization ≠ capability permission ≠ task authority. Operation available ≠ model can see it ≠ permission to invoke ≠ operation executed ≠ output schema valid ≠ task accomplished. Tool-description bytes ≠ model input tokens ≠ provider-billed tokens ≠ end-to-end marginal cost.

## 4. Worked boundary traces (conceptual, no provider figures invented)

**A. GitHub Actions orchestration with external model**

`repository event → Actions workflow/controller → selected hosted OR external runner → model API invocation → report evidence → run status`. Trigger, runtime placement, model account and report storage are different refs. Charge measurements may include runner time, remote compute, model tokens and retained artifacts; each belongs to its actual payer/product/meter and its observation period. An external runner does not become “GitHub-hosted compute” simply because Actions triggered it.

**B. Same intended review-log operation through CLI, MCP or browser**

Candidate semantic postcondition: *obtain the failure-bearing steps and source references of a pinned GitHub Actions run*. CLI `gh run view ... --log-failed`, a connector's log-retrieval method and browser UI are not automatically equivalent. Each has different available fields, authentication scope, result filtering, setup/residency and output completeness. Preserve raw-source evidence and whether the model saw only a filtered projection. Compare eligible paths only *after* postcondition, authority and privacy checks.

**C. Free-only tool call requiring access approval**

No chargeable allowance claims does **not** mean no permission/admission checks. The specification already supports authorized free-only work; process-local Python reference logic requiring positive allowance claims is an identified implementation defect candidate.

**D. Context compression / retrieval with stale source**

`source version A → transformed summary S → model-visible context projection P → operation O`, followed by source version B. A successful `O` does not prove `P` was current or retained an important optional constraint. Keep lineage, transform version and missing data explicit. Corpus 530's omitted `filter.since` is a concrete semantic-intent warning.

**E. Tool output drift**

`input accepted → provider executes → stale-shaped output → output-schema check fails → API-level result not qualified → no successful work outcome inferred`. Accounting must still record spent resources even if the result fails validation. Existing prototype Test C3 and live corpus D4 support the *failure mechanism* but do not prove cross-transport enforcement.

## 5. Falsifiable invariants, not premature subsystem designs

These are **candidate properties for later tests**, not claims that a complete working system now passes them.

1. **Sufficiency and privacy before optimization:** no candidate route may be selected solely for tokens/cash if it fails an independently checked task postcondition, data boundary or capability permission.
2. **Distinct identities:** account/payer, model, harness, runtime environment, trigger and operation binding cannot silently substitute one another. Work Unit remains the future Engine identity.
3. **No resource or policy bypass:** launch requires independently valid attempt/resource authorization **and** capability/task authority for the chosen operation and route, unless an explicitly documented externally observed/unsupported path is being recorded (not falsely controlled).
4. **Revisions and idempotency:** changes to account, route, schema, material capability or authorization require revalidation unless the original grant explicitly covers the alternative; replays and external triggers must not silently cause double launches/charges.
5. **Usage truth:** record actual paid or free usage after failed work, overrun, cancellation and teardown; don't censor to reservations, subtract both provider aggregate and local events, or treat unknown as zero.
6. **Information and output truth:** schema-valid calls may be semantically wrong; output-schema-valid responses may still be incomplete; verified work outcome needs its own evidence and cannot be inferred from transport/settlement/archive status.
7. **No untested generalization:** stdio lazy connector results, a single live-model minimal-description comparison and mock admission proofs cannot establish universal MCP/CLI/API/browser equivalence, provider billing or secure authority enforcement.

## 6. Discriminating next decisions (only those not already settled)

- **D1 — Operation/binding identity:** Is `op_id` plus a versioned binding relation sufficient for all supported adapters? Treat a distinct Binding record as an interface choice; first-class global gateway only if an actual multi-route case cannot be represented without it.
- **D2 — Trigger identity:** Default to origin metadata/reference on the attempt and provider operation. Elevate Trigger to durable independent identity only if configuration-specific replay, authority or cross-attempt semantics demand it.
- **D3 — Permission conjunction and override:** Define exact authoritative parties for task grant, capability policy, account spending/borrowing and launch admission; ensure one authority cannot bypass the others via a cheaper route.
- **D4 — Information lineage/validation owner:** Specify which evidence links are emitted by adapters, context manager and verification workers, while keeping the Solver out of content orchestration.
- **D5 — Route changes:** Require revision-bound revalidation unless a set of alternates was deliberately authorized in advance.

**Not decisions to reopen:** Planner versus admission, multi-meter identity, Work Unit naming, future Observer, CPU oversubscription policy, provider billing separation, private-account boundaries, adopting an optimizer, or mandatory specialist review gates. These already have settled or explicitly provisional status.

## 7. Status and next bounded action

**Completed here:** Source-backed classification of all material independent review claims; correction of the live-model evidence omission; minimal relation contract and concrete counterexample traces. **Not completed:** schema/code changes, formal cross-system conformance test, real provider route comparators, measured end-to-end token/price savings, security proof, P7 sealed six-case benchmark, or canonical promotion.

**Next bounded operation:** validate the proposed *relations* against existing schemas/records with a small frozen symbolic fixture set, then separately compare two safe equivalent routes for one real operation. The fixture should try to falsify identities and permissions, not optimize prices yet. Avoid new persistent services or changing active MCP integrations before the crosswalk is demonstrated. Any test should count setup, model-visible context, validation, retries, successful qualified outcome and authorization failures, not just tool-description tokens.

This remains a research proposal in draft PR #62. Operator retains approval for ontology/methodology changes; source evidence, reviewer findings and later test results remain separate.
