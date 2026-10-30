---
title: Constraint-Driven Realization and Assurance Selection Method
program: ASES
layer: Methodology
document_type: Methodology Specification
status: Active
authority: Canonical
canonical_repository: ases
depends_on:
  - docs/methodology/ASES Bounded Project Build Method.md
related_documents:
  - docs/research/kernel-0/Kernel-0-Reasoning-Session-Decision-Record.md
  - docs/methodology/State-Model Applicability and Reuse Method.md
consumed_by:
  - project verification architectures
  - project implementation decision records
last_updated: 2026-10-30
---

# Constraint-Driven Realization and Assurance Selection Method

## Purpose

Select a system realization **by deriving requirements and excluding approaches that fail them**, not by choosing from a preapproved list of languages, frameworks, architectures, or technologies.

A realization is whatever mechanism physically or operationally satisfies the system's specified behavior. A traditional software implementation, programming language, or processor is not a prerequisite. The outcome of this method must be *demonstrated adequacy*, not membership in an approved category.

This is a design-selection method, not a replacement for requirements engineering, VSDD, state-modeling, implementation conformance or tests.

## Governing rules

1. **Define the properties before viewing solutions.** Establish behavior, safety, correctness, security, resource, performance, reliability, recovery and maintainability requirements at the appropriate system boundary. Avoid candidate examples, favored implementations and technology lists in the initial derivation prompt.
2. **Express exclusions as falsifiable requirements.** A constraint must specify the forbidden condition or mandatory guarantee, the scope/environment, a measurable threshold or invariant where possible, and a mechanism for establishing whether it holds. Vague labels such as "safe", "fast" or "formal" are not acceptance criteria.
3. **Eliminate for evidence-based failure, not unfamiliarity.** An approach is excluded when it cannot satisfy a hard requirement under the stated constraints, or satisfying it would require an unacceptable change to those constraints. A candidate with insufficient evidence is **UNRESOLVED**, not proven viable; a candidate from an unfamiliar realization family is not rejected for that reason.
4. **Preserve an open search space.** Search across mechanisms and system boundaries without assuming a language, runtime, processor, deployment topology, or conventional architecture. Look for ways to remove components and failure modes entirely rather than only mitigating them.
5. **Separate constraints from optimization.** Safety and other non-negotiable guarantees are gates. Among surviving candidates, compare verified fitness, trusted-base size, performance headroom, complexity, cost, agent implementation/review reliability, and maintenance. No amount of convenience compensates for a failed mandatory guarantee.
6. **Use appropriate assurance.** Ask which properties are mechanically enforced, proven, tested, observed or still assumed; distinguish abstract-model correctness from actual realization conformance. A type system, memory-safety claim or formally verified subcomponent is not proof of the whole system.
7. **Minimize the actual trusted boundary.** Account for libraries, runtimes, compilers, firmware/hardware, operating systems, permissions, external processes, network services and operator procedures wherever the claimed property depends on them.
8. **Reopen on evidence.** A new failure, requirement, platform constraint or verifiable alternative can change exclusions and the selected realization. Record the reason and affected guarantees.

## Selection procedure

### 1 — Specify independent of realization

State what must be true and what must never occur. Classify safety, liveness and other requirements; identify authority, ownership, lifecycle, resource and external boundaries. Establish measurable performance/resource ceilings or targets with workloads and measurement conditions, rather than calling an implementation efficient by reputation.

### 2 — Assess whether a state model helps

Use the State-Model Applicability and Reuse Method where behavior has meaningful transitions or authority/lifecycle semantics. Derive relevant guards and invariants without choosing the mechanism that enforces them. A justified NOT APPLICABLE result is valid.

### 3 — Build the exclusion criteria

For every mandatory property record:

| Field | Obligation |
| --- | --- |
| Claim | Exact property, invariant, forbidden event, or performance bound |
| Scope | Component, system boundary, assumptions, operating conditions |
| Failure | Observable counterexample or unmet threshold |
| Evidence | The discriminating proof, test, inspection or deployment observation |
| Consequence | Exclude, remain unresolved pending evidence, or proceed to comparison |

Requirements may rule out whole realization families, a proposed design within a family, or a specific configuration. Do not infer broad categorical exclusions from one failing implementation.

### 4 — Search without supplying an approved-option list

Generate and investigate possible ways to satisfy the properties, including opportunities to remove the need for a component or architectural assumption. Search prior art for **mechanisms that meet the constraints**, not examples to copy by default. Where an agent is used, give it requirements, exclusions and evidence obligations before disclosing prior favored choices. Permit competing independent derivations when anchoring could materially narrow the search.

### 5 — Filter and test

For each concrete candidate, map required properties to mechanisms and evidence. Mark:
- **EXCLUDED** when credible, relevant evidence establishes failure of a hard constraint;
- **UNRESOLVED** when a critical property cannot yet be supported or a key assumption remains untested;
- **VIABLE** only after evidence supports every applicable non-negotiable requirement at the claimed scope.

Use the cheapest discriminating experiment to resolve pivotal uncertainties. A local test cannot establish untested host, network, hardware or production boundaries. Maintain an explicit record of *what was not evaluated*.

### 6 — Choose within the viable set

Only after exclusion gates have been applied, compare surviving realizations on justified trade-offs, including assurance strength, implementation/operational complexity, resource costs, performance, reversibility, maintenance and total trusted computing base. If no candidate is demonstrated viable, do not pick the least-bad one by fiat: report the unsatisfied requirements or investigation needed and seek a change in constraints when warranted.

### 7 — Record and verify

A project decision record preserves: the properties and their sources; measurable exclusion gates; models/assumptions; search coverage (including unexplored regions); excluded and unresolved approaches with evidence; viable alternatives; chosen realization and why; verification plan; remaining trust assumptions; and conditions that reopen the decision.

A chosen candidate is still a hypothesis about realized behavior until the implementation/physical system passes its own conformance and operational acceptance gates.

## Prompt and agent discipline

Do not give a selection agent a "choose one of these" list, a default language, a sample architecture, or a success-shaped prototype unless the operator has explicitly imposed that constraint or the investigation's purpose is to evaluate those specific candidates. Do not convert illustrative technologies in research sources into allowed-option inventories.

When a previous implementation already exists, separate **behavioral evidence** from implementation preference. Existing tests may define required behavior but do not justify retaining that language or architecture. Where independent ideation matters, withhold historical choices until after the initial requirements-first derivation and then use them as prior art or adversarial comparisons.

## Relation to VSDD

VSDD supplies specification and verification activities; it does not decide the implementation realization. Where state-based representation is useful, its adaptation and conformance methods instantiate the obligations. This method defines the selection gate **upstream of implementation choice**, without weakening VSDD's test-first, adversarial or realization-conformance requirements.

## Kernel-0 precedent

Kernel-0 illustrates semantics-first separation: its state and authority model is evaluated independently of the physical mechanism that might realize it. Reconsideration of a previously discussed software realization did not require abandoning the state model. The general method therefore must neither presume a programming language nor predetermine a processorless result.

## Governing principle

**Constrain by required properties; exclude by evidence; search broadly without seeding answers; select only among demonstrated survivors.**
