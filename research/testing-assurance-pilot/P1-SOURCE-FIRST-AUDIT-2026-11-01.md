---
title: P1 Evidence Reconstruction and Adversarial Source Audit
program: EDASES
layer: Research
document_type: Source-First Audit
status: Completed Internal Audit; Independent Review Pending
authority: Experimental
last_updated: 2026-11-01
---

# P1 reconstruction: machine evidence versus claims

**Audit role:** source-first adversarial consistency check performed in the **same assistant conversation**, using the preregistered plan, archived machine output, index and harness source instead of accepting the narrative results document. **This is NOT an independent human/agent reviewer** and must not satisfy the proposal's independent-review promotion gate.

## Inputs used

- Frozen plan: [P1-PREREGISTERED-PLAN-2026-11-01.md](P1-PREREGISTERED-PLAN-2026-11-01.md); first committed in `33d2781279cf85784a6fb880c8bb3a9a90d90130`.
- Correction-run observed machine outcome: [evidence/gitlab-3015307498-p1.json](evidence/gitlab-3015307498-p1.json).
- Evidence index: [evidence/gitlab-3015307498-index.json](evidence/gitlab-3015307498-index.json).
- Exact harness source: [pilot_p1.py](pilot_p1.py).
- Verified GitLab job: [3015307498](https://gitlab.com/rock-solid-sites-group/rock-solid-sites-project/-/pipelines/3015307498), job `17647798593`.
- The original failure in the first archive-check implementation remains at [initial P1 evidence](evidence/gitlab-3015298236-index.json); earlier notes were not rewritten.

## Reconstructed checks without relying on the author's conclusion

1. The five frozen examples have expected triples `(accepted, reason, charge_cents)`: free-covered accepted/0; free-spill-authorized accepted/10; free-spill-denied rejected/paid-opt-in-required/0; postpaid-authorized accepted/40; postpaid-unapproved rejected/paid-opt-in-required/0. **All five** actual outputs independently match these fixed values in both compiled languages.
2. For each of four source mutants, the stored actual verdicts were checked against the frozen examples **rather than trusting its `detected=true` flag**. Both paid-authorization bypass mutations admitted the two prohibited paid requests, while all three legitimate neighbors remained correct. Both final-rejection mutations denied all three legitimate neighbors, while both prohibited paid requests remained denied. Thus **4/4 expected mutant faults are visible** in the actual records, not just reported in test status.
3. The frozen plan hash `33493c4d4b5cf9931fc08105cbc1a27f341bcd07a8dc1faae8bc52a748607971` in the pilot output matches the hash recorded in the independent evidence index. The GitLab index records exact ASES source revision `a1c397d5d4fc8f5e2428df6a70de06d4ef0b54f0`.
4. The synthetic archive test records `COMPLETE` on two valid artifacts, `MISSING` when one is deleted, and `CORRUPT` when the other is modified. The subsequent CI `--verify-only` check reported `COMPLETE_LOCALLY` after the index was frozen.
5. The evidence index enumerates **31** files; **only two** representative machine records were independently copied into the public ASES research branch. The complete indexed GitLab artifacts remain native to GitLab, marked `NOT_VERIFIED` for independent archival.
6. Source and evidence do not demonstrate provider-account settlement, atomic reservations, safety under real races, or a language choice.

## Methodological findings and gaps

- **Supported within selected controls:** original implementation behavior, expected mutation detection, paired positive neighbors, and integrity checking on synthetic fixtures.
- **Instrument quality is conditional:** mutations were chosen to target known guards and the frozen five examples. A 4/4 result is *not* an unbiased mutation score or a general assurance guarantee. A genuinely unanticipated fault should be tested in another substrate.
- **External archive unresolved for P1:** the GitLab-hosted ZIP was not independently recovered and hash-verified as a complete external snapshot. The index alone cannot close that gap.
- **Review independence unresolved:** this audit is a separate consistency calculation but shares the same assistant, context and access as the builder. Human/other-agent reconstruction from a deliberately minimal evidence packet is still **NOT_RUN**.
- **Method effectiveness comparison unresolved:** qualification added ~4.37 seconds of targeted executions and tests at one CI substrate, but end-to-end agent effort/token use and defect prevention against a conventional baseline were not measured.
- **CI platform scope:** GitLab runner verification is observed, GitHub Actions for the ASES language evaluation is not yet proven.

## Reviewer handoff and pass/fail rubric

A truly separate reviewer should be given **only** the frozen plan, immutable source revision, raw P1 JSON outcome, evidence index, and provider job link—without this file or the author's P1 result narrative—and asked to:

- derive five fixed expected output triples and identify the authoritative claim source;
- enumerate both source-level mutants per language and infer expected fault signatures;
- compare actual outcomes to predicted signatures, including positive neighbors;
- distinguish compilation or test-instrument failures from behavioral RED;
- verify which archived artifact bytes can actually be accessed and hashed;
- independently classify claims, method sensitivity, confidence limits and acceptance status.

Record reviewer identity or model, access, start/end, material consulted, disagreements, missing evidence and additional effort. **Do not mark this independent-review gate complete without an actual separate reviewer.**

The appropriate methodological acceptance status remains **DEFER**.
