---
title: EDASES Work Unit Component Design
program: EDASES
layer: Architecture
document_type: Specification
status: Active
authority: Canonical
canonical_repository: edases

depends_on:
  - Concept: Kernel
  - Concept: Levels of Abstraction
  - Work Unit — Design and Reasoning Record

consumed_by:
  - Work Unit Formal Specification
  - Work Unit Prototype Testing
  - Future Work Unit build plan

related_documents:
  - Concepts and Topics Registry
  - Prime Agent → EDASES: Major Architectural Conclusions
  - Gas Town Deep Dive: An Architectural Archaeology

implements: []
implemented_by: []
supersedes: []
superseded_by: []

last_updated: 2026-09-27
---

# EDASES Work Unit — Component Design

> **Canonical update — 2026-09-27**
>
> Sections **A–L** below are the current canonical Work Unit model. They supersede conflicting definitions in the earlier design record while preserving that record in full for reasoning provenance. In particular, the earlier strict hierarchy `Work Unit → Attachment Point → Execution`, the definition of Attachment Point as an executor position, and the definition of Execution as a disposable runtime instance are no longer canonical.
>
> The complete 2026-09-13 design follows afterward under **Historical Design and Reasoning Record**. It is intentionally retained rather than rewritten away so that the design path, discarded hypotheses, motivations, and still-compatible material remain inspectable.

## A. Current canonical definition

A **Work Unit** is a bounded object created, defined, modified, and revocable by the Kernel.

The minimum theoretical Work Unit requires no agent, active computation, file, tool, CPU allocation, memory allocation, attachment, or child Work Unit. An empty bounded object is still a Work Unit.

The Kernel may grant a Work Unit resources, capabilities, relationships, and containment. These grants define what can exist within the Work Unit and how anything inside it may affect or be affected by the world outside its boundary.

Conceptually:

```text
Kernel
  └── Work Unit W
       ├── bounded interior
       ├── granted resources
       ├── attached capabilities
       ├── optional nested Work Units
       └── execution, if any, occurring inside
```

The Work Unit is not intrinsically an agent session, task, workflow, container, VM, process, worktree, issue, context packet, or methodology object. Those may be represented inside it or related to it through Kernel-controlled grants.

The core security intuition is that the minimal Work Unit behaves like a completely confined enclave within the assumed computer/physical trust boundary: absent a Kernel-authorized relationship across its boundary, nothing inside it can affect the outside world and no outside resource becomes internally actionable merely by existing elsewhere on the machine.

## B. Grants, resources, and attachments

At the underlying ontology level, a **resource** and an **attachment** are both Kernel-granted relationships involving a Work Unit. The distinction is operational rather than ontological.

- A **resource** is granted to support or bound the Work Unit but is not directly actionable from inside the Work Unit merely by virtue of the grant. CPU capacity, memory capacity, or other substrate allocations may be resources.
- An **attachment** is a granted relationship that is exposed across the Work Unit boundary so activity inside the Work Unit can act through it. Shell commands, network access, external services, tools, filesystems, agent/model connections, or other callable interfaces may be attachments.

The attachments collectively form the Work Unit's **thin API to the outside world**.

Conceptually:

```text
resource grant
    Kernel ──grant──> W
    supports/bounds W
    not directly invoked from inside

attachment
    W ──Kernel-mediated boundary relation──> outside capability/resource
    exposed internally through the thin API
```

Granting a capability means creating or widening an authorized boundary relationship. Revoking it means removing or narrowing that relationship. A model prompt or process assertion cannot create authority that the Kernel has not granted.

A Work Unit with no attachments remains valid and sealed from external action even if it has internal contents or allocated resources.

## C. Execution

**Execution** is a descriptive term for whatever activity or state evolution occurs inside a Work Unit. It is not currently a separate Kernel primitive and does not require a durable `Execution` object.

The term **executor** is not required by the ontology. An agent, process, model session, deterministic computation, human-driven interface, or other mechanism may participate through an attachment, but the identity of that mechanism does not define the Work Unit or the continuity of its work.

For example, if an agent writes the numbers `1` through `50`, its stream dies, and a different agent later writes `51` through `100`, the durable work remains one continuing body of work in the same Work Unit. The agent and its live connection are disposable; the bounded Work Unit and its accepted contents are what matter.

This implies:

> **The lifetime of containment is independent of the lifetime of execution.**

