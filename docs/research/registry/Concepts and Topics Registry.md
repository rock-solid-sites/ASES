---
title: Concepts and Topics Registry
program: EDASES
layer: Research
document_type: Registry
status: Active
authority: Canonical
canonical_repository: edases
depends_on:
- Documentation Standard
- Canonical Terminology
- Research Conversation Closeout Standard
consumed_by:
- EDASES research conversations
- Canonical specifications
- Future graph/index tooling
related_documents:
- Concept: Levels of Abstraction
implements: []
implemented_by: []
supersedes: []
superseded_by: []
concepts:
- id: concept:kernel
  name: Kernel
  aliases: []
  status: active
  summary: Trusted authority mechanism that represents and enforces admissible state transitions and user-derived grants; it does not originate root authority.
  canonical_home: null
  reasoning_records:
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
  - EDASES Authority Ontology
  relationships:
  - type: governs
    target: concept:work-unit
  - type: related_to
    target: concept:formal-state-invariants
  future_work:
  - topic:kernel-formal-specification
- id: concept:work-unit
  name: Work Unit
  aliases: []
  status: active
  summary: Kernel-defined bounded durable object whose containment persists independently of active execution; it may exist empty and may contain nested Work Units.
  canonical_home: EDASES Work Unit Component Design
  reasoning_records:
  - EDASES Minimal Execution Substrate — Design and Reasoning Record
  relationships:
  - type: governed_by
    target: concept:kernel
  - type: receives
    target: concept:grant
  - type: has
    target: concept:boundary-record
  - type: participates_in
    target: concept:containment
  - type: may_contain
    target: concept:work-unit
  - type: may_have_activity_described_as
    target: concept:execution
  - type: related_to
    target: concept:formal-state-invariants
  - type: related_to
    target: concept:work-topology
  future_work:
  - topic:work-unit-formal-specification
  - topic:work-unit-prototype-testing
- id: concept:observer
  name: Observer
  aliases: []
  status: active
  summary: Optional subsystem responsible for observing runtime, system, external state, liveness, and time-related facts without owning Kernel authority.
  canonical_home: null
  reasoning_records:
  - EDASES Execution Engine Roadmap
  - EDASES Efficiency Architecture
  relationships:
  - type: provides_to
    target: concept:processor
  - type: related_to
    target: concept:orchestrator
  future_work:
  - topic:observer-design
- id: concept:processor
  name: Processor
  aliases: []
  status: active
  summary: Optional deterministic derivation layer that computes reusable consequences from known state without owning authority or semantic judgment.
  canonical_home: null
  reasoning_records:
  - EDASES Execution Engine Roadmap
  - Phase I Processorless Core Falsification
  - EDASES Efficiency Architecture
  relationships:
  - type: consumes_from
    target: concept:observer
  - type: provides_to
    target: concept:orchestrator
  - type: contains
    target: concept:deterministic-reuse
  future_work:
  - topic:processor-subsystem-design
- id: concept:orchestrator
  name: Orchestrator
  aliases: []
  status: active
  summary: Expected primary user-facing agent role for semantic judgment, planning and delegation; it receives exactly the authority currently delegated by the user and is not required for Kernel correctness.
  canonical_home: null
  reasoning_records:
  - EDASES Authority Ontology
  - EDASES Execution Engine Roadmap
  relationships:
  - type: consumes_from
    target: concept:processor
  - type: related_to
    target: concept:observer
  - type: uses
    target: concept:api-capability-surface
  future_work: []
- id: concept:api-capability-surface
  name: API Capability Surface
  aliases: []
  status: active
  summary: Thin externally actionable surface exposed to activity through current Work Unit attachments without requiring direct knowledge of internal higher-level machinery.
  canonical_home: EDASES Work Unit Component Design
  reasoning_records:
  - EDASES Authority Ontology
  relationships:
  - type: related_to
    target: concept:orchestrator
  - type: related_to
    target: concept:attachment
  - type: historically_constrained
    target: concept:executor-authority
  future_work: []
