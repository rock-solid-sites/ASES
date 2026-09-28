---
title: EDASES Authority Ontology
program: EDASES
layer: Architecture
document_type: Ontology
status: Draft
authority: Derived
canonical_repository: edases

depends_on:
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
  - EDASES Work Unit Component Design
  - EDASES Currentness and Recovery Assurance
  - EDASES Phase I Core Substrate Closure

consumed_by:
  - Phase I formalization
  - Phase I realization
  - Work Unit Formal Specification
  - Future Orchestrator design
  - Future Observer design
  - Future Processor design

related_documents:
  - Concepts and Topics Registry
  - EDASES Execution Engine Roadmap
  - Phase-I Processorless Falsification
  - Phase-I Verification
  - Agent Orchestration Playbook
  - OpenCode orchestrator guard
  - Crosslink guard
  - RTK guard

implements: []
implemented_by: []
supersedes: []
superseded_by: []

last_updated: 2026-09-28
---

# EDASES Authority Ontology

## 1. Status and purpose

This document is a **working authority ontology**, not a frozen implementation specification.

Its purpose is to make explicit how authority originates, is represented, delegated, narrowed, extended, exercised, revoked, expired, and recovered across EDASES. It exists to give later Kernel, Work Unit, Orchestrator, Observer, Processor, and realization work a common semantic base while those components are still being refined.

The document should constrain future reasoning where the distinction is already clear, but it must not turn implementation candidates such as leases, generations, fencing tokens, particular databases, process identities, or credential brokers into primitives without necessity evidence.

The central architectural distinction is:

> **The user is the root source of authority. The Kernel/execution engine represents, distributes, and enforces that authority. Other system roles receive only bounded derived authority or capabilities.**

This separates **who ultimately authorizes** from **what mechanism makes an authorization real**.

---

## 2. Core authority chain

Within the EDASES policy boundary, the **user/operator** is the root authority source.

The execution engine does not possess an independent sovereign authority. It is the trusted mechanism through which user-originating authority is represented in authoritative state, transformed into bounded grants, and enforced at protected boundaries.

The **Orchestrator Role** is the expected primary user-facing agent role in ordinary EDASES operation. It preserves the familiar LLM-chat interaction model: the user normally talks to an Orchestrator agent, which interprets intent, coordinates work, and exercises whatever authority the user has delegated to it.

The role is nevertheless not a root authority and is not required for Kernel correctness. An Orchestrator agent may be granted extremely narrow authority, broad operational authority, or effectively all authority the user chooses to delegate, and that delegation may be widened, narrowed, suspended, replaced, or revoked at any time. The system remains coherent in principle if the user controls it directly with no LLM occupying the Orchestrator Role, but direct low-level control is a fallback capability rather than the intended normal UX.

The Orchestrator Role is therefore best understood as a **user-facing semantic role plus a capability/authority package**. Being called the Orchestrator creates no authority by itself.

A Work Unit is a bounded Kernel-governed object that may receive resources and capability attachments.

Execution is activity inside a Work Unit. Execution has no authority merely by existing, by naming a role, by asserting an identity, or by producing a model decision.

Conceptually:

```text
USER / OPERATOR
root authority and intent
        |
        v
KERNEL / EXECUTION ENGINE
authoritative representation, mediation, enforcement
        |
        +---- bounded management/selection authority ---> ORCHESTRATOR
        |
        +---- resource grants ---------------------------> WORK UNIT
        |
        +---- capability attachments --------------------> WORK UNIT
                                                            |
                                                            v
                                                        EXECUTION
                                                  may exercise only the
                                                  currently attached surface
```

The intended operating model is normally:

```text
USER
  ↕
ORCHESTRATOR AGENT
  ↕
KERNEL / EXECUTION ENGINE
  ↕
WORK UNITS / CAPABILITY ATTACHMENTS / OTHER AGENTS
```

The authority direction is different from the conversational direction: authority originates with the user and is delegated downward through Kernel-enforced grants. The user may instead interact directly through an engine interface or another authorized control surface. This architectural fallback prevents the Orchestrator agent from becoming a correctness dependency without making direct low-level control the primary product design.

---

## 3. Authority, intent, judgment, and enforcement are different things

EDASES must keep four concepts separate.

### 3.1 User intent

**Intent** is what the user wants the system to accomplish or avoid.

Intent may be broad, semantic, incomplete, or expressed conversationally. It guides Orchestrator reasoning, but intent by itself is not necessarily a mechanically exercisable permission.

