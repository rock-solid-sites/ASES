---
title: ASES Testing and Assurance Method
program: ASES
layer: Methodology
document_type: Methodology Specification
status: Draft
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/standards/Documentation Standard.md
  - docs/methodology/ASES Bounded Project Build Method.md
  - docs/methodology/State-Model Applicability and Reuse Method.md
  - docs/methodology/Implementation Realization and Assurance Selection Method.md
related_documents:
  - docs/methodology/ASES Debugging and Fault Isolation Method - Proposal.md
  - docs/research/Guarantee-Driven Testing and Goal-Substitution Resistance.md
  - docs/research/EDASES Review Methodology.md
  - docs/PROVISIONAL-RED-GREEN-VERIFICATION-NOTE-2026-11-01.md
  - docs/research/Resource Solver Red Green Mutation Verification 2026-11-01.md
  - docs/requirements/Methodology to Requirements Mapping Specification.md
consumed_by:
  - project-specific assurance adaptations (proposed)
  - portable CI evidence contract (proposed)
  - future Observer and execution-engine requirements (proposed)
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-01
---

# ASES Testing and Assurance Method

> **PROPOSAL — not an adopted global policy.** This document integrates existing ASES principles and proposes additional obligations for review. It does not change the authority or scope of VSDD, existing methodology, agent rules, project-specific policies, or the provisional resource-solver red–green procedure. Acceptance, enforcement, retention settings, and project rollout require explicit decisions.

## 1. Purpose and outcome

Select, qualify, execute, and evaluate verification activities so that claims about a system are supported by **relevant, discriminating, preserved evidence**. The objective is neither maximum test count nor universal use of any favored test technique. A useful result may be a confirmed violation, an observation of no discrepancy within scope, a falsified assumption, an inconclusive test, a valid decision to perform no new test, or evidence that the test method itself is defective.

Every substantive assurance conclusion should answer:

1. **What is claimed, by whom, under which conditions?**
2. **Why was this question worth investigating, and what was believed before observation?**
3. **What possible observation would change the conclusion?**
4. **Why was this verification method selected over cheaper or stronger alternatives?**
5. **What was actually executed and observed, including failures and non-results?**
6. **What can and cannot be concluded, and which downstream decision changed?**

Testing is one form of evidence gathering. Specification review, static analysis, proof, model exploration, live observation, source inspection, and doing no new testing when sufficient evidence exists are all eligible outcomes of method selection.

## 2. Layers, authority, and relationship to existing methodology

- **EDASES (research)** studies the reliability, discrimination, costs, failure modes, and limits of evidence-gathering methods. It records the reasoning that led to an experiment as well as its results. The draft research framework *Guarantee-Driven Testing and Goal-Substitution Resistance* is relevant input, not a final universal rule.
- **ASES (methodology)** derives reusable selection principles, evidence expectations, assurance decisions, and justified project adaptations from findings. This document is a candidate ASES method.
- **Execution systems and projects** choose and operate concrete test runners, CI providers, storage, scripts, and checks in accordance with adopted requirements. Those implementations do not establish ASES method by their mere existence.

**No competing development lifecycle.** The canonical *ASES Bounded Project Build Method* already establishes target, acceptance, specification, verification, implementation, and independent review. VSDD, where adopted, supplies its own test-first, verification-architecture, adversarial, hardening, and convergence gates. This proposal defines how to select and preserve assurance evidence **within** those activities; it does not create an extra VSDD phase or authorize bypassing project acceptance gates.

**No favored realization.** Under the *Implementation Realization and Assurance Selection Method*, a valid solution may require no new code and therefore no implementation-language choice. Verification selection has the same neutrality: do not choose tests or automation before establishing what question evidence must answer. A justifiable NO_NEW_TEST result is possible, but must state the existing evidence and why it is sufficient.

**Human authority remains explicit.** Agents may propose claims, methods, findings, and changes, but may not silently weaken approved guarantees or redefine acceptance criteria to make a result pass. Final acceptance and method-policy changes remain with the authorized decision maker.

## 3. Proposed governing principles