- id: concept:executor-authority
  name: Executor Authority
  aliases: []
  status: historical
  summary: Earlier framing in which bounded authority was attached to a distinct executor/execution object; retained for lineage, while the current Work Unit model expresses authority through Kernel grants, attachments, and containment.
  canonical_home: EDASES Work Unit Component Design
  reasoning_records:
  - EDASES Minimal Execution Substrate — Design and Reasoning Record
  relationships:
  - type: historically_part_of
    target: concept:work-unit
  - type: superseded_by
    target: concept:grant
  - type: superseded_by
    target: concept:attachment
  - type: constrained_by
    target: concept:kernel
  future_work:
  - topic:work-unit-formal-specification
- id: concept:grant
  name: Grant
  aliases:
  - Granted Relationship
  status: provisional
  summary: Kernel-authorized bounded relationship by which a Work Unit receives a resource, capability, or other relation; current resource/attachment distinctions specialize how the grant is exposed.
  canonical_home: EDASES Work Unit Component Design
  reasoning_records: []
  relationships:
  - type: governed_by
    target: concept:kernel
  - type: applies_to
    target: concept:work-unit
  - type: specialized_as
    target: concept:resource
  - type: specialized_as
    target: concept:attachment
  future_work:
  - topic:work-unit-formal-specification
- id: concept:resource
  name: Resource
  aliases: []
  status: provisional
  summary: Convenience term for a Kernel-granted thing or relationship that supports or bounds a Work Unit but is not internally actionable merely by virtue of that grant.
  canonical_home: EDASES Work Unit Component Design
  reasoning_records: []
  relationships:
  - type: specialization_of
    target: concept:grant
  - type: granted_to
    target: concept:work-unit
  future_work:
  - topic:work-unit-formal-specification
- id: concept:attachment
  name: Attachment
  aliases:
  - Attached Capability
  status: provisional
  summary: Convenience term for a Kernel-granted relationship exposed internally across a Work Unit boundary so activity inside the Work Unit can act through it; attachments collectively form the thin external API.
  canonical_home: EDASES Work Unit Component Design
  reasoning_records: []
  relationships:
  - type: specialization_of
    target: concept:grant
  - type: exposed_within
    target: concept:work-unit
  - type: related_to
    target: concept:api-capability-surface
  future_work:
  - topic:work-unit-formal-specification
- id: concept:attachment-point
  name: Attachment Point
  aliases: []
  status: superseded
  summary: Historical Work Unit concept for a durable executor-facing position defining tools, resources, permissions, and continuity; no longer a current primitive, with its relevant boundary semantics absorbed by grants and attachments.
  canonical_home: EDASES Work Unit Component Design
  reasoning_records:
  - EDASES Minimal Execution Substrate — Design and Reasoning Record
  relationships:
  - type: superseded_by
    target: concept:grant
  - type: superseded_by
    target: concept:attachment
  future_work: []
- id: concept:execution
  name: Execution
  aliases: []
  status: provisional
  summary: Descriptive term for activity or state evolution occurring inside a Work Unit; not currently a separate Kernel primitive or required durable object.
  canonical_home: EDASES Work Unit Component Design
  reasoning_records:
  - EDASES Minimal Execution Substrate — Design and Reasoning Record
  relationships:
  - type: occurs_within
    target: concept:work-unit
  - type: not_a_primitive_of
    target: concept:kernel
  future_work:
  - topic:work-unit-formal-specification
- id: concept:containment
  name: Work Unit Containment
  aliases:
  - Nested Work Unit Containment
  status: provisional
  summary: Relationship by which one Work Unit exists within another; containment grants no automatic inheritance, and a child cannot exceed the effective capability allowed by its full containment chain.
  canonical_home: EDASES Work Unit Component Design
  reasoning_records: []
  relationships:
  - type: relates
    target: concept:work-unit
  - type: constrained_by
    target: concept:kernel
  future_work:
  - topic:work-unit-formal-specification
- id: concept:boundary-record
  name: Work Unit Boundary Record
  aliases:
  - Boundary Metadata
  status: provisional
  summary: Intrinsic Kernel-maintained metadata attached to a Work Unit's construction rather than stored as ordinary interior content; it supports identification and recovery but cannot by itself prove currentness against rollback.
  canonical_home: EDASES Work Unit Component Design
  reasoning_records: []
  relationships:
  - type: part_of
    target: concept:work-unit
  - type: maintained_by
    target: concept:kernel
  - type: related_to
    target: concept:formal-state-invariants
  future_work:
  - topic:work-unit-formal-specification
- id: concept:formal-state-invariants
  name: Formal State Invariants
  aliases:
  - Formal verification boundary
  status: active
  summary: Critical substrate invariants and transition-correctness properties selected for formal verification; semantic correctness is excluded.
  canonical_home: null
  reasoning_records:
  - Kernel-0 Verification Obligations
  - EDASES Phase I Core Substrate Closure
  relationships:
  - type: constrains
    target: concept:kernel
  - type: constrains
    target: concept:work-unit
  - type: alternative_to
    target: concept:semantic-correctness-verification
  future_work:
  - topic:work-unit-formal-specification
- id: concept:semantic-correctness-verification
  name: Semantic Correctness Verification
  aliases: []
  status: active
  summary: External or domain-specific evaluation of whether work meaningfully satisfies intent; explicitly outside the formally verified substrate.
  canonical_home: null
  reasoning_records:
  - EDASES Authority Ontology
  - EDASES Execution Engine Roadmap
  relationships:
  - type: alternative_to
    target: concept:formal-state-invariants
  future_work: []
- id: concept:deterministic-reuse
  name: Deterministic Reuse
  aliases:
  - Unified caching model
  status: active
  summary: Reuse of deterministic computation through cheap applicability checks, provenance, invalidation, and recomputation only when needed.
  canonical_home: null
  reasoning_records:
  - EDASES Efficiency Architecture
  - Phase I Processorless Core Falsification
  relationships:
  - type: part_of
    target: concept:processor
  future_work:
  - topic:processor-subsystem-design
- id: concept:work-topology
  name: Work Topology
  aliases: []
  status: active
  summary: Optional relationships among multiple Work Units used for dependency, decomposition, coordination, and integration at scale.
  canonical_home: null
  reasoning_records:
  - EDASES Minimal Execution Substrate — Design and Reasoning Record
  relationships:
  - type: relates
    target: concept:work-unit
  - type: related_to
    target: concept:sfc
  future_work:
  - topic:scaled-orchestration
- id: concept:sfc
  name: Scaffold-Fork-Converge
  aliases:
  - SFC
  status: active
  summary: Optional scaled-work strategy using scaffolded state, parallel forks, and deterministic or semantic convergence where appropriate.
  canonical_home: null
  reasoning_records:
  - EDASES Minimal Execution Substrate — Design and Reasoning Record
  relationships:
  - type: part_of
    target: concept:work-topology
  future_work:
  - topic:scaled-orchestration
- id: concept:minimal-prototype
  name: Minimal Prototype
  aliases: []
  status: active
  summary: Initial experiment containing only a bounded Kernel/Work Unit realization and enough observation to test substrate behavior without assuming later optional subsystems.
  canonical_home: null
  reasoning_records:
  - EDASES Execution Engine Roadmap
  - EDASES Phase I Core Substrate Closure
  - Phase I Core Substrate Verification Work
  relationships:
  - type: contains
    target: concept:kernel
  - type: contains
    target: concept:work-unit
  - type: excludes
    target: concept:observer
  - type: excludes
    target: concept:processor
  future_work:
  - topic:work-unit-prototype-testing
topics:
- id: topic:kernel-formal-specification
  name: Kernel Formal Specification
  aliases: []
  status: active
  summary: Reconcile and maintain the abstract Kernel contract, capabilities, transitions, assumptions, and critical invariants.
  canonical_home: null
  reasoning_records:
  - EDASES Minimal Execution Substrate — Design and Reasoning Record
  relationships:
  - type: concerns
    target: concept:kernel
  - type: related_to
    target: concept:formal-state-invariants
  future_work: []
- id: topic:work-unit-formal-specification
  name: Work Unit Formal Specification
  aliases: []
  status: active
  summary: Specify the bounded-object Work Unit model, Kernel grants and attachments, containment, lifecycle/destruction transitions, recovery/currentness assumptions, and formally verified invariants.
  canonical_home: null
  reasoning_records:
  - EDASES Minimal Execution Substrate — Design and Reasoning Record
  relationships:
  - type: concerns
    target: concept:work-unit
  - type: concerns
    target: concept:grant
  - type: concerns
    target: concept:attachment
  - type: concerns
    target: concept:containment
  - type: concerns
    target: concept:boundary-record
  - type: concerns
    target: concept:execution
  - type: depends_on
    target: topic:kernel-formal-specification
  future_work: []
- id: topic:work-unit-prototype-testing
  name: Work Unit Prototype Testing
  aliases: []
  status: active
  summary: Adversarially test implementation conformance, recovery, races, stale authority, and reconstruction against the formal substrate model.
  canonical_home: null
  reasoning_records:
  - EDASES Minimal Execution Substrate — Design and Reasoning Record
  relationships:
  - type: depends_on
    target: topic:work-unit-formal-specification
  - type: concerns
    target: concept:minimal-prototype
  future_work: []
- id: topic:processor-subsystem-design
  name: Processor Subsystem Design
  aliases: []
  status: active
  summary: Define the Processor's internal modularity, deterministic tool interface, caching, invalidation, graph derivation, and escalation boundaries.
  canonical_home: null
  reasoning_records:
  - EDASES Minimal Execution Substrate — Design and Reasoning Record
  relationships:
  - type: concerns
    target: concept:processor
  - type: contains
    target: concept:deterministic-reuse
  future_work: []
- id: topic:observer-design
  name: Observer Design
  aliases: []
  status: deferred
  summary: Define unified runtime observation, liveness, timekeeping, change detection, and fact delivery without assigning semantic judgment to the Observer.
  canonical_home: null
  reasoning_records:
  - EDASES Minimal Execution Substrate — Design and Reasoning Record
  relationships:
  - type: concerns
    target: concept:observer
  future_work: []
- id: topic:scaled-orchestration
  name: Scaled Orchestration and SFC
  aliases: []
  status: deferred
  summary: Explore optional dependency graphs, waves, convergence, and integration once ordinary independent Work Units are insufficient.
  canonical_home: null
  reasoning_records:
  - EDASES Minimal Execution Substrate — Design and Reasoning Record
  relationships:
  - type: concerns
    target: concept:work-topology
  - type: concerns
    target: concept:sfc
  - type: depends_on
    target: topic:work-unit-prototype-testing
  future_work: []
- id: topic:crosslink-decomposition
  name: Crosslink Decomposition
  aliases: []
  status: deferred
  summary: Reassess which current Crosslink responsibilities belong in storage, Processor, Kernel, API, or other components after the substrate is proven.
  canonical_home: null
  reasoning_records:
  - EDASES Minimal Execution Substrate — Design and Reasoning Record
  relationships:
  - type: related_to
    target: concept:kernel
  - type: related_to
    target: concept:processor
  - type: related_to
    target: concept:api-capability-surface
  - type: depends_on
    target: topic:work-unit-prototype-testing
  future_work: []
- id: topic:checkpointing-and-stacked-diffs
  name: Checkpointing and Stacked Diffs
  aliases: []
  status: deferred
  summary: Determine the eventual boundary between Work Unit recovery checkpoints, shared integration states, and semantic Git history.
  canonical_home: null
  reasoning_records:
  - EDASES Minimal Execution Substrate — Design and Reasoning Record
  relationships:
  - type: concerns
    target: concept:work-unit
  - type: related_to
    target: topic:scaled-orchestration
  future_work: []
last_updated: '2026-09-28'
---

# Concepts and Topics Registry

## Authority boundary

This registry is **canonical for conceptual identity, aliases, lineage, and graph relationships only**.

It is **not canonical for substantive architectural truth**. The `summary` field is an identifying orientation aid, not a specification. When a concept has a canonical home, that document defines the concept. When it does not, relevant reasoning records contain the current substantive discussion.

A registry entry must never silently override, reinterpret, or expand a canonical specification.

## Purpose

The registry gives stable identities to concepts and research/design topics so that relationships survive conversation boundaries, title changes, terminology changes, and future tooling migrations.

The YAML frontmatter is the machine-readable graph source. The body explains registry policy and should not be parsed as the authoritative graph representation.

## Provisional Work Unit ontology build baseline — 2026-09-27

The current Work Unit ontology is sufficiently stable to constrain the first build, but its names, decomposition, and primitive status are **not frozen**. The substantive source is `EDASES Work Unit Component Design`; this registry only records identities, lineage, and relationships useful to implementation and review.

For the first build, implementations should preserve these conceptual boundaries:

- a Work Unit is a Kernel-defined bounded durable object and remains valid even when empty;
- resources and attachments are both Kernel-granted relationships, with the distinction determined by whether the grant is internally actionable across the Work Unit boundary;
- attachments collectively form the thin API exposed to activity inside the Work Unit;
- Execution currently names activity inside a Work Unit rather than a separate durable Kernel object;
- `Attachment Point` and `Executor Authority` are retained as historical identities but must not be reintroduced as required primitives merely because older documents used them;
- nested Work Units inherit nothing automatically and cannot exceed the effective authority available through their full containment chain;
- containment and management authority are distinct relationships;
- an empty child Work Unit remains independently bounded by both its own boundary and each containing Work Unit boundary;
- stopping or losing execution does not release Work Unit contents;
- destruction cannot make contained objects unbounded: durable contents must be transferred into another bounded location or deleted, and nested Work Units must be transferred/reparented or recursively destroyed before the containing Work Unit ceases to exist;
- the Work Unit boundary record is intrinsic Kernel-maintained metadata, not ordinary mutable interior content; at minimum it tracks resources granted, capabilities attached, created-by provenance, agent attachment, and associated project, updating when the Kernel changes the relevant relationship;
- boundary metadata assists discovery and recovery but cannot establish its own currentness against rollback;
- a restarted compatible engine may mediate a durable Work Unit only by re-establishing current authority; engine-process identity is not permanent ownership;
- the last-recorded capability attachments are retained as recovery context but are not current after engine loss; they require fresh authorized reassessment before reattachment, normally through the Orchestrator in the expected user-facing operating model;
- sealing disables affected outward capability use but does not inherently stop resource-backed internal computation;
- reparenting is permitted in principle and may move a sealed Work Unit into another Work Unit before reactivation under a newly valid set of resources and capabilities;
- completion of work does not itself export its products across the boundary.

The lifecycle words **sealed**, **revoked**, **destroyed**, **transfer**, and **reparent** are useful current vocabulary but have not yet been promoted to stable concept IDs. Their exact state-machine meanings should be established by the Work Unit formal specification and build evidence.

Candidate generalization retained for testing rather than treated as a theorem:

> A state wholly contained within a rollback domain cannot, using only information rolled back with it, establish that it is the current state of that domain.

This baseline should be revised when implementation, formalization, or adversarial review demonstrates that a distinction is unnecessary, incorrectly located, or missing.

## Maintenance rules

- Update the registry at research-conversation closeout whenever conceptual identity, aliases, lineage, canonical homes, or material relationships change.
- Keep summaries compact and non-normative.
- Preserve aliases when terminology changes.
- Mark supersession explicitly rather than deleting historical nodes.
- Prefer stable `concept:<slug>` and `topic:<slug>` identifiers.
- When a Topic becomes a Concept, retain the Topic node and add an explicit lineage relationship rather than silently renaming it.
- Detailed definitions, invariants, requirements, and architecture belong in their canonical documents or reasoning records, not here.
- `status: provisional` means the identity is useful enough to reference during design/build but its name, boundary, or primitive status may change.
- `status: historical` or `status: superseded` preserves prior conceptual identities for lineage and reasoning; it must not be treated as current architecture without an explicit re-promotion decision.