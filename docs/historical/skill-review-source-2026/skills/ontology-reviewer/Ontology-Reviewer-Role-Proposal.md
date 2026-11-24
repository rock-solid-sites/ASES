---
title: Ontology Reviewer Role Proposal
program: EDASES
layer: Research
document_type: Role Proposal
status: Proposed
authority: Derived
last_updated: 2026-09-22
---

# Ontology Reviewer Role Proposal

## Purpose

Define a specialist **Ontology Reviewer** role for EDASES and related agent workflows, and distinguish the two review modes that have emerged from use: exploratory pre-build review and post-build ontology conformance review.

The role asks whether a system is describing and relating the right things. It is distinct from ordinary implementation review even when both inspect the same artifact.

## Rationale

EDASES already has a distributed ontology substrate:

- Canonical Terminology for controlled vocabulary;
- Concepts and Topics Registry for stable identity, aliases, lineage, canonical homes, and typed relationships;
- canonical architecture/specification documents for substantive definitions, boundaries, exclusions, invariants, ownership, lifecycle, and rationale.

The reviewer should consume this structure rather than create a competing ontology.

Material ontology failures include conflation, duplicate concepts, missing distinctions, category errors, incorrect ownership or boundaries, lifecycle/state mismatches, semantic drift, unjustified concepts, and relationships that contradict canonical meaning.

## The role is one domain with two review modes

The important distinction is epistemic, not merely chronological.

### Exploratory pre-build ontology review

The conceptual model itself is still under test. Review can be broad, speculative, directed, and iterative. It may question hidden assumptions, search for missing distinctions, challenge boundaries or ownership, identify unnecessary concepts, or propose that the current ontology needs revision.

An iterative loop is valid:

`proposal -> review -> revised proposal -> reassessment`

Accumulated design context can help because the goal is refinement rather than independent verification of a frozen artifact. Directed prompts and richer checklists are defensible when they enlarge the design search space.

Formal independence still requires a different model family from the family that produced the proposal. Same-family models tend to reproduce related architectural preferences and blind spots. A same-family acceptance check may still be operationally useful but is not independent evidence.

Pre-build panels may be relatively large and diverse, often including frontier models. This is a routing hypothesis to test, not a permanent assignment.

### Post-build ontology conformance review

The artifact and canonical ontology are fixed inputs. The task is to falsify a specific claim or invariant.

This mode should be terse, specific, and clean-room. The reviewer receives only the finished artifact, the claim/invariant, the relevant canonical definitions/relationships, and explicit assumptions needed to evaluate the proposition.

It should not receive builder reasoning, prior defects, earlier reviewer findings, expected weak points, implementation rationale, or peer-review outputs. This is zero process-history context, not zero task-defining context.

Representative prompts:

> This implementation claims concepts A and B remain distinct under canonical definitions X and Y. Falsify the claim.

> Under assumptions X, Y, and Z, prove invariant P holds.

The reviewer chooses the method of attack. Extra review prose is a potential source of anchoring.

A suite of two or three reviewers may often be enough. Smaller, systematic models may be especially effective at exhaustive rederivation even when they are weak orchestrators or builders. This is another routing hypothesis for benchmark evaluation.

## Formal review provenance

Formal review evidence in either mode must come from a different model family than the artifact-producing family.

This rule is stricter than ordinary workflow acceptance. For example, a same-family orchestrator checking a worker submission may be entirely acceptable for practical task acceptance, but that result must not be counted as an independent judgement-only review.

Reviewer independence after build should also be structural:

- independently instantiated contexts;
- no peer findings before each independent pass completes;
- synthesis only after the independent outputs exist;
- no reliance on prompts telling reviewers to ignore information they have already seen.

Reviewer model identity normally need not appear in the reviewer prompt. Eligibility and isolation belong to orchestration/runtime state.

## Reviewer selection

Review orchestration must not leave model selection implicit. A review-orchestrator prompt should either name the reviewer models or ask the orchestrator to propose a small, cost-efficient set suited to the task before launch.

Model strength is role-specific. A model may be a poor orchestrator or builder but an excellent falsification reviewer. Routing should therefore be benchmarked by operation rather than inferred from general capability.

## Authority boundary

The Ontology Reviewer is read-only and non-authoritative. It may identify that the artifact is wrong, that canonical ontology is ambiguous, or — in exploratory mode — that the ontology itself may need revision. It does not silently change canonical meaning.

Canonical ontology changes remain explicit decisions for the Orchestrator or human operator.

## Capability profile

Recommended capabilities:

- read the target artifact/proposal;
- read the selected canonical concept slice;
- inspect relevant diffs/files/history through read-only tools;
- search project documentation and Crosslink Knowledge;
- inspect bounded Crosslink issue state when that context is deliberately selected;
- run read-only tests or queries needed to falsify a conformance claim;
- return findings.

Mutation, commit/merge/deploy, permission changes, unrestricted agent launch, and autonomous canonical-document editing should be structurally unavailable.

## Context selection

The Prompt Skill should select the smallest context that can change the review.

For exploratory review, broader neighboring concepts and design history may be useful.

For post-build conformance, the preferred context is:

`artifact + proposition + canonical definitions + explicit assumptions`

Do not include process history merely because it exists.

## Output shape

Exploratory review can use richer findings because its output feeds another design iteration: observed claim, canonical comparison, issue/question, evidence, impact, confidence, and smallest resolution question.

Post-build conformance should be lean: concrete counterexample/defect and evidence, unresolved uncertainty, or the claim actually established. Do not duplicate evidence already mechanically preserved in tests or diffs.

## Relationship to code review

Code review and ontology review are separate domains. Either can be exploratory before build or claim-focused after build.

The important axes are therefore:

1. **review domain** — ontology, implementation, abstraction, necessity, etc.;
2. **review mode** — exploratory pre-build or conformance/falsification post-build.

Treating these as separate axes prevents “ontology review” from implying one fixed prompt shape.

## Evaluation plan

The role is an empirical hypothesis. The benchmark should evaluate exploratory ontology review and post-build ontology conformance separately.

A small initial benchmark should contain known defective cases and clean controls derived from real project distinctions. Useful dimensions include:

- detection of real conflation, missing distinctions, category errors, boundary/ownership errors, semantic drift, and unjustified concepts;
- false-positive rate on sound designs;
- tendency to replace canonical ontology with the reviewer’s own preferred architecture;
- canonical fidelity and evidence quality;
- context efficiency;
- model-family sensitivity;
- comparative performance of frontier, mid-level, and smaller systematic models;
- difference between exploratory-review quality and conformance-review quality.

Formal benchmark results should respect cross-family provenance. Same-family acceptance checks can be recorded separately as operational evidence.

## Open questions

- Which model traits predict exploratory ontology-review quality?
- Which predict post-build ontology-conformance quality?
- Does one reviewer profile work well for both modes, or should routing split?
- How small can the canonical context slice become before conformance quality falls?
- Which ontology claims are suitable for deterministic or classifier-assisted checking before invoking an LLM reviewer?
- Which changes should trigger ontology review automatically versus by Orchestrator judgement?

These questions should be answered by benchmark evidence rather than fixed in the role prematurely.

## Bridge application

The Bridge should remain thin. It needs to route the selected review domain/mode, provide selected context, launch eligible reviewers, preserve structural independence where required, and return findings. It should not become an ontology engine or model-routing theory encoded in infrastructure.