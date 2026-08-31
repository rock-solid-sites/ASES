---
id: MF-10
class: PE
kind: malformed
title: Provenance chain — stale reference to non-existent artefact (malformed)
version: 0.1.0
---

# Brief MF-10 — Stale reference

## Context

Three artefacts form a chain: observation `observations/latency-spike-missing.md` (does not exist) → finding `findings/retry-backoff-finding.md` → decision `docs/architecture/decision-002-retry-policy.md`.

## Task

Build a provenance chain where the first hop references `observations/latency-spike-missing.md`, which **has never existed** in this repository. The system must detect the missing reference and fail the lookup, not fabricate a placeholder.

_expected_recovery: Detect missing reference, fail lookup_

_why_malformed: References to non-existent artefacts must be detected; silent success would hide a provenance gap._
