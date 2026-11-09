---
title: Shared Investigation Decision Records — Minimal Live-Notes Pilot
program: ASES
layer: Methodology
document_type: Methodology Specification
status: Draft
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/standards/Documentation Standard.md
  - AGENTS.md
  - docs/research/2026-11-09-agent-recovery-investigation-treadmill-postmortem.md
related_documents:
  - skills/workflow-orchestration/SKILL.md
consumed_by:
  - skills/workflow-orchestration/SKILL.md
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-09
---

# Shared investigation decision records — experimental proposal

> **PROPOSAL, not active global ASES policy.** Pilot the smallest mechanism that helps agents retain their actual goal, use negative evidence, avoid redundant investigations, and avoid creating irrelevant blockers. This is a general-purpose method, not a physical-networking procedure or a kernel-state-machine concept.

## Motivation

The 8–9 November 2026 UniFi recovery incident documented a pattern in which agents made valid intermediate repairs but repeatedly checked the same downstream symptoms and stopped over requirements irrelevant to the next authorized action. The pending ASES Debugging and Fault Isolation Method draft (currently on the separate `proposal/testing-and-assurance-method-2026-11-01` branch) already articulates the right reasoning disciplines; an executable agent still failed to adhere to them during a long session. The proposed intervention is a **visible, continually updated decision record**, not a new architecture or specialist reviewer.

Primary hypotheses to test:

1. Keeping the original user-facing goal and live failing boundary visible reduces goal displacement.
2. Requiring a concise result and implication after a meaningful test reduces equivalent retries and rediscovery.
3. Requiring a specific reason for a blocker reduces unnecessary interruptions.
4. Shared visibility lets another Chat/Work instance intervene earlier than a post-hoc summary.
5. Structural validation may improve record consistency with negligible execution cost; **semantic enforcement remains a future execution-engine concern**.

The method must apply to software builds, distributed systems, API integrations, deployments and any multi-stage work where local repairs can alter downstream state.

## Storage and organization

Preferred storage: a separate Projektor workspace for **agent Working Notes**, accessible through the existing Projektor MCP from Chat, Work and Codex. The operator need not use its application UI.

- **Workspace:** Agent Working Notes (name provisional).
- **One parent wiki page per project:** serves as the project's folder in the wiki tree (e.g., ASES, Trip'n, HMS, infrastructure). A page is created only for an actually used project.
- **One child wiki page per investigation:** original goal, current state, upcoming decision, and chronological results. Stable slug/ID used for cross-instance retrieval.
- **Multiple investigations per project** remain separate. Do not mix live working records with canonical research or project documentation.
- **Canonical outputs** such as reviewed postmortems, specifications or source changes continue to live in their appropriate repositories. Projektor notes are ephemeral operational evidence, not automatically authoritative methodology.
- Use page revisions and section-addressed patches rather than repeatedly replacing full documents. Where supported, append experiment entries using an append operation; update only current-state sections.
- **No GitHub commit per test**, separate dashboard, custom MCP, database migration, continuously running poller or workflow engine is initially required.

**Workspace endpoint discovery (2026-11-09):** A new workspace named `Agent Working Notes` was created successfully with workspace ID `6160a41b-7ef2-41bf-a69e-20ad00710cb6`. The existing MCP connection remained bound to the original Projects workspace when tested after creation. The upstream Projektor server's MCP route is already `POST /mcp/:workspaceId`, and uses the workspace ID in the request path. Therefore, the smallest likely route is **a separate authenticated MCP connection to `https://projektor-rss.rss-tools.workers.dev/mcp/6160a41b-7ef2-41bf-a69e-20ad00710cb6`**, not modifying the server to add a workspace-switching tool. The authenticated route has **not** been tested with the new connection. The operator must authorize/add that connection in ChatGPT and configure corresponding connections in Work and Codex as supported. One session's connector visibility cannot prove the others' access. Do not modify or replace the working Projects MCP endpoint.

