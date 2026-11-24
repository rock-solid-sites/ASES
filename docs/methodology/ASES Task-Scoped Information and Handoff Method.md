---
title: ASES Task-Scoped Information and Handoff Method
version: 1.1.2
program: ASES
layer: Methodology
document_type: Methodology Specification
status: Active
authority: Canonical
canonical_repository: ases
depends_on:
  - docs/standards/Documentation Standard.md
  - docs/methodology/AI Orchestration Guide.md
consumed_by:
  - skills/current/compact-prompt/SKILL.md
  - skills/current/workflow-orchestration/SKILL.md
  - ASES task coordinators and agent handoffs
related_documents:
  - docs/architecture/Task-Scoped Information Architecture Decision 2026-11-21.md
  - research/agent-information-topology/greenfield-task-context/TASK-VIEW-CONTRACT.md
  - research/agent-information-topology/greenfield-task-context/comparison/RESULTS-2026-11-20.md
last_updated: 2026-11-24
---

# ASES Task-Scoped Information and Handoff Method

## Purpose and authority

**Select the information needed for one authorized task and deliver it to the right consumer at the point of use.** ASES coordinates from task intent, scope, authority, evidence and observable completion—not from a fixed set of startup documents. This method formalizes the [architecture decision](../architecture/Task-Scoped%20Information%20Architecture%20Decision%202026-11-21.md).

This is **canonical methodology for composing task context**, not an agent launcher, permission system, model router, mandatory prompt template, database, or automatic context injection mechanism. Existing active operational skills remain the source for the *procedure* specific to their task. A concise view is useful only if it contains or reliably references all material governing information.

## Source selection

For each task, the coordinator determines:

1. **Operation and consumer:** objective, bounded transition, receiver role and acceptance criterion. Separate parent orchestration from worker implementation and independent review; they may need different context from the same project.
2. **Relevance:** retrieve the sources capable of changing the task's behavior, restrictions, verification or decision. Omit unrelated source bodies rather than loading entire repositories or old chat transcripts.
3. **Authority and applicability:** distinguish current canonical/project rules, operator decisions, current operational skills, evidence/research and superseded history. Verify the source governs this task and stage; a directory, filename, link or index position does not establish authority.
4. **Revision and access:** record verified source revision/identity or explicitly mark revision unknown. Check sensitivity and recipient permissions. Do not expose private rules, credentials or unrelated project information in public packets.
5. **Read versus reference:** choose whether the coordinator must **read and apply** the method before claiming a prepared task, or whether an accessible source reference for the receiver is sufficient. A document linked by another PR is not evidence it was read.
6. **Exceptions and conflicts:** include only approved scoped overrides and extensions. An approved *complete override* excludes the original rule body from the effective context; retain original identity/revision in the provenance record. A new extension has a distinct rule ID. Contradictory applicable authoritative rules with no approved resolution block the affected action, not unrelated work.

Possible outcomes for each candidate source are **read/apply**, **reference**, **omit**, and **unavailable/unresolved**. Do not use a historical document as an implicit fallback when an applicable current source is unavailable.

### Current ASES operational-source selection

[The current Skills index](../../skills/current/README.md) identifies the current operational skill for each task. The task-relevant current skills, not old packages with similar names, govern prompt selection, orchestration, build compilation and launches. In particular, **substantial bounded Implementation Packets** require the full canonical [ASES Bounded Project Build Method](ASES%20Bounded%20Project%20Build%20Method.md) before being called compiled; a long-running orchestration assignment alone is **not** a reason to apply that compilation method to every worker. Use the actual [current prompting skill](../../skills/current/compact-prompt/SKILL.md) for the task-dependent admission rules.

The [earlier prompting variants](../historical/Skill%20and%20Review%20Design%20History.md) and Strategy-to-Builder research derivation remain historical/derivative material, not replacement current prompting authority. They may be cited as evidence when relevant but are not mandatory reads.

## Effective task view

Deliver the smallest reliable view containing:

| Obligation | What its consumer needs |
| --- | --- |
| **Target and outcome** | Requested transition or finding, exact target/scope and an observable stop/completion condition |
| **Applicable meaning** | Current relevant rules, settled decisions, necessary project facts and explicit unresolved assumptions |
| **Authority and limits** | Permitted operations, access/secret boundaries, escalation/stop conditions, and verified caller-side execution authorization when dispatch is intended |
| **Evidence obligation** | Cheapest relevant falsifying check, what result counts as evidence and which claims remain untested |
| **Durable destination** | Intended final home of retained artifacts and evidence; distinct temporary workspace and disposition where used; existing execution record for blockers and current position |

These are **semantic obligations, not required headings, JSON keys or separate files**. A simple task may use a few lines of prose with direct links. A complex or cross-role task may use an explicitly structured packet. Only introduce machine-readable records, a context resolver or additional persistent storage when recurring empirical failures justify the overhead.

A model route, provider account, subscription entitlement, purchased-credit budget, promotional balance or free-tier allowance is a **separately authorized caller-side fact**. Never infer cost or substitute a model from its provider name or catalog. Use the current [agent-launch skill](../../skills/current/agent-launch/SKILL.md) for an actual launch; this methodology does not grant spending permission. A task packet should not ask the receiving agent to choose its own model.

## Provenance and handoff

