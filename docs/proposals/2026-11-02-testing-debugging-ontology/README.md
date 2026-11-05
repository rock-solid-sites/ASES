---
title: Testing, Debugging, and Ontology Review - Reconciliation Proposal
program: ASES
layer: Methodology
document_type: Methodology Proposal Bundle
status: Draft
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/methodology/ASES Bounded Project Build Method.md
  - docs/roles/Ontology-Reviewer.md
  - docs/research/EDASES Review Methodology.md
related_documents:
  - docs/research/prompting/Ontological Connection to Review Skill.md
  - docs/research/research-addendum-epistemic-validation.md
consumed_by:
  - cross-conversation methodology reconciliation (proposed)
supersedes: []
superseded_by: []
last_updated: 2026-11-02
---

# ASES Proposed Testing, Debugging, and Ontology Review Integration

**Status: proposal-only.** This bundle consolidates candidate changes from one ChatGPT documentation round for comparison with concurrent ASES work happening in other conversations. It contains **no adopted policies**, **no automatic new gates**, and **no proof that independent model reviews or benchmarks have run**. Draft PR #4 stays unmerged until reconciled.

## What's here

| File | Purpose | Relationship to existing work |
| --- | --- | --- |
| [testing-and-assurance-method.md](testing-and-assurance-method.md) | Select and qualify evidence for requirements and claims; record CI outcomes; environmental perturbation is optional | Candidate sibling to the canonical bounded-build method and VSDD |
| [debugging-and-fault-isolation-method.md](debugging-and-fault-isolation-method.md) | Smallest discriminating tests to isolate failures, correct minimally and verify original user-facing outcomes | Candidate sibling, not a new development phase |
| [ontology-design-reviewer.md](ontology-design-reviewer.md) | **Exploratory conceptual design challenge**, with design context and authorized revision of the proposed model | Separate *role contract* extracted from historical Ontology Reviewer pre-build mode |
| [ontology-conformance-reviewer.md](ontology-conformance-reviewer.md) | **Independent conceptual conformance** against fixed canonical meaning, clean-room and falsification-oriented | Separate *role contract* extracted from historical Ontology Reviewer post-build mode |
| [integration-plan.md](integration-plan.md) | Proposed ownership, routing, review entry points, dependencies, and conflicts to check | Nothing is wired in by this document |
| [cross-conversation-reconciliation-2026-11-02.md](cross-conversation-reconciliation-2026-11-02.md) | First synthesis of HMS, cgrmcp, Resource Solver and Account Enumeration feedback, plus P6/P7 research | Review-only note linking response files on main, not an adoption decision |
| [integration-changes.patch](integration-changes.patch) | **Exact earlier candidate edits** to four pre-existing operational/methodology documents, against current main at capture | Comparison input only; **do not blindly apply** before reconciliation |

## Cross-conversation responses

Four response documents were subsequently committed by other discussions to this same folder path **on main**, not this proposal branch: [HMS chat](https://github.com/rock-solid-sites/ASES/blob/main/docs/proposals/2026-11-02-testing-debugging-ontology/HMS%20chat.md), [cgrmcp response](https://github.com/rock-solid-sites/ASES/blob/main/docs/proposals/2026-11-02-testing-debugging-ontology/cgrmcp-chat-response-2026-11-02.md), [Resource Solver response](https://github.com/rock-solid-sites/ASES/blob/main/docs/proposals/2026-11-02-testing-debugging-ontology/resource-solver-chat-response-2026-11-02.md), and [Account Enumeration response](https://github.com/rock-solid-sites/ASES/blob/main/docs/proposals/2026-11-02-testing-debugging-ontology/ases-account-enumeration-chat-2026-11-02.md). Their evidence classification, common findings and unresolved issues are summarized in the [cross-conversation reconciliation](cross-conversation-reconciliation-2026-11-02.md). Follow these links for exact source statements; do not assume the main and branch folders have identical contents.

## Existing sources to compare against

- docs/roles/Ontology-Reviewer.md — September 2026 umbrella role v0.2-draft on main
- skills/ontology-reviewer/* — historical/discussion-derived role and skill documents
- docs/research/prompting/Ontological Connection to Review Skill.md — prior distinction between review *domain* and *mode*
- skills/prompt/SKILL.md — already recognizes ontology-review as a domain and pre-build/post-build as modes
- docs/research/EDASES Review Methodology.md and docs/methodology/Clean Room Execution Guide.md — independence, synthesis, operator decision
- docs/ORCHESTRATOR.md — current Auditor/Reviewer role separation and orchestration policy
- docs/methodology/ASES Bounded Project Build Method.md — primary bounded development lifecycle; avoid duplicate stages
- docs/methodology/State-Model Applicability and Reuse Method.md — applicability-based modeling
- AGENTS.md — binding user-intent, cheapest-test, reasoning certainty, human authority and tool/routing constraints

## Provisional decisions preserved from the conversation

1. **Separation by question rather than stage count:** development asks *what to realize*, testing asks *what evidence establishes a claim*, debugging asks *what causes the observed deviation*.
2. **Common evidence discipline:** preserve original objective, competing explanations, pretest prediction, actual observation, limits, causal interpretations, decision and subsequent revision. A failed test or a passed check is not automatically a justified diagnosis/acceptance.
3. **Two distinct ontology roles:** Ontology **Design** Reviewer can challenge the proposed conceptual model; Ontology **Conformance** Reviewer tests adherence of a completed artifact to fixed definitions. They have distinct authority/context/evaluation contracts, not merely two names in a prompt.
4. **Selective invocation:** do not impose a reviewer on every change, presume a deployed route, or create an unnecessary VSDD phase. Explicitly separate Code Reviewer, Auditor and the proposed ontology roles.
5. **Independent conformance evidence:** preserve real model-family provenance and structural clean-room isolation; same-family operational acceptance is not an independent formal ontology review.
6. **No silent promotion:** draft proposal text does not amend existing canonical ontology or project-wide controls.
7. **Benchmarks before promotion:** start with the earlier two-mode six-case ontology-review seed (four defective cases and two clean controls, as historically proposed); evaluate incremental value, false positives, model routing and cost, plus actual testing/debugging cases.

## Status of branch changes

This bundle was assembled on PR #4's existing branch. The earlier draft **changes to active document paths** are preserved as an exact comparison patch, then restored to main content on this branch. The two previously new draft-method files are moved into this folder. The final intended PR diff therefore consists of this proposal folder alone, with no operationally effective modifications outside it.

**Next reconciliation:** compare against current work in other chats and any later main-branch changes before deciding whether to adopt any particular role contract, methodology text, routing rule or implementation. A patch captured against an earlier main revision must be re-derived or reviewed if its target changed.

## Authority and scope

No agent, security permission, CI schedule, provider model route, deployed service or production system is changed. Individual project repos may adapt adopted methods after separate authorization. Decisions in other chats may supersede this proposal; preserve the conflict and its rationale rather than silently replacing the earlier version.
