---
title: ASES Universal Conformance Checklist — State-Based Artefacts
program: Methodology
layer: Methodology
document_type: Universal Conformance Checklist
status: Draft
authority: Derived
canonical_repository: edases
depends_on:
  - VSDD Adaptation Profile — State-Based Specifications
  - to-file/VSDD.md
consumed_by:
  - ASES state-based project specifications
  - project-specific conformance suites
  - VSDD Phases 1–6
  - builder completion gates
  - adversarial reviewer gates
supersedes: []
superseded_by: []
last_updated: 2026-08-29
---
# ASES Universal Conformance Checklist — State-Based Artefacts

> **Purpose:** Universal framework for deriving a project-specific conformance suite from an ASES state-based specification. **Scope:** Universal conformance dimensions only; no project-specific states, events, resources, technologies, tests, or assumptions. **Authority:** Derived from the VSDD Adaptation Profile; does not replace, amend, or extend VSDD.

## 1. Canonicality
The canonical checklist must remain domain-independent. Project-specific material belongs in the instantiated suite. The universal document defines **what must be checked**; the project suite defines **what that means here**. Project experience must not silently rewrite universal obligations.

## 2. Lifecycle Integration
### Phase 1 — Specification and Verification Architecture
[ ] State-based representation is justified.  
[ ] State model is established.  
[ ] Critical invariants and forbidden transitions are identified.  
[ ] Identity/ownership rules are identified where applicable.  
[ ] Abstraction boundaries and assumptions are explicit.  
[ ] Verification tooling is selected in Phase 1b.  
[ ] Verification scope and limitations are recorded.  
[ ] Initial conformance strategy is defined.  
[ ] Traceability is defined.

### Phase 2 — Test-First Implementation
[ ] Model-derived transition/guard/forbidden-transition tests exist.  
[ ] Relevant identity/concurrency tests exist.  
[ ] Tests satisfy the existing VSDD red-gate before corresponding implementation is accepted.

### Phase 3 — Adversarial Refinement
[ ] Adversary reviews model.  
[ ] Adversary reviews assumptions and abstractions.  
[ ] Adversary reviews verification architecture.  
[ ] Adversary reviews model-derived tests.  
[ ] Adversary reviews model→implementation mapping and evidence.

### Phase 4 — Feedback Integration
[ ] Model refinements are integrated when discoveries invalidate it.  
[ ] Affected requirements/tests/implementation/evidence are updated.  
[ ] Revised artefacts return through applicable VSDD review/gates.

### Phase 5 — Formal Hardening
[ ] Selected model verification is executed.  
[ ] Implementation conformance is verified.  
[ ] Critical external-resource, concurrency, and mutation obligations are verified where applicable.

### Phase 6 — Convergence
[ ] Model remains consistent with requirements.  
[ ] Required model verification is complete.  
[ ] Required tests pass.  
[ ] Implementation conforms.  
[ ] Adversarial findings are resolved or dispositioned.  
[ ] Evidence supports the claims.

## 3. Checklist Semantics
Each item is `[ ] OPEN`, `[x] VERIFIED`, `[~] PARTIAL`, or `[!] FAILED`; applicability is separately recorded as `APPLICABLE`, `NOT APPLICABLE`, `OUT OF SCOPE`, or `BLOCKED`. `BLOCKED` is not `VERIFIED`.

## 4. Evidence Classes
Use, as applicable: MODEL, CONFORMANCE, UNIT, PROPERTY, MODEL-BASED, INTEGRATION, RESOURCE, OBSERVATION, MUTATION, INSPECTION, OPERATIONAL. Evidence from one class must not be treated as stronger evidence from another.

## 5. State Model Completeness
[ ] States defined where relevant.  
[ ] Initial and terminal states defined.  
[ ] Events defined.  
[ ] Guards defined.  
[ ] Permitted transitions defined.  
[ ] Forbidden transitions identifiable.  
[ ] Transition/state effects identified.  
[ ] Identity and ownership defined where material.  
[ ] Settlement conditions defined.  
[ ] Invariants defined.  
[ ] Relevant concurrency semantics defined.  
[ ] External and abstraction boundaries identified.

A model is complete when relevant behaviour is represented, explicitly abstracted with justification, or explicitly outside scope.

## 6. State Conformance
For each applicable state: [ ] implementation correspondence identified; [ ] entry conditions conform; [ ] exit conditions conform; [ ] guards enforced; [ ] effects permitted; [ ] no alternate path bypasses required state semantics; [ ] invalid/unknown state handling defined; [ ] abstractions documented; [ ] evidence supports the state contract.

