---
id: PE-03
class: PE
kind: well-formed
title: Build a multi-hop provenance chain across artefacts
version: 0.1.0
---

# Brief PE-03 — Build a multi-hop provenance chain across artefacts

## Context

Three artefacts form a chain: observation `observations/latency-spike.md` → finding `findings/retry-backoff-finding.md` → decision `docs/architecture/decision-002-retry-policy.md`. The provenance must be queryable as a graph.

## Artefact under test

The provenance graph linking the three artefacts.

## Task

1. Ensure each artefact has explicit provenance links:
   - observation → raw data / log
   - finding → observation (with relationship `derived-from`)
   - decision → finding (with relationship `justified-by`)
2. Represent the chain in a way that a graph query (or simple traversal) can answer "what observations support this decision?" without reading all files.
3. Add a `provenance-chain.md` summary or update the decision's frontmatter with a `provenance_chain: [id1, id2, id3]` ordered list.
4. Verify no link is broken — every referenced ID/path exists.

## Acceptance criteria

- [ ] AC1: All three artefacts have typed provenance links (derived-from / justified-by at minimum).
- [ ] AC2: A single chain summary exists (file or frontmatter) that orders the hops.
- [ ] AC3: Chain is machine-traversable (JSON array, graph edge, or indexed relationship).
- [ ] AC4: No dangling references — every ID/path in the chain resolves to an existing artefact.

## Scoring

- 2 points per AC. Max 8.
