---
title: ASES Task-Scoped Information and Handoff Method
version: 1.1.8
program: ASES
layer: Methodology
document_type: Methodology Specification
status: Active
authority: Canonical
canonical_repository: ases
depends_on:
  - docs/standards/Documentation Standard.md
  - docs/methodology/AI Orchestration Guide.md
  - docs/research/registry/AI Capability Registry Specification.md
consumed_by:
  - skills/current/compact-prompt/SKILL.md
  - skills/current/workflow-orchestration/SKILL.md
  - skills/current/agent-launch/SKILL.md
  - skills/current/review-launch/SKILL.md
  - ASES task coordinators and agent handoffs
related_documents:
  - docs/architecture/Task-Scoped Information Architecture Decision 2026-11-21.md
  - research/agent-information-topology/greenfield-task-context/TASK-VIEW-CONTRACT.md
  - research/agent-information-topology/greenfield-task-context/comparison/RESULTS-2026-11-20.md
last_updated: 2026-11-28
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

### Reconciliation of project-local adaptations

When a shared source changes, identify its known consuming documents, including locally modified versions in other projects. Use the [existing document inventory and impact lookup](../README.md#full-document-inventory-and-reconciliation) to surface candidates when available; resolve missing coverage explicitly. Consider the actual changed rules and their applicability to each local adaptation. A project retains authority over its own procedure, rationale, extensions and approved overrides; a shared-source change is a trigger for consideration, not automatic adoption, synchronization or replacement. Record the reconciliation decision in the owning project when material, even if the local version remains unchanged. Do not overwrite consumer files or fabricate a reviewed revision. Keep private consumer relationships within authorized scope.

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

### Chat persistence and record granularity

**ChatGPT mode selection (operator preference):** Remain in Chat mode unless the operator explicitly requests a switch to Work mode. Do not proactively suggest, prompt or initiate a Work-mode handoff merely because a task is lengthy, complex, involves repository work or uses connected tools. Continue authorized work with available Chat tools. If a required capability is unavailable, report the specific blocker and any feasible Chat-native alternative; do not treat the blocker as consent to change modes. The operator reports that unsolicited transition prompts frequently freeze while appearing active; this is an observed usability problem, not a verified diagnosis. A request to use Work mode does not itself authorize unrelated execution or changes. This is a project/operator preference, not a platform control or guarantee of host behavior.

**Each substantive Chat turn is a recoverability checkpoint, not a record boundary.** Before returning a turn that advances work, decisions, or understanding, persist the material change in the relevant existing Work Notes, Projektor or repository records according to information ownership. A turn can update multiple records when distinct subjects advance; it need not update every store or create a note. A conversation can advance several work units, and a work unit can span several conversations. Do not use chat boundaries as issue boundaries.

**Route the material delta by information ownership:**

| Destination | Record when the turn changes | Retain |
| --- | --- | --- |
| Projektor | Human intent, priorities, scope, subject understanding, dependencies, open questions or adoption decisions | Project/subject relationships, decision and its rationale, proposed vs accepted direction, outstanding human decisions; links to evidence and work where useful |
| Repository (GitHub or equivalent) | Retained implementation, technical knowledge, methodology, research findings or reproducible evidence | Code, tests, authoritative or explicitly provisional documents, findings with provenance, relevant negative results and evidence; publish only to an authorized destination |
| Work Notes | Operational state, execution ownership, progress, blockers, recovery or the next action | Current work-unit checkpoint, relevant scope and acceptance pointers, source/destination identity, verified progress, in-flight/failed/unverified operations, precise resume action and evidence links; concise history where needed for recovery |

A turn may change none, one, or several of these dimensions. A discussion of alternatives can advance Projektor without an execution record; a technical research finding can warrant a repository document without a new issue; a failed run can require only a Work Notes checkpoint, unless its evidence or implications warrant separate durable records. An implementation milestone may warrant a repository result and Work Notes checkpoint, with Projektor updated only if human-facing scope, status, decision or dependency materially changes. Link across destinations when useful; do not copy the same narrative into all three or use one destination as a substitute for another's material obligation. Keep private source material in authorized private stores. Other projects can choose equivalent destinations and their own lifecycle policies.

Keep the operational record a concise, current resume point: replace stale state, blockers and next-action pointers rather than append indefinitely. Preserve material evidence, decisions, rejected alternatives and rationale in appropriate comments or durable documents; keep canonical technical content in its authoritative home. Reuse existing subject records and split work at meaningful changes of scope, ownership, independent acceptance or dependency, not at arbitrary turn counts or text lengths. A discussion without execution still preserves material questions, ideas, alternatives, decisions and provenance in the appropriate existing subject record (or a new one when the subject genuinely warrants it); this does not authorize implementation or require an execution issue. Immaterial turns need no artificial write.

Verify material writes at the durable destination. When reading a body for replacement, verify completeness (follow continuation cursors or use a complete-body retrieval path); never overwrite a record with a partial read. If persistence is blocked, explicitly identify the gap and do not claim recoverability. These are Chat coordination information obligations, not a mandatory record template, one-note-per-turn rule, or universal lifecycle for other projects.

### Model capability evidence intake

**Capture new model feedback in the turn in which it is received.** Whenever an ASES coordination turn receives or establishes a material observation about model capability, limitation, reliability, efficiency, context behaviour or instruction adherence, persist that observation in the existing [AI Capability Registry](../research/registry/AI%20Capability%20Registry%20Specification.md) evidence records before concluding the turn, including discussion-only operator feedback and results from other sessions. Development and review agents apply the same obligation at meaningful result/evidence checkpoints. Do not defer intake until session closeout, a successful retry, or a periodic profile review. Positive, negative, partial and failed results all matter; a result from a tool or harness is not by itself evidence of intrinsic model behaviour.

Record the smallest attributable material delta in the appropriate existing model/route record or a dated evidence entry. Preserve source/run/turn identity or a privacy-safe pointer, date, exact model/version when known (including distinct variants), provider/access route, harness/configuration and task conditions as relevant, observation and evidence basis, verification status, uncertainty and attribution limits. Distinguish operator reports, model claims, independently reproduced findings, provider/transport/harness failures and untested hypotheses; retain unavailable identity or usage as unknown, not a guessed variant, zero or a definitive ranking. Record changed or corrected assessments without erasing prior observations. Deduplicate by evidence identity and use cross-family independent checks where relevant; same-family preference is a possible assessment bias. A periodic synthesis may update a profile but does not replace prompt intake. No full profile, score, new file or registry write is required for a repeated or immaterial observation already captured.

The coordinator owns intake and verifies the durable receipt (repository ref/path or authorized private evidence record). Retain private source material and account-sensitive telemetry only at authorized destinations; publish sanitized evidence where permitted. If registry persistence is blocked, retain the pending intake and source pointer in the existing Work Notes checkpoint or authorized private record, identify the missing persistence explicitly, and reconcile it when access is restored. Do not report an unverified write as complete. This rule concerns ASES capability learning; it does not automatically impose ASES lifecycle or publication rules on independent projects. The capture requirement is procedural until a controlled execution boundary or independently validated archive reconciliation implements it; a document or successful model output does not prove mechanical enforcement.

### Cross-chat related-work flags

When a material finding, decision or unresolved conflict could change other active work, preserve the substantive change once at its authoritative destination and link the distinct subjects in the existing topic register where applicable. A topic relationship alone does not deliver new context to the receiving conversation.

Place a concise **RELATED WORK — check here** pointer near the active position in the affected existing checkpoint or work note, where ordinary recovery will encounter it. Include the current topic/source link, one sentence explaining the material impact and when to consult it. Use the receiver's authorized destination, preserve private/public boundaries and avoid duplicating the finding or copying raw chats. Prefer a targeted, conflict-aware patch that preserves the other agent's current state; verify the write. If the destination is unavailable or a conflict cannot be safely resolved, record the undelivered pointer and report the gap.

The receiving agent consults the linked current source before advancing the affected question, applies relevant evidence, records unresolved conflicts or limits and avoids duplicate experiments. A flag does not authorize a scope change, execution, adoption or acceptance of unverified evidence. Update or retire resolved/stale flags; retain meaningful topic relationships. Do not require every neighboring topic to be retrieved on every turn or invent another record type.

A derived related-work view may later be evaluated using reviewed topic relationships, actual checkpoint associations and material source changes, with deduplication, provenance, relevance and access controls. This is not a requirement to build a service or push context into chats. Verified placement, actual receiving-agent uptake and automatic discovery are distinct claims.

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