## 7. Transition Conformance
For each permitted transition: [ ] event implemented; [ ] source-state condition enforced; [ ] guard enforced; [ ] destination reached; [ ] required effects occur; [ ] unauthorized effects do not occur; [ ] identity preserved; [ ] ownership preserved/transferred as specified; [ ] ordering/linearization preserved where applicable; [ ] discriminating verification exists; [ ] VSDD traceability retained where required.

## 8. Forbidden Transitions
For each relevant forbidden transition: [ ] explicitly represented; [ ] prevented by an authoritative mechanism; [ ] attempted invalid event has defined behaviour; [ ] discriminating test/proof exists; [ ] plausible mutation removing the barrier is detected.

## 9. Invariant Conformance
For each critical invariant: [ ] precisely stated; [ ] implementation mechanism identified; [ ] verification method selected in Phase 1b; [ ] scope defined; [ ] relevant model coverage exists; [ ] implementation coverage exists; [ ] external-boundary verification exists where required; [ ] plausible violating mutation is detectable; [ ] evidence supports the exact claim. Use exhaustive exploration where tractable; state bounded/sampled scope otherwise.

## 10. Identity Conformance
Where independently evolving entities or asynchronous commands exist: [ ] sufficient identity defined; [ ] identity survives relevant boundaries; [ ] delayed events cannot retarget another entity; [ ] retries/queued work retain intended identity; [ ] pending user actions retain identity where needed; [ ] restart cannot alias old identity to new entity; [ ] stale identity behaviour defined; [ ] critical identity mutations are detected.

## 11. Ownership Conformance
For each relevant resource/activity: [ ] owner identified; [ ] ownership established before guarantees apply; [ ] transfer defined where applicable; [ ] ownership cannot silently disappear; [ ] lifecycle/release mechanism exists; [ ] required resources cannot outlive ownership unnoticed; [ ] uncontrolled resources are classified; [ ] cross-boundary ownership is explicit; [ ] ownership mutations are detected.

## 12. Resource Conformance
Maintain a project resource inventory. For each relevant resource class: [ ] resource identified; [ ] owner identified; [ ] lifetime identified; [ ] cancellation/termination identified; [ ] settlement signal identified; [ ] terminal condition defined; [ ] resource state observable enough to establish the claim; [ ] appropriate verification exists; [ ] wrapper termination is not used as a substitute for resource termination; [ ] scope matches the declared guarantee.

## 13. External Boundary Conformance
For each process, subsystem, runtime, network, or other independent boundary: [ ] boundary identified; [ ] command/response/error semantics defined; [ ] delay/loss semantics defined where relevant; [ ] identity across boundary defined; [ ] ownership across boundary defined; [ ] settlement semantics defined; [ ] boundary does not imply unsupported guarantees; [ ] integration evidence exists where unit evidence is insufficient; [ ] unavailability has defined semantics.

## 14. Concurrency Conformance
Where events may race: [ ] relevant orderings identified; [ ] allowed outcomes defined; [ ] linearization semantics defined for critical transitions; [ ] arbitration mode defined; [ ] mutually exclusive states cannot be simultaneously authoritative; [ ] duplicate events defined; [ ] completion/cancellation interaction defined; [ ] successor admission relative to predecessor settlement defined; [ ] distinct identities remain isolated; [ ] representative interleavings tested; [ ] exhaustive exploration used where tractable; [ ] concurrency mutations detected where practical.

## 15. Temporal/Asynchronous Conformance
Where timing, retries, deferred events, or asynchronous observation exist: [ ] authoritative vs observed state distinguished; [ ] requested vs settled state distinguished where necessary; [ ] delayed/missing observation cannot manufacture authoritative transitions; [ ] timers cannot manufacture authoritative state unless explicitly assigned that authority; [ ] retry/timeout/late-event semantics defined; [ ] reconciliation exists where state may become stale; [ ] reconciliation is bounded and controlled.

## 16. Transport Conformance
For each asynchronous/remote command: [ ] success, failure, timeout, response loss, duplicate, stale, and owner-unavailable semantics defined where applicable; [ ] transport acceptance distinguished from underlying completion where necessary; [ ] ambiguous outcomes cannot silently become success; [ ] recovery/reconciliation has a deterministic trigger; [ ] reconciliation duplication is controlled.

