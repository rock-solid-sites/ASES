---
title: Resource Solver Chat — Response on Testing, Debugging, and Ontology Proposals
program: ASES / EDASES
document_type: In-Context Discussion Draft
status: Draft commentary; not adopted policy
authority: Research / Discussion
date: 2026-11-02
target_conversation: Resource Solver Chat
related_proposal_branch: proposal/testing-and-assurance-method-2026-11-01
---

# Response for the Resource Solver Chat

The new [testing, debugging, and ontology proposals](https://github.com/rock-solid-sites/ASES/tree/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology) fit the Resource Solver's direction, but they reveal several distinctions that need to remain explicit in its architecture. I would incorporate the **reasoning and evidence discipline** provisionally, without adopting the draft methods as compulsory gates or changing our current resource-solver design solely to accommodate them.

Our testing work on the [experimental Rust–Haskell branch](https://github.com/rock-solid-sites/ASES/tree/research/rust-haskell-admission-2026-11-01/research/testing-assurance-pilot) now provides concrete observations from five pilots:

- **P1:** Targeted positive/negative controls detected four deliberate paid-authorization and false-rejection mutations. One attempted evidence archive check initially suffered a write-after-index race; fixing that was part of testing the *test instrument*.
- **P2:** Trip'n's existing six self-tests still passed when a forbidden-content protection was deliberately disabled. A more discriminating valid/invalid neighbor pair caught the defect. That example is especially relevant to a Resource Solver whose admission checks could be green while the wrong guard is exercised.
- **P3:** The narrow five-case suite missed all six capacity, prepaid-wallet, and spend-cap mutants; the preexisting 1,025-case corpus caught all six, as did six newly frozen boundary cases. Test scope and explanatory value matter more than an undifferentiated pass count.
- **P4:** In-memory Rust and Haskell reservation prototypes preserved the specified invariants in normal and deliberately delayed trials; stale-snapshot counterexamples violated capacity, spending, or idempotency constraints. A bounded, measured CPU-contention treatment increased latency without finding another invariant violation. These are not production scheduler guarantees.
- **P5:** A credible conventional restart/retry suite caught duplicate-commit behavior but missed acknowledgement issued *before* a journal was durably written. Checkpoint-qualified SIGKILL/recovery tests exposed that ordering error five times in each language, while correctly ordered implementations survived the targeted interruption points. The first CI run also contained an incorrect spending-cap fixture: an apparent red assertion was a test-oracle error, not an implementation defect.

The result is not that every solver change needs mutation testing, crash injection, ontology reviewers, or lengthy pre-registration. It is that **the chosen evidence method needs to distinguish the specific consequential failure it claims to rule out**, and that the instrument itself can be defective.

## Resource Solver concepts that must not collapse into one status

The [proposed Ontology Design Reviewer](https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/ontology-design-reviewer.md) and [Ontology Conformance Reviewer](https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/ontology-conformance-reviewer.md) make an important distinction between identifying the right concepts and checking an implementation against approved meanings. For this solver, the first task is to preserve the following boundaries:

1. **Proposal versus authorization versus execution.** The Orchestrator proposes a job with expected duration, model, environment, quota consumption, and cost. The thin solver/API authorizes or refuses the proposed reservation against the current effective allowances. Only then may an agent or environment launch. Launching, becoming active, completing, failing, and being cancelled are separate events. An affirmative admission is not proof that work actually started.
2. **Estimate versus reservation versus measured consumption versus settlement.** A projected 45-minute Codespace job, an allocation of 45 minutes, an actual 30- or 60-minute run, and provider-billed usage are four different facts. Recording the estimate as actual usage, or the reserved amount as the eventual charge, would be a category error. Reconciliation must use observations and correction events, not overwrite an earlier prediction as if it had never existed.
3. **Allowance versus entitlement versus available capacity.** Provider-published quotas, subscription entitlements, observed current usage, remaining allowance, rate limits, provider availability and actual billing limits are related but not interchangeable. Their freshness, provenance, scope, units, and confidence need to travel with them. A stale or unknown price is not a verified zero price.
4. **Work Unit versus session versus provider resource.** A durable job identity should survive changes of agent session or execution environment. A Codespace, cloud task, model call and Orchestrator conversation are not necessarily one-to-one with Work Units. Retries and provider callbacks must not duplicate a financial or capacity commitment.
5. **Event observed versus state inferred versus decision authorized.** A CI job marked successful, an agent saying it finished, a provider reporting usage and the solver declaring the account reconciled are different evidence claims. No single global `success` field should collapse them.

Those conceptual boundaries matter even if we initially store everything in a small JSON event stream rather than a larger database or formal ontology.

## What the testing proposal changes for the solver

The proposed [Testing and Assurance Method](https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/testing-and-assurance-method.md) would be most useful as a **claim-oriented selection method**. It does not prescribe the same tests for every component.

The solver's highest-value guarantees concern admission, accounting and recovery: no unbounded launches by the Orchestrator; no overallocation of simultaneously reserved resources; no unauthorized positive cost; no duplicate reservation or charge on a retry; accurate reconciliation of estimated, committed, measured and provider-settled usage; and explicit degraded decisions when quota, pricing or provider data are stale or unavailable.

These suggest a graded test portfolio rather than a global pass/fail suite. Pure deterministic arithmetic and parsing can use reference examples, generated cases and targeted boundary tests. State transitions and competing admissions need interleaving/property or state-model tests. Durable reservation and reconciliation require kill/restart and replay tests. Provider-facing account/allowance correctness ultimately needs provider observations at the actual interface, with safe authorization boundaries. Performance tests should measure the decision path separately from transport and serialization overhead.

The Rust–Haskell language experiments are evidence about *two small implementations*, not a settled choice of language, state engine, storage scheme, solver library or operational stack. The same principle applies to Pumpkin and other possible constraint engines: they should be judged against independent requirements and practical integration evidence rather than adopted because a synthetic benchmark is attractive.

## A minimal shared evidence vocabulary

Our P5 fixture error makes it clear why the solver and its tests should not emit only `PASS` or `FAIL`. A useful lightweight envelope has separate fields for:

- **Identity and provenance:** Work Unit / experiment / claim / test / run IDs, source and requirement revisions, actor, provider, timestamps, environment and units.
- **Before-event reasoning:** proposed action, predicted usage and cost, hypothesis, freshness and assumptions, authorization conditions, expected falsifier and chosen verification method.
- **Actual observation:** lifecycle transition, source of measurement, amount and units, timing, provider response, journal/ledger event and relevant artifact hashes.
- **Execution classification:** completed, failed assertion, infrastructure error, blocked, skipped, cancelled, incomplete or not run.
- **Evidence qualification:** instrument effective or ineffective, completeness and recoverability of archive, oracle independence and unresolved observation gaps.
- **Interpretation and decision:** claim supported within tested scope, contradicted or unresolved; authorized admission/denial/reconciliation/correction; source of authority; next action.

This describes **distinct meanings**, not a demand to build a complicated universal schema. A small typed schema and append-only event history are enough for the initial prototype, provided they leave room for additional event streams and explicit supersession links.

The Resource Solver should own its timestamps and job lifecycle accounting **for now**, because the planned Observer/Execution Engine do not yet exist. Capture streams should be modular so a later Observer can consume them without redefining source-of-truth ownership or requiring a second reconstruction from agent chat histories. Likewise, the thin API should make provider allowance, prices, effective limits and resource availability accessible *before* launch so the Orchestrator cannot bypass admissions or repeatedly scan entire conversations for status.

## Debugging and ontology review are complementary, not additional compulsory stages

The [Debugging and Fault Isolation Method](https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/debugging-and-fault-isolation-method.md) starts from a discrepancy and finds the smallest causal boundary using cheap discriminating tests. Applied to the solver, for example, an apparent overrun could come from a bad initial estimate, a real longer-running job, stale quota data, duplicate lifecycle events, delayed provider reporting, or an incorrect reconciliation formula. Each implies a different intervention. Replacing the scheduler or tightening a quota before distinguishing them would be speculative.

Ontology review asks a different question: are we even modeling the right thing? If the design treats *provider-reported usage* and *final settlement* as identical, perfect arithmetic tests could still prove the wrong guarantee.

The proposed two-role split is worth testing, but the existing Ontology Reviewer already has exploratory and conformance modes. The decision to make them separate runtime roles should depend on measured incremental value, false positives, routing cost and verified model-family/context independence. A deterministic terminology check may be sufficient; a second agent should not be summoned by ritual. No independent reviewer has yet validated P1–P5, and a reviewer handed the identities of planted faults is reconstructing evidence rather than performing blind defect discovery.

The [integration patch](https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/integration-changes.patch) is reference-only and still assumes the older combined ontology role. It should not be applied unmodified.

## Practical next direction

For the Resource Solver's next development decisions, I would preserve the current plan—thin launch/admission API, explicit projected resource use, event-driven actual-use reconciliation, provider-specific allowance and pricing records, and modular future Observer feeds—while treating the proposals as **testable design criteria**.

The nearest valuable experiments are small state-transition and reconciliation tests built around incorrect estimates, longer/shorter actual execution, cancellation, duplicate callbacks, and stale or missing provider usage. At least one test should compare a credible conventional suite with a qualified boundary/replay method, and show what *additional* violation the latter detects at what cost. Tests that do not change a real decision should remain optional.

Evidence from these experiments can eventually inform a canonical testing method, ontology-review routing and the Execution Engine's durable event model. For now the proposals remain draft, the Resource Solver has no proven production guarantees, and no language or infrastructure choice follows automatically from P1–P5.

**The shared principle is to preserve the difference between what we planned, what the solver authorized, what actually happened, what we observed, and what we are justified in concluding.** That distinction should be structural in the Resource Solver, not reconstructed from Orchestrator conversation history after the fact.
