---
title: Round 25 — Work Unit authority, native admission and custody evidence
version: 1.0.0
program: ASES
layer: Research
document_type: Experimental Research Evidence
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-25
---

# Round 25 research record

This record is classified under the Astra follow-up and preserves source-pinned experimental results. It does not change implementation or declare an authority owner.

## Decision packet

[Work Unit Authority vs. Rust Custody](WORK-UNIT-AUTHORITY-RUST-CUSTODY.md) was authored in a MiMo session and revised after a separate fixed-head Go DeepSeek review. DeepSeek explicitly accepted the final packet and citation corrections; receipts are in [packet acceptance](review/DEEPSEEK-PACKET-ACCEPTANCE.md) and [citation acceptance](review/DEEPSEEK-CITATION-ACCEPTANCE.md).

The decision remains bounded: PR #42 is cost/launch custody only; PR #38 is a candidate authority-side source, not an established Work Unit owner; W5/W6 remain **NOT REPRESENTED**; owner selection is unresolved pending a durable W/P crosswalk and owner-authenticated X/Y eligibility evidence. No implementation is proposed here.

Pins: PR #42 `27bcc552cecb8bbb456b9db3a0a77da1513b31ab`; PR #83 `8de559c78272bf639a82d284572e218a14cc1269`; PR #38 `0bd51a34700164a5eb77efe98158fa37d1a74e23`; PR #84 test base `bfabf1d95a1f51052679ff4855a2ccc147b97584`; test-only follow-up `7ed5e10baf752499b6eeef6cbb8c6905782dd15d`.

## Native regression follow-up — preserved, not accepted yet

The test-only PR #98 branch ran `python docs/research/phase-ii-native-pending-admission/verify_probe.py /tmp/ases-round25-launch/native/followup-run-7ed5e10-01` against the pinned #84 base and returned exit 0 / `PASS`. The capture records A1–A6; A7 (#35/#36 parent regression) was not rerun. A separate MiMo review identified four defensive assertion gaps in this test diff. Until admission supplies a corrected diff and verified rerun, this run is preserved as provenance only and its assertions are **not accepted as sufficient coverage**. See [execution manifest](evidence/native/execution.json) and [raw capture](evidence/native/raw.json).

- Raw capture: 3,873,376 bytes; SHA-256 `d2d811bbb88801967d28f1bee5e285f101be8ebf0b1628fba48d353cac103cbd`.
- Manifest SHA-256 `764524bdd092a407acd6def90ae1a236ae7d3c591f2eaf670d6f7aa59097d636`.
- The test diff is test-only; no production implementation is included or accepted here.

## Custody gate — blocked

PR #85 head `7cb443821659ad7606b906ba601952afde028d66` requires exact image `sha256:b5ba49a53a9c5ad0d0fc3c2c925773589e0d8912cd8077eca91af0bb4ab5e335` and its UID-separated runtime gate. Docker 28.4.0 with `vfs` was available, but inspection returned “No such image”; UID probe was not attempted. No image pull/build/substitution, container run, or #85 probe occurred. The raw [preflight record](evidence/custody/preflight.json) preserves command outputs and constraints. Custody status remains blocked; do not substitute another image.

## Separate unavailable report

The original DeepSeek PR #84 Actions run [45408696041](https://github.com/rock-solid-sites/ases-plugins/actions/runs/45408696041) completed, but its Step Summary report body could not be recovered through the authenticated connector. Job logs expose metadata only, artifacts are empty, and unauthenticated HTML yields a sign-in page. WNASES-4 comments `192fed59-fb00-4902-858f-2e8c9a941551` and `2aeb12c7-139f-4e69-b1ed-4fd639d6a87c` preserve receipts and resume instructions. This round's DeepSeek packet review is independent evidence about the decision packet; it does not reconstruct or disposition the missing original PR #84 report.
