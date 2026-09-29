---
title: Kernel-0 Machine Realization Investigation
program: EDASES
layer: Research
document_type: Research Finding
status: Draft
authority: Derived
canonical_repository: ASES
crosslink_issue: 573
baseline_commit: c34d08413b2cca4f4a6add986c5b5c04e739b24f
depends_on:
  - Kernel-0 Machine-Adjacent Realization Input Packet
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
consumed_by:
  - Kernel machine realization formalization and experiments
related_documents:
  - EDASES Phase I Core Substrate Closure
  - EDASES Work Unit Component Design
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-29
---

# Kernel-0 machine realization investigation

Research checkpoint: provenance and investigation boundary are established; conclusions are still being evaluated. This record does not change the supplied semantics or select a production implementation.

## Input provenance and context boundary

The reasoning branch starts at `c34d08413b2cca4f4a6add986c5b5c04e739b24f`, the fetched tip of `codex/kernel-machine-realization-input` on 2026-09-29. The packet's semantic baseline is `8d158e3e82d5811e420c80cc6c9664d3ae4a6088`. Git blob identities were checked against the packet before reasoning.

| Input at the branch start | Git blob | Scope read |
| --- | --- | --- |
| [Input packet](./Kernel-0-Machine-Realization-Input-Packet.md) | `8e76ff7821d638cd5c3c5cba57461543416c329f` | Full |
| [Abstract semantics](./Kernel-0-Abstract-Semantics.md) | `fd2a485dba3805884fc394b093a61daa60719072` | Full |
| [Verification obligations](./Kernel-0-Verification-Obligations.md) | `7c1d9b198b34c360dd6e8d7d4795704811cfdfa3` | Full |
| [Phase-I closure](../../architecture/core-substrate/Phase-I-Closure.md) | `a82482b1718a652a39a5a2bb179797f92908380d` | Selected §§1, 2, 7, 8, 9 |

Additional repository context is limited to these recorded expansions:

| Added source | Exact scope and reason it could change the result |
| --- | --- |
| Phase-I closure, same blob | §4: §7 refers to this section for protected attachment contracts. Needed to distinguish use-time authority from a previously committed exact obligation; this determines whether an output gate must cancel delayed actions. Historical experiments mentioned there are not adopted as fresh evidence. |
| [Work Unit component design](../../architecture/EDASES%20Work%20Unit%20Component%20Design.md), blob `22c98dbabdaed7f41d656209a6ce96269dde8390` | §D only: §7 requires W.D boundary observations without enumerating them. Identity/genesis, creator, project, containment, granted resources, attached capabilities/agent and boundary state must remain interpretable without executing the interior. This constrains the abstraction and recovery relation. |
| [AGENTS](../../../..//AGENTS.md), blob `4e284d23966bdcb16e6394b715665dc3d4cecff1`; [ORIENTATION](../../../../ORIENTATION.md), blob `9423fa71597f5a525bfd29378978b6daacbcfc22`; [Documentation Standard](../../standards/Documentation%20Standard.md), blob `15c47446695686b19d5e4e67325dd45e0592aa7f` | Operational instructions and document metadata only; not extra semantic premises. Closure front matter/introduction and repository filenames were incidentally visible during navigation; historical realization arguments were not imported. |

The packet reports provisional authority/recovery refinements through `ad24f856a` on `codex/stage1-authority-recovery`. That branch was not retrieved. Current reassessment on recovery, continued accounting of surviving allocations, and sealing not proving safe destruction are carried as provisional conditions; the final analysis will identify where each matters.

## Investigation plan and evidence status

Derive necessary functions before matching technologies. Compare correctness assumptions, not component or source-line counts. Search primary research across software/ISA verification, interpreted confinement, proof-carrying computation, circuit refinement, crash refinement, and assurance diversity. Check every proposal against engine-loss mediation, whole commitment, current recovery and useful success witnesses.

WHY: these are where an apparently small semantic machine can hide a large trusted realization. WHAT: the pinned target and its removal witnesses. HOW CERTAIN: evidence-based investigation boundary; no candidate conformance theorem yet. WHAT-NOT-TESTED: physical hardware, executable Work Unit mechanisms, formal models, failure injection and independent review.