### 3.2 Authorization

An **authorization** is a user-originating or validly delegated decision that permits a bounded change in authority, state, or capability.

Examples include:

- allowing a particular model to be launched;
- granting network access to one Work Unit;
- allowing a Work Unit to write to one repository;
- permitting the Orchestrator to select among a bounded set of cheap models;
- authorizing a resource allocation;
- revoking a previously granted capability.

### 3.3 Semantic judgment

A model, human Orchestrator, deterministic rule, or other reasoner may conclude that an action is desirable, necessary, safe, or consistent with the user's goal.

That conclusion is **not authority merely because it is correct**.

An Orchestrator may decide:

> "This work should use model X."

That does not imply:

> "The Orchestrator is authorized to instantiate model X."

The second claim depends on current delegated authority.

### 3.4 Enforcement

The Kernel/execution engine is responsible for making protected effects conform to current authority.

A prompt saying "do not write" is not enforcement.

A role label saying "reviewer" is not enforcement.

A permission record saying "deny" is insufficient if an unmediated effect path still exists.

For a protected effect, the required property is:

> **If current authority does not permit the effect, the effect cannot occur through any in-scope path.**

The OpenCode and Crosslink guards are relevant empirical motivation: role restrictions currently require multiple overlapping hooks and command-path checks because policy declarations alone do not completely mediate effects.

---

## 4. Root authority and the engine

### 4.1 The user is the root authority source

Within EDASES, the user's authority is not derived from an agent, Work Unit, Orchestrator, engine process, or historical record.

The user may create, widen, narrow, revoke, or replace delegated authority subject only to constraints outside the EDASES policy boundary.

This does not require the user to perform execution personally. The design goal is the opposite: the user should normally express goals, approvals, constraints, and corrections while bounded agents perform execution.

### 4.2 The engine is an authority mechanism, not an authority owner

The execution engine is how user authority becomes mechanically meaningful.

It maintains or accesses the authoritative state needed to answer questions such as:

- which grant is current;
- which capability is active;
- what Work Unit a grant applies to;
- whether an Orchestrator choice falls within its delegated envelope;
- whether a protected transition is admissible;
- whether a stale actor or process may still exercise an old grant.

Engine **process identity** is not permanent ownership.

A restarted engine process does not receive authority from the process that died. It resumes the same user-controlled mediation role only after the system establishes that it is operating from a trustworthy current authoritative view and that stale mediator instances cannot continue producing conflicting protected effects.

Thus:

> **Engine restart is primarily a currentness and mediation problem, not a transfer of sovereignty between engines.**

---

## 5. Grants

A **Grant** is the current working term for a Kernel-authorized bounded relationship.

A grant must carry enough semantic information to determine, without relying on a model's assertion:

- what object or relationship is authorized;
- to what Work Unit, role, or management scope it applies;
- what operations or effects it permits;
- what restrictions bound it;
- what authority allowed it to be created or changed;
- whether it is current;
- any validity condition material to its use, such as expiry or required mediation.

This is a semantic requirement, not a commitment to a particular schema.

A grant is current authority only while its declared validity conditions hold.

Historical evidence that a grant once existed is not current authority.

---

## 6. Three important grant classes

The ontology currently needs at least three conceptually different kinds of granted relationship.

### 6.1 Resource grants

A **resource** supports, bounds, or supplies a Work Unit but is not directly callable across the Work Unit boundary merely because the grant exists.

Examples may include:

- CPU capacity;
- memory capacity;
- local storage capacity;
- other substrate allocations.

A resource grant can survive loss of the engine process if the underlying resource allocation survives and the grant itself has not expired or been revoked.

Engine death does **not** inherently revoke computation.

This resolves the Phase I Q1 ambiguity:

> **A sealed Work Unit need not be computationally inert. Internal computation may continue using already-granted resources after engine loss.**

### 6.2 Capability attachments

An **attachment** is a Kernel-granted relationship exposed across the Work Unit boundary so activity inside the Work Unit can act through it.

Examples may include:

- network access;
- credential access;
- external service access;
- repository write access;
- filesystem views;
- tool invocation surfaces;
- model/provider connections;
- other interfaces capable of producing protected effects.

Capability attachments are:

- explicit;
- bounded;
- revocable;
- normally validity-limited;
- dependent on a currently valid engine-mediated authorization relationship.

Unlike ordinary resource grants, capability attachments must fail closed when the engine is no longer able to mediate them.

