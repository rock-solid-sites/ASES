---
title: Ontology Reviewer Role Proposal
program: EDASES
layer: Research
document_type: Role Proposal
status: Proposed
authority: Derived
last_updated: 2026-09-21
---

# Ontology Reviewer Role Proposal

## Purpose

Define a specialist **Ontology Reviewer** role for EDASES and related agent workflows.

The role exists to review the conceptual model implied by a design, specification, documentation change, or implementation. It is distinct from ordinary code review: its primary question is not whether the implementation works, but whether the system is describing and relating the right things.

This proposal is intended to be applied later to the Review Bridge Spec without expanding that specification's immediate scope.

## Rationale

Recent ontology-review discussions suggest a useful review operation:

> identify what the system claims exists, what each thing means, how those things relate, and whether the change introduces conflation, duplication, category errors, unstable terminology, or incorrect boundaries.

EDASES already contains much of the required substrate:

- **Canonical Terminology** provides controlled vocabulary and reduces terminology drift.
- **Concepts and Topics Registry** provides stable concept identities, aliases, lineage, canonical homes, and typed relationships.
- **Canonical architecture/specification documents** provide substantive definitions, boundaries, exclusions, invariants, and rationale.

The Ontology Reviewer should consume this existing structure rather than create a competing ontology.

## Role Definition

The Ontology Reviewer is a **read-only specialist reviewer** responsible for conceptual consistency.

Its core questions are:

1. What entities, concepts, categories, states, roles, or relationships does this change imply?
2. Do those concepts already exist canonically under another name?
3. Has one concept acquired multiple meanings?
4. Have distinct concepts been collapsed into one?
5. Has a new distinction been introduced that is only accidental implementation structure?
6. Is a concept located at the wrong abstraction level?
7. Has responsibility moved across an established boundary?
8. Do the proposed relationships match the canonical conceptual model?
9. Does terminology drift from the project's controlled vocabulary?
10. Does the change silently redefine, supersede, or duplicate a canonical concept?

## Distinction from Code Review

A code reviewer primarily asks whether a change is correct as an implementation:

- Does it work?
- Is it safe?
- Are there bugs or regressions?
- Are interfaces respected?
- Are tests sufficient?
- Are edge cases handled?

An Ontology Reviewer asks whether the **object model and conceptual structure are correct before or independently of implementation correctness**.

A technically correct implementation can still encode the wrong conceptual model.

### Example

A direct relationship such as:

`Work Unit -> Agent`

can be mechanically implementable while conceptually conflating:

- permissions,
- model identity,
- role,
- resource view,
- context continuity,
- session lifetime.

The EDASES Work Unit design resolves this by distinguishing:

`Work Unit -> Attachment Point -> Execution`

This is the kind of problem the Ontology Reviewer should detect even when ordinary code review finds no implementation defect.

## Authority Boundary

The Ontology Reviewer:

- does not modify code;
- does not rewrite specifications;
- does not change canonical terminology;
- does not create new canonical concepts on its own;
- does not approve architectural changes;
- does not own implementation correctness;
- does not become a second Orchestrator.

It produces specialized semantic evidence for the Orchestrator or human operator.

Canonical ontology changes remain explicit decisions.

## Tool and Capability Profile

The default Ontology Reviewer should be deliberately narrow.

Recommended capabilities:

- read the target change or document;
- read relevant canonical project documentation;
- read the Concepts and Topics Registry;
- inspect diffs and related files;
- search project knowledge;
- report findings.

Normally excluded:

- shell mutation;
- code writes;
- repository mutation;
- deployment;
- merge;
- authority changes;
- autonomous creation of new canonical documentation.

The role should remain useful even when implemented by a frontier model with only read-only project access.

## Inputs

The Ontology Reviewer should receive only the context relevant to the conceptual neighborhood under review.

Typical inputs:

1. the proposed change, design, spec, or diff;
2. the relevant canonical concept slice;
3. directly related definitions, invariants, and boundaries;
4. the review operation;
5. a narrow output contract.

It should not receive the entire EDASES corpus by default.

## Output Contract

Preferred finding shape:

**Observed concept or relationship**  
What the reviewed material appears to assert.

**Canonical comparison**  
The existing concept, relationship, boundary, or terminology it should be compared against.

