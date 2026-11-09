---
title: Agent Recovery Investigation Treadmill — UniFi UDR Incident, 2026-11-08 to 2026-11-09
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - AGENTS.md
  - docs/standards/Documentation Standard.md
related_documents:
  - docs/research/registry/Failure-Matrix.md
  - docs/proposals/2026-11-09-shared-investigation-decision-records.md
consumed_by:
  - docs/proposals/2026-11-09-shared-investigation-decision-records.md
  - skills/workflow-orchestration/SKILL.md
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-09
---

# Agent recovery investigation treadmill — incident record

## Scope and evidentiary status

A real, authorized repair of a UniFi Dream Router (UDR) and two mesh extenders was executed through a Windows-hosted Codex agent during 8–9 November 2026. Multiple model sessions, including Terra and Luna, performed work. The operator supplied the shared agent transcript and described substantial model-usage expenditure (approximately 94% of one five-hour allocation in one session). This report analyzes **agent decision quality and investigation control**, not the merit of a particular vendor, model family, or network topology.

This is a retrospective analysis, not a new live diagnosis. Evidence below is based on reported tool runs, commands and final results in the operator-supplied transcript. Some tool output is summarized or collapsed, and the terminal state was observed immediately after repair rather than over a long stability interval. Do not substitute interpretations below for raw logs when testing specific causal claims. The original transcript contains operational identifiers and private configuration; this public report deliberately omits identifying network addresses, device secrets and local account paths.

## Original objective and actual outcome

**Original objective:** Restore the router, the existing internet connection, and both mesh extenders to working service. Preserve material ISP configuration. The operator did not require retaining historical controller statistics or avoiding ordinary brief service interruptions.

The initial defect was a corrupt MongoDB/WiredTiger store for the UDR's integrated UniFi Network application. An isolated attempted database repair failed with evidence of a missing collection file. The agent preserved the old database and initialized a fresh store. Database and application processes restarted successfully and existing WAN/Wi-Fi continued working.

This **intermediate repair** invalidated management state: the fresh controller had no corresponding gateway or extender device records, and old device informs were not recognized. Both extenders then underwent repeated discovery, adoption, provisioning, and offline cycles. One device was reset early; another remained reachable temporarily.

The successful final repair was obtained only after inspecting **effective runtime behavior**, not merely controller settings: the UDR advertised a valid hidden 5 GHz mesh parent, but the extenders had no active association. The agent used direct setup access, a verified mesh profile and subsequent controller provisioning. Both extenders were reported online at the end; one had active client traffic and the other had active radios but no clients at the final observation. Long-term database and mesh stability remained unverified.

The exact original condition that broke the extenders' effective mesh configuration was not conclusively isolated. A missing controller gateway record was initially hypothesized to prevent mesh-parent operation; the live radio observation **contradicted** that explanation.

## Chronological decision points

| Boundary | Observed event | Decision-quality finding |
| --- | --- | --- |
| Database | Missing WiredTiger collection; isolated repair failed; original bytes preserved; clean database started | Reasonable immediate isolation, but downstream device identities/configuration were not accounted for as recovery obligations |
| Controller startup | Application and MongoDB became healthy with unchanged WAN | Healthy process state was an intermediate milestone, not original user-facing acceptance |
| Device identity | Gateway and extenders sent unrecognized encrypted management messages after loss of records | Agents needed to distinguish authentication/adoption state from live traffic-forwarding state |
| WAN safeguards | Extensive checks of persistent config, runtime rollback, offline restoration, backup and hypothetical wired recovery | Material WAN risk was legitimate for gateway reprovisioning, but the precaution expanded into blockers for operations that did not change WAN |
| Initial extender | Reset and mobile/Bluetooth/QR/advanced adoption attempted; setup network observed | Reset occurred before the relevant wireless dependency was confirmed; discovery/adoption success did not mean uplink success |
| Provisioning | Extenders appeared adopted, became offline, and failed reconnection | Repeated controller status checks and restarts brought limited new information about the first failing boundary |
| Radio conditions | Weak reported signal prompted relocation; extender remained offline near gateway | New negative result should have constrained weak-signal hypothesis and prompted a different boundary test |
| Redundant reset proposal | Agent recommended repeating physical reset even though saved controller changes could not reach offline device | No demonstrated changed precondition explained why repeating reset would work |
| SSH access | A later agent stopped over an unverified host key; preexisting evidence contained the relevant verified key | Existing evidence was not retrieved before promoting a solvable local issue to a global blocker |
| Execution channel | Agent joined an extender setup Wi-Fi without preserving its independent internet/control route, interrupting its own remote execution path | Diagnostic operation endangered the instrument/control channel; independent route was available |
| Final focused diagnosis | Confirmed UDR's hidden mesh parent active, observed zero extender associations, then configured a verified profile via direct setup access | First useful discriminating localization; original service was recovered |

These rows are **not** proof that every earlier action was pointless. Preserving the WAN values, the backup, and a verified external route had real value. The error was promoting *additional, unproven safeguards* to prerequisites for unrelated low-risk operations, while repeating higher-disruption actions with insufficient causal justification.

