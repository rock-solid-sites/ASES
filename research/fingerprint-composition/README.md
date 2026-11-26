---
title: Fingerprint dataset composition field trial
program: ASES
layer: Research
document_type: Research Protocol
status: Experimental
authority: Experimental
canonical_repository: ases
related_documents:
  - docs/research/kernel-0/One-handover-across-resource-owners.md
  - docs/methodology/ASES Task-Scoped Information and Handoff Method.md
last_updated: 2026-11-26
---

# Fingerprint dataset composition field trial

Purpose: investigate useful upstream collaboration among existing open technology-detection projects while testing ASES multi-source investigation and composition methods. No new maintained product, mandatory common registry or predetermined merger. Keep domain findings and methodology findings distinct. Research questions and experimental methods may evolve with evidence.

## Initial evidence and competing composition policies

- [Enthec #189](https://github.com/enthec/webappanalyzer/issues/189) and [HTTP Archive #52](https://github.com/HTTPArchive/wappalyzer/issues/52): proposed repository unification; maintainers' compatibility, maintenance and scope concerns; exchange of improvements remains a separate question. Enthec's public statements describe backward compatibility, validation, automation and language-specific implementations. Distinguish intentions from demonstrated activity.
- [Enthec #75](https://github.com/enthec/webappanalyzer/issues/75), [#223](https://github.com/enthec/webappanalyzer/issues/223): schema inconsistencies and reported selector/array interpretation problems. Reproduce; do not assume reporter's engine or defect is established.
- [HTTP Archive #33](https://github.com/HTTPArchive/wappalyzer/issues/33), [#70](https://github.com/HTTPArchive/wappalyzer/issues/70): prioritization and automated updates; distinguish absence of detection from obsolescence.
- [WappalyzerGo updater](https://github.com/projectdiscovery/wappalyzergo/blob/305f999a80e22863971870b7a56ac479651715c6/cmd/update-fingerprints/main.go): source read at HEAD; sequential Enthec then HTTP Archive shards, assignment by technology name replaces whole overlapping record, then normalization. Certain fields absent from typed output. Lowercases several regex-bearing fields. Candidate loss/semantic changes require tests.
- [wappalyzer-pure synchronizer](https://github.com/jakubkoje/wappalyzerpy/blob/130567cdf369087c6bd75a641795341f37eb678e/src/wappalyzer_pure/sync_data.py): normalizes separately, merges mappings recursively, lists via serialized equality deduplication, nonempty scalar conflicts prefer Enthec. Fetches commit metadata after reading mutable ref; test snapshot consistency. Not evidence of semantic equivalence.
- [OpenTechalyzer importer](https://github.com/Houseofmvps/opentechalyzer/blob/a3d30e479c91c06732ef88867d69b7feef8f3f35/src/fingerprints/external.ts) and [index](https://github.com/Houseofmvps/opentechalyzer/blob/a3d30e479c91c06732ef88867d69b7feef8f3f35/src/fingerprints/index.ts): built-ins replace imported records by case-folded name. Importer retains first array value for map patterns, reduces DOM object to selector keys, strips relationship confidence metadata and maps script-body and script-URL patterns into scriptSrc. Partial shard failures may be skipped; distinguish intentionally unsupported signals from defects. Built-in MIT and optional GPL data must remain legally separable.
- [Smudged Fingerprints](https://www.usenix.org/publications/loginonline/understanding-and-improving-web-application-fingerprinting-wasabo): controlled versus real-world accuracy and version ambiguity; inspect paper and available artifacts.
- Further corpus: ZAP parser and downstream discussions, BBOT #1245, ProjectDiscovery PR #70, Wappalyzer-next, HTTP Archive forum and research. Confirm claims from original sources, including disagreements and any later resolution. No assumption of maintainer consent.

## Initial source snapshot candidates

Commit IDs returned by GitHub commits/HEAD on 2026-11-26 (re-fetch immutable files and verify hashes before runs; source inspection above used HEAD, not a proven identical snapshot):

| Repository | Commit |
|---|---|
| enthec/webappanalyzer | 7dba7bf3e8b4f25c6a5b4b2c9f5e7a0e73e6a1bf |
| HTTPArchive/wappalyzer | 35b0847c01c118055c42596d5c6d01f60f15d706 |
| Houseofmvps/opentechalyzer | a3d30e479c91c06732ef88867d69b7feef8f3f35 |
| projectdiscovery/wappalyzergo | 305f999a80e22863971870b7a56ac479651715c6 |
| jakubkoje/wappalyzerpy | 130567cdf369087c6bd75a641795341f37eb678e |

## Initial research transitions

1. Independently map public prior work and maintainer positions. Register claims, source, date, unresolved disputes, existing implementations and what has not been tested. Review existing ASES multi-donor and hylomorphic research before finalizing methodology experiment; do not invent findings.
2. Pin all inputs and establish native baselines. Inventory identifiers, aliases, field capabilities, raw vs normalized changes, provenance and license boundaries. Mechanically compare exact matches, conflicts and unique information, not just name counts.
3. Reproduce existing composition policies before proposing new ones. Test whole-record overwrite, recursive merge, name case-folding and import conversions; isolate representation vs engine semantics. Build minimal positive and negative fixtures for selectors, multiple patterns, version capture, confidence, relationships, duplicate signals, unsupported capabilities and missing input shards. Measure order-dependence and loss, without assuming associativity, commutativity or idempotence are appropriate for all policies.
4. Compare native and composite behavior on identical controlled observations and appropriately labeled held-out examples. Separate parser success from detection correctness, false positives from misses, inability to observe from negative evidence. Benchmark only where justified; preserve counterexamples. Historical replay and broader live validation require source access, licensing and bounded network/cost controls.
5. Compare mechanical structural analysis, independent agent investigation and hybrid research on predeclared tasks with ground truth and blind verification. Record source coverage, evidence errors, time/usage where measurable and unknowns. Do not conflate semantic accuracy with research agent performance.
6. Synthesize reproducible upstream recommendations and ASES observations; no upstream posting or adoption without review. Retain negative results.

## Execution and evidence

Persistent, replaceable orchestrator controls dynamic bounded workers; no calendar or fixed concurrency. Parallelize independent questions; sequence dependent checks. Publish source manifests, experiments and evidence here on main, explicitly experimental. Disposable isolated workspaces; short recoverable remote checkpoints; verify publication. Work Notes WNASES-33 holds operational position; Projektor ASES-26 holds human scope. No paid inference fallback, no unverified resource entitlement, no secrets or private chats in public artifacts. Actual host, launcher, model and billing verification remain prerequisites to dispatch. No agents launched or runtime tests performed yet. Initial observations are source inspection, not verified runtime findings.
