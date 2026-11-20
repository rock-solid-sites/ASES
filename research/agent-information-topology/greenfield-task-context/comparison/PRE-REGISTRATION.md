---
title: Preregistered Three-Format Task-Context Comparison
program: ASES
layer: Research
document_type: Research Protocol
status: Experimental
authority: Experimental
canonical_repository: ases
last_updated: 2026-11-20
---

# WNASES-22: preregistered non-model comparison

## Question

Does a persistent typed task-context graph materially outperform (A) a compact manually written task packet or (B) a lightweight structured packet for *the same* bounded task and source facts, without introducing more authoring/storage overhead?

## Design frozen before constructing packets

Compare **three formats** for each of **two synthetic tasks**:

- **T1: simple documentation revision** — one applicable document-quality rule, one evidence record, no override, no model invocation. Distractor: an unrelated marketing rule/source.
- **T2: multi-source instruction decision** — two upstream rules, a project-scoped approved complete replacement of one rule, uncertain evidence, a reviewer handoff and no model invocation. Distractors: an unrelated task rule and a *stale experimental* research note that must not become an authoritative instruction.

Formats:

- **A — manually authored compact prose:** an operator's short task brief with relevant explicit references; no imposed schema.
- **B — lightweight structured packet:** headings and inline source references, without a persistent graph or resolver.
- **C — typed-graph view:** assembled mechanically from a synthetic graph and a deterministic, test-only resolver; includes a separate receipt. No service, database, hosted model or actual launch.

**Equal access:** all three are authored from the same committed `cases.json` and same identified expected facts. Do not seed A/B with intentionally wrong instructions or hide needed facts; the graph should not win by design. Do not count the fixture's deliberately included irrelevant source text as present in a packet unless its body is included. All formats may use direct references rather than reprinting entire source documents.

## Mechanical scoring and hard gates

For each case and format, evaluate the final *effective content plus displayed source references* for:

1. **Completeness:** all task-required observable markers and explicit decision/authority details present. Full marks only when all are present.
2. **Contamination:** no distractor markers, stale-research promotions, or superseded rule bodies occur in the delivered task view.
3. **Provenance:** source IDs with exact fixture revisions, evidence IDs/certainty/WHAT-NOT-TESTED, and override decision ID where applicable. A graph's receipt does not receive bonus marks just for being separate.
4. **Scope and route safety:** exact task ID, output and durable evidence destination; no model launch authorization, no fallback and no substituted provider.
5. **Context size:** UTF-8 bytes and line count of delivered packet, excluding source/benchmark definition files. **Not equivalent to exact tokenizer count**.
6. **Maintenance complexity:** count number of separately maintained *format-specific* persisted artifacts and manual edit requirements. This is qualitative; **do not invent authoring time, token cost, latency, retrieval cost or user effort**. Where a format creates a reusable renderer, report this additional dependency explicitly.

Acceptability thresholds: 100% required markers, 100% exact source-reference checks, zero forbidden markers, zero missing safety restrictions, and an explicit recorded unresolved status for any unsupported input. A failure in any critical gate means "not ready for dispatch," regardless of shorter size.

For a preliminary *architecture preference*, if A or B ties C on all correctness gates and has no material evidence loss, prefer the simpler non-persistent format unless C demonstrates useful additional protection against a negative mutation or a documented recurring manual mistake. No performance claims about an actual LLM can be drawn from these static tests.

## Negative controls

- Missing or duplicate rule ID; dangling source/edge; wrong source authority.
- Absent/revoked or cross-task override; two conflicting overrides for one rule.
- Superseded text present in the effective view; stale experimental evidence elevated to a rule.
- Irrelevant source included in the packet.
- Source revision mismatch, absent uncertainty disclosure, missing output/evidence destination, and accidental model-route authorization.

Expected result: flag or block, never reinterpret the error as a reason to auto-import old root instruction files.

## Reporting requirements and limitations

Report a **2×3 result table**, a compact list of negative-test outcomes, raw machine outputs and exact branch/commit/Actions run. Keep *measured* facts distinct from interpretation, and record that all artifacts were authored by one coordinator using synthetic, hand-constructed examples.

**No Luna execution is queued.** WNASES-18 is an unlaunched proposed Codex independent pilot; this comparison is fully independent of it. WNASES-19/OpenCode exposure remains a separate incomplete investigation. Neither is needed for an offline first pass.

No existing `AGENTS.md`, `SESSION-START.md`, active skills or production repository is modified. No model, gateway, API wallet, paid/free entitlement or provider test is launched.