1. **Claim before technique.** Begin with an attributable requirement, documented external guarantee, approved property, hypothesis, or observed anomaly. Record source, revision, scope, and limits. Do not invent a requirement to justify using a tool.
2. **Falsifiability and applicability.** State what would constitute contradictory evidence, or why the claim is not presently testable. Separate requirement truth from the means of observing it.
3. **Cheapest discriminating investigation first.** Prefer the smallest test that separates live competing explanations before a large test campaign. Cheapest does not mean weakest: a decisive cheap test can eliminate expensive wrong turns.
4. **Method choice is conditional.** Use tests, inspections, proofs, models, external checks, or no additional experiment according to the actual guarantee, risk, epistemic question, and operational boundaries. No universal test framework, language, state machine, or CI provider.
5. **Qualify evidence-producing instruments.** A green test is not by itself evidence that the test detects relevant incorrect behavior. Examine controls, oracles, fixtures, sensitivity, and false rejection risks.
6. **Preserve pre-observation reasoning.** Capture assumptions, hypotheses, predictions, and experiment criteria before execution. Never rewrite history after seeing a result. Label retrospective reconstructions honestly.
7. **Preserve every CI result independently of its provider.** Passing, failing, cancelled, timed-out, skipped, blocked, and inconclusive runs are part of the engineering record. Native CI retention is not the durable archive.
8. **Scope every conclusion.** Distinguish model conformance, test-environment results, deployed-system behavior, and actual external-resource settlement. Evidence about one is not proof of the others.
9. **Make limitations visible.** Report what was not tested, environmental blockers, unverified assumptions, confidence, and the next smallest resolving test.
10. **Separate observation from decision.** Test output, interpretation, finding, recommendation, and authorized acceptance are different records. A reviewer consensus is not a substitute for authority.
11. **Preserve methodological history.** Contrary evidence and subsequent decisions may supersede an earlier interpretation, but must not silently erase the observation, its original context, or the reasoning that generated it.
12. **Avoid gratuitous ceremony.** Scale the investigation to the consequence of a wrong conclusion. Reuse existing evidence and mechanisms; do not create gates merely to accumulate green checks.

These are **proposed** principles unless already established independently in a canonical source. This document does not retroactively classify historical work as compliant.

## 4. Verification selection and execution protocol

This is a logical checklist to embed in existing VSDD/project activities, not an imposed sequence of new workflow phases. For trivial changes, a compact record referencing the relevant acceptance check may satisfy several steps.

### 4.1 Establish the target and question

Identify the actual object (revision, service, interface, property, environment); source of the proposed guarantee; authoritative requirement owner; relevant constraints; and candidate outcomes. Distinguish a product requirement from an external maintainer's claim and a research hypothesis.

For an empirical investigation, record existing observations, competing explanations, assumptions, and prediction **before running the deciding test**. For routine scheduled CI, link to an already versioned specification and test plan rather than inventing a fresh hypothesis for each repetition.

### 4.2 Design the evidence question

Define compliant and violating behaviors where they can be specified legitimately. State the evidence that would support, challenge, or leave the claim unresolved; the failure consequence; and whether a finite test can substantiate the proposed level of confidence. Reject tautological or circular criteria.

### 4.3 Select the least costly sufficient method

Compare relevant options on discrimination, assurance strength, execution time, cloud/compute costs, dependencies, reversibility, impact on live users, reproducibility, and remaining trust assumptions. Record why the selected method is adequate. A small read-only inspection may precede a riskier live transaction; a formal or exhaustive check may be preferable to a broad example suite when the state space permits it.

Method-selection outcomes are **SELECTED**, **NOT_APPLICABLE**, **NO_NEW_TEST**, or **UNRESOLVED**. The latter three require a short reason and consequences. If evidence cannot be obtained without a prohibited or unsafe action, report **BLOCKED** instead of substituting a weaker claim.

### 4.4 Specify and qualify the check

Record the oracle (how expected behavior is determined), fixture and environment assumptions, execution boundaries, and controls that could expose a broken test. Prefer an independent oracle where feasible; a test that reproduces the implementation's own algorithm may copy its error.

When constructible without inventing requirements, pair a violating case that must be rejected with a compliant neighboring case that must pass. This detects both accept-everything and reject-everything implementations. Mutation, fault injection, metamorphic relations, independent reference examples, or manually verified controls can help qualify the instrument. The selected technique should be justified, not automatically imposed.

