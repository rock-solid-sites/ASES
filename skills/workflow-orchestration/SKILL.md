---
name: workflow-orchestration
version: 0.1-draft
description: Choose and coordinate the smallest effective loop of reconnaissance, strategy, parallel testing, implementation, and verification based on uncertainty, task independence, evidence, and readiness.
status: provisional-reference
---

# Workflow Orchestration Skill

## Purpose

Choose the next work mode that most efficiently reduces material uncertainty or advances a sufficiently specified task. Use reconnaissance, orchestration, strategy, implementation, and verification as complementary modes that can be revisited as evidence changes. Do not force every task through every stage.

This skill governs workflow selection and handoffs. It does not replace domain-specific skills, the Strategy-to-Builder integration-packet method, or the Compact Prompt skill.

## Governing rule

Choose the **smallest evidence-to-decision-to-execution loop** that resolves the current blocker.

- Unknown mechanism, constraints, or baseline: **recon**.
- Multiple bounded tests that are independent and practical to run concurrently: **parallel orchestration**.
- Evidence needs interpretation, conflict resolution, or a design decision: **synthesis / strategy**.
- Required behavior and interfaces are sufficiently settled: **builder / implementation**.
- Implementation exists and acceptance criteria are known: **verification**.
- New evidence invalidates an assumption or decision: return to the smallest relevant earlier mode.

## Procedure

### 1. Establish the current state

Before assigning work, inspect the relevant target, prior findings, specifications, tests, harnesses, and handoff notes. Reuse evidence that remains applicable; do not repeat work merely because a new agent or phase has started.

Record:
- the target and desired outcome;
- the main unresolved question or implementation gap;
- settled requirements and constraints;
- known evidence versus assumptions;
- the required observable completion condition.

### 2. Select the next mode

**Use reconnaissance when a material unknown controls the next decision.** Frame a narrow, falsifiable question. Inspect the actual target and relevant runtime behavior. Recon may include a disposable feasibility prototype when static inspection cannot answer the question, but it must distinguish prototype evidence from production readiness. Specify what evidence would resolve the question and what finding should stop or escalate the investigation.

**Use parallel orchestration when tasks are independently executable and reviewable.** Parallelize only when each task has a distinct question, meaningful result, bounded setup cost, explicit output, and compatible completion criteria. Do not split work solely to increase agent count. Keep dependent tasks sequenced.

**Use synthesis or strategy when results must become a decision.** Reconcile findings, expose disagreements, distinguish observations from inferences, and decide whether evidence is sufficient to freeze behavior, interfaces, and acceptance tests. If it is not, define the smallest follow-up recon or test set.

**Use implementation when the design is sufficiently specified.** Supply the builder with the frozen requirements, existing code and behaviors to preserve, relevant evidence, minimal interfaces, tests, constraints, and stop conditions. Permit adaptation for concrete environment incompatibilities, not silent redesign. Material contradictions should return to strategy.

**Use verification when claims can be tested against known criteria.** Run targeted tests and regressions. Parallelize independent suites when state is isolated; retain end-to-end tests for behavior that depends on an integrated, shared runtime. Feed failures into a gap report and select the smallest next loop.

### 3. Decide whether tests can run in parallel

Parallel tests should not influence one another's outcome. Check for shared mutable state, including:
- browser profiles, cookies, or logged-in accounts;
- WebView or app instances and active playback;
- files, worktrees, databases, queues, or deployed resources;
- rate limits, shared external services, and time-sensitive state.

If state is shared, either isolate each test with distinct fixtures/profiles/worktrees/resources or sequence the tests. Record the isolation boundary. Small tests are not automatically independent.

### 4. Choose the execution environment

Use the local machine when the question requires desktop UI, native OS behavior, an interactive browser/WebView, local credentials, hardware, or human-visible confirmation. Use a VPS when the question benefits from a reproducible headless/service environment, persistent automation, network-facing behavior, or isolated resources. Use both only when they answer complementary questions; record relevant environment and version differences. Never move credentials, cookies, or sensitive session state into an environment merely for convenience.

### 5. Require an explicit handoff contract

Each delegated task must state:

1. **Objective or hypothesis** — the one primary question or change.
2. **Context** — exact target and relevant prior artifacts; do not paste unrelated project history.
3. **Environment and isolation** — runtime/build, profile or fixture, and shared-state assumptions.
4. **Procedure** — test cases or bounded steps.
5. **Evidence required** — logs, values, traces, screenshots, code references, or reproducible observations as appropriate.
6. **Completion and stop conditions** — what constitutes a result and when to return a blocker.
7. **Output contract** — findings, changes, test outcomes, limitations, and unresolved questions.

Classify conclusions as appropriate: reproduced, confirmed by multiple tests, observed once, inferred, contradicted, failed, or not tested. Preserve exact values and reproduction conditions when they affect the decision.

### 6. Review results and loop narrowly

After work returns:
- compare results with the original question and acceptance criteria;
- check for contradictory results, missing evidence, and environment differences;
- decide whether the current decision is supported;
- identify the smallest remaining blocker;
- route that blocker to recon, an independent test, strategy, implementation, or verification as appropriate.

Do not restart the full workflow when a targeted follow-up is enough. Do not advance merely because a phase has completed if decisive evidence is still missing.

## Default decision table

| Current condition | Next mode |
|---|---|
| Core behavior or runtime constraint unknown | Recon |
| Several independent hypotheses can be tested | Orchestrator with isolated parallel tests |
| Tests depend on prior results or shared mutable state | Sequence or isolate, then orchestrate |
| Results exist but their implications are unresolved | Synthesis / strategy |
| Requirements, interfaces, and acceptance criteria are stable enough | Builder |
| A concrete implementation claim has objective criteria | Verification |
| Implementation reveals a material incompatibility or false assumption | Targeted recon / strategy |
| A test fails for a known, localized defect and authority permits correction | Bounded fix, then retest |

## Relationship to other methods

- **Compact Prompt Skill:** use it to turn each selected task into a high-signal prompt with only the context and constraints needed for that run.
- **Strategy-to-Builder Integration Packet Method:** use it to freeze and communicate design decisions before substantial implementation.
- **Domain-specific skills and project specifications:** remain authoritative for the substance of the work. This workflow skill selects the next mode; it does not override product requirements or security rules.

## Non-goals

- Do not mandate a fixed number of agents or stages.
- Do not parallelize dependent tasks or tasks that collide on shared state.
- Do not treat agent count, prompt length, or phase completion as evidence of progress.
- Do not let a builder silently resolve material product or architecture questions.
- Do not label untested behavior as proven.

## Completion standard

A workflow step is complete when it returns enough reproducible evidence, a verified bounded change, or a documented blocking uncertainty to justify the next decision. The overall workflow is complete only when the specified acceptance criteria have been verified or remaining limitations have been explicitly accepted and recorded.