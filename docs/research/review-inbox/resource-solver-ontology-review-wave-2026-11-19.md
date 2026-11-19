---
title: Resource Solver ontology — independent exploratory review wave, 2026-11-19
program: EDASES
layer: Research
document_type: Review Synthesis
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/research/Resource Solver Specification Reconciliation 2026-11-02.md
  - docs/research/review-inbox/resource-solver-ontology-independent-review-brief-2026-11-19.md
related_documents:
  - docs/research/review-inbox/resource-solver-ontology-audit-2026-11-19.md
  - docs/research/Identifier-First Tool Calling.md
  - docs/standards/Canonical Terminology.md
  - research/capability-schema-validation/report.md
consumed_by:
  - subsequent ontology integration and review plan
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-19
---

# Resource Solver ontology — first independent exploratory review wave

**Verdict:** 2 independent reports delivered; 1 model timed out with no report. Two independent *research* verdicts were both **CONDITIONAL PASS**, not production or methodology approval. This review did not run the separate, formally blinded six-case P7 Design/Conformance benchmark. It applied P7's **exploratory pre-build mode and clean-input/isolation discipline** to the Resource Solver integration question. Do not label P7's six-case benchmark complete.

## Dispatch and evidence

- **Pinned ASES source:** `cb27e4de21142c36c634f9130c9591b7912c3dec`
- **Private reviewer harness:** [ases-plugins Actions run 44580280375](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44580280375), dispatch commit `5869ec32320de0524af09411600244f62db18c42`.
- **Prompt SHA-256:** `82466bccd73b8802c7cab7c219994bb30d7468cfb4f4c9494c43e605d2b0e5bd`; **neutral input packet SHA-256:** `2f8feec5ccc045869e6609c0d8631dcd7f4fd9c500ca0247c464d0f2ef599e87`.
- **No contamination by companion audit:** the source packet used the neutral review brief plus pinned ASES source excerpts, *not* the audit, expected diagnoses, previous reviewers, or private P7 answer key.
- **Model provenance:** caller-side Codex diagnostics confirmed `pgs2` plus exact selected model. Source authoring was in a different model family. Independent jobs had no peer outputs.
- **Permissions:** GitHub contents read-only, Codex CLI read-only sandbox in independent temporary workspaces. This is **not independently proven deny-all tool isolation**. No target repo code intentionally executed, no canonical files edited.
- **Retries:** zero configured provider/stream retries, no automatic fallback. Provider monetary charges and authoritative metering are **unknown**; zero is not inferred.

| Route | Verified result | Raw evidence |
| --- | --- | --- |
| DeepSeek `deepseek-v4.1-flash-1017` | Exit 0; substantive 18,549-byte first-pass report; CONDITIONAL PASS | [Job 135758752902](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44580280375/job/135758752902) |
| GLM `glm-5.3-flash` | Exit 0; substantive 11,217-byte first-pass report; CONDITIONAL PASS | [Job 135758753594](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44580280375/job/135758753594) |
| MiMo `mimo-v2.6-flash` | Exit 124 after 270-second deadline; 0 output bytes; **NON-DELIVERY / NOT SCORED** | [Job 135758753222](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44580280375/job/135758753222) |

The two raw reports and the MiMo failure record are committed under the **private** `rock-solid-sites/ases-plugins` branch `review/resource-solver-ontology-pgs2-20261119`, at `docs/reviews/results/20261119-resource-solver-ontology/`. They must not be paraphrased as three independent successful reviewers.

## Synthesis of material conceptual questions

### 1. Semantic operation, capability, route and meter relations — credible integration gap

**Agreement:** Both delivered reviewers found the existing identities broadly sensible but the link between *what an operation does*, *how an agent accesses it* and *which account/meter pays* insufficiently explicit. DeepSeek calls this an under-specified route identity; GLM highlights operation/harness-level resource claims. The documented identifier-first research already contains operation IDs and authoritative schemas, and the Resource Solver already contains account- and meter-bound claims.

**Narrow follow-up:** Build a *crosswalk/reference contract* among those existing definitions before proposing a new class, gateway, or service. Distinguish semantic operation, client presentation, transport, credential/identity, triggering service, runtime placement and billed action.

### 2. Trigger versus attempt, cancellation and runtime life — gap in consolidated contract, disputed entity choice

