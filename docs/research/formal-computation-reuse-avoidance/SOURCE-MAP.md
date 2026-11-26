---
title: Formal Computation — source map and initial reconciliation
program: EDASES
layer: Research
document_type: Research Source Map
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-26
---

# Earlier work and current evidence

Initial reconciliation, not a complete transcript audit. The distinction between a research lead, proposed mechanism, measured result and adopted method is essential. Private archive pointers are in WNASES-32, not public transcript copies.

## Earlier questions recovered

| Study | Surviving question | Status |
| --- | --- | --- |
| Universal Caching & Computation Reuse / Unified Caching Model | Can reusable verifiable artifacts avoid repeated work across domains? Candidate identity: input + environment + transformation + evidence. Reconcile domain-specific rules before common primitives. | August/September discussion and catalog evidence; full source review pending; no adopted universal cache |
| Merkle Schemes | Can content-addressed recursive structures support precise identity, sharing and demand-driven evaluation? | Research idea; operator confirmed no actual work as of Nov 12 |
| Transitive Frontier | Can changed dependencies define the minimum affected computation boundary? | Research idea; operator confirmed no actual work as of Nov 12 |
| AST Efficiency | What structural results can be retained or incrementally derived? | Archive entry located; distinguish from actual CodeGraph measurements |
| Tidepool Dive | Can typed IR, composed effects, optimization and compilation share verifiable intermediate results? | Archived investigation; source/benchmark claims and applicability need verification |
| ExoMonad | What can composable typed execution contribute to reusable computation? | Archived investigation; no established ASES adoption |
| Typed Effects, Constraints & Compiled Execution | Can domain-specific representations and explicit effects make composition and verification easier? | Earlier research cluster, source reconciliation pending |
| Inference/context reuse | Which input/context transformations preserve reusable inference work and at what correctness cost? | Prior CLM/partial-cache discussions; external performance claims require source verification |

Earlier discussion sources are not represented as publicly available or independently audited. Confirm exact archive provenance and recover prior reasoning before claiming novelty or completed experiments.

## Verified repository evidence and research transfer

| Evidence | Observation | Limitation / implication |
| --- | --- | --- |
| [CodeGraph historical reconciliation](../../proposals/2026-11-02-testing-debugging-ontology/cgrmcp-engine-scope-migration-results-2026-11-03.md#local-reconciliation-historical-indexing-identity-and-continuity-research-2026-11-26) (blob cf1a5f23a72373d62155d240ea3a2a90e37679ba) | Two corrected 7/7 synthetic TS comparisons; changed-case medians 0.53 vs 0.82 s and 0.64 vs 1.02 s. Cross-checkout seed + sync 0.693 vs 1.01 s. | Same-engine clean comparison not independent semantic proof. CLI truncation initially produced false discrepancy. |
| Same historical source, real-source controls | Go fzf seeded 1.6.0 graph had 14 missing contains edges vs two agreeing clean builds. Scoped 1.6.2/extraction 27 controls passed. | Preserve actual negative result; version, extraction and dependency identities matter. No general incremental correctness claim. |
| Same historical source, repeated optimization | 15 alternating trials: 866 vs 1,116 ms median index work, 7.89 vs 8.77 MiB unique allocated storage; 6.48 vs 6.46 s total MCP test. | Local computation reduction did not imply end-to-end speedup. Old service retired; no migration reopening. |
| [Current CodeGraph revision selection](../../proposals/2026-11-26-codegraph-revision-selection.md) (blob 0f380de124ae26d4d0072db4def1dee587974243) | Verified same resolved commit reused across tag/SHA and branch/default alias. Cache key includes repository/resolved commit/producer version/platform. | Whole-index identity, not proof of partial or semantic cross-commit reuse. Active route owner unchanged. |
| [Kernel-0 shared handover](../kernel-0/One-handover-across-resource-owners.md) (blob 4910c60f13992714114d7effc8020623206583e6) | Exact finite one-replacement witness agreed with permutation oracle on 100,800 cases; 2,304 pass separate local witnesses but fail combined. | Local correctness insufficient; shared eligibility is a cross-component constraint. Bound excludes multi-resource reads, shared capacity and other global constraints. |
| [Comparative implementation proposal](../Comparative%20Implementation%20Research%20and%20Upstream%20Contribution%20Proposal%202026-11-25.md) ([composition extension commit](https://github.com/rock-solid-sites/ASES/commit/ca8205670540e80e34c32bc05c28b9ffc2a7df4b)) and [T03](https://github.com/rock-solid-sites/extensions-comparative/blob/main/results/2026-11-26-t03-composed-slot.md) | Native 16/16 + 12/12; composed 4/4 including duplicate-effect oracle control. | Synthetic effect/transport/storage; no full HTTP/auth, real provider acceptance, full persistence or exactly-once proof. Existing owner work WNCHATWS-4 is not duplicated. |
| [State-Model Applicability and Reuse Method](../../methodology/State-Model%20Applicability%20and%20Reuse%20Method.md) (blob b2d972fa56f0548da3e954b4e1c05ebf2f4ff32a) | Existing active method already selects model suitability and transferable verification mechanisms. | Related governing source, not adopted universal formal computation methodology. |

## Synthesis: hypotheses, not conclusions

An artifact identity is evidence of sameness only relative to a specified transformation and relevant environment. A cache hit can be invalid if a semantic dependency is omitted. Equality of outputs may be adequate for a particular observation but not for effect authority, freshness or provenance. Validation can cost more than rerunning. Separate dependency completeness, result validity, permission to reuse, and measured benefit. Composition adds compatibility of assumptions, shared effects/constraints and evidence boundaries; component proofs do not automatically combine. Avoid building a generic mechanism before characterizing these conditions in each domain.

## Next bounded study

Recover the Unified Caching Model source and the August domain inventory; identify the intended guarantees and open questions, then reconcile AST Efficiency with the existing CodeGraph observations. Compare a candidate formal description of the already recorded incremental-vs-clean test, including the Go negative case, with its ordinary description. Investigate whether it clarifies a validity condition, needed dependency or falsifying test before proposing new execution. Kernel-0 and comparative composition are parallel evidence sources, not duplicated tasks.

Primary literature leads for later verification: Meijer/Fokkinga/Paterson on recursion schemes; Hinze/Wu/Gibbons on structured recursion; typed embedded DSLs/tagless-final; Foster et al. on lawful bidirectional transformations. Literature review not yet completed.
