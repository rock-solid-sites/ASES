---
title: ASES Task View and Source Admission Contract - Candidate v0.1
program: ASES
layer: Research
document_type: Design Document
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/standards/Documentation Standard.md
related_documents:
  - research/agent-information-topology/greenfield-task-context/PROPOSAL.md
  - research/agent-information-topology/greenfield-task-context/comparison/RESULTS-2026-11-20.md
  - research/agent-information-topology/greenfield-task-context/field-trial/PROMPT-SOURCE-ADMISSION-2026-11-20.md
  - docs/research/Workflow Topology Design and Reasoning Record.md
last_updated: 2026-11-20
---

# ASES task view and source admission — candidate v0.1

**Status: superseded as a *proposal* by the accepted 2026-11-21 architectural decision.** Its evidence and drafting history remain Experimental. Governing methodology is [ASES Task-Scoped Information and Handoff Method](../../../docs/methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md); this document is not operational policy.  This describes the smallest *information contract* a coordinator and its workers should satisfy. It does **not** prescribe a root `AGENTS.md`, startup/end document, prompt template, graph database, indexing service, automated resolver, provider launcher or new issue tracker.

The [2 × 3 synthetic comparison](comparison/RESULTS-2026-11-20.md) found that manual, lightweight structured and graph-derived packets could all satisfy the same source and handoff checks; the manual packet was smallest. A [real coordination failure](field-trial/PROMPT-SOURCE-ADMISSION-2026-11-20.md) identified a different problem: the assistant **did not select the method applicable to the requested work**, although the method existed. Therefore **source admission**, rather than a particular serialization format, is the candidate design's load-bearing requirement.

## 1. Task is the unit of information selection

At a task boundary, establish the **operation**, target/scope, intended consumer and completion condition. Typical operations are recon, implementation, verification, review, synthesis, autonomous orchestration and bounded build compilation. One task may cause multiple distinct work units; do not combine a thin orchestrator's policy with the worker's source material merely because both belong to the same campaign.

An *effective task view* is the information that its consumer actually needs to take the next authorized action. It may be short prose with links, a structured packet or an in-memory payload. The repository, skills index, Git issue and evidence store remain independently owned sources; the view is **derived**, not new authority.

## 2. Source admission: six questions

For each candidate source, the coordinator answers:

1. **Relevance:** Could this source change the decision, required behavior, execution authority or verification of this task? If not, omit it.
2. **Authority:** Is it an operator instruction, an approved project rule, current canonical methodology, a current operational skill, a historical instruction, or research/evidence? A citation or file path never promotes experimental/retired material into current policy.
3. **Applicability:** Does it govern this *operation, project, receiver and stage*, or only a different work unit? A five-hour campaign does not make every worker task a precompiled build.
4. **Revision/freshness:** What exact revision or retrieved version was checked? Record a Git SHA only if verified. A moving `main` URL is not an immutable reference; do not substitute an assumed pin.
5. **Access/sensitivity:** Is the source permitted in this receiver's context? A public research view must not reproduce project-private instructions or credentials.
6. **Delivery:** Must the coordinator actually read the full source to apply a method, or will a pinned reference suffice for the receiving worker? **A link in a packet is not proof that a required method was read.**

**Result per source:** `read+apply`, `reference`, `omit`, or `blocked/unresolved`. No default action is `load everything`. A source can be applicable yet inaccessible; that is a recorded blocker, not permission to invent or replace it.

### Current prompting example (source-level rule already published)

For an ASES autonomous multi-agent assignment, the current `skills/current/compact-prompt/SKILL.md` and `skills/current/workflow-orchestration/SKILL.md` are applicable. For actual model dispatch, `skills/current/agent-launch/SKILL.md` supplies launch authorization. **Only when a bounded Implementation Packet is being compiled** do `skills/current/compile-build/SKILL.md` and the full canonical `docs/methodology/ASES Bounded Project Build Method.md` become mandatory. The older `skills/prompt/SKILL.md` and Strategy-to-Builder *derivation* do not substitute for those current authorities. [PR #73](https://github.com/rock-solid-sites/ASES/pull/73) corrected this current source-selection rule; this research contract does not redeclare or supersede it.

## 3. Resolve authority, conflicts and overrides explicitly

- **Higher-priority operator and platform restrictions:** A task view cannot grant permissions, paid spend, secret access or a provider/model route that the actual caller is not authorized to use.
- **Approved canonical/project rules:** Select the current rules actually applicable to this task. Use one logical identity per rule; old copies, derived summaries and duplicate filenames do not create additional policy.
- **Project-owned exceptions:** Require explicit owner/authorizer, scope, exact replaced rule and revision, reason and applicable status. A complete override **removes the original rule's body from the effective view** while retaining its ID/revision in the receipt. A project extension gets a distinct identity; it must not silently shadow upstream.
- **Research, observations and work notes:** Use as evidence with uncertainty, not normative rules unless deliberately promoted by an authorized decision.
- **Unresolved competing authoritative rules:** Do not concatenate contradictory text or use last-read/last-write wins. Record the conflict and block only the transition that requires choosing between them.

Task views must distinguish *selected source*, *approved rule* and *observed evidence*. Certainty belongs to claims, not implicitly to the document containing them.

## 4. Minimal delivered view

A simple task can express the following as a few sentences; a complex handoff may label each field. These are **semantic requirements, not mandatory headings or file fields**.

| Needed fact | Minimum content | When it may be abbreviated |
| --- | --- | --- |
| **Objective** | Target, requested transition/behavior and observable completion | Never omit the target or completion condition |
| **Governing context** | Applicable current rules/decisions and minimal required knowledge; exact source references | Include only relevant rules; source bodies may remain behind accessible links when consumer can retrieve them |
| **Authority/boundary** | Receiver's capabilities, forbidden actions and caller-verified provider/model/account/funding route **if dispatching** | For a no-model documentation task, record `no model launch` rather than invent route details |
| **Evidence/verification** | Cheapest falsifying check, claim/basis, certainty and WHAT-NOT-TESTED for decision-gating handoffs | A trivial edit may use one test link instead of a full schema |
| **Durability** | Where result, proof, blockers and next decision will be recorded | Use the existing Git commit, issue or work-unit record; no mandatory session-end document |

Where another agent will rely on an unverified claim, carry **WHY / WHAT / HOW-CERTAIN / WHAT-NOT-TESTED** across the producer–consumer boundary. Preserve the source and revision that support a claim; do not upgrade `observed` to `proven` by rewriting the handoff.

## 5. Optional resolution receipt

A receipt is useful for material source-selection, override, multi-agent or compliance decisions; it is **not** a requirement to generate a file for every small task. It may be a comment in Work Notes, metadata alongside the task or a compact structured object.

The smallest meaningful receipt contains: task ID, source IDs with verified revisions or an explicit `unverified` mark, applied rule/decision IDs, excluded/superseded source identities where material, any unresolved conflict, and the result/evidence destination. Record whether each required source was actually read, merely referenced or unavailable. A generated digest helps reproducibility only if its underlying source selection is itself correct.

**Do not include secrets or full private source contents in a public receipt.** Source scope, ownership and retrieval permissions remain enforced at the original store.

## 6. Readiness and information-flow transitions

1. **Classify → select:** Identify the requested operation and candidate authoritative/current sources.
2. **Select → resolve:** Check applicability, revision and accessibility; remove irrelevant and superseded bodies; apply only authorized scoped exceptions.
3. **Resolve → dispatch:** If mandatory context was unread, a material conflict remains or the execution authority is unknown, mark **PRELIMINARY / NOT READY**. Do not manufacture a fallback route or claim a frozen method was applied.
4. **Dispatch → evidence:** The producer records artifact, test outcome, source revision, current position, blocker, and what was not tested at the existing durable destination.
5. **Evidence → consumer:** Reviewers receive the minimal independent claim and artifact rather than builder process history when a clean-room judgement is needed; coordinators retain decision authority.
6. **Feedback → sources:** A finding becomes an observation/issue until reviewed and promoted. It does not silently mutate methodology or require immediate cross-project publication.

The implementation can be **manual coordination plus source links**. Nothing here requires a resident service, full-time knowledge graph, a prescribed role-specific file or an automatic startup ritual.

## 7. Limits and pending architectural decision

- The six synthetic packets all passed static checks. This supports *format flexibility*, not comparative reliability in real agent execution.
- The observed missed-prompt-method incident supports the **need for an explicit source-admission decision**, but merged Markdown does not guarantee ChatGPT/plugin automatic selection. The behavioral test is **deferred by operator direction**; do not treat it as a blocker to documenting the format.
- Provider/model/funding access is a **caller-side authorization fact**, not inferred from the task packet or a provider catalog; Resource Solver's live entitlement checks are separate.
- The current installed dispatcher and active skill texts are operational documents. **This candidate document has experimental authority only.** It must not conflict with or silently override them.
- This proposal does not assume root `AGENTS.md`, `SESSION-START.md`, `SESSION-END.md` or their replacement must exist. Thin harness adapters are optional, evidence-dependent.
- ASES-22 in Projektor owns the human architectural decision. WNASES-22 tracks technical evidence. PRs #63/#64 are separate exposure/publication experiments, not dependencies or adopted schema.

**Decision suggested by present evidence:** standardize the **information obligations**, not storage, filenames or model prompts. Use compact manually authored task views by default, optional light structure for complex handoffs and a persistent graph only if actual scale/conflict evidence later justifies one. No live deployment or policy migration is authorized by this candidate.