Therefore:

> **Engine loss deactivates capability attachments but does not inherently stop internal computation.**

This must be true at the effect boundary, not merely in metadata. A raw socket, reusable credential, host handle, or other retained path must not allow execution to continue exercising a capability after the attachment is no longer current.

This requirement does not imply a particular lease, token, fencing, proxy, broker, or kernel mechanism. Those remain realization candidates.

### 6.3 Management or delegation authority

Some authority permits changing other grants rather than directly exercising an external tool.

The Orchestrator Role is the primary expected example. Its authority envelope is not fixed by the role: it contains exactly the management, selection, and other capabilities that the user currently grants to the agent occupying it.

An Orchestrator may therefore be delegated authority to:

- create or propose Work Units;
- choose among permitted models;
- assign work;
- request or approve capabilities within a bounded envelope;
- narrow or revoke subordinate authority;
- route work;
- escalate decisions to the user.

This is distinct from direct data-plane capability.

No arbitrary shell, filesystem, network, credential, or external-service access follows merely from occupying the Orchestrator Role. Those powers may be granted when the user wants them, including very broad grants, but they must be explicit current authority rather than ambient consequences of being the primary chat agent.

Conceptually:

```text
Orchestrator judgment:
    "Builder needs repository write access"

        |
        v

management proposal / delegated decision

        |
        v

Kernel checks current management authority

        +---- permitted ---> create/widen bounded grant
        |
        +---- not permitted -> escalate to user
```

Whether "management authority" becomes a stable named primitive is still open. The distinction itself is required even if the implementation represents it using ordinary guarded grants.

---

## 7. Delegation and attenuation

Authority may be **derived** from existing authority only through a current authorized transition.

Derived authority must not exceed the authority from which it is validly delegated unless a higher authority explicitly widens it.

This gives the system an attenuation rule:

> **A delegate may exercise or further delegate only what its current authority permits.**

A child Work Unit receives no authority automatically merely because it is contained inside another Work Unit.

Containment and authority are separate relationships.

A nested Work Unit cannot exceed the effective restrictions of its full containment chain, but it may also be more restricted than its parent.

Similarly, a role name such as Builder, Reviewer, Auditor, or Orchestrator does not create authority. These are reusable profiles or semantic roles whose actual authority is determined by current grants.

---

## 8. Extending or widening authority

Authority must not widen accidentally.

Widening may occur only through an explicit current transition authorized by a principal with sufficient management authority.

Examples:

- the user directly grants network access;
- the user authorizes the Orchestrator to choose any model from a bounded set;
- the Orchestrator grants a Builder repository write access because that grant lies within its delegated envelope;
- a Work Unit is reparented and receives a newly authorized capability set.

The following must **not** widen authority by themselves:

- restart;
- recovery;
- model inference;
- historical configuration;
- role name;
- process identity;
- successful authentication without corresponding authorization;
- possession of stale credentials;
- being the creator of a Work Unit;
- prior approval whose scope or lifetime has ended.

If an Orchestrator concludes that broader authority is useful but lacks authority to grant it, the correct operation is escalation to the user.

---

## 9. Narrowing, revocation, and expiry

Authority may become invalid through explicit revocation, narrowing, expiry, containment change, failed validity conditions, or loss of required mediation.

Revocation is not merely a metadata update.

For a protected capability, once revocation is authoritative, future exercise through the revoked path must be prevented according to the declared effect boundary.

Revocation does not necessarily undo an external effect that was already validly authorized and accepted by an external sink. Cancellation, compensation, or exactly-once semantics require separate support and must not be inferred from revocation alone.

Narrowing should be representable independently from destruction. A Work Unit may remain alive and continue internal computation while losing one or more capability attachments.

---

## 10. The Orchestrator's authority

The Orchestrator is the expected primary conversational role through which most users will direct EDASES. It is a convenience layer for the user, not an independent authority source.

An agent occupying the Orchestrator Role has **exactly as much authority as the user currently grants it**. That may range from an advisory-only role to broad operational control. The user may change or revoke that authority at any time.

The Kernel does not require an Orchestrator agent for correctness. In principle the user can operate the system directly. This is an architectural property, not the design direction of the user experience: normal operation is expected to use an LLM agent as Orchestrator.

The Orchestrator Role itself is therefore a semantic role plus a capability package whose purpose includes preventing the primary conversational agent from exercising authority the user did not grant.

The Orchestrator may:

