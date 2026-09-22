---
title: Ontological Connection to Review Skill
program: EDASES
layer: Research
document_type: Design Note
status: Proposed
authority: Derived
canonical_repository: ases
last_updated: 2026-09-22
---

# Ontological Connection to Review Skill

## Purpose

Explain how EDASES ontology, the compact Prompt Skill, reviewer routing, and the emerging pre-build/post-build review distinction fit together without turning prompts into project summaries or the Bridge into an ontology engine.

## Core claim

Ontology and prompt compression solve different parts of the same problem:

- ontology makes project meaning reusable;
- the Prompt Skill selects the minimum relevant meaning and task delta;
- the orchestration layer selects eligible reviewers and enforces provenance/isolation;
- the reviewer performs the reasoning operation.

Short prompts work only when omitted meaning is supplied by stable canonical context or mechanically enforced structure.

## Existing ontology substrate

EDASES already distributes canonical meaning across:

- Canonical Terminology — authoritative vocabulary;
- Concepts and Topics Registry — identity, aliases, lineage, canonical homes, and typed relationships;
- architecture/specification documents — substantive definitions, boundaries, invariants, exclusions, ownership, lifecycle, and rationale;
- Crosslink Knowledge — durable supporting findings/rationale that are not themselves the canonical ontology.

The Prompt Skill should select from these sources rather than reconstructing them in every prompt.

## Two independent axes: review domain and review mode

Earlier drafts treated “ontology review” as if it implied one prompt shape. The refined model separates two axes.

### Review domain

What kind of thing is being judged: ontology, implementation, abstraction placement, necessity, security, etc.

### Review mode

What epistemic job the reviewer is doing:

- **exploratory pre-build review** — broaden/challenge the idea space;
- **post-build conformance/falsification review** — independently test a frozen claim in a finished artifact.

Ontology review can therefore appear in either mode.

## Exploratory pre-build review

Pre-build review is intentionally flexible. The artifact is still a proposal and the objective is improvement.

Useful prompts may be speculative, directed, or broad:

- look for hidden assumptions;
- identify missing distinctions;
- challenge ownership/boundaries;
- question whether a concept is necessary;
- compare alternative decompositions;
- argue that the ontology itself should change.

Iterative reassessment is legitimate:

`proposal -> critique -> revised proposal -> reassessment`

The reviewer can see accumulated design context because that context is part of the refinement process.

However, formal reviewer provenance still matters. A model family should not formally review an artifact produced by the same family, because family-level architectural preferences and blind spots can correlate even when contexts are separate. Same-family checks can be operational acceptance, not independent review evidence.

A large and diverse reviewer panel may be useful in this mode, and frontier models often provide valuable abstraction/search breadth. This remains a hypothesis to measure.

## Post-build review

Post-build review has the opposite objective: minimize contamination and independently falsify a concrete proposition.

The preferred input is:

`artifact + claimed property/invariant + relevant canonical definitions + explicit assumptions`

Process history should be absent: no builder reasoning, previous reviewer results, known bug history, implementation rationale, expected weak points, or statements that another agent believes the artifact is correct.

The task prompt should be as small as possible. Examples:

> This code claims X. Verify X.

> Prove invariant P holds under assumptions X, Y, Z.

> Code A should produce B. Break A so it produces not-B.

For ontology conformance:

> This implementation claims concepts A and B remain distinct under canonical definitions X and Y. Falsify the claim.

The reviewer should determine how to attack the proposition. Phrases such as “look for hidden assumptions” may be useful before build but are usually unnecessary post-build because they bias the search space.

## Clean-room means zero process-history context

“Zero context” does not mean withholding the specification needed to judge the artifact. It means withholding the social/process history that can trigger anchoring and default agreeableness.

Post-build independence should be structural:

- fresh reviewer context;
- no peer outputs before independent completion;
- no builder/reviewer history beyond task-defining evidence;
- synthesis only after all independent results exist.

Do not implement isolation by telling a reviewer “do not read the other reviewer.” If the reviewer can see it, isolation has already failed.

## Model-family provenance

Formal review evidence in both modes must come from a different model family than the artifact-producing family.

The practical exception is an acceptance/coordination check inside an execution workflow. For example, a same-family orchestrator may inspect a worker’s submission for task acceptance. That can be useful operationally but does not count as independent judgement-only evidence.

The reviewer normally does not need to know its own model identity. The orchestration layer records provenance and decides eligibility.

## Reviewer selection is part of prompt compilation

Every review-orchestrator prompt must either:

- name the reviewer models; or
- ask the orchestrator to propose a small, cost-efficient set suited to the review operation before launch.

Do not leave model selection implicit. Review quality is role-specific: a model that is weak at orchestration or building may be unusually strong at exhaustive falsification.

## Routing hypotheses from observed use

The current working hypotheses are:

- exploratory/pre-build review benefits from model-family diversity, broader panels, and often frontier-level abstraction;
- post-build review often needs only two or three independent models;
- smaller systematic models can outperform frontier models at narrow claim-by-claim rederivation;
- model routing should distinguish reviewer behavior from general model capability.

These are empirical claims to benchmark, not permanent model assignments.

## Ontology Reviewer implications

The Ontology Reviewer should therefore expose two modes rather than one generic procedure:

### Exploratory ontology review

Broader conceptual criticism is allowed. It can search for conflation, missing distinctions, bad boundaries, ownership mistakes, unnecessary concepts, semantic drift, or alternative conceptual decompositions.

### Ontology conformance review

Canonical ontology is fixed input. The task is to prove/falsify a specific relationship, identity, boundary, ownership rule, or invariant in the finished artifact.

The same role may serve both modes, but model routing may differ. Benchmarking must determine whether one model profile is actually good at both.

## Prompt Skill architecture

A useful decomposition is:

1. **Canonical project knowledge** — what exists and what it means.
2. **Prompt Skill** — review domain, review mode, minimum context, run-specific routing policy, completion condition.
3. **Orchestration layer** — model eligibility, provenance, capability profile, context isolation, peer-output withholding.
4. **Reviewer task prompt** — only the task-specific proposition or exploratory request.

The Skill is a selector/compressor, not an ontology engine and not the authority for canonical meaning.

## Context selection

Use the smallest conceptual neighborhood that can change the answer.

For exploratory ontology review, neighboring concepts and design rationale may be relevant.

For post-build ontology conformance, prefer only the claim/invariant and canonical definitions necessary to interpret it. Broader project context is contamination unless it is actually needed to define the proposition.

## Evaluation

The Ontology Reviewer benchmark should evaluate the two modes separately and include defective cases plus clean controls.

Useful dimensions include:

- true conceptual defect detection;
- false positives on sound designs;
- conflation/missing-distinction/boundary/category/ownership/semantic-drift detection;
- unjustified concept invention;
- tendency to replace canonical ontology with model preference;
- evidence quality and canonical fidelity;
- context/token efficiency;
- model-family sensitivity;
- exploratory versus conformance performance.

Benchmark runs intended as formal evidence should use different model families from the artifact-producing family. Same-family acceptance results may be retained separately but should not be merged into the independent-review score.

## Bridge application

The Review Bridge remains thin. It receives the requested domain/mode, obtains the selected context from the Prompt Skill, launches eligible reviewers through the available provider/runtime, preserves required isolation, and returns results for later synthesis.

It does not need to understand the full ontology, maintain model-specific reasoning instructions, or absorb project-wide ontology maintenance.