---
title: Efficiency Architecture Investigation Record
program: EDASES
layer: Architecture
document_type: Design and Reasoning Record
status: Experimental
authority: Derived
canonical_repository: edases
crosslink_issue: 572
baseline_commit: 8d158e3e82d5811e420c80cc6c9664d3ae4a6088
depends_on:
  - EDASES Work Unit Component Design
  - EDASES Execution Engine Roadmap
  - Phase I Processorless Core Falsification
consumed_by:
  - EDASES Efficiency Architecture
  - Efficiency Architecture Discriminating Experiments
related_documents:
  - Efficiency Architecture Evidence Ledger
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-29
---

# Efficiency Architecture investigation record

## Basis and independence

This is an architecture research pass, not methodology, a core amendment, or an implementation plan. Its exact repository basis is Stage-1 commit `8d158e3e82d5811e420c80cc6c9664d3ae4a6088`. The initial Efficiency Architecture is blob `349eee3b51171a9365201eff5d2bd10d8cbfa719`. The research branch starts at that commit; the original document body will remain available in full as historical reasoning when the new synthesis is introduced.

The separate reconciliation `ad24f856a` and its independent review are excluded as settled evidence. Neither its diff nor its conclusions were consulted. Repository tracking state is administrative provenance, not research evidence. This investigation is independent analysis by this session; it is not a claim of independent adversarial verification or a multi-agent consensus.

| Frozen input | Git blob |
| --- | --- |
| `docs/architecture/EDASES-Efficiency-Architecture.md` | `349eee3b51171a9365201eff5d2bd10d8cbfa719` |
| `docs/architecture/EDASES Work Unit Component Design.md` | `22c98dbabdaed7f41d656209a6ce96269dde8390` |
| `docs/architecture/EDASES-Execution-Engine-Roadmap.md` | `a82d8a3fc54fd075fd6a20cf9e64ce560313f87c` |
| `docs/architecture/core-substrate/Phase-I-Processorless-Falsification.md` | `33ff65100cbb10c107337e0f325d1db023e8ffe1` |
| `docs/standards/Documentation Standard.md` | `15c47446695686b19d5e4e67325dd45e0592aa7f` |
| `docs/standards/Concept - Levels of Abstraction.md` | `88c23fe6b43b8249f0b66282b3a8bbfd989016a9` |
| `AGENTS.md` | `4e284d23966bdcb16e6394b715665dc3d4cecff1` |
| `ORIENTATION.md` | `9423fa71597f5a525bfd29378978b6daacbcfc22` |

## Initial observations and discriminating questions

1. The baseline already conditions elimination of derived state on retained inputs, interpretation, observations and deadlines. The research must test those conditions rather than attack an unconditional recomputation claim the baseline does not make.
2. Work Unit A–L distinguishes containment lifetime from execution. A sealed Work Unit can still compute internally under surviving grants. Therefore sealed, dormant, and cheap cannot be treated as synonyms.
3. Phase-I falsification P1 requires trusted guard evaluation or sound verification. Processorless does not mean computation-free or universally untrusted derivation.
4. Phase-I P3/P4 already expose incomplete negative domains and validation/commit races. A cache hit or input hash cannot settle either by itself.
5. Phase-I P6/P8/P9 preserves observations, historical choices and accepted outputs. Derived origin does not imply disposable lifetime.
6. Phase-I P11 names a real reopening condition: a required timing bound plus a defensible recomputation lower bound. A slow benchmark alone cannot establish a new core component.

**WHY:** these distinctions prevent false challenges and prevent efficiency from rewriting the frozen contract. **WHAT:** the frozen documents and sections above. **HOW CERTAIN:** evidence-based textual interpretation. **WHAT-NOT-TESTED:** implementation conformance, acceptance of the frozen core, the separate reconciliation, or any workload performance.

The next analysis asks whether applicability cost dominates reuse; which observations permit lossy reduction; whether maintenance and recovery erase fast-path gains; and which coordination costs can be eliminated without changing required outcomes. Counterexamples and economic models will precede recommendations to build mechanisms.
