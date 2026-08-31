---
id: KD-04
class: KD
kind: well-formed
title: Revisit a prior decision with new evidence and update provenance
version: 0.1.0
---

# Brief KD-04 — Revisit a prior decision with new evidence and update provenance

## Context

`decisions/cache-strategy-001.md` was made on 2026-08-15. On 2026-08-31, a new benchmark shows the chosen strategy degrades under concurrent load. The decision must be revisited without losing history.

## Artefact under test

Revisit of `decisions/cache-strategy-001.md`.

## Task

1. Add a revisit record to the decision (frontmatter `revisited_at: 2026-08-31`, `revisited_by`, `new_evidence:`) or create a new artefact `decisions/cache-strategy-001-revisit.md` that supersedes the original.
2. The revisit must state: what new evidence emerged, how it changes the trade-off, and whether the decision is `upheld`, `revised`, or `reversed`.
3. Preserve the original decision's provenance — do not overwrite it; append the revisit as a new provenance entry or new version.
4. Update traceability so an auditor can see both the original and revisit chains.

## Acceptance criteria

- [ ] AC1: Revisit record exists with revisited_at/by, new evidence, and verdict (upheld/revised/reversed) — one of the three.
- [ ] AC2: Original decision's history is preserved (not overwritten); revisit is additive.
- [ ] AC3: Trade-off is re-evaluated in light of new evidence (not just "new data").
- [ ] AC4: Traceability reflects both original and revisit (auditor can see both).

## Scoring

- 2 points per AC. Max 8.
