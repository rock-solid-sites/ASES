---
title: "Doll Corpus Extraction Method — Gates 0-10 + Resilience Checklist"
tags: ["doll-corpus", "extraction", "gates", "lexicon", "resilience", "atproto"]
sources: ["docs/research/doll-corpus-retrospective.md", ".design/doll-corpus-extraction.md"]
contributors: ["ASES"]
created: 2026-08-27
updated: 2026-08-27
---

# Doll Corpus Extraction Method — Gates 0-10 + Resilience Checklist

## Summary

Source **19,932 posts** collected from **21,413 scanned** via unauthenticated ATProto AppView; **Gates 0-10 funnel** (mechanical Gates 0-4 deterministic, interpretive Gates 5-10 curated); **strict local git** — raw/normalized/state/corpus/derived/__pycache__ gitignored, derived bulk disk-only; **no LLM in Gate 1** — lexical eligibility is pure normalization + vocab match before any model spend. Vocab hash `d8cca707` after `doll` alias strip; word-boundary enforcement for len≤3.

## Gates 0-10

| Gate | Name | Input → Output | STOP? |
|------|------|----------------|-------|
| 0 | **Probe & Scope** | question → AppView capability + filter behaviour | **STOP** if probe fails — no collection |
| 1 | **Collect** | AppView pages → raw posts (atomic writes + cursor) | Resume-from-cursor; RSS <500 MB; streaming `jsonl_stream` |
| 2 | **Lexical eligibility** | raw → lexically eligible (vocab `d8cca707`) | **STOP** if quality gate FAIL; **no LLM** |
| 3 | **Contextual eligibility** | lexical → contextual (co-occurrence / anchoring) | Filter low-only, rescue anchored |
| 4 | **Thread expansion** | contextual posts → threads (primary unit) | Threads carry context downstream |
| 5 | **Decisions** | threads → decisions (10 in Doll run) | Human/LLM curation with evidence links |
| 6 | **Eras / URIs** | decisions+threads → eras + URI sets (5 eras / 29 URIs) | Era bounds explicit |
| 7 | **Facets / Evidence** | eras → facets + evidence (16 / 72) | Facet→evidence traceability |
| 8 | **Research Questions** | facets → RQs prioritised (16, P0 5) | P0 = must-answer |
| 9 | **Finals — draft** | RQs → draft deliverables | Linked to RQs |
| 10 | **Finals — release** | drafts → released finals (4) | Gate close requires termination-path verification |

Gates 0-4 mechanical, Gates 5-10 interpretive. Do not reorder; do not merge.

**Observed funnel:** 21,413 scanned → 19,932 collected → 2,326 lexical (4,392 pre-`doll`-strip) → 509 contextual (460 high + 49 rescued) → 284 threads → 1,251 posts (avg 4.4/thread) → 10 decisions → 5 eras/29 URIs → 16 facets/72 evidence → 16 RQs (P0 5) → 4 finals.

Mnemonic: `21k → 20k → 2.3k → 509 → 284 (1,251) → 10 → 5/29 → 16/72 → 16(5) → 4`.

## Lexical Vocab

| Group | Specificity | n | Terms |
|-------|-------------|---|-------|
| **L1** primary lineage | **high** | 14 | beads, bead, chainlink, crosslink, VDD, VSDD, verified design docs, verified spec docs, spec driven, spec-driven, verification-driven, VDD-IAR, VSDD-IAR, IAR |
| **L2** methodology | low | 27 | agent memory, agentic, multi-agent, multi agent, coordination, orchestrator, orchestration, swarm, kickoff, worktree, lock, locks, heartbeat, stale, recovery, handoff, session, context, token, tokens, context window, tracker, issue tracker, issue tracking, adversarial, adversary, builder |
| **L3** architecture | low | 12 | SQLite, JSONL, Git, source of truth, ADR, lifecycle, execution engine, statechart, XState, property graph, provenance, supersession |
| **L4** cost/failure | low | 12 | cost, failure, burn, budget, rate limit, 429, earlyoom, OOM, memory pressure, retry, retries, crash |
| **L5** authority | low | 6 | steveyegge, yegge, gas town hall, forecast bio *(+2 alias variants; strip `doll` alias — 2,585 FP hits)* |
| **L6** Gas Town | **high** | 7 | gas town, gastown, gas-city, gas city, gas city divergence, gastownhall, gas town hall |

Plus **known_refs** (6, always eligible): `github.com/dollspace-gay/chainlink`, `github.com/forecast-bio/crosslink`, `github.com/gastownhall/beads`, `github.com/steveyegge/beads`, `gist.github.com`, `leaflet.pub`. Total canonical 76 + 6 = 82 entries; vocab hash `d8cca707` (prefix of `d8cca707fbaf7749…`) **after** `doll` alias strip (pre-strip 4,392; post-strip 2,326).

**Normalization:** NFKC → lowercase → `isalnum` filter (`[^\p{L}\p{N}]+` → single space), trim/collapse. Matching is substring `nterm in normalized_text` EXCEPT len≤3 requires word-boundary: `f" {nterm} " in f" {text} "` (or `\b` regex). Affected: `IAR`, `Git`, `OOM`, `lock` (L2), plus `VDD`, `ADR`, `429` — fixes `IAR↔familiar/liar`, `Git↔legitimate/digit`, `OOM↔room/bloom`, `lock↔block`. 649 false positives eliminated by this rule in Gate 3.

## Quality Gate (Gate 2)

`n=120`, seed `49102`, stratified **40 / 40 / 40** = high-only (L1/L6) / low-only (L2-L5) / mixed + 40 unmatched recall probe (160 rows total, 120 primary for precision). Human inspection simulation, no LLM.

