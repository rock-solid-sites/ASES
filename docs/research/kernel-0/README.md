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

## Relationship to older work

Earlier EDASES kernel, Work Unit, state-machine, and formal-verification research remains provenance. The Evidence Packet consolidates the settled requirements needed for the current derivation without requiring the first frontier pass to ingest the historical implementation path.

Historical material should be pulled back in only when the current reasoning produces a concrete question that it can help answer.

## Current objective

Derive the smallest defensible Kernel-0 consistent with the evidence, test it as the authority substrate needed by the Work Unit architecture, and defer realization selection until the semantic candidate survives adequacy and adversarial reasoning.