## 17. Observation and Projection
For each client, interface, status stream, cache, or similar projection: [ ] authoritative source identified; [ ] projection relation identified; [ ] delay/loss handled; [ ] unknown state explicit; [ ] projection cannot silently become authoritative; [ ] human-facing output does not claim more than authority establishes; [ ] independent verification exists where projection is insufficient.

## 18. Recovery
For each recoverable abnormal condition: [ ] trigger defined; [ ] recovery state/actions defined; [ ] ownership preserved; [ ] no duplicate active entities; [ ] no unintended resurrection; [ ] required work not silently discarded; [ ] success/failure observable; [ ] behaviour remains consistent with the model.

## 19. Alternative Control Paths
For every independent state-changing mechanism: [ ] mapped to the model; [ ] authority preserved; [ ] critical guards cannot be bypassed; [ ] identity cannot be bypassed; [ ] ownership cannot be bypassed; [ ] alternate paths cannot produce conflicting semantics; [ ] materially different implementations are tested separately where required.

## 20. Purity Boundary Audit
Where pure model logic and effectful implementation are separated: [ ] boundary explicit; [ ] pure logic free of unintended external effects; [ ] network/filesystem/process/UI/logging/timer effects remain outside the pure boundary unless deliberately justified; [ ] exceptions documented and verified; [ ] existing VSDD Purity Boundary Audit applied.

## 21. Model→Implementation Conformance
For each material model element: [ ] state mapping; [ ] event trigger; [ ] guard enforcement point; [ ] permitted transition path; [ ] forbidden-transition barrier; [ ] declared effects implemented; [ ] implementation-specific behaviour does not alter model semantics; [ ] abstractions mapped; [ ] alternate paths cannot bypass critical obligations.

## 22. Model-Derived Tests
For each derived test: [ ] traces to a model element; [ ] requirement/invariant identifiable; [ ] created in the appropriate VSDD test-first stage; [ ] corresponding implementation was not accepted first; [ ] test is discriminating; [ ] exercises actual implementation; [ ] does not merely compare an implementation to an independently recreated model; [ ] mocks do not remove the behaviour under test; [ ] relevant coverage recorded.

## 23. Verification Tooling
[ ] State-model verification mechanism selected in Phase 1b.  
[ ] Representation recorded.  
[ ] Reason for selection recorded.  
[ ] Scope and limitations recorded.  
[ ] Environment recorded.  
[ ] Evidence format recorded.  
[ ] Implementation-conformance mechanism recorded.

The checklist is technology-neutral but does not permit deferral of the Phase 1b decision.

## 24. Adversarial Verification
The reviewer independently examines the model, assumptions, abstractions, verification architecture, derived tests, model→implementation mapping, and evidence for missing behaviour, weak guards, identity/ownership/concurrency errors, unjustified abstraction, tautological testing, bypass paths, stale evidence, and claims stronger than the evidence.

### Review Context Independence
Where adversarial review is required: [ ] reviewer evaluates the current artefact; [ ] reviewer has the authoritative information required to judge it; [ ] prior approvals are not treated as correctness evidence; [ ] prior conclusions do not substitute for independent examination; [ ] builder reasoning does not substitute for current implementation evidence; [ ] relevant prior reasoning is treated as evidence or an object of challenge, not an assumed conclusion; [ ] material changes are reviewed against the current version.

## 25. Abstraction Conformance
For every material abstraction: [ ] behaviour abstracted identified; [ ] reason recorded; [ ] omitted safety/ownership/identity/concurrency properties are covered elsewhere where relevant; [ ] environmental/deployment assumptions explicit; [ ] omitted-boundary verification identified; [ ] adversary has reviewed the abstraction.

## 26. Scope and Guarantee Conformance
For every significant claim: [ ] supported scope explicit; [ ] unsupported scope explicit where needed; [ ] local vs cross-boundary guarantees distinguished; [ ] resource vs state guarantees distinguished; [ ] infrastructure vs feature guarantees distinguished; [ ] crash boundaries defined where relevant; [ ] remote/external boundaries defined where relevant; [ ] terminal states do not imply unsupported external behaviour.

## 27. Recovery and Refinement
When later evidence invalidates the model: [ ] discovery recorded; [ ] affected model elements identified; [ ] requirements reassessed; [ ] affected tests identified; [ ] implementation identified; [ ] affected evidence invalidated/updated; [ ] revised model passes the applicable gate; [ ] revised tests remain within VSDD test-first discipline.

