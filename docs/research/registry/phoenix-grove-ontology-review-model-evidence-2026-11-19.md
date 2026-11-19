---
title: Phoenix Grove Ontology Review — Model Feedback Evidence, 2026-11-19
program: EDASES
layer: Research
document_type: Research Record
status: Draft
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/research/registry/AI Capability Registry Specification.md
  - docs/research/review-inbox/resource-solver-ontology-review-wave-2026-11-19.md
related_documents:
  - docs/research/review-inbox/resource-solver-ontology-source-reconciliation-2026-11-19.md
  - docs/research/registry/Model-Routing-Matrix.md
last_updated: 2026-11-19
---

# Phoenix Grove Resource Solver exploratory ontology review — bounded model feedback

**Purpose:** capture the model-specific evidence required at the end of this research session without prematurely revising the historical Model Routing Matrix or merging model generations. This record belongs to a **draft research PR**, not the accepted live capability registry. Different model IDs, routes and tasks must not be merged into one reliability score.

## Frozen review conditions

- **Review task:** exploratory, pre-build ontology integration of Resource Solver with capability, tool interface, authority, context and execution evidence. No implementation/runtime audit.
- **Review source:** `rock-solid-sites/ASES@cb27e4de21142c36c634f9130c9591b7912c3dec`.
- **Identical request packet for all substantive first responses:** prompt SHA-256 `82466bccd73b8802c7cab7c219994bb30d7468cfb4f4c9494c43e605d2b0e5bd`; source packet SHA-256 `2f8feec5ccc045869e6609c0d8631dcd7f4fd9c500ca0247c464d0f2ef599e87`.
- **Provider route:** Phoenix Grove `pgs2` through Codex CLI, model explicitly requested and route logged as confirmed. GitHub-hosted Ubuntu Actions runner, a configured read-only Codex sandbox, no fallback and configured provider/stream retries 0. These settings **do not** establish verified deny-all tool isolation.
- **Independent opinions:** first substantive report from each of three named model families, no peer results in prompt. Agreement is not independent runtime validation.
- **Public synthesis:** [three-model wave and addendum](../review-inbox/resource-solver-ontology-review-wave-2026-11-19.md); [source-first reconciliation](../review-inbox/resource-solver-ontology-source-reconciliation-2026-11-19.md). Full raw reports are in private `rock-solid-sites/ases-plugins` review branch, not copied into the public ASES registry.

## Observed per-model evidence

| Invoked model ID | Job evidence | Delivery & verdict | Observed contribution | Limitation/failure |
| --- | --- | --- | --- | --- |
| `deepseek-v4.1-flash-1017` | [Job 135758752902](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44580280375/job/135758752902) | Success, substantive 18,549 stdout bytes; **conditional** | Identified operation/route distinctions, trigger lifecycle, context ownership, Engine authority and correctness-versus-cost constraints | Documentary analysis only; no implementation repro, source selection bounded |
| `glm-5.3-flash` | [Job 135758753594](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44580280375/job/135758753594) | Success, substantive 11,217 stdout bytes; **conditional** | Focused on operation/sub-operation meter linkage, launch trigger and route substitution | Suggested extra reservation/Trigger abstractions not established as necessary; conflated Work Unit semantics with job/stage in some reasoning; source-first reconciliation required |
| `mimo-v2.6-flash` | [Failed job 135758753222](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44580280375/job/135758753222) and [successful retry job 135766611767](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44582509135/job/135766611767) | **First attempt:** exit 124 at 270s, zero report bytes, no verdict. **Second separately operator-authorized attempt:** exit 0, substantive 17,913 stdout bytes; **conditional** | Independently highlighted tool binding, origin correlation, capability/resource permission conjunction, context provenance and output-validation separations | At least one intermittent delivery failure; increasing bound from 270s to 420s in second attempt prevents causal attribution of success solely to retry. No live transport or enforcement tests |

**Total: four provider invocations, three delivered substantive first reviews, one failed invocation.** The MiMo second attempt used identical prompt/source hashes and a larger invocation bound; it is **not** a fourth independent reviewer, and no second DeepSeek or GLM invocation occurred in this wave.

## Qualified performance and reliability

- **Delivered review adequacy:** all three produced falsifiable concepts and explicit limitations suitable for *hypothesis generation*. No source-first testing demonstrates a reproducible implementation bug from these opinions. The crosswalk revision is a synthesis by a separate source reconciler, not the models' independent sign-off on the revised proposal.
- **Error taxonomy:** MiMo first failure is an *invocation timeout / non-delivery*, not an incorrect verdict. GLM's proposed new reservation entity is a *reviewer abstraction overclaim*, not provider failure; its concerns about multi-meter replay remain relevant as unproven cross-process implementation safety. A model's correct source quote may still omit a document not supplied.
- **Model confidence:** preliminary for this *specific task and provider route*. Do not extrapolate to model families, all Phoenix Grove workloads, coding quality or independent implementation verification. Earlier `mimo-v2.5`, `glm-5.2` and `deepseek-v4-flash` records are different identifiers/routes and should not be edited as if these were replacements.
- **Token / cost metering:** `cli_aggregate_tokens=not_exposed`, `provider_metering=unknown`, `billed_usd=unknown` for each job. **No comparison of token cost, price, or economic efficiency is supported.** The failed 270-second MiMo call may have generated provider costs despite delivering zero bytes. Review bytes and duration are not tokens or billed usage.
- **Timing:** MiMo success completed at 2026-11-19 18:01:54 UTC. Explicit retry was bounded to 420 seconds; no claim of actual model inference duration from outer timeout or GitHub job wall time.
- **Permissions:** `contents: read` and configured Codex read-only sandbox were observed in workflow; no hostile escape tests or independent credential-scope audit were performed.

## What to do with this evidence

- **Do** use it when designing Projektor `ASES-10` reviewer-launch metering requirement: distinguish every invocation from the delivered first substantive report, preserve explicit retries and failure costs, record provider/model, prompt/source hashes and result quality.
- **Do not** assign numeric 1–5 ratings, alter model-routing recommendations, or claim a model is more economical from this single three-family documentary review.
- **Do not** treat the pending Work Notes `WNASES-17` ontology conformance cases as already verified. They must check the actual relation contract separately; the sealed formal P7 six-case benchmark is not complete.
- **Follow-up tracking:** human reviewer-service evolution is Projektor `ASES-10`; future crosswalk validation is `ASES-20` / Work Notes `WNASES-17`. Technical detail, source pins and safe-to-publish findings stay in GitHub; private raw reviewer reports remain in the private tool repository.

**Status:** evidence captured for later capability-registry evaluation; not a recommendation, score, model qualification or canonical promotion.
