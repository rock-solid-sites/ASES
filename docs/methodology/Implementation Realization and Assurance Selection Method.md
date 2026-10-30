---
title: Implementation Realization and Assurance Selection Method
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

# Implementation Realization and Assurance Selection Method

## Purpose and scope

Choose an implementation *realization* and assurance mechanisms based on the properties a project must satisfy. Realization includes programming language(s) and runtime, but may instead or additionally use declarative specifications, hardware/RTL, processorless or minimal-TCB designs, verified components, configuration, or existing services. **No traditional program, processor, or particular language is required by ASES.**

This method governs how to make and substantiate an implementation choice; it does not impose a universal realization. The project chooses its form only after describing its behavior and the assurances it needs. A state model may be the primary behavioral specification without implying a software implementation.

## Governing rules

1. **Semantics before realization.** Define required behavior, trust boundaries, invariants, failure modes, and acceptance evidence before choosing a language, runtime, ISA, processor or hardware design. Do not use a favored implementation to hide an unresolved semantic question.
2. **Evaluate absence as a candidate.** Ask whether a traditional program, language, processor or persistent service is necessary. Where a smaller declarative, hardware, processorless or existing mechanism suffices, compare it on equal terms; do not treat "no language" as an automatic exemption from verification.
3. **Prefer mechanically established guarantees.** Assess type/ownership systems, refinement types, contracts, model checking, proof, static analysis, OS/hardware enforcement and observational evidence against *specific* properties. Prefer the least complicated combination that achieves the required assurance.
4. **Consider the whole trusted base.** Include compiler, toolchain, runtime, dependencies, unsafe/FFI interfaces, OS, hardware, firmware, network and external control planes. A proof of one component does not prove the total system.
5. **Separate evidence classes.** Memory safety does not imply authorization safety; verified models do not establish implementation conformance; tests do not constitute proof; formally verified code does not guarantee properties of unmodeled external resources.
6. **Assurance is proportionate to failure.** Concentrate stronger verification where violation would invalidate critical authority, isolation, safety, durability or termination guarantees. Prefer cheaper discriminating tests elsewhere.
7. **Account for practical reliability.** Compare dependency health, compatibility, agent ability to build and review, compilation/test cost, portability, reproducibility, maintenance and cost. Do not optimize a theoretical property at the expense of deployability without reason.
8. **Record and revise.** Preserve evidence, rejected alternatives, limitations and reopening conditions. Change choices on concrete counterevidence, not language fashion.

## Decision procedure

### 1. State required properties

List guarantees and classify each as **safety** (nothing forbidden happens), **liveness** (required progress eventually occurs under stated assumptions), or another precisely described property. Identify the authority and external resources involved. State which properties are critical and what evidence can falsify them.

### 2. Assess modeling suitability

Apply the separate State-Model Applicability and Reuse Method. A PRIMARY or SUPPLEMENTARY state model supplies behavioral and transition obligations independently of implementation technology. NOT APPLICABLE is an acceptable justified outcome.

### 3. Identify realization families

Include plausible realizations, not just languages: for example an existing vetted service; a declarative configuration or policy; processorless or minimal-processor hardware; RTL/FPGA; a small verified kernel; and software in Rust, Haskell, OCaml, SPARK/Ada, F*, Go, Python or another suitable language. Eliminate candidates only with documented constraints or a cheap test.

### 4. Map properties to mechanisms

For each candidate, distinguish:
- what the language, type system, compiler, proof assistant, model checker or hardware **actually guarantees**;
- what still depends on runtime checks, kernel/hardware enforcement and operating procedures;
- what requires implementation-conformance, fault-injection, resource or integration tests;
- what remains unverified or outside scope.

Identify the minimum trusted computing base and external assumptions.

### 5. Run the cheapest discriminating comparison

If competing choices materially differ, prototype only the difficult invariant, proof or boundary, not full competing products. Measure feasibility and evidence quality, then select the smallest adequate realization.

### 6. Record the decision

The project decision record must name the chosen realization or justified absence of a traditional language/processor, alternatives, required guarantees, evidence mapping, trusted base, operational constraints, unverified assumptions, and triggers for reassessment. Integrate with the existing verification architecture and acceptance gates.

## Boundary with VSDD

VSDD's specification, test-first and verification practices remain applicable regardless of realization, adapted to the artifact being tested. This selection method neither replaces VSDD nor introduces additional VSDD phases. A verified state model, if used, must still be checked against its actual physical/software realization.

## Kernel-0 precedent

Kernel-0 has progressed beyond the earlier provisional Verus/Rust software choice toward evaluation of a minimal-TCB / processorless architecture. The model and its admissible transitions are considered independently of a realization. That precedent demonstrates why a software-language preference must never be an upstream methodological requirement. This document does not settle Kernel-0's final design.

## Governing principle

**Choose the smallest justified realization and verification mechanism that establishes the required guarantees; a language, runtime or conventional processor is optional, not assumed.**