**Issue**  
Conflation, duplication, category error, boundary violation, semantic drift, missing distinction, unjustified concept, or other conceptual inconsistency.

**Evidence**  
The concrete text, code, schema, or relationship that supports the finding.

**Impact**  
Why the mismatch matters.

**Suggested resolution question**  
A concise question or correction for the Orchestrator/human to decide.

The reviewer should report **material findings only**. It should not produce a replacement architecture unless explicitly asked.

## Invocation Triggers

Do not invoke the Ontology Reviewer mechanically on every small change.

Strong triggers include:

- introducing a new named concept;
- renaming or redefining an existing concept;
- adding a subsystem or major abstraction;
- changing ownership or responsibility;
- changing architectural boundaries;
- changing state categories or lifecycle semantics;
- adding a new relationship between canonical concepts;
- substantial specification restructuring;
- recurring agent confusion around the same terminology;
- a design spanning several established conceptual domains;
- a normal reviewer identifying ambiguity that appears conceptual rather than implementation-specific.

Ontology review may be especially valuable **before implementation**.

## Placement in the Review Flow

Possible design review flow:

`design draft -> ontology review -> architecture/code review -> implementation`

Possible implementation review flow:

`change -> code review + ontology review when triggered -> Orchestrator/human synthesis`

Code Review and Ontology Review may run independently over the same material when both are justified.

Neither reviewer should see the other's conclusions before independent analysis unless the task explicitly calls for a synthesis pass.

## Minimal Prompt Shape

The persistent role definition should stay small.

A representative invocation is:

> Ontology-review this change against the supplied canonical context. Report only material conceptual inconsistencies, conflations, missing distinctions, boundary errors, or unjustified new concepts. Do not review implementation correctness or modify the system.

The surrounding prompt machinery should select the relevant canonical context rather than expand this instruction into a long checklist.

## Relationship to Canonical EDASES Documentation

The Ontology Reviewer should treat:

- **Canonical Terminology** as the authoritative vocabulary;
- **Concepts and Topics Registry** as canonical for conceptual identity, aliases, lineage, and graph relationships;
- **canonical specifications and architecture documents** as authoritative for substantive definitions, invariants, exclusions, and boundaries.

The Registry should not become a duplicate architecture specification.

The reviewer should therefore compare across the existing documentation structure rather than demand a monolithic `ONTOLOGY.md`.

## Relationship to the Orchestrator

The Orchestrator decides:

- whether ontology review is warranted;
- which conceptual slice is relevant;
- whether a finding requires correction;
- whether a new concept is justified;
- whether canonical documentation must change;
- whether another specialist review is needed.

The Ontology Reviewer supplies evidence and conceptual analysis, not authority.

## Evaluation Plan

The role should be treated as an empirical hypothesis.

A useful evaluation compares the same set of non-trivial changes under:

1. ordinary code/design review only;
2. verbose ontology-review checklist;
3. minimal ontology-review prompt with relevant canonical context.

Measure:

- material conceptual issues uniquely found;
- false positives;
- duplicate findings;
- prompt/context cost;
- reviewer latency;
- whether accepted findings lead to simpler or more stable designs;
- whether the ontology review catches defects earlier than implementation review.

The goal is not to prove that every change needs ontology review. The goal is to identify where this specialist operation adds enough value to justify invocation.

## Open Questions

- Should ontology review be a named review type in the Review Bridge or remain a generic specialist-agent role?
- Which changes should trigger it deterministically versus by Orchestrator judgment?
- How should the relevant conceptual neighborhood be selected?
- Should ontology findings be machine-classified into standard categories?
- Which ontology relationships deserve stronger machine-readable semantics?
- Should teleology review remain separate or become an optional companion operation?
- When does a conceptual finding justify changing the ontology itself rather than the reviewed artifact?

## Bridge-Spec Application Note

When this proposal is brought into the Review Bridge Spec discussion, the intended change is narrow:

- add the Ontology Reviewer as a possible specialist review role;
- keep it read-only and non-authoritative;
- route it through the same agent-launching infrastructure as other reviewers;
- let the prompt/review skill generate a compact invocation with only the relevant conceptual context;
- avoid importing the broader ontology research program into the Bridge itself.

The Bridge should use the role; it should not become the ontology system.