Loss of an agent, stream, process, engine instance, or active attachment must not implicitly destroy the Work Unit or release its contents.

## D. Intrinsic boundary record

A Work Unit carries an intrinsic **boundary record** as part of its Kernel-defined construction. This is analogous to a label fixed to the outside of a box rather than a note stored among the contents inside the box.

The boundary record is Kernel-maintained metadata about the bounded object. It is not ordinary mutable Work Unit content and cannot be rewritten from inside the Work Unit merely by editing a file or producing output.

At minimum the record must represent:

- Work Unit identity/genesis;
- **created by** provenance;
- associated **project**;
- current containment/parent relationship, if any;
- **resources granted**;
- **capabilities attached**;
- **agent attached**, if any;
- lifecycle/boundary state sufficient to interpret the object.

When the Kernel changes any of these relationships, the boundary record updates automatically as part of the authoritative change. It should not depend on an agent remembering to maintain metadata.

`created by` is provenance and is not necessarily the same as current governing authority. Project association is organizational metadata and does not itself create authority or containment.

The boundary record exists so a restarted engine can discover a sealed durable object and understand what it is without first executing or trusting its interior.

## E. Currentness and recovery

The boundary record assists recovery but cannot, by itself, prove that its own authority relationships are current.

A stale but authentic Work Unit image can carry an equally stale but authentic boundary record. Therefore the current Kernel-0 recovery limitation applies here as a **candidate general principle**:

> **A state wholly contained within a rollback domain cannot, using only information rolled back with it, establish that it is the current state of that domain.**

This principle has direct bounded evidence from Kernel-0 recovery work but is recorded here as a potentially broader generalization rather than an unqualified universal theorem.

Accordingly, recovery distinguishes:

```text
intrinsic boundary record
    identifies/interprets the Work Unit and its last recorded relationships

trusted currentness / authority evidence
    determines whether those relationships may be treated as current
```

If the engine crashes or is not running, durable Work Units remain sealed bounded objects. **Sealed does not imply computationally frozen**: internal activity may continue using already-granted resources whose own realization and validity survive the engine loss, but engine-dependent outward capability attachments cannot be exercised while their mediation relationship is unavailable. A later compatible engine instance may recover the Work Unit only by establishing the authority required to mediate those objects under the declared currentness/failure model. The process instance that originally created a Work Unit has no permanent special privilege merely because it was the creator.

If the Work Unit is found but current governing authority cannot be established, it remains sealed rather than becoming unbounded or automatically regaining outward capabilities.

Full historical event replay is not intrinsically required. Recovery requires a trustworthy current authoritative cut, or sufficient surviving information to reconstruct an observationally equivalent current state under the declared failure assumptions.

## F. Engine restart

The execution-engine process is disposable relative to durable Work Units.

On restart, the safe conceptual sequence is:

1. establish the engine's current authority to mediate Work Units;
2. discover durable Work Unit objects and their intrinsic boundary records;
3. reconstruct the containment topology and last-recorded grants without activating them;
4. validate current authority/currentness under the declared recovery boundary;
5. register valid Work Units with the Kernel in a sealed/inactive state;
6. reconstruct only those attachments and grants that are currently authorized;
7. resume execution only through explicit authorized relationships.

Transient sockets, model sessions, shell processes, network connections, and similar realizations do not need to survive merely because the durable attachment relationship may be recoverable.

## G. Containment and nested Work Units

A Work Unit may be contained within another Work Unit.

```text
W_outer
└── W_inner
```

A nested Work Unit remains a Work Unit even when it has no resources, attachments, files, or active execution. It is then subject to both its own boundary and every containing boundary above it.

Containment does **not** grant automatic inheritance. A child receives no resource, capability, attachment, or authority merely because its parent has it.

A nested Work Unit cannot exceed the effective capabilities permitted by its containment chain. Conceptually:

```text
effective(child) ⊆ effective(parent containment)
```

For quantities, a child's usable allocation cannot exceed what the containing relationship can supply. For capabilities, absence or restriction at an outer boundary cannot be bypassed by an inner grant.

Therefore:

```text
parent has network
    does NOT imply child has network

parent lacks network
    implies child cannot obtain effective external network access through that containment
```

Containment and management authority are distinct relationships. Code executing inside a parent Work Unit does not automatically gain administrative control over a child merely because the child is contained there.

An authority able to govern an outer Work Unit may also, where authorized by the Kernel's authority structure, act directly on descendants without destroying the containing Work Unit.

