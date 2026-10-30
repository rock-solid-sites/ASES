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

Select a system realization by enforcing safety, correctness, security, performance and other measurable requirements first, excluding designs that fail them, and then assessing the demonstrated survivors. **For substantive systems, do not start from a shortlist of approved architectures or languages.**

A realization is any mechanism that satisfies the specified behavior. Conventional program structure or a particular execution architecture is not a prerequisite. An unconventional, previously untried or genuinely novel design may be the best fit: the absence of a long track record, community or example projects is a **risk to measure**, not an automatic exclusion. Such a design may be selected when evidence demonstrates that its project-specific benefits outweigh the additional validation, maintenance, tooling and support risks, and its critical guarantees are verified at the appropriate boundaries.

This method has **two levels of application**: a bounded implementation-language shortcut for small plugins/connectors, and the full open-ended exclusion process for more ambitious systems. Universal language exclusions apply to both. This is not a replacement for requirements engineering, VSDD, state-modeling, implementation conformance or tests.

## Governing rules

1. **Define the properties before viewing solutions.** Establish behavior, safety, correctness, security, resource, performance, reliability, recovery and maintainability requirements at the appropriate system boundary. Avoid candidate examples, favored implementations and technology lists in the initial derivation prompt.
2. **Express exclusions as falsifiable requirements.** A constraint must specify the forbidden condition or mandatory guarantee, the scope/environment, a measurable threshold or invariant where possible, and a mechanism for establishing whether it holds. Vague labels such as "safe", "fast" or "formal" are not acceptance criteria.
3. **Eliminate for evidence-based failure, not unfamiliarity.** An approach is excluded when it cannot satisfy a hard requirement under the stated constraints, or satisfying it would require an unacceptable change to those constraints. A candidate with insufficient evidence is **UNRESOLVED**, not proven viable. Limited prior art, few maintainers or unfamiliar design mechanisms raise the burden of investigation rather than ruling a candidate out; demonstrated benefits can outweigh these disadvantages.
4. **Preserve an open search space for substantial systems.** Search across mechanisms and system boundaries without presuming a language, runtime, deployment topology or conventional architecture. Find opportunities to remove components and failure modes rather than merely mitigate them. Apply the explicit language safety exclusions and use the small-project shortcut only when its scope conditions hold.
5. **Separate constraints from optimization.** Safety and other non-negotiable guarantees are gates. Among surviving candidates, compare verified fitness, trusted-base size, performance headroom, complexity, cost, agent implementation/review reliability, and maintenance. No amount of convenience compensates for a failed mandatory guarantee.
6. **Use appropriate assurance.** Ask which properties are mechanically enforced, proven, tested, observed or still assumed; distinguish abstract-model correctness from actual realization conformance. A type system, memory-safety claim or formally verified subcomponent is not proof of the whole system.
7. **Minimize the actual trusted boundary.** Account for libraries, runtimes, compilers, firmware/hardware, operating systems, permissions, external processes, network services and operator procedures wherever the claimed property depends on them.
8. **Reopen on evidence.** A new failure, requirement, platform constraint or verifiable alternative can change exclusions and the selected realization. Record the reason and affected guarantees.

## Universal implementation-language exclusions

**Do not author maintained project implementation code** in `C`, `C++`, `Objective-C`, `Zig`, or `PHP`. The prohibition extends to other implementation languages or modes that rely on unchecked/manual memory handling or do not meet the project's baseline safety and correctness expectations. This is a **project policy gate**, not a claim that all excluded languages share the same technical vulnerability: `PHP` is ordinarily memory-managed, but is excluded on the project's engineering and assurance criteria. Do not label a memory-managed language memory-unsafe without evidence.

Do not circumvent the exclusion by placing unsafe implementation in a native extension, embedded snippet, generated source, or FFI wrapper. Existing system dependencies and third-party runtimes do not automatically become forbidden simply because they contain excluded-language code, but they belong in the trusted-base and vulnerability assessment. An external dependency's existence does not license new unsafe-language application code.

Small disposable experiments can use temporary tools to *investigate* a candidate, but experimental output is not accepted as a maintained implementation without passing the relevant gate. No automatic exception for agent familiarity, shorter prompts or ecosystem popularity.

## Two-level application

### Level A — Short experiments and bounded plugins/connectors

A **short, disposable test** may use the fastest suitable tool provided its output is not deployed or retained as the maintained application. If it becomes a maintained project, re-evaluate before accepting the implementation.

For a **small, bounded plugin or connector** intended for actual use, select from this safety-oriented default language set:

- **Rust** — memory and resource ownership controls; strong compiler guarantees, with `unsafe` usage and dependencies audited.
- **Haskell** — strong static types and functional modeling; isolate and test effectful boundaries.
- **OCaml** — strong static types and algebraic modeling; validate runtime/native bindings.
- **Ada/SPARK** — contracts and proof-oriented subsets when the verified subset and toolchain are applicable.
- **F#** — strong static types and functional modeling, with managed runtime assumptions stated.
- **Go** — memory-safe managed execution and straightforward concurrency tooling; explicitly test the weaker application-level invariant guarantees.

This is a **practical default set for a narrow work class**, not a claim of equal formal assurance, an absolute catalog of safe languages, or a shortlist to seed open-ended research for larger architectures. A platform that only supports another implementation language is a material constraint to document and escalate rather than silently violating the gate.

The shortcut requires: a bounded scope, no unresolved critical trust-boundary assumptions, a documented reason for the choice, explicit safety/resource requirements, dependency inspection, and discriminating tests of failures and external boundaries. Adding arbitrary remote command execution, multiple service identities or durable agent authority can raise verification obligations even when delivered as a connector. The shortcut reduces *language research*, not safety checks.

### Level B — Systems beyond a bounded connector

For a standalone or multi-component system, persistent state/authority substrate, substantial product, complex concurrency or novel architectural claim, execute the **full exclusion-first selection procedure** below. Do not seed the initial reasoning with the Level A list. Start with requirements and elimination tests, then search without a predefined architecture or language menu. Apply the universal language exclusions only if implementation code is actually required.

Novel, unusual or poorly documented approaches are eligible **when their demonstrated advantages against the actual requirements outweigh** their extra implementation, verification, maintenance, tooling and operational risks. Proof of an abstract model alone is insufficient; require evidence that the proposed realization can satisfy the project's actual interfaces and boundaries. A lack of existing projects demands stronger evaluation, not automatic rejection.

## Selection procedure

### 1 — Specify independent of realization

State what must be true and what must never occur. Classify safety, liveness and other requirements; identify authority, ownership, lifecycle, resource and external boundaries. Establish measurable performance/resource ceilings or targets with workloads and measurement conditions, rather than calling an implementation efficient by reputation.

Determine whether the work is a disposable, short experiment; a bounded plugin/connector; or a larger system. Do not classify a complex multi-component product as a small plugin merely because its entry point is an MCP server or an API.

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

### 4 — Search without supplying an approved-option list (full process)

For systems beyond a bounded plugin/connector, generate and investigate ways to satisfy the properties, including opportunities to remove an entire component or architectural assumption. Search prior art for **mechanisms that meet the constraints**, not examples to copy by default. Give agents requirements, exclusions and evidence obligations before disclosing prior favored choices. Permit competing independent derivations when anchoring could materially narrow the search.

**Novelty assessment:** Compare a novel design's measurable gains against its absence of mature tools, community, demonstrations and operating history. Require tests/prototypes that directly challenge the proposed gains and the unknowns. Do not use adoption/popularity as a proxy for correctness, or novelty itself as an advantage.

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

For the **full process**, do not give a selection agent a "choose one of these" list, default language, sample architecture or success-shaped prototype unless the operator has explicitly imposed that constraint or the investigation evaluates those candidates. Do not convert illustrative research examples into allowed-option inventories. For an eligible **small plugin/connector**, use the bounded safety-focused language list below to reduce selection cost; it is not an architecture shortlist for larger systems.

When a previous implementation already exists, separate **behavioral evidence** from implementation preference. Existing tests may define required behavior but do not justify retaining that language or architecture. Where independent ideation matters, withhold historical choices until after the initial requirements-first derivation and then use them as prior art or adversarial comparisons.

## Relation to VSDD

VSDD supplies specification and verification activities; it does not decide the implementation realization. Where state-based representation is useful, its adaptation and conformance methods instantiate the obligations. This method defines the selection gate **upstream of implementation choice**, without weakening VSDD's test-first, adversarial or realization-conformance requirements.

## Kernel-0 precedent

Kernel-0 illustrates semantics-first separation: its state and authority model is evaluated independently of the physical mechanism that might realize it. Reconsideration of a previously discussed software realization did not require abandoning the state model. The general method must not presume conventional software or predetermine any particular physical architecture.

## Governing principle

**Exclude unsafe implementation languages by policy. For small connectors, select from a vetted safety-oriented language set. For substantial systems, derive measurable constraints first, search broadly without anchoring, and select only among verified survivors—including unconventional designs when their demonstrated benefits justify the added uncertainty.**
