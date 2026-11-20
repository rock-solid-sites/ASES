---
title: ASES Task-Scoped Context Topology - Greenfield Format Proposal
program: ASES
layer: Research
document_type: Design Document
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/standards/Documentation Standard.md
related_documents:
  - docs/research/Workflow Topology Design and Reasoning Record.md
  - docs/research/EDASES-Methodology-Feedback-and-Enforcement.md
last_updated: 2026-11-20
---

# ASES task-scoped context topology — greenfield proposal

**Proposal, not adopted methodology.** Design the information and workflow topology **without requiring any existing document names, directory structure, CLI, agent role files, or start/end procedures**. The companion [candidate task-view contract](TASK-VIEW-CONTRACT.md) consolidates the architecture's information obligations after the [2 × 3 synthetic comparison](comparison/RESULTS-2026-11-20.md) and [observed source-admission failure](field-trial/PROMPT-SOURCE-ADMISSION-2026-11-20.md). **Neither experiment justified a mandatory persisted graph or a new resolver service.** Previous artifacts (including root `AGENTS.md`, `SESSION-START.md`, Crosslink and historical skills) are evidence about observed problems, not shape-defining inputs. Do not rename or port them as the default solution. This design is independent of draft PRs #63/#64 and does not overwrite their pilot evidence or production agent instructions.

## 1. Start from information flows, not files

The primary object is a **task** with an authorized purpose and bounded decision contract. A task needs only a *resolved view* of the information applicable to it. Repository files, skill indexes, model-specific instruction files, issue trackers and provider configurations are **source stores or delivery adapters**, not mandatory objects in the topology.

Logical flow:

```
operator intent / project objective
          |
          v
       TASK -------------------------+
          |                          |
     requires / applies             requires capability
          v                          |
    CONTEXT RESOLUTION               v
       /    |    \           approved execution route
  policy  evidence project decision   |
       \    |    /                    |
         EFFECTIVE TASK VIEW <--------+
                 |
            DISPATCH/WORK
                 |
       position + artifact + evidence
                 |
       verifier/reviewer gates as needed
                 |
        decision / finding / learning
                 |
       update owned source / task record
```

The resolver is a **logical operation**, not an authorization to build a service or Resource Solver. A human or coordinator may perform it with ordinary references and small deterministic checks. A task's effective view may be a small structured prompt; it **need not be a file**, and it must not implicitly load all source bodies.

## 2. Minimal typed information objects

These are semantic objects, **not necessarily separate files, tables, processes or roles**:

| Kind | Meaning | Immutable or owned facts |
| --- | --- | --- |
| **Source** | A referenced source of knowledge, requirements, policy or observations | Stable ID, owner, location, revision/content digest, authority/lifecycle, sensitivity, provenance |
| **Rule** | A prescriptive requirement that may apply to some task/project | Stable ID, source ID, precise scope/predicate, rule content/reference, authority, version, conflict policy |
| **Decision** | A human- or policy-authorized choice, exception, override or promotion | Stable ID, subject, authorizer/authority, reason, scope, exact source/revision replaced, effective period |
| **Task** | The bounded unit of work and its consumer needs | Stable ID, goal, project/scope, required capabilities, restrictions, outputs and evidence gate |
| **Evidence** | An observation or claim with source and certainty | Stable ID, claim, producer, artifact/test reference, confidence, what-not-tested, applicable revision |
| **Position** | Current work state, blocker and next transition | Task ID, state, checkpoint time, completed/next, blocker, evidence links, durability reference |

**Derived artifact: Effective task view.** Compiled/rendered from eligible Source + Rule + Decision + relevant Evidence + Task facts. It is **not a seventh authoritative source**. It records exact resolved source versions/IDs and omitted/replaced rules for audit. A different task or role may render a different view of the same underlying graph.

Capabilities, model selection, billing entitlements and permissions are **constraints and independently owned external facts**, not guessed from a rule file or treated as free simply because a model is listed. Resource Solver research owns later automated admission; here the task view merely carries a verified caller-side route and explicit stop conditions.

## 3. Typed relationships, not a document hierarchy