After connecting, test that a note is writable in Codex and read from Chat and Work without changing the original workspace. If authentication fails, diagnose that boundary before modifying workspace routing. Merely creating a workspace or knowing its URL is not an acceptance test.

Visibility means **on-demand current reads** across clients. Do not claim live push or automatic notifications unless tested.

## One lightweight record

A note maintains a current snapshot plus an append-only experiment ledger. Suggested headings:

1. `Goal and acceptance` — user-required outcome, material constraints, authorization; stable for the run unless the operator explicitly changes scope.
2. `Current state` — what works, what fails, earliest established failure boundary, active competing explanations, recovery obligations.
3. `Next decision` — specific question, predicted results and what each result would change.
4. `Blockers` — only actual blockers, naming prevented operation, material consequence and independent work still available.
5. `Experiment history` — brief observations and implications; do not overwrite negative findings.
6. `Acceptance evidence` — original user-facing behavior, not merely intermediate green checks.

Keep the **human-visible text readable**, and optionally use an embedded YAML document for machine-checkable fields. Example experiment:

```yaml
kind: experiment
id: E-007
question: Does the dependency respond?
prediction: If upstream is down, the request will fail
decision_value: Distinguish upstream outage from local authorization
status: completed
outcome: observed_failure
observation: Dependency responded successfully
implication: Upstream outage weakened; examine local authorization
next_action: Probe the local authorization boundary
```

`outcome` describes the result of the actual test and must not conflate **test-instrument error** with target failure. Allow `success`, `observed_failure`, `inconclusive`, `test_error` as distinct outcomes. `status` may be `planned`, `completed`, or `interrupted`. An `interrupted` experiment records why the result was unavailable. The sample is illustrative; the pilot may simplify fields further if updates become burdensome.

The initial validator uses **one `kind: state` YAML code fence** for the current snapshot, plus zero or more `kind: experiment` YAML code fences appended under the experiment-history heading. The human-readable Markdown headings surround these blocks. Example state record:

```yaml
kind: state
original_goal: Restore working service
acceptance: Router, dependent components and users work
current:
  working: [main service]
  failing: [dependent client]
next:
  question: Which dependency first fails?
  decision_value: Select the smallest useful test
```

The experiment example below is validated only when `kind: experiment` is present. For each completed experiment, include `status: completed`, `outcome`, `observation`, `implication` and `next_action`. `planned` entries may omit result fields.

**Pilot checker:** `scripts/validate-investigation-note.py` in this branch; `python scripts/validate-investigation-note.py note.md` (requires PyYAML). It parses YAML code fences and checks only required text, status/outcome enums, exactly one state record and unique experiment IDs. It does not inspect other tool operations, verify the original goal against earlier revisions, adjudicate blocker relevance, or enforce append-only behavior. Those remain operator-visible expectations rather than mechanically guaranteed properties.

## Minimal YAML validation only

The validator's job is **syntactic and structural**, not to determine whether the agent reasoned correctly.

For investigation records in the designated workspace only:

- Parse YAML and require stable field names, basic types and known enum values.
- Require `original_goal` and `acceptance` at creation.
- Require a question, predicted observation and decision value when an experiment is created.
- Require an outcome, observation, implication and next action (or explicit no-action reason) when a completed experiment is written.
- Allow partial progress, interrupted tests and unknowns to be represented without fabricating results.
- Return precise, short validation errors with the rejected field. Do not silently repair records.
- Do not impose validation on wiki pages in other workspaces or on unrelated notes.

**Do not implement** a causal-relevance classifier, test originality verifier, automatic stop/go authorization, retry prohibition, mandatory risk scoring, model-usage counter, large schema, inferred hypotheses, or arbitrary-text evaluation. An eventual execution-engine component may implement decision-level guards once empirical failure rates justify it.

The first implementation can be a **client-side YAML structural validator** invoked by the writing agent before the existing wiki create/patch operation, with its schema stored alongside the ASES pilot. Do not claim it is server-enforced or impossible to bypass. For server-wide enforcement, a future change to the Projektor shared wiki write path would be required; defer that unless repeated validation failures justify it. This is deliberately lighter than adding or modifying the MCP.

