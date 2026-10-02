---
title: Kernel-0 Direct RTL Clean-Room Review Packet
program: EDASES
layer: Research
document_type: Research Protocol
status: Active
authority: Derived
canonical_repository: ASES
depends_on:
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
  - Kernel-0 Finite Model
consumed_by:
  - Independent post-build review of c03bf1c470e54f51c299cb3347c547eeeae0e5ce
related_documents: []
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-10-02
---

# Kernel-0 Direct RTL Clean-Room Review Packet

## Frozen artifact

Review target:

- repository: `rock-solid-sites/ASES`
- commit: `c03bf1c470e54f51c299cb3347c547eeeae0e5ce`
- branch label at freeze time: `codex/kernel-0-direct-rtl-00086d17`

The target commit is immutable for review purposes. Do not review later ingress-reduction work as part of this claim.

## Claim A — bounded semantic correspondence

For each of the three finite profiles defined by the supplied model, and for every valid bounded state and every compared proposal in the declared input alphabet, the RTL authoritative transition and outcome refine the finite Kernel-0 reference transition under the stated realization assumptions.

Required consequences include:

- committed transitions decode to the same authoritative successor as the reference model;
- denied transitions leave authoritative state unchanged;
- stale or invalid authority cannot commit where the reference model denies it;
- whole-effect and configured invariant behavior match the bounded model;
- the authoritative state presented after a completed RTL transition is the state used by the next transition.

This is a bounded correspondence claim only. It does not claim unbounded populations, arbitrary content, arbitrary delegation depth, physical source authentication, power-loss recovery, external-effect exactly-once behavior, or analog hardware correctness.

## Claim B — evidence adequacy

The verification apparatus at the frozen commit is sufficient to establish Claim A over the declared bounded domain if its trusted tools and oracle are correct.

This includes the claims that:

- the enumerated state/proposal domain is complete for the declared finite target;
- the encoding/decoding relation is injective and faithful over that domain;
- exhaustive RTL comparison is against the unchanged finite-model oracle rather than a duplicated transition implementation;
- the clocked wrapper does not expose an additional authoritative transition between completed states under the declared synchronous abstraction;
- post-synthesis equivalence checks preserve the relevant RTL transition behavior;
- the verification is non-vacuous and detects representative semantic/RTL faults.

A reviewer may reject Claim B without rejecting the RTL itself if the evidence is incomplete, circular, unsound, or materially narrower than claimed.

## Realization assumptions

The review claim is conditional on these assumptions:

- trusted initialization/reset and build-time profile configuration;
- a complete stable proposal at the sampling boundary;
- trusted authority observation and authenticity information supplied at the ingress boundary;
- correct coherent clocking and register retention for the authoritative holder;
- correctness of the finite reference model and of the verification/synthesis tools used as assurance scaffolding.

These are assumptions, not properties proven by this artifact.

## Minimum governing sources

Read these from the frozen target commit:

### Semantic specification

- `docs/research/kernel-0/Kernel-0-Abstract-Semantics.md`
- `docs/research/kernel-0/Kernel-0-Verification-Obligations.md`

### Bounded target / oracle

- `docs/research/kernel-0/Kernel-0-Finite-Model.md`
- `docs/research/kernel-0/kernel0_finite_model.py`

### RTL artifact

- `docs/research/kernel-0/direct-rtl/kernel0.v`
- `docs/research/kernel-0/direct-rtl/correspondence.py`

### Verification apparatus

- `docs/research/kernel-0/direct-rtl/verify.py`
- `docs/research/kernel-0/direct-rtl/boundary_formal.v`
- `docs/research/kernel-0/direct-rtl/exhaustive_tb.v`
- `docs/research/kernel-0/direct-rtl/sequence_tb.v`
- `docs/research/kernel-0/direct-rtl/evidence/results.json`
- `docs/research/kernel-0/direct-rtl/evidence/source-manifest.json`

Additional generated logs or Yosys scripts under `direct-rtl/evidence/` may be inspected when needed to verify a concrete evidence claim.

## Excluded context

Do not use these as review inputs:

- `Kernel-0-Direct-RTL-Result.md`;
- builder reasoning, chat transcripts, or implementation rationale;
- the later ingress-reduction branch or its findings;
- previous reviewer outputs;
- older service/SQLite realization work;
- Work Unit or higher execution-engine architecture except where the supplied semantic specifications explicitly depend on them.

The review should be derived from the frozen artifact and the minimum governing sources above.

## Review outcome

For the assigned claim, return one of:

- **supported** — no material counterexample or evidence gap found within the declared assumptions and bounded scope;
- **falsified** — provide a concrete counterexample, mismatch, or unsoundness sufficient to defeat the claim;
- **not established** — identify the smallest missing evidence or ambiguity preventing the claim from being established.

Do not expand the architecture or propose a replacement design unless needed to explain a concrete failure.