## 28. Contract Chain and Traceability
The project suite should preserve, as applicable:

```text
Requirement
  ↓
State Model
  ↓
Verification Property
  ↓
Tracked VSDD Work
  ↓
Test / Verification Method
  ↓
Implementation
  ↓
Conformance Evidence
  ↓
Adversarial Review
```

[ ] Critical requirements map to model elements where applicable.  
[ ] Critical model elements map to verification properties where applicable.  
[ ] Reviewable obligations remain represented in the existing VSDD tracking mechanism.  
[ ] Derived tests retain traceability.  
[ ] Implementation mappings are traceable.  
[ ] Evidence is traceable.  
[ ] Adversarial findings are traceable.

Tracking granularity follows existing VSDD accountability rules; not every model element requires an independent work item.

## 29. Builder Completion Gate
[ ] Model sufficient to derive obligations.  
[ ] Applicable universal dimensions instantiated.  
[ ] Applicability/scope decisions explicit.  
[ ] Critical model elements mapped to implementation.  
[ ] Critical invariants and forbidden transitions have verification methods.  
[ ] Identity/ownership/concurrency obligations addressed where applicable.  
[ ] Resource inventory sufficient for the claimed guarantee.  
[ ] External boundaries identified.  
[ ] Tooling selected in Phase 1b.  
[ ] Model-derived tests satisfy VSDD test-first discipline.  
[ ] Discovered refinements integrated.  
[ ] Evidence current.  
[ ] Blocked verification explicit.  
[ ] No critical claim rests only on assertion or inspection where executable verification is practical.

Builder completion is an evidence claim, not the final verdict.

## 30. Adversarial Reviewer Gate
[ ] Suite was derived from the actual model.  
[ ] Model represents the claimed behavioural boundary.  
[ ] Hidden assumptions are identified.  
[ ] Abstractions are justified.  
[ ] Authority is correctly assigned.  
[ ] Identity/ownership survive relevant boundaries.  
[ ] Forbidden transitions are genuinely prevented.  
[ ] Concurrency semantics are explicit and correctly implemented.  
[ ] External resources satisfy the stated guarantee.  
[ ] Observation cannot manufacture authority.  
[ ] Derived tests are discriminating.  
[ ] Implementation conforms to the model.  
[ ] Current evidence supports the claim.  
[ ] Plausible mutations are detected.  
[ ] Blocked/partial evidence is represented honestly.

The adversary should attempt the smallest plausible counterexample to each critical obligation.

## 31. Mutation Verification
[ ] Critical properties have plausible violating mutations.  
[ ] Mutations are introduced at the relevant implementation/boundary.  
[ ] The suite detects them.  
[ ] Surviving mutations trigger review of the property or test.

## 32. Test Environment Integrity
[ ] Required infrastructure and OS capabilities are available.  
[ ] Required external boundaries can be exercised.  
[ ] Fixtures preserve the relevant behaviour.  
[ ] Test doubles do not remove the behaviour under test.  
[ ] Environment failures are recorded as `BLOCKED`, not PASS.  
[ ] Evidence is from the implementation under review and current enough to support the claim.

## 33. Verdict
### PASS
All applicable critical obligations are verified; no unresolved critical failure exists; evidence supports the claim; required adversarial and mutation checks pass.

### REWORK
Material obligations, mappings, tests, assumptions, or evidence remain incomplete or ambiguous, but the architecture remains potentially viable.

### FAIL
A critical obligation is violated, a forbidden transition is reachable, authority/identity/ownership is broken, or the declared guarantee cannot be satisfied without architectural change.

### BLOCKED
A critical obligation cannot currently be verified because required infrastructure, environment, or external capability is unavailable. `BLOCKED` prevents a full verification claim unless the capability is explicitly outside scope.

## 34. Minimality
The project suite should prefer:

```text
one model property
    ↓
one conformance obligation
    ↓
one or more discriminating verification mechanisms
```

over duplicated prose and tests for behaviour already captured by the model.

## 35. Universal Adaptation Rule
A project-specific suite may instantiate, omit when genuinely inapplicable, and add project-specific obligations, but must not weaken a universal obligation. Project additions remain project-specific.

## 36. Governing Principle
> **The universal checklist defines the dimensions of conformance that state-based ASES work must examine. The project state model supplies the behavioural structure. The project-specific conformance suite instantiates the universal dimensions against that structure. Verification evidence establishes whether the resulting obligations have actually been satisfied.**