## H. Revocation, sealing, and descendant effects

Revocation or cessation of execution must not weaken containment.

When a Work Unit loses the authority necessary for continued external effects, its durable contents remain bounded. Conceptually it becomes **sealed**: it still exists, but its active external relationships cannot be exercised except as separately authorized by the Kernel.

If an outer Work Unit is revoked/sealed, contained Work Units cannot continue exercising effective capabilities through the outer boundary. This may effectively seal descendants without requiring their durable contents to be deleted.

Conversely, a nested Work Unit may be independently revoked without revoking or destroying its ancestors.

The words `sealed`, `revoked`, and `destroyed` describe different facts:

- **sealed**: the durable bounded object remains and engine-dependent outward capability use is disabled; internal computation may continue within already-granted resources unless separately paused, terminated, or deprived of those resources;
- **revoked**: some governing authority or grant has been withdrawn; the Work Unit remains bounded and may thereby become sealed from affected outward capabilities;
- **destroyed**: the Work Unit itself ceases to exist only after its contents have been safely dispositioned.

Exact implementation state names may differ. The semantic distinctions must remain.

## I. Work products, export, and destruction

Completion of work does not imply publication or escape from containment.

A file produced inside a Work Unit remains inside that bounded object until a Kernel-authorized transfer or attachment exposes it elsewhere. Calling something an `output` does not make it safe or unbounded.

A Work Unit may be destroyed only after every durable thing whose containment depends on that Work Unit has been explicitly dispositioned.

Before the Work Unit boundary can cease to exist, each contained durable object must be either:

1. **transferred/reparented** to another valid bounded destination through an authorized whole transition; or
2. **deleted/disposed of** according to the declared storage guarantee.

External resources that were merely granted to the Work Unit need not themselves be destroyed; the grant relationship is revoked. Owned files and nested Work Units may not silently fall into a general host namespace.

Conceptually:

```text
Active W
  ↓
Seal W
  ↓
revoke/disable outward capability attachments
  │
  └── internal computation may continue within surviving resource grants
  ↓
disposition owned durable contents
    ├── transfer/reparent to another bounded destination
    └── delete/dispose
  ↓
disposition nested Work Units
    ├── transfer/reparent
    └── recursively destroy
  ↓
remove Work Unit boundary/envelope
  ↓
Destroyed
```

Hard destruction precondition:

> **A Work Unit may cease to exist only when no remaining bounded object would experience weaker containment because that Work Unit disappeared.**

If destruction is interrupted, the remaining object must recover to a still-bounded sealed state. Partial destruction must never expose previously confined contents.

`Delete` initially means logical disposal within the declared persistence/storage boundary. Secure physical erasure from snapshots, backups, SSD cells, remapped sectors, or hostile storage media is a stronger optional guarantee and is not implied by ordinary Work Unit destruction.

## J. Reparenting and transfer

Reparenting is allowed in principle through a Kernel-authorized whole transition.

A sealed child Work Unit may move from one containment boundary to another:

```text
W1                 W3
└── W2 [sealed]    │
        ────────>  └── W2 [sealed]
```

The move cannot accidentally widen the child's effective authority. The destination containment must support every grant retained by the child, or those grants must be reduced/revoked as part of the same authorized transition.

A reparented Work Unit may subsequently be reactivated with a different set of granted resources and attached capabilities appropriate to its new containment. Reparenting therefore does not imply automatic preservation of old attachments.

Authority transfer, delegation, and revocation remain distinct operations:

- **delegation** may grant bounded authority while the delegator retains authority;
- **transfer** moves authority such that the transferred authority is no longer usable through the old observation/evidence;
- **revocation** removes authority without necessarily granting it elsewhere.

These transitions use the Kernel's guarded whole-commitment/current-authority semantics rather than trusting assertions from inside the Work Unit.

## K. Minimal Work Unit invariants

The current model should preserve at least these properties:

