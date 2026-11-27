---
title: ASES Debugging and Fault Isolation Method
program: ASES
layer: Methodology
document_type: Methodology Specification
status: Draft
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/standards/Documentation Standard.md
  - docs/methodology/ASES Bounded Project Build Method.md
related_documents:
  - docs/proposals/2026-11-02-testing-debugging-ontology/testing-and-assurance-method.md
  - docs/methodology/State-Model Applicability and Reuse Method.md
  - docs/methodology/Implementation Realization and Assurance Selection Method.md
  - docs/research/registry/Failure-Matrix.md
  - docs/research/Workflow Topology Design and Reasoning Record.md
  - docs/research/Guarantee-Driven Testing and Goal-Substitution Resistance.md
  - docs/research/crosslink-db-rollback-incident.md
  - docs/research/regression-testing-orchestrator-compliance.md
consumed_by:
  - project-specific diagnostic playbooks (proposed)
  - MCP/connector diagnostic profile (proposed)
  - CI and deployment diagnostic profile (proposed)
  - future Observer and execution-engine requirements (proposed)
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-02
---

# ASES Debugging and Fault Isolation Method

> **PROPOSAL — not adopted global policy.** This document captures recurring ASES debugging practice and develops it into a candidate reusable method. It does not supersede canonical AGENTS rules, VSDD, project safety controls, existing incident procedures, or the parallel proposed Testing and Assurance Method. Its empirical value and scope require review and piloting.

## 1. Purpose: find the failed boundary before selecting a fix

Debugging is an evidence-producing investigation of a **deviation between required and observed behavior**. Its goal is to localize and explain that deviation sufficiently to select a proportionate correction, recover the original behavior, and preserve the reasoning for future work.

The primary loop is:

**Observe deviation → bound the claim and system → enumerate competing explanations → run the cheapest discriminating test → update the evidence map → intervene only when justified → verify the original outcome → preserve the investigation.**

This is not a mandated sequence of tools or a substitute for VSDD. A successful conclusion may be **confirmed defect with fix**, **external cause with workaround**, **configuration or authorization issue**, **documented expected behavior**, **test/monitor defect**, **intermittent/environmental limitation**, **recovered without attributable cause**, or **unresolved with narrowed hypotheses**. Avoid inventing a fix to make an incident feel complete.

A symptom, a failed test, a suspected cause, a localized mechanism, a proven cause, and a completed remedy are **different claims**. Do not silently promote one to another.

## 2. Relationship to ASES, EDASES, and the testing method

- **EDASES:** retains the pre-investigation assumptions, rejected explanations, experiments, raw evidence, counterexamples, revisions of belief, negative findings, and cost/effectiveness of different diagnostic strategies. Debugging episodes are empirical data about the reliability of ASES and its tools, including evidence of ineffective tests.
- **ASES:** proposes a general fault-isolation method independent of programming language, service provider, tool, operating system, and repository layout. Projects specialize it to their actual failure boundaries.
- **Execution tooling:** gathers logs, inspectable state, tests, telemetry, reproduction artifacts and CI results, preserving them using a common evidence contract. Tooling assists diagnosis; it does not declare root cause or acceptance by itself.

The sibling *Testing and Assurance Method* selects and qualifies verification evidence for claims and invariants. **Debugging** starts with a discrepancy and chooses experiments to separate explanations; **testing** supplies some of the instruments and later validates the correction. Neither automatically requires the other to create extra workflow phases.

Apply the existing *Bounded Project Build Method* when a diagnosed change needs implementation: the smallest corrected behavior is specified, implemented and independently verified through its appropriate verification architecture. Diagnosis does not authorize unrequested redesign or architecture changes. The *State-Model Applicability and Reuse Method* may help when a failure involves lifecycle, guards, ordering, or recovery; do not force a state machine onto a non-state problem.

The current **AGENTS.md** already requires reasoning certainty (WHY / WHAT / HOW CERTAIN / WHAT-NOT-TESTED), cheapest discriminating tests, tool independence, operator-thinness and independently supported review. Those are current policy independently of this draft. This proposal specifies additional diagnostic practice; it must not claim the status of a canonical rule until promoted.

