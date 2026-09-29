---
title: Astra Reasoning Input Provenance
program: EDASES
layer: Research
document_type: Research Record
status: Active
authority: Derived
canonical_repository: edases

depends_on:
  - Documentation Standard
  - Documentation Taxonomy

consumed_by:
  - EDASES architecture consolidation
  - Astra architecture review and exploration

related_documents:
  - EDASES Execution Engine Roadmap
  - EDASES Authority Ontology
  - EDASES Work Unit Component Design
  - EDASES Phase I Core Substrate Closure

implements: []
implemented_by: []
supersedes: []
superseded_by: []

last_updated: 2026-09-29
---

# Astra Reasoning Input Provenance

## Purpose

This record preserves the exact repository versions used as architectural evidence by Astra and separates those inputs from later concurrent or human-directed changes.

Astra work must remain reproducible against the evidence actually available to the reasoning run. Later consolidation may change current working documents without retroactively changing the input packet from which prior conclusions were derived.

Blob SHA is recorded because it identifies the exact file contents even when later commits move or edit the path.

## Phase I initial reasoning baseline

Astra's Phase I core-substrate investigation began from repository commit:

`4e800957a673c8bd07eeea3c3c909349cdae76ac`

The Phase I closure record itself identifies this as its baseline. The following evidence set is the architectural packet referenced by that investigation.

| Document | Path at baseline | Blob SHA |
| --- | --- | --- |
| Execution Engine Roadmap | `docs/architecture/EDASES-Execution-Engine-Roadmap.md` | `5f52b23c2825933a5d6eb56fe6d732b908b3d69d` |
| Work Unit Component Design | `docs/architecture/EDASES Work Unit Component Design.md` | `1a05126cfbf11b9da749b1e9393dfcd9da92244e` |
| Kernel-0 Abstract Semantics | `docs/research/kernel-0/Kernel-0-Abstract-Semantics.md` | `fd2a485dba3805884fc394b093a61daa60719072` |
| Kernel-0 Verification Obligations | `docs/research/kernel-0/Kernel-0-Verification-Obligations.md` | `7c1d9b198b34c360dd6e8d7d4795704811cfdfa3` |
| Work Unit-0 Foundational Reduction | `docs/research/work-unit-0/Work-Unit-0-Foundational-Reduction.md` | `70443d7c2b76953188b3c4d2f39c1aef1a963a32` |
| Kernel-0 Assurance Continuation | `docs/research/kernel-0/Kernel-0-Assurance-Continuation.md` | `5ccabb35d12b115a26cf4a52e8d9d2433f5741c0` |
| Kernel-0 Re-Minimization | `docs/research/kernel-0/Kernel-0-Re-Minimization.md` | `a623236d7a944dc831f71ed108537f394647064f` |
| Kernel-0 Crash Recovery | `docs/research/kernel-0/Kernel-0-Crash-Recovery.md` | `a67f9d4012be7a28439c4d189257008074499d12` |
| EDASES Currentness and Recovery Assurance | `docs/research/currentness/EDASES-Currentness-Recovery-Assurance.md` | `f1c0911aa3f617d39806f2ca251cdf347727f68d` |
| Kernel-0 Protected External Effects | `docs/research/kernel-0/Kernel-0-External-Effects.md` | `07e71249ac793b438347a752f20a1cdd3cead1d5` |
| EDASES Bounded Structural Transitions | `docs/research/structural-change/EDASES-Bounded-Structural-Transitions.md` | `78e2b21f34bc65df83bdfdb2a1693e1193e980fa` |

This table records the evidence packet, not an assertion that each document was read with equal weight in every reasoning step.

## Astra Phase I output lineage

Astra's Phase I investigation produced the following seven commits from that baseline:

1. `73b6d64fee670757f4d07e741f3b0f6f4f4dcb91` — establish failure/realization boundary
2. `1c477c6628c9267841bb08d240a8fa65784b83a9` — close realization/replacement contracts
3. `de8fcd9e7a297320b21217905ea65618d5747806` — processorless falsification and fact admission
4. `76a38fb73147f18c0e168ab845f66e4d74bfb608` — closure obligation and exclusion obligations
5. `8bebb4037ac037ded385b25a6e2310d638de72f4` — preserve realization-boundary finding
6. `96a184e384c235ae43a3d479bc6263c5fca38589` — freeze Phase I candidate and downstream gates
7. `cff5f57c2855c1a251d5b2d4b2f7058be12a3b07` — reconcile Phase I findings and publish resumable closure

The Phase I Astra output checkpoint is therefore:

`cff5f57c2855c1a251d5b2d4b2f7058be12a3b07`

Later commits on the same branch must not be described as part of that original Astra run unless separately established.

## Post-Astra reasoning and reconciliation

After the Astra checkpoint, the branch received additional work including:

- `2bcad274ab0115d77700b379118df31b88c87297` — provisional Authority Ontology;
- `7391a917d28225ffdb816f42dfe777e1f9cba363` through `75cf6868ce3a732aa0e905c1aabdc76c6406af0e` — revocation/Q1 investigation, verification-plan changes, and reconciliation with the concurrently introduced ontology;
- `4b60d6c7066caa81e89f72af87114b48277bee04` — pre-consolidation branch head used to begin the documentation consolidation pass.

These later records are valuable evidence but are not retroactive inputs to the original Astra Phase I reasoning.

