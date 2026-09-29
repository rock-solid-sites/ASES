---
title: Kernel-0 Machine-Adjacent Realization Input Packet
program: EDASES
layer: Research
document_type: Reasoning Input Packet
status: Frozen
authority: Derived
canonical_repository: ASES
baseline_commit: 8d158e3e82d5811e420c80cc6c9664d3ae4a6088
last_updated: 2026-09-29
---

# Kernel-0 machine-adjacent realization input packet

## Purpose

This packet is the minimal fresh-context basis for the next Kernel-0 realization investigation. It supplies the surviving semantic target, the verification/refinement obligations, and the reduced Phase-I realization contract without importing historical realization candidates or later-system architecture.

Use the exact sources below as the initial context.

## Frozen sources

### 1. Kernel-0 abstract semantics

Read in full:

`docs/research/kernel-0/Kernel-0-Abstract-Semantics.md`

Blob:

`fd2a485dba3805884fc394b093a61daa60719072`

This is the realization-neutral semantic target.

### 2. Kernel-0 verification obligations

Read in full:

`docs/research/kernel-0/Kernel-0-Verification-Obligations.md`

Blob:

`7c1d9b198b34c360dd6e8d7d4795704811cfdfa3`

This defines the minimum model, trace, realization-conformance, and trusted-assumption obligations.

### 3. Phase-I core-substrate closure

Read only these sections initially:

`docs/architecture/core-substrate/Phase-I-Closure.md`

Blob:

`a82482b1718a652a39a5a2bb179797f92908380d`

Required sections:

- §1 — A concrete baseline without a new primitive
- §2 — Trusted realization: enforce effects, not component names
- §7 — Frozen semantic target for downstream work
- §8 — Remaining architectural uncertainty and review propositions
- §9 — Concise synthesis and handoff

These sections carry the reduced Work Unit realization demands, selected failure profile, surviving trusted functions, frozen target, and current claim boundary. The rest of the closure record is provenance and may be retrieved only if a concrete ambiguity makes it material.

## Provisional post-baseline delta

A later authority/recovery reconciliation on branch `codex/stage1-authority-recovery`, through commit `ad24f856a`, completed in reconciliation state A: no new core primitive or material architectural pivot was established.

Pending independent review, carry forward only these provisional refinements:

- recovery requires current reassessment before historical material can regain current authority;
- surviving resource allocations remain accounted for while they survive;
- sealing alone does not establish that destruction is safe.

If the realization investigation materially depends on one of these refinements, identify the dependency explicitly rather than assuming the pending review outcome.

## Context expansion rule

Begin from this packet only. Retrieve additional repository material when a concrete ambiguity, missing definition, or discriminating realization question makes it necessary. Record the exact added source and why it could change the result.

Do not reconstruct the historical realization search merely to survey alternatives. The task is to reason from the surviving semantic and verification target toward the lowest-assumption realizations that can refine it.