| Precision | Action |
|-----------|--------|
| ≥ 0.85 | PASS — proceed to Gate 3 |
| 0.65–0.84 | **CONDITIONAL** — tighten Gate 3 co-occurrence, proceed, re-audit after Gate 3 |
| < 0.65 | FAIL — rerun Gate 1 with vocab pruning |

Doll run observed **0.658 overall** (79/120, borderline half-weight; 95% CI 0.57-0.74) → **CONDITIONAL PASS**. Action taken: did not rerun Gate 1 / prune; enforced `IAR`/`bead`-alone requires second L1/L6 term or thread anchoring; `Git`/`OOM`/`lock`/`token` alone must satisfy both co-occurrence and thread check on first Gate 3 pass, then relax after re-audit.

Artifacts: `research/doll-corpus/derived/gate2/quality-report.md`, `samples.jsonl` (160 rows), `sample.json` (120 primary).

## Contextual Eligibility (Gate 3)

- **High (L1/L6) presumptive** → retained automatically (460 after word-boundary).
- **Low (L2-L5) only if** ANY of:
  1. **N=50 co-occurrence** — high term within 50-token window in same post (rescued 0 in Doll run — expected, low-only posts have no high in-post);
  2. **Thread anchoring** — post's `thread_root` URI in `threads_with_high` (362 threads-with-high → **49 rescued**, 1,168 not anchored → discarded);
  3. **Explicit URL/marker** — known_ref URL or marker (`beads->chainlink`, `chainlink->crosslink`, `gas town divergence`, `VDD_adjacent_chainlink_within_20` within 20 tokens) (rescued 0).

Retained 509 = 460 high + 49 low-anchored; discarded 1,817 (649 short-term FP + 1,168 low-no-context). See `derived/gate3/rules.json` and `stats.json`.

## Resilience Checklist — 7 Points (copy verbatim before Gate 1)

- [ ] **< 2 m checkpoint + 45 s heartbeat** — state flushed every <2 min; liveness file updated every 45 s; visible output so heartbeat disambiguates busy vs stalled (survived Observer pane-hash false positives `pp3g-qlIC` failed / `pp3g-lGBq` succeeded + `b2N7` rtk-git loop; `earlyoom` SIGTERM 05:58 PID 704).
- [ ] **Streaming `jsonl_stream` RSS < 500 MB** — never hold full corpus in memory; stream pages to disk (streaming kept 21k corpus alive on memory-constrained host; `earlyoom` at 3.4/3.9 GB swap still recoverable via atomic writes).
- [ ] **Strict `.gitignore`** — `raw/`, `normalized/`, `state/`, `corpus/`, `derived/`, `__pycache__/` ignored (`/derived/` anchored, not bare `derived` — verify with `git check-ignore -v -- <path>`); derived bulk disk-only, never staged (prevents 5 GB commits; exception tracked: over-eager `derived/` hid `extraction/`).
- [ ] **Model fallback wired** — `muse-spark` free → `hy3-free` → `muse-spark` Go (wired via harness, unused in Doll run but required as insurance).
- [ ] **Filter probe one-page both filters (68/100 gap)** — Gate 0 probe before any collection: assert filter name/params, expected vs observed pass-through gap (68/100 gap observed), fallback `posts_with_replies`, exact-match `postsCount 14,333`; without probe, 205 pages would be collected under wrong filter.
- [ ] **Word-boundary len≤3** — `IAR`/`Git`/`OOM`/`lock` etc require `\b` / padded-space match; test with substring probes (`IAR` must not match `familiar`).
- [ ] **Alias strip for third-person self-reference** — enumerate every alias; strip/demote aliases colliding with common English (`doll` stripped: 4,392 → 2,326, −2,585); report pre- and post-strip counts. Swarm vs sequential: Observer Swarm v1.1 singleton guard rejects second swarm — default to sequential `kickoff`s until lifted.

## Archiving

5 GB sessions: use `tar`, not `7zip` (7zip not guaranteed, poor streaming):

```bash
tar cJf archive.tar.xz <dir>
tar --zstd -19 --long -cf archive.tar.zst <dir>   # or tar -I 'zstd --long' -cf
```

`xz`/`zstd --long` are universally available and stream without holding full archive in memory.

## Links

- Design: `.design/doll-corpus-extraction.md` (template + extraction/lib trio: collector / lexicon / threader)
- Retrospective: `docs/research/doll-corpus-retrospective.md` (full §1-§9, reusable method + funnel)
- Derived: `research/doll-corpus/derived/gate1/` (vocab.json hash `d8cca707`, stats.json, candidates.jsonl) · `gate2/` (quality-report.md, samples.jsonl) · `gate3/` (rules.json, stats.json, contextual-candidates.jsonl) · `gate4/`-`gate10/` (threads → finals)
- Issues: #491 (Doll Corpus extraction), #471 (related)
- Cross-ref: `.crosslink/knowledge/agent-orchestration-playbook.md` §5.8 (workflow topology), `docs/research/Workflow Topology Design and Reasoning Record.md`

## Quick Lookup

| Need | Value |
|------|-------|
| Vocab hash | `d8cca707` (after doll strip) |
| Normalization | NFKC lower + isalnum punct→space |
| Short-token rule | word-boundary if len≤3 |
| Quality seed | 49102, n=120 40/40/40 |
| Thresholds | 0.85 pass / 0.65 conditional / <0.65 fail |
| Thread anchoring | N=50 window; 362 threads-with-high → 49 rescued |
| Checkpoint | <2 m; heartbeat 45 s |
| RSS cap | <500 MB streaming |
| Archiver | tar xz / zstd --long |
