---
id: MF-11
class: KD
kind: malformed
title: Revisit decision — missing provenance for state-modifying decision (malformed)
version: 0.1.0
---

# Brief MF-11 — Missing provenance for state-modifying decision

## Context

`decisions/cache-strategy-001.md` is being revised to `reversed` based on new evidence, but this brief **provides no provenance** — no WHY, no WHAT, no HOW-CERTAIN, no WHAT-NOT-TESTED, and no evidence link.

## Task

Revise the decision to `reversed` without providing any provenance or evidence. A conforming implementation must **enforce the provenance requirement** and block the state-modifying decision until provenance is supplied.

_expected_recovery: Enforce provenance requirement, block_

_why_malformed: Per AGENTS.md Reasoning Certainty, state-modifying claims must state WHY/WHAT/HOW-CERTAIN/WHAT-NOT-TESTED. Missing provenance must block._