1. An empty Work Unit is still a valid Work Unit.
2. A Work Unit remains valid with no active execution and no attachments.
3. No actionable relationship crosses a Work Unit boundary unless the Kernel authorizes it.
4. Resources and attachments are both grants; attachments are the internally exposed subset.
5. Removing an attachment removes that internally available avenue of external influence.
6. Execution is activity inside the Work Unit, not currently a separate primitive.
7. Loss of agents, streams, tools, processes, or engine instances does not implicitly destroy the Work Unit or release its contents.
8. The intrinsic boundary record is Kernel-maintained and is not ordinary Work Unit content.
9. Boundary metadata aids recovery but cannot certify its own freshness against rollback.
10. Nested Work Units inherit nothing automatically.
11. A child's effective capabilities cannot exceed those permitted by its complete containment chain.
12. Containment does not itself grant code in the parent administrative authority over the child.
13. Revoking/sealing a parent prevents descendants from exercising authority through the revoked outer boundary.
14. A descendant may be revoked independently without revoking its ancestors.
15. Completion does not imply export.
16. Revocation or sealing does not imply deletion or unsealing of contents.
17. Destruction cannot weaken the containment of any surviving content.
18. Interrupted destruction recovers to a bounded/sealed condition.
19. Reparenting is an explicit Kernel transition and cannot silently widen authority.
20. The Work Unit's live realizations may be disposable; its bounded identity, required contents, and authoritative boundary relationships follow the declared durability/recovery model.

## L. Current build boundary

This update deliberately makes the Work Unit smaller than the earlier component design.

The following are **not intrinsic to Work Unit-0 merely because they are useful**:

- agents or model identities;
- durable `Execution` objects;
- executor roles such as Builder or Reviewer;
- generated tool guides;
- context construction or summarization;
- metrics and accounting;
- issue tracking;
- reasoning/evidence semantics;
- Git/worktrees;
- project-wide scheduling or queues;
- Observer, Processor, or Orchestrator internals;
- a container/VM implementation;
- a resident process per Work Unit.

Higher layers may use the boundary record, stable Work Unit identity, grants, attachments, contents, and containment topology to provide those features.

The first implementation should therefore test the bounded-object semantics directly: confinement, grants/attachments, nesting/attenuation, sealed durability, recovery, reparenting, destruction without escape, and replacement/loss of transient execution relationships. It should not rebuild the larger historical feature set merely because that set was previously proposed.

---

# Historical Design and Reasoning Record — 2026-09-13

The material below is the previous canonical component design **preserved in full** as reasoning provenance. It records why the project originally introduced Attachment Points as durable executor-facing positions, Executions as disposable runtime objects, context/tool presentation, metrics, and related mechanisms.

Where this historical record conflicts with Sections A–L above, Sections A–L are canonical. Compatible motivations, constraints, failure cases, performance concerns, and subsystem boundaries remain useful evidence for later design work.

# EDASES Work Unit — Component Design

**Status:** Design specification  
**Purpose:** Define the Work Unit as a generic durable execution primitive suitable for implementation planning.  
**Scope:** Work Unit substrate, Attachment Points, Executions, capability/resource boundaries, persistence, recovery, context/tool presentation, resource accounting, and subsystem interfaces.  
**Out of scope:** Detailed implementation plan, database schemas, kernel API syntax, scheduling algorithms, reasoning methodology, issue-tracker schema, Observer implementation, Processor implementation, and Orchestrator implementation.

## 1. Summary

A **Work Unit** is a lightweight, durable, kernel-governed environment in which one or more disposable execution agents can perform work.

Its fundamental purpose is to separate **the durable work** from **the temporary executor performing it**.

The Work Unit is intended to replace fragile arrangements such as opening a new `tmux` pane for an agent, creating an ad hoc Git worktree, relying on an agent session to remember its permissions and context, or losing execution continuity when a connection, model session, or process disappears.

A Work Unit persists independently of any agent attached to it.

Agents execute through durable **Attachment Points**. An Attachment Point defines the resources, capabilities, context, and tools available to an executor occupying that position.

Actual model/process instances are **Executions**. Executions are deliberately disposable.

```text
Work Unit
    └── Attachment Point
            └── Execution
```

A Work Unit may have one or many Attachment Points; one executor over its lifetime, many sequential executors, many concurrent executors, or no currently active executor. The underlying Work Unit must remain valid in all of these cases.

The Work Unit is **methodology-neutral**. It must remain useful for users who do not use an issue tracker, do not record reasoning, never use more than one agent at a time, do not use EDASES methodology, or are not doing software development at all. It should work equally for software, research, finance, accounting, marketing, art, documentation, data work, or other computer-mediated projects.

EDASES-specific concepts such as reasoning records, evidence relationships, issue links, review methodology, or project-specific workflows may reference Work Units but do not define them.

## 2. Core Design Principle

> **Persist the work, not the worker.**

The executor is temporary. The work environment, relevant durable state, permissions, resources, and continuity exist independently of the model or process performing the work.

