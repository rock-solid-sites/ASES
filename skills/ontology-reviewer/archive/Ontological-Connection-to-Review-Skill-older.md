---
title: Ontological Connection to Review Skill
program: EDASES
layer: Research
document_type: Design Note
status: Proposed
authority: Derived
last_updated: 2026-09-21
---

# Ontological Connection to Review Skill

## Purpose

Explain how the emerging EDASES ontology work supports the proposed compact **Review/Prompt Skill**, and how the skill can use ontology without turning prompts into large project summaries.

This note is intended for later application to the Review Bridge Spec while keeping that specification focused on its immediate implementation task.

## Core Claim

The compact-prompt approach and the ontology work solve different parts of the same problem.

- **Ontology makes project meaning reusable.**
- **The Review/Prompt Skill makes task instructions reusable and compact.**

A short prompt is reliable only when omitted explanation is available through stable shared semantics or selected context.

The goal is therefore not merely to make prompts shorter. It is to stop repeatedly spending inference on reconstructing conceptual structure that the project has already established.

## Existing EDASES Substrate

EDASES already has the outline of a reusable conceptual model:

### Canonical Terminology

Defines authoritative project vocabulary and exists specifically to reduce terminology drift across agents and documentation.

### Concepts and Topics Registry

Provides:

- stable concept IDs;
- names and aliases;
- status;
- canonical homes;
- reasoning provenance;
- typed relationships;
- future-work relationships.

It is canonical for conceptual identity and graph relationships, while substantive definitions remain in canonical documents.

### Architecture and Specifications

Define:

- what concepts actually mean;
- responsibility boundaries;
- exclusions;
- invariants;
- lifecycle semantics;
- rationale.

Together these form a lightweight project ontology even though they are not currently presented as one monolithic ontology document.

## Why This Matters for Prompt Compression

Without shared semantics, prompts must repeatedly explain:

- what each role means;
- what each subsystem owns;
- what terms mean;
- which boundaries matter;
- what must not be conflated;
- what review operation is intended.

That creates long prompts that partly serve as temporary ontology reconstruction.

With a stable conceptual model, the task prompt can describe only the **delta**:

> what should this agent do now?

For example, instead of embedding a long explanation of the Work Unit, Attachment Point, Execution, Kernel, and authority model, a review invocation can supply the relevant canonical slice and say:

> Ontology-review this Work Unit change. Report material conceptual inconsistencies only.

The compact instruction works because the meaning is supplied by the selected project context rather than encoded repeatedly in prose.

## Three-Layer Prompt Architecture

A practical model is:

### 1. Ontology / Canonical Project Knowledge

Answers:

- What exists?
- What do project terms mean?
- Which concepts are distinct?
- How are they related?
- Which boundaries and invariants are canonical?

This layer is reusable across tasks.

### 2. Review/Prompt Skill

Answers:

- What kind of operation is being requested?
- Which concepts are relevant?
- What minimum context must the target model receive?
- Which output contract applies?
- What can safely be omitted?

This layer performs instruction and context compression.

### 3. Task Prompt

Answers:

- What specific artifact or change is being reviewed?
- What local constraint or objective applies now?
- What should the reviewer return?
- When is the task complete?

This layer should be small.

## The Skill as a Context Selector

The Review/Prompt Skill should not paste the whole ontology into every invocation.

Its useful function is closer to:

`requested operation + target artifact -> relevant conceptual neighborhood + compact instruction`

For a Work Unit capability change, the conceptual neighborhood might include:

- Work Unit;
- Attachment Point;
- Execution;
- Executor Authority;
- Kernel;
- API Capability Surface.

For a Processor change, a different neighborhood may be enough:

- Processor;
- Observer;
- Orchestrator;
- Deterministic Reuse;
- API Capability Surface.

This supports the existing EDASES principle of minimal agent context.

## The Skill Should Not Become an Ontology Engine

The Review/Prompt Skill should not:

- decide what the canonical ontology is;
- silently redefine concepts;
- generate a new ontology for every task;
- infer large architectural changes as part of prompt construction;
- encode all ontology rules inside one giant system prompt.

Its job is to **select and compress**, not to become a second source of conceptual truth.

## Named Review Operations

Ontology makes it possible to define compact review operations whose meaning is stable across invocations.

Examples:

### Code Review

Focus on implementation correctness, regressions, interfaces, safety, tests, and edge cases.

Minimal form:

> Adversarially review this implementation against the spec. Findings only; do not modify code.

### Ontology Review

Focus on conceptual identities, distinctions, relationships, categories, boundaries, terminology, and conceptual drift.

Minimal form:

> Ontology-review this change against the supplied canonical context. Report material conceptual issues only.

### Abstraction Review

Focus on whether material appears at the correct Research, Methodology, Requirements, Architecture, or Implementation layer.

Minimal form:

> Review this change for abstraction-boundary violations. Findings only.

### Necessity Review

Focus on whether proposed concepts, components, mechanisms, or work are required by the stated objective or already supplied elsewhere.

Minimal form:

> Review this plan for unnecessary work, duplicated mechanisms, or concepts already provided elsewhere.

The exact operation catalogue should emerge from use rather than being exhaustively designed in advance.

## Relationship to Specialist Roles

