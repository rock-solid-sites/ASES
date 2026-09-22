---
title: ASES Bounded Project Build Method
program: ASES
layer: Methodology
document_type: Methodology Specification
status: Active
authority: Canonical
canonical_repository: ases
depends_on:
  - docs/methodology/AI Orchestration Guide.md
consumed_by:
  - skills/prompt/SKILL.md
  - bounded project build workflows
related_documents:
  - docs/research/pre-build-compilation/Strategy-to-Builder Integration Packet Method - Derivation.md
  - docs/research/prompting/Ontological Connection to Review Skill.md
  - docs/methodology/Clean Room Execution Guide.md
last_updated: 2026-09-22
---

# ASES Bounded Project Build Method

## Purpose

Default preparation method for bounded software projects: resolve each decision at the earliest layer with enough evidence to resolve it reliably, then do not pay to resolve it again downstream.

The method compiles research, requirements, design, reuse, deterministic work, UI decisions and verification into the smallest residual implementation task. It is methodology, not an execution component; authority and confinement remain external.

Applicability to whole large projects is unvalidated. Until evidence supports otherwise, apply it to bounded slices. Trivial changes may collapse the procedure to target → inspect → implement → verify.

## Invariants

- Preserve the user-selected target, required behavior and settled constraints before optimizing execution.
- Search before invention. Broad landscape search may confirm a design or change it; stop when additional search no longer materially changes requirements, design or the reuse map.
- Reuse selectively. Extract mechanisms that satisfy requirements; do not inherit upstream architecture merely because it exists.
- Every proposed requirement, feature, component, abstraction, dependency and custom implementation must survive a necessity test: what fails if it is removed, and can a smaller, native or existing mechanism satisfy the same need?
- Move deterministic or pure work earlier when practical; do not spend live build inference recomputing settled results.
- Reference canonical project meaning rather than duplicating it into packets or prompts.
- Freeze only what evidence supports. Reopen frozen decisions only on concrete contradictory evidence from the live environment or acceptance tests.
- Verify completion at the abstraction level of the requirement.

## Procedure

### 1. Establish target and acceptance

Identify the objective, observable behavior, settled constraints and completion condition. Implementation convenience must not substitute for task semantics.

### 2. Landscape reconnaissance

Search broadly for existing implementations, protocols, standards, adjacent designs and counterexamples that could alter requirements, design or build scope. Search and design may iterate.

### 3. Requirements and design

Define required behavior, states, boundaries, failure semantics and interfaces. Search findings are evidence: they may supply mechanisms or cause requirements/design to change.

### 4. Targeted source inspection and reuse map

Inspect the current target and the strongest relevant implementations. Record what to preserve, supersede, adapt, replace or omit. Prefer exact mechanisms over whole upstream systems.

### 5. Necessity pass

For each surviving element ask:

1. What current requirement fails without it?
2. Can it be removed entirely?
3. Can a native or already-present mechanism replace it?
4. Can a smaller subset satisfy the requirement?
5. Does it introduce downstream code, state, permissions, tests or review cost disproportionate to its value?

During implementation the same principle may descend to files, functions, branches and lines: code should trace to a requirement, invariant, integration necessity or verified platform constraint.

### 6. Specification and prototype

Freeze behavior before build. Specify state transitions, persistence/update rules, naming/path rules, output semantics, failure behavior and acceptance evidence. Where UI materially affects behavior, resolve it with the lightest useful artifact: text layout, mockup, interactive prototype or real component prototype.

### 7. Precompute deterministic work

Write and test pure logic before live integration when doing so reduces builder reasoning: state classification, filtering, sorting, transformations, renderers, retry policy, naming, small contracts and similar deterministic work.

### 8. Pre-build compilation

Assemble an Implementation Packet containing only information that can change execution. A packet may include:

- frozen behavior and acceptance;
- relevant current-project state and preserved/superseded components;
- reduced external mechanisms with provenance;
- supplied deterministic components;
- minimal interfaces and configuration;
- frozen UI/assets where applicable;
- persistence/state semantics;
- pure tests and live acceptance sequence;
- live assumptions that still require verification;
- explicit stopping condition.

Not every packet needs every field. The packet is task context, not a replacement for canonical project knowledge.

### 9. Execute the residual task

The builder integrates and verifies rather than repeating research or product design. If live evidence contradicts the packet, make the smallest compatible substitution, preserve the required behavior, record the evidence and return genuinely strategic conflicts upstream.

### 10. Verify independently

Operational acceptance may use the packet. Formal post-build review follows clean-room rules: the packet is process history and should not be supplied wholesale. Provide the artifact, concrete claim/invariant, explicit assumptions and the minimum canonical definitions needed to judge it.

### 11. Preserve reusable results

Feed durable findings, reusable mechanisms, new constraints and corrected canonical meaning back into the appropriate project knowledge so later work does not repeat the same inference.

## Relationships

- **Prompt Skill:** compiles the operation-specific prompt and selected context. When a frozen Implementation Packet exists, the prompt normally references it rather than restating it.
- **Work Unit:** bounds authority and execution state. The packet constrains work content but grants no capability.
- **Orchestration:** decides decomposition, routing and whether pre-build compilation is worthwhile; it should not recreate decisions already compiled.
- **Review:** independently tests finished claims; packet/process history is withheld when clean-room evidence is required.

## Output

For a nontrivial bounded build, the normal preparation output is a frozen Implementation Packet plus a compact residual-task prompt. The desired result is not merely better instructions: the builder should have few unresolved decisions left.