- interpret user intent;
- plan;
- select among choices already within its delegated authority;
- propose changes;
- delegate bounded work;
- reassess whether previous grants still match current intent;
- request additional authority;
- escalate unresolved or unauthorized choices to the user.

The Orchestrator must not gain authority merely from:

- a model output;
- a prompt instruction;
- a prior run;
- a role label;
- a historical grant;
- an unavailable user being assumed to agree.

In particular, model selection is bounded authority.

If the user has authorized:

```text
Luna Light -> Luna Medium on concrete capability failure
```

the Orchestrator may exercise that choice under the declared rule.

That does not authorize:

```text
launch any model the Orchestrator judges useful
```

unless the user explicitly delegated that broader choice.

The same principle applies to tools, credentials, network access, spending, external writes, deployment, and every other protected capability.

---

## 11. Work Unit authority and execution

A Work Unit is a bounded durable object. It may have:

- no execution;
- one or more active computations;
- resources;
- capability attachments;
- nested Work Units;
- accepted durable contents;
- private or candidate state.

Execution inside the Work Unit is not itself authority.

Internal computation may be arbitrary within the resource and confinement boundaries. What matters to the Kernel is whether activity can cross a protected boundary or change authoritative meaning.

Therefore:

> **Sealed does not mean frozen.**

A Work Unit may be sealed from protected external effects while computation continues internally.

Private or candidate state may evolve during this period unless a separate policy requires quiescence.

---

## 12. Crash and recovery semantics

Crash recovery must distinguish **remembering the previous configuration** from **restoring current authority**.

When the engine becomes unavailable:

1. durable Work Unit identity and bounded contents remain;
2. resource grants may continue where their own validity and underlying realization survive;
3. capability attachments become inactive because their engine-mediated authorization path is no longer live;
4. internal computation need not stop merely because the engine process stopped;
5. the boundary record preserves what capabilities were attached before the crash as historical recovery context.

The recorded last capability set is **not considered still valid authority** after recovery.

On recovery:

1. a current engine realization establishes a trustworthy current authoritative view under the declared recovery model;
2. the Work Unit is discovered in a sealed state;
3. its previous capability attachments are treated as historical candidates, not live permissions;
4. a currently authorized semantic decision-maker reassesses those previous capabilities against:
   - current user intent;
   - current user policy and standing grants;
   - current Work Unit purpose and state;
   - changed external conditions known to matter;
5. in the intended operating model, this decision-maker is the Orchestrator agent; if no Orchestrator agent is active, the user may perform the reassessment directly or may have explicitly authorized another policy/mechanism to make the bounded decision;
6. the decision-maker proposes reattachment, narrowing, replacement, or omission;
7. the Kernel permits only those fresh attachments that fall within current authority;
8. anything outside the decision-maker's delegated envelope is escalated to the user.

Conceptually:

```text
before crash:
    W
    resources: R
    attachments: A, B, C

engine loss:
    W survives
    R may continue
    A/B/C become inactive
    record remembers {A, B, C}

recovery:
    historical set {A, B, C}
            |
            v
    authorized reassessment
    (normally Orchestrator)
    against current user intent
            |
      +-----+-----+
      |     |     |
      v     v     v
      A'    omit B  C'
      |             |
      +------v------+
             Kernel
       current authority check
             |
             v
      fresh current attachments
```

This prevents a stale but authentic Work Unit image from silently resurrecting credentials, sockets, sessions, model approvals, or other capability authority.

Recovery therefore follows the rule:

> **Remember previous capability relationships for provenance and reconstruction, but never treat remembered capability state as current merely because it was current before the crash.**

---

## 13. Currentness and stale mediator instances

User root authority persists conceptually across engine process failure, but the ability to exercise it through the system depends on a trustworthy current mediator.

Two engine processes must not independently exercise conflicting versions of the same mediated authority.

The problem is not that they are competing sovereign authorities. They are competing realizations of one user-derived authority mechanism.

A realization must therefore ensure that once one process is established as the current mediator for a protected authority domain, stale process instances cannot continue producing protected effects for that same domain.

The exact mechanism remains open.

Generation identifiers, leases, locks, fencing tokens, kernel handles, source binding, or OS-mediated revocation are implementation candidates only.

---

## 14. Observer and Processor boundaries

The authority ontology constrains later components.

### Observer

The Observer produces or records facts about what is happening.

Observation does not create authority.

A liveness fact, external status, or detected event may become a trusted premise to a Kernel guard only under an explicit trust/currentness contract.