## Consolidated Astra packet — Stage 1 documentation repair

The first documentation-consolidation stage froze the next Astra working packet at pre-manifest branch head:

`8d158e3e82d5811e420c80cc6c9664d3ae4a6088`

The following exact blobs form the consolidated working set. Several are intentionally Draft, Experimental, or Derived. Inclusion here does **not** promote their authority.

| Document | Path | Blob SHA | Intended role for Astra |
| --- | --- | --- | --- |
| Work Unit Component Design | `docs/architecture/EDASES Work Unit Component Design.md` | `22c98dbabdaed7f41d656209a6ce96269dde8390` | Current canonical Work Unit semantics, including resolved sealing/recovery wording |
| Authority Ontology | `docs/architecture/EDASES-Authority-Ontology.md` | `170016e0d8cfcb72bbe51f5cad230bf53192aa02` | Project-critical Draft/Derived authority model for falsification and refinement |
| Efficiency Architecture | `docs/architecture/EDASES-Efficiency-Architecture.md` | `349eee3b51171a9365201eff5d2bd10d8cbfa719` | Experimental/Derived efficiency baseline; substantial research remains |
| Execution Engine Roadmap | `docs/architecture/EDASES-Execution-Engine-Roadmap.md` | `a82d8a3fc54fd075fd6a20cf9e64ce560313f87c` | Current sequencing and reopening rules |
| Phase I Core Substrate Closure | `docs/architecture/core-substrate/Phase-I-Closure.md` | `a82482b1718a652a39a5a2bb179797f92908380d` | Reconciled Phase I candidate and adversarial closure record |
| Processorless Falsification | `docs/architecture/core-substrate/Phase-I-Processorless-Falsification.md` | `33ff65100cbb10c107337e0f325d1db023e8ffe1` | Processor necessity attacks and conditional elimination evidence |
| Revocation/Q1 Record | `docs/architecture/core-substrate/Phase-I-Revocation-and-Q1.md` | `4103042649e07b7fd4d6bb1c0f4cf30a01bcc9a9` | Preserved reasoning record with explicit post-investigation disposition |
| Phase I Verification Plan | `docs/architecture/core-substrate/Phase-I-Verification.md` | `ca378a16e31128d6ed11d5472d83253340802253` | Downstream formalization/realization acceptance gates |
| Kernel-0 Abstract Semantics | `docs/research/kernel-0/Kernel-0-Abstract-Semantics.md` | `fd2a485dba3805884fc394b093a61daa60719072` | Provisional Kernel semantic contract used by both Astra passes |
| Kernel-0 Verification Obligations | `docs/research/kernel-0/Kernel-0-Verification-Obligations.md` | `7c1d9b198b34c360dd6e8d7d4795704811cfdfa3` | Provisional Kernel assurance target |
| Concepts and Topics Registry | `docs/research/registry/Concepts and Topics Registry.md` | `6b7ddf737c14a3853e9be2e64b4417c013ee9c96` | Identity/lineage/navigation only; not substantive architectural authority |

### Stage-1 semantic changes relative to the prior Astra checkpoint

The next Astra pass must not treat these as conclusions Astra had already reached at `cff5f57c`. They are new working inputs:

1. root authority belongs to the user; the engine represents/mediates/enforces user-derived authority rather than owning it;
2. the Orchestrator is expected to be the normal user-facing LLM agent but possesses exactly the authority currently delegated by the user; Kernel correctness does not require an Orchestrator agent;
3. baseline sealing disables affected capability admission/use and protected outward effects but does not inherently stop already-granted resource-backed internal computation;
4. pre-crash capability attachments are retained as historical recovery context only and require fresh authorized reassessment before reattachment, normally by the Orchestrator;
5. the efficiency architecture is now consolidated as an Experimental/Derived baseline rather than scattered across Work Unit history, roadmap targets, and processorless research;
6. the Concepts Registry no longer points active concepts at the nonexistent `EDASES Minimal Execution Substrate Architecture` document.

The invariant is:

> **Every Astra reasoning run should be recoverable to an exact repository commit and/or exact document blob set, with later semantic changes recorded separately rather than silently replacing its evidence base.**


## Stage-1 authority/recovery reconciliation output — 2026-09-29

The next reasoning pass used exactly the eleven Stage-1 blobs above at
`8d158e3e82d5811e420c80cc6c9664d3ae4a6088`, reading this manifest as blob
`89af38131465ee37fc780b7fb867860f51492f6e` at commit
`d310a08de512aa7864b283e3964173e64358a4ff`. Its separate reasoning branch is
`codex/stage1-authority-recovery`.

The [Stage-1 Authority and Recovery Reconciliation](../architecture/core-substrate/Stage-1-Authority-Recovery-Reconciliation.md)
records completion **A**, with no material architectural pivot established for
the scoped Phase-I candidate. It preserves fourteen constructed histories,
corrected/clarified contracts, prior-claim dispositions, nine supplementary
invariants and fourteen downstream verification fixtures. The substantive closure
checkpoint is `df67899af`; preceding checkpoints are listed in the record.

This is a Draft/Derived architectural result, not canonical promotion, formal
verification or realization evidence. No later architecture sources were added.
The original packet table and prior reasoning lineage above are unchanged;
this output entry does not retroactively alter either input set. F1/F3 remain
next, with the reconciliation's explicit obligations and claim limits.