### 4.5 Execute and capture evidence

Run at the relevant interface and environment. Record exact code/specification revisions, commands or procedure identifiers, test data or deterministic seeds, runner/tool version where material, result, observed behavior, logs and artifact references. Distinguish an assertion failure from an import/setup error, infrastructure outage, timeout, unavailable authorization, or invalid test fixture.

Do not call a local green test a successful production integration test. Do not call an unrun generated suite verified. Repeated runs may establish consistency, not general proof.

### 4.6 Interpret independently and decide

Separate the observed result from the supported claim and from the decision. An independent reviewer should receive the artifact, claim, relevant canonical definitions, and minimal needed assumptions, not automatically the builder's persuasive history. For research, the instrument's quality and the target's behavior are separate evaluation objects.

Record authorized acceptance, revision, rejection, deferral, or new experiment, with affected requirements and superseded conclusions. An inconclusive or no-change result is a legitimate terminal outcome.

### 4.7 Feed back into the system

Link new observations to challenged assumptions, changed decisions, regression guards, updated specifications, and future monitoring. Reopen previously accepted conclusions when new contradictory evidence appears. Preserve all earlier evidence and provenance.

## 5. Method library: selection, not universal mandate

The following are examples, not a fixed shortlist or required stack:

| Method | Especially useful for | Important limitation |
| --- | --- | --- |
| Focused example / unit tests | Pure rules, boundary inputs, regressions | Coverage does not establish meaningful assertions |
| Integration / contract tests | Component and API agreements | Mocks may not match provider reality |
| Live-interface / end-to-end tests | Deployment, browser journeys, external service behavior | Can be costly, flaky, unsafe, or environment-dependent |
| Red–green–refactor–mutate | New or repaired correctness behavior, test sensitivity | Historical green tests do not become original red–green evidence |
| Property-based / metamorphic tests | Broad input spaces, invariant relationships | Generated cases and oracles still need qualification |
| State/model exploration | Guards, ordering, concurrency, authority, recovery | Model correctness does not establish realization conformance |
| Formal / exhaustive verification | Bounded or mathematically expressible guarantees | Valid only under stated assumptions and abstraction boundaries |
| Static analysis / source inspection | Structural, typing, dependency, security constraints | May not demonstrate actual runtime behavior |
| Fault injection / adversarial tests | Recovery, fail-closed behavior, resilience | Test-induced failures must be contained and reversible |
| Environmental perturbation tests | Timing, contention, resource limits, dependency and recovery boundaries | Stress-related failures require attribution; results depend on measured conditions |
| Operational observation / monitoring | Continuing deployed invariants, regressions | A passing probe does not establish complete system health |
| Independent or clean-room review | Specification fidelity, assumptions, missing cases | Agent agreement is not executable evidence |

A project may combine methods. Every proposed additional gate should name the failure mode it prevents, its acceptance criteria, its false-accept/false-reject risk, and the evidence that the gate itself works. Avoid blanket mutation-score or coverage thresholds until their utility is demonstrated for the relevant class of guarantees.

### Red–green–refactor–mutate is a selectable protocol

When selected, distinguish:
- **RED:** the focused test fails on the pre-fix implementation for the intended behavioral reason, not a setup error;
- **GREEN:** the minimal correction passes, including relevant nearby valid cases and regressions;
- **REFACTOR:** behavior remains unchanged while code is improved and checks are rerun;
- **MUTATE:** reintroducing the original defect or an appropriate targeted equivalent in isolation causes the relevant check to fail; restore and recheck the correct version.

Keep a contemporaneous red-before-fix record distinct from **retrospective mutation verification**. A mutation that survives because it targets the wrong guard cannot be scored as a meaningful sensitivity failure without diagnosing the mismatch. This protocol remains provisional beyond its currently documented resource-solver scope until adopted explicitly.

### Environmental perturbation testing

