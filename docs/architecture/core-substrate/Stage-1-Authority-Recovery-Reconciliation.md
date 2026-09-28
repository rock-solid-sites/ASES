---
title: Stage-1 Authority and Recovery Reconciliation
program: EDASES
layer: Architecture
document_type: Design and Reasoning Record
status: Draft
authority: Derived
canonical_repository: edases
crosslink_issue: 571
baseline_commit: 8d158e3e82d5811e420c80cc6c9664d3ae4a6088
depends_on:
  - Astra Reasoning Input Provenance
  - EDASES Work Unit Component Design
  - EDASES Authority Ontology
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
  - EDASES Phase I Core Substrate Closure
consumed_by:
  - Phase I formalization
  - Phase I realization
  - Phase I architectural closure review
related_documents:
  - Phase I Processorless Core Falsification
  - Phase I Revocation Verification and Q1 Reduction
  - Phase I Core Substrate Verification Work
  - EDASES Execution Engine Roadmap
  - EDASES Efficiency Architecture
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-28
---

# Stage-1 authority and recovery reconciliation

## 1. Run boundary and exact evidence

This is the operator-requested reconciliation of the Stage-1 authority/recovery
semantic delta against the existing Kernel + Work Unit candidate. It is not a
rerun of Phase I, a canonical change, implementation, or formal verification.
New counterhistories below are constructed reasoning, not executed traces.

**Initial checkpoint:** provenance verified; investigation in progress. No A/B
completion verdict is asserted by this checkpoint.

The frozen architecture basis is the following exact eleven-document set at
`8d158e3e82d5811e420c80cc6c9664d3ae4a6088`. The manifest was read at
`d310a08de512aa7864b283e3964173e64358a4ff`, which changes only
`docs/research/Astra-Reasoning-Input-Provenance.md` relative to that head. This run
branches from that manifest commit as `codex/stage1-authority-recovery`.
The branch base is not permission to consume other files as architecture inputs.

Manifest: [Astra Reasoning Input Provenance](../../research/Astra-Reasoning-Input-Provenance.md).
For each row, `git rev-parse <frozen-head>:<path>` and the checkout's
`git hash-object <path>` both matched the recorded blob. All eleven passed.

| Frozen path | Git blob |
| --- | --- |
| `docs/architecture/EDASES Work Unit Component Design.md` | `22c98dbabdaed7f41d656209a6ce96269dde8390` |
| `docs/architecture/EDASES-Authority-Ontology.md` | `170016e0d8cfcb72bbe51f5cad230bf53192aa02` |
| `docs/architecture/EDASES-Efficiency-Architecture.md` | `349eee3b51171a9365201eff5d2bd10d8cbfa719` |
| `docs/architecture/EDASES-Execution-Engine-Roadmap.md` | `a82d8a3fc54fd075fd6a20cf9e64ce560313f87c` |
| `docs/architecture/core-substrate/Phase-I-Closure.md` | `a82482b1718a652a39a5a2bb179797f92908380d` |
| `docs/architecture/core-substrate/Phase-I-Processorless-Falsification.md` | `33ff65100cbb10c107337e0f325d1db023e8ffe1` |
| `docs/architecture/core-substrate/Phase-I-Revocation-and-Q1.md` | `4103042649e07b7fd4d6bb1c0f4cf30a01bcc9a9` |
| `docs/architecture/core-substrate/Phase-I-Verification.md` | `ca378a16e31128d6ed11d5472d83253340802253` |
| `docs/research/kernel-0/Kernel-0-Abstract-Semantics.md` | `fd2a485dba3805884fc394b093a61daa60719072` |
| `docs/research/kernel-0/Kernel-0-Verification-Obligations.md` | `7c1d9b198b34c360dd6e8d7d4795704811cfdfa3` |
| `docs/research/registry/Concepts and Topics Registry.md` | `6b7ddf737c14a3853e9be2e64b4417c013ee9c96` |

The original Phase-I output checkpoint remains
`cff5f57c2855c1a251d5b2d4b2f7058be12a3b07`. The reconciled closure and Q1
records in this packet include later work; their wording is not attributed
retroactively to that original run. Work Unit A–L controls current semantics;
the historical design below A–L and Q1's pre-disposition arguments are historical
evidence, not revived requirements. Registry use is navigation/lineage only.

### Additional evidence and operational reads

- The attached operator request supplies the objective, semantic delta, stop rule
  and two completion states. Its SHA-256 is `69cd86c4487860c37b2f9a3d41b8ffc594f5b8d9c387c114fb5ed957972378cd`.
- No outside architecture source, later architecture revision, linked historical
  research file, live platform claim, or implementation experiment has yet been
  introduced. References within the frozen packet are inherited claims unless
  separately listed here; their linked sources were not silently imported.
- Operational guidance read from the starting checkout: AGENTS.md, ORIENTATION.md,
  Documentation Standard and Concept: Levels of Abstraction. These govern work
  and document structure, not architecture conclusions. Crosslink issue/session
  state and Git/worktree metadata were inspected for task coordination only.
  Shared AGENTS hygiene reported current. The active corresponding issue is #571.
- The main checkout has unrelated changes and is preserved. This investigation
  uses `/home/claude-code/.codex/worktrees/authority-recovery/ASES`.

## 2. Initial discriminators

1. Does user-rooted authority require a new primitive, or does it instantiate
   Kernel-0's explicit initial management premise and guarded delegation?
2. Can fresh reassessment be distinguished from automatic historical replay without
   assuming an Orchestrator, an intent oracle, or a second authority owner?
3. Does continued sealed computation mutate accepted meaning, create protected
   effects, or race safe disposition? A seal alone cannot establish quiescence.
4. Can the existing coherent-view, effect-contract and currentness distinctions
   separate those histories without hiding a new subsystem inside an unspecified
   guard?

**WHY:** these are immediate consequences of the supplied semantic delta, with
cheap counterhistories capable of defeating superficially compatible records.
**WHAT:** the exact packet above, especially Work Unit E–J, Authority Ontology
§§4–13, Kernel-0's view/order/failure contract and closure H1/H4/H14/C1–C13.
**HOW CERTAIN:** evidence-based investigation targets; no reconciliation result yet.
**WHAT-NOT-TESTED:** all model/realization obligations, independent review, and
whether the candidate survives the remaining reasoning.