### Ontology review for diagnostic category and boundary errors

The existing [Ontology Reviewer](../../roles/Ontology-Reviewer.md) is a **selectable specialist review domain**, not a new debugging stage. Choose it when an investigation depends on contested or incorrectly conflated conceptual distinctions—for example **client tool exposure vs MCP backend health**, **trigger not delivered vs CI job failed**, **symptom vs root cause**, **provider acknowledgment vs durable settlement**, or **test harness failure vs application failure**.

An exploratory ontology review can clarify ambiguous failure boundaries before committing to a debugging model or invasive experiment. A post-build conformance review can independently challenge whether a finished diagnostic artifact maps observations to the correct canonical entities and boundaries. This does **not** validate a causal hypothesis by itself: discriminating runtime tests, real-surface acceptance and evidence of the actual mechanism remain necessary. Do not summon an extra model where a direct definition/identity check resolves the distinction. Review execution must retain the role's independent-family, minimal-context and authority constraints.

The [testing proposal](testing-and-assurance-method.md) may supply qualified diagnostic instruments; the Ontology Reviewer examines whether the **categories under examination** are coherent. Both feed the same evidence and reasoning record.

## 3. Proposed governing disciplines

1. **Original objective is the acceptance oracle.** Define what the operator/user actually needed. A green probe at an intermediate layer does not close the incident if the requested operation still fails.
2. **Observed facts before interpretations.** Preserve the exact error, affected interface, identity, environment, operation, time window, prior known-good state, and what was not observed. Distinguish direct observation, provider documentation, agent report, inference, and experiment.
3. **Shrink the search space.** Identify independently testable failure boundaries, competing hypotheses, and a discriminating result for each. Eliminate hypotheses when evidence warrants it; do not merely collect more logs.
4. **Prefer read-only, low-cost, reversible tests.** Rank experiments by likelihood of separating live hypotheses per unit of time, compute, money, risk, privileges, and disruption—not by how familiar a test command is.
5. **Observe one causal contrast at a time where practical.** Paired controls (working vs failing account, route, hostname, commit, environment, or permission set) are especially valuable. Freeze everything else possible and record unavoidable differences.
6. **Do not over-serialize diagnostic work.** Batch independent, cheap, read-only tests once the discriminating questions are known. Avoid one-conversation-turn-per-probe when a bounded sweep can eliminate several independent explanations safely.
7. **Measure the boundary actually reached.** Registration, connection, authorization, discovery, execution, and user-facing outcome are separate properties. Passing an upstream layer never proves a downstream layer.
8. **Do not equate absence of evidence with evidence of absence.** A missing tool, skipped scheduled job, absent log, cancelled run, API limit or lost telemetry may reflect the observing mechanism rather than the target.
9. **Instrument adaptively.** Prefer existing source/CI/log information before adding invasive diagnostics. Raise sampling or tracing only when the current evidence cannot distinguish hypotheses; stop excess instrumentation after the question is resolved.
10. **Safety and authority precede curiosity.** No speculative production edits, disabling security controls, broad destructive cleanup, secrets exposure, unauthorized account switching, or uncontrolled stress as a diagnostic shortcut. Capture a rollback path before any permitted state-changing probe.
11. **Diagnose the test itself.** Separate a target-system defect from a monitor, fixture, assertion, reference oracle, CI scheduler, or environment fault. An observed green result may be a false negative.
12. **Preserve chronology and negative results.** Record what was believed before each test, what was tried, the actual observation, what was eliminated, what remains unknown, and what decision follows. Do not overwrite earlier reasoning with hindsight.
13. **Use explicit stop/continue conditions.** Stop when the accepted original behavior is restored and verified; when a hypothesis is sufficiently supported and further probing would add no decision value; or when safety, authority, or evidence limits block progress. Resume only for a named, information-gaining next experiment.
14. **Do not outsource technical operations to the operator.** Shell, scripts, admin navigation, SSH, logs, environment configuration and command interpretation are agent work under canonical ASES operator-thinness doctrine. Request only genuinely irreducible human-identity or separately gated approvals, as a single clear action.

