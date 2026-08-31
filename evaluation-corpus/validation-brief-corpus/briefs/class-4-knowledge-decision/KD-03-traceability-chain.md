---
id: KD-03
class: KD
kind: well-formed
title: Trace a decision back through findings, evidence, and observations
version: 0.1.0
---

# Brief KD-03 — Trace a decision back through findings, evidence, and observations

## Context

Given `decisions/cache-strategy-001.md`, an auditor wants to answer: "Why was this decision made? What evidence supported it? Which assumptions influenced it?"

## Artefact under test

Traceability for `decisions/cache-strategy-001.md`.

## Task

1. Starting from the decision, traverse: decision → findings → evidence → observations → raw data/logs. Ensure each hop has an explicit typed link.
2. Produce a `traceability-report.md` or update the decision's frontmatter with a `traceability:` block that lists the chain with IDs/paths per hop.
3. For each hop, state the relationship type (e.g., `justified-by`, `derived-from`, `supports`, `observed-in`).
4. Verify the chain is complete: every finding cited has evidence, every evidence has a source, and no link is broken.

## Acceptance criteria

- [ ] AC1: Report/block lists the full chain with IDs/paths per hop (decision → finding → evidence → observation).
- [ ] AC2: Each hop has a typed relationship (not generic "related").
- [ ] AC3: Chain is machine-readable (structured list, not only prose) and auditable.
- [ ] AC4: No broken links — every referenced ID/path exists and resolves.

## Scoring

- 2 points per AC. Max 8.
