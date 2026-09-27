# Kernel-0 Research

This directory contains the active inputs for the Kernel-0 reasoning program.

## Read first

1. [Kernel-0 Evidence Packet](./Kernel-0-Evidence-Packet.md) — neutral requirements and boundaries. This is the primary context for the first open Astra reasoning pass.
2. [Kernel-0 Reasoning Session Decision Record](./Kernel-0-Reasoning-Session-Decision-Record.md) — orchestration/routing decisions for Sol. Do **not** include this in the first Astra pass.
3. [Compact Prompt Skill](../../../skills/prompt/SKILL.md) — prompt construction rules used for Sol/Astra task prompts.

## Current reasoning result

[Kernel-0 Reasoning Phase Result](./Kernel-0-Reasoning-Phase-Result.md) records the open derivation, Work Unit adequacy test, falsification pass, retained semantic candidate, and unresolved alternatives for Crosslink issue #566.

[Kernel-0 Abstract Semantics](./Kernel-0-Abstract-Semantics.md) states the current provisional realization-neutral candidate and its guarantee boundary.

[Kernel-0 Verification Obligations](./Kernel-0-Verification-Obligations.md) separates abstract invariants, model adequacy, regression traces, realization correspondence, and trusted assumptions.

[Kernel-0 Bounded Realization Comparison](./Kernel-0-Realization-Comparison.md) compares realization families against the frozen minimum semantics and states the next discriminating experiment.

[Kernel-0 Finite Model](./Kernel-0-Finite-Model.md) records the bounded model result and its unchanged executable evidence.

[Kernel-0 Still-Live Realization Experiment](./Kernel-0-Realization-Experiment.md) records the subsequent concrete experiment, its pre-implementation correspondence, tests, findings and claim boundary. The [conformance review](./Kernel-0-Realization-Conformance.md) traces the relevant semantic obligations through the service.

## Relationship to older work

Earlier EDASES kernel, Work Unit, state-machine, and formal-verification research remains provenance. The Evidence Packet consolidates the settled requirements needed for the current derivation without requiring the first frontier pass to ingest the historical implementation path.

Historical material should be pulled back in only when the current reasoning produces a concrete question that it can help answer.

## Current objective

Test the candidate through bounded model and realization correspondence, preserving the distinction between research evidence and production architecture. The realization experiment identifies the next discriminating assurance step; it does not authorize architectural expansion.

## Stronger assurance program

[Assurance continuation](./Kernel-0-Assurance-Continuation.md) is the compact
restart cursor for the operator-authorized ordered program (Crosslink #567,
child of #566). [Authority-service crash/recovery](./Kernel-0-Crash-Recovery.md)
derives and tests the stronger failure profile. These findings extend the
assurance evidence; they do not silently revise the base semantic contract.

[Protected external effects](./Kernel-0-External-Effects.md) defines the selected
decision-authorized obligation profile, including its explicit duplicate-delivery
and post-revocation visibility limits.

[Multi-domain composition](./Kernel-0-Composition.md) records local independence,
coupled admission and the compatible-recovery-cut requirement (bounded model only).

[Generalization](./Kernel-0-Generalization.md) separates conditional parametric
arguments from finite evidence and preserves wraparound, longer-cycle and
delegation-depth counterexamples.

[Whole-history refinement](./Kernel-0-Refinement-Assurance.md) checks whether
complete observed concurrent/crash histories admit one permitted abstract order.

[Re-minimization](./Kernel-0-Re-Minimization.md) classifies retained distinctions,
optional profiles, trusted assumptions and mechanisms; no new primitive is justified.

[Stronger realization direction](./Kernel-0-Stronger-Realization.md) retains the
small transactional reference and records real storage-call/partial-write crash
experiments, with explicit limits on power loss and trusted storage currentness.