These proposed disciplines extend but do not replace existing binding source documents.

## 4. Diagnostic protocol

This is a **repeating reasoning loop**, not a fixed number of stages or obligatory artifact set. A simple incident may collapse to a symptom, one decisive control, a minimal fix and an acceptance check. A multi-service incident may repeat the loop for successive boundaries.

### 4.1 Establish the symptom, target and exact acceptance surface

Capture:
- **Requested outcome:** the actual user-facing, API, CI, or system behavior the operator wants.
- **Observed deviation:** exact error text/status and whether it is reproducible, intermittent, delayed, or merely reported.
- **Surface and identity:** client/product, tenant/account, authenticated role, environment, hostname, branch/commit, provider/model/runner version when relevant.
- **Time and comparison:** first observation, last known-good state, relevant changes, working neighboring paths, and whether the observer might itself be degraded.
- **Impact and constraints:** who is affected, sensitivity/production boundaries, severity, change restrictions, and success and stop criteria.

Do not start by assuming a programming-language defect, a particular service's fault, or that a failure at one layer describes every client or account. Do not diagnose from the error's wording alone.

### 4.2 Map the minimum fault boundaries

Represent only boundaries that could explain this symptom. Typical categories include:

| Boundary | Discriminating question |
| --- | --- |
| Product/client exposure | Is the requested capability/tool actually offered on this specific surface and account? |
| Registration/discovery | Is the provider, app, workflow or tool visible and active for this client? |
| Transport / reachability | Can the client contact the correct endpoint and complete the required protocol? |
| Authentication / authorization | Is the intended identity authenticated and permitted for the exact operation? |
| Request/contract/data | Is the request well-formed and is the expected state present at the authoritative source? |
| Runtime / business behavior | Does the relevant operation execute correctly after the preceding boundaries pass? |
| Persistence / settlement | Did a write persist or external side effect really occur, rather than merely returning a success acknowledgment? |
| Observer / monitor / scheduler | Was the check actually scheduled, run, and interpreted correctly? Is the telemetry fresh and trustworthy? |
| User-facing acceptance | Does the original requested operation work from the intended surface, not just an internal probe? |

The boundaries form a **causal map**, not a mandatory linear pipeline: some operations bypass stages, use multiple identities, or branch across components. The aim is to localize where the first observable divergence occurs and what that observation rules out.

### 4.3 Maintain a live, falsifiable hypothesis register

A compact working register is sufficient:

| Field | Meaning |
| --- | --- |
| Hypothesis ID | Stable label for one competing explanation |
| Basis | Evidence suggesting it, without overstating certainty |
| Prediction | What the next test should observe if the hypothesis is true |
| Discriminating control | What outcome would favor a competing explanation or falsify it |
| Status | OPEN / SUPPORTED / WEAKENED / ELIMINATED / UNTESTABLE |
| Remaining risk | What testing or access boundary is still missing |

Do not turn an isolated successful test into proof that all downstream functions work. When several hypotheses share a prediction, that test is not discriminating enough. Prefer a paired contrast over broad exploratory logs unless the contrast is unavailable.

### 4.4 Choose and run the cheapest informative tests

Use the following selection order **when suitable**, rather than a universal checklist:

1. Reuse already available evidence, existing test results, configuration snapshots, immutable source and authorized provider status information.
2. Verify the target identity, relevant tool inventory, version, route and effective account permissions at the exact failing surface; compare to one known-working control.
3. Run the smallest read-only or isolated probe that reaches one contested boundary; record raw response and whether the instrument worked.
4. If necessary, gather targeted logs, execution traces, CI run records, timing/resource metrics or a controlled reproduction.
5. Only after narrower tests are insufficient, use a bounded reversible configuration experiment, fault injection, perturbation, or code modification with explicit authority and recovery criteria.