Preserve a **small receipt when material** to authority, overrides, independence or reproducibility. It may live in an existing issue comment, Git metadata or the coordinating handoff. Include task ID, actual source IDs/revisions or `unverified`, read/reference decisions for mandatory methods, approved replacement IDs, unresolved conflicts and evidence destination. A hash only validates selected bytes, not the correctness of the selection.

A producer's claim crossing to another agent carries **claim, basis/source, confidence, cheapest falsifier and WHAT-NOT-TESTED**. Reviewers receive the artifact and independent claim, not necessarily the builder's whole process packet; use the applicable clean-room review rules. The coordinator retains acceptance authority. Research findings become traceable observations until formally approved as methodology.

Checkpoint the current position in the existing work record: completed verified work, current blocker, next transition and supporting commits/tests. **No universal session-start or session-end file is required** to preserve state.

### Destination-first execution and recovery

**Branches are temporary and disposable.** Before creating a branch or starting work that produces retained artifacts, identify the source repository/revision, intended final repository and discoverable path (normally on its default branch), artifact status/authority, temporary workspace if used, and expected disposition. A temporary branch, local checkout or PR is a checkpoint, not the final home. The destination may be an existing document, directory, issue, or other authorized durable store; a task that produces no retained files needs no invented Git destination. Record a material change of destination or disposition with its reason and authority.

For agent work, the existing Work Notes packet carries the source and final destination, disposable workspace, active owner or unclaimed status, material blocking dependencies, latest verified remote checkpoint and resume pointer when relevant. These are information obligations, not a prescribed YAML template or database schema. Git retains substantive code, documents, reasoning, evidence and meaningful historical states; Work Notes retains operational state and pointers; Projektor retains human-facing priorities, dependencies and adoption decisions. Do not duplicate canonical technical content in either tracker.

**Cadence depends on execution environment.** Development agents working in interruption-prone execution environments (Codex, OpenCode and equivalent) commit and push substantive progress at short recoverable intervals (aim for five minutes or meaningful checkpoints as appropriate), before long or interruption-prone operations, and at handoff. Chat coordination instead updates the relevant authoritative sources each substantive turn; do not impose a five-minute commit cadence on Chat. Record launch state before dispatch when needed for recovery. Publish useful results, outcomes, evidence, decisions and reusable artifacts to the appropriate repository's `main` branch, classified experimental where applicable, without waiting for the experimental branch's lifetime to end. Independently verify the remote ref/commit or equivalent durable checkpoint and record the latest recoverable position. An unpushed local commit or reported push is not proof of recoverability. If remote publication is blocked, report the missing durability and preserve authorized evidence where possible; do not claim delivery.

Isolate concurrent or risky changes and replacement comparisons as needed. Clearly classified experimental or work-in-progress artifacts may be published to an appropriate default-branch location without activating them or approving their adoption. Preserve useful findings from rejected experiments. Git history is not a deliverable. Preserve useful results and outcomes, source identities and reproducibility evidence in durable authoritative locations; do not require retaining intermediate experimental branches or their commit history. Publication does not authorize production activation, bypass review, or expose private material.

At completion, verify retained outputs are readable at the intended authorized remote destination, including their source/authority status and relevant navigation. Record final pointers and explicitly identify branch-only remainder as unfinished or intentionally temporary. A branch becomes disposable only after its retained outputs and necessary evidence are independently verified at their intended home and no active dependency requires it. Do not delete branches or rewrite shared history without applicable authority. Keep the final handoff proportional to the task.

## Readiness and exceptions

A task is **ready to dispatch** only when required current sources have actually been consulted as needed, no material unresolved authority conflict exists, intended execution permissions/funding are authorized, and completion/verification/handoff are defined. Otherwise mark the work **PRELIMINARY / NOT READY** and identify the missing requirement. An intentionally exploratory task can be ready for **reconnaissance** even when implementation details are unresolved; do not falsely mark a build packet frozen.

For a small edit, collapse this method to target → relevant source → change → check → durable result. Do not manufacture a form, graph, startup ritual or extensive context receipt to satisfy the methodology.

## Implementation independence and migration boundary

The methodology does **not** require `AGENTS.md`, `SESSION-START.md`, `SESSION-END.md`, particular agent-role files, a graph database, daemon, service or always-loaded skill catalog. A launcher may still need a thin compatibility adapter; verify that launcher requirement separately. An adapter should route to current sources and must not become another independently maintained copy of the methodology.

Existing historical documents are **not deleted or declared mechanically non-loaded** by this decision. Retirement, actual runtime exposure tests, source-policy publication, and any multi-project distribution service are separate compatibility/engineering work, not prerequisites for applying the information method.

## Evidence and limits

The [synthetic comparison](../../research/agent-information-topology/greenfield-task-context/comparison/RESULTS-2026-11-20.md) found all three representations met static correctness checks and a manual packet was shortest; it did **not** measure agent outcomes, authoring time or retrieval at scale. The [real prompt-selection incident](../../research/agent-information-topology/greenfield-task-context/field-trial/PROMPT-SOURCE-ADMISSION-2026-11-20.md) demonstrated a task-relevant method could be missed despite existing, prompting the current skills correction in [PR #73](https://github.com/rock-solid-sites/ASES/pull/73). The fresh-chat automatic-selection test was expressly deferred and is **not claimed passed**.

**No conclusion about model-visible context or enforcement follows from this methodology's ratification.** The architectural decision is settled; later experimental evidence may motivate a versioned revision without reopening the choice of an unnecessarily graph-first system.