Therefore executor disappearance must not imply work disappearance, and executor replacement must not imply a new piece of work.

A replacement executor should be able to occupy the same Attachment Point and continue the existing work without reconstructing the entire task manually.

## 3. Motivation

Current agent workflows commonly couple several logically different things:

```text
agent session
+ shell/process
+ permissions
+ context
+ worktree
+ task ownership
+ tool access
```

This creates unnecessary fragility. If the session dies, the system may need to determine what the agent was doing, where its files are, which permissions it had, which tools it was supposed to use, what context it had received, whether the work is still valid, whether another agent can safely continue, and which state is authoritative.

Existing systems often compensate through handoff prompts, supervisors, agent-to-agent messaging, orchestration loops, session reconstruction, role-specific agents, extensive project documentation, polling, watchdogs, and worktree bookkeeping.

The Work Unit aims to move as much of this as possible into a small deterministic substrate.

## 4. Design Goals

The Work Unit should provide:

1. **Durability** — work survives executor/session/process failure.
2. **Recoverability** — a replacement executor can continue work from durable state.
3. **Executor independence** — work identity is not tied to a specific model, agent implementation, provider, or session.
4. **Lightweight operation** — an inactive Work Unit should consume almost no runtime resources.
5. **Bounded authority** — executors receive only explicitly granted capabilities.
6. **Minimal context** — executors receive only the information needed for their role and task.
7. **Minimal tool surface** — tools are deny-by-default and exposed only when useful.
8. **Flexible resource topology** — executors may share resources or work in isolated resource views.
9. **Single-, sequential-, and multi-agent support** — these should be configurations of the same primitive, not separate architectural modes.
10. **Model replacement** — switching models should be cheap and should not reset the logical work.
11. **Role reconfiguration** — permissions or resource access can be changed without recreating the Work Unit.
12. **Resource accounting** — runtime and inference costs should be attributable to the work being performed.
13. **Methodology neutrality** — EDASES concepts can attach to the primitive without being required by it.
14. **Agent usefulness** — restriction should reduce irrelevant choices and reconnaissance rather than merely limit the model.

## 5. Non-Goals

The Work Unit is not inherently an issue, project-management task, reasoning record, prompt, conversation, agent memory system, workflow, DAG, queue, orchestrator, supervisor, scheduler, Observer, Processor, evidence model, Git abstraction, model router, agent role hierarchy, or multi-agent framework.

Any of these systems may interact with Work Units. None is required to define what a Work Unit is.

## 6. Architectural Position

```text
                    Human / Project Policy
                             │
                             ▼
                       Orchestrator
                    reasoning / choices
                             │
                             ▼
                         Kernel
              authority / state / enforcement
                             │
                             ▼
                        Work Unit
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
          Attachment Point      Attachment Point
                  │                     │
                  ▼                     ▼
             Execution             Execution
                  │                     │
                  ▼                     ▼
           model / process        model / process
```

Other components operate alongside this:

- **Observer:** observes factual runtime/project state.
- **Processor:** performs deterministic computation.
- **Tracker databases:** retain durable project/work facts.
- **Reasoning databases:** optionally retain reusable reasoning.
- **Metrics:** retain unavoidable runtime/inference measurements.

The Work Unit should not absorb responsibilities belonging to these systems merely because they interact with it.

## 7. Work Unit as a Microkernel-Style Execution Domain

The conceptual inspiration is closer to an operating-system protection domain than to an agent session.

A Work Unit owns or references durable identity, durable state, resources, capability boundaries, and Attachment Points. Executions operate **inside** those boundaries.

```text
Work Unit
├── identity
├── lifecycle
├── resources
├── capability envelope
├── attachment points
└── runtime accounting
```

Executions do not define the Work Unit. They temporarily consume its capabilities and resources.

## 8. Fundamental Invariants

### 8.1 Work Unit identity survives executor loss

Destroying an Execution must not imply destroying the Work Unit.

### 8.2 Attachment Point identity survives executor loss

An Attachment Point represents durable continuity within a Work Unit. If its executor dies, the Attachment Point remains and another Execution can attach.

### 8.3 Important state must not exist only inside an executor

If state is required for continuation, permissions, resource ownership, task understanding, correctness, or recovery, relying exclusively on an LLM context window or process memory is insufficient.

### 8.4 Authority is external to the model

The executor may request an action. The substrate determines whether it is allowed. Prompt instructions are not an authority boundary.