## Agent update discipline

When the agent starts, it creates the note and records the **original objective unchanged**.

Before a consequential experiment, record the question, predicted outcome and decision value. After the experiment, record the actual observation and its implication **before starting the next material experiment**. Update the current snapshot when understanding changes. Record a genuine blocker only with the specific blocked operation and consequence; continue independent work where possible.

Do not add a record per trivial command or poll. Batch related read-only probes into one experiment if they answer the same question. A repeated test may be appropriate after a changed prerequisite or as a bounded intermittent-sampling experiment: say what changed and why the repetition can now answer something new.

The operator and supervising agent can inspect the current note **during** execution and correct a speculative or irrelevant direction. The note does not replace ordinary operator reports or authorization; it makes them more evidence-based.

Avoid storing credentials, setup codes, private addresses, customer data or other unnecessary secrets in workspace notes. Link to protected private evidence where essential.

## Relationship to ASES

- **EDASES research:** incident evidence, competing interpretations, negative findings, and comparison of pilot outcomes.
- **ASES methodology:** this candidate practice is a specialization of the existing evidence-to-decision diagnostic loop, not a replacement for it. It remains experimental until tested.
- **Execution engine:** richer semantic enforcement, resource orchestration and automatic detection of repeated low-information operations are deliberately deferred.
- **MCP skills:** teach agents how to open/read/update the shared record with the existing Projektor tools. Skills are operational guidance and cannot make an unverified capability claim.

The kernel's implementation primitives are not ASES methodological principles and are unrelated to the justification for this proposal.

## Live pilot: recovered UniFi installation

The immediate pilot investigation is **stability verification and bounded optimization**, not another open-ended repair:

- Original objective: ensure the repaired controller and extenders remain stable; seek measured, low-risk improvements to Wi-Fi performance while preserving working internet.
- Baseline: controller/database logs, evidence of new disk errors, uptime/reconnection events, wireless uplink quality, client reachability and coverage at meaningful locations.
- Next decisions: only tests that distinguish a particular instability or plausible performance constraint; no speculative factory resets or broad configuration rework.
- Changes: one justified reversible adjustment at a time, paired before/after measurement, revert when not beneficial.
- Completion: operational behavior verified across a declared observation interval; remaining long-term uncertainty recorded rather than concealed.

The pilot must use a note accessible to the supervising Chat conversation before extended work begins. If cross-client visibility fails, stop the **note integration test** and fix the connector route; this does not require stopping unrelated safe network checks.

## Pilot acceptance, rejection and escalation

Successful pilot evidence includes:

- One note created in the correct project parent page and read from Chat, Work and Codex.
- At least one experiment submitted before execution and completed afterward; older history remains retrievable.
- A test-instrument error accurately classified and not treated as proof of target failure.
- A repeated intervention explicitly justified by changed conditions, or avoided.
- A proposed blocker either tied to the prevented operation or deferred when irrelevant.
- Original acceptance checked independently of intermediary process status.
- Validator rejects missing keys/invalid enum, accepts valid and legitimately interrupted records, and has no effect on existing workspace content.

Compare with baseline behavior using redundant attempts, preventable stops, operator handoffs, cost to decisive result and acceptance quality. Also measure note-writing overhead and false blockers. If a lightweight record does not improve behavior, simplify or drop it before adding enforcement.

## Implementation sequence (intentionally narrow)

1. Add the second workspace-specific MCP connection through the existing registration/authentication path and test it from each client. Do not add a workspace-switching tool without a demonstrated need.
2. Establish separate workspace and parent-page-per-project organization.
3. Implement the small YAML structural validator for designated notes; add valid/invalid tests.
4. Update ASES MCP skills with the record-writing convention and tested tool route. Installed plugin skills may be pinned snapshots; source changes require whatever publishing/reload step their distribution uses.
5. Run the live UniFi stability/optimization pilot, observe behavior, and record follow-up research.

**Stop expanding the implementation** once the cross-instance shared record and simple validation work. Add new machinery only in response to repeated measured failures.
