---
title: State-Model Applicability and Reuse Method
program: ASES
layer: Methodology
document_type: Methodology Specification
status: Active
authority: Canonical
canonical_repository: ases
depends_on:
  - docs/methodology/ASES Bounded Project Build Method.md
related_documents:
  - docs/methodology/Implementation Realization and Assurance Selection Method.md
  - VSDD Adaptation Profile — State-Based Specifications (historical Library draft, 2026-08-29)
  - ASES Universal Conformance Checklist — State-Based Artefacts (historical Library draft, 2026-08-29)
consumed_by:
  - project behavioral specifications
  - project verification architectures
  - project conformance suites
last_updated: 2026-10-30
---

# State-Model Applicability and Reuse Method

## Purpose

Evaluate **whether**, **where**, and **how** state-based modeling improves a project's specification, construction, testing and verification. Assess the suitability of a state machine before selecting implementation technology. A project may be described as a state-transition system while its realization is processorless, hardware-based, declarative or software-based.

State machines are a useful representation, not a mandated universal architecture or a competing methodology. VSDD supplies test-first and verification gates where adopted; the existing state-based VSDD adaptation profile and universal conformance checklist supply the detailed conformance dimensions. Do not duplicate or weaken them here.

## Applicability assessment

During behavioral specification, seek concrete evidence of:
- distinguishable states and events;
- guards, legal and forbidden transitions;
- identity, ownership, authority and durable lifecycle;
- interruptions, recovery, retries, or asynchronous work;
- concurrent events, ordering and cancellation;
- invariants, terminal conditions or external-resource settlement.

Then ask: **Would modeling these distinctions yield testable guarantees, reveal illegal transitions, or reduce ambiguity more effectively than a simpler representation?** Do not model incidental implementation steps as authoritative state.

Record one outcome for each significant component:

- **PRIMARY:** state/transition semantics are the main behavioral representation.
- **SUPPLEMENTARY:** a model covers a meaningful lifecycle, protocol or authority boundary while other models describe computation.
- **NOT APPLICABLE:** no material modeling advantage was established, with a short reason.
- **UNRESOLVED:** perform the smallest discriminating model experiment before fixing architecture.

A mixed project may have different outcomes for different components.

## Minimal model experiment

For PRIMARY, SUPPLEMENTARY or UNRESOLVED candidates:
1. Identify the authoritative entities, state and initial/terminal conditions.
2. Specify events, guards, allowed/forbidden transitions and effects.
3. State critical invariants, identity/ownership and ordering conditions.
4. Separate requested, authoritative and observed state; distinguish success acknowledgement from physical resource settlement.
5. Identify network/process/storage/time/hardware boundaries and justify abstractions.
6. Construct the cheapest plausible forbidden trace, counterexample or adversarial interleaving.

If these do not clarify material behavior or provide discriminating verification, reject or narrow the state model; do not invent a universal engine.

## Verification and reuse

When applicable, instantiate the existing state-based VSDD adaptation and conformance checklist. Derive model-based tests or proof obligations for critical guards, transitions, concurrency, failures, forbidden states and external settlement. Separately demonstrate model correctness and *implementation/realization conformance*. A proof of abstract state legality does not prove that processes have stopped, credentials are isolated, or hardware complies.

Projects should compare reusable mechanisms such as state representations, invariant checkers, model exploration, counterexample traces, property-based test generation, fault injection, model-to-implementation adapters and evidence reports. Share mechanisms whose reuse is supported by repeated successful application; leave domain-specific transitions and authority decisions within each project. Avoid installing a DSL or heavyweight orchestration engine unless necessity is demonstrated.

A state model is versioned alongside requirements, assumptions, verified claims and acceptance evidence. New counterexamples reopen the relevant model and tests rather than merely adding implementation patches.

## Phase and scope boundary

Model suitability is assessed during behavior specification. Verification method, abstraction and implementation-conformance strategy are selected in the existing verification-architecture step (VSDD Phase 1b where VSDD is used). Keep VSDD's test-first, adversarial, hardening and convergence process intact. The applicability method is not another VSDD phase, not a universal proof requirement and not a replacement for other forms of testing.

## Crosslink MCP example

For the remote shell MCP, command/session ownership and stop/cancellation form PRIMARY state models. Authentication and tunnel connection lifecycles may be SUPPLEMENTARY; individual JSON parsing need not be state-machine driven. A terminal state labelled "stopped" cannot be accepted without an independently enforceable resource-settlement observation, such as correctly scoped cgroup termination. Implementing the same state model in Python, Rust or nontraditional architecture does not by itself settle the guarantee.

## Governing principle

**Evaluate state-machine suitability before implementation choice, use modeling where it materially strengthens precision or testability, and preserve reusable verification mechanisms without turning every project into a state machine.**