### 8.5 Tools are deny-by-default

Unavailable tools should ideally be uncallable, undocumented, and absent from the agent-facing interface.

### 8.6 Context is minimized by default

Project knowledge being available somewhere does not imply it belongs in every executor context.

### 8.7 Resource ownership follows work

Where practical, resources and resource consumption should be attributable to a Work Unit rather than merely to temporary OS processes.

### 8.8 Multi-agent operation is not a special execution mode

The same Work Unit abstraction supports one Execution or several concurrent Executions without requiring a fundamentally different substrate.

## 9. Core Object Model

### 9.1 Work Unit

The durable identity of a bounded piece of computational work.

```text
WorkUnit {
    id
    lifecycle_state
    base_capability_policy
    resources
    attachment_points
}
```

This is illustrative rather than a final schema. The Work Unit should contain only mechanically necessary execution state.

### 9.2 Attachment Point

A durable execution position inside a Work Unit.

```text
AttachmentPoint {
    id
    work_unit_id
    capability_policy
    resource_view
    context_state
    tool_set
    current_execution?
}
```

An Attachment Point defines what an executor can access, what it can do, which tools it sees, which durable context belongs to this line of work, which resources are visible, and where a replacement executor resumes.

An Attachment Point may correspond to a conceptual role such as Builder, Reviewer, Researcher, Analyst, or Auditor, but those roles are **not kernel primitives**. They are reusable configurations.

### 9.3 Execution

A temporary runtime instance attached to an Attachment Point.

```text
Execution {
    id
    attachment_point_id
    executor
    model
    runtime_state
    metrics
}
```

An Execution may represent a remote LLM API session, Codex worker, local process, other agent runtime, deterministic worker, or potentially a human-driven execution interface. Executions are disposable.

## 10. Why Attachment Points Exist

A direct `Work Unit → Agent` relationship conflates permissions, model identity, role, resource view, context continuity, and session lifetime.

The Attachment Point separates these. It is the durable location at which an executor performs a particular part of the work.

Useful metaphor:

```text
Work Unit        = workshop
Attachment Point = workbench
Execution        = worker currently at the bench
Capabilities     = permitted tools/actions
Resources        = materials available at the bench
Durable context  = notes left at the bench
```

A worker may leave without dismantling the workshop or bench.

## 11. Executor Replacement

Executor replacement should be ordinary.

```text
Work Unit W17
Attachment Point A3
Execution E7 / Model X
```

If E7 fails or Model X proves unsuitable:

```text
E7 terminates
A3 remains
E8 / Model Y attaches to A3
```

The new executor inherits the appropriate capability policy, resource view, durable context, tool surface, and work state.

Model replacement and agent replacement are therefore conceptually the same operation. The system should not require a separate handoff architecture merely because the executor changed.

## 12. Concurrent Executors

A Work Unit may have multiple Attachment Points active simultaneously:

```text
WU
├── AP1 → E1
├── AP2 → E2
└── AP3 → E3
```

Examples include parallel research, competing implementations, builder + reviewer, specialist agents, or independent adversarial analysis.

Concurrency introduces ordinary shared-state issues where resources overlap, but should not require a separate concept of an "agent team" at the kernel level.

## 13. Sequential Executors

A single Attachment Point may host many Executions over time:

```text
AP1
├── E1 ended
├── E2 ended
├── E3 failed
└── E4 active
```

This supports context-window exhaustion, model changes, provider failure, process crashes, deliberate replacement, escalation from a cheaper to a stronger model, or switching to a specialist.

## 14. Resource Views

### 14.1 Shared resources

Useful for collaborative research or shared analysis:

```text
WU
└── shared/
    ├── AP1
    ├── AP2
    └── AP3
```

### 14.2 Isolated resources

Useful for independent implementations:

```text
WU
├── workspace-A/ → AP1
├── workspace-B/ → AP2
└── workspace-C/ → AP3
```

This can produce behavior analogous to current Kickoff or independent-worktree systems without requiring a special Kickoff primitive.

### 14.3 Hybrid resources

```text
WU
├── shared-research/
├── shared-requirements/
├── implementation-A/
├── implementation-B/
└── review/
```

Example policy:

```text
AP-builder-A
    read shared
    write implementation-A

AP-builder-B
    read shared
    write implementation-B

AP-reviewer
    read all implementations
    write review
```

This topology is configuration rather than a special orchestration framework.