A test must say which hypotheses its possible outcomes distinguish. Record its *expected* observations before executing when feasible. Capture result, raw evidence link, revised hypothesis statuses, confidence, and what remains untested. Batch independent nonmutating tests to reduce operator interruptions and conversation overhead; avoid parallel mutations of shared state.

**Budget rule:** choose the smallest test that changes the next decision. A cheap test with no diagnostic separation is wasted work; a modestly costlier decisive test may be better.

### 4.5 Classify results and select the next intervention

Separate:
- **Target fault established:** behavioral violation at a verified boundary.
- **Instrument fault established:** the monitor, test, agent, client feature exposure, or harness is wrong or missing.
- **External/provider condition:** permissions, billing, quota, provider limitation, unavailable service, or noncontractual behavior.
- **Environmental/temporal condition:** resource pressure, race, startup/shutdown timing, schedule omission, or intermittent execution.
- **Expected behavior / requirement mismatch:** documentation, configuration or expectations conflict with actual approved requirements.
- **Inconclusive:** evidence cannot yet differentiate causes, or a necessary test is blocked.

A provider or infrastructure issue may have a direct operational remediation without a source-code fix. Distinguish **proximate triggering condition**, **underlying mechanism**, and **systemic contributing factors**; do not claim one definitive root cause without causal evidence.

### 4.6 Change minimally and verify at both boundaries

Before changes, preserve baseline configuration, data version, permissions, rollback route, and the tests that should fail and pass. Select the smallest intervention the evidence justifies.

After a change, verify:
1. The **specific fault boundary** now behaves correctly.
2. The **originally requested user-facing operation** works through its real route and account.
3. Relevant neighboring **valid cases remain valid** and **invalid cases remain rejected**, where applicable.
4. Persistence, deployment and downstream settlement are observed **where claimed**, not inferred from internal acknowledgments.
5. The intervention did not create an unacceptable regression; rollback is checked after temporary experiments.

Use the sibling testing method for selecting regression tests, red–green or targeted mutation, integration checks, state-model checks, or live acceptance. Avoid retroactively labeling existing green tests as having demonstrated a red-before-fix failure.

A passing internal smoke test is progress, not closure. If no authorized fix is possible, preserve the bounded diagnosis, an actionable blocker and the cheapest remaining test; do not state that the incident has been repaired.

### 4.7 Preserve the episode and feed back into methodology

Record the complete chain: symptom → initial hypotheses → chosen discriminating tests → actual observations → eliminated explanations → selected action → verification → downstream decisions. Include unsuccessful tests and changed beliefs.

Retain execution evidence through the same portable, project-owned storage and provenance approach proposed in *ASES Testing and Assurance Method*. Native CI/MCP logs are not the sole archive. Emit findings to the EDASES failure-matrix research process when they generalize, and add only justified project-specific regression guards or diagnostic canaries. No incidental incident becomes universal methodology without independent evaluation.

## 5. Domain-specific diagnostic profiles (illustrative)

A profile supplies likely boundaries, probes, and safety constraints; it does **not** replace the universal reasoning loop.

### 5.1 Custom MCPs, plugins, and agent connectors

Check separately: **product surface / account support → installation/registration → activation → transport connection → identity/auth → tool discovery → exact tool invocation → observed side effect or result → security/isolation**. Not all systems use these stages; classify omitted stages as NOT_APPLICABLE rather than PASS.

A useful capability matrix names the *client surface, account identity, precise requested operation, reached boundary, result, and what was not checked*. Compare one successful route to the failing one. A provider working in Codex does not prove that the same feature is exposed to ordinary ChatGPT conversations; local backend success does not prove client discovery; tool listing does not prove correct execution; execution success does not prove confinement.

Cheap tests often start with a tool inventory and actual linked-account list before code changes, reinstallations, token rotations or VPS work. If a required connector is absent at the client surface, changing backend code is premature. Test authentication and effective permissions separately from mere connectivity. Validate the actual intended operation, not only health/ping. Preserve sensitive information safely; avoid broad shell execution as a default diagnostic substitute for a broken specialized connector.