### Processor

The Processor, if present, computes deterministic consequences, reusable derivations, dependency information, caches, or other structured results.

Derivation does not create authority.

A Processor result may inform a guard or Orchestrator judgment, but its authority significance depends on the authoritative inputs, trust assumptions, currentness, completeness, and the guard that consumes it.

### Orchestrator

The Orchestrator performs semantic judgment.

Judgment does not create authority outside the Orchestrator's current delegated envelope.

These distinctions preserve the processorless-core result while allowing trusted deterministic guard computation where correctness requires it.

---

## 15. Things that are not authority

The following may carry useful information but must not be treated as authority merely by existing:

- role names;
- model identity;
- agent identity;
- process identity;
- session identity;
- prompt instructions;
- natural-language claims;
- historical approval records;
- cached decisions;
- previous capability configuration;
- provenance alone;
- credentials detached from a current grant;
- successful reasoning;
- confidence scores;
- tool documentation;
- a Work Unit's creator identity;
- an Orchestrator's preference.

Any of these may be evidence or inputs to policy. None is a substitute for current Kernel-recognized authorization.

---

## 16. Provisional invariants

The following are the current authority invariants for further research and formalization.

1. **Root-source invariant** — within EDASES, authority ultimately derives from the user/operator.
2. **Mediation invariant** — protected authority is exercised only through a current trusted Kernel/engine mediation path.
3. **No-self-authorization invariant** — no model, execution, Orchestrator, role label, or Work Unit can enlarge its own authority by assertion.
4. **Attenuation invariant** — delegated authority cannot exceed its valid parent authority without an explicit higher-authority widening transition.
5. **Currentness invariant** — historical authority evidence is not sufficient proof of current authority.
6. **Role/authority separation invariant** — semantic roles are profiles; actual authority is determined by current grants.
7. **Resource/capability separation invariant** — loss of capability mediation does not inherently revoke already-granted computation resources.
8. **Capability-liveness invariant** — capability attachments become unusable when their required engine-mediated authorization relationship is unavailable.
9. **Recovery non-resurrection invariant** — remembered pre-crash capability attachments are candidates for reassessment, never automatically current after recovery.
10. **Orchestrator-bound invariant** — occupying the Orchestrator Role grants no intrinsic authority; an Orchestrator agent may directly authorize only what lies within its current user-delegated envelope, which may be narrow or broad and may change or be revoked at any time.
11. **Containment invariant** — nested Work Units gain nothing automatically and cannot escape restrictions imposed by their containment chain.
12. **Effect invariant** — denial or revocation must prevent future protected effects at the actual effect boundary, not merely change descriptive metadata.
13. **Engine-identity invariant** — engine process identity does not own authority; restart is current mediator recovery, not sovereignty transfer.
14. **Execution-neutral invariant** — internal computation is not itself an authority-bearing act unless it crosses a protected boundary or changes authoritative meaning.

These remain subject to falsification by concrete histories, realization constraints, or assurance obligations.

---

## 17. Open questions intentionally left for later work

This ontology does not yet freeze:

- the physical mechanism by which engine liveness invalidates capability attachments;
- the exact persisted representation of grants;
- whether management authority deserves a distinct stable concept ID or remains a specialization of Grant;
- the authentication mechanism by which the system knows an instruction came from the root user;
- the exact semantics of resource expiry and forced resource reclamation;
- how fine-grained capability validity should be;
- whether some capability classes require stronger source binding than others;
- how Orchestrator reassessment after recovery should be represented and audited;
- which user approvals are single-use, time-scoped, task-scoped, or standing policy;
- the minimal realization needed to prove that no unmediated effect path bypasses Kernel authority.

These are valid targets for Astra or later formal/empirical work. They must not be silently answered by importing mechanisms from existing harnesses.

---

## 18. Consequence for Phase I

Phase I should now treat the authority problem as:

> **Can Kernel + Work Unit realize user-derived, current, attenuated and revocable authority such that semantic decision roles remain bounded and protected effects are completely mediated?**

The remaining realization work should test that claim directly.

In particular, F1/F3 should distinguish:

- user/root authority;
- current engine mediation;
- Orchestrator management authority;
- Work Unit resource grants;
- Work Unit capability attachments;
- internal execution;
- historical capability state after crash;
- newly authorized capability state after reassessment.

Any model or prototype that collapses those distinctions should be treated as a candidate ontology failure rather than accepted as an implementation shortcut.