**Agreement:** A GitHub Actions trigger need not be the environment where a job executes. The attempt, external runner, billable resource lifetime, stop confirmation and retry may diverge.

**Disagreement:** GLM recommends a first-class Trigger event/actor. DeepSeek recommends retaining trigger as an attribute/relation of attempts or external events, promoting it only if independent identity is required. Neither proposal is an authorized design decision.

**Narrow follow-up:** State the required invariants (external events; exactly-once/admission intent; launch idempotency; retries; cancellation/drain; independently billable resource lifetime) and identify which existing event/journal structures satisfy them. Add an entity only if a counterexample demands separate identity.

### 3. Context and information costs — existing owner, incomplete cost joins

DeepSeek identifies an unfinished relationship linking retrieval, filtering, caching, context inclusion and original evidence to work attempts and model charges. Canonical Engine Vision already owns context management; the Solver needs observations/quotes for its resource consequences, **not a new context authority**. Distinguish provider billed tokens from displayed bytes, cached results, context occupancy and correctness/retry consequences.

### 4. Hard constraints versus economics — keep existing separation

Both reports support retaining separate forecast, reservation, usage, provider report and settlement; no evidence justifies collapsing these into one `cost`. Free-only admission, rate limits and opaque quotas remain unresolved *implementation/provider evidence*, not evidence that these concepts are absent.

### 5. Overclaims and likely false positives requiring triage

- GLM raises duplicate allocations and requests a new “reservation substrate”, but the Solver specification **already requires atomic multi-meter reservation, independent validation and revision-bound admission**. The current Python gate's lack of durable cross-process atomicity is a known **implementation limitation**, not proof of a missing ontology object. Preserve as a targeted implementation falsifier, not accepted ontology finding.
- GLM refers to “the work unit” as the scheduled unit; Solver Spec D12 explicitly reserves named **Work Unit** for the future Engine component and uses work graph/stage/job/attempt today. Do not repeat the conflation.
- Proposed provider billing-cycle or trigger objects and a universal capability gateway have not demonstrated distinct identity needs. Do not add them on reviewer preference alone.
- Existing **Canonical Terminology** defines Capability as “a demonstrable ability of an AI system, tool or participant to perform a defined engineering task.” It was *not supplied in the packet*, so GLM's apparent ambiguity should be checked against that authoritative definition before accepting a new capability identity.
- The packet intentionally selected a source neighborhood, not the full ASES corpus. Both successful reviews have corresponding WHAT-NOT-TESTED limits; absence from the packet is not proof of absence from the repository.

## Prompting review and procedural lessons

Read the current ASES skill index and current `review-launch`, `compact-prompt`, `agent-launch`, and `workflow-orchestration` skills before dispatch. Also reviewed `ases-plugins/docs/INDEPENDENT-REVIEWER-WORKING-RECIPE.md`, `docs/research/prompting/Ontological Connection to Review Skill.md`, `docs/roles/Ontology-Reviewer.md`, `adversarial-reviews/adversarial-review-prompt-inventory.md`, `docs/research/EDASES Review Methodology.md`, and the P7 review execution protocol.

The general adversarial-review fixed core emphasizes tests and code; P7 distinguishes **exploratory ontology-design** from **post-build invariant conformance**. For this *pre-build conceptual review* the same compact, neutral, falsifiability-oriented exploratory prompt was given to each independently selected model. No direct defect checklist or companion audit was included. This is a separate application, **not** an executed outcome for P7's privately scored six-case comparative benchmark.

## Current status and next decision

**Prepared and executed:** two independent conceptual review reports, one explicitly logged failed delivery; sources and first-pass evidence preserved. **Not executed:** any canonical ontology modification, MCP/CLI migration, provider-account integration, live billing/usage test, P7 sealed-key benchmark scoring, or MiMo rerun.

**Next research operation:** reconcile the two reports against Canonical Terminology, full source declarations and the pre-existing admission/API semantics; classify each issue as already solved, terminology/crosswalk gap, policy decision, or implementation test. Define minimal falsifying examples and sound neighboring cases before changing ontology. A separate bounded MiMo retry may be useful only with explicit authorization and a narrower packet (the cause of timeout was not verified).

**Conclusion:** The evidence supports a *targeted integration contract audit*, not a general ontology replacement or universal-gateway build. This recommendation is preliminary research synthesis, not reviewer consensus as authority.
