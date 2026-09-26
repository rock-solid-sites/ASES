---
title: Kernel-0 Evidence Packet
program: EDASES
layer: Research
document_type: Evidence Packet
status: Active
authority: Derived
canonical_repository: ASES
last_updated: 2026-09-26
---

# Kernel-0 Evidence Packet

## Purpose

Provide a compact, realization-neutral evidence base for reasoning about the smallest authoritative substrate required by EDASES.

This packet records established requirements and boundaries. It does not define Kernel-0's internal ontology, primitive vocabulary, state representation, transition vocabulary, implementation architecture, or verification technology.

Earlier kernel designs and implementation experiments are provenance and mechanism evidence, not constraints on the result.

## Source basis

This packet was reconciled from the later EDASES work on:

- the minimal execution substrate;
- the Work Unit / Attachment Point / Execution architecture;
- state-machine determinism and model adequacy;
- formal-verification boundaries;
- later kernel-verification discussion, including reduction of trusted assumptions;
- earlier kernel experiments where they provide relevant provenance or counterexamples.

The source material includes historical branches that made stronger implementation assumptions than the current research direction. Those assumptions are not carried forward merely because they were once concrete.

## Established requirements

### Authoritative state change

There must be an authoritative boundary governing which requested state changes are permitted.

A caller may propose or request an action. The fact that the caller is a particular model, process, human, controller, role, or other actor does not itself make that action authoritative.

Accepted authoritative changes must satisfy the requirements assigned to the substrate and preserve its critical invariants.

Invalid changes must not silently produce a different or partial authoritative mutation.

### Bounded authority

Execution authority is external to the executing model or process.

Prompt instructions are not an authority boundary.

Executors may exercise only authority actually granted to them.

Authority that has ceased to be valid must not remain usable merely because an old executor, process, session, or representation still exists.

Where the architecture requires exclusivity, incompatible authoritative states must not coexist.

### Durable work and disposable execution

The durable object is the work, not the executor.

A Work Unit persists independently of a particular model, process, provider, or session.

An Attachment Point provides durable continuity for an executor-facing position within a Work Unit.

An Execution is temporary and replaceable.

Executor loss must not itself destroy authoritative work state required for continuation.

A stale or superseded Execution must not be able to mutate current authoritative state merely because it previously had access.

Replacing an executor must not require treating the continuing work as a new piece of work.

### Configuration rather than special modes

Single-executor, sequential-executor, and concurrent-executor operation are configurations of the same substrate rather than distinct kernel execution modes.

Shared, isolated, and hybrid resource arrangements are configurations rather than separate architectural products.

Names such as Builder, Reviewer, Researcher, Analyst, or Auditor are higher-level profiles or configurations, not kernel-defined roles.

### Separation of responsibilities

Kernel responsibility is limited to authoritative state and permitted authoritative change.

Semantic judgment about what should be done is outside the Kernel.

The Kernel does not need to determine whether research, code, design, or another substantive work product is correct.

Observation, deterministic derivation, orchestration, workflow, review methodology, project management, issue tracking, reasoning records, and similar higher-level concerns do not become Kernel responsibilities merely because they interact with authoritative state.

### Minimality

The first execution substrate exists to test the Kernel and Work Unit hypothesis, not to reproduce the eventual EDASES harness.

A mechanism belongs in the authoritative substrate only when the required guarantees cannot be obtained without placing that responsibility there.

Inactive Work Units and Attachment Points should not inherently require resident processes or other heavyweight active execution machinery.

## Work Unit as an adequacy constraint

The established architecture is:

```text
Work Unit
    └── Attachment Point
            └── Execution
```

These concepts constrain what the substrate must be capable of supporting.

They must not automatically be projected into Kernel-0 as kernel objects, state variables, or primitive concepts.

The relevant question is whether the required Work Unit guarantees can be expressed and enforced by the eventual Kernel-0 model.

The Work Unit design intentionally left lower-level questions unresolved, including exact state machines, persistence representation, capability-composition semantics, and concrete resource-enforcement mechanisms. Those unresolved choices must not be silently imported into Kernel-0.

## Verification requirements

Kernel-0 is intended to support strong assurance for substrate-critical properties.

The formal target is limited to properties whose failure would make the execution substrate itself untrustworthy. Semantic correctness of arbitrary work is outside that target.

A model is not adequate merely because every transition it contains can be explored.

Before an exhaustiveness claim is meaningful, the model must adequately represent the distinctions relevant to the guarantees it claims. Where correctness depends on event ordering, materially distinct orderings must be representable.

Any later realization must separately establish correspondence between the abstract model and the behavior of the realization. Verification of the model alone does not establish implementation conformance.

Formal claims are conditional on explicitly stated trusted assumptions. They must not imply guarantees below that boundary.

## External effects and assumptions

Kernel-0 reasoning must distinguish authoritative semantics from mechanisms through which a realization interacts with the outside world.

Storage, networking, timers, processes, hardware behavior, runtime behavior, and other external effects may matter to a realization without therefore becoming intrinsic Kernel-0 concepts.

If an external fact can affect authoritative behavior, the model must expose enough of that boundary to reason correctly rather than relying on hidden nondeterminism.

The minimum necessary boundary is intentionally unspecified here.

## Non-assumptions

No current implementation technology is part of the Kernel-0 definition.

This packet assumes no particular:

- programming language;
- proof language;
- compiler;
- instruction-set architecture;
- operating system or microkernel;
- processor architecture;
- processorless or hardware realization;
- database or persistence engine;
- IPC design;
- capability representation;
- scheduler representation;
- clock representation;
- state-machine formalism.

Previous experiments using such mechanisms remain available as evidence after the semantic problem has been reduced enough to make them relevant.

## Historical material

Earlier EDASES work explored several concrete representations of the kernel problem.

Those experiments may contain reusable mechanisms, tests, counterexamples, or rejected assumptions. They do not establish the ontology of Kernel-0.

No historical primitive name, object type, state representation, concurrency mechanism, resource representation, or realization strategy should be retained merely because it appeared in an earlier design.

Historical material should be reintroduced only when it materially helps answer a question raised by current reasoning.

## Deliberately unresolved

This packet does not answer:

- what the irreducible Kernel-0 concepts are;
- what authoritative state Kernel-0 must contain;
- what the minimal transition relation looks like;
- which distinctions are fundamental and which are derived;
- how much identity, ownership, ordering, resource, lifecycle, or external-event information must be represented;
- which architectural concepts can remain entirely outside Kernel-0;
- what realization strategy should eventually be used.

Resolving those questions is the purpose of the next reasoning stage.

If the established requirements are inconsistent, incomplete, or force a distinction not previously recognized, that is a valid result and should be exposed rather than hidden by adding an implementation convention.
