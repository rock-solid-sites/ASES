# Session Audit — Stage 2 Classification Summary

**Date:** 2026-07-20
**Total sessions:** 969

## Overall Breakdown

| Category | Count | % | Cost | Events | Action |
|----------|-------|---|------|--------|--------|
| **A — Ephemeral** | 838 | 86.5% | $21.06 | 120,581 | Auto-delete after Stage 5 |
| **B — Productive** | 119 | 12.3% | $152.78 | 69,473 | Audit in Stage 3-4 |
| **C — Needs review** | 12 | 1.2% | $0.49 | 0 | Manual review |

## By Project

| Project | Sessions | A | B | C | Cost |
|---------|----------|---|---|---|------|
| tripn-astro (`9cc6...`) | 526 | 467 | 51 | 8 | $88.48 |
| ASES (`b826...`) | 320 | 297 | 23 | 0 | $66.45 |
| crosslink (`d656...`) | 37 | 18 | 19 | 0 | — |
| AI art (`38bb...`) | 30 | 6 | 20 | 4 | — |
| Dynamic Models (`a5ed...`) | 29 | 24 | 5 | 0 | — |
| global | 25 | 25 | 0 | 0 | — |
| server (`6727...`) | 2 | 1 | 1 | 0 | — |

## Category B Sessions to Audit

### ASES (23 sessions)
High-value orchestrators and research sessions. Includes crosslink onboarding ($31.21), adversarial review cycles, monorepo migration planning, and execution-engine UI research.

### tripn-astro (51 sessions)
Image pipeline work, OG site updates, Canva integration, review page creation, Phase 1-3 reorganization. Includes 8 high-cost orchestrators ($11-$25 range).

### crosslink (19 sessions)
Model-agnostic implementation reviews, crosslink compatibility work.

### AI art (20 sessions)
Bluesky publisher, image pipelines, audit tools, museum PRs.

### Dynamic Models (5 sessions)
Plugin implementation plans.

## Files

- `session-index.csv` — full session metadata with event counts
- `ases-session-classification.csv` / `tripn-session-classification.csv` / `other-session-classification.csv` — per-session classification
- `ases-session-summary.txt` / `tripn-session-summary.txt` / `other-session-summary.txt` — aggregate summaries
