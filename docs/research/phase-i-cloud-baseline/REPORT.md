---
title: Phase I Native Baseline Replay in Codex Cloud
program: EDASES
layer: Research
document_type: Reproduction Record
status: Experimental
authority: Derived
last_updated: 2026-11-10
---

# Result

The frozen native harness reproduced the denied-descendant publication counterexample and its authorized neighbor. The original component sources and harness were not edited. This replay used the `origin/pr-11` tree at `1970abe` on branch `research/phase-i-baseline-cloud-20261110`; the harness fetched its five missing component commits from `origin` before execution.

For `attenuated-descendant`, the original L5 write returned `allowed=false, result=DENY`. The same adapter envelope was then accepted by F4 `/submit` with HTTP 201, event sequence 4, published revision 5, and journal SHA-256 `04548df805fba498f4243b90108db9bafd68bc49d453e6c884027edc8ac8f312`. The independent observer found one durable effect and one proposed composition violation: downstream effect despite no descendant write authority.

For `authorized-neighbor`, L5 returned `allowed=true, result=COMMITTED`; F4 `/submit` returned HTTP 201 with event sequence 4, revision 5, and journal SHA-256 `1f04da2a9025f82b2cb84afe4dce2cb60a2bb13fcf7b7d53ab0ba4c85ed29b22`. The observer found one effect and no proposed composition violation.

The existing receipt-loss case also reproduced: the first F4 call returned HTTP 503 with `local_control_committed=true` after remote publication, and retry returned HTTP 201. The durable journal contained two effects with the same request ID. The existing L6 removal case reproduced local removal followed by F4 HTTP 201 while L5's accepted object remained. Full case results are in `native-capture.tar.gz`.

## Frozen basis

The exact experiment source was `docs/research/phase-i-sol-integration/{native.py,observe.py,reproduce.sh}` from this branch. The captured source index records the complete executed byte hashes. Frozen component commits were F1 `29ec3960c4c60dfb5d5f76d1c5dba7d2ea32d38a`, L5 `51b34aface9340b7e6821b8c40dc62ca38da15e2`, L6 `0f348fda050e67f3d9081a7fc22078eddc547a61`, F4 `26db6db361be986cdd168045f510f5567ee9df53`, and receipt extension `9226cd4b8cd155a1d1b8e6b0495c0e1b99b941b9`.

The frozen policy comparator cited by the experiment is Phase-I-Closure §7 C1–C13 and Phase-I-Verification F1/F3/F4, both read at F1 commit `29ec3960c4c60dfb5d5f76d1c5dba7d2ea32d38a`. Their frozen Git blob IDs are `a82482b1718a652a39a5a2bb179797f92908380d` (`docs/architecture/core-substrate/Phase-I-Closure.md`) and `ca378a16e31128d6ed11d5472d83253340802253` (`docs/architecture/core-substrate/Phase-I-Verification.md`). The test adapter's aliases and cross-component envelope remain test-only assumptions; this does not establish trusted native ingress or source authentication.

## Execution and limits

The exact command was:

```sh
bash docs/research/phase-i-sol-integration/reproduce.sh /tmp/ases-cloud-baseline
```

The integration run completed 16 cases with 77 managed child processes and 169 recorded events; recovery completed two cases. Both reported `PASS`. The observer completed, validated eight altered-evidence controls as rejected, independently read back all 18 persisted F1 SQLite rows, and reported `FINDINGS_REPRODUCED_INCLUDING_UNSAFE_HISTORIES`. The archive preserves `raw.json`, full per-case state and SQLite files, and `evaluation.json`, including process, SQL and HTTP evidence. Its SHA-256 is `2689ff5ce6a974bd8a730b2ceb4038cebe6b53e30c567fcd99015faa9686e0cd`.

This is a repeat of the same harness and same-investigator observer, not an independent review or global proof. It establishes only the selected native histories under the test adapter's trusted import assumptions. It does not establish native F3 acceptance, alias authority, source authentication, native confinement, physical power-loss durability, nonrollback witness behavior, or complete Work Unit state. No CI, archival restore, or publication campaign was run.
