---
title: ASES Task-Scoped Information Architecture Decision
version: 1.0.0
program: ASES
layer: Architecture
document_type: ADR
status: Active
authority: Canonical
canonical_repository: ases
depends_on:
  - docs/methodology/ASES Task-Scoped Information and Handoff Method.md
related_documents:
  - research/agent-information-topology/greenfield-task-context/PROPOSAL.md
  - research/agent-information-topology/greenfield-task-context/TASK-VIEW-CONTRACT.md
  - research/agent-information-topology/greenfield-task-context/comparison/RESULTS-2026-11-20.md
  - research/agent-information-topology/greenfield-task-context/field-trial/PROMPT-SOURCE-ADMISSION-2026-11-20.md
last_updated: 2026-11-21
---

# Decision: Task-scoped information architecture

**Decision ID:** ASES-22 / 2026-11-21  
**Status:** Accepted by operator on 2026-11-20; recorded 2026-11-21  
**Governing method:** [ASES Task-Scoped Information and Handoff Method](../methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md)

## Decision

**ASES uses task-scoped information views as its coordination interface.** What a task needs is derived from its goal, governing rules, current decisions, evidence, receiver, capabilities and expected results. The information topology is a logical model; it does not oblige agents to load a fixed set of documents.

### Settled choices

1. **No historical-file constraint.** `AGENTS.md`, `SESSION-START.md`, `SESSION-END.md`, older role documents and Crosslink-era bootstrap procedures are not architectural requirements. They are not automatically deleted; harness-specific adapters may remain where verified necessary.
2. **Selection before compression.** Read and apply task-relevant current canonical methods and active skills before calling a task packet complete. Omit unrelated material. A source's existence, discoverability or filename does not confer authority or prove that it was loaded.
3. **Representation is flexible.** Use a concise, human-authored task view for straightforward work. Use optional headings/structured metadata and a provenance receipt for multiple sources, overrides and cross-role handoffs. No mandatory format, CMS or extra context storage layer.
4. **No required persistent graph or resolver.** Six semantic object kinds—Source, Rule, Decision, Task, Evidence and Position—and typed relationships remain a useful mental/analytical model, **not mandatory storage objects or services**. A specialized index/renderer is permissible when measured complexity, churn or errors justify it.
5. **Authority and overrides are explicit.** Preserve source ownership, current revisions, applicable policies, scoped operator/project decisions and uncertainty. An authorized complete override excludes the superseded rule body from delivered effective context while retaining its identity in provenance. Unresolved authoritative conflicts are reported and block the dependent action.
6. **Evidence moves across boundaries.** Work results, claims, uncertainty, checks and next position persist in their current owners. GitHub stores technical source and evidence; Work Notes tracks agent execution; Projektor tracks human decisions. A read-only derived index does not become canonical policy.
7. **Dispatch authority is separate.** Source selection does not grant model/provider use, funds, credentials, or new capabilities. Apply the exact approved provider/model/account/funding route when relevant; do not silently substitute a paid model.

### Questions closed by this decision

| Question | Resolution |
| --- | --- |
| Must we keep separate agent/start/end documentation? | **No.** Use only adapters technically required by a specific harness |
| Must we create a central persistent knowledge graph? | **No.** The relationships are conceptual; use existing stores |
| Must an agent receive every skill and methodology document? | **No.** Select relevant current sources at the task boundary |
| Is a manual packet inherently insufficient? | **No.** It met the static tests; add structure when complexity warrants |
| Does a reference prove the method was read/applied? | **No.** Track read-versus-reference when material |
| Who owns the information and the handoff? | Canonical project sources own meaning; execution records own position/evidence; human decisions own exceptions |
| Is a behavioral auto-skill-invocation experiment necessary to decide the architecture? | **No.** The operator expressly deferred it. It remains unverified, not passed |
| Must independent Luna/OpenCode publisher/exposure pilots finish first? | **No.** They are unrelated execution/compatibility experiments; neither is queued as a dependency |

## Decision basis

- [Preregistered comparison](../../research/agent-information-topology/greenfield-task-context/comparison/RESULTS-2026-11-20.md): all six synthetic manual, structured and graph-derived packets passed equivalent mechanical checks. The manual option was smallest; this does not prove comparative performance in real agents.
- [Real coordination incident](../../research/agent-information-topology/greenfield-task-context/field-trial/PROMPT-SOURCE-ADMISSION-2026-11-20.md): task-relevant current methodology was missed, demonstrating a **selection** problem. The current operational skill guidance was corrected by [merged PR #73](https://github.com/rock-solid-sites/ASES/pull/73).
- [Greenfield research PR #72](https://github.com/rock-solid-sites/ASES/pull/72): preserved proposal, comparisons and candidate source-admission contract. Those research documents retain **Experimental** authority; they are evidence, not a second canonical method.

This decision endorses the **information contract**, not the hypothesis that software must be built to maintain it.

## Disposition and non-goals

**Adopted now:** The canonical method above governs task-level information composition and evidence handoffs. Current operational skills continue to govern their specialized operations. An existing published prompt/skill remains operationally current unless revised through its own process.

**Not adopted:** Mandatory generated `AGENTS.md`, forced migration of existing repositories, automatic policy publisher, persistent graph service, new document registry, blanket deletion of historical records, or automatic agent prompt injection.

**Separate technical inquiries remain independent:** WNASES-18/PR #64 policy-publication pilot and WNASES-19/PR #63 instruction-exposure experiment have their own evidence and may continue or be retired on their own merits. Their status does **not** reopen this architectural decision. The deferred fresh-chat selection test is optional follow-up, not a hidden acceptance gate.

**Closure:** Projektor `ASES-22` is the architectural decision record owner; Work Notes `WNASES-22` tracks the completed research/evidence. Future changed evidence can motivate a **new versioned proposal** with specific falsifying observations; existing discussion is closed rather than left indefinitely awaiting another format debate.
