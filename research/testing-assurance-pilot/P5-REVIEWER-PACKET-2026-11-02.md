# P5 source-first reviewer packet — sealed reconstruction exercise

**Status:** Prepared, **NOT independently reviewed**. This document intentionally does not reproduce the author's P5 conclusions.

## Inputs — read in this order

1. [P5 preregistration](P5-PREREGISTERED-PLAN-2026-11-02.md), frozen at source commit `3b997aad036fe56963250f89b0a72784bfa84069`. Record the stated hypotheses and what would falsify them.
2. [Rust journal source](../assurance-p5/rust/main.rs), [Haskell journal source](../assurance-p5/haskell/Main.hs), and [Python harness](../assurance-p5/run_p5.py), at experiment source revision `0e25c4b8970a0064af4d4169f68f5ac7e0cfab2e`.
3. [Original successful GitLab CI](https://gitlab.com/rock-solid-sites-group/rock-solid-sites-project/-/jobs/17650933508) and [original failed CI](https://gitlab.com/rock-solid-sites-group/rock-solid-sites-project/-/jobs/17650922007).
4. Recovered **complete original archived ZIPs**, stored in ASES as [failed/base64](evidence/p5-red_instrument_error-original-ci-artifacts.zip.b64) and [corrected/base64](evidence/p5-green_corrected-original-ci-artifacts.zip.b64), with [hash/size metadata](evidence/P5-ARCHIVES-MANIFEST-2026-11-02.json). Decode and verify with `base64 -d` and `sha256sum` independently; inspect `results/p5.json` and `results/environment.txt`.

**Do not read** the author's [P5 results and interpretation](P5-RESULTS-2026-11-02.md) until after an initial written verdict has been recorded.

## Questions to reconstruct blind

- Which exact journal transition is the acknowledgment intended to prove? Does the code call fsync before that claim in each variant?
- Does the harness distinguish a real signal death at the intended milestone from a timeout, successful exit or failed marker synchronization?
- Which defects does ordinary restart-and-retry testing independently detect, and which does checkpoint-specific killing detect? Recompute from `p5.json`, not from its summary flags alone.
- Compare the original failed job with the corrected successful job. Which underlying statement was wrong: the implementation or the fixture? Was the preregistration modified after observations?
- Verify preserved valid-neighbor behavior, duplicate ID accounting, no-op rejected transactions, and checkpoint replay for both languages.
- Calculate marginal test execution cost, setup cost, archive bytes, and any errors in the published comparison.
- State exactly what power-loss, partial journal write, multi-process concurrency, directory sync and external transaction guarantees remain **NOT_TESTED**.
- Decide whether the extra test method genuinely adds a worthwhile discriminator given the *selected* defect pool; flag the potential bias from preselecting the premature-ACK fault.
- Report independent reviewer model/person, tools, evidence accessed, missing bytes, reconstruction time, claim classifications and any differences found after unsealing the narrative.

**Review acceptance is not automatic.** A reader using the same conversation or relying on the written findings is not an independent reviewer. The broader ASES testing-and-assurance method remains experimental.