**Status: proposed selectable technique, not a mandatory stress gate.** A reported observation ([Jim Calabro, Bluesky, 2026-10-25](https://bsky.app/profile/calabro.io/post/3myp675zzok2r)) suggests rerunning a test suite during heavy CPU contention to reveal latent failures. That observation is a **hypothesis worth evaluating**, not empirical proof that saturating CPUs is universally effective or safe. The broader method is to deliberately change environmental conditions to challenge assumptions about timing, resources, isolation, recovery, and external dependencies.

**Selection question.** Could a permitted environmental change expose a violation of this specific guarantee that ordinary testing would probably miss? Relevant changes may include CPU competition or throttling; reduced memory; disk-space, I/O, or filesystem latency; constrained network throughput, latency, packet loss or disconnection; process interruption/restart; concurrent requests; dependency outages; clock/time-boundary effects; and scheduling variation. Choose only conditions relevant to the target claim. Not every project or component benefits from every perturbation.

**Experimental protocol (when selected):**

1. **Freeze the guarantee, hypothesis, expected invariant, and failure criteria before running.** For example: "Under CPU contention, concurrent reservation attempts must not both commit the same inventory unit." State which performance degradation, timeout, or partial service is permitted by the requirement. Do not invent an unconditional availability guarantee.
2. **Establish a baseline** with the same test suite, inputs, code/spec revisions, and comparable environment before perturbation. Record baseline failures and variability; a pre-existing flaky test is not a newly exposed application defect.
3. **Isolate and vary one dimension first.** Prefer bounded resource controls in a disposable runner, container, or VM. Record *achieved* pressure (for example, CPU throttling and contention measurements), not only configured load. CPU quota/throttling and competition with CPU-consuming work are distinct experiments; record which occurred. Expand to combined conditions only after single-factor evidence is interpretable.
4. **Repeat and compare.** Retain run counts, seeds, load configuration, environmental metrics, error types, durations/latencies, and whether failures recur. Random timing may need repeated trials and minimization; one success or one incidental failure must not be overgeneralized.
5. **Classify the cause rather than counting any red result as a defect.** Distinguish (a) a violation of the application or system invariant, (b) a test fixture/oracle/harness defect, (c) expected degradation within the specified envelope, and (d) environmental or CI infrastructure failure. Use additional discriminating tests to resolve ambiguity; leave unresolved cases INCONCLUSIVE.
6. **Preserve both baseline and perturbed records** in the evidence archive with pre-run rationale, host isolation boundary, relevant configuration, measured pressure, outputs, interpretation, and later decisions. A suspected defect becomes a regression guard only after adequate confirmation and attribution.

**Safety and applicability.** Do not indiscriminately saturate a shared development host, production service, externally owned system, or live customer workflow. Protect provider limits, sensitive data, neighboring workloads, and resource budgets; define stop conditions, cleanup, and any required operator approval. For the currently resource-constrained development VPS, favor isolated cloud runners or bounded containers/VMs with independently verified resource limits, rather than host-wide stress. Host-level experiments are separate, explicitly justified work. Stress tools are instruments, not proof of defect or performance.

**CI integration.** Baseline CI remains independent of perturbation campaigns. Run relevant perturbations selectively on dedicated PR, scheduled, or pre-release routes when their added evidentiary value justifies cost; do not mandate full stress suites on every commit. GitHub Actions, GitLab CI, Tangled Spindles, and other runners may execute the same scenario, but different hosts, kernel settings, and resource controls must be recorded before comparing outcomes. Capture and durably archive failing **and passing** runs. Distinguish performance benchmarks from stress-induced correctness tests: stressing a machine changes measurement conditions and may make throughput comparisons misleading.

**Candidate pilots.** Try one bounded, non-production test each for resource-solver concurrency/admission, an HMS reservation-state invariant against a controlled mock or test backend, and a Trip'n deployment/invariant-check harness. An experimentally observed improvement would justify adding a reusable profile; failure to discover relevant defects, excessive cost, or nondiscriminating flaky results should limit or reject the technique's broader adoption.

### Relationship to the debugging method

The sibling [ASES Debugging and Fault Isolation Method](ASES%20Debugging%20and%20Fault%20Isolation%20Method%20-%20Proposal.md) starts with an observed discrepancy, separates competing causes across relevant failure boundaries, and chooses cheap discriminating experiments before making a correction. This testing method supplies qualified verification instruments and regression/acceptance evidence when needed. Both inherit the same EDASES obligations to preserve pre-test reasoning, execution artifacts, limitations and downstream decisions; neither creates a new mandatory development phase. A working intermediate probe does not resolve a debugging case until the originally requested operation is verified at its actual surface.

### Ontology review as an assurance specialization

The existing [Ontology Reviewer](../roles/Ontology-Reviewer.md) evaluates conceptual fidelity **before** a proposed guarantee is translated into tests and, when meaningful, **after** a completed artifact claims to implement fixed canonical concepts. This is distinct from proving that a test is sensitive to a behavior violation.

Before freezing a substantial new specification or test design, select exploratory ontology review where terms such as **requirement**, **claim**, **property**, **test run**, **evidence**, **finding**, **acceptance**, **monitor state**, or **external settlement** are conflated or ambiguous. A test suite can be green while enforcing a category error. When canonical concepts are fixed and a completed assurance artifact claims to preserve them, a post-build clean-room ontology conformance review can attempt to falsify the semantic mapping.

Invoke the specialist only for a material conceptual risk; use a cheaper direct comparison when sufficient. Record findings and their evidential links under the same project provenance rules, without treating reviewer agreement as proof of test correctness. An ontology review cannot replace test-instrument qualification, behavioral verification, real-interface testing, or authorized acceptance. The selection mechanics are proposed in docs/ORCHESTRATOR.md, not a new testing phase.

## 6. Assurance intensity: per claim, not per repository

Choose effort based on potential harm of an incorrect conclusion, reversibility, trust boundaries, external side effects, data sensitivity, concurrency, operational exposure, novelty, and strength of existing evidence.

- **Low-consequence or cosmetic:** observable acceptance with a focused inspection or test and a concise evidence link may be sufficient.
- **Ordinary behavioral:** traceable spec, discriminating controls, affected regressions, and appropriate independent review or integration checks.
- **High-consequence or safety/authority-critical:** stronger qualification, negative/positive boundaries, independently derived references, fault/concurrency cases or proof as relevant, and verification at the real interface before consequential claims.

These are examples of tailoring, **not a mandatory three-tier classification**. A single project can contain all kinds of guarantees. The purpose is to spend evidence-gathering effort where it changes risk or confidence, not to reward maximal test volume.

## 7. Evidence and reasoning record

### 7.1 Minimum conceptual record

Use stable identifiers and explicit typed relationships between objects. Physical schemas and storage implementations are downstream choices. The record must be sufficient for a later independent investigator to recover:

| Record group | Minimum meaning |
| --- | --- |
| Identity | Project/monorepo, case/claim/experiment ID, run ID, creator/runner, timestamps and source revision |
| Before-run reasoning | Observation, hypothesis, competing explanations, assumptions, expected behavior, planned falsifier, rationale for selecting method, frozen criterion revision |
| Method definition | Requirement/spec source and revision, test/harness version, fixtures, inputs/seeds, environment/interface, oracle and trust assumptions |
| Execution | Platform and runner identity, workflow/command, exit status, duration when available, individual checks and actual observations, infrastructure errors |
| Retained artifacts | Manifest with hashes, size, content type, storage location, access class, log/report/trace/screenshot references and capture completeness |
| Interpretation | Result classification, supported/contradicted claim, confidence, WHAT-NOT-TESTED, alternate explanations and limitations |
| Decision | Authorized outcome, reason, affected requirements/records, supersession links, subsequent tests or monitoring |

Preserve causal relationships such as **ASSUMPTION_MOTIVATES_TEST**, **TEST_EXAMINES_CLAIM**, **RUN_EXECUTES_TEST**, **ARTIFACT_EVIDENCES_RUN**, **FINDING_INTERPRETS_OBSERVATION**, **DECISION_USES_FINDING**, and **NEW_EVIDENCE_CHALLENGES_DECISION**. These are conceptual links, not a mandatory database schema.

### 7.2 Capture and retention

**Proposed retention rule:** every CI run is indexed and its complete available test results and diagnostic artifacts are durably archived **outside the native CI provider**, independent of outcome. Full raw outputs should be captured when safe and feasible; do not replace them with a green/red summary. Routine local investigations selected as evidence-bearing work should use the same semantics.

- Record PASS, FAIL, ERROR, INCONCLUSIVE, BLOCKED, CANCELLED, SKIPPED, and NOT_RUN distinctly; separate **execution status** from **claim conclusion**. A no-discrepancy observation supports only its tested scope.
- Preserve a before-run plan or reference to its pre-existing frozen version; later interpretation is appended rather than rewriting that plan. Retrospective entries identify themselves as retrospective.
- Use an index and small structured manifests in versioned project knowledge; store large artifacts separately in a project-associated durable repository or object store. Use hashes and stable references to detect loss and enable controlled deduplication. Do not rely on a CI provider URL as the only copy.
- Treat a missing, incomplete, corrupt, or inaccessible archive as an **evidence-retention failure**, distinguishable from the outcome of the underlying test. A test may have run successfully while its evidential record is not durable; do not claim full verification or archival success without checking.
- Protect secrets, personal data, payment information, and live credentials: minimize collection, redact before external storage, set access controls, and record when necessary redaction limits reproducibility. Logs should never be made public merely because the project is open source.
- Define storage ownership by project and account, backup/replica needs, access and deletion rules, auditability, expected volume, and retention/archival lifecycle **before adopting a concrete provider**. R2, Backblaze, other free storage, or an internal service are candidates, not mandated ASES infrastructure. Storage limits and terms must be verified at adoption.
- Prefer append-only or immutable historical snapshots for research evidence. Corrections and supersession references preserve the original interpretation; any legally or operationally required deletion is recorded in the index where safe.

A permanent-retention aspiration must be paired with an actual capacity and recovery plan; the detailed lifespan, replication, and archival verification cadence remain open decisions. No silent garbage collection of evidence-bearing records.

### 7.3 Provenance and independence

Record source/spec revision, test revision, runner environment, and relevant external service state separately. When test design and implementation share the same agent or code path, record that correlation risk. A second CI provider or second execution of an identical oracle can check reproducibility; **neither alone is an independent oracle**.

Do not infer that a passing synthetic test demonstrates real quota accounting, payment settlement, transactional durability, provider availability, or correctness of an unobserved distributed system.

## 8. CI and cloud execution are interchangeable routes

GitHub Actions, GitLab CI, Tangled/Spindle, local hosts, remote development instances, and future execution environments may all run relevant checks. ASES chooses assurance **requirements**, not a compulsory CI service.

A portable downstream CI evidence contract should require each route to emit a common manifest and export its results to the project archive; provider-specific workflow definitions may differ. Test entry points should be reusable when practical; do not impose a framework rewrite to achieve cosmetic consistency.

Use the least costly suitable location and frequency:
- **In-task/local:** fast discriminating checks while implementing or investigating.
- **Pull request/merge gate:** deterministic relevant acceptance and regression checks; fail or block according to the actual requirement.
- **Scheduled/release:** more expensive campaigns, long-running tests and evidence-retention integrity checks where valuable.
- **Post-deploy/live:** read-only production invariants and separately authorized controlled transactions where necessary.

Allow different routes for the same workload where cloud resource/cost constraints justify them. Do not assume self-hosted runners are free compute: they compete for local CPU, RAM, storage and operational attention. CI run metrics and outcomes should eventually feed the resource solver and Observer, without making either a prerequisite to the first implementation.

An archive/export failure should produce a visible distinct diagnostic. Whether it blocks a merge or deployment must be justified by the applicable assurance requirement, not silently inferred from this draft.

## 9. Test and gate outcomes

Never reduce all results to a boolean:

- **Execution:** PASS / FAIL / ERROR / INCONCLUSIVE / BLOCKED / CANCELLED / SKIPPED / NOT_RUN.
- **Claim evaluation:** SUPPORTED_WITHIN_SCOPE / CONTRADICTED / UNRESOLVED / NOT_TESTABLE_AS_STATED.
- **Acceptance:** ACCEPT / REVISE / DEFER / REJECT / ESCALATE, attributed to the authorized decision maker.
- **Evidence quality:** QUALIFIED / PARTIALLY_QUALIFIED / UNQUALIFIED, with reasons and a distinct archive-completeness marker.

The exact enum names are proposed and subject to reconciliation with existing EDASES research vocabularies. In particular, the experimental *Guarantee-Driven Testing* framework uses NO_DISCREPANCY and CONFIRMED_DISCREPANCY; do not silently reinterpret those research outcomes as formal universal proof.

A gate must distinguish absent evidence from evidence of failure, and must be tested against deliberately invalid **and** legitimately valid cases where possible. A test or gate may itself be the object under investigation.

## 10. Project adaptations for initial study

| Project | Typical focus | Evidence boundary that must not be skipped |
| --- | --- | --- |
| Rock Solid Sites | Static build, accessibility, usability, performance, no-unnecessary-JS, link and deployment checks | Automated scores are incomplete accessibility evidence; source checks do not establish deployed behavior |
| Trip'n | Multi-property identity, booking handoff, valid bookability, live routing, CI/deploy invariants | Provider/account state and customer-facing production behavior differ from local fixtures |
| HMS / Beds24 integrations | Reservation and payment invariants, malformed input, concurrency, retries, third-party contracts and rollback | Simulations cannot prove external booking/payment settlement; sensitive live tests need separate authorization |
| ASES / resource solver | Specifications, numerical references, transitions, admission/allowance rules, mutation sensitivity, reproducible experimental runs | Local prototypes and synthetic budgets cannot establish provider billing or distributed atomicity |

Adaptations should link to inherited methodological obligations and state explicitly what differs. No project is required to install a universal monorepo harness merely to be compatible with the reasoning/evidence model.

## 11. Pilot and falsification plan

**Pilot only; no automatic ecosystem rollout.** Select at least two unlike substrates:

1. **ASES resource-solver tests:** reconstruct links from assumptions and frozen claims to existing recorded green tests and retrospective mutation results; preserve the precise distinction between historical and contemporaneous red evidence.
2. **Trip'n production-invariant Action:** capture an actual successful or failing execution and its full available logs, detector self-test, workflow revision and archived evidence without depending on GitHub's retention period.
3. **Optional HMS controlled diagnostic:** exercise the same schema on an existing read-only or safely recorded Beds24 experiment; do not run a live state-changing booking or payment test merely to validate the methodology.

Evaluate whether a separate reviewer can reconstruct the original question, expected outcome, test execution, actual observation, limitation, and subsequent decision without asking the builder for missing context. Demonstrate that (a) an intentionally broken test is detected, (b) a valid neighboring case is not rejected, (c) an archive failure is visible, (d) a no-new-test choice can be justified, and (e) a second CI route can read the common record without changing the claims.

Measure run cost, storage footprint, cognitive/documentation overhead, reviewer effort, and defects or false conclusions prevented. Compare against the current baseline; **a heavier protocol with no measurable reliability or traceability benefit is a failure of the proposal**, not a reason to declare more gates necessary.

## 12. Unresolved decisions before promotion

- Required minimum evidence for low-risk changes versus high-consequence guarantees; whether risk profiles should be formal registries.
- Which test changes warrant mutation/controlled-failure proof; whether mutation-score targets can be justified at all.
- Treatment of randomized, nondeterministic, probabilistic, and external-service tests, including when environmental perturbation campaigns add enough discrimination to warrant cost.
- Exact evidence schema, allowed corrections, privacy/access tiers, and common outcome vocabulary.
- Durable retention duration, storage owner, backup verification, handling of sensitive artifacts, capacity exhaustion, and disposition of historical evidence.
- Whether an archive failure blocks specific CI gates or merely produces an independent evidence-integrity failure.
- How independent reviews are selected and how to evaluate whether they add value.
- Choice and benchmarking of GitHub, GitLab, Tangled hosted/self-hosted CI, and other cloud execution routes.
- How to link operational evidence into the future Observer and resource solver without making either an architectural prerequisite.
- How to measure methodology benefit against time, token use, storage, and complexity.

## 13. Promotion criteria

Do **not** mark this document Active/Canonical solely because it has been committed. Promotion requires: reconciliation with VSDD and other canonical methods; independently reviewed, falsifiable claims about the method; pilot evidence demonstrating that its selection and retention rules work; explicit decisions on unresolved mandatory requirements; and an approved path to update downstream requirements, project adaptations, and operational documentation.

**Target principle:** preserve engineering reasoning **before** gathering evidence, the evidence **as actually gathered**, and the decisions **afterwards**—independently of which test, language, CI provider, execution host, or storage system was used.
