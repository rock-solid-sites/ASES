# Kernel-0 Research

This directory contains the active inputs and evidence for the Kernel-0 reasoning program.

## Current experiment — read first

The active implementation-discriminating task is the [Kernel-0 Direct RTL Realization Experiment](./Kernel-0-Direct-RTL-Experiment.md).

A fresh agent working on that experiment should read, from the **same repository ref/commit**:

1. [Kernel-0 Direct RTL Realization Experiment](./Kernel-0-Direct-RTL-Experiment.md) — experiment scope, authority order, exclusions, success conditions and escalation rule.
2. [Kernel-0 Abstract Semantics](./Kernel-0-Abstract-Semantics.md) — normative realization-neutral Kernel contract.
3. [Kernel-0 Verification Obligations](./Kernel-0-Verification-Obligations.md) — normative correspondence and invariant obligations.
4. [Kernel-0 Finite Model](./Kernel-0-Finite-Model.md) and [kernel0_finite_model.py](./kernel0_finite_model.py) — bounded executable target and reference oracle.
5. [Kernel-0 Re-Minimization](./Kernel-0-Re-Minimization.md) — reduction constraint preventing prior realization mechanisms from becoming accidental Kernel primitives.

Do not begin the current experiment from the older realization, crash/recovery, stronger-assurance, Work Unit, or execution-engine documents. Pull them in only when the direct experiment produces a concrete question that requires them.

## Original reasoning entry point

For reconstruction of the original Kernel-0 reasoning program rather than the current RTL experiment:

1. [Kernel-0 Evidence Packet](./Kernel-0-Evidence-Packet.md) — neutral requirements and boundaries.
2. [Kernel-0 Reasoning Session Decision Record](./Kernel-0-Reasoning-Session-Decision-Record.md) — orchestration/routing decisions for Sol; do not treat it as semantic authority.
3. [Compact Prompt Skill](../../../skills/prompt/SKILL.md) — prompt construction rules used for Sol/Astra task prompts.

## Current reasoning result

[Kernel-0 Reasoning Phase Result](./Kernel-0-Reasoning-Phase-Result.md) records the open derivation, Work Unit adequacy test, falsification pass, retained semantic candidate, and unresolved alternatives for Crosslink issue #566.

[Kernel-0 Abstract Semantics](./Kernel-0-Abstract-Semantics.md) states the current provisional realization-neutral candidate and its guarantee boundary.

[Kernel-0 Verification Obligations](./Kernel-0-Verification-Obligations.md) separates abstract invariants, model adequacy, regression traces, realization correspondence, and trusted assumptions.

[Kernel-0 Finite Model](./Kernel-0-Finite-Model.md) records the bounded model result and its executable evidence.

Earlier realization work remains evidence and provenance, not the default architecture for the current experiment:

- [Kernel-0 Bounded Realization Comparison](./Kernel-0-Realization-Comparison.md)
- [Kernel-0 Still-Live Realization Experiment](./Kernel-0-Realization-Experiment.md)
- [Kernel-0 Realization Conformance](./Kernel-0-Realization-Conformance.md)

## Relationship to older work

Earlier EDASES kernel, Work Unit, state-machine, formal-verification, and implementation research remains provenance. Historical material should be pulled back in only when the current task produces a concrete question that it can help answer.

A prior implementation is never evidence that its mechanisms are required by the Kernel. The current direct RTL experiment deliberately starts again from the semantic contract and bounded model.

## Current objective

Determine whether the bounded Kernel-0 target can be realized directly as fixed low-level transition logic, without a processor or general runtime programmability inside the trusted machine, and measure the mechanisms such a realization actually requires.

The experiment should either produce a low-level realization with bounded correspondence/synthesis evidence or a concrete obstruction showing which stronger mechanism is forced.

## Stronger assurance program

The stronger-assurance documents remain valid evidence for profiles beyond the base bounded experiment, but they are **not default inputs** to the direct RTL task.

[Assurance continuation](./Kernel-0-Assurance-Continuation.md) is the compact restart cursor for the operator-authorized ordered program (Crosslink #567, child of #566). [Authority-service crash/recovery](./Kernel-0-Crash-Recovery.md) derives and tests the stronger failure profile.

[Protected external effects](./Kernel-0-External-Effects.md) defines the selected decision-authorized obligation profile, including its explicit duplicate-delivery and post-revocation visibility limits.

[Multi-domain composition](./Kernel-0-Composition.md) records local independence, coupled admission and the compatible-recovery-cut requirement (bounded model only).

[Generalization](./Kernel-0-Generalization.md) separates conditional parametric arguments from finite evidence and preserves wraparound, longer-cycle and delegation-depth counterexamples.

[Whole-history refinement](./Kernel-0-Refinement-Assurance.md) checks whether complete observed concurrent/crash histories admit one permitted abstract order.

[Re-minimization](./Kernel-0-Re-Minimization.md) classifies retained distinctions, optional profiles, trusted assumptions and mechanisms; no new primitive is justified.

[Stronger realization direction](./Kernel-0-Stronger-Realization.md) retains the small transactional reference and records storage-call/partial-write crash experiments, with explicit limits on power loss and trusted storage currentness.