### 5.2 CI schedule, workflow, and monitor anomalies

Distinguish **configuration intent**, **workflow trigger delivery**, **actual run creation**, **runner start**, **job execution**, **assertion interpretation**, **notifications**, and **production state**. A cron expression does not prove the intended number of executions took place; missing runs differ from failed runs; a green self-test does not prove that a detector catches violations.

Compare expected windows and actual run timestamps, trigger type, workflow revision, job outcome, failures/skips, provider limits and relevant events. Use synthetic or mutation-based detector qualification where appropriate. Do not change cron frequency or monitoring thresholds speculatively before identifying which boundary drops or delays runs. Preserve CI results and the reasoning behind monitor changes outside the provider's native retention.

### 5.3 Third-party business integrations (Beds24 / HMS)

Verify property/account/role identity, configured booking/rate rules, effective source-of-truth data, API or UI response, browser-visible behavior, and final downstream state separately. A payment field's presence does not prove payment collection, storage, compliance, or settlement. A read-only booking preview does not prove a submitted reservation.

Use paired property/room/rate/date controls with actual validity constraints before manipulating production settings. A controlled state change requires explicit authorization, recorded baseline, least-impact scope, immediate rollback, and post-rollback verification. Never use real guest/payment data merely to diagnose a UI defect.

### 5.4 Hosting, resource pressure, and intermittent behavior

Distinguish VM/host faults, process lifetime, memory/CPU/disk pressure, editor/server processes, network/DNS/redirect behavior, client rendering and observability. A stale status flag is not process liveness. Shared infrastructure problems should be isolated with one small reproducer before launching more agents or increasing concurrency.

Where timing/load may matter, use the testing proposal's **Environmental perturbation testing** under bounded, isolated, authorized conditions. Diagnose whether the failure belongs to application, harness, infrastructure or expected resource-constrained operation. Repeating an uncontrolled stress test is not causal attribution.

## 6. Evidence record and handoff contract

A minimally useful diagnostic episode should include:

- **Incident ID and scope:** project, service/client, environment, account/role (not secret), relevant commit/config versions, timestamps.
- **Original request and acceptance:** what user-facing operation failed and how success will be established.
- **Observed facts and provenance:** exact error, recorded observation, actor/tool, artifact IDs, verified versus reported nature, links to raw outputs.
- **Hypotheses and pre-test predictions:** include rejected alternatives and why a proposed probe is discriminating.
- **Experiments:** probe/test ID, tested boundary, baseline/control, change/no-change, time/cost/safety constraints, commands or procedure references, execution status, outcome and evidence hashes.
- **Inference:** which hypothesis was weakened/confirmed, WHY / WHAT / HOW CERTAIN / WHAT-NOT-TESTED; distinguish causal claim from correlation.
- **Intervention and recovery:** authorized fix/configuration change, rollback plan and result, revisions, focused and original-surface acceptance evidence.
- **Outcome and future obligations:** repaired / localized-no-fix / external-blocked / inconclusive / expected behavior; regression and monitoring follow-up, owner/decision, links to later episodes and any superseded conclusions.

The records should be append-oriented, portable across GitHub, GitLab, Tangled, local debugging, and future execution environments, with project-appropriate privacy controls. Retain incident failures, false alarms and null results—not merely final fixes. All raw or machine-recorded test evidence should remain separately identifiable from agent narrative.

For complex work, provide compact check-ins containing **verified findings, currently live hypotheses, next discriminating test(s), and blockers**. Check-ins should not force the operator to repeatedly authorize ordinary continuing diagnostic work that is already in scope. An end-of-session handoff must be sufficient for a new agent to resume without replaying the same expensive tests.

## 7. Anti-patterns and failure modes to test

A future adversarial qualification suite should include controlled examples of:

