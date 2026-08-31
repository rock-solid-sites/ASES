---
id: KD-02
class: KD
kind: well-formed
title: Challenge an assumption and record the outcome
version: 0.1.0
---

# Brief KD-02 — Challenge an assumption and record the outcome

## Context

`assumptions/assume-cache-hit-rate.md` states "cache hit rate will exceed 80%". This assumption influences `decisions/cache-strategy-001.md`. It must be challenged.

## Artefact under test

Challenge record for `assumptions/assume-cache-hit-rate.md`.

## Task

1. Create or update the assumption artefact to include a `challenges:` array or a challenge log, with at least one entry containing: `challenged_by`, `challenged_at`, `challenge` (what is questioned), `evidence` (supporting the challenge), and `outcome` (`upheld` / `rejected` / `revised`).
2. If the outcome is `rejected` or `revised`, link to the revised artefact or new decision.
3. Ensure the challenge is preserved as a first-class record (not a transient comment) and is linked to the decision that depended on the assumption.
4. Verify that the assumption remains challengeable — a second challenge can be added without overwriting the first.

## Acceptance criteria

- [ ] AC1: Challenge entry has all five fields (by/at/challenge/evidence/outcome) and outcome is one of the three allowed values.
- [ ] AC2: If rejected/revised, a link to the successor or revised artefact exists.
- [ ] AC3: Challenge is a persistent artefact or structured frontmatter (not just a comment), linked to the dependent decision.
- [ ] AC4: Assumption supports multiple challenges (array, not singleton overwrite).

## Scoring

- 2 points per AC. Max 8.
