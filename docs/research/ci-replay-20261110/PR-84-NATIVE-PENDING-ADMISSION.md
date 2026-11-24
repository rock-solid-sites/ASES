---
title: PR #84 native pending-admission CI replay
version: 0.1.0
program: ASES
layer: Research
document_type: CI Replay Note
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-24
---

# PR #84 native pending-admission CI replay

## Existing hosted coverage at the pinned source

PR #84 head `bfabf1d95a1f51052679ff4855a2ccc147b97584` is based on the pinned PR #43 source `e91fb4b14875487dee9c19cc764e72655ba534c0`. At the time of this inspection, GitHub Actions reported no workflow runs and no combined status for that exact head. The workflow inventory at the pinned head contains `phase-i-independent-replay.yml`, but its cases cover earlier Phase I slices and do not run the native pending-admission probe or the #35/#36 parent histories. The committed local evidence is not itself a hosted CI run.

## Replay

`.github/workflows/native-pending-admission-replay.yml` checks out the exact #84 source SHA into a separate `source` directory on `ubuntu-24.04` with Python 3.12, `contents: read`, and checkout credentials disabled. It runs:

- `python3 docs/research/phase-ii-native-pending-admission/verify_probe.py <fresh-output>` — A1–A6, including repeated-B and distinct-owner controls plus A5 reconciliation, current-authority admission and exact accepted-A replay.
- `python3 docs/research/phase-ii-native-local-observation/probe.py --out <fresh-output>` — A7 local-observation and nested #35/#36 publication-reconciliation histories.

Each history has a 900-second timeout; the job has a 40-minute timeout and runs sequentially. The workflow records runner, Python/SQLite, CPU count, commit SHAs, source hashes, exit status and elapsed seconds. It retains raw outputs and logs as a 30-day GitHub Actions artifact. No secrets, container privileges or external provider are needed by these source-bound histories.

## Scope limits

This replay covers PR #84's A1–A7 native admission packet and its named recovery regressions. It does not cover the Rust candidates, the UID/container custody candidate, all WNASES-6 slices, or establish broader security or production guarantees. Workflow source and a local pass do not prove hosted execution; only the linked GitHub Actions run and its artifact do.
