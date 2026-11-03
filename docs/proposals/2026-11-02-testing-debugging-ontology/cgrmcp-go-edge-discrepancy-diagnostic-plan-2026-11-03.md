---
date: 2026-11-03
type: preregistered follow-up discrimination
status: diagnostic plan, before new diagnostic CI
parent: cgrmcp-index-seed-real-repos-crash-preregistration-2026-11-03.md
---
# Go fzf edge-count discrepancy — prediagnostic hypotheses

The **first** real-source matrix [run 41701139522](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41701139522) found a substantive discrepancy for pinned `junegunn/fzf` commit `99bfd5aa0f66133d7dcfbf18f8044eb765f04649`: both seeded and clean indexes contained 116 indexed files, 2,925 nodes, the same kinds/languages and extraction version, yet the seeded index had **13,091** edges versus the clean build's **13,105** (14 fewer). This is a **FAIL**, not a speedup or inconclusive successful test. The earlier TypeScript and Rust cases passed triplicate comparisons. Their success does not excuse the Go discrepancy.

## Competing explanations, selected cheapest tests

- **G1, incremental-specific lost edges:** two independently fresh indexes produce the same edge multiset, while the seeded `sync` index reproducibly lacks certain source/target relationships. Test using an independently repeated clean build and canonical SQL edge-multiset diff; if supported, do not promote index reuse for Go.
- **G2, nondeterministic upstream resolution:** two clean builds of the identical pinned source also disagree on relationships, perhaps under concurrent resolver scheduling. Compare full canonical edge multisets for **clean A versus clean B**, then compare seeded against both; record exact mismatching relationship fingerprints.
- **G3, comparison instrumentation defect:** 14 edges differ only because paths, generated IDs, metadata or timestamps are treated as semantically meaningful. Canonicalize using `edges.kind`, source/target node qualified names + file paths + kinds and relationship coordinates. Treat duplicate rows as **multiset counts**, never deduplicate away evidence. Compare edge counts before normalizing.
- **G4, real regression in changed dependencies:** the SQL multiset isolates a small group of caller/reference edges in changed Go files; use direct source facts and exact full CLI callers/calIees as cross-check before deciding whether CodeGraph `sync` itself is responsible.

Use **CodeGraph 1.6.0** unchanged, the same real immutable revisions, and same GitHub CI runner type. One clean-twin/seed triplet is the initial cheap test, not a statistical conclusion. Print only a bounded sample of edge differences and categories, but retain complete result counts. If SQLite schema is incompatible, record BLOCKED and inspect `PRAGMA table_info`; never silently upgrade or patch CodeGraph itself. Query limits must be explicit due to upstream caller-list truncation. Preserve existing failing run.

**Decision constraint:** zero tolerance for unexplained graph differences. Real-source parity must remain a failing gate even if median timing is favorable. No production use, no code-merge or ASES-wide Processor semantics follow from this diagnostic.
