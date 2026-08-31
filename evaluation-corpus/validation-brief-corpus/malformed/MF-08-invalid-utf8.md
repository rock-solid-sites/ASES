---
id: MF-08
class: SR
kind: malformed
title: Persist state — invalid UTF-8 sequence (malformed)
version: 0.1.0
---

# Brief MF-08 — Invalid UTF-8 sequence

## Context

Artefact `docs/architecture/decision-012-persistence.md` is in `Active`. State must be explicit and recoverable.

## Task

Persist the artefact's state explicitly in a durable store with the following body that contains an invalid UTF-8 lone surrogate: `valid text \uD800 invalid`.

This brief intentionally contains an invalid UTF-8 sequence (the lone surrogate `\uD800` above) to test encoding detection. A conforming implementation must detect the encoding error and reject the brief, not silently replace or ignore.

_expected_recovery: Detect encoding error, reject_

_why_malformed: Lone surrogates are not valid UTF-8 or Unicode scalar values; they must be rejected._
