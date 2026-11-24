---
title: Execution Engine Vision
version: 2026-11-24.1
program: ASES
layer: Architecture
document_type: Architecture Vision
status: Active
authority: Canonical
canonical_repository: ases
depends_on:
  - docs/methodology/AI Orchestration Guide.md
  - docs/requirements/Methodology to Requirements Mapping Specification.md
  - docs/research/kernel-0/Kernel-0-Evidence-Packet.md
related_documents:
  - docs/historical/Engine Architecture and Experiment History.md
  - docs/architecture/Task-Scoped Information Architecture Decision 2026-11-21.md
last_updated: 2026-11-24
---

# Execution Engine Vision

## Purpose and current boundary

ASES defines how engineering should be performed; the execution engine supports and mechanically enforces the applicable requirements where justified. It is not a replacement for the human operator, model judgment, development tools, or the methodology itself. This document describes the intended responsibilities and boundaries, **not a deployed architecture or a frozen implementation design**.

The engine should coordinate durable work, enforce authority at the actual effect boundary, preserve verifiable evidence and allow continuation despite disposable executors. It should minimize unnecessary reasoning, repeated context, resource consumption and operator intervention. Human approval and engineering judgment remain outside the mechanical substrate.

## Established authority and continuity requirements

The [Kernel-0 Evidence Packet](../research/kernel-0/Kernel-0-Evidence-Packet.md) is the realization-neutral source for substrate requirements and their unresolved semantic questions. It is intentionally not expanded with November implementation findings: it remains suitable as neutral input to open derivation.

- **Kernel:** governs authoritative state and permitted authoritative change. An executor's identity, instructions, declared role or claims do not confer authority. An invalid request must not cause partial or different authoritative mutation; stale or revoked execution authority must not remain usable.
- **Work Unit → Attachment Point → Execution:** durable work, durable executor-facing continuity position, replaceable execution. These are consumer requirements on the substrate, not an assertion that all three are Kernel objects. Replacing an execution must preserve continuing work identity while excluding superseded execution authority.
- **Verification:** distinguish semantic adequacy of a model from implementation conformance and evidence of real behavior. Formal claims are conditional on explicit trusted assumptions. Local process histories, synthetic property tests and a correctly functioning ledger each establish only their tested properties.

Single/sequential/concurrent execution, resource sharing/isolation, and higher-level role profiles are configurations, not separate Kernel modes. Keep orchestration, semantic judgment, observation, resource management, issue tracking, review and project knowledge outside the Kernel unless a necessary authoritative guarantee demonstrates otherwise. No language, database, workflow engine, graph store, scheduler or hosting platform is selected by this vision.

## Responsibilities above the substrate

| Responsibility | Intended boundary |
| --- | --- |
| Execution coordination | Thin, replaceable execution API; bounded dispatch and observable outcomes, durable continuation and explicit cancellation/stop authority. No blind duplicate launch when outcomes are unknown. Model harnesses and providers remain replaceable. |
| Resource planning and admission | Advisory planning is distinct from authoritative admission and bounded resource reservation, launch, observation and settlement. The [Resource Solver reconciliation](../research/Resource%20Solver%20Specification%20Reconciliation%202026-11-02.md) records the experimental subsystem design; it is not the Kernel or a deployed control plane. |
| Methodology and assurance | Apply the relevant workflow and verification criteria rather than a universal pipeline. Mechanically enforce authorized gates only where the governing rule and effect boundary are established. Support independent review and human acceptance without transferring judgment to the Kernel. |
| Context and evidence | Select task-relevant current information; preserve decisions, reasoning, rejected alternatives and source-bound evidence at their existing durable homes. Follow the [accepted task-scoped architecture](Task-Scoped%20Information%20Architecture%20Decision%202026-11-21.md); no mandatory graph, resolver, service or session ritual. |
| Human planning and visibility | Expose meaningful status, dependencies, uncertainty and interventions. Git retains technical artifacts; Work Notes retains operational position; Projektor retains planning and adoption decisions. Do not assume a new global state database or UI must replace them. |

Recoverability means recovering authoritative state and the actual disposition of effects, not guessing that a process completed, that an unseen response meant no effect, or that a recorded job is the continuing Work Unit. Separate launch intent, observed execution, effect acceptance, publication, observation and finalization where their distinction matters.

## Current implementation and assurance position

The November research has native authority/ownership and local Rust execution/custody experiments on **separate unmerged PR stacks**. They demonstrate specific bounded mechanisms and counterexamples, not an integrated Kernel, production launcher, universal security boundary or completed Work Unit model. The [engine architecture and experiment history](../historical/Engine%20Architecture%20and%20Experiment%20History.md) records source-pinned reports, earlier alternatives and current work pointers.

The latest prepared handoffs in [experimental PR #77](https://github.com/rock-solid-sites/ASES/pull/77) address a confirmed native pending-effect admission defect and Work Unit adequacy against the Rust prototype. They are preparation, not evidence of a repaired implementation or newly passing tests. In particular, native replacement of an execution for the same Work Unit and Attachment Point, with atomic exclusion of the old authority, remains a discriminating adequacy question. Neither a durable job ID nor a process exit check is sufficient.

Human integration planning is ASES-8; current technical continuation is WNASES-4, with dependency inventory and independent replay tracked separately. Consult current work records and pinned source before dispatching. Do not merge experimental components or revive the retired Crosslink/VPS setup on the strength of this vision.

## Rationale and history

The original architecture vision emphasized traceable reasoning, recoverable state and mechanical enforcement. Earlier state-gated engine proposals and technology surveys explored many concrete mechanisms; adversarial reviews challenged prematurely selected stacks, insufficient falsifiers and overlapping lifecycle ownership. The present boundaries retain the useful goals while refusing to elevate implementation convenience or historical labels into authoritative semantics.

See [Engine Architecture and Experiment History](../historical/Engine%20Architecture%20and%20Experiment%20History.md) for the original vision, proposal, reviews, UI/system surveys, neutral derivation packet and November evidence. The [methodology-to-requirements mapping](../requirements/Methodology%20to%20Requirements%20Mapping%20Specification.md) defines the higher-level requirement boundary. Revise implementation requirements through evidence and explicit decisions, not silent promotion of an experiment.