The skill and the reviewer role are separate.

The skill determines:

- operation;
- context;
- compact instruction;
- output form.

The specialist determines:

- the reasoning performed over that input.

For ontology review:

`Orchestrator -> Review/Prompt Skill -> Ontology Reviewer`

For implementation review:

`Orchestrator -> Review/Prompt Skill -> Code Reviewer`

The same prompt skill can therefore support several reviewer roles without embedding those roles into one oversized prompt.

## Why a Separate Ontology Reviewer Helps

If ontology review is merely appended as another section of ordinary code review, several problems arise:

- conceptual findings compete with implementation findings;
- the reviewer may prioritize concrete bugs and skip conceptual structure;
- the prompt becomes longer;
- the output becomes harder to route;
- the specialist operation becomes difficult to evaluate independently.

A separate reviewer lets EDASES test whether ontology review adds unique value.

It also allows invocation before code exists.

## Prompt Construction Rule

A useful design rule is:

> Put stable meaning in canonical project knowledge, stable procedure in the skill, and only task-specific differences in the task prompt.

This prevents three common forms of duplication:

1. repeating project definitions in every prompt;
2. repeating review methodology in every prompt;
3. copying large amounts of irrelevant project context into every agent invocation.

## Short Prompts Are Not a Goal by Themselves

The project should not optimize for character count.

A short prompt is useful when it is **compressed against shared semantics**.

A prompt that deletes required information without supplying stable context is simply underspecified.

The Review/Prompt Skill therefore needs a failure mode for cases where the conceptual context is not mature enough to compress safely.

Possible response:

- include additional explicit context;
- ask the Orchestrator to resolve ambiguity;
- invoke an ontology review before proceeding;
- identify that a canonical term or boundary is missing.

## Interaction with Human-Guided Ontology

The recent ontology discussion provides a caution against assuming that automatic ontology generation is sufficient.

A likely EDASES pattern is:

1. humans and frontier reasoners identify or refine conceptual distinctions;
2. canonical documentation records accepted meaning;
3. the Review/Prompt Skill reuses that accepted meaning;
4. specialist reviewers detect drift or contradictions;
5. the Orchestrator/human decides whether the artifact or ontology should change.

This keeps ontology changes explicit while still using models heavily for inspection and proposal.

## Practical Bridge-Spec Pattern

The Review Bridge should remain thin.

A Bridge implementation does not need a large ontology subsystem.

It needs enough integration to:

1. receive the requested review type;
2. invoke the Review/Prompt Skill;
3. supply the target artifact and relevant project context;
4. launch the selected reviewer;
5. return the findings to the Orchestrator.

Conceptually:

```text
Orchestrator
    |
    v
Review Bridge
    |
    v
Review/Prompt Skill
    |-- select operation
    |-- select relevant context
    |-- produce compact prompt
    |
    v
Specialist Reviewer
    |-- Code Reviewer
    |-- Ontology Reviewer
    |-- other future roles
    |
    v
Findings
```

The Bridge does not need to understand the full ontology. The skill and project knowledge provide the semantic layer.

## Candidate Minimal Ontology-Review Invocation

Persistent role guidance:

> Your responsibility is conceptual consistency, not implementation correctness.

Task invocation:

> Ontology-review this change against the supplied canonical context. Report only material conceptual inconsistencies, missing distinctions, conflations, boundary errors, or unjustified new concepts. Do not modify the system.

Everything else should come from the selected source material where possible.

## Evaluation

The compact-prompt hypothesis should be tested rather than assumed.

For representative reviews, compare:

1. a long structured review prompt;
2. a short review prompt without curated conceptual context;
3. a short review prompt with the relevant ontology slice.

Measure:

- useful findings;
- missed findings;
- false positives;
- context/token consumption;
- latency;
- consistency across models;
- sensitivity to weaker versus stronger models.

For ontology review specifically, also compare:

1. ordinary code/design reviewer;
2. same reviewer with an ontology-review instruction;
3. dedicated Ontology Reviewer role.

This can determine whether the value comes from the word "ontology," from the reasoning operation, from the supplied conceptual model, or from the specialization of the role.

## Design Constraints for the Review Skill

The current ontology discussion suggests these constraints:

- **Do not duplicate canonical definitions in the skill.**
- **Do not default to whole-project context.**
- **Do not make the skill the authority for ontology changes.**
- **Prefer named, compact review operations.**
- **Select only the relevant conceptual neighborhood.**
- **Escalate ambiguity instead of filling it with prompt prose.**
- **Keep reviewer roles separable so their value can be evaluated independently.**
- **Allow longer prompts when shared semantics are insufficient.**
- **Treat prompt length as an efficiency variable, not a correctness objective.**

## Bridge-Spec Application Note

When this note is applied to the Review Bridge Spec, the intended contribution is limited:

- the prompt/review skill should be ontology-aware when selecting context;
- it should support a named Ontology Review operation;
- the Ontology Reviewer should be routable as a separate specialist role;
- prompts should remain compact because canonical project meaning is supplied separately;
- the Bridge itself should not absorb ontology maintenance or project-wide semantic reasoning.

This lets the Bridge gain the benefits of the ontology work without turning the Bridge build into an ontology project.