## 15. Capability Model

Capabilities are deny-by-default. An executor receives only what its Attachment Point permits.

Conceptually:

```text
effective authority
=
Work Unit maximum authority
constrained by
Attachment Point policy
constrained by
Execution-specific limits
```

Exact composition semantics remain an implementation decision.

Possible capabilities include reading or writing resources, executing commands, running tests, searching a workspace, network access, external-service access, modifying repositories, launching subprocesses, creating another execution, requesting additional capability, messaging the Orchestrator, deploying, merging, or accessing secrets.

The system should avoid creating an unnecessarily elaborate capability taxonomy before use cases require it.

## 16. Capability Profiles

Conceptual roles should be expressible as reusable capability/resource profiles rather than hardcoded kernel roles.

```text
Builder Profile
    read project subset
    write assigned workspace
    run tests
    inspect diff
    message Orchestrator
```

```text
Reviewer Profile
    read implementation
    run tests
    write review result
    no implementation writes
    message Orchestrator
```

Another project might define Analyst, Auditor, Approver, Designer, or Researcher. The kernel should not need to understand these names.

## 17. Dynamic Permission Changes

Attachment Point permissions should be adjustable during work without recreating the Work Unit, creating a new task, recreating the workspace, or discarding context.

Whether changes affect active Executions immediately or require reattachment remains an implementation question.

## 18. Escalation

Minimal capability sets require an escape path. Every general-purpose executor should normally have access to a narrow escalation mechanism such as `message_orchestrator`.

An executor can report missing permission, resource, information, unsuitable tool, blocked state, or uncertainty requiring external judgment.

The Orchestrator can then grant access, deny access, provide information, alter the Attachment Point, create another Work Unit, assign a specialist, or ask the human operator.

This allows conservative initial permissions without turning boundedness into deadlock.

## 19. Agent-Facing Environment

The agent should experience the Work Unit as a prepared workshop.

A generic Builder should not receive an enormous harness manual. The model-facing packet should be approximately:

1. What are we working on?
2. Which resources/files are available?
3. How should work be performed in this project?
4. Which tools are available?
5. What relevant work has already happened?
6. How do I escalate if something necessary is unavailable?

The interface should reduce irrelevant decision-making.

## 20. Tool Exposure

Tools are exposed dynamically according to granted capabilities.

If a tool is not approved, it is not callable; ideally it is not visible; and its documentation is not included.

```text
capability granted
→ tool exposed
→ documentation supplied
```

```text
capability absent
→ tool absent
→ documentation absent
```

This avoids giving models a large generic tool menu and asking them repeatedly to reason about which tools matter.

## 21. Dynamic Tool-Use Guide

Every fresh executor should receive a tool-use guide generated from the exact tool set approved for its Attachment Point.

For each tool, provide only enough documentation to use it correctly: purpose, call shape, outputs, and minimal example where useful.

The guide should avoid tools that are not available, unrelated subsystem descriptions, extensive conceptual documentation, and unnecessary edge cases unless required for correct use.

## 22. Project Working Guide

A project may provide a concise working-method document.

For EDASES/ASES, a Builder should normally receive a short document covering what the project is, how builders should work, how work should be documented, important project invariants, how completion is reported, and when to escalate.

This is preferable to automatically injecting many foundation/architecture documents.

Detailed project documents remain available for deliberate retrieval when needed.

> **Available knowledge is not automatically required context.**

## 23. Context Layers

### Work Unit context
Information common to the work: overall objective, shared requirements, shared source materials.

### Attachment Point context
Information specific to this line of work: specialist focus, prior executor findings, current local progress, role-specific instructions.

### Execution context
The temporary model-specific rendering supplied to the current executor. This may be regenerated whenever an executor attaches.

## 24. Context Continuity

The system should preserve **durable sources of context**, not attempt to preserve the hidden cognitive state of a model.

A replacement executor should be reconstructible from:

```text
Work Unit state
+ Attachment Point state
+ durable outputs
+ relevant project knowledge
+ previous execution summaries/results
```

The exact context-building mechanism belongs primarily to the Processor/context-construction layer rather than the Work Unit itself.

## 25. Context Minimization

The ideal fresh executor receives the minimum sufficient context needed to work effectively. This reduces token/inference cost and unnecessary exploration.

Agents should not automatically receive unrelated project history, irrelevant architecture, unused tools, unrelated files, other agents' work, or infrastructure details.

Additional information should be retrieved or requested when demonstrated need appears.

## 26. Resource Limits

Work Units should support bounded resource use. Potential limits include memory, CPU, disk, subprocess count, filesystem scope, network access, local runtime duration, inference/token budget, and external API budget.

The exact enforcement mechanisms remain to be designed.

> Resource limits should belong to durable work, not merely to transient process identity.

This allows a replacement executor to remain within the same resource envelope automatically.

## 27. Relationship to System Resource Management

The Work Unit provides resource ownership and policy. Other subsystems may observe or react to resource conditions.

```text
Observer:
    detects memory pressure

Kernel:
    knows resource ownership and hard limits

Orchestrator:
    decides among ambiguous trade-offs

Possible result:
    pause Execution A
    terminate Execution B
    defer Processor job
    reroute execution
    ask operator
```

Hard deterministic limits may be enforced without Orchestrator reasoning.

## 28. Efficiency Requirements

Efficiency is a core architectural constraint, not an optimization to add later.

A Work Unit should be at least as lightweight conceptually as opening a new `tmux` pane and worktree, while offering substantially stronger durability and control. Ideally it should be lighter.

An inactive Work Unit should require approximately small durable database records plus filesystem metadata and optional workspace resources.

It should not require a permanent process, dedicated daemon, database server, VM, container runtime, scheduler instance, or resident model session.

An inactive Attachment Point should similarly be little more than durable state.

## 29. Scaling Principle

> **Local resource consumption should scale with actual local execution, not with the number of logical Work Units or agents represented.**

A small machine might hold 100 Work Units and 250 Attachment Points while only 3 Executions are active. The first two numbers should have very little effect on CPU/RAM.

This is especially important for inexpensive VPSs, laptops, low-power machines, phones, and edge systems. Heavy inference usually occurs remotely and should not require a heavy local coordination substrate.

## 30. Metrics Are Core Runtime Facts

Metrics are not an optional methodology feature. LLM execution necessarily produces resource usage that should be accounted for where available.

Possible measurements include wall time, active execution time, model calls, input tokens, output tokens, cached tokens, uncached tokens, estimated monetary cost, tool calls, retries, executor replacements, local CPU, local memory, disk use, and network use.

Metrics may be exact, estimated, or unavailable depending on provider/runtime. That provenance should be representable.

## 31. Metrics Hierarchy

Measurements should naturally aggregate:

```text
model/API call
    ↓
Execution
    ↓
Attachment Point
    ↓
Work Unit
    ↓
project
```

Higher-level EDASES systems may additionally relate costs to reasoning, issues, experiments, reviews, or project goals. Those semantic relationships are outside the Work Unit core.

## 32. Work Tracking

A work-tracking system is strongly encouraged but not mandatory for using Work Units.

Tracking what is being done, what was already done, what remains, what failed, and what was abandoned can prevent substantial repeated inference and project reconstruction.

The default user experience should therefore make lightweight work tracking easy and attractive.

However, a Work Unit must not require an Issue or tracked task. A user may create one manually and use it simply as a durable execution environment.

## 33. Reasoning

Reasoning is important to EDASES but does not belong inside the generic Work Unit schema.

Reasoning may reference Work Units, for example:

```text
Reasoning R17 influences W4
W8 tests R17
Evidence from W8 updates R17
```

But the Work Unit need not understand what "reasoning," "supports," "tests," or "supersedes" mean.

A separate lightweight reasoning database is acceptable and likely desirable.

## 34. Other Optional Semantic Systems

The same principle applies to issue tracking, evidence/provenance, review methodology, project-specific workflows, architectural decisions, and experiments.

These systems may reference stable Work Unit IDs. They should not be prerequisites for Work Unit operation.

## 35. Multiple Databases

The architecture may use multiple lightweight databases. This is not considered problematic.

SQLite makes specialized durable stores cheap to create and operate.

Possible separation:

```text
kernel/work-unit database
work-tracking database
reasoning database
evidence database
other project-specific stores
```

The exact physical split is not yet specified. Metrics remain a core runtime concern even if physically stored separately.

## 36. Lifecycle

The exact Work Unit state machine remains open and should remain small.

Possible conceptual states might include `created`, `active`, `paused`, `completed`, and `aborted`, but these are not final.

Attachment Points and Executions may require independent lifecycle states.

The kernel should own legal transitions. Agents should not establish authoritative lifecycle state merely by assertion.

## 37. Execution Failure
