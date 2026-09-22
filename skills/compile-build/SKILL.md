---
name: compile-build
version: 0.1-draft
description: Compile a bounded software project or bounded slice into a frozen Implementation Packet before execution. Use when requirements, design, reuse, deterministic work, UI, or verification can be materially resolved before build.
---

# Compile Build

## Governing method

Before compiling, retrieve and follow:

`docs/methodology/ASES Bounded Project Build Method.md`

That document owns the methodology. This skill operationalizes it; do not restate or replace its canonical meaning. If a methodological point remains ambiguous after reading the canon, consult:

`docs/research/pre-build-compilation/Strategy-to-Builder Integration Packet Method - Derivation.md`

only as non-normative evidence.

Use `skills/prompt/SKILL.md` to render the final residual-task prompt.

## Applicability

Default to this operation for nontrivial bounded software projects or bounded slices where pre-build work can materially reduce live implementation reasoning.

Do not force it onto trivial edits. Whole-large-project applicability is unvalidated; compile bounded slices unless project evidence supports a larger freeze.

## Inputs

Identify only what can change compilation:

- objective and user-selected target;
- observable acceptance condition;
- relevant canonical project context;
- current target implementation/repository;
- settled constraints;
- available landscape/source-search tools.

## Procedure

1. Preserve task semantics before optimization.
2. Search broadly enough to find existing implementations, standards, adjacent designs and counterexamples that could change requirements, design or reuse.
3. Iterate requirements/design with search findings until further search is no longer materially changing the candidate solution.
4. Inspect the target and strongest relevant sources; map what to preserve, supersede, adapt, replace or omit.
5. Run the necessity pass on every proposed requirement, feature, component, abstraction, dependency and custom implementation: what fails without it, and can a smaller/native/existing mechanism satisfy the need?
6. Freeze behavior and interfaces. Where UI affects behavior, resolve it with the lightest useful prototype.
7. Precompute and test pure/deterministic logic when this removes work from live implementation.
8. Define pure tests and live acceptance at the same abstraction level as the requirements.
9. Emit the smallest Implementation Packet that contains the execution-changing result of the above work.
10. Compile the builder prompt with `skills/prompt/SKILL.md`.

Freeze only evidence-supported decisions. If an unresolved fact can only be learned in the live environment, expose it as a bounded live assumption rather than inventing an answer.

## Packet

Include only fields that materially affect execution. Typical contents:

- frozen behavior and acceptance;
- relevant current-project state;
- preserve/supersede decisions;
- reduced reusable mechanisms with provenance;
- supplied deterministic components;
- minimal interfaces/configuration;
- frozen UI/assets when applicable;
- persistence/state semantics;
- tests and live acceptance sequence;
- remaining live assumptions;
- stopping condition.

Reference retrievable canonical documents instead of copying their contents.

## Residual task

The builder should integrate and verify, not repeat landscape research, product design, or deterministic work already compiled into the packet.

If live evidence contradicts a frozen mechanism, preserve the required behavior with the smallest compatible substitution and report the concrete incompatibility. Return genuinely strategic conflicts upstream.

## Review boundary

The Implementation Packet is builder/process context. Do not pass it wholesale to clean-room post-build reviewers. Select only the artifact, claim/invariant, explicit assumptions, and canonical definitions required to judge the claim.

## Output

Produce:

1. the frozen Implementation Packet and any supplied artifacts/components;
2. the compact residual-task prompt produced under `skills/prompt/SKILL.md`.

The success criterion is not packet completeness for its own sake. It is that the builder has few unresolved decisions left.