| Relationship | From -> to | Resolution meaning |
| --- | --- | --- |
| `derived_from` | Rule/Evidence -> Source | Supports provenance; a citation does not promote research to policy |
| `applies_to` | Rule/Decision -> Task or project scope | Only matching rules enter the effective view |
| `depends_on` | Task/Rule -> other object | Bring in the dependency's relevant facts, not its entire unbounded text |
| `overrides` | Approved Decision -> exact Rule@revision | **Exclude** original rule body from the effective task view; show replacement and provenance only |
| `supersedes` | New revision/Decision -> old object | Older text stays archived, but cannot silently reenter an effective view |
| `supported_by` | Claim/decision -> Evidence | Consumers can check basis, confidence and WHAT-NOT-TESTED |
| `produces` | Task -> artifact/evidence/position | Trace outputs to original assignment and validated revision |
| `blocks` | Evidence/Decision -> task transition | An unresolved gate prevents that action; it does not block unrelated work |

A pointer is not a precedence rule. In particular: a path named `AGENTS.md`, a directory named `skills/current`, a high-level research note, and a model-catalog listing **cannot acquire authority by being found**. Conflicting authoritative rules with no approved resolution yield an explicit conflict, never silent concatenation or last-write-wins.

## 4. The execution-view contract

A *context view* is assembled at the **point of use**, with six sections:

1. **Objective and output:** the task goal, exact boundary, artifact and completion criterion.
2. **Applicable rules:** the minimum effective normative content after scope, version and authorized overrides are resolved.
3. **Relevant knowledge:** source-linked facts and evidence for this task, including uncertainties and contrary evidence; not a whole repository dump.
4. **Capabilities and resource authority:** permissions, available tools/host, explicit **provider/model/account/funding route** where a model is invoked, limits and no unapproved fallback.
5. **Verification contract:** cheapest falsifying tests, expected evidence, any independent consumption gate, and WHAT-NOT-TESTED.
6. **Durability/feedback:** where checkpoint and final result land, who can use them next, and how discoveries enter the research/decision loop.

Where source identity, approval, override or cross-agent handoff is material, retain a **compact resolution receipt** (selected source revisions, applicable rules/decisions, replaced IDs and unresolved conflicts). It may be a Work Notes comment or metadata alongside the task rather than a new file. A digest is optional and cannot prove that the source selection itself was correct. Provenance matters most at producer–consumer boundaries.

The view must be **small because it is selected**, not small because important requirements were dropped. Missing safety or permission metadata is a blocker, not a reason to use a generic "default agent" profile.

## 5. No fixed startup or handoff documents are required

The minimum bootstrap for a new task is a **task reference + access to the relevant trusted sources + caller-side execution authority**. The coordinator may select sources manually or by a small deterministic procedure at the point of use. Nothing in the semantic model requires an `AGENTS.md`, `SESSION-START.md`, `SESSION-END.md`, agent-name-specific document, continuously loaded skill index or new CMS.

If a particular harness requires a static root instruction file, publish a **thin compatibility adapter** that states only how to access a validated task view. It should not duplicate rules or add an independently maintained policy corpus. If the harness can accept caller-supplied instructions, skip the adapter.

Likewise, a task's durable position and handoff belong to the task's existing durable record (currently, for many ASES experiments, Work Notes/Git); generating a "session-end" document per run is optional and must have evidence of usefulness. The **graph is conceptual**: repository Markdown with metadata, an optional compact relation index, Work Notes tasks and Git commit references may suffice. Do not install a database, daemon or orchestration engine to prove it.

## 6. Example selection, project override and producer-consumer edge

Synthetic task `task:test-checkout-47` concerns a small guest booking regression. It requests the code change, a fixed source pin and a falsifying parity test. The source graph contains `rule:remote-checkpoint` for durable work and `rule:review-route@7` as upstream guidance. The consuming project has `decision:local-review-route@3` with an approved complete replacement scoped to this task.

Resolution:
- Include `rule:remote-checkpoint` once.
- Include only the text approved in `decision:local-review-route@3`.
- **Exclude** the body of `rule:review-route@7`; preserve its ID/digest in the receipt for traceability.
- Include task-specific booking/guest-count evidence, not unrelated provider history.
- Specify the exact review model/funding route only when review dispatch is authorized.
- At handoff, emit producer evidence with claim basis, certainty, cheapest falsifying test and WHAT-NOT-TESTED; reviewer consumes that compact claim contract, not a transcript.
- A discovery about the methodology becomes an evidence/event node, **not automatically a new canonical policy**.

This example illustrates relationships, not the preferred filename, app, framework, data storage backend or live Tripn project implementation.

## 7. Minimal physical representation — no default graph

The **logical relationships** above need not map to persisted nodes or another indexing layer. Based on the comparison evidence, the minimal starting representation is:

- **Compact prose task view** with exact current references and explicit output/verification/stop criteria for a simple bounded task.
- **Lightweight structured task view** with selected source/override identities, uncertainty and an inline receipt when several sources, roles or authority boundaries interact.
- **Optional machine-readable source index and renderer**, only where measured repeated omissions, conflict rates or actual scale warrant their maintenance. The `EXAMPLE-GRAPH.json` and `EXAMPLE-VIEWS.json` remain synthetic research fixtures, not required production state.

A task view can be delivered in the caller's message or through an already-owned Work Notes/Git issue. The source bodies stay at their canonical owners. Existing Git/Work Notes records provide durable outcomes, so no mandatory `AGENTS.md`, session-start/end document, database, daemon or new CMS follows from this proposal.

[The task-view contract](TASK-VIEW-CONTRACT.md) specifies **what the consumer must know**, while allowing each interface to choose the smallest safe representation.

## 8. Cheap falsifiers and decision gate

| Claim to falsify | Cheapest test | Failure signal |
| --- | --- | --- |
| A graph view needs no universal startup doc | Compose a useful task view and run static checks with no root instructions | Missing mandatory information forces implicit legacy reads |
| Rule applicability is deterministic | Same task/context rev yields identical selected IDs/digest | Undeclared rules appear, or ordering changes effective content |
| Overrides remove upstream influence | Conflicting synthetic rule text and exact scoped approved decision | Both original and replacement bodies appear in effective content |
| Source authority is preserved | Feed experimental research and a stale rule as apparent policy | Any is promoted to binding instruction without a decision |
| Retrieval stays minimal | Add irrelevant sources and check selected context and source receipt | Unrelated source bodies enter the view or size scales with entire repo |
| Role/consumer transfer retains certainty | Produce a handoff with uncertain claim and a missing falsifier | Consumer presents uncertain claim as verified or loses provenance |
| Harness adapters are optional | Compare caller-supplied view with thin adapter in supported harness | Different rule selection, double loading or hidden global rule precedence |
| Position/evidence survive session boundaries | Lose current process and reconstruct task state from durable references | Cannot recover last verified state and next step without transcript |

**Completed:** Two synthetic task types were represented as manual, lightweight structured and graph-derived views. [Results](comparison/RESULTS-2026-11-20.md): all six passed the identical static gate; the graph had no verified correctness advantage and the manual packets were smallest. A later [real coordination incident](field-trial/PROMPT-SOURCE-ADMISSION-2026-11-20.md) exposed missing *source selection* despite source availability, addressed in merged PR #73. A fresh-chat behavior test has been **deferred by operator direction**, not run or passed. No production format should be declared adopted from these results.

## 9. Explicit non-goals and unresolved choices

- **Not adopting or migrating current AGENTS/SESSION files.** Those legacy objects are not authoritative design constraints and can eventually be retired, archived or replaced following actual harness tests.
- **Not a universal context server, new CMS, new issue tracker, or global Resource Solver.**
- **Not evidence that Codex or OpenCode automatically loads only a chosen view.** Observed load paths and model-visible request boundaries require separate, version-pinned tests.
- **Not a mandate to share private project instructions in public ASES.** Source scope and sensitivity are first-class; a resolver lacking authority to fetch must not materialize restricted content.
- **Not a claim that the Graph/Knowledge Index prototype is canonical.** Any index is a derived retrieval aid, not a source of authority.

Decisions to test, not assume: what smallest relation vocabulary is sufficient; whether rules and decisions need separate persisted objects; how the caller verifies a view receipt; when local override review is warranted; whether the view can be entirely in-memory; and which harnesses require an adapter.

**Next architectural decision (Projektor ASES-22):** review the candidate [task-view/source-admission contract](TASK-VIEW-CONTRACT.md), including document authority, selective retrieval and producer–consumer certainty transfer, **without assuming a graph or old startup documents are necessary**. The fresh-chat behavior test is deferred, not a precondition to consolidating documentation. Do not merge this experimental design as canonical methodology before the operator's architectural decision.