## Failure mechanism A: investigation without decision value

The agents produced a large number of observations—offline statuses, controller API records, discovery attempts, restarts—that did not consistently narrow the live set of hypotheses. They often returned to the same action following a negative result.

The critical missing question was: **Which decision would change if this test succeeded, failed, or was inconclusive?** If all plausible results produce the same next action, the test ordinarily has little diagnostic value. Monitoring a time-dependent transition can be valid, but it needs an explicit window and stop condition.

Three distinct anti-patterns appeared:

1. **Status polling as investigation:** repeated queries of an offline controller record without a theory of when or why it should change.
2. **Equivalent intervention replay:** another reset/adoption cycle under substantially equivalent prerequisites, with no justification for a different outcome.
3. **Evidence rediscovery:** obtaining or demanding facts that had already been established in available project artifacts, especially the verified SSH identity.

The underlying failure is not a lack of logged data, but a failure to make **negative evidence operationally constraining**. Repeated failure should update permitted next actions, not merely become another paragraph in a report.

## Failure mechanism B: objective displacement and spurious blockers

The original goal—working router and extenders—was repeatedly displaced by intermediate aims: clean database, operational controller process, adopted-device record, credential hygiene, offline WAN restoration, and tooling setup.

Some intermediate work was indispensable. It became harmful when agents treated an unrelated or disproportionate concern as a reason to stop the entire repair.

The safeguard-relevance test the agents needed:

- Which *specific pending operation* is blocked?
- What credible material harm, authorization violation, or irreversible effect would proceeding cause?
- Does existing evidence already resolve the prerequisite?
- Can useful, authorized work continue independently while this operation remains blocked?

For example, overwriting static WAN parameters through gateway reprovisioning had a credible service-loss risk. Reading live radio configuration did not carry that same risk. A controlled restart normally produces a brief service interruption; it does not automatically require a separately proven persistent restore. Temporary credential cleanup was authorized for later and should not have blocked work.

This was not a uniform preference for safety. The agents sometimes avoided low-risk inspection while repeatedly proposing disruptive extender resets. The actual defect was **risk and blocker relevance**, not simply excessive caution.

## Shared systemic cause

The two failures are complementary:

- **Unnecessary continuation:** an agent undertakes work that is not expected to change the next decision.
- **Unnecessary suspension:** an agent stops authorized work over a requirement not causally necessary for that work.

Both indicate loss of **objective-conditioned decision control**: local actions are no longer reliably evaluated against the user's unchanged original acceptance criterion, current evidence and the next consequential decision.

The pending ASES debugging proposal (currently on the separate `proposal/testing-and-assurance-method-2026-11-01` branch) and AGENTS rules already call for cheapest discriminating tests, original-surface acceptance, reuse of evidence, explicit negative results and operator-thinness. This case shows that general prose guidance was insufficient in an extended agent session. More prescriptive instructions alone would risk adding another burden.

## Candidate low-machinery response

Pilot a **live shared investigation record**: a fixed original objective and acceptance criterion, current state and next decision, followed by short append-only experiments/results. The executing agent writes updates while working; a supervising Chat/Work session can inspect those updates during execution rather than receiving only a terminal summary. A lightweight schema check verifies the *shape* and required fields of entries, not truthfulness or causal reasoning.

Important properties:

- A test result must say what was observed and what it means for the next action; distinguish target failure from test/tool failure.
- A repeated intervention notes the relevant changed condition, or is visibly marked as repetition without new justification.
- A proposed blocker identifies the operation prevented and the concrete consequence.
- The original objective and actual acceptance remain visible during every intermediate repair.
- The log retains rejected explanations and earlier observations without rewriting history.
- No new decision engine, semantic classifier, custom MCP or mandatory ritual is presumed. The proposed future execution engine may eventually enforce these checks; the initial experiment relies on a shared page, agent instructions, and minimal structural validation.

See the separate experimental proposal for storage, schema, workspace organization and pilot criteria.

## Qualification and limits

Test the record across multiple domains, not only routers: cascading database/authentication recovery, dependency upgrades, a broken CI workflow and a case where repeating a bounded test *is* justified (intermittence). Also include a true safety/authorization blocker so that the method is not rewarded merely for acting aggressively.

Measure **redundant investigations avoided**, invalidated hypotheses carried forward, unnecessary human interventions, time/compute per first decisive result, unnecessary stoppages and user-facing acceptance quality. A method that increases log maintenance without measurable improvement should be simplified or discarded.

**No policy promotion or causal generalization is justified by a single observed incident.** Retain this report as empirical research with stated uncertainty.

## Open follow-ups

- Verify long-term controller database health and the earlier filesystem anomalies separately; final recovery did not establish their cause.
- Verify extender coverage and stability over ordinary operation, not solely immediate adoption status.
- Determine whether shared records are directly available and writable from Chat, Work and Codex in the selected Projektor workspace.
- Test the limited validator and compare its decision quality with the existing unstructured workflow.