| Anti-pattern | Why it fails |
| --- | --- |
| Fix-first guessing | A configuration change or reinstall destroys evidence without isolating the failed boundary |
| One-error one-cause | Treats an error label as the root cause despite multiple possible origins |
| Wrong-surface success | A backend ping is reported as proof that the operator's client workflow is fixed |
| Passing-test overreach | A self-test that passes with a guard disabled is used to declare the monitor healthy |
| Repeated uninformative retries | Adds cost without separating remaining hypotheses |
| Multi-variable edits | Confounds which change caused recovery or regression |
| Status-as-liveness | Infers healthy processes from static flags rather than advancing evidence |
| Run-not-created vs failed-run confusion | Treats missing CI triggers as failures of an executed job |
| Temporal coincidence as causal proof | Assumes the latest change caused a failure without a controlled comparison |
| Production mutation without rollback | Causes user impact or irreversible state changes to satisfy curiosity |
| Silent external fallback | Substitutes a different tool/surface and declares the requested capability available |
| Lost negative evidence | Rewrites diagnosis history after a successful fix and hides rejected hypotheses |
| Unnecessary operator handoff | Shifts commands, console navigation or technical validation onto the operator |
| Premature escalation or stopping | Stops after a cheap failure without exhausting available safe discriminating tests |

Qualify the debugging method by testing whether an agent resists these failure modes and can isolate the correct boundary with fewer tests than a fix-first baseline. Do not reward incident closure counts or total probes as quality proxies.

## 8. Proposed pilot programme

Validate across contrasting real cases, using existing records first and marking reconstructions honestly:

1. **Custom MCP/connector exposure:** compare ordinary ChatGPT, Codex, and local backend capabilities for one previously failing connector. Test whether the method detects an absent client tool before suggesting backend changes. Use the documented surface/capability matrix; no additional permissions or shell bridging should be assumed.
2. **Trip'n GitHub Actions schedule anomaly:** distinguish configured 30-minute cron, actual scheduled run creation, job outcomes and detector correctness. Verify whether the method prevents speculative cron edits and separates a scheduling issue from a production outage. Historical reported run statistics must be rechecked against source evidence before use as formal pilot measurements.
3. **Beds24 card-field diagnostic:** evaluate the read-only paired-property and controlled rollback protocol as a test of causal isolation and authorization boundaries. No new production mutation is authorized by this pilot.
4. **Shared VPS and agent-liveness diagnosis:** validate that the method distinguishes cached status indicators from advancing process/tool evidence and avoids amplifying infrastructure failures via parallel launches.
5. **Optional historical incident:** apply to the Crosslink database rollback record, testing the distinction between internal database consistency and correctness of the authoritative dataset.

For each pilot, record **hypotheses eliminated per probe**, diagnostic cost/time, number of speculative changes avoided, fidelity of original-surface acceptance, evidence completeness, false attribution rate, and remaining uncertainty. A method that demands more process without improving isolation, safety or recoverability should be simplified or rejected.

## 9. Unresolved decisions and promotion

Before promotion to Active / Canonical:

- Reconcile overlapping terms and outcome codes with EDASES Failure Matrix, current AGENTS and the sibling testing proposal.
- Determine the threshold for demanding independent causal confirmation versus a sufficient operational workaround.
- Determine the minimal record for trivial repairs and how to archive ephemeral logs or secrets without disproportionate overhead.
- Qualify the proposed hypothesis/decision model against actual MCP, CI and third-party integration incidents.
- Establish reusable *profiles* only for demonstrated recurring boundaries; avoid a universal taxonomy that forces irrelevant steps.
- Define how the Observer records incident evidence automatically and how the resource solver uses diagnostic costs without becoming prerequisites.
- Run independent adversarial review, including deliberately misleading symptoms, stale logs, multiple simultaneous defects, intermittent failures, inaccessible external systems, and cases in which **no fix** is correct.
- Preserve conflicting conclusions and correction history; decide when a diagnosis is credible enough to generalize into research findings.

**Candidate governing principle:** *Reduce uncertainty at the cheapest relevant boundary, preserve the reasoning that made the test worth running, and claim resolution only at the originally requested outcome